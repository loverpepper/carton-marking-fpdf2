# -*- coding: utf-8 -*-
"""
Barberpub 全搭盖样式 - 将原有的 BoxMarkEngine 转换为样式类
"""
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import pathlib as Path
from style_base import BoxMarkStyle, StyleRegistry
import general_functions
from general_functions import generate_barcode_image


@StyleRegistry.register
class BarberpubFullOverlapStyle(BoxMarkStyle):
    '''Barberpub 全搭盖样式'''
    
    def get_style_name(self):
        return "barberpub_fulloverlap"
    
    def get_style_description(self):
        return "Barberpub 全搭盖箱唛样式"
    
    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'ppi', 'color', 'product', 'side_text', 'sku_name', 'box_number']
    
    def get_layout_config(self, sku_config):
        '''
        Barberpub 全搭盖样式 - 5块布局（4列3行）
        '''
        
        x0 = 0
        x1 = sku_config.l_px
        x2 = sku_config.l_px + sku_config.w_px
        x3 = sku_config.l_px * 2 + sku_config.w_px
        
        y0 = 0
        y1 = sku_config.w_px
        y2 = sku_config.w_px + sku_config.h_px
        
        return {
            # 第一行：顶盖层 (Top Flaps)
            "flap_top_front1":  (x0, y0, sku_config.l_px, sku_config.w_px),
            "flap_top_side1": (x1, y0, sku_config.w_px, sku_config.w_px),
            "flap_top_front2":  (x2, y0, sku_config.l_px, sku_config.w_px),
            "flap_top_side2": (x3, y0, sku_config.w_px, sku_config.w_px),

            # 第二行：正身层 (Main Body)
            "panel_front1":     (x0, y1, sku_config.l_px, sku_config.h_px),
            "panel_side1":    (x1, y1, sku_config.w_px, sku_config.h_px),
            "panel_front2":     (x2, y1, sku_config.l_px, sku_config.h_px),
            "panel_side2":    (x3, y1, sku_config.w_px, sku_config.h_px),

            # 第三行：底盖层 (Bottom Flaps)
            "flap_btm_front1":  (x0, y2, sku_config.l_px, sku_config.w_px),
            "flap_btm_side1": (x1, y2, sku_config.w_px, sku_config.w_px),
            "flap_btm_front2":  (x2, y2, sku_config.l_px, sku_config.w_px),
            "flap_btm_side2": (x3, y2, sku_config.w_px, sku_config.w_px),
        }
    
    def get_panels_mapping(self, sku_config):
        """定义每个区域应该粘贴哪个面板"""
        
        return {
            "flap_top_front1": "left_up",
            "flap_top_side1": "blank",
            "flap_top_front2": "right_up",
            "flap_top_side2": "blank",
            "panel_front1": "front",
            "panel_side1": "side",
            "panel_front2": "front",
            "panel_side2": "side",
            "flap_btm_front1": "left_down",
            "flap_btm_side1": "blank",
            "flap_btm_front2": "right_down",
            "flap_btm_side2": "blank",
        }
        
    # ── fpdf2 required abstract methods (hybrid PIL → PDF) ──────────────────

    def get_layout_config_mm(self, sku_config):
        """mm-based layout for fpdf2 (mirrors get_layout_config in mm)"""
        l_mm = sku_config.l_cm * 10
        w_mm = sku_config.w_cm * 10
        h_mm = sku_config.h_cm * 10

        x0, x1 = 0.0, l_mm
        x2, x3 = l_mm + w_mm, 2 * l_mm + w_mm
        y0, y1, y2 = 0.0, w_mm, w_mm + h_mm

        return {
            "flap_top_front1": (x0, y0, l_mm, w_mm),
            "flap_top_side1":  (x1, y0, w_mm, w_mm),
            "flap_top_front2": (x2, y0, l_mm, w_mm),
            "flap_top_side2":  (x3, y0, w_mm, w_mm),
            "panel_front1":    (x0, y1, l_mm, h_mm),
            "panel_side1":     (x1, y1, w_mm, h_mm),
            "panel_front2":    (x2, y1, l_mm, h_mm),
            "panel_side2":     (x3, y1, w_mm, h_mm),
            "flap_btm_front1": (x0, y2, l_mm, w_mm),
            "flap_btm_side1":  (x1, y2, w_mm, w_mm),
            "flap_btm_front2": (x2, y2, l_mm, w_mm),
            "flap_btm_side2":  (x3, y2, w_mm, w_mm),
        }

    def register_fonts(self, pdf: FPDF):
        pdf.add_font('CentSchbook', '', self.font_paths['CentSchbook BT'])
        pdf.add_font('DroidSans',   '', self.font_paths['Droid Sans Bold'])
        pdf.add_font('CalibriB',    '', self.font_paths['Calibri Bold'])

    def draw_to_pdf(self, pdf: FPDF, sku_config):
        """Native fpdf2 vector drawing – all text is editable / searchable."""
        layout = self.get_layout_config_mm(sku_config)

        r, g, b = sku_config.background_color
        pdf.set_fill_color(r, g, b)
        for _, (x, y, w, h) in layout.items():
            pdf.rect(x, y, w, h, style='F')

        l_mm = sku_config.l_cm * 10
        w_mm = sku_config.w_cm * 10
        h_mm = sku_config.h_cm * 10

        x0 = 0.0
        x1 = l_mm
        x2 = l_mm + w_mm
        x3 = 2 * l_mm + w_mm
        y1 = w_mm          # flap height = w_mm (full overlap)

        # Two front panels
        self._draw_front_panel_v(pdf, sku_config, x0, y1, l_mm, h_mm)
        self._draw_front_panel_v(pdf, sku_config, x2, y1, l_mm, h_mm)

        # Two side panels
        self._draw_side_panel_v(pdf, sku_config, x1, y1, w_mm, h_mm)
        self._draw_side_panel_v(pdf, sku_config, x3, y1, w_mm, h_mm)

        # Left-up flap (and right-down = 180° rotated copy)
        self._draw_flap_left_up_v(pdf, sku_config, x0, 0.0, l_mm, w_mm)
        self._draw_flap_right_down_v(pdf, sku_config, x2, y1 + h_mm, l_mm, w_mm)

    # ── fpdf2 vector helper methods ─────────────────────────────────────────

    def _get_resource_path(self, key):
        """Return the resource file path (pathlib.Path)."""
        res_base = self.base_dir / 'assets' / 'Barberpub' / '全搭盖' / '矢量文件'
        mapping = {
            'icon_logo':           res_base / '正唛logo.png',
            'icon_top_logo':       res_base / '顶盖logo信息.png',
            'icon_attention_info': res_base / '全搭盖开箱注意事项.png',
            'icon_company':        res_base / '正唛公司信息.png',
            'icon_webside':        res_base / '侧唛网址.png',
            'icon_side_label':     res_base / '侧唛标签_窄.png',
            'icon_slogan':         res_base / '正唛宣传语.png',
            'icon_box_info':       res_base / '正唛多箱选择框.png',
        }
        return mapping[key]

    def _get_font_size_v(self, text, font_key, target_width_mm, ppi):
        """Return (font_size_pt, pil_font) so text fits target_width_mm."""
        font_key_map = {
            'CentSchbook': 'CentSchbook BT',
            'DroidSans':   'Droid Sans Bold',
            'CalibriB':    'Calibri Bold',
        }
        path = self.font_paths[font_key_map.get(font_key, font_key)]
        target_px = int(target_width_mm * ppi / 25.4)
        size_px = general_functions.get_max_font_size(text, path, target_px)
        size_pt = size_px * 72.0 / ppi
        pil_font = ImageFont.truetype(path, size_px)
        return size_pt, pil_font

    def _get_font_size_constrained_v(self, text, font_key, target_w_mm, max_h_mm, ppi):
        """Same as _get_font_size_v with additional max_height constraint."""
        font_key_map = {
            'CentSchbook': 'CentSchbook BT',
            'DroidSans':   'Droid Sans Bold',
            'CalibriB':    'Calibri Bold',
        }
        path = self.font_paths[font_key_map.get(font_key, font_key)]
        target_px = int(target_w_mm * ppi / 25.4)
        max_h_px = int(max_h_mm * ppi / 25.4)
        size_px = general_functions.get_max_font_size(
            text, path, target_px, max_height=max_h_px)
        size_pt = size_px * 72.0 / ppi
        pil_font = ImageFont.truetype(path, size_px)
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

    # ── 正面面板 (vector) ────────────────────────────────────────────────────

    def _draw_front_panel_v(self, pdf: FPDF, sku_config, x_mm, y_mm, w_mm, h_mm):
        """Draw front (正唛) panel with native fpdf2 calls."""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4
        margin_top = 30.0
        margin_left = 30.0
        margin_right = 27.0

        # 1. Logo (top-left)
        icon_logo = self._get_resource_path('icon_logo')
        logo_h_mm = h_mm * 0.11
        with Image.open(icon_logo) as img:
            orig_w, orig_h = img.size
        logo_w_mm = logo_h_mm * orig_w / orig_h
        pdf.image(icon_logo, x=x_mm + margin_left, y=y_mm + margin_top,
                  w=logo_w_mm, h=logo_h_mm)

        # 2. Company info (top-right)
        icon_company = self._get_resource_path('icon_company')
        company_h_mm = h_mm * 0.048
        with Image.open(icon_company) as img:
            orig_w, orig_h = img.size
        company_w_mm = company_h_mm * orig_w / orig_h
        pdf.image(icon_company,
                  x=x_mm + w_mm - company_w_mm - margin_right,
                  y=y_mm + margin_top,
                  w=company_w_mm, h=company_h_mm)

        # 3. Product name (DroidSans, centred at 48% height)
        product_text = sku_config.product
        prod_pt, pil_prod = self._get_font_size_constrained_v(
            product_text, 'DroidSans', w_mm * 0.78, h_mm * 0.28, ppi)
        left_p, top_p, right_p, bottom_p = self._pil_bbox_mm(pil_prod, product_text, ppi)
        text_w_mm = right_p - left_p
        prod_h_mm = bottom_p - top_p
        text_x = x_mm + (w_mm - text_w_mm) / 2

        # 4. Slogan image below product name
        icon_slogan = self._get_resource_path('icon_slogan')
        slogan_w_mm_target = w_mm * 0.38
        with Image.open(icon_slogan) as img:
            s_orig_w, s_orig_h = img.size
        slogan_h_mm = slogan_w_mm_target * s_orig_h / s_orig_w
        vertical_gap = 20.0  # ~2 cm

        total_center_h = prod_h_mm + vertical_gap + slogan_h_mm
        center_y_start = y_mm + h_mm * 0.48 - total_center_h / 2

        self._draw_text_top_left(pdf, text_x, center_y_start,
                                  product_text, 'DroidSans', '', prod_pt, pil_prod, ppi)

        slogan_x = x_mm + (w_mm - slogan_w_mm_target) / 2
        slogan_y = center_y_start + prod_h_mm + vertical_gap
        pdf.image(icon_slogan, x=slogan_x, y=slogan_y, w=slogan_w_mm_target, h=slogan_h_mm)

        # 5. Bottom diagonal stripes (simplified as black rectangle)
        stripe_height_mm = 16.0
        bottom_margin_stripe = 12.0
        stripe_y = y_mm + h_mm - stripe_height_mm - bottom_margin_stripe
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(x_mm, stripe_y, w_mm, stripe_height_mm, style='F')

        margin_bottom = 50.0

        # 6. SKU code (bottom-left, CentSchbook)
        sku_text = sku_config.sku_name
        sku_pt, pil_sku = self._get_font_size_constrained_v(
            sku_text, 'CentSchbook', w_mm * 0.715, h_mm * 0.14, ppi)
        _, sku_top_mm, _, sku_bot_mm = self._pil_bbox_mm(pil_sku, sku_text, ppi)
        sku_h_mm = sku_bot_mm - sku_top_mm
        sku_y_top = y_mm + h_mm - margin_bottom - sku_h_mm - 14.0
        sku_x = x_mm + margin_left - 6.0
        self._draw_text_top_left(pdf, sku_x, sku_y_top,
                                  sku_text, 'CentSchbook', '', sku_pt, pil_sku, ppi)

        # 7. Colour text (above SKU)
        color_text = sku_config.color.upper()
        color_px = int(h_mm * px_per_mm * 0.06)
        color_pt = color_px * 72.0 / ppi
        pil_color = ImageFont.truetype(self.font_paths['CentSchbook BT'], color_px)
        _, c_top_mm, _, c_bot_mm = self._pil_bbox_mm(pil_color, color_text, ppi)
        color_h_mm = c_bot_mm - c_top_mm
        color_y_top = sku_y_top - color_h_mm - 3.0
        color_x = x_mm + margin_left
        self._draw_text_top_left(pdf, color_x, color_y_top,
                                  color_text, 'CentSchbook', '', color_pt, pil_color, ppi)

        # 8. Box number (bottom-right, rounded black bg, white text)
        box_text = (f"BOX {sku_config.box_number['current_box']} "
                    f"OF {sku_config.box_number['total_boxes']}")
        box_pt, pil_box = self._get_font_size_constrained_v(
            box_text, 'CentSchbook', w_mm * 0.155, h_mm * 0.048, ppi)
        left_b, top_b, right_b, bot_b = self._pil_bbox_mm(pil_box, box_text, ppi)
        box_w_mm = right_b - left_b
        box_h_mm = bot_b - top_b
        box_y_top = y_mm + h_mm - margin_bottom - box_h_mm - 14.0
        box_x = x_mm + w_mm - margin_right - box_w_mm

        pad_x = 5.0
        pad_y_top = 4.9
        pad_y_bot = 9.8
        radius_mm = 16 * 25.4 / ppi
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(box_x - pad_x, box_y_top - pad_y_top,
                 box_w_mm + 2 * pad_x, box_h_mm + pad_y_top + pad_y_bot,
                 style='F', round_corners=True, corner_radius=radius_mm)

        bg_r, bg_g, bg_b = sku_config.background_color
        self._draw_text_top_left(pdf, box_x, box_y_top,
                                  box_text, 'CentSchbook', '', box_pt, pil_box, ppi,
                                  color=(bg_r, bg_g, bg_b))

    # ── 侧面面板 (vector) ────────────────────────────────────────────────────

    def _draw_side_panel_v(self, pdf: FPDF, sku_config, x_mm, y_mm, w_mm, h_mm):
        """Draw side (侧唛) panel – content drawn rotated 90° into the cell."""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        # The side panel content is drawn in a landscape orientation
        # (width=h_mm, height=w_mm) then rotated 90° into the portrait cell.
        cw = h_mm   # content width
        ch = w_mm   # content height

        # SKU text
        sku_text = sku_config.sku_name
        sku_pt, pil_sku = self._get_font_size_constrained_v(
            sku_text, 'CentSchbook', cw * 0.92, ch * 0.55, ppi)
        sl, st, sr, sb = self._pil_bbox_mm(pil_sku, sku_text, ppi)
        sku_text_w = sr - sl
        sku_text_h = sb - st

        # Website icon
        webside_path = self._get_resource_path('icon_webside')
        webside_w = cw * 0.57
        with Image.open(webside_path) as img:
            ws_ow, ws_oh = img.size
        webside_h = webside_w * ws_oh / ws_ow

        # Side label
        label_path = self._get_resource_path('icon_side_label')
        label_w = cw * 0.28
        with Image.open(label_path) as img:
            lb_ow, lb_oh = img.size
        label_h = label_w * lb_oh / lb_ow

        bottom_icons_h = max(webside_h, label_h)
        min_gap_mm = 70.0  # ~7cm
        gap_sku_icons = max(ch * 0.22, min_gap_mm)
        total_h = sku_text_h + gap_sku_icons + bottom_icons_h
        start_y_content = (ch * 1.1 - total_h) / 2

        margin_side = 30.0  # ~3cm

        # Use pdf.rotation to draw landscape content rotated into portrait cell
        # Rotation centre = top-left of cell; rotate -90° (CCW) maps:
        #   content-x  → cell-y (from top)
        #   content-y  → cell-x (from right)
        rot_cx = x_mm
        rot_cy = y_mm
        with pdf.rotation(-90, rot_cx, rot_cy):
            # After -90° rotation, to place content at cell position:
            #   draw_x = y_mm,  draw_y = -(x_mm + w_mm)
            ox = rot_cy          # effective x origin after rotation
            oy = -(rot_cx + w_mm)  # effective y origin after rotation

            # SKU text
            sku_cx = ox + (cw - sku_text_w) / 2
            sku_cy = oy + start_y_content
            self._draw_text_top_left(pdf, sku_cx, sku_cy,
                                      sku_text, 'CentSchbook', '', sku_pt, pil_sku, ppi)

            # Website icon (bottom-left of content)
            web_x = ox + margin_side
            web_y = oy + start_y_content + sku_text_h + gap_sku_icons
            pdf.image(webside_path, x=web_x, y=web_y, w=webside_w, h=webside_h)

            # Side label (bottom-right of content)
            lbl_x = ox + cw - label_w - margin_side
            lbl_y = web_y + (webside_h - label_h) / 2
            pdf.image(label_path, x=lbl_x, y=lbl_y, w=label_w, h=label_h)

            # Overlay barcodes and origin bar on the label
            self._draw_label_overlay_v(
                pdf, sku_config, lbl_x, lbl_y, label_w, label_h,
                barcode1_text=sku_config.sku_name,
                barcode2_text=sku_config.side_text['sn_code'],
                bc1_xf=0.05,  bc1_yf=0.04, bc1_wf=0.533, bc1_hf=0.28,
                bc2_xf=0.60,  bc2_yf=0.04, bc2_wf=0.36,  bc2_hf=0.28,
                bar_yf=0.88,  bar_hf=0.12,
            )

    # ── 翻盖面板 (vector) ────────────────────────────────────────────────────

    def _draw_flap_left_up_v(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm):
        """Left-up flap: attention info, logo, SKU, dashed line, GW/NW & BOX SIZE."""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        if sku_config.w_cm > 30:
            self._draw_flap_tall_v(pdf, sku_config, x_mm, y_mm, w_mm, h_mm, ppi, px_per_mm)
        else:
            self._draw_flap_compact_v(pdf, sku_config, x_mm, y_mm, w_mm, h_mm, ppi, px_per_mm)

    def _draw_flap_tall_v(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm, ppi, px_per_mm):
        """Tall flap layout (w_cm > 30): stacked vertically."""
        # Attention icon (top, 95% width, centred)
        att_path = self._get_resource_path('icon_attention_info')
        att_w = w_mm * 0.95
        with Image.open(att_path) as img:
            a_ow, a_oh = img.size
        att_h = att_w * a_oh / a_ow
        att_margin_top = att_h * 0.50
        att_x = x_mm + (w_mm - att_w) / 2
        att_y = y_mm + att_margin_top
        pdf.image(att_path, x=att_x, y=att_y, w=att_w, h=att_h)
        att_bottom = att_y + att_h

        # Logo (below attention, 16% height)
        icon_logo = self._get_resource_path('icon_logo')
        logo_h = h_mm * 0.16
        with Image.open(icon_logo) as img:
            l_ow, l_oh = img.size
        logo_w = logo_h * l_ow / l_oh
        logo_y = att_bottom + 30.0  # ~3cm gap
        logo_x = x_mm + (w_mm - logo_w) / 2
        pdf.image(icon_logo, x=logo_x, y=logo_y, w=logo_w, h=logo_h)
        logo_bottom = logo_y + logo_h

        # Pre-calculate bottom info area
        margin_bottom = h_mm * 0.10
        info_font_h_mm = w_mm * 0.030 / px_per_mm * px_per_mm  # keep proportional
        bottom_info_h = margin_bottom + w_mm * 0.030 + 5.0

        # SKU name
        sku_text = sku_config.sku_name
        avail_for_sku = h_mm - (logo_bottom - y_mm) - bottom_info_h - 40.0
        sku_pt, pil_sku = self._get_font_size_constrained_v(
            sku_text, 'CentSchbook', w_mm * 0.90, avail_for_sku * 0.6, ppi)
        sl, st, sr, sb = self._pil_bbox_mm(pil_sku, sku_text, ppi)
        sku_w = sr - sl
        sku_h_v = sb - st
        sku_y = logo_bottom + (avail_for_sku - sku_h_v) * 0.35
        sku_x = x_mm + (w_mm - sku_w) / 2
        self._draw_text_top_left(pdf, sku_x, sku_y,
                                  sku_text, 'CentSchbook', '', sku_pt, pil_sku, ppi)

        # Dashed line below SKU
        dash_y = sku_y + sku_h_v + h_mm * 0.10
        dash_x_start = sku_x
        dash_x_end = sku_x + sku_w
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.3)
        cx = dash_x_start
        while cx < dash_x_end:
            pdf.line(cx, dash_y, min(cx + 2.0, dash_x_end), dash_y)
            cx += 3.5

        # Bottom info: G.W./N.W. and BOX SIZE with black-bg labels
        self._draw_flap_bottom_info(pdf, sku_config,
                                     x_mm, y_mm, w_mm, h_mm, ppi, px_per_mm,
                                     left_x_frac=0.09, right_x_frac=0.54,
                                     info_y=y_mm + h_mm - margin_bottom - w_mm * 0.030,
                                     label_h_mm=w_mm * 0.030,
                                     value_h_mm=w_mm * 0.025,
                                     gap_after_label=18.0)

    def _draw_flap_compact_v(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm, ppi, px_per_mm):
        """Compact flap layout (w_cm ≤ 30): attention top, then left logo / right content."""
        # Attention icon
        att_path = self._get_resource_path('icon_attention_info')
        att_w = w_mm * 0.95
        with Image.open(att_path) as img:
            a_ow, a_oh = img.size
        att_h = att_w * a_oh / a_ow
        att_margin_top = att_h * 0.50
        att_x = x_mm + (w_mm - att_w) / 2
        att_y = y_mm + att_margin_top
        pdf.image(att_path, x=att_x, y=att_y, w=att_w, h=att_h)
        content_start_y = att_y + att_h + 15.0

        left_ratio = 0.25
        left_w = w_mm * left_ratio
        right_w = w_mm * (1 - left_ratio)
        right_x = x_mm + left_w
        avail_h = (y_mm + h_mm) - content_start_y

        # Logo (left, vertically centred)
        icon_logo = self._get_resource_path('icon_logo')
        logo_h = avail_h * 0.40
        with Image.open(icon_logo) as img:
            l_ow, l_oh = img.size
        logo_w = logo_h * l_ow / l_oh
        logo_x = x_mm + (left_w - logo_w) / 2
        logo_y = content_start_y + (avail_h - logo_h) / 2
        pdf.image(icon_logo, x=logo_x, y=logo_y, w=logo_w, h=logo_h)

        # Right side: SKU
        margin_bottom_r = h_mm * 0.10
        info_label_h = w_mm * 0.022
        bottom_info_h = margin_bottom_r + info_label_h + 3.0
        avail_sku_h = (avail_h - bottom_info_h) * 0.45

        sku_text = sku_config.sku_name
        sku_pt, pil_sku = self._get_font_size_constrained_v(
            sku_text, 'CentSchbook', right_w * 0.90, avail_sku_h, ppi)
        sl, st, sr, sb = self._pil_bbox_mm(pil_sku, sku_text, ppi)
        sku_w = sr - sl
        sku_h_v = sb - st
        sku_y = content_start_y + avail_h * 0.10
        sku_x = right_x + (right_w - sku_w) * 0.35
        self._draw_text_top_left(pdf, sku_x, sku_y,
                                  sku_text, 'CentSchbook', '', sku_pt, pil_sku, ppi)

        # Dashed line
        dash_y = sku_y + sku_h_v + h_mm * 0.12
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.3)
        cx = sku_x
        while cx < sku_x + sku_w:
            pdf.line(cx, dash_y, min(cx + 2.0, sku_x + sku_w), dash_y)
            cx += 3.5

        # Bottom info
        info_lbl_y = dash_y + h_mm * 0.07
        value_h_mm = w_mm * 0.018
        gap_label = 8.0
        left_box_x = sku_x + right_w * 0.07
        right_box_x = right_x + right_w * 0.52

        self._draw_flap_bottom_info(pdf, sku_config,
                                     x_mm, y_mm, w_mm, h_mm, ppi, px_per_mm,
                                     left_x_frac=None, right_x_frac=None,
                                     info_y=info_lbl_y,
                                     label_h_mm=info_label_h,
                                     value_h_mm=value_h_mm,
                                     gap_after_label=gap_label,
                                     abs_left_x=left_box_x,
                                     abs_right_x=right_box_x)

    def _draw_flap_bottom_info(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm,
                                ppi, px_per_mm,
                                left_x_frac, right_x_frac, info_y,
                                label_h_mm, value_h_mm, gap_after_label,
                                abs_left_x=None, abs_right_x=None):
        """Draw G.W./N.W. and BOX SIZE labels with black-bg tags on a flap."""
        label_px = int(label_h_mm * px_per_mm)
        label_pt = label_px * 72.0 / ppi
        pil_lbl = ImageFont.truetype(self.font_paths['CentSchbook BT'], label_px)

        value_px = int(value_h_mm * px_per_mm)
        value_pt = value_px * 72.0 / ppi
        pil_val = ImageFont.truetype(self.font_paths['CentSchbook BT'], value_px)

        bg_r, bg_g, bg_b = sku_config.background_color

        # ── G.W./N.W. ──
        gw_label = "G.W./N.W."
        gl, gt, gr, gb = self._pil_bbox_mm(pil_lbl, gw_label, ppi)
        gw_lbl_w = gr - gl
        gw_lbl_h = gb - gt

        gw_x = abs_left_x if abs_left_x is not None else x_mm + w_mm * left_x_frac
        gw_y = info_y

        pad_x, pad_y_top, pad_y_bot = 5.0, 4.9, 9.8
        radius_mm = 16 * 25.4 / ppi
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(gw_x - pad_x, gw_y - pad_y_top,
                 gw_lbl_w + 2 * pad_x, gw_lbl_h + pad_y_top + pad_y_bot,
                 style='F', round_corners=True, corner_radius=radius_mm)
        self._draw_text_top_left(pdf, gw_x, gw_y,
                                  gw_label, 'CentSchbook', '', label_pt, pil_lbl, ppi,
                                  color=(bg_r, bg_g, bg_b))

        gw_value = (f"{sku_config.side_text['gw_value']} / "
                    f"{sku_config.side_text['nw_value']} LBS")
        vl, vt, vr, vb = self._pil_bbox_mm(pil_val, gw_value, ppi)
        val_h = vb - vt
        gw_val_x = gw_x + gw_lbl_w + gap_after_label
        gw_val_y = gw_y + gw_lbl_h / 2 - val_h / 2
        self._draw_text_top_left(pdf, gw_val_x, gw_val_y,
                                  gw_value, 'CentSchbook', '', value_pt, pil_val, ppi)

        # ── BOX SIZE ──
        box_label = "BOX SIZE"
        bl2, bt2, br2, bb2 = self._pil_bbox_mm(pil_lbl, box_label, ppi)
        box_lbl_w = br2 - bl2
        box_lbl_h = bb2 - bt2

        box_x = abs_right_x if abs_right_x is not None else x_mm + w_mm * right_x_frac
        box_y = info_y

        pdf.set_fill_color(0, 0, 0)
        pdf.rect(box_x - pad_x, box_y - pad_y_top,
                 box_lbl_w + 2 * pad_x, box_lbl_h + pad_y_top + pad_y_bot,
                 style='F', round_corners=True, corner_radius=radius_mm)
        self._draw_text_top_left(pdf, box_x, box_y,
                                  box_label, 'CentSchbook', '', label_pt, pil_lbl, ppi,
                                  color=(bg_r, bg_g, bg_b))

        l_in = sku_config.l_in
        w_in = sku_config.w_in
        h_in = sku_config.h_in
        dim_text = f'{l_in:.1f}" x {w_in:.1f}" x {h_in:.1f}"'
        bvl, bvt, bvr, bvb = self._pil_bbox_mm(pil_val, dim_text, ppi)
        bval_h = bvb - bvt
        dim_val_x = box_x + box_lbl_w + gap_after_label
        dim_val_y = box_y + box_lbl_h / 2 - bval_h / 2
        self._draw_text_top_left(pdf, dim_val_x, dim_val_y,
                                  dim_text, 'CentSchbook', '', value_pt, pil_val, ppi)

    def _draw_flap_right_down_v(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm):
        """Right-down flap: 180° rotated copy of left-up content."""
        # Draw the same content as left-up but rotated 180° around the cell centre
        cx = x_mm + w_mm / 2
        cy = y_mm + h_mm / 2
        with pdf.rotation(180, cx, cy):
            self._draw_flap_left_up_v(pdf, sku_config, x_mm, y_mm, w_mm, h_mm)

    # ── 标签叠加 (vector) ────────────────────────────────────────────────────

    def _draw_label_overlay_v(self, pdf, sku_config, label_x, label_y,
                               label_w, label_h,
                               barcode1_text, barcode2_text,
                               bc1_xf, bc1_yf, bc1_wf, bc1_hf,
                               bc2_xf, bc2_yf, bc2_wf, bc2_hf,
                               bar_yf, bar_hf):
        """Overlay barcodes and origin bar on a side label template."""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        def fmm(xf, yf):
            return label_x + xf * label_w, label_y + yf * label_h

        # Barcodes
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
                font_h_mm = label_h * 0.04
                font_px_bc = int(font_h_mm * px_per_mm)
                font_pt_bc = font_px_bc * 72.0 / ppi
                if font_px_bc >= 4:
                    pil_bc = ImageFont.truetype(self.font_paths['CentSchbook BT'], font_px_bc)
                    self._draw_text_top_center(
                        pdf, bx + bc_w_mm / 2, by + bc_h_mm + 1.0,
                        bc_text, 'CentSchbook', '', font_pt_bc, pil_bc, ppi)
            except Exception:
                pass

        # Black origin bar
        bar_y = label_y + label_h * bar_yf
        bar_h = label_h * bar_hf
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(label_x, bar_y, label_w, bar_h, style='F')

        origin_text = sku_config.side_text.get('origin_text', 'MADE IN CHINA')
        font_h_mm = bar_h * 0.5
        font_px = int(font_h_mm * px_per_mm)
        font_pt = font_px * 72.0 / ppi
        if font_px >= 4:
            pil_orig = ImageFont.truetype(self.font_paths['CentSchbook BT'], font_px)
            origin_y = bar_y + bar_h * 0.2
            bg_r, bg_g, bg_b = sku_config.background_color
            self._draw_text_top_center(
                pdf, label_x + label_w / 2, origin_y,
                origin_text, 'CentSchbook', '', font_pt, pil_orig, ppi,
                color=(bg_r, bg_g, bg_b))





### 历史代码文件，仅供参考原始的样式是什么
    def generate_all_panels(self, sku_config):
        """生成 Barberpub 全搭盖样式需要的所有面板"""
        
        canvas_front = self.generate_barberpub_front_panel(sku_config)
        canvas_side = self.generate_barberpub_side_panel(sku_config)
        canvas_left_up, canvas_left_down, canvas_right_up, canvas_right_down = self.generate_barberpub_left_panel(sku_config)
        canvas_blank = Image.new(sku_config.color_mode, (sku_config.w_px, sku_config.w_px), sku_config.background_color)


        return {
            "left_up": canvas_left_up,
            "left_down": canvas_left_down,
            "right_up": canvas_right_up,
            "right_down": canvas_right_down,
            "front": canvas_front,
            "side": canvas_side,
            "blank": canvas_blank,
        }
    
    
    def _load_resources(self):
        """加载 Barberpub 全搭盖样式的图片资源"""
        res_base = self.base_dir / 'assets' / 'Barberpub' / '全搭盖' / '矢量文件'
        
        self.resources = {
            'icon_logo': Image.open(res_base / '正唛logo.png').convert('RGBA'),
            'icon_top_logo': Image.open(res_base / '顶盖logo信息.png').convert('RGBA'),
            'icon_attention_info': Image.open(res_base / '全搭盖开箱注意事项.png').convert('RGBA'),
            'icon_company': Image.open(res_base / '正唛公司信息.png').convert('RGBA'),
            'icon_webside': Image.open(res_base / '侧唛网址.png').convert('RGBA'),
            'icon_side_label': Image.open(res_base / '侧唛标签_窄.png').convert('RGBA'),
            'icon_slogan': Image.open(res_base / '正唛宣传语.png').convert('RGBA'),
            'icon_box_info': Image.open(res_base / '正唛多箱选择框.png').convert('RGBA'),
        }
    
    def _load_fonts(self):
        """加载字体路径"""
        font_base = self.base_dir / 'assets' / 'Barberpub' / '全搭盖' / '箱唛字体'
        self.font_paths = {
            'CentSchbook BT': str(font_base / '111.ttf'),
            'Droid Sans Bold': str(font_base / 'CENSBKBI.TTF'),
            'Calibri Bold': str(font_base / 'calibri_blod.ttf'),

        }

    
    def generate_barberpub_left_panel(self, sku_config):
        """
        生成 Barberpub 全搭盖样式的左侧面板
        
        根据箱子宽度（w_cm）自动选择布局：
        - 宽度 > 30cm：使用上下结构（顶部注意事项、Logo、SKU、虚线、底部信息框）
        - 宽度 ≤ 30cm：使用简单结构（仅居中Logo）
        """
        # 创建空白画布，尺寸为箱子的长×宽
        canvas = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.w_px), sku_config.background_color)
        canvas_w, canvas_h = canvas.size
        
        # 准备四个面板（左上、左下、右上、右下）
        canvas_left_up = canvas.copy()
        canvas_left_down = canvas.copy()
        canvas_right_up = canvas.copy()
        icon_top_logo = self.resources['icon_top_logo']
        
        # 根据箱子宽度决定使用哪种布局结构
        if sku_config.w_cm > 30:
            # ========== 上下结构布局 ==========
            # 适用于较高的箱子（宽度>30cm），包含多个信息区域
            draw = ImageDraw.Draw(canvas_left_up)
            font_path_centschbook = self.font_paths['CentSchbook BT']
            
            # --- 区域 A: 顶部注意事项信息 ---
            # 显示开箱注意事项图标，位于顶部
            icon_attention = self.resources.get('icon_attention_info')
            if icon_attention:
                attention_w = int(canvas_w * 0.95)  # 图标宽度占画布95%
                attention_resized = general_functions.scale_by_width(icon_attention, attention_w)
                attention_h = attention_resized.height
                
                # 设置顶部边距：图标自身高度的50%
                attention_margin_top = int(attention_h * 0.50)
                attention_x = (canvas_w - attention_w) // 2  # 水平居中
                attention_y = attention_margin_top
                canvas_left_up.paste(attention_resized, (attention_x, attention_y), mask=attention_resized)
                
                # 记录注意事项底部位置，用于后续元素定位
                attention_bottom_y = attention_y + attention_h
            else:
                attention_bottom_y = 0
            
            # --- 区域 B: Logo（与注意事项间隔3cm）---
            # 显示公司Logo，位于注意事项下方
            icon_logo = self.resources['icon_logo']
            icon_logo_h_px = int(canvas_h * 0.16)  # Logo高度为画布高度的16%
            icon_logo_resized = general_functions.scale_by_height(icon_logo, icon_logo_h_px)
            
            logo_y = attention_bottom_y + int(3 * sku_config.dpi)  # 与注意事项间隔3cm
            logo_x = (canvas_w - icon_logo_resized.width) // 2  # 水平居中
            canvas_left_up.paste(icon_logo_resized, (logo_x, logo_y), mask=icon_logo_resized)
            
            # 记录Logo底部位置
            logo_bottom_y = logo_y + icon_logo_resized.height
            
            # --- 区域 C: 底部信息框（需要先计算高度）---
            # 预先计算底部信息框的尺寸，以便为SKU预留空间
            margin_bottom_px = int(canvas_h * 0.10)  # 底部边距为画布高度的10%
            info_font_frame_size = int(canvas_w * 0.030)  # 标签文字字号根据画布宽度调整（大大缩小）
            info_font_without_frame_size = int(canvas_w * 0.025)  # 具体值文字字号根据画布宽度调整（大大缩小）
            
            # 底部信息区域的总高度（包括边距）
            bottom_info_total_h = margin_bottom_px + info_font_frame_size + int(0.5 * sku_config.dpi)
            
            # --- 区域 D: SKU名称（动态计算位置）---
            # SKU名称是最重要的信息，需要尽可能大
            sku_text = sku_config.sku_name
            target_sku_w = int(canvas_w * 0.90)  # 目标宽度为画布90%
            
            # 计算SKU可用的垂直空间（Logo下方到底部信息框之间）
            available_space_for_sku = canvas_h - logo_bottom_y - bottom_info_total_h - int(4 * sku_config.dpi)
            
            # 获取在约束条件下的最大字号
            sku_font_size = general_functions.get_max_font_size(
                sku_text, font_path_centschbook, target_sku_w, max_height=int(available_space_for_sku * 0.6)
            )
            sku_font = ImageFont.truetype(font_path_centschbook, sku_font_size)
            
            # 计算SKU文字的实际尺寸
            sku_w = draw.textlength(sku_text, font=sku_font)
            bbox_sku = draw.textbbox((0, 0), sku_text, font=sku_font)
            sku_h = bbox_sku[3] - bbox_sku[1]  # 获取真实文字高度（不含基线偏移）
            
            # 在可用空间中偏上放置（35%位置），留出下方空间给虚线
            sku_y = logo_bottom_y + int((available_space_for_sku - sku_h) * 0.35)
            sku_x = (canvas_w - sku_w) // 2  # 水平居中
            draw.text((sku_x, sku_y), sku_text, font=sku_font, fill=(0, 0, 0))
            
            # --- 区域 E: 虚线（SKU下方）---
            # 在SKU下方绘制装饰性虚线
            dashed_line_y = sku_y + sku_h + int(canvas_h * 0.10)  # SKU和虚线间距为画布高度的10%
            dashed_line_x_start = sku_x  # 与SKU文字左对齐
            dashed_line_x_end = sku_x + sku_w  # 与SKU文字右对齐
            
            # 虚线样式参数
            dash_length = 20  # 每段虚线长度（像素）
            gap_length = 15   # 虚线间隙长度（像素）
            line_width = 3    # 虚线粗细（像素）
            
            # 绘制虚线
            current_x = dashed_line_x_start
            while current_x < dashed_line_x_end:
                next_x = min(current_x + dash_length, dashed_line_x_end)
                draw.line([(current_x, dashed_line_y), (next_x, dashed_line_y)], fill=(0, 0, 0), width=line_width)
                current_x = next_x + gap_length
            
            # --- 区域 F: 底部信息框 ---
            # 显示净毛重（G.W./N.W.）和箱子尺寸（BOX SIZE）
            info_font_frame = ImageFont.truetype(font_path_centschbook, info_font_frame_size)
            info_font_without_frame = ImageFont.truetype(font_path_centschbook, info_font_without_frame_size)
            
            # 左侧：净毛重信息
            gw_text = "G.W./N.W."  # 标签文字
            weight_text = f"{sku_config.side_text['gw_value']} / {sku_config.side_text['nw_value']} LBS"  # 具体值
            
            # 计算标签文字宽度
            bbox_gw = draw.textbbox((0, 0), gw_text, font=info_font_frame)
            bbox_gw_width = bbox_gw[2] - bbox_gw[0]
            
            # 定位左侧信息框（根据canvas_w动态调整，约9%位置）
            left_box_x = int(canvas_w * 0.09)  # 起始位置为画布宽度的9%
            left_box_y = canvas_h - margin_bottom_px - info_font_frame_size
            
            # 绘制黑色圆角背景框
            bbox_gw_pos = (left_box_x, left_box_y)
            draw = general_functions.draw_rounded_bg_for_text(
                draw, bbox_gw, sku_config, bbox_gw_pos,
                bg_color=(0, 0, 0), padding_cm=(0.7, 0.6), radius=16
            )
            # 在黑色背景上绘制白色标签文字
            draw.text(bbox_gw_pos, gw_text, font=info_font_frame, fill=sku_config.background_color)
            
            # 在标签右侧绘制具体重量值（黑色文字）
            bbox_weight_x = left_box_x + bbox_gw_width + int(1.8 * sku_config.dpi)  # 与标签间隔1.8cm
            bbox_weight_y = left_box_y + int((info_font_frame_size - info_font_without_frame_size) / 2)  # 垂直居中对齐
            draw.text((bbox_weight_x, bbox_weight_y), weight_text, font=info_font_without_frame, fill=(0, 0, 0))
            
            # 右侧：箱子尺寸信息
            box_size_text = "BOX SIZE"  # 标签文字
            l_in = sku_config.l_in
            w_in = sku_config.w_in
            h_in = sku_config.h_in
            dimension_text = f'{l_in:.1f}" x {w_in:.1f}" x {h_in:.1f}"'  # 尺寸值（英寸）
            
            # 计算标签文字宽度
            bbox_box = draw.textbbox((0, 0), box_size_text, font=info_font_frame)
            bbox_box_w = bbox_box[2] - bbox_box[0]
            
            # 定位右侧信息框（根据canvas_w动态调整，约57%位置）
            right_box_x = int(canvas_w * 0.54)  # 起始位置为画布宽度的54%
            right_box_y = canvas_h - margin_bottom_px - info_font_frame_size
            
            # 绘制黑色圆角背景框
            bbox_box_pos = (right_box_x, right_box_y)
            draw = general_functions.draw_rounded_bg_for_text(
                draw, bbox_box, sku_config, bbox_box_pos,
                bg_color=(0, 0, 0), padding_cm=(0.7, 0.6), radius=16
            )
            # 在黑色背景上绘制白色标签文字
            draw.text(bbox_box_pos, box_size_text, font=info_font_frame, fill=sku_config.background_color)
            
            # 在标签右侧绘制具体尺寸值（黑色文字）
            dim_y = right_box_y + int((info_font_frame_size - info_font_without_frame_size) / 2)  # 垂直居中对齐
            dim_x = right_box_x + bbox_box_w + int(1.8 * sku_config.dpi)  # 与标签间隔1.8cm
            draw.text((dim_x, dim_y), dimension_text, font=info_font_without_frame, fill=(0, 0, 0))
        else:
            # ========== 左右结构布局 ==========
            # 适用于较矮的箱子（宽度≤30cm）
            # 顶部：注意事项图标（横跨整个画布）
            # 下方左侧：Logo | 下方右侧：SKU名称、虚线、净毛重和箱号信息
            draw = ImageDraw.Draw(canvas_left_up)
            font_path_centschbook = self.font_paths['CentSchbook BT']
            
            # --- 区域 A: 顶部注意事项信息（与上下结构一致）---
            icon_attention = self.resources.get('icon_attention_info')
            if icon_attention:
                attention_w = int(canvas_w * 0.95)  # 图标宽度占画布95%
                attention_resized = general_functions.scale_by_width(icon_attention, attention_w)
                attention_h = attention_resized.height
                
                # 设置顶部边距：图标自身高度的50%
                attention_margin_top = int(attention_h * 0.50)
                attention_x = (canvas_w - attention_w) // 2  # 水平居中
                attention_y = attention_margin_top
                canvas_left_up.paste(attention_resized, (attention_x, attention_y), mask=attention_resized)
                
                # 记录注意事项底部位置，用于后续元素定位
                content_start_y = attention_y + attention_h + int(1.5 * sku_config.dpi)  # 与注意事项间隔1.5cm
            else:
                content_start_y = int(canvas_h * 0.15)
            
            # 定义左右区域分割比例（从content_start_y开始）
            left_area_ratio = 0.25  # 左侧Logo区域占25%
            right_area_ratio = 0.75  # 右侧内容区域占75%
            
            left_area_w = int(canvas_w * left_area_ratio)
            right_area_w = int(canvas_w * right_area_ratio)
            right_area_x_start = left_area_w
            
            # 可用高度（去除顶部注意事项区域）
            available_h = canvas_h - content_start_y
            
            # ========== 左侧区域：Logo ==========
            icon_logo = self.resources['icon_logo']
            # Logo高度为可用高度的40%
            icon_logo_h = int(available_h * 0.40)
            icon_logo_resized = general_functions.scale_by_height(icon_logo, icon_logo_h)
            
            # Logo在左侧区域内居中（垂直方向在可用区域内居中）
            logo_x = (left_area_w - icon_logo_resized.width) // 2
            logo_y = content_start_y + (available_h - icon_logo_resized.height) // 2
            canvas_left_up.paste(icon_logo_resized, (logo_x, logo_y), mask=icon_logo_resized)
            
            # ========== 右侧区域：内容 ==========
            # 计算字号（大幅缩小，基于画布宽度而非右侧区域宽度）
            margin_bottom_px = int(canvas_h * 0.10)  # 底部边距
            info_font_frame_size = int(canvas_w * 0.022)  # 标签文字（大幅缩小）
            info_font_without_frame_size = int(canvas_w * 0.018)  # 具体值文字（大幅缩小）
            
            # 预先计算底部信息框高度
            bottom_info_total_h = margin_bottom_px + info_font_frame_size + int(0.3 * sku_config.dpi)
            
            # --- SKU名称 ---
            sku_text = sku_config.sku_name
            target_sku_w = int(right_area_w * 0.90)  # SKU宽度为右侧区域的90%
            # SKU可用高度：从content_start_y到底部信息框之间
            available_sku_h = int((available_h - bottom_info_total_h) * 0.45)
            
            sku_font_size = general_functions.get_max_font_size(
                sku_text, font_path_centschbook, target_sku_w, max_height=available_sku_h
            )
            sku_font = ImageFont.truetype(font_path_centschbook, sku_font_size)
            
            sku_w = draw.textlength(sku_text, font=sku_font)
            bbox_sku = draw.textbbox((0, 0), sku_text, font=sku_font)
            sku_h = bbox_sku[3] - bbox_sku[1]
            
            # SKU位置：在右侧区域内偏左，从content_start_y开始偏下10%
            sku_y = content_start_y + int(available_h * 0.10)
            sku_x = right_area_x_start + int((right_area_w - sku_w) * 0.35)  # 偏左对齐（35%位置）
            draw.text((sku_x, sku_y), sku_text, font=sku_font, fill=(0, 0, 0))
            
            # --- 虚线 ---
            dashed_line_y = sku_y + sku_h + int(canvas_h * 0.12)  # SKU下方12%（增大间距）
            dashed_line_x_start = sku_x
            dashed_line_x_end = sku_x + sku_w
            
            dash_length = 20
            gap_length = 15
            line_width = 3
            
            current_x = dashed_line_x_start
            while current_x < dashed_line_x_end:
                next_x = min(current_x + dash_length, dashed_line_x_end)
                draw.line([(current_x, dashed_line_y), (next_x, dashed_line_y)], fill=(0, 0, 0), width=line_width)
                current_x = next_x + gap_length
            
            # --- 底部信息框（紧挨虚线下方）---
            info_font_frame = ImageFont.truetype(font_path_centschbook, info_font_frame_size)
            info_font_without_frame = ImageFont.truetype(font_path_centschbook, info_font_without_frame_size)
            
            # 净毛重信息（左侧）
            gw_text = "G.W./N.W."
            weight_text = f"{sku_config.side_text['gw_value']} / {sku_config.side_text['nw_value']} LBS"
            
            bbox_gw = draw.textbbox((0, 0), gw_text, font=info_font_frame)
            bbox_gw_width = bbox_gw[2] - bbox_gw[0]
            
            # 与SKU左对齐，紧贴虚线下方
            left_box_x = sku_x + int(right_area_w * 0.07) # 在右侧区域内偏右7%位置
            left_box_y = dashed_line_y + int(canvas_h * 0.07)  # 虚线下方7%（更近）
            
            bbox_gw_pos = (left_box_x, left_box_y)
            draw = general_functions.draw_rounded_bg_for_text(
                draw, bbox_gw, sku_config, bbox_gw_pos,
                bg_color=(0, 0, 0), padding_cm=(0.5, 0.8), radius=16
            )
            draw.text(bbox_gw_pos, gw_text, font=info_font_frame, fill=sku_config.background_color)
            
            bbox_weight_x = left_box_x + bbox_gw_width + int(0.8 * sku_config.dpi)
            bbox_weight_y = left_box_y + int((info_font_frame_size - info_font_without_frame_size) / 2)
            draw.text((bbox_weight_x, bbox_weight_y), weight_text, font=info_font_without_frame, fill=(0, 0, 0))
            
            # 箱号信息（右侧）
            box_size_text = "BOX SIZE"
            l_in = sku_config.l_in
            w_in = sku_config.w_in
            h_in = sku_config.h_in
            dimension_text = f'{l_in:.1f}" x {w_in:.1f}" x {h_in:.1f}"'
            
            bbox_box = draw.textbbox((0, 0), box_size_text, font=info_font_frame)
            bbox_box_w = bbox_box[2] - bbox_box[0]
            
            # 在右侧区域中间偏左位置（约52%位置）
            right_box_x = right_area_x_start + int(right_area_w * 0.52)
            right_box_y = dashed_line_y + int(canvas_h * 0.07)  # 与净毛重同高（紧贴虚线）
            
            bbox_box_pos = (right_box_x, right_box_y)
            draw = general_functions.draw_rounded_bg_for_text(
                draw, bbox_box, sku_config, bbox_box_pos,
                bg_color=(0, 0, 0), padding_cm=(0.5, 0.8), radius=16
            )
            draw.text(bbox_box_pos, box_size_text, font=info_font_frame, fill=sku_config.background_color)
            
            dim_y = right_box_y + int((info_font_frame_size - info_font_without_frame_size) / 2)
            dim_x = right_box_x + bbox_box_w + int(0.8 * sku_config.dpi)
            draw.text((dim_x, dim_y), dimension_text, font=info_font_without_frame, fill=(0, 0, 0))
        
        # 生成右下面板：将左上面板旋转180度
        canvas_right_down = canvas_left_up.rotate(180, expand=True)
        
        # 返回四个面板（目前左下、右上未使用，保持空白）
        return canvas_left_up, canvas_left_down, canvas_right_up, canvas_right_down
        
    
    def generate_barberpub_front_panel(self, sku_config):
        canvas = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.h_px), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)
        
        canvas_w, canvas_h = canvas.size
        
        # 加载字体路径
        font_path_centschbook = self.font_paths['CentSchbook BT']
        font_path_droid = self.font_paths['Droid Sans Bold']
        
        # --- 区域 A: 左上角 Logo ---
        margin_top_px = int(3 * sku_config.dpi)  # 顶部边距3cm
        margin_left_px = int(3 * sku_config.dpi)  # 左边距3cm
        margin_right_px = int(2.7 * sku_config.dpi)  # 右边距2.7cm
        
        icon_logo = self.resources['icon_logo']
        icon_logo_h_px = int(canvas_h * 0.11)  # Logo高度约为画布高度的11%（适当缩小）
        icon_logo_resized = general_functions.scale_by_height(icon_logo, icon_logo_h_px)
        icon_logo_x = margin_left_px
        icon_logo_y = margin_top_px
        canvas.paste(icon_logo_resized, (icon_logo_x, icon_logo_y), mask=icon_logo_resized)
        
        # --- 区域 B: 右上角公司信息 ---
        icon_company = self.resources['icon_company']
        icon_company_h_px = int(canvas_h * 0.048)  # 公司信息高度约为画布高度的4.8%（适当缩小）
        icon_company_resized = general_functions.scale_by_height(icon_company, icon_company_h_px)
        icon_company_x = canvas_w - icon_company_resized.width - margin_right_px
        icon_company_y = margin_top_px
        canvas.paste(icon_company_resized, (icon_company_x, icon_company_y), mask=icon_company_resized)
        
        # --- 区域 C: 中间 Product 名称和标语作为整体居中（稍微缩小）---
        product_text = sku_config.product
        target_product_w = int(canvas_w * 0.78)  # 提高到78%宽度
        max_product_h = int(canvas_h * 0.28)  # 缩小到28%高度
        
        product_font_size = general_functions.get_max_font_size(
            product_text, font_path_droid, target_product_w, max_height=max_product_h
        )
        product_font = ImageFont.truetype(font_path_droid, product_font_size)
        
        # 计算Product文字尺寸
        product_w = draw.textlength(product_text, font=product_font)
        bbox = draw.textbbox((0, 0), product_text, font=product_font)
        product_h = bbox[3] - bbox[1]
        
        # --- 区域 D: 标语（小字，斜体）---
        icon_slogan = self.resources['icon_slogan']
        icon_slogan_w_px = int(canvas_w * 0.38)  # 缩小到38%宽度
        icon_slogan_resized = general_functions.scale_by_width(icon_slogan, icon_slogan_w_px)
        
        # 计算Product和Slogan的整体高度
        vertical_gap = int(2 * sku_config.dpi)  # Product和Slogan之间间距2cm
        total_center_h = product_h + vertical_gap + icon_slogan_resized.height
        
        # 整体垂直居中（在画布的48%处）
        center_y_start = int(canvas_h * 0.48) - (total_center_h // 2)
        
        # 绘制Product（居中）
        product_x = (canvas_w - product_w) // 2
        product_y = center_y_start
        draw.text((product_x, product_y), product_text, font=product_font, fill=(0, 0, 0))
        
        # 粘贴Slogan（居中）
        icon_slogan_x = (canvas_w - icon_slogan_resized.width) // 2
        icon_slogan_y = product_y + product_h + vertical_gap
        canvas.paste(icon_slogan_resized, (icon_slogan_x, icon_slogan_y), mask=icon_slogan_resized)
        
        # --- 区域 G: 底部斜纹条块（先绘制，避免遮盖文字）---
        stripe_height_cm = 1.6
        bottom_margin_cm = 1.2
        stripe_y_start = canvas_h - int(stripe_height_cm * sku_config.dpi) - int(bottom_margin_cm * sku_config.dpi)
        stripe_y_end = canvas_h - int(bottom_margin_cm * sku_config.dpi)

        
        canvas = general_functions.draw_diagonal_stripes(
            canvas, 
            stripe_height_cm=stripe_height_cm,
            dpi=sku_config.dpi,
            bottom_margin_cm=bottom_margin_cm,
            stripe_width_px=150,
            stripe_color=(0, 0, 0),
            bg_color=sku_config.background_color
        )
        draw = ImageDraw.Draw(canvas)  # 重新创建draw对象，因为canvas被更新了
        
        # --- 区域 E: 左下角颜色和SKU代码 ---
        margin_bottom_px = int(5 * sku_config.dpi)  # 底部边距5cm（增大间距，确保文字在斜纹上方）
        text_vertical_gap = int(0.3 * sku_config.dpi)  # 文字之间的垂直间距
        
        # SKU代码文字（大字，粗体）
        sku_code_text = sku_config.sku_name
        target_sku_code_w = int(canvas_w * 0.715)  # 宽度为面板宽度的71.5%
        sku_code_font_size = general_functions.get_max_font_size(
            sku_code_text, font_path_centschbook, target_sku_code_w, max_height=int(canvas_h * 0.14)
        )
        sku_code_font = ImageFont.truetype(font_path_centschbook, sku_code_font_size)
        
        # 计算SKU代码尺寸
        bbox_sku = draw.textbbox((0, 0), sku_code_text, font=sku_code_font)
        sku_code_h = bbox_sku[3] - bbox_sku[1]
        
        # SKU代码Y坐标（从底部往上算）
        sku_code_y = canvas_h - margin_bottom_px - sku_code_h - int(1.4 * sku_config.dpi)
        sku_code_x = margin_left_px - int(0.6 * sku_config.dpi)  # 左移0.6cm以增加边距

        draw.text((sku_code_x, sku_code_y), sku_code_text, font=sku_code_font, fill=(0, 0, 0))
        
        # 颜色文字（粗体，与SKU代码相同字体）
        color_text = f"{sku_config.color.upper()}"
        color_font_size = int(canvas_h * 0.06)
        color_font = ImageFont.truetype(font_path_centschbook, color_font_size)
        
        bbox_color = draw.textbbox((0, 0), color_text, font=color_font)
        color_text_h = bbox_color[3] - bbox_color[1]
        color_text_y = sku_code_y - color_text_h - text_vertical_gap  # 在SKU代码上方
        color_text_x = margin_left_px
      
        draw.text((color_text_x, color_text_y), color_text, font=color_font, fill=(0, 0, 0))
        
        # --- 区域 F: 右下角箱号信息（黑框文字）---
        box_text = f"BOX {sku_config.box_number['current_box']} OF {sku_config.box_number['total_boxes']}"
        box_text_font_w = int(canvas_w * 0.155)  # 目标宽度为画布宽度的15.5%（增大）
        box_text_font_h = int(canvas_h * 0.048)  # 字体大小为画布高度的4.8%（增大）
        box_text_font_size = general_functions.get_max_font_size(
            box_text, font_path_centschbook, box_text_font_w, max_height=box_text_font_h)
        box_text_font = ImageFont.truetype(font_path_centschbook, box_text_font_size)
        
        # 计算文字尺寸
        bbox_box_text = draw.textbbox((0, 0), box_text, font=box_text_font)
        bbox_box_text_w = bbox_box_text[2] - bbox_box_text[0]
        bbox_box_text_h = bbox_box_text[3] - bbox_box_text[1]
        
        # 箱号位置（右下角，与SKU代码Y坐标对齐）
        bbox_text_x = canvas_w - margin_right_px - bbox_box_text_w
        bbox_text_y = canvas_h - margin_bottom_px - bbox_box_text_h - int(1.4 * sku_config.dpi) 
        box_text_pos = (bbox_text_x, bbox_text_y)
        
        # 绘制黑框背景
        draw = general_functions.draw_rounded_bg_for_text(
            draw, bbox_box_text, sku_config, box_text_pos,
            bg_color=(0, 0, 0), padding_cm=(0.5, 0.9), radius=16
        )
        
        # 绘制白色文字
        draw.text(box_text_pos, box_text, font=box_text_font, fill=sku_config.background_color)
        
        canvas_front = canvas
        return canvas_front
    
    def generate_barberpub_side_panel(self, sku_config):
        """
        生成 Barberpub 全搭盖样式的侧面板
        
        侧面板采用横向画布，包含三个主要元素（从上到下）：
        1. SKU名称（大号字体，居中）
        2. 网址图标（左下角）
        3. 侧唛标签（右下角，包含条形码和产地信息）
        
        这三个元素会整体居中，间距随画布高度动态调整
        """
        # ========== 创建横向画布 ==========
        # 注意：侧面板是"横着"画的，因此宽度=箱子高度，高度=箱子宽度
        canvas_w = sku_config.h_px  # 画布宽度 = 箱子高度
        canvas_h = sku_config.w_px  # 画布高度 = 箱子宽度
        
        canvas = Image.new(sku_config.color_mode, (canvas_w, canvas_h), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)
        
        # 加载字体
        font_path_centschbook = self.font_paths['CentSchbook BT']
        
        # ========== 区域 A: 核心 SKU名称 ==========
        # SKU是侧面板的主要信息，需要非常大且醒目
        sku_text = sku_config.sku_name
        
        # 设置约束条件：宽度92%，高度55%
        target_sku_w = int(canvas_w * 0.92)  # 目标宽度为画布宽度的92%
        max_sku_h = int(canvas_h * 0.55)     # 最大高度为画布高度的55%
        
        # 在约束条件下计算最大字号
        sku_font_size = general_functions.get_max_font_size(
            sku_text, font_path_centschbook, target_sku_w, max_height=max_sku_h
        )
        sku_font = ImageFont.truetype(font_path_centschbook, sku_font_size)
        
        # 计算 SKU 文本的实际尺寸
        sku_text_w = draw.textlength(sku_text, font=sku_font)
        bbox = draw.textbbox((0, 0), sku_text, font=sku_font)
        sku_text_h = bbox[3] - bbox[1]  # 获取真实高度（去除基线偏移）
        
        # ========== 区域 B: 底部图标资源 ==========
        # 加载网址图标和侧唛标签图标
        img_web = self.resources['icon_webside']       # 网址搜索条（左侧）
        img_label = self.resources['icon_side_label']  # 条形码标签（右侧）
        
        # 设定图标尺寸（相对于画布宽度）
        icons_web_w_px = int(canvas_w * 0.57)    # 网址条宽度为画布的57%
        icons_label_w_px = int(canvas_w * 0.28)  # 标签宽度为画布的28%
        
        # 按宽度等比缩放图标
        img_web_resized = general_functions.scale_by_width(img_web, icons_web_w_px)
        img_label_resized = general_functions.scale_by_width(img_label, icons_label_w_px)
        
        # 填充标签内容（添加条形码、产地信息等）
        img_label_resized_filled = self.fill_side_label_barberpub_fulloverlap(sku_config, img_label_resized, self.font_paths)
        
        # ========== 整体居中布局 ==========
        # 定义动态间距（相对于画布高度），设置最小值以保持合理间距
        min_gap_cm = 7  # 最小间距7cm
        gap_sku_to_icons = max(int(canvas_h * 0.22), int(min_gap_cm * sku_config.dpi))  # SKU到底部图标的间距
        
        # 计算所有元素的总高度（两个图标并排，取较高的那个）
        bottom_icons_h = max(img_web_resized.height, img_label_resized_filled.height)
        total_content_h = sku_text_h + gap_sku_to_icons + bottom_icons_h
        
        # 整体垂直居中（起始Y坐标），稍微偏下10%以优化视觉效果
        content_start_y = int((canvas_h * 1.1 - total_content_h) // 2)
        
        # ========== 绘制所有元素 ==========
        
        # 1. 绘制 SKU 文本（水平居中）
        sku_x = (canvas_w - sku_text_w) // 2  # 水平居中
        sku_y = content_start_y               # 从计算的起始位置开始
        draw.text((sku_x, sku_y), sku_text, font=sku_font, fill=(0, 0, 0))
        
        # 2. 粘贴网址图标（位于SKU下方，左侧）
        margin_side = int(3 * sku_config.dpi)  # 左右边距 3cm
        web_x = margin_side                    # 左对齐
        web_y = sku_y + sku_text_h + gap_sku_to_icons  # 位于SKU下方
        canvas.paste(img_web_resized, (web_x, web_y), mask=img_web_resized)
        
        # 3. 粘贴标签图标（与网址图标同一水平线，右对齐）
        label_x = canvas_w - img_label_resized_filled.width - margin_side  # 右对齐
        # 让两个图标的中心在同一水平线上（垂直居中对齐）
        label_y = web_y + (img_web_resized.height - img_label_resized_filled.height) // 2
        canvas.paste(img_label_resized_filled, (label_x, label_y), mask=img_label_resized_filled)
        
        # ========== 旋转生成最终面板 ==========
        # 将横向画布旋转90度，变成竖长的侧面板
        # expand=True 会自动调整画布尺寸以容纳旋转后的内容
        canvas_right_side = canvas.rotate(90, expand=True)
        
        return canvas_right_side
    
    
    # ============================================================================
    # 侧唛标签填充函数
    # ============================================================================


    def fill_side_label_barberpub_fulloverlap(self, sku_config, img_label, fonts_paths):
        """
        填充 Barberpub 全搭盖样式的侧唛标签
        
        在空白标签图片上添加以下内容：
        1. 左侧条形码（SKU名称）
        2. 右侧条形码（SN代码）
        3. 底部产地信息条（黑底白字）
        
        参数:
            sku_config: SKU配置对象
            img_label: 空白标签图片
            fonts_paths: 字体路径字典
        
        返回:
            填充好内容的标签图片
        """
        # 复制空白标签，避免修改原图
        label_canvas = img_label.copy()
        draw = ImageDraw.Draw(label_canvas)
        
        label_w, label_h = label_canvas.size
        font_path_centschbook = fonts_paths['CentSchbook BT']
        
        # ========== 统一设置条形码参数 ==========
        barcode_h = int(label_h * 0.28)  # 条形码高度为标签高度的28%
        barcode_y = int(label_h * 0.04)  # 条形码距顶部为标签高度的4%

        # ========== 区域1: 左侧条形码（SKU名称）==========
        barcode1_text = sku_config.sku_name
        barcode1_w = int(label_w * 0.533)  # 宽度为标签宽度的53.3%
        barcode1_h = barcode_h  
        
        try:
            # 生成条形码图片
            barcode1_img = general_functions.generate_barcode_image(barcode1_text, barcode1_w, barcode1_h)
            barcode1_x = int(label_w * 0.05)  # 左边距5%
            barcode1_y = barcode_y
            label_canvas.paste(barcode1_img, (barcode1_x, barcode1_y), barcode1_img if barcode1_img.mode == 'RGBA' else None)
            
            # 在条形码下方添加文字说明
            barcode1_font_size = int(label_h * 0.04)
            barcode1_font = ImageFont.truetype(font_path_centschbook, barcode1_font_size)
            bbox_barcode1 = draw.textbbox((0, 0), barcode1_text, font=barcode1_font)
            barcode1_text_x = barcode1_x + int((barcode1_w - (bbox_barcode1[2] - bbox_barcode1[0])) / 2)  # 居中对齐
            barcode1_text_y = barcode1_y + barcode1_h + int(label_h * 0.0020)  # 条形码下方
            draw.text((barcode1_text_x, barcode1_text_y), barcode1_text, font=barcode1_font, fill=(0, 0, 0))
            
        except Exception as e:
            # 条形码生成失败时，降级显示纯文字
            draw.text((int(label_w * 0.05), barcode_y - int(1.5 * sku_config.dpi)), 
                    barcode1_text, 
                    font=ImageFont.truetype(font_path_centschbook, int(label_h * 0.05)), 
                    fill=(0, 0, 0))
        
        # ========== 区域2: 右侧条形码（SN代码）==========
        barcode2_text = sku_config.side_text['sn_code']
        barcode2_w = int(label_w * 0.36)  # 宽度为标签宽度的36%
        barcode2_h = barcode_h  
        
        try:
            # 生成条形码图片
            barcode2_img = general_functions.generate_barcode_image(barcode2_text, barcode2_w, barcode2_h)
            barcode2_x = label_w - barcode2_w - int(label_w * 0.04)  # 右边距4%
            barcode2_y = barcode_y
            label_canvas.paste(barcode2_img, (barcode2_x, barcode2_y), barcode2_img if barcode2_img.mode == 'RGBA' else None)
            
            # 在条形码下方添加文字说明
            barcode2_font_size = int(label_h * 0.04)
            barcode2_font = ImageFont.truetype(font_path_centschbook, barcode2_font_size)
            bbox_barcode2 = draw.textbbox((0, 0), barcode2_text, font=barcode2_font)
            barcode2_text_x = barcode2_x + int((barcode2_w - (bbox_barcode2[2] - bbox_barcode2[0])) / 2)  # 居中对齐
            barcode2_text_y = barcode2_y + barcode2_h + int(label_h * 0.0020)  # 条形码下方
            draw.text((barcode2_text_x, barcode2_text_y), barcode2_text, font=barcode2_font, fill=(0, 0, 0))
            
        except Exception as e:
            # 条形码生成失败时，降级显示纯文字
            draw.text((label_w - int(label_w * 0.25), barcode_y - int(1.5 * sku_config.dpi)), 
                    barcode2_text, 
                    font=ImageFont.truetype(font_path_centschbook, int(label_h * 0.05)), 
                    fill=(0, 0, 0))
        
        # ========== 区域3: 底部产地信息条 ==========
        # 在标签底部绘制黑色背景条，显示产地信息
        stripe_bottom_margin = int(label_h * 0.12)  # 底部信息条高度为标签高度的12%
        
        stripe_top_y = label_h - stripe_bottom_margin
        china_bar_y = stripe_top_y
        china_bar_height = stripe_bottom_margin
        # 绘制黑色矩形背景
        draw.rectangle([(0, china_bar_y), (label_w, label_h)], fill=(0, 0, 0))
        
        # 在黑色背景上绘制白色产地文字
        origin_text = sku_config.side_text.get('origin_text', 'MADE IN CHINA')  # 默认显示"MADE IN CHINA"
        china_font_size = int(china_bar_height * 0.5)  # 字号为信息条高度的50%
        china_font = ImageFont.truetype(font_path_centschbook, china_font_size)
        china_text_w = draw.textlength(origin_text, font=china_font)
        china_x = (label_w - china_text_w) // 2  # 水平居中
        china_y = china_bar_y + int(china_bar_height * 0.20)  # 垂直偏上20%
        draw.text((china_x, china_y), origin_text, font=china_font, fill=sku_config.background_color)
        
        # 返回填充好内容的标签
        return label_canvas