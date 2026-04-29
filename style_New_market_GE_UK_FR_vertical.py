# -*- coding: utf-8 -*-
"""
MCombo 标准样式 - 将原有的 BoxMarkEngine 转换为样式类
"""
from fpdf import FPDF
from PIL import Image, ImageFont
from style_base import BoxMarkStyle, StyleRegistry
import general_functions

@StyleRegistry.register
class MComboStandardStyle(BoxMarkStyle):
    """MCombo 标准箱唛样式（原始样式）"""

    def get_style_name(self):
        return "new_market_vertical"

    def get_style_description(self):
        return "new_market 侧唛垂直箱唛样式"

    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'color', 'product', 'size', 'side_text', 'sku_name', 'box_number',
                'sponge_verified']

    def get_layout_config_mm(self, sku_config):
        """mm-based layout for fpdf2 (mirrors get_layout_config in mm; vertical variant)"""
        l_mm = sku_config.l_cm * 10
        w_mm = sku_config.w_cm * 10
        h_mm = sku_config.h_cm * 10
        half_w_mm = w_mm / 2

        x0, x1 = 0.0, l_mm
        x2, x3 = l_mm + w_mm, 2 * l_mm + w_mm
        # Vertical: top-left panel is l×w (full-width flap); others use half_w
        y0 = 0.0
        y1 = half_w_mm          # partial top starts here
        y2 = w_mm               # body starts after full-width top flap
        y3 = w_mm + h_mm        # bottom flap starts

        return {
            "flap_top_front1": (x0, y0, l_mm, w_mm),       # big top-left panel (l × w)
            "flap_top_side1":  (x1, y1, w_mm, half_w_mm),
            "flap_top_front2": (x2, y1, l_mm, half_w_mm),
            "flap_top_side2":  (x3, y1, w_mm, half_w_mm),
            "panel_front1":    (x0, y2, l_mm, h_mm),
            "panel_side1":     (x1, y2, w_mm, h_mm),
            "panel_front2":    (x2, y2, l_mm, h_mm),
            "panel_side2":     (x3, y2, w_mm, h_mm),
            "flap_btm_front1": (x0, y3, l_mm, half_w_mm),
            "flap_btm_side1":  (x1, y3, w_mm, half_w_mm),
            "flap_btm_front2": (x2, y3, l_mm, w_mm),       # big bottom-right panel (l × w)
            "flap_btm_side2":  (x3, y3, w_mm, half_w_mm),
        }

    def register_fonts(self, pdf: FPDF):
        pdf.add_font('Calibri',     '', self.font_paths['calibri'])
        pdf.add_font('CalibriBold', '', self.font_paths['calibri_bold'])
        pdf.add_font('ITCDemi',     '', self.font_paths['itc_demi'])
        pdf.add_font('Courier',     '', self.font_paths['courier'])

    def draw_to_pdf(self, pdf: FPDF, sku_config):
        """Render all panels as fully-vector fpdf2 output (vertical variant)."""
        layout = self.get_layout_config_mm(sku_config)

        # Fill all panel backgrounds
        r, g, b = sku_config.background_color
        pdf.set_fill_color(r, g, b)
        for _, (x, y, w, h) in layout.items():
            pdf.rect(x, y, w, h, style='F')

        # Front panels (×2) — fully vector
        for key in ('panel_front1', 'panel_front2'):
            x, y, w, h = layout[key]
            self._draw_front_panel_v(pdf, sku_config, x, y, w, h)

        # Side panels — fully vector (rotated 90°)
        x, y, w, h = layout['panel_side1']
        self._draw_side_panel_v(pdf, sku_config, x, y, w, h,
                                show_legal=True, rotate_deg=90)
        x, y, w, h = layout['panel_side2']
        self._draw_side_panel_v(pdf, sku_config, x, y, w, h,
                                show_legal=False, rotate_deg=90)

        # Left flaps
        self._draw_left_flaps_v(pdf, sku_config, layout)

        # Right flaps
        self._draw_right_flaps_v(pdf, sku_config, layout)

        # Side up/down — blank (already filled with background)

    def _load_resources(self):
        """加载 MCombo 标准样式的图片资源"""

        self.res_base = self.base_dir / 'assets' / 'New-market' / '样式一' / '矢量文件'
        self.resources = {
            'icon_left_2_panel': Image.open(self.res_base / '顶部-左-2箱.png').convert('RGBA'),
            'icon_left_3_panel': Image.open(self.res_base / '顶部-左-3箱.png').convert('RGBA'),
            'icon_left_4_panel': Image.open(self.res_base / '顶部-左-4箱.png').convert('RGBA'),
            'icon_right_2-1_panel': Image.open(self.res_base / '顶部-右-2-1.png').convert('RGBA'),
            'icon_right_2-2_panel': Image.open(self.res_base / '顶部-右-2-2.png').convert('RGBA'),
            'icon_right_3-1_panel': Image.open(self.res_base / '顶部-右-3-1.png').convert('RGBA'),
            'icon_right_3-2_panel': Image.open(self.res_base / '顶部-右-3-2.png').convert('RGBA'),
            'icon_right_3-3_panel': Image.open(self.res_base / '顶部-右-3-3.png').convert('RGBA'),
            'icon_right_4-1_panel': Image.open(self.res_base / '德文-顶部-右-4-1.png').convert('RGBA'),
            'icon_right_4-2_panel': Image.open(self.res_base / '德文-顶部-右-4-2.png').convert('RGBA'),
            'icon_right_4-3_panel': Image.open(self.res_base / '德文-顶部-右-4-3.png').convert('RGBA'),
            'icon_right_4-4_panel': Image.open(self.res_base / '德文-顶部-右-4-4.png').convert('RGBA'),
            'icon_top_box_number_2_1': Image.open(self.res_base / '顶部-右-2-1.png').convert('RGBA'),
            'icon_top_box_number_2_2': Image.open(self.res_base / '顶部-右-2-2.png').convert('RGBA'),
            'icon_top_box_number_3_1': Image.open(self.res_base / '顶部-右-3-1.png').convert('RGBA'),
            'icon_top_box_number_3_2': Image.open(self.res_base / '顶部-box-3-2.png').convert('RGBA'),
            'icon_top_box_number_3_3': Image.open(self.res_base / '顶部-box-3-3.png').convert('RGBA'),
            'icon_top_box_number_4_1': Image.open(self.res_base / '德文-顶部-右-4-1.png').convert('RGBA'),
            'icon_top_box_number_4_2': Image.open(self.res_base / '德文-顶部-右-4-2.png').convert('RGBA'),
            'icon_top_box_number_4_3': Image.open(self.res_base / '德文-顶部-右-4-3.png').convert('RGBA'),
            'icon_top_box_number_4_4': Image.open(self.res_base / '德文-顶部-右-4-4.png').convert('RGBA'),
            # 'icon_trademark': Image.open(res_base / '正唛logo.png').convert('RGBA'),
            # 'icon_company': Image.open(res_base / '正唛公司信息.png').convert('RGBA'),
            'icon_box_number_1': Image.open(self.res_base / '正唛 Box 1.png').convert('RGBA'),
            'icon_box_number_2': Image.open(self.res_base / '正唛 Box 2.png').convert('RGBA'),
            'icon_box_number_3': Image.open(self.res_base / '正唛 Box 3.png').convert('RGBA'),
            'icon_box_number_4': Image.open(self.res_base / '正唛 Box 4.png').convert('RGBA'),
            # 'icon_side_label_box': Image.open(res_base / '侧唛标签框.png').convert('RGBA'),
            # 'icon_side_logo': Image.open(res_base / '侧唛logo.png').convert('RGBA'),
            'icon_side_text_box': general_functions.make_it_pure_black(Image.open(self.res_base / '条码框-去掉竖线.png').convert('RGBA')),
            'icon_side_sponge': Image.open(self.res_base / '海绵认证.png').convert('RGBA'),
            'icon_side_FSC': general_functions.make_it_pure_black(Image.open(self.res_base / 'FSC.png').convert('RGBA')),
            'icon_company_bg_left': general_functions.make_it_pure_black(Image.open(self.res_base / '正唛-公司名称.png').convert('RGBA')),
            'icon_company_bg_right': general_functions.make_it_pure_black(Image.open(self.res_base / '正唛-邮箱.png').convert('RGBA')),
            # 'legal_icon_2_1': make_it_pure_black(Image.open(res_base / legal_icon).convert('RGBA')),
            # 'legal_icon_2_2': general_functions.make_it_pure_black(Image.open(res_base / legal_icon).convert('RGBA')),
            'legal_icon_3_1': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-3-1.png').convert('RGBA')),
            'legal_icon_3_2': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-3-2CC.png').convert('RGBA')),
            'legal_icon_3_3': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-3-2CK.png').convert('RGBA')),
            'legal_icon_3_4': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-3-2RoHs.png').convert('RGBA')),
            'legal_icon_3_5': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-3-2回收.png').convert('RGBA')),
            'legal_icon_3_6': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-3-2绿点.png').convert('RGBA')),
            'legal_icon_4': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-4.png').convert('RGBA')),
        }

    def _load_fonts(self):
        """加载字体路径"""
        font_base = self.base_dir / 'assets' / 'Mcombo' / '样式一' / '箱唛字体'
        self.font_paths = {
            'calibri': str(font_base / 'calibri.ttf'),
            'calibri_bold': str(font_base / 'calibri-bold.ttf'),
            'itc_demi': str(font_base / 'avantgardelt-demi.ttf'),
            'courier': str(font_base / 'cour.ttf'),
            'side_font_label': str(font_base / 'avantgardelt-demi.ttf'),
            'side_font_bold': str(font_base / 'calibri-bold.ttf'),
            'side_font_barcode': str(font_base / 'calibri_blod.ttf')
        }

        # 字体大小相对比例
        self.font_ratios = {
            'color_font': 51 / 1332,
            'product_font': 180 / 1332,
            'size_font': 60 / 1332,
            'regular_font': 40 / 1332,
            'side_font': 40 / 1332
        }

        return self.font_paths

    # ── fpdf2 vector helper methods ─────────────────────────────────────────────

    def _get_logo_file(self, sku_config):
        """Return the front-panel logo path based on market flag (GE/FR/UK)."""
        if getattr(sku_config, 'GE', 0) == 1:
            return self.res_base / '正唛logo-ELEGUE.png'
        elif getattr(sku_config, 'FR', 0) == 1 or getattr(sku_config, 'UK', 0) == 1:
            return self.res_base / '正唛logo-MCombo.png'
        return self.res_base / '正唛logo-MCombo.png'

    @staticmethod
    def _pil_bbox_mm(pil_font, text, ppi):
        """Measure text bbox using anchor='ls' and convert to mm.
        top is negative (above baseline), bottom is positive (below baseline)."""
        left, top, right, bottom = pil_font.getbbox(text, anchor='ls')
        px_per_mm = ppi / 25.4
        return left / px_per_mm, top / px_per_mm, right / px_per_mm, bottom / px_per_mm

    def _draw_text_top_left(self, pdf, x_mm, y_top_mm, text,
                             font_family, font_style, font_size_pt, pil_font, ppi,
                             color=(0, 0, 0)):
        """Draw text anchored at visual top-left (like PIL anchor='la')."""
        _, top_mm, _, _ = self._pil_bbox_mm(pil_font, text, ppi)
        baseline_y = y_top_mm + (-top_mm)
        r, g, b = color
        pdf.set_text_color(r, g, b)
        pdf.set_font(font_family, font_style, font_size_pt)
        pdf.text(x_mm, baseline_y, text)

    def _draw_text_top_center(self, pdf, x_center_mm, y_top_mm, text,
                               font_family, font_style, font_size_pt, pil_font, ppi,
                               color=(0, 0, 0)):
        """Draw text anchored at visual top-center (horizontally centered)."""
        left_mm, top_mm, right_mm, _ = self._pil_bbox_mm(pil_font, text, ppi)
        text_w_mm = right_mm - left_mm
        x_mm = x_center_mm - text_w_mm / 2.0
        baseline_y = y_top_mm + (-top_mm)
        r, g, b = color
        pdf.set_text_color(r, g, b)
        pdf.set_font(font_family, font_style, font_size_pt)
        pdf.text(x_mm, baseline_y, text)

    def _draw_text_mid_center(self, pdf, x_center_mm, y_center_mm, text,
                               font_family, font_style, font_size_pt, pil_font, ppi,
                               color=(0, 0, 0)):
        """Draw text anchored at visual center (like PIL anchor='mm')."""
        left_mm, top_mm, right_mm, bottom_mm = self._pil_bbox_mm(pil_font, text, ppi)
        text_w_mm = right_mm - left_mm
        text_h_mm = bottom_mm - top_mm
        x_mm = x_center_mm - text_w_mm / 2.0
        baseline_y = y_center_mm + (-top_mm) - text_h_mm / 2.0
        r, g, b = color
        pdf.set_text_color(r, g, b)
        pdf.set_font(font_family, font_style, font_size_pt)
        pdf.text(x_mm, baseline_y, text)

    # ── vector panel drawing methods ────────────────────────────────────────────

    def _draw_front_panel_v(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm):
        """Draw the front panel with vector text and raster bottom bar."""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        # ── 1. Logo (centered top, h/3 height, max w/2 width) ──
        logo_file = self._get_logo_file(sku_config)
        icon_tm = general_functions.make_it_pure_black(
            Image.open(logo_file).convert('RGBA'))
        _tm_w, _tm_h = icon_tm.size

        tm_h_mm = h_mm / 3.0
        tm_w_mm = tm_h_mm * _tm_w / _tm_h
        max_tm_w = w_mm / 2.0
        if tm_w_mm > max_tm_w:
            tm_w_mm = max_tm_w
            tm_h_mm = tm_w_mm * _tm_h / _tm_w

        tm_x = x_mm + (w_mm - tm_w_mm) / 2.0
        tm_y = y_mm
        pdf.image(icon_tm, x=tm_x, y=tm_y, w=tm_w_mm, h=tm_h_mm)

        # ── 2. Bottom bar — fully vector ──
        bottom_h_mm = sku_config.bottom_gb_h * 10.0
        self._draw_bottom_bar_v(pdf, sku_config, x_mm, y_mm, w_mm, h_mm)

        # ── 3. Color text (right top, black rounded background) ──
        color_text = str(sku_config.color)
        color_size_px = int(h_mm * px_per_mm * self.font_ratios['color_font'])
        color_size_pt = color_size_px * 72.0 / ppi
        pil_color = ImageFont.truetype(self.font_paths['calibri_bold'],
                                       color_size_px)

        left_c, top_c, right_c, bottom_c = self._pil_bbox_mm(
            pil_color, color_text, ppi)
        text_w = right_c - left_c
        text_h = bottom_c - top_c

        color_x = x_mm + w_mm - text_w - 40.0   # 4cm from right
        color_y = y_mm + 40.0                     # 4cm from top

        pad_x_mm = 8.0             # 0.8cm
        pad_y_top_mm = 4.0 * 0.7   # match mcombo pattern
        pad_y_bot_mm = 4.0 * 1.4
        radius_mm = 16 * 25.4 / ppi

        rect_x = color_x - pad_x_mm
        rect_y = color_y - pad_y_top_mm
        rect_w = text_w + 2 * pad_x_mm
        rect_h = text_h + pad_y_top_mm + pad_y_bot_mm

        pdf.set_fill_color(0, 0, 0)
        pdf.rect(rect_x, rect_y, rect_w, rect_h,
                 style='F', round_corners=True, corner_radius=radius_mm)

        self._draw_text_top_left(pdf, color_x, color_y, color_text,
                                  'CalibriBold', '', color_size_pt, pil_color, ppi,
                                  color=(161, 142, 102))

        # ── 4. Product text (centered, dynamic size) ──
        product_text = sku_config.product
        product_size_px = int(h_mm * px_per_mm * self.font_ratios['product_font'])
        pil_product = ImageFont.truetype(self.font_paths['itc_demi'],
                                         product_size_px)

        p_left, p_top, p_right, p_bottom = pil_product.getbbox(product_text)
        product_w_px = p_right - p_left
        max_product_w_px = int(w_mm * px_per_mm * 0.85)
        if product_w_px > max_product_w_px:
            product_size_px = int(product_size_px * max_product_w_px / product_w_px)
            pil_product = ImageFont.truetype(self.font_paths['itc_demi'],
                                             product_size_px)
            p_left, p_top, p_right, p_bottom = pil_product.getbbox(product_text)
            product_w_px = p_right - p_left
        product_size_pt = product_size_px * 72.0 / ppi
        product_w_mm = product_w_px / px_per_mm

        # ── 5. Size text ──
        size_text = getattr(sku_config, 'size', None) or " "
        size_size_px = int(h_mm * px_per_mm * self.font_ratios['size_font'])
        size_size_pt = size_size_px * 72.0 / ppi
        pil_size = ImageFont.truetype(self.font_paths['calibri_bold'],
                                      size_size_px)

        # ── 6. Group layout: product + decorative line + size ──
        product_em_h_mm = product_size_px / px_per_mm   # em-square height
        size_em_h_mm = size_size_px / px_per_mm
        gap_mm = 10.0       # 1cm
        line_h_mm = 3.0     # 0.3cm
        line_w_mm = product_w_mm * 0.85
        product_offset_mm = 5.0   # 0.5cm up

        total_group_h = product_em_h_mm + line_h_mm + size_em_h_mm + gap_mm * 2
        logo_bottom = y_mm + tm_h_mm
        bottom_section_top = y_mm + h_mm - bottom_h_mm
        available_h = bottom_section_top - logo_bottom
        group_start_y = logo_bottom + (available_h - total_group_h) / 2.0

        # Product text (shifted up ~0.5cm, matching original offset)
        cx = x_mm + w_mm / 2.0
        self._draw_text_top_center(pdf, cx,
                                    group_start_y - product_offset_mm,
                                    product_text,
                                    'ITCDemi', '', product_size_pt,
                                    pil_product, ppi)

        # Decorative ellipse (black)
        line_y = group_start_y + product_em_h_mm + gap_mm
        line_x = cx - line_w_mm / 2.0
        pdf.set_fill_color(0, 0, 0)
        pdf.ellipse(line_x, line_y, line_w_mm, line_h_mm, style='F')

        # Size text
        size_y = line_y + line_h_mm + gap_mm
        self._draw_text_top_center(pdf, cx, size_y, size_text,
                                    'CalibriBold', '', size_size_pt,
                                    pil_size, ppi)

    def _draw_left_flaps_v(self, pdf, sku_config, layout):
        """Draw left flap panels (vertical variant).
        flap_top_front1 (full-width l×w): icon_top_box_number at 18cm.
        flap_btm_front1 (half-width l×half_w): blank."""
        total = sku_config.box_number['total_boxes']
        current = sku_config.box_number['current_box']
        icon = self.resources[f'icon_top_box_number_{total}_{current}']

        x, y, w, h = layout['flap_top_front1']
        target_h_mm = 180.0   # 18cm
        max_w_mm = w * 0.8
        icon_w = target_h_mm * icon.width / icon.height
        if icon_w > max_w_mm:
            icon_w = max_w_mm
            icon_h = icon_w * icon.height / icon.width
        else:
            icon_h = target_h_mm

        ix = x + (w - icon_w) / 2.0
        iy = y + (h - icon_h) / 2.0
        pdf.image(icon, x=ix, y=iy, w=icon_w, h=icon_h)
        # flap_btm_front1 is blank (already background-filled)

    def _draw_right_flaps_v(self, pdf, sku_config, layout):
        """Draw right flap panels (vertical variant).
        flap_top_front2 (half-width l×half_w): blank.
        flap_btm_front2 (full-width l×w): 180° rotated icon at 17cm."""
        total = sku_config.box_number['total_boxes']
        current = sku_config.box_number['current_box']
        icon = self.resources[f'icon_top_box_number_{total}_{current}']
        icon_rotated = icon.rotate(180, expand=True)

        # flap_top_front2 is blank (already background-filled)
        x, y, w, h = layout['flap_btm_front2']
        target_h_mm = 170.0   # 17cm
        max_w_mm = w * 0.8
        icon_w = target_h_mm * icon.width / icon.height
        if icon_w > max_w_mm:
            icon_w = max_w_mm
            icon_h = icon_w * icon.height / icon.width
        else:
            icon_h = target_h_mm

        ix = x + (w - icon_w) / 2.0
        iy = y + (h - icon_h) / 2.0
        pdf.image(icon_rotated, x=ix, y=iy, w=icon_w, h=icon_h)

    # ── fully-vector bottom bar ───────────────────────────────────────────────

    def _draw_bottom_bar_v(self, pdf, sku_config, x_mm, y_mm, panel_w_mm, panel_h_mm):
        """Draw the front-panel bottom bar entirely in fpdf2 (S-curve + vector text)."""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        h_right_mm = 100.0
        h_left_mm  = 50.0
        icon_h_mm  = 16.0
        sku_margin_mm  = 5.0
        margin_1cm_mm  = 10.0
        margin_4cm_mm  = 40.0
        margin_10cm_mm = 100.0

        panel_bottom = y_mm + panel_h_mm

        brand_bg, brand_texts = general_functions.draw_company_brand_for_pdf(
            sku_config, sku_config.company_name, sku_config.contact_info,
            self.font_paths, self.resources)
        brand_w_mm = brand_bg.width * icon_h_mm / brand_bg.height
        left_section_w_mm = margin_1cm_mm + brand_w_mm + margin_4cm_mm

        max_sku_h_mm = h_right_mm * 0.8
        start_px = int(180 * ppi / 72)
        min_px   = int(max_sku_h_mm * px_per_mm * 0.15)
        sku_pil  = None
        sku_w_mm = 0.0
        sku_size_pt = float(180)

        current_px = start_px
        while current_px >= min_px:
            pf = ImageFont.truetype(self.font_paths['calibri_bold'], current_px)
            bb = pf.getbbox(sku_config.sku_name)
            sw_mm = (bb[2] - bb[0]) / px_per_mm
            sh_mm = (bb[3] - bb[1]) / px_per_mm
            if sw_mm <= (panel_w_mm - left_section_w_mm - 2 * sku_margin_mm) and sh_mm <= max_sku_h_mm:
                sku_pil     = pf
                sku_w_mm    = sw_mm
                sku_size_pt = current_px * 72.0 / ppi
                break
            current_px -= 5
        if sku_pil is None:
            sku_pil     = ImageFont.truetype(self.font_paths['calibri_bold'], min_px)
            bb          = sku_pil.getbbox(sku_config.sku_name)
            sku_w_mm    = (bb[2] - bb[0]) / px_per_mm
            sku_size_pt = min_px * 72.0 / ppi

        sku_block_left_mm = panel_w_mm - sku_margin_mm - sku_w_mm - sku_margin_mm
        space_is_enough   = left_section_w_mm <= sku_block_left_mm

        if space_is_enough:
            x3_mm = left_section_w_mm - margin_10cm_mm
            x4_mm = left_section_w_mm
            brand_x_mm = x_mm + margin_1cm_mm
            brand_y_mm = panel_bottom - h_right_mm 
            sku_area_l = x_mm + x4_mm - 6 * sku_margin_mm
            sku_area_r = x_mm + panel_w_mm - sku_margin_mm
        else:
            x4_mm = max(left_section_w_mm, panel_w_mm - sku_margin_mm - sku_w_mm - sku_margin_mm)
            x3_mm = max(margin_1cm_mm, x4_mm - margin_10cm_mm)
            brand_x_mm = x_mm + margin_1cm_mm
            brand_y_mm = panel_bottom - h_left_mm / 2.0 - icon_h_mm / 2.0 - 15.0
            sku_area_l = x_mm + x4_mm - 6 * sku_margin_mm
            sku_area_r = x_mm + panel_w_mm - sku_margin_mm

        abs_x3 = x_mm + x3_mm
        abs_x4 = x_mm + x4_mm
        y_left_top  = panel_bottom - h_left_mm
        y_right_top = panel_bottom - h_right_mm

        pdf.set_fill_color(0, 0, 0)
        pdf.rect(x_mm,   y_left_top,  x3_mm,              h_left_mm,  style='F')
        pdf.rect(abs_x4, y_right_top, panel_w_mm - x4_mm, h_right_mm, style='F')

        curve = []
        for i in range(21):
            t  = i / 20.0
            cx = abs_x3 + (abs_x4 - abs_x3) * t
            ts = t * t * (3 - 2 * t)
            cy = y_left_top + (y_right_top - y_left_top) * ts
            curve.append((cx, cy))
        curve.append((abs_x4, panel_bottom))
        curve.append((abs_x3, panel_bottom))
        pdf.polygon(curve, style='F')

        box_icon   = self.resources[f"icon_box_number_{sku_config.box_number['current_box']}"]
        box_icon_h = h_right_mm * 0.25
        box_icon_w = box_icon_h * box_icon.width / box_icon.height
        pdf.image(box_icon,
                  x=x_mm + margin_1cm_mm,
                  y=y_left_top + (h_left_mm - box_icon_h) / 2.0,
                  w=box_icon_w, h=box_icon_h)

        pdf.image(brand_bg, x=brand_x_mm, y=brand_y_mm, w=brand_w_mm, h=icon_h_mm)

        img_scale = icon_h_mm / brand_bg.height
        for bt in brand_texts:
            fs_pt = bt['font_size_px'] * 72.0 / ppi
            pf    = ImageFont.truetype(bt['font_path'], bt['font_size_px'])
            self._draw_text_mid_center(pdf,
                                       brand_x_mm + bt['x_px'] * img_scale,
                                       brand_y_mm + bt['y_px'] * img_scale,
                                       bt['text'], 'CalibriBold', '', fs_pt, pf, ppi,
                                       color=bt['color'])

        sku_cx = (sku_area_l + sku_area_r) / 2.0
        sku_cy = y_right_top + h_right_mm / 2.0 + 3.0
        self._draw_text_mid_center(pdf, sku_cx, sku_cy, sku_config.sku_name,
                                   'CalibriBold', '', sku_size_pt, sku_pil, ppi,
                                   color=(161, 142, 102))

    # ── fully-vector side panel ──────────────────────────────────────────────

    def _draw_side_panel_v(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm,
                            show_legal, rotate_deg=0):
        """Draw the side panel entirely in fpdf2 vector text + images."""
        cx = x_mm + w_mm / 2.0
        cy = y_mm + h_mm / 2.0

        if rotate_deg == 90:
            o_x = cx - h_mm / 2.0
            o_y = cy - w_mm / 2.0
            eff_w, eff_h = h_mm, w_mm
            h_left_mm, logo_h_mm = 80.0, 40.0
        else:
            o_x, o_y = x_mm, y_mm
            eff_w, eff_h = w_mm, h_mm
            h_left_mm, logo_h_mm = 100.0, 50.0

        def _draw():
            self._draw_side_content_v(pdf, sku_config,
                                      o_x, o_y, eff_w, eff_h,
                                      show_legal, h_left_mm, logo_h_mm)

        if rotate_deg == 90:
            with pdf.rotation(angle=90, x=cx, y=cy):
                _draw()
        else:
            _draw()

    def _draw_side_content_v(self, pdf, sku_config,
                              o_x, o_y, eff_w, eff_h,
                              show_legal, h_left_mm, logo_h_mm):
        """Low-level side panel drawing in a given coordinate frame."""
        ppi       = sku_config.ppi
        px_per_mm = ppi / 25.4

        h_right_mm    = h_left_mm / 2.0
        sku_margin_mm = 5.0
        margin_10mm   = 100.0
        max_sku_h_mm  = h_left_mm * 0.8
        start_px      = int((180 if h_left_mm >= 100 else 160) * ppi / 72)
        min_px        = int(max_sku_h_mm * px_per_mm * 0.15)
        panel_bottom  = o_y + eff_h

        sku_pil     = None
        sku_w_mm    = 0.0
        sku_size_pt = start_px * 72.0 / ppi
        max_sku_block_mm = eff_w - margin_10mm - 40.0

        current_px = start_px
        while current_px >= min_px:
            pf    = ImageFont.truetype(self.font_paths['calibri_bold'], current_px)
            bb    = pf.getbbox(sku_config.sku_name)
            sw_mm = (bb[2] - bb[0]) / px_per_mm
            sh_mm = (bb[3] - bb[1]) / px_per_mm
            if sw_mm <= max_sku_block_mm - 2 * sku_margin_mm and sh_mm <= max_sku_h_mm:
                sku_pil     = pf
                sku_w_mm    = sw_mm
                sku_size_pt = current_px * 72.0 / ppi
                break
            current_px -= 5
        if sku_pil is None:
            sku_pil     = ImageFont.truetype(self.font_paths['calibri_bold'], min_px)
            bb          = sku_pil.getbbox(sku_config.sku_name)
            sku_w_mm    = (bb[2] - bb[0]) / px_per_mm
            sku_size_pt = min_px * 72.0 / ppi

        sku_block_w_mm = max(60.0, min(sku_w_mm + 2 * sku_margin_mm, max_sku_block_mm))
        x3_mm = sku_block_w_mm
        x4_mm = x3_mm + margin_10mm
        if x4_mm > eff_w - 10.0:
            x4_mm = eff_w - 10.0
            x3_mm = x4_mm - margin_10mm
            sku_block_w_mm = x3_mm

        abs_x3      = o_x + x3_mm
        abs_x4      = o_x + x4_mm
        y_left_top  = panel_bottom - h_left_mm
        y_right_top = panel_bottom - h_right_mm

        pdf.set_fill_color(0, 0, 0)
        pdf.rect(o_x,    y_left_top,  x3_mm,          h_left_mm,  style='F')
        pdf.rect(abs_x4, y_right_top, eff_w - x4_mm,  h_right_mm, style='F')
        curve = []
        for i in range(21):
            t  = i / 20.0
            cx = abs_x3 + (abs_x4 - abs_x3) * t
            ts = t * t * (3 - 2 * t)
            cy = y_left_top + (y_right_top - y_left_top) * ts
            curve.append((cx, cy))
        curve.append((abs_x4, panel_bottom))
        curve.append((abs_x3, panel_bottom))
        pdf.polygon(curve, style='F')

        sku_cx = o_x + sku_block_w_mm / 2.0 + sku_margin_mm * 3
        sku_cy = y_left_top + h_left_mm / 2.0 + 3.0
        self._draw_text_mid_center(pdf, sku_cx, sku_cy, sku_config.sku_name,
                                   'CalibriBold', '', sku_size_pt, sku_pil, ppi,
                                   color=(161, 142, 102))

        logo_file = self._get_logo_file(sku_config)
        logo_img  = general_functions.make_it_pure_black(
            Image.open(logo_file).convert('RGBA'))
        logo_w_mm  = logo_h_mm * logo_img.width / logo_img.height
        margin_side_mm = logo_h_mm * 0.6
        pdf.image(logo_img,
                  x=o_x + eff_w - logo_w_mm - margin_side_mm,
                  y=o_y + margin_side_mm,
                  w=logo_w_mm, h=logo_h_mm)

        table_h_mm     = 80.0
        bottom_gb_h_mm = sku_config.bottom_gb_h * 10.0
        gap_above_mm   = 20.0 if h_left_mm >= 100.0 else 10.0
        elem_y   = panel_bottom - bottom_gb_h_mm - gap_above_mm - table_h_mm
        gap_mm   = 3.0
        current_x = o_x + 30.0

        def _embed_h(res_key):
            img = self.resources[res_key]
            w   = table_h_mm * img.width / img.height
            return img, w

        if getattr(sku_config, 'sponge_verified', False):
            sp_img, sp_w = _embed_h('icon_side_sponge')
            pdf.image(sp_img, x=current_x, y=elem_y, w=sp_w, h=table_h_mm)
            current_x += sp_w + gap_mm

        if getattr(sku_config, 'show_fsc', False):
            fs_img, fs_w = _embed_h('icon_side_FSC')
            pdf.image(fs_img, x=current_x, y=elem_y, w=fs_w, h=table_h_mm)
            current_x += fs_w + gap_mm

        raw_box   = self.resources['icon_side_text_box']
        box_w_mm  = table_h_mm * raw_box.width / raw_box.height
        pdf.image(raw_box, x=current_x, y=elem_y, w=box_w_mm, h=table_h_mm)
        self._draw_barcode_box_v(pdf, sku_config,
                                  current_x, elem_y, box_w_mm, table_h_mm)

        if show_legal and getattr(sku_config, 'legal_data', None):
            if getattr(sku_config, 'GE', 0) == 1:
                legal_icon_file = self.res_base / '法律标-2-1-GE.png'
            else:
                legal_icon_file = self.res_base / '法律标-2-2-UK-FR.png'
            legal_icon_2_2 = general_functions.make_it_pure_black(
                Image.open(legal_icon_file).convert('RGBA'))

            legal_w_mm      = 224.0
            right_margin_mm = 20.0
            legal_x = o_x + eff_w - legal_w_mm - right_margin_mm

            buffer_mm = 10.0
            if legal_x < abs_x4 - 2 * buffer_mm:
                legal_y = panel_bottom - 120.0 - 140.0
            else:
                legal_y = panel_bottom - 70.0 - 140.0

            self._draw_legal_v(pdf, sku_config, legal_x, legal_y, legal_icon_2_2)

    def _draw_barcode_box_v(self, pdf, sku_config,
                             box_x, box_y, box_w_mm, box_h_mm):
        """Draw the side-panel barcode section as vector text + raster barcodes."""
        ppi       = sku_config.ppi
        px_per_mm = ppi / 25.4
        th = box_h_mm

        label_size_px  = int(th * px_per_mm * 0.081)
        bold_size_px   = int(th * px_per_mm * 0.095)
        barcode_txt_px = int(th * px_per_mm * 0.058)

        label_size_pt  = label_size_px  * 72.0 / ppi
        bold_size_pt   = bold_size_px   * 72.0 / ppi
        barcode_txt_pt = barcode_txt_px * 72.0 / ppi

        pil_label   = ImageFont.truetype(self.font_paths['side_font_label'],   label_size_px)
        pil_bold    = ImageFont.truetype(self.font_paths['side_font_bold'],    bold_size_px)
        pil_barcode = ImageFont.truetype(self.font_paths['side_font_barcode'], barcode_txt_px)

        gw   = sku_config.side_text.get('gw_value', '')
        nw   = sku_config.side_text.get('nw_value', '')
        l_in = getattr(sku_config, 'l_in', sku_config.l_cm / 2.54)
        w_in = getattr(sku_config, 'w_in', sku_config.w_cm / 2.54)
        h_in = getattr(sku_config, 'h_in', sku_config.h_cm / 2.54)
        gw_text  = f"G.W./N.W.: {gw} / {nw} lbs"
        dim_text = f"BOX SIZE: {l_in:.1f}'' x {w_in:.1f}'' x {h_in:.1f}''"

        text_x = box_x + box_w_mm * 0.55
        self._draw_text_top_left(pdf, text_x, box_y + th * 0.044,
                                  gw_text, 'ITCDemi', '', label_size_pt, pil_label, ppi)
        self._draw_text_top_left(pdf, text_x, box_y + th * 0.214,
                                  dim_text, 'ITCDemi', '', label_size_pt, pil_label, ppi)

        barcode_h_mm = th * 0.35
        barcode_h_px = int(barcode_h_mm * px_per_mm)
        barcode_y_mm = box_y + th * 0.42
        barcode_txt_y = box_y + th * 0.76

        sku_bc  = general_functions.generate_barcode_image_1(
            sku_config.sku_name, height=barcode_h_px)
        sn_code = sku_config.side_text.get('sn_code', '')
        sn_bc   = general_functions.generate_barcode_image_1(
            sn_code, height=barcode_h_px) if sn_code else None

        total_bc_w = sku_bc.width + (sn_bc.width if sn_bc else sku_bc.width)
        line_frac  = sku_bc.width / total_bc_w if total_bc_w > 0 else 0.5
        line_x     = box_x + box_w_mm * line_frac

        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(3.0 * 25.4 / ppi)
        pdf.line(line_x, box_y + th * 0.36, line_x, box_y + th * 0.855)

        sku_zone_w = line_x - box_x
        sku_bc_w   = sku_zone_w * 0.9
        sku_bc_img = sku_bc.resize(
            (int(sku_bc_w * px_per_mm), barcode_h_px), Image.Resampling.LANCZOS)
        sku_bc_x   = box_x + (sku_zone_w - sku_bc_w) / 2
        pdf.image(sku_bc_img, x=sku_bc_x, y=barcode_y_mm, w=sku_bc_w, h=barcode_h_mm)
        self._draw_text_top_center(
            pdf, sku_bc_x + sku_bc_w / 2, barcode_txt_y,
            sku_config.sku_name, 'CalibriBold', '', barcode_txt_pt, pil_barcode, ppi)

        if sn_bc and sn_code:
            sn_zone_w = box_x + box_w_mm - line_x
            sn_bc_w   = sn_zone_w * 0.9
            sn_bc_img = sn_bc.resize(
                (int(sn_bc_w * px_per_mm), barcode_h_px), Image.Resampling.LANCZOS)
            sn_bc_x   = line_x + (sn_zone_w - sn_bc_w) / 2
            pdf.image(sn_bc_img, x=sn_bc_x, y=barcode_y_mm, w=sn_bc_w, h=barcode_h_mm)
            self._draw_text_top_center(
                pdf, sn_bc_x + sn_bc_w / 2, barcode_txt_y,
                sn_code, 'CalibriBold', '', barcode_txt_pt, pil_barcode, ppi)

        made_y = box_y + th * 0.885
        self._draw_text_top_center(
            pdf, box_x + box_w_mm / 2, made_y,
            'MADE IN CHINA', 'CalibriBold', '', bold_size_pt, pil_bold, ppi)

    def _draw_legal_v(self, pdf, sku_config, x_mm, y_mm, legal_icon_2_2):
        """Draw the legal label component entirely in fpdf2."""
        ppi = sku_config.ppi

        box_w_mm = 224.0
        box_h_mm = 140.0
        row1_h   = 57.0
        row2_h   = 20.0
        row3_h   = 63.0

        lw_thin  = 3.0 * 25.4 / ppi
        lw_thick = 4.0 * 25.4 / ppi

        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(lw_thick)
        pdf.rect(x_mm, y_mm, box_w_mm, box_h_mm, style='D')

        pdf.set_line_width(lw_thin)
        pdf.line(x_mm, y_mm + row1_h, x_mm + box_w_mm, y_mm + row1_h)
        pdf.line(x_mm, y_mm + row1_h + row2_h,
                 x_mm + box_w_mm, y_mm + row1_h + row2_h)

        scale_r1 = 0.85
        if getattr(sku_config, 'GE', 0) == 1:
            scale_r1 = scale_r1 / 2 - 0.15
        icon_r1_h = row1_h * scale_r1
        icon_r1_w = icon_r1_h * legal_icon_2_2.width / legal_icon_2_2.height

        margin_right_mm = 8.0
        gap_mm          = 10.0
        v_line_x_rel    = box_w_mm - margin_right_mm - icon_r1_w - gap_mm / 2
        abs_v_line_x    = x_mm + v_line_x_rel

        pdf.set_line_width(lw_thin)
        pdf.line(abs_v_line_x, y_mm, abs_v_line_x, y_mm + row1_h)

        icon_r1_x = x_mm + box_w_mm - margin_right_mm - icon_r1_w
        icon_r1_y = y_mm + (row1_h - icon_r1_h) / 2
        pdf.image(legal_icon_2_2, x=icon_r1_x, y=icon_r1_y, w=icon_r1_w, h=icon_r1_h)

        text_area_w = v_line_x_rel - gap_mm / 2
        if sku_config.legal_data:
            self._draw_legal_text_v(pdf, sku_config,
                                    x_mm + 7.5, y_mm, text_area_w, row1_h)

        row2_icons = []
        icon_3_1   = self.resources['legal_icon_3_1']
        i31_h = row2_h * 0.85
        i31_w = i31_h * icon_3_1.width / icon_3_1.height
        row2_icons.append((icon_3_1, i31_w, i31_h))

        check_list = [
            (getattr(sku_config, 'legal_3_2', 0), 'legal_icon_3_2'),
            (getattr(sku_config, 'legal_3_3', 0), 'legal_icon_3_3'),
            (getattr(sku_config, 'legal_3_4', 0), 'legal_icon_3_4'),
            (getattr(sku_config, 'legal_3_5', 0), 'legal_icon_3_5'),
            (getattr(sku_config, 'legal_3_6', 0), 'legal_icon_3_6'),
        ]
        for is_on, key in check_list:
            if is_on == 1:
                img = self.resources[key]
                ih  = row2_h * 0.4
                iw  = ih * img.width / img.height
                row2_icons.append((img, iw, ih))

        icon_gap_mm = 7.0
        total_w = (sum(iw for _, iw, _ in row2_icons)
                   + icon_gap_mm * (len(row2_icons) - 1))
        cur_x   = x_mm + (box_w_mm - total_w) / 2
        row2_y  = y_mm + row1_h
        for img, iw, ih in row2_icons:
            pdf.image(img, x=cur_x, y=row2_y + (row2_h - ih) / 2, w=iw, h=ih)
            cur_x += iw + icon_gap_mm

        icon_4  = self.resources['legal_icon_4']
        i4_h    = row3_h * 0.85
        i4_w    = i4_h * icon_4.width / icon_4.height
        row3_y  = y_mm + row1_h + row2_h
        pdf.image(icon_4,
                  x=x_mm + (box_w_mm - i4_w) / 2,
                  y=row3_y + (row3_h - i4_h) / 2,
                  w=i4_w, h=i4_h)

    def _draw_legal_text_v(self, pdf, sku_config, x_mm, y_mm,
                            area_w_mm, area_h_mm):
        """Render legal key-value data as bold label + regular value in fpdf2."""
        import textwrap as _tw
        ppi       = sku_config.ppi
        px_per_mm = ppi / 25.4

        base_px    = 28
        line_ratio = 1.3
        reg_path   = self.font_paths['calibri']
        bold_path  = self.font_paths['calibri_bold']

        def _build_lines(size_px):
            pil_r  = ImageFont.truetype(reg_path,  size_px)
            pil_b  = ImageFont.truetype(bold_path, size_px)
            avg_cw = pil_r.getlength('a') / px_per_mm
            pad_l  = 30.0 / px_per_mm
            pad_r  = 35.0 / px_per_mm
            avail  = area_w_mm - pad_l - pad_r
            climit = max(1, int(avail / avg_cw))
            lines  = []
            for label, value in sku_config.legal_data.items():
                full_label = f'{label}: '
                lbl_w_mm   = pil_b.getlength(full_label) / px_per_mm
                wrapped    = _tw.wrap(full_label + str(value), width=climit)
                for i, ln in enumerate(wrapped):
                    lines.append(dict(
                        text=ln, is_first=(i == 0),
                        label=full_label if i == 0 else '',
                        lbl_w=lbl_w_mm   if i == 0 else 0.0,
                    ))
            return lines, size_px, pad_l

        cur_px = base_px
        while cur_px > 12:
            lines, cur_px, pad_l = _build_lines(cur_px)
            line_h = cur_px * line_ratio / px_per_mm
            if len(lines) * line_h <= (area_h_mm - 5.0):
                break
            cur_px -= 2

        lines, cur_px, pad_l = _build_lines(cur_px)
        line_h   = cur_px * line_ratio / px_per_mm
        size_pt  = cur_px * 72.0 / ppi
        pil_r    = ImageFont.truetype(reg_path,  cur_px)
        pil_b    = ImageFont.truetype(bold_path, cur_px)

        total_h  = len(lines) * line_h
        extra_y  = 0.2 * 25.4
        curr_y   = y_mm + (area_h_mm - total_h) / 2 + extra_y
        curr_x   = x_mm + pad_l

        for ln in lines:
            if ln['is_first'] and ln['label']:
                self._draw_text_top_left(pdf, curr_x, curr_y, ln['label'],
                                         'CalibriBold', '', size_pt, pil_b, ppi)
                content = ln['text'][len(ln['label']):]
                if content:
                    self._draw_text_top_left(pdf, curr_x + ln['lbl_w'], curr_y,
                                             content, 'Calibri', '', size_pt, pil_r, ppi)
            else:
                self._draw_text_top_left(pdf, curr_x, curr_y, ln['text'],
                                         'Calibri', '', size_pt, pil_r, ppi)
            curr_y += line_h
