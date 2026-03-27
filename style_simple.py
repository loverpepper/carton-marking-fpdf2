# -*- coding: utf-8 -*-
"""
简化样式示例 - 演示如何创建新样式
这是一个简单的样式模板，用于快速创建新的箱唛样式
"""
from fpdf import FPDF
from PIL import ImageFont
from style_base import BoxMarkStyle, StyleRegistry


@StyleRegistry.register
class SimpleStyle(BoxMarkStyle):
    """简化箱唛样式 - 极简设计，只有基本文字信息"""

    def get_style_name(self):
        return "simple"

    def get_style_description(self):
        return "箱唛样式 - 极简设计，只包含基本文字信息和 SKU"

    def get_required_params(self):
        return ['product', 'box_number']

    def get_layout_config_mm(self, sku_config):
        """简化样式 - 5块布局（示例），单位 mm"""
        l_mm = sku_config.l_cm * 10
        w_mm = sku_config.w_cm * 10
        h_mm = sku_config.h_cm * 10
        half_w_mm = w_mm / 2

        return {
            "top_flap":    (0.0,         0.0,       l_mm, half_w_mm),
            "main_front":  (0.0,         half_w_mm, l_mm, h_mm),
            "main_side":   (l_mm,        half_w_mm, w_mm, h_mm),
            "bottom_flap": (0.0,         half_w_mm + h_mm, l_mm, half_w_mm),
            "back_panel":  (l_mm + w_mm, half_w_mm, l_mm, h_mm),
        }

    def get_panels_mapping(self, sku_config):
        return {
            "top_flap":    "top",
            "main_front":  "front",
            "main_side":   "side",
            "bottom_flap": "bottom",
            "back_panel":  "front",
        }

    def _load_resources(self):
        self.resources = {}

    def _load_fonts(self):
        font_base = self.base_dir / 'assets' / 'Mcombo' / '样式一' / '箱唛字体'
        self.font_paths = {
            'calibri_bold': str(font_base / 'calibri-bold.ttf'),
            'avantgarde':   str(font_base / 'avantgardelt-demi.ttf'),
        }

    def register_fonts(self, pdf: FPDF):
        pdf.add_font('Calibri-Bold',      '', self.font_paths['calibri_bold'])
        pdf.add_font('AvantGardeLT-Demi', '', self.font_paths['avantgarde'])

    def draw_to_pdf(self, pdf: FPDF, sku_config):
        """将所有面板直接绘制到已添加页面的 FPDF 对象上"""
        layout = self.get_layout_config_mm(sku_config)

        r, g, b = sku_config.background_color
        pdf.set_fill_color(r, g, b)
        for _, (x, y, w, h) in layout.items():
            pdf.rect(x, y, w, h, style='F')

        l_mm = sku_config.l_cm * 10
        w_mm = sku_config.w_cm * 10
        h_mm = sku_config.h_cm * 10
        half_w_mm = w_mm / 2

        self._draw_front_content(pdf, sku_config, 0.0, half_w_mm, l_mm, h_mm)

    def _draw_front_content(self, pdf: FPDF, sku_config, x_mm, y_mm, w_mm, h_mm):
        """在正面面板区域绘制 SKU、产品名称和箱号文字"""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        # ── SKU 文字（大号，居中，面板 1/3 高度处）──────────────────────────────
        sku_text = sku_config.sku_name
        sku_size_px = max(1, int(h_mm * px_per_mm * 0.15))
        sku_size_pt = sku_size_px * 72.0 / ppi
        pil_sku = ImageFont.truetype(self.font_paths['calibri_bold'], sku_size_px)

        _, top_s, _, _ = pil_sku.getbbox(sku_text, anchor='ls')
        left_s, _, right_s, _ = pil_sku.getbbox(sku_text, anchor='ls')
        sku_w_mm = (right_s - left_s) / px_per_mm
        sku_ascent_mm = -top_s / px_per_mm
        sku_x = x_mm + (w_mm - sku_w_mm) / 2.0
        sku_baseline = (y_mm + h_mm / 3.0) + sku_ascent_mm

        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Calibri-Bold', '', sku_size_pt)
        pdf.text(sku_x, sku_baseline, sku_text)

        # ── 产品名称（中号，居中，面板 2/3 高度处）──────────────────────────────
        product_text = sku_config.product
        product_size_px = max(1, int(h_mm * px_per_mm * 0.08))
        product_size_pt = product_size_px * 72.0 / ppi
        pil_product = ImageFont.truetype(self.font_paths['avantgarde'], product_size_px)

        _, top_p, _, _ = pil_product.getbbox(product_text, anchor='ls')
        left_p, _, right_p, _ = pil_product.getbbox(product_text, anchor='ls')
        product_w_mm = (right_p - left_p) / px_per_mm
        product_ascent_mm = -top_p / px_per_mm
        product_x = x_mm + (w_mm - product_w_mm) / 2.0
        product_baseline = (y_mm + h_mm * 2.0 / 3.0) + product_ascent_mm

        pdf.set_font('AvantGardeLT-Demi', '', product_size_pt)
        pdf.text(product_x, product_baseline, product_text)

        # ── 箱号（小号，右下角）────────────────────────────────────────────────
        box_text = (f"Box {sku_config.box_number['current_box']}"
                    f"/{sku_config.box_number['total_boxes']}")
        box_size_px = max(1, int(h_mm * px_per_mm * 0.05))
        box_size_pt = box_size_px * 72.0 / ppi
        pil_box = ImageFont.truetype(self.font_paths['calibri_bold'], box_size_px)

        _, top_b, _, _ = pil_box.getbbox(box_text, anchor='ls')
        left_b, _, right_b, _ = pil_box.getbbox(box_text, anchor='ls')
        box_w_mm = (right_b - left_b) / px_per_mm
        box_ascent_mm = -top_b / px_per_mm
        box_x = x_mm + w_mm - box_w_mm - 20.0     # 2 cm from right
        box_baseline = (y_mm + h_mm - 30.0) + box_ascent_mm   # 3 cm from bottom

        pdf.set_font('Calibri-Bold', '', box_size_pt)
        pdf.text(box_x, box_baseline, box_text)
