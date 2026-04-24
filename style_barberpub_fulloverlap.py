# -*- coding: utf-8 -*-
"""
Barberpub 全搭盖样式 - 将原有的 BoxMarkEngine 转换为样式类
"""
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import pathlib
import fitz  # PyMuPDF
from style_base import BoxMarkStyle, StyleRegistry
import general_functions
from general_functions import generate_barcode_image
import layout_engine as engine


@StyleRegistry.register
class BarberpubFullOverlapStyle(BoxMarkStyle):
    '''Barberpub 全搭盖样式'''
    
    def get_style_name(self):
        return "barberpub_fulloverlap"
    
    def get_style_description(self):
        return "Barberpub 全搭盖箱唛样式"
    
    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'ppi', 'color', 'product', 'side_text', 'sku_name', 'box_number']

    def _load_resources(self):
        res_base = self.base_dir / 'assets' / 'Barberpub' / '全搭盖' / '矢量文件'
        self.resources = {
            'icon_logo':           res_base / '正唛logo.png',
            'icon_top_logo':       res_base / '顶盖logo信息.png',
            'icon_attention_info': res_base / '全搭盖开箱注意事项.png',
            'icon_company':        res_base / '正唛公司信息.png',
            'icon_webside':        res_base / '侧唛网址.png',
            'icon_side_label':     res_base / '侧唛标签_窄.png',
            'icon_side_label_narrow': res_base / '侧唛标签_窄.png',
            'line_drawing': self.base_dir / 'assets' / 'Barberpub' / '对开盖' / '矢量文件' / '侧唛线描图.png',
            'icon_slogan':         res_base / '正唛宣传语.png',
            'icon_box_info':       res_base / '正唛多箱选择框.png',
        }

    def _load_fonts(self):
        font_base = self.base_dir / 'assets' / 'Barberpub' / '全搭盖' / '箱唛字体'
        # 直接用 fpdf2 字体代号作为 Key，与 register_fonts / set_font 保持一致
        self.font_paths = {
            'CentSchbook': str(font_base / '111.ttf'),
            'DroidSans':   str(font_base / 'CENSBKBI.TTF'),  # 斜体风格字体
            'CalibriB':    str(font_base / 'calibri_blod.ttf'),
        }

    def register_fonts(self, pdf: FPDF):
        for font_key, path in self.font_paths.items():
            pdf.add_font(font_key, '', path)

        
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
        self._draw_front_panel(pdf, sku_config, x0, y1, l_mm, h_mm)
        self._draw_front_panel(pdf, sku_config, x2, y1, l_mm, h_mm)

        # Two side panels
        self._draw_side_panel(pdf, sku_config, x1, y1, w_mm, h_mm)
        self._draw_side_panel(pdf, sku_config, x3, y1, w_mm, h_mm)

        # Left-up flap (and right-down = 180° rotated copy)
        self._draw_flap_left_up(pdf, sku_config, x0, 0.0, l_mm, w_mm)
        self._draw_flap_right_down(pdf, sku_config, x2, y1 + h_mm, l_mm, w_mm)

    # ── fpdf2 vector helper methods ─────────────────────────────────────────

    def _get_resource_path(self, key):
        """Return the resource file path (pathlib.Path)."""
        return self.resources[key]

    def _get_font_size(self, text, font_key, target_width_mm, ppi, max_h_mm=None, max_size=None):
        """Return (font_size_pt, pil_font) so text fits target_width_mm.
        Optionally constrain by max_h_mm."""
        path = self.font_paths[font_key]
        target_px = int(target_width_mm * ppi / 25.4)
        max_h_px = int(max_h_mm * ppi / 25.4) if max_h_mm is not None else None
        size_px = general_functions.get_max_font_size(text, path, target_px, max_height=max_h_px, max_size=max_size)
        size_pt = size_px * 72.0 / ppi
        pil_font = ImageFont.truetype(path, size_px)
        return size_pt, pil_font

    @staticmethod
    def _get_image_size(path) -> tuple:
        """获取图片尺寸 (width, height)，兼容 PDF 和光栅图片。"""
        path = pathlib.Path(path)
        if path.suffix.lower() == '.pdf':
            doc = fitz.open(str(path))
            rect = doc[0].rect
            doc.close()
            return rect.width, rect.height
        with Image.open(path) as img:
            return img.size

    @staticmethod
    def _prepare_image_for_fpdf(path):
        """返回可直接传给 fpdf2 pdf.image() 的对象。"""
        import tempfile, os
        path = pathlib.Path(path)
        if path.suffix.lower() == '.pdf':
            doc = fitz.open(str(path))
            page = doc[0]
            svg_str = page.get_svg_image()
            doc.close()
            tmp_fd, tmp_path = tempfile.mkstemp(suffix='.svg')
            os.write(tmp_fd, svg_str.encode('utf-8'))
            os.close(tmp_fd)
            return pathlib.Path(tmp_path)
        return path

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

    def _build_badge_text(self, text, font_family, font_size_pt, font_path, ppi,
                          text_color, background_color, border_radius):
        probe = engine.Text(
            text,
            font_family,
            font_size_pt,
            font_path=font_path,
            ppi=ppi,
        )
        padding_x = max(2.8, min(8.5, probe.width * 0.06 + probe.height * 0.10))
        padding_y = max(2.2, min(6.0, probe.height * 0.62))
        return engine.Text(
            text,
            font_family,
            font_size_pt,
            font_path=font_path,
            ppi=ppi,
            draw_background=True,
            background_color=background_color,
            color=text_color,
            padding_x=padding_x,
            padding_y=padding_y,
            border_radius=border_radius,
            nudge_y = -padding_y
        )
        
    def _draw_diagonal_stripes_pdf(
            self, pdf, x_mm, y_mm, w_mm, stripe_h_mm, stripe_w_mm=4.0, bg_color=(161, 142, 102)
        ):
        """Draw alternating diagonal warning stripes in a rectangle using PDF polygons."""
        """ w_mm 参数是底边宽度，stripe_h_mm 是条纹高度（垂直方向），stripe_w_mm 是条纹宽度（沿斜线方向）。"""
        with pdf.rect_clip(x_mm, y_mm, w_mm, stripe_h_mm):
            r, g, b = bg_color
            pdf.set_fill_color(r, g, b)
            pdf.rect(x_mm, y_mm, w_mm, stripe_h_mm, style="F")
            pdf.set_fill_color(0, 0, 0)
            stripe_offset = stripe_w_mm * 1.75  # 条纹间距，stripe_offset 是从一个条纹开始到下一个条纹开始的距离
            num = int((w_mm + stripe_h_mm) / stripe_offset) + 2
            for i in range(num):
                sx = x_mm + i * stripe_offset - stripe_h_mm
                pts = [
                    (sx, y_mm + stripe_h_mm),
                    (sx + stripe_w_mm, y_mm + stripe_h_mm),
                    (sx + stripe_w_mm + stripe_h_mm, y_mm),
                    (sx + stripe_h_mm, y_mm),
                ]
                pdf.polygon(pts, style="F")
        # ── 关键修复 ──────────────────────────────────────────────────────────
        # rect_clip 使用 q/Q 保存/恢复 PDF 流的图形状态（颜色被还原为背景色），
        # 但 fpdf2 的 Python 对象 fill_color 仍停留在 clip 内最后一次 set_fill_color(0,0,0)
        # 的值（DeviceGray(0)）。若不重置，后续调用 set_text_color(0,0,0) 时 fpdf2 会
        # 认为 text_color == fill_color（都是黑色），从而跳过颜色运算符的输出，
        # 导致文字以 Q 还原后的背景色渲染（不可见）。
        # 重新设置 fill_color 使 Python 状态与 PDF 流实际颜色重新同步。
        r, g, b = bg_color
        pdf.set_fill_color(r, g, b)

    # ── 正面面板 (vector) ────────────────────────────────────────────────────

    def _draw_front_panel(self, pdf: FPDF, sku_config, x_mm, y_mm, w_mm, h_mm):
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
        prod_pt, pil_prod = self._get_font_size(
            product_text, 'DroidSans', w_mm * 0.78, ppi, w_mm * 0.28)
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

        # 5. 底部斜纹条纹
        stripe_height_mm = 15.0
        bottom_margin_mm = 6.0
        stripe_y = y_mm + h_mm - stripe_height_mm - bottom_margin_mm
        stripe_width_mm = 30.0  # 条纹宽度
        self._draw_diagonal_stripes_pdf(pdf, x_mm, stripe_y, w_mm, stripe_height_mm, stripe_width_mm)

        margin_bottom = 32.0

        # 6. SKU 代码（左下角，CentSchbook）
        sku_text = sku_config.sku_name
        sku_pt, pil_sku = self._get_font_size(
            sku_text, 'CentSchbook', w_mm * 0.715, ppi, h_mm * 0.16)
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
        color_y_top = sku_y_top - color_h_mm - 10.0 # 颜色文字与 SKU 文字之间间距 10mm
        color_x = x_mm + margin_left
        self._draw_text_top_left(pdf, color_x, color_y_top,
                                  color_text, 'CentSchbook', '', color_pt, pil_color, ppi)

        # 8. 箱号文字（右下角，圆角黑框，白字）
        box_text = (f"BOX {sku_config.box_number['current_box']} "
                    f"OF {sku_config.box_number['total_boxes']}")
        box_pt, pil_box = self._get_font_size(
            box_text, 'CentSchbook', w_mm * 0.127, ppi, h_mm * 0.038)
        left_b, top_b, right_b, bot_b = self._pil_bbox_mm(pil_box, box_text, ppi)
        box_w_mm = right_b - left_b
        box_h_mm = bot_b - top_b
        box_y_top = y_mm + h_mm - margin_bottom - box_h_mm - (5 + 0.7 * 1.2 * 10) # 0.7 * 1.2 * 10 是下面文字外框的高度
        box_x = x_mm + w_mm - margin_right - box_w_mm

        # 黑色圆角背景
        pad_x = 5.0
        pad_y_top = 0.7 * 1.2 * 10  # 0.7cm * 1.2 → mm  = 8.4
        pad_y_bot = 0.7 * 1.2 * 10  # 0.7cm * 1.2 → mm  = 8.4
        radius_mm = 20 * 25.4 / ppi
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(box_x - pad_x, box_y_top - pad_y_top,
                 box_w_mm + 2 * pad_x, box_h_mm + pad_y_top + pad_y_bot,
                 style='F', round_corners=True, corner_radius=radius_mm)

        r, g, b = sku_config.background_color
        self._draw_text_top_left(pdf, box_x, box_y_top,
                                  box_text, 'CentSchbook', '', box_pt, pil_box, ppi,
                                  color=(r, g, b))

    # ── 侧面面板 (vector) ────────────────────────────────────────────────────

    def _draw_side_panel(self, pdf: FPDF, sku_config, x_mm, y_mm, w_mm, h_mm):
        """Draw side (侧唛) panel – dispatches based on panel dimensions."""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        if w_mm > 400 and h_mm < 500:
            # 宽大于40cm且高小于50cm，使用低高侧唛布局
            self._draw_side_low(pdf, sku_config, x_mm, y_mm, w_mm, h_mm,
                                ppi, px_per_mm)
        elif w_mm > 400 and h_mm >= 500:
            # 宽大于40cm且高大于50cm，使用窄侧唛布局
            self._draw_side_narrow(pdf, sku_config, x_mm, y_mm, w_mm, h_mm,
                                   ppi, px_per_mm)
        else:
            # 其余情况使用旋转宽侧唛布局
            self._draw_side_wide(pdf, sku_config, x_mm, y_mm, w_mm, h_mm,
                                 ppi, px_per_mm)

    def _draw_side_wide(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm, ppi, px_per_mm):
        """原宽侧唛布局 – 内容旋转90°绘入竖向格子。"""
        # The side panel content is drawn in a landscape orientation
        # (width=h_mm, height=w_mm) then rotated 90° into the portrait cell.
        cw = h_mm   # content width
        ch = w_mm   # content height

        # SKU text
        sku_text = sku_config.sku_name
        sku_pt, pil_sku = self._get_font_size(
            sku_text, 'CentSchbook', cw * 0.90, ppi, ch * 0.55)
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

        margin_side = 25.0  # ~2.5cm

        # Use pdf.rotation to draw landscape content rotated into portrait cell
        # Rotation centre = top-left of cell; rotate -90° (CCW) maps:
        #   content-x  → cell-y (from top)
        #   content-y  → cell-x (from right)
        rot_cx = x_mm 
        rot_cy = y_mm 
        with pdf.rotation(90, rot_cx, rot_cy):
            # After -90° CW rotation around (x_mm, y_mm):
            #   drawn (ox+p, oy+q) appears at page (x_mm+q, y_mm+h_mm-p)
            #   → oy = rot_cy, ox = rot_cx - h_mm (= x_mm - cw)
            ox = rot_cx - h_mm   # effective x origin after rotation
            oy = rot_cy          # effective y origin after rotation

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
            self._draw_label_overlay(
                pdf, sku_config, lbl_x, lbl_y, label_w, label_h,
                barcode1_text=sku_config.sku_name,
                barcode2_text=sku_config.side_text['sn_code'],
                bc1_xf=0.05,  bc1_yf=0.04, bc1_wf=0.533, bc1_hf=0.28,
                bc2_xf=0.60,  bc2_yf=0.04, bc2_wf=0.36,  bc2_hf=0.28,
                bar_yf=0.88,  bar_hf=0.12,
            )

    def _draw_side_low(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm, ppi, px_per_mm):
        """侧唛布局：宽>40cm 且 高<50cm"""

        # 网址图标
        webside_path = self.resources['icon_webside']
        webside_w_mm = w_mm * 0.5
        with Image.open(webside_path) as img:
            ws_orig_w, ws_orig_h = img.size
        webside_h_mm = webside_w_mm * ws_orig_h / ws_orig_w
        webside_x = x_mm + (w_mm - webside_w_mm) / 2
        webside_y = y_mm + h_mm * 0.05
        pdf.image(webside_path, x=webside_x, y=webside_y,
                  w=webside_w_mm, h=webside_h_mm)

        # 底部斜条纹的下边缘位置
        bottom_margin_mm = h_mm * 0.47

        # 底部斜纹条
        stripe_height_mm = 15.0
        stripe_width_mm = 30.0
        stripe_y = y_mm + h_mm - bottom_margin_mm - stripe_height_mm
        self._draw_diagonal_stripes_pdf(pdf, x_mm, stripe_y, w_mm, stripe_height_mm, stripe_width_mm)

        bottom_area_top = y_mm + h_mm - bottom_margin_mm

        # SKU 文字（居中，条纹上方）
        sku_text = sku_config.sku_name
        sku_pt, pil_sku = self._get_font_size(
            sku_text, 'CentSchbook', w_mm * 0.83, ppi, h_mm * 0.23)
        sl, st, sr, sb = self._pil_bbox_mm(pil_sku, sku_text, ppi)
        sku_text_w = sr - sl
        sku_text_h = sb - st

        sku_text_y = stripe_y - sku_text_h - h_mm * 0.08
        sku_text_x = x_mm + (w_mm - sku_text_w) / 2
        self._draw_text_top_left(pdf, sku_text_x, sku_text_y,
                                  sku_text, 'CentSchbook', '', sku_pt, pil_sku, ppi)

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

        # 带外框的文字大小
        label_font_h_mm = h_mm * 0.068
        label_font_w_mm = w_mm * 0.13
        label_font_pt, pil_lbl = self._get_font_size(
            "G.W./N.W.", 'CentSchbook', label_font_w_mm, ppi, label_font_h_mm)

        # 不带外框的文字大小
        value_font_h_mm = h_mm * 0.05
        value_font_w_mm = w_mm * 0.12
        value_font_pt, pil_val = self._get_font_size(
            "BOX SIZE", 'CentSchbook', value_font_w_mm, ppi, value_font_h_mm)

        # G.W./N.W. 标签（黑框）
        gw_label = "G.W./N.W."
        gl, gt, gr, gb = self._pil_bbox_mm(pil_lbl, gw_label, ppi)
        gw_lbl_w = gr - gl
        gw_lbl_h = gb - gt
        gw_lbl_y = info_center_y - vertical_gap / 2 - gw_lbl_h * 1.3

        pad_x = 3.0
        pad_y_top = 0.7 * 1.2 * 10
        pad_y_bot = 0.7 * 1.2 * 10
        radius_mm = 20 * 25.4 / ppi
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
        box_val_text = (f'{sku_config.l_in:.1f}" x '
                        f'{sku_config.w_in:.1f}" x '
                        f'{sku_config.h_in:.1f}"')
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

    def _draw_side_narrow(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm, ppi, px_per_mm):
        """侧唛布局：宽>40cm 且 高>=50cm（含线描图）"""

        # 网址图标
        webside_path = self.resources['icon_webside']
        webside_w_mm = w_mm * 0.5
        with Image.open(webside_path) as img:
            ws_orig_w, ws_orig_h = img.size
        webside_h_mm = webside_w_mm * ws_orig_h / ws_orig_w
        webside_x = x_mm + (w_mm - webside_w_mm) / 2
        webside_y = y_mm + h_mm * 0.05
        pdf.image(webside_path, x=webside_x, y=webside_y,
                  w=webside_w_mm, h=webside_h_mm)

        # 线描图（居中，网址下方）
        if hasattr(sku_config, 'img_line_drawing') and sku_config.img_line_drawing is not None:
            line_path = sku_config.img_line_drawing
        else:
            line_path = self.resources['line_drawing']
        line_h_mm = h_mm * 0.46
        l_orig_w, l_orig_h = self._get_image_size(line_path)
        line_w_mm = line_h_mm * l_orig_w / l_orig_h
        line_x = x_mm + (w_mm - line_w_mm) / 2
        line_y = webside_y + webside_h_mm + 30.0
        # 重置填充色为黑色，防止 fpdf2 SVG 渲染器继承斜纹条的背景色填充
        pdf.set_fill_color(0, 0, 0)
        pdf.image(self._prepare_image_for_fpdf(line_path), x=line_x, y=line_y,
                  w=line_w_mm, h=line_h_mm)

        # 底部斜条纹的下边缘位置
        bottom_margin_mm = h_mm * 0.23

        # 底部斜纹条
        stripe_height_mm = 15.0
        stripe_width_mm = 30.0
        stripe_y = y_mm + h_mm - bottom_margin_mm - stripe_height_mm
        self._draw_diagonal_stripes_pdf(pdf, x_mm, stripe_y, w_mm, stripe_height_mm, stripe_width_mm)

        bottom_area_top = y_mm + h_mm - bottom_margin_mm

        # SKU 文字（居中，线描图下方）
        sku_text = sku_config.sku_name
        sku_pt, pil_sku = self._get_font_size(
            sku_text, 'CentSchbook', w_mm * 0.9, ppi, h_mm * 0.12)
        sl, st, sr, sb = self._pil_bbox_mm(pil_sku, sku_text, ppi)
        sku_text_w = sr - sl
        sku_text_h = sb - st
        sku_text_y = stripe_y - sku_text_h - h_mm * 0.03
        sku_text_x = x_mm + (w_mm - sku_text_w) / 2
        self._draw_text_top_left(pdf, sku_text_x, sku_text_y,
                                  sku_text, 'CentSchbook', '', sku_pt, pil_sku, ppi)

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
            origin_y=0.2,
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
        pad_y_top = 0.7 * 1.2 * 10
        pad_y_bot = 0.7 * 1.2 * 10
        radius_mm = 20 * 25.4 / ppi
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
        box_val_text = (f'{sku_config.l_in:.1f}" x '
                        f'{sku_config.w_in:.1f}" x '
                        f'{sku_config.h_in:.1f}"')
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

    # ── 翻盖面板 (vector) ────────────────────────────────────────────────────

    def _draw_flap_left_up(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm):
        """Left-up flap: attention info, logo, SKU, dashed line, GW/NW & BOX SIZE."""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        if sku_config.w_cm > 30:
            self._draw_flap_tall(pdf, sku_config, x_mm, y_mm, w_mm, h_mm, ppi, px_per_mm)
        else:
            self._draw_flap_compact(pdf, sku_config, x_mm, y_mm, w_mm, h_mm, ppi, px_per_mm)

    def _draw_flap_tall(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm, ppi, px_per_mm):
        """Tall flap layout (w_cm > 30): stacked vertically, driven by layout_engine."""
        font_path = self.font_paths['CentSchbook']
        bg_r, bg_g, bg_b = sku_config.background_color
        radius_mm = 16 * 25.4 / ppi

        att_path  = self._get_resource_path('icon_attention_info')
        logo_path = self._get_resource_path('icon_logo')

        # ── 字体大小 ──
        sku_text = sku_config.sku_name
        sku_pt, _ = self._get_font_size(sku_text, 'CentSchbook', w_mm * 0.85, ppi = ppi, max_h_mm= h_mm * 0.20, max_size= 2000)

        label_pt = int(w_mm * 0.030 * px_per_mm) * 72.0 / ppi
        value_pt = int(w_mm * 0.025 * px_per_mm) * 72.0 / ppi

        gw_value = (f"{sku_config.side_text['gw_value']} / "
                    f"{sku_config.side_text['nw_value']} LBS")
        dim_text = (f'{sku_config.l_in:.1f}" x '
                    f'{sku_config.w_in:.1f}" x '
                    f'{sku_config.h_in:.1f}"')
        
        # 生成一个文本框，量一下宽度，后续底部信息布局用
        probe_left = engine.Text(gw_value, 'CentSchbook', value_pt,
                            font_path=font_path, ppi=ppi)
        
        probe_right = engine.Text(dim_text, 'CentSchbook', value_pt,
                            font_path=font_path, ppi=ppi)

        # ── 底部信息（G.W./N.W. 在 9% 处，BOX SIZE 在 54% 处）──
        gw_group = engine.Row(
            spacing= probe_right.width * 0.14, align='center',
            children=[
                self._build_badge_text(
                    "G.W./N.W.", 'CentSchbook', label_pt, font_path, ppi,
                    (bg_r, bg_g, bg_b), (0, 0, 0), radius_mm,
                ),
                engine.Text(gw_value, 'CentSchbook', value_pt,
                            font_path=font_path, ppi=ppi, nudge_y = 0),
            ]
        )
        box_group = engine.Row(
            spacing= probe_right.width * 0.14, align='center',
            children=[
                self._build_badge_text(
                    "BOX SIZE", 'CentSchbook', label_pt, font_path, ppi,
                    (bg_r, bg_g, bg_b), (0, 0, 0), radius_mm,
                ),
                engine.Text(dim_text, 'CentSchbook', value_pt,
                            font_path=font_path, ppi=ppi, nudge_y = 0),
            ]
        )
        mid_spacer_w = max(0.0, w_mm * 0.43 - gw_group.width)
        bottom_row = engine.Row(
            fixed_width=w_mm, align='center',
            children=[
                engine.Spacer(width=w_mm * 0.09),
                gw_group,
                engine.Spacer(width=mid_spacer_w),
                box_group,
            ]
        )
        # ── SKU 文字 + 虚线（Text 在 __init__ 即可测量宽度）──
        sku_elem = engine.Text(sku_text, 'CentSchbook', sku_pt,
                               font_path=font_path, ppi=ppi)
        sku_block = engine.Column(
            align='center', spacing=h_mm * 0.05,
            children=[
                sku_elem,
                engine.DashedLine(width=sku_elem.width, dash_len=2.0,
                                  dash_gap=1.5, line_width=0.3),
                bottom_row,
            ]
        )

        # ── 主布局列：构造后用 height 居中 ──
        main_col = engine.Column(
            fixed_height=h_mm,
            fixed_width=w_mm,
            justify='center',
            align='center',
            spacing=h_mm * 0.08,
            children=[
                # 顶部警示图标的宽度是整个面板的 85%，留一点边距更美观
                engine.Image(att_path,  width=w_mm * 0.85),
                engine.Image(logo_path, height=h_mm * 0.16),
                sku_block,
            ]
        )
        
        main_col.layout(x_mm, y_mm)
        main_col.render(pdf)

    def _draw_flap_compact(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm, ppi, px_per_mm):
        """Tall flap layout (w_cm > 30): stacked vertically, driven by layout_engine."""
        font_path = self.font_paths['CentSchbook']
        bg_r, bg_g, bg_b = sku_config.background_color
        radius_mm = 16 * 25.4 / ppi

        att_path  = self._get_resource_path('icon_attention_info')
        logo_path = self._get_resource_path('icon_logo')

        # ── 字体大小 ──
        sku_text = sku_config.sku_name
        sku_pt, _ = self._get_font_size(sku_text, 'CentSchbook', w_mm * 0.71, ppi)

        label_pt = int(w_mm * 0.0255 * px_per_mm) * 72.0 / ppi
        value_pt = int(w_mm * 0.0212 * px_per_mm) * 72.0 / ppi

        gw_value = (f"{sku_config.side_text['gw_value']} / "
                    f"{sku_config.side_text['nw_value']} LBS")
        dim_text = (f'{sku_config.l_in:.1f}" x '
                    f'{sku_config.w_in:.1f}" x '
                    f'{sku_config.h_in:.1f}"')

        # ── 底部信息（G.W./N.W. 在 9% 处，BOX SIZE 在 54% 处）──
        gw_group = engine.Row(
            spacing=18.0, align='center',
            children=[
                self._build_badge_text(
                    "G.W./N.W.", 'CentSchbook', label_pt, font_path, ppi,
                    (bg_r, bg_g, bg_b), (0, 0, 0), radius_mm,
                ),
                engine.Text(gw_value, 'CentSchbook', value_pt,
                            font_path=font_path, ppi=ppi, nudge_y = 4.9),
            ]
        )
        box_group = engine.Row(
            spacing=18.0, align='center',
            children=[
                self._build_badge_text(
                    "BOX SIZE", 'CentSchbook', label_pt, font_path, ppi,
                    (bg_r, bg_g, bg_b), (0, 0, 0), radius_mm,
                ),
                engine.Text(dim_text, 'CentSchbook', value_pt,
                            font_path=font_path, ppi=ppi, nudge_y = 4.9),
            ]
        )
        mid_spacer_w = max(0.0, w_mm * 0.35 - gw_group.width)
        bottom_row = engine.Row(
            fixed_width= gw_group.width + mid_spacer_w + box_group.width, 
            align='center',
            children=[
                # engine.Spacer(width=w_mm * 0.09),
                gw_group,
                engine.Spacer(width=mid_spacer_w),
                box_group,
            ]
        )
        # ── SKU 文字 + 虚线（Text 在 __init__ 即可测量宽度）──
        sku_elem = engine.Text(sku_text, 'CentSchbook', sku_pt,
                               font_path=font_path, ppi=ppi)
        sku_block = engine.Column(
            align='center', spacing=h_mm * 0.05,
            children=[
                sku_elem,
                engine.DashedLine(width=sku_elem.width, dash_len=2.0,
                                  dash_gap=1.5, line_width=0.3),
                bottom_row,
            ]
        )

        # ── logo 和 sku 水平布局 ──
        
        logo_sku_row = engine.Row(
            align='center', 
            spacing=w_mm * 0.05,
            children=[
                engine.Image(logo_path, height=h_mm * 0.16),
                sku_block,
            ]
        )
        
        # ── 主布局列：构造后用 height 居中 ──
        main_col = engine.Column(
            fixed_height=h_mm,
            fixed_width=w_mm,
            justify='center',
            align='center',
            spacing=h_mm * 0.10,
            children=[
                engine.Image(att_path,  width=w_mm * 0.95),
                logo_sku_row,
            ]
        )
        
        main_col.layout(x_mm, y_mm)
        main_col.render(pdf)

    def _draw_flap_bottom_info(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm,
                                ppi, px_per_mm,
                                left_x_frac, right_x_frac, info_y,
                                label_h_mm, value_h_mm, gap_after_label,
                                abs_left_x=None, abs_right_x=None):
        """Draw G.W./N.W. and BOX SIZE labels with black-bg tags on a flap."""
        label_px = int(label_h_mm * px_per_mm)
        label_pt = label_px * 72.0 / ppi
        pil_lbl = ImageFont.truetype(self.font_paths['CentSchbook'], label_px)

        value_px = int(value_h_mm * px_per_mm)
        value_pt = value_px * 72.0 / ppi
        pil_val = ImageFont.truetype(self.font_paths['CentSchbook'], value_px)

        bg_r, bg_g, bg_b = sku_config.background_color

        # ── G.W./N.W. ──
        gw_label = "G.W./N.W."
        gl, gt, gr, gb = self._pil_bbox_mm(pil_lbl, gw_label, ppi)
        gw_lbl_w = gr - gl
        gw_lbl_h = gb - gt

        gw_x = abs_left_x if abs_left_x is not None else x_mm + w_mm * left_x_frac
        gw_y = info_y

        pad_x, pad_y_top, pad_y_bot = 5.0, 4.9, 4.9
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

        dim_text = f'{sku_config.l_in:.1f}" x {sku_config.w_in:.1f}" x {sku_config.h_in:.1f}"'
        bvl, bvt, bvr, bvb = self._pil_bbox_mm(pil_val, dim_text, ppi)
        bval_h = bvb - bvt
        dim_val_x = box_x + box_lbl_w + gap_after_label
        dim_val_y = box_y + box_lbl_h / 2 - bval_h / 2
        self._draw_text_top_left(pdf, dim_val_x, dim_val_y,
                                  dim_text, 'CentSchbook', '', value_pt, pil_val, ppi)

    def _draw_flap_right_down(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm):
        """Right-down flap: 180° rotated copy of left-up content."""
        # Draw the same content as left-up but rotated 180° around the cell centre
        cx = x_mm + w_mm / 2
        cy = y_mm + h_mm / 2
        with pdf.rotation(180, cx, cy):
            self._draw_flap_left_up(pdf, sku_config, x_mm, y_mm, w_mm, h_mm)

    # ── 标签叠加 (vector) ────────────────────────────────────────────────────

    def _draw_label_overlay(self, pdf, sku_config, label_x, label_y,
                               label_w, label_h,
                               barcode1_text, barcode2_text,
                               bc1_xf, bc1_yf, bc1_wf, bc1_hf,
                               bc2_xf, bc2_yf, bc2_wf, bc2_hf,
                               bar_yf, bar_hf, origin_y = 0.2):
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
                    pil_bc = ImageFont.truetype(self.font_paths['CentSchbook'], font_px_bc)
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
            pil_orig = ImageFont.truetype(self.font_paths['CentSchbook'], font_px)
            origin_y = bar_y + bar_h * 0.2
            bg_r, bg_g, bg_b = sku_config.background_color
            self._draw_text_top_center(
                pdf, label_x + label_w / 2, origin_y,
                origin_text, 'CentSchbook', '', font_pt, pil_orig, ppi,
                color=(bg_r, bg_g, bg_b))
