import sqlite3
import pandas as pd
from pathlib import Path
import logging
import os
import streamlit as st

logger = logging.getLogger("app")

# 数据存放目录，如果不存在会自动创建，映射到了 Docker 的 ./data 宿主机目录
DB_DIR = Path(__file__).parent / "data"
DB_PATH = DB_DIR / "stats.db"

def init_db():
    try:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        
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

import streamlit as st

def log_success(style_name: str, sku_name: str, gen_type: str = "单张", product_name: str = ""):
    """记录一次成功的预览或生成"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''
                INSERT INTO generation_logs (style_name, sku_name, gen_type, product_name)
                VALUES (?, ?, ?, ?)
            ''', (style_name, sku_name, gen_type, product_name))
            conn.commit()
            
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
