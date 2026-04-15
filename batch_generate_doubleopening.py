# -*- coding: utf-8 -*-
"""
批量生成 Exacme 对开盖箱唛 PNG
读取桌面上的 对开盖样式表.xlsx，输出到桌面 output 文件夹
"""
import sys
from pathlib import Path

# 确保项目路径在 sys.path 中
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

import openpyxl
from generation_core_v3 import BoxMarkGenerator, SKUConfig

EXCEL_PATH   = Path(r'C:\Users\QckQu\Desktop\对开盖样式表.xlsx')
OUTPUT_DIR   = Path(r'C:\Users\QckQu\Desktop\output')
BASE_DIR     = PROJECT_DIR
STYLE_NAME   = 'exacme_doubleopening'
PPI          = 150
PRODUCT_FULLNAME = 'TRAMPOLINE\nSPRING COVER'
PRODUCT      = 'TRAMPOLINE'


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    wb = openpyxl.load_workbook(str(EXCEL_PATH), data_only=True)
    ws = wb['Sheet1']

    rows = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[0]]
    print(f'共读取 {len(rows)} 条 SKU，开始生成...\n')

    # 复用同一个 generator（避免重复加载资源）
    gen = BoxMarkGenerator(base_dir=BASE_DIR, style_name=STYLE_NAME, ppi=PPI)

    ok, fail = 0, 0
    for i, row in enumerate(rows, 1):
        sku_name = str(row[0]).strip()
        sn_code  = str(row[1]).strip().rstrip('/').strip() if row[1] else ''
        color    = str(row[2]).strip() if row[2] else ''
        l_cm     = float(row[3]) if row[3] else 0.0
        w_cm     = float(row[4]) if row[4] else 0.0
        h_cm     = float(row[5]) if row[5] else 0.0
        gw_lbs   = round(float(row[12]), 2) if row[12] else 0.0
        nw_lbs   = round(float(row[13]), 2) if row[13] else 0.0

        side_text = {
            'gw_value': gw_lbs,
            'nw_value': nw_lbs,
            'sn_code':  sn_code,
        }

        try:
            sku_config = SKUConfig(
                sku_name=sku_name,
                length_cm=l_cm,
                width_cm=w_cm,
                height_cm=h_cm,
                style_name=STYLE_NAME,
                ppi=PPI,
                color=color,
                product=PRODUCT,
                product_fullname=PRODUCT_FULLNAME,
                side_text=side_text,
            )

            img = gen.generate_complete_layout(sku_config)
            out_path = OUTPUT_DIR / f'{sku_name}.png'
            img.save(str(out_path))
            print(f'  [{i:02d}/{len(rows)}] OK  {sku_name}')
            ok += 1

        except Exception as e:
            print(f'  [{i:02d}/{len(rows)}] ERR {sku_name}  ->  {e}')
            fail += 1

    print(f'\n done: {ok} ok, {fail} failed')
    print(f'output: {OUTPUT_DIR}')


if __name__ == '__main__':
    main()
