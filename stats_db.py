import sqlite3
import pandas as pd
from pathlib import Path
import logging
import os
import shutil
import tempfile
from datetime import datetime, timezone
import streamlit as st

logger = logging.getLogger("app")

# 数据存放目录，如果不存在会自动创建，映射到了 Docker 的 ./data 宿主机目录
DB_DIR = Path(__file__).parent / "data"
DB_PATH = DB_DIR / "stats.db"
R2_ENABLED = os.getenv("R2_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID", "").strip()
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID", "").strip()
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY", "").strip()
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "").strip()
R2_OBJECT_PREFIX = os.getenv("R2_OBJECT_PREFIX", "carton-marking/backups").strip().strip("/")
R2_LEGACY_OBJECT_KEY = os.getenv("R2_OBJECT_KEY", "carton-marking/stats.db").strip()


def _r2_ready() -> bool:
    return all([
        R2_ENABLED,
        R2_ACCOUNT_ID,
        R2_ACCESS_KEY_ID,
        R2_SECRET_ACCESS_KEY,
        R2_BUCKET_NAME,
        R2_OBJECT_PREFIX,
    ])


def _get_r2_client():
    import boto3

    endpoint_url = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )


def _get_local_row_count() -> int:
    if not DB_PATH.exists():
        return 0

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS generation_logs (id INTEGER PRIMARY KEY AUTOINCREMENT)")
            cursor = conn.execute("SELECT COUNT(*) FROM generation_logs")
            result = cursor.fetchone()
            return int(result[0]) if result else 0
    except Exception:
        return 0


def _list_r2_backup_objects(client):
    objects = []
    prefix = f"{R2_OBJECT_PREFIX}/"
    paginator = client.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=R2_BUCKET_NAME, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj.get("Key", "")
            if key.endswith(".db"):
                objects.append(obj)

    return objects


def restore_db_from_r2_if_needed():
    """仅当本地库不存在时，从 Cloudflare R2 恢复最新的增量快照。"""
    if DB_PATH.exists() or not _r2_ready():
        return

    try:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        client = _get_r2_client()
        backup_objects = _list_r2_backup_objects(client)
        restore_key = None

        if backup_objects:
            latest_backup = max(backup_objects, key=lambda obj: obj["LastModified"])
            restore_key = latest_backup["Key"]
        elif R2_LEGACY_OBJECT_KEY:
            restore_key = R2_LEGACY_OBJECT_KEY

        if not restore_key:
            logger.info("Cloudflare R2 中未找到统计数据库快照，将使用本地新库初始化")
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_file:
            temp_path = Path(tmp_file.name)

        try:
            client.download_file(R2_BUCKET_NAME, restore_key, str(temp_path))
            shutil.move(str(temp_path), str(DB_PATH))
            logger.info(f"已从 Cloudflare R2 恢复统计数据库快照: {restore_key}")
        finally:
            if temp_path.exists():
                temp_path.unlink()
    except Exception as e:
        logger.warning(f"从 Cloudflare R2 恢复统计数据库失败，将继续使用本地新库: {e}")


def sync_db_to_r2():
    """将本地 SQLite 作为追加快照同步到 Cloudflare R2，避免覆盖历史备份。"""
    if not DB_PATH.exists() or not _r2_ready():
        return

    row_count = _get_local_row_count()
    if row_count <= 0:
        logger.info("本地统计数据库为空，跳过 Cloudflare R2 同步，避免空库覆盖历史快照")
        return

    snapshot_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_file:
            snapshot_path = Path(tmp_file.name)

        shutil.copy2(DB_PATH, snapshot_path)
        client = _get_r2_client()
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        snapshot_key = f"{R2_OBJECT_PREFIX}/stats_{timestamp}_{row_count}.db"
        client.upload_file(
            str(snapshot_path),
            R2_BUCKET_NAME,
            snapshot_key,
            ExtraArgs={"Metadata": {"row-count": str(row_count), "source": "carton-marking-fpdf2"}},
        )
        logger.info(f"统计数据库增量快照已同步到 Cloudflare R2: {snapshot_key}")
    except Exception as e:
        logger.warning(f"同步统计数据库到 Cloudflare R2 失败，本地数据库仍可继续使用: {e}")
    finally:
        if snapshot_path and snapshot_path.exists():
            snapshot_path.unlink()

def init_db():
    try:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        restore_db_from_r2_if_needed()
        
        with sqlite3.connect(DB_PATH) as conn:
            # 记录每一次成功生成的流水账
            conn.execute('''
                CREATE TABLE IF NOT EXISTS generation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                    style_name TEXT,
                    sku_name TEXT,
                    gen_type TEXT
                )
            ''')
            # 兼容老版本，自动添加产品名称列
            try:
                conn.execute("ALTER TABLE generation_logs ADD COLUMN product_name TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass
            conn.commit()
    except Exception as e:
        logger.error(f"初始化统计数据库失败: {e}", exc_info=True)

def log_success(style_name: str, sku_name: str, gen_type: str = "单张", product_name: str = ""):
    """记录一次成功的预览或生成"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''
                INSERT INTO generation_logs (style_name, sku_name, gen_type, product_name)
                VALUES (?, ?, ?, ?)
            ''', (style_name, sku_name, gen_type, product_name))
            conn.commit()

        sync_db_to_r2()
            
    except Exception as e:
        logger.error(f"写入统计数据失败: {e}")
    finally:
        # 写入新数据后清理缓存，让页面能读取到最新统计
        st.cache_data.clear()

@st.cache_data(ttl=60)
def get_daily_stats() -> pd.DataFrame:
    """获取每日按样式分组的生成统计"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            query = '''
                SELECT 
                    date(created_at) as "生成日期",
                    time(created_at) as "时间",
                    sku_name as "SKU",
                    product_name as "产品名称",
                    style_name as "选择样式",
                    gen_type as "生成方式"
                FROM generation_logs
                ORDER BY created_at DESC
            '''
            return pd.read_sql_query(query, conn)
    except Exception as e:
        logger.error(f"读取每日统计失败: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_overall_stats() -> pd.DataFrame:
    """获取全生命周期的总排行榜"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            query = '''
                SELECT 
                    style_name as "选择样式",
                    count(*) as "历史累计总生成张数"
                FROM generation_logs
                GROUP BY "选择样式"
                ORDER BY "历史累计总生成张数" DESC
            '''
            return pd.read_sql_query(query, conn)
    except Exception:
        return pd.DataFrame()
