# -*- coding: utf-8 -*-
"""
Barberpub 对开盖样式 - fpdf2 版
"""
from fpdf import FPDF
from PIL import Image, ImageFont
import pathlib
from style_base import BoxMarkStyle, StyleRegistry
import general_functions
from general_functions import generate_barcode_image


@StyleRegistry.register
class BarberpubDoubleOpeningStyle(BoxMarkStyle):
    """Barberpub 对开盖样式 (fpdf2 版)"""

    def get_style_name(self):
        return "barberpub_doubleopening"

    def get_style_description(self):
        return "Barberpub 对开盖箱唛样式"

    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'ppi', 'color', 'product',
                'side_text', 'sku_name', 'box_number', 'img_line_drawing']

    def get_layout_config_mm(self, sku_config):
        """Barberpub 对开盖样式 - 12块布局（4列3行），单位 mm"""
        l_mm = sku_config.l_cm * 10
        w_mm = sku_config.w_cm * 10
        h_mm = sku_config.h_cm * 10
        half_w_mm = w_mm / 2

        x0 = 0.0
        x1 = l_mm
        x2 = l_mm + w_mm
        x3 = 2 * l_mm + w_mm

        y0 = 0.0
        y1 = half_w_mm
        y2 = half_w_mm + h_mm

        return {
            "flap_top_front1": (x0, y0, l_mm,  half_w_mm),
            "flap_top_side1":  (x1, y0, w_mm,  half_w_mm),
            "flap_top_front2": (x2, y0, l_mm,  half_w_mm),
            "flap_top_side2":  (x3, y0, w_mm,  half_w_mm),
            "panel_front1":    (x0, y1, l_mm,  h_mm),
            "panel_side1":     (x1, y1, w_mm,  h_mm),
            "panel_front2":    (x2, y1, l_mm,  h_mm),
            "panel_side2":     (x3, y1, w_mm,  h_mm),
            "flap_btm_front1": (x0, y2, l_mm,  half_w_mm),
            "flap_btm_side1":  (x1, y2, w_mm,  half_w_mm),
            "flap_btm_front2": (x2, y2, l_mm,  half_w_mm),
            "flap_btm_side2":  (x3, y2, w_mm,  half_w_mm),
        }

    def get_panels_mapping(self, sku_config):
        return {
            "flap_top_front1": "left_up",
            "flap_top_side1":  "blank",
            "flap_top_front2": "right_up",
            "flap_top_side2":  "blank",
            "panel_front1":    "front",
            "panel_side1":     "side",
            "panel_front2":    "front",
            "panel_side2":     "side",
            "flap_btm_front1": "left_down",
            "flap_btm_side1":  "blank",
            "flap_btm_front2": "right_down",
            "flap_btm_side2":  "blank",
        }

    # ── 资源 / 字体加载 ─────────────────────────────────────────────────────────

    def _load_resources(self):
        """加载资源为 pathlib.Path，fpdf2 可直接接受路径"""
        res_base = self.base_dir / 'assets' / 'Barberpub' / '对开盖' / '矢量文件'
        self.resources = {
            'icon_logo':              res_base / '正唛logo.png',
            'icon_top_logo':          res_base / '顶盖logo信息.png',
            'icon_attention_info':    res_base / '对开盖开箱注意事项.png',
            'icon_company':           res_base / '正唛公司信息.png',
            'icon_webside':           res_base / '侧唛网址.png',
            'icon_side_label_wide':   res_base / '侧唛标签_宽.png',
            'icon_side_label_narrow': res_base / '侧唛标签_窄.png',
            'icon_slogan':            res_base / '正唛宣传语.png',
            'icon_box_info':          res_base / '正唛多箱选择框.png',
            'line_drawing':           res_base / '侧唛线描图.png',
        }

    def _load_fonts(self):
        """加载字体路径"""
        font_base = self.base_dir / 'assets' / 'Barberpub' / '对开盖' / '箱唛字体'
        self.font_paths = {
            'CentSchbook': str(font_base / '111.ttf'),
            'DroidSans':   str(font_base / 'CENSBKBI.TTF'),
            'CalibriB':    str(font_base / 'calibri_blod.ttf'),
        }

    # ── fpdf2 字体注册 ──────────────────────────────────────────────────────────

    def register_fonts(self, pdf: FPDF):
        pdf.add_font('CentSchbook', '', self.font_paths['CentSchbook'])
        pdf.add_font('DroidSans',   '', self.font_paths['DroidSans'])
        pdf.add_font('CalibriB',    '', self.font_paths['CalibriB'])

    # ── 核心绘制入口 ────────────────────────────────────────────────────────────

    def draw_to_pdf(self, pdf: FPDF, sku_config):
        layout = self.get_layout_config_mm(sku_config)

        r, g, b = sku_config.background_color
        pdf.set_fill_color(r, g, b)
        for _, (x, y, w, h) in layout.items():
            pdf.rect(x, y, w, h, style='F')

        l_mm = sku_config.l_cm * 10
        w_mm = sku_config.w_cm * 10
        h_mm = sku_config.h_cm * 10
        half_w_mm = w_mm / 2

        x0 = 0.0
        x1 = l_mm
        x2 = l_mm + w_mm
        x3 = 2 * l_mm + w_mm
        y1 = half_w_mm

        # Two front panels
        self._draw_front_panel(pdf, sku_config, x0, y1, l_mm, h_mm)
        self._draw_front_panel(pdf, sku_config, x2, y1, l_mm, h_mm)

        # Two side panels
        self._draw_side_panel(pdf, sku_config, x1, y1, w_mm, h_mm)
        self._draw_side_panel(pdf, sku_config, x3, y1, w_mm, h_mm)

        # Left-up flap
        self._draw_flap_left_up(pdf, sku_config, x0, 0.0, l_mm, half_w_mm)

        # Right-up flap
        self._draw_flap_right_up(pdf, sku_config, x2, 0.0, l_mm, half_w_mm)

        # Left-down and right-down are blank (already background-filled)

    # ── 内部辅助方法 ────────────────────────────────────────────────────────────

    def _get_font_size(self, text, font_key, target_width_mm, ppi):
        """返回 (font_size_pt, pil_font) 使文字适合 target_width_mm"""
        target_px = int(target_width_mm * ppi / 25.4)
        size_px = general_functions.get_max_font_size(text, self.font_paths[font_key], target_px)
        size_pt = size_px * 72.0 / ppi
        pil_font = ImageFont.truetype(self.font_paths[font_key], size_px)
        return size_pt, pil_font

    def _get_font_size_constrained(self, text, font_key, target_width_mm, max_height_mm, ppi):
        """同 _get_font_size，额外受 max_height_mm 约束"""
        target_px = int(target_width_mm * ppi / 25.4)
        max_h_px = int(max_height_mm * ppi / 25.4)
        size_px = general_functions.get_max_font_size(
            text, self.font_paths[font_key], target_px, max_height=max_h_px)
        size_pt = size_px * 72.0 / ppi
        pil_font = ImageFont.truetype(self.font_paths[font_key], size_px)
        return size_pt, pil_font

    @staticmethod
    def _pil_bbox_mm(pil_font, text, ppi):
        left, top, right, bottom = pil_font.getbbox(text, anchor='ls')
        px_per_mm = ppi / 25.4
        return left / px_per_mm, top / px_per_mm, right / px_per_mm, bottom / px_per_mm

    def _draw_text_top_left(self, pdf, x_mm, y_top_mm, text,
                             font_family, font_style, font_size_pt, pil_font, ppi,
                             color=(0, 0, 0)):
        _, top_mm, _, _ = self._pil_bbox_mm(pil_font, text, ppi)
        baseline_y = y_top_mm + (-top_mm)
        r, g, b = color
        pdf.set_text_color(r, g, b)
        pdf.set_font(font_family, font_style, font_size_pt)
        pdf.text(x_mm, baseline_y, text)

    def _draw_text_top_center(self, pdf, x_center_mm, y_top_mm, text,
                               font_family, font_style, font_size_pt, pil_font, ppi,
                               color=(0, 0, 0)):
        left_mm, top_mm, right_mm, _ = self._pil_bbox_mm(pil_font, text, ppi)
        text_w_mm = right_mm - left_mm
        x_mm = x_center_mm - text_w_mm / 2.0
        baseline_y = y_top_mm + (-top_mm)
        r, g, b = color
        pdf.set_text_color(r, g, b)
        pdf.set_font(font_family, font_style, font_size_pt)
        pdf.text(x_mm, baseline_y, text)

    # ── 翻盖面板 ─────────────────────────────────────────────────────────────

    def _draw_flap_left_up(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm):
        """左翻盖（上）：顶盖 logo，宽 55%，居中"""
        icon_path = self.resources['icon_top_logo']
        with Image.open(icon_path) as img:
            orig_w, orig_h = img.size
        img_w_mm = w_mm * 0.55
        img_h_mm = img_w_mm * orig_h / orig_w
        img_x = x_mm + (w_mm - img_w_mm) / 2
        img_y = y_mm + (h_mm - img_h_mm) / 2
        pdf.image(icon_path, x=img_x, y=img_y, w=img_w_mm, h=img_h_mm)

    def _draw_flap_right_up(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm):
        """右翻盖（上）：开箱注意事项，宽 86%，居中"""
        icon_path = self.resources['icon_attention_info']
        with Image.open(icon_path) as img:
            orig_w, orig_h = img.size
        img_w_mm = w_mm * 0.86
        img_h_mm = img_w_mm * orig_h / orig_w
        img_x = x_mm + (w_mm - img_w_mm) / 2
        img_y = y_mm + (h_mm - img_h_mm) / 2
        pdf.image(icon_path, x=img_x, y=img_y, w=img_w_mm, h=img_h_mm)

    # ── 正面面板 ─────────────────────────────────────────────────────────────

    def _draw_front_panel(self, pdf: FPDF, sku_config, x_mm, y_mm, w_mm, h_mm):
        """绘制正面（正唛）面板"""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4
        margin_top = 30.0
        margin_left = 30.0
        margin_right = 27.0

        # 1. Logo（左上角）
        icon_logo = self.resources['icon_logo']
        logo_h_mm = h_mm * 0.14
        with Image.open(icon_logo) as img:
            orig_w, orig_h = img.size
        logo_w_mm = logo_h_mm * orig_w / orig_h
        pdf.image(icon_logo, x=x_mm + margin_left, y=y_mm + margin_top,
                  w=logo_w_mm, h=logo_h_mm)

        # 2. 公司信息（右上角）
        icon_company = self.resources['icon_company']
        company_h_mm = h_mm * 0.06
        with Image.open(icon_company) as img:
            orig_w, orig_h = img.size
        company_w_mm = company_h_mm * orig_w / orig_h
        pdf.image(icon_company,
                  x=x_mm + w_mm - company_w_mm - margin_right,
                  y=y_mm + margin_top,
                  w=company_w_mm, h=company_h_mm)

        # 3. 产品名称（DroidSans，48% 高度居中）
        product_text = sku_config.product
        prod_pt, pil_prod = self._get_font_size_constrained(
            product_text, 'DroidSans', w_mm * 0.63, h_mm * 0.28, ppi)
        left_mm, top_mm, right_mm, bottom_mm = self._pil_bbox_mm(pil_prod, product_text, ppi)
        text_w_mm = right_mm - left_mm
        prod_h_mm = bottom_mm - top_mm
        text_x = x_mm + (w_mm - text_w_mm) / 2

        # 4. 标语图片（产品名称下方，居中）
        icon_slogan = self.resources['icon_slogan']
        slogan_h_mm = h_mm * 0.05
        with Image.open(icon_slogan) as img:
            s_orig_w, s_orig_h = img.size
        slogan_w_mm = slogan_h_mm * s_orig_w / s_orig_h
        vertical_gap = 13.0  # 1.3cm

        total_center_h = prod_h_mm + vertical_gap + slogan_h_mm
        center_y_start = y_mm + h_mm * 0.48 - total_center_h / 2

        # 绘制产品名称
        self._draw_text_top_left(pdf, text_x, center_y_start,
                                  product_text, 'DroidSans', '', prod_pt, pil_prod, ppi)
        product_y_top = center_y_start

        # 绘制标语
        slogan_x = x_mm + (w_mm - slogan_w_mm) / 2
        slogan_y = product_y_top + prod_h_mm + vertical_gap
        pdf.image(icon_slogan, x=slogan_x, y=slogan_y, w=slogan_w_mm, h=slogan_h_mm)

        # 5. 底部黑色条纹
        stripe_height_mm = 12.0
        bottom_margin_mm = 6.0
        stripe_y = y_mm + h_mm - stripe_height_mm - bottom_margin_mm
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(x_mm, stripe_y, w_mm, stripe_height_mm, style='F')

        margin_bottom = 32.0

        # 6. SKU 代码（左下角，CentSchbook）
        sku_text = sku_config.sku_name
        sku_pt, pil_sku = self._get_font_size_constrained(
            sku_text, 'CentSchbook', w_mm * 0.715, h_mm * 0.14, ppi)
        _, sku_top_mm, _, sku_bot_mm = self._pil_bbox_mm(pil_sku, sku_text, ppi)
        sku_h_mm = sku_bot_mm - sku_top_mm
        sku_y_top = y_mm + h_mm - margin_bottom - sku_h_mm - 5.0
        sku_x = x_mm + margin_left - 6.0
        self._draw_text_top_left(pdf, sku_x, sku_y_top,
                                  sku_text, 'CentSchbook', '', sku_pt, pil_sku, ppi)

        # 7. 颜色文字（SKU 上方，CentSchbook）
        color_text = sku_config.color.upper()
        color_px = int(h_mm * px_per_mm * 0.06)
        color_pt = color_px * 72.0 / ppi
        pil_color = ImageFont.truetype(self.font_paths['CentSchbook'], color_px)
        _, c_top_mm, _, c_bot_mm = self._pil_bbox_mm(pil_color, color_text, ppi)
        color_h_mm = c_bot_mm - c_top_mm
        color_y_top = sku_y_top - color_h_mm - 3.0
        color_x = x_mm + margin_left
        self._draw_text_top_left(pdf, color_x, color_y_top,
                                  color_text, 'CentSchbook', '', color_pt, pil_color, ppi)

        # 8. 箱号文字（右下角，圆角黑框，白字）
        box_text = (f"BOX {sku_config.box_number['current_box']} "
                    f"OF {sku_config.box_number['total_boxes']}")
        box_pt, pil_box = self._get_font_size_constrained(
            box_text, 'CentSchbook', w_mm * 0.127, h_mm * 0.038, ppi)
        left_b, top_b, right_b, bot_b = self._pil_bbox_mm(pil_box, box_text, ppi)
        box_w_mm = right_b - left_b
        box_h_mm = bot_b - top_b
        box_y_top = y_mm + h_mm - margin_bottom - box_h_mm - 5.0
        box_x = x_mm + w_mm - margin_right - box_w_mm

        # 黑色圆角背景
        pad_x = 5.0
        pad_y_top = 0.7 * 0.7 * 10  # 0.7cm * 0.7 → mm  = 4.9
        pad_y_bot = 0.7 * 1.4 * 10  # 0.7cm * 1.4 → mm  = 9.8
        radius_mm = 12 * 25.4 / ppi
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(box_x - pad_x, box_y_top - pad_y_top,
                 box_w_mm + 2 * pad_x, box_h_mm + pad_y_top + pad_y_bot,
                 style='F', round_corners=True, corner_radius=radius_mm)

        r, g, b = sku_config.background_color
        self._draw_text_top_left(pdf, box_x, box_y_top,
                                  box_text, 'CentSchbook', '', box_pt, pil_box, ppi,
                                  color=(r, g, b))

    # ── 侧面面板 ─────────────────────────────────────────────────────────────

    def _draw_side_panel(self, pdf: FPDF, sku_config, x_mm, y_mm, w_mm, h_mm):
        """绘制侧面（侧唛）面板 - 宽侧唛或窄侧唛"""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        # 网址图标（两种布局共用，顶部居中）
        webside_path = self.resources['icon_webside']
        webside_w_mm = w_mm * 0.5
        with Image.open(webside_path) as img:
            ws_orig_w, ws_orig_h = img.size
        webside_h_mm = webside_w_mm * ws_orig_h / ws_orig_w
        webside_x = x_mm + (w_mm - webside_w_mm) / 2
        webside_y = y_mm + 30.0
        pdf.image(webside_path, x=webside_x, y=webside_y,
                  w=webside_w_mm, h=webside_h_mm)

        if sku_config.w_cm > sku_config.h_cm:
            self._draw_side_wide(pdf, sku_config, x_mm, y_mm, w_mm, h_mm,
                                 ppi, px_per_mm)
        else:
            self._draw_side_narrow(pdf, sku_config, x_mm, y_mm, w_mm, h_mm,
                                   ppi, px_per_mm,
                                   webside_y=webside_y, webside_h_mm=webside_h_mm)

    def _draw_side_wide(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm, ppi, px_per_mm):
        """宽侧唛布局（w_cm > h_cm）"""

        # 底部黑色条纹
        stripe_height_mm = 12.0
        bottom_margin_mm = 6.0
        stripe_y = y_mm + h_mm - stripe_height_mm - bottom_margin_mm
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(x_mm, stripe_y, w_mm, stripe_height_mm, style='F')

        # 线描图（左侧）
        if hasattr(sku_config, 'img_line_drawing') and sku_config.img_line_drawing is not None:
            line_path = sku_config.img_line_drawing
        else:
            line_path = self.resources['line_drawing']
        line_h_mm = h_mm * 0.66
        with Image.open(line_path) as img:
            l_orig_w, l_orig_h = img.size
        line_w_mm = line_h_mm * l_orig_w / l_orig_h
        line_x = x_mm + 50.0
        line_y = y_mm + (h_mm - line_h_mm) / 2 + h_mm * 0.05
        pdf.image(line_path, x=line_x, y=line_y, w=line_w_mm, h=line_h_mm)

        # SKU 文字（右区，CentSchbook）
        sku_text = sku_config.sku_name
        sku_pt, pil_sku = self._get_font_size_constrained(
            sku_text, 'CentSchbook', w_mm * 0.571, h_mm * 0.11, ppi)
        _, sku_top_mm, sku_right_mm, sku_bot_mm = self._pil_bbox_mm(pil_sku, sku_text, ppi)
        sku_left_mm, _, _, _ = self._pil_bbox_mm(pil_sku, sku_text, ppi)
        sku_w_mm = sku_right_mm - sku_left_mm
        sku_h_mm = sku_bot_mm - sku_top_mm
        sku_x = x_mm + w_mm * 0.38
        sku_y_top = y_mm + h_mm * 0.38
        self._draw_text_top_left(pdf, sku_x, sku_y_top,
                                  sku_text, 'CentSchbook', '', sku_pt, pil_sku, ppi)

        # 颜色文字（SKU 下方右区）
        color_text = sku_config.color.upper()
        color_px = int(h_mm * px_per_mm * 0.041)
        color_pt = color_px * 72.0 / ppi
        pil_color = ImageFont.truetype(self.font_paths['CentSchbook'], color_px)
        c_left_mm, c_top_mm, c_right_mm, c_bot_mm = self._pil_bbox_mm(pil_color, color_text, ppi)
        color_w_mm = c_right_mm - c_left_mm
        color_h_mm = c_bot_mm - c_top_mm
        color_x = sku_x + sku_w_mm - color_w_mm - 3.0
        color_y_top = sku_y_top + sku_h_mm + 26.0
        self._draw_text_top_left(pdf, color_x, color_y_top,
                                  color_text, 'CentSchbook', '', color_pt, pil_color, ppi)

        # 箱号文字（颜色左侧，圆角黑框）
        box_text = (f"BOX {sku_config.box_number['current_box']} "
                    f"OF {sku_config.box_number['total_boxes']}")
        box_pt, pil_box = self._get_font_size_constrained(
            box_text, 'CentSchbook', w_mm * 0.127, h_mm * 0.038, ppi)
        bl, bt, br, bb = self._pil_bbox_mm(pil_box, box_text, ppi)
        box_w_mm = br - bl
        box_h_mm = bb - bt
        box_x = color_x - box_w_mm - 15.0
        box_y_top = color_y_top + (color_h_mm - box_h_mm) / 3

        pad_x = 5.0
        pad_y_top = 4.9
        pad_y_bot = 9.8
        radius_mm = 12 * 25.4 / ppi
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(box_x - pad_x, box_y_top - pad_y_top,
                 box_w_mm + 2 * pad_x, box_h_mm + pad_y_top + pad_y_bot,
                 style='F', round_corners=True, corner_radius=radius_mm)
        r, g, b = sku_config.background_color
        self._draw_text_top_left(pdf, box_x, box_y_top,
                                  box_text, 'CentSchbook', '', box_pt, pil_box, ppi,
                                  color=(r, g, b))

        # 宽侧唛标签（模板 + 内容叠加）
        label_w_mm = sku_w_mm * 0.93
        label_h_mm = label_w_mm * 868 / 4140
        label_x = sku_x + sku_w_mm * 0.07
        label_y = box_y_top + box_h_mm + h_mm * 0.14
        pdf.image(self.resources['icon_side_label_wide'],
                  x=label_x, y=label_y, w=label_w_mm, h=label_h_mm)

        gw_text = (f"G.W./N.W. : {sku_config.side_text['gw_value']} / "
                   f"{sku_config.side_text['nw_value']} LBS")
        box_size_text = (f"BOX SIZE : {sku_config.l_cm:.1f}\" x "
                         f"{sku_config.w_cm:.1f}\" x {sku_config.h_cm:.1f}\"")

        self._draw_label_overlay(
            pdf, sku_config,
            label_x, label_y, label_w_mm, label_h_mm,
            barcode1_text=sku_config.sku_name,
            barcode2_text=sku_config.side_text['sn_code'],
            bc1_xf=0.598, bc1_yf=0.05, bc1_wf=0.25,  bc1_hf=0.26,
            bc2_xf=0.855, bc2_yf=0.05, bc2_wf=0.14,  bc2_hf=0.26,
            bar_yf=0.78,  bar_hf=0.18,
            gw_text=gw_text,  gw_xf=0.023, gw_yf=0.13, gw_hf=0.182,
            box_text=box_size_text, box_xf=0.023, box_yf=0.48, box_hf=0.182,
        )

    def _draw_side_narrow(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm,
                          ppi, px_per_mm, webside_y, webside_h_mm):
        """窄侧唛布局（w_cm <= h_cm）"""

        # 线描图（居中，网址下方）
        if hasattr(sku_config, 'img_line_drawing') and sku_config.img_line_drawing is not None:
            line_path = sku_config.img_line_drawing
        else:
            line_path = self.resources['line_drawing']
        line_h_mm = h_mm * 0.46
        with Image.open(line_path) as img:
            l_orig_w, l_orig_h = img.size
        line_w_mm = line_h_mm * l_orig_w / l_orig_h
        line_x = x_mm + (w_mm - line_w_mm) / 2
        line_y = webside_y + webside_h_mm + 30.0
        pdf.image(line_path, x=line_x, y=line_y, w=line_w_mm, h=line_h_mm)

        # SKU 文字（居中，线描图下方）
        sku_text = sku_config.sku_name
        sku_pt, pil_sku = self._get_font_size_constrained(
            sku_text, 'CentSchbook', w_mm * 0.9, h_mm * 0.12, ppi)
        sl, st, sr, sb = self._pil_bbox_mm(pil_sku, sku_text, ppi)
        sku_text_w = sr - sl
        sku_text_y = line_y + line_h_mm + 30.0
        sku_text_x = x_mm + (w_mm - sku_text_w) / 2
        self._draw_text_top_left(pdf, sku_text_x, sku_text_y,
                                  sku_text, 'CentSchbook', '', sku_pt, pil_sku, ppi)

        # 底部斜纹条（简化为纯黑色矩形）
        stripe_height_mm = 12.0
        bottom_margin_mm = h_mm * 0.21
        stripe_y = y_mm + h_mm - bottom_margin_mm - stripe_height_mm
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(x_mm, stripe_y, w_mm, stripe_height_mm, style='F')

        bottom_area_top = y_mm + h_mm - bottom_margin_mm

        # 窄侧唛标签（右侧）
        label_h_mm = w_mm * 0.15
        label_w_mm = label_h_mm * 2076 / 1073
        label_y = bottom_area_top + (bottom_margin_mm - label_h_mm) / 2
        label_x = x_mm + w_mm / 2 + (w_mm / 2 - label_w_mm) / 2
        pdf.image(self.resources['icon_side_label_narrow'],
                  x=label_x, y=label_y, w=label_w_mm, h=label_h_mm)

        self._draw_label_overlay(
            pdf, sku_config,
            label_x, label_y, label_w_mm, label_h_mm,
            barcode1_text=sku_config.sku_name,
            barcode2_text=sku_config.side_text['sn_code'],
            bc1_xf=0.05,  bc1_yf=0.04, bc1_wf=0.533, bc1_hf=0.28,
            bc2_xf=0.60,  bc2_yf=0.04, bc2_wf=0.36,  bc2_hf=0.28,
            bar_yf=0.88,  bar_hf=0.12,
        )

        # 左侧信息区域（毛重净重、箱子尺寸）
        info_x = x_mm + w_mm * 0.0987
        info_center_y = bottom_area_top + bottom_margin_mm / 2
        vertical_gap = 26.0

        label_font_h_mm = h_mm * 0.028
        label_font_px = int(label_font_h_mm * px_per_mm)
        label_font_pt = label_font_px * 72.0 / ppi
        pil_lbl = ImageFont.truetype(self.font_paths['CentSchbook'], label_font_px)

        value_font_h_mm = h_mm * 0.024
        value_font_px = int(value_font_h_mm * px_per_mm)
        value_font_pt = value_font_px * 72.0 / ppi
        pil_val = ImageFont.truetype(self.font_paths['CentSchbook'], value_font_px)

        # G.W./N.W. 标签（黑框）
        gw_label = "G.W./N.W."
        gl, gt, gr, gb = self._pil_bbox_mm(pil_lbl, gw_label, ppi)
        gw_lbl_w = gr - gl
        gw_lbl_h = gb - gt
        gw_lbl_y = info_center_y - vertical_gap / 2 - gw_lbl_h * 1.3

        pad_x = 3.0
        pad_y_top = 4.9
        pad_y_bot = 9.8
        radius_mm = 16 * 25.4 / ppi
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(info_x - pad_x, gw_lbl_y - pad_y_top,
                 gw_lbl_w + 2 * pad_x, gw_lbl_h + pad_y_top + pad_y_bot,
                 style='F', round_corners=True, corner_radius=radius_mm)
        r, g, b = sku_config.background_color
        self._draw_text_top_left(pdf, info_x, gw_lbl_y,
                                  gw_label, 'CentSchbook', '', label_font_pt, pil_lbl, ppi,
                                  color=(r, g, b))

        # G.W./N.W. 值
        gw_value = (f"{sku_config.side_text['gw_value']} / "
                    f"{sku_config.side_text['nw_value']} LBS")
        vl, vt, vr, vb = self._pil_bbox_mm(pil_val, gw_value, ppi)
        val_h = vb - vt
        gw_value_x = info_x + gw_lbl_w + 20.0
        gw_val_center_y = gw_lbl_y + gw_lbl_h / 2
        gw_val_y = gw_val_center_y - val_h / 2
        self._draw_text_top_left(pdf, gw_value_x, gw_val_y,
                                  gw_value, 'CentSchbook', '', value_font_pt, pil_val, ppi)

        # BOX SIZE 标签（黑框）
        box_label = "BOX SIZE"
        bl2, bt2, br2, bb2 = self._pil_bbox_mm(pil_lbl, box_label, ppi)
        box_lbl_w = br2 - bl2
        box_lbl_h = bb2 - bt2
        box_lbl_y = info_center_y + vertical_gap / 2
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(info_x - pad_x, box_lbl_y - pad_y_top,
                 box_lbl_w + 2 * pad_x, box_lbl_h + pad_y_top + pad_y_bot,
                 style='F', round_corners=True, corner_radius=radius_mm)
        self._draw_text_top_left(pdf, info_x, box_lbl_y,
                                  box_label, 'CentSchbook', '', label_font_pt, pil_lbl, ppi,
                                  color=(r, g, b))

        # BOX SIZE 值
        box_val_text = (f'{sku_config.l_cm:.1f}" x '
                        f'{sku_config.w_cm:.1f}" x '
                        f'{sku_config.h_cm:.1f}"')
        bvl, bvt, bvr, bvb = self._pil_bbox_mm(pil_val, box_val_text, ppi)
        bval_h = bvb - bvt
        box_val_center_y = box_lbl_y + box_lbl_h / 2
        box_val_y = box_val_center_y - bval_h / 2
        self._draw_text_top_left(pdf, gw_value_x, box_val_y,
                                  box_val_text, 'CentSchbook', '', value_font_pt, pil_val, ppi)

        # 虚线（两行文字中间）
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.3)
        dash_x = x_mm + w_mm * 0.101
        end_x = dash_x + w_mm * 0.44
        cx = dash_x
        while cx < end_x:
            pdf.line(cx, info_center_y, min(cx + 2.5, end_x), info_center_y)
            cx += 5.0

    # ── 标签内容叠加 ─────────────────────────────────────────────────────────

    def _draw_label_overlay(self, pdf, sku_config, label_x, label_y, label_w, label_h,
                             barcode1_text, barcode2_text,
                             bc1_xf, bc1_yf, bc1_wf, bc1_hf,
                             bc2_xf, bc2_yf, bc2_wf, bc2_hf,
                             bar_yf, bar_hf,
                             gw_text=None, gw_xf=None, gw_yf=None, gw_hf=None,
                             box_text=None, box_xf=None, box_yf=None, box_hf=None):
        """在标签模板上叠加绘制动态内容"""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        def fmm(xf, yf):
            return label_x + xf * label_w, label_y + yf * label_h

        # G.W./N.W. 文字
        if gw_text is not None:
            font_h_mm = label_h * gw_hf
            font_px = int(font_h_mm * px_per_mm)
            font_pt = font_px * 72.0 / ppi
            pil_f = ImageFont.truetype(self.font_paths['CentSchbook'], font_px)
            tx, ty = fmm(gw_xf, gw_yf)
            self._draw_text_top_left(pdf, tx, ty, gw_text, 'CentSchbook', '', font_pt, pil_f, ppi)

        # BOX SIZE 文字
        if box_text is not None:
            font_h_mm = label_h * box_hf
            font_px = int(font_h_mm * px_per_mm)
            font_pt = font_px * 72.0 / ppi
            pil_f = ImageFont.truetype(self.font_paths['CentSchbook'], font_px)
            tx, ty = fmm(box_xf, box_yf)
            self._draw_text_top_left(pdf, tx, ty, box_text, 'CentSchbook', '', font_pt, pil_f, ppi)

        # 条形码
        for bc_text, xf, yf, wf, hf in [
            (barcode1_text, bc1_xf, bc1_yf, bc1_wf, bc1_hf),
            (barcode2_text, bc2_xf, bc2_yf, bc2_wf, bc2_hf),
        ]:
            bc_w_mm = label_w * wf
            bc_h_mm = label_h * hf
            bc_w_px = int(bc_w_mm * px_per_mm)
            bc_h_px = int(bc_h_mm * px_per_mm)
            try:
                bc_img = generate_barcode_image(bc_text, bc_w_px, bc_h_px)
                bx, by = fmm(xf, yf)
                pdf.image(bc_img, x=bx, y=by, w=bc_w_mm, h=bc_h_mm)
                # 条形码下方文字标签
                font_h_mm = label_h * 0.04
                font_px_bc = int(font_h_mm * px_per_mm)
                font_pt_bc = font_px_bc * 72.0 / ppi
                if font_px_bc >= 4:
                    pil_bc = ImageFont.truetype(self.font_paths['CentSchbook'], font_px_bc)
                    self._draw_text_top_center(
                        pdf, bx + bc_w_mm / 2, by + bc_h_mm + 1.0,
                        bc_text, 'CentSchbook', '', font_pt_bc, pil_bc, ppi)
            except Exception:
                pass

        # 黑色底条 + 产地文字
        bar_y = label_y + label_h * bar_yf
        bar_h = label_h * bar_hf
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(label_x, bar_y, label_w, bar_h, style='F')

        origin_text = sku_config.side_text.get('origin_text', 'MADE IN CHINA')
        font_h_mm = bar_h * 0.5
        font_px = int(font_h_mm * px_per_mm)
        font_pt = font_px * 72.0 / ppi
        if font_px >= 4:
            pil_orig = ImageFont.truetype(self.font_paths['CentSchbook'], font_px)
            origin_y = bar_y + bar_h * 0.2
            r, g, b = sku_config.background_color
            self._draw_text_top_center(
                pdf, label_x + label_w / 2, origin_y,
                origin_text, 'CentSchbook', '', font_pt, pil_orig, ppi,
                color=(r, g, b))
