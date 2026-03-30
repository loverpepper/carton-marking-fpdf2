"""
@author: Yushu&Cankun
"""


from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
from style_base import BoxMarkStyle, StyleRegistry
import general_functions
from general_functions import generate_barcode_image
import layout_engine as engine

@StyleRegistry.register
class ExacmeTopAndBottomDoubleRingAndBuriedTrampolineStyle(BoxMarkStyle):
    '''Exacme 双圈和埋地天地盖样式'''

    def get_style_name(self):
        return "exacme_topandbottom_doubleringandburiedtrampoline"

    def get_style_description(self):
        return "Exacme 双圈和埋地蹦床天地盖样式"

    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'product', 'color', 'side_text', 'sku_name', 'box_number']

    def get_layout_config(self, sku_config):
        '''
        Exacme 双圈和埋地天地盖样式 - 5块布局（3列3行）
        修正布局：中间大面 (L x W)，上下侧面 (L x H)，左右侧面 (H x W)
        '''
        x0 = 0
        x1 = sku_config.h_px
        x2 = sku_config.h_px + sku_config.l_px

        y0 = 0
        y1 = sku_config.h_px
        y2 = sku_config.h_px + sku_config.w_px

        return {
            "back_side_panel": (x1, y0, sku_config.l_px, sku_config.h_px),
            "left_side_panel": (x0, y1, sku_config.h_px, sku_config.w_px),
            "top_panel": (x1, y1, sku_config.l_px, sku_config.w_px),
            "right_side_panel": (x2, y1, sku_config.h_px, sku_config.w_px),
            "front_side_panel": (x1, y2, sku_config.l_px, sku_config.h_px)
        }

    def get_panels_mapping(self, sku_config):
        return {
            'top_panel': 'main_panel',
            'back_side_panel': 'long_side_upper',
            'front_side_panel': 'long_side_lower',
            'left_side_panel': 'short_side_left',
            'right_side_panel': 'short_side_right'
        }

    # ── fpdf2 required abstract methods (hybrid PIL → PDF) ──────────────────

    def get_layout_config_mm(self, sku_config):
        """mm-based layout for fpdf2 (mirrors get_layout_config in mm)"""
        l_mm = sku_config.l_cm * 10
        w_mm = sku_config.w_cm * 10
        h_mm = sku_config.h_cm * 10

        x0, x1, x2 = 0.0, h_mm, h_mm + l_mm
        y0, y1, y2 = 0.0, h_mm, h_mm + w_mm

        return {
            "back_side_panel":  (x1, y0, l_mm, h_mm),
            "left_side_panel":  (x0, y1, h_mm, w_mm),
            "top_panel":        (x1, y1, l_mm, w_mm),
            "right_side_panel": (x2, y1, h_mm, w_mm),
            "front_side_panel": (x1, y2, l_mm, h_mm),
        }

    def register_fonts(self, pdf: FPDF):
        pdf.add_font('Arial', '', self.font_paths['Arial Regular'])
        pdf.add_font('Arial', 'B', self.font_paths['Arial Bold'])

    def draw_to_pdf(self, pdf: FPDF, sku_config):
        """Render all panels directly to PDF using native fpdf2 vector text."""
        layout = self.get_layout_config_mm(sku_config)

        r, g, b = sku_config.background_color
        pdf.set_fill_color(r, g, b)
        for _, (x, y, w, h) in layout.items():
            pdf.rect(x, y, w, h, style='F')

        x, y, w, h = layout['top_panel']
        self._draw_top_panel_v(pdf, sku_config, x, y, w, h)

        x, y, w, h = layout['front_side_panel']
        self._draw_long_side_panel_v(pdf, sku_config, x, y, w, h, rotate_180=False)

        x, y, w, h = layout['back_side_panel']
        self._draw_long_side_panel_v(pdf, sku_config, x, y, w, h, rotate_180=True)

        x, y, w, h = layout['left_side_panel']
        self._draw_short_side_panel_v(pdf, sku_config, x, y, w, h, rotation_deg=-90)

        x, y, w, h = layout['right_side_panel']
        self._draw_short_side_panel_v(pdf, sku_config, x, y, w, h, rotation_deg=90)

    # ── fpdf2 vector helpers ────────────────────────────────────────────────

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

    def _draw_text_top_center(self, pdf, cx_mm, y_top_mm, text,
                               font_family, font_style, font_size_pt, pil_font, ppi,
                               color=(0, 0, 0)):
        left_mm, top_mm, right_mm, _ = self._pil_bbox_mm(pil_font, text, ppi)
        text_w = right_mm - left_mm
        x_mm = cx_mm - text_w / 2.0
        baseline_y = y_top_mm + (-top_mm)
        r, g, b = color
        pdf.set_text_color(r, g, b)
        pdf.set_font(font_family, font_style, font_size_pt)
        pdf.text(x_mm, baseline_y, text)

    def _draw_text_mid_center(self, pdf, cx_mm, cy_mm, text,
                               font_family, font_style, font_size_pt, pil_font, ppi,
                               color=(0, 0, 0)):
        left_mm, top_mm, right_mm, bottom_mm = self._pil_bbox_mm(pil_font, text, ppi)
        text_w = right_mm - left_mm
        text_h = bottom_mm - top_mm
        x_mm = cx_mm - text_w / 2.0
        baseline_y = cy_mm + (-top_mm) - text_h / 2.0
        r, g, b = color
        pdf.set_text_color(r, g, b)
        pdf.set_font(font_family, font_style, font_size_pt)
        pdf.text(x_mm, baseline_y, text)

    @staticmethod
    def _img_dims_mm(img_or_path, height_mm=None, width_mm=None):
        if isinstance(img_or_path, (str, __import__('pathlib').Path)):
            with Image.open(img_or_path) as img:
                orig_w, orig_h = img.size
        else:
            orig_w, orig_h = img_or_path.width, img_or_path.height
        if height_mm is not None:
            return height_mm * orig_w / orig_h, height_mm
        return width_mm, width_mm * orig_h / orig_w

    @staticmethod
    def _barcode_on_white(barcode_img):
        bg = Image.new('RGB', barcode_img.size, (255, 255, 255))
        if barcode_img.mode == 'RGBA':
            bg.paste(barcode_img, mask=barcode_img.split()[3])
        else:
            bg.paste(barcode_img.convert('RGB'))
        return bg

    # ── Top panel (L×W) ─────────────────────────────────────────────────────

    def _draw_top_panel_v(self, pdf: FPDF, sku_config,
                           x_mm, y_mm, w_mm, h_mm):
        """Draw the main top panel using native fpdf2 vector text."""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        # 1. Line drawing (68% h, centred, offset down 10%)
        if hasattr(sku_config, 'img_line_drawing') and sku_config.img_line_drawing is not None:
            line_src = sku_config.img_line_drawing
        else:
            line_src = self.resources['line_drawing']
        line_h_mm = h_mm * 0.68
        line_w_mm, _ = self._img_dims_mm(line_src, height_mm=line_h_mm)
        line_x = x_mm + (w_mm - line_w_mm) / 2.0
        line_y = y_mm + h_mm * 0.10
        pdf.image(line_src, x=line_x, y=line_y, w=line_w_mm, h=line_h_mm)

        # 2. Logo (30% h, centred above product text)
        logo_src = self.resources['logo']
        logo_h_mm = h_mm * 0.30
        logo_w_mm, _ = self._img_dims_mm(logo_src, height_mm=logo_h_mm)

        # Product text sizing
        product_lines = sku_config.product.split('\n')
        font_product_target_w_px = int(logo_w_mm * 1.0 * px_per_mm)
        longest_line = max(product_lines, key=len)
        font_product_px = general_functions.get_max_font_size(
            longest_line, self.font_paths['Arial Regular'], font_product_target_w_px)
        pil_product = ImageFont.truetype(self.font_paths['Arial Regular'], font_product_px)
        font_product_pt = font_product_px * 72.0 / ppi

        padding_col_mm = h_mm * 0.05

        product_children = [
            engine.Text(line, 'Arial', '', font_product_pt,
                        pil_font=pil_product, ppi=ppi, color=(0, 0, 0))
            for line in product_lines
        ]

        column = engine.Column(
            fixed_width=w_mm,
            align='center',
            spacing=padding_col_mm,
            children=[
                engine.Image(logo_src, height=logo_h_mm),
                *product_children,
            ]
        )

        column_y = y_mm + (h_mm * 0.9 - column.height) / 2.0
        column.layout(x_mm, column_y)
        column.render(pdf)

        # 3. Warning bar (10% h at bottom)
        warn_bar_h = h_mm * 0.10
        warn_bar_y = y_mm + h_mm - warn_bar_h

        img_warning_bg = self.resources['warning_bg']
        pdf.image(img_warning_bg, x=x_mm, y=warn_bar_y, w=w_mm, h=warn_bar_h)

        # 4. Warning icons (60% of bar height, distributed left/center/right)
        icons = [self.resources['warning_1'], self.resources['warning_2'], self.resources['warning_3']]
        icon_h_mm = warn_bar_h * 0.6
        max_icon_w_mm = w_mm * 0.305

        for i, icon in enumerate(icons):
            iw, ih = self._img_dims_mm(icon, height_mm=icon_h_mm)
            if iw > max_icon_w_mm:
                iw, ih = self._img_dims_mm(icon, width_mm=max_icon_w_mm)
            iy = warn_bar_y + (warn_bar_h - ih) / 2.0

            if i == 0:
                ix = x_mm + w_mm * 0.02
            elif i == 1:
                ix = x_mm + (w_mm - iw) / 2.0
            else:
                ix = x_mm + w_mm - iw - w_mm * 0.02

            pdf.image(icon, x=ix, y=iy, w=iw, h=ih)

        # 5. SKU text (right, above warning bar)
        sku_text = sku_config.sku_name
        font_sku_px = int(h_mm * 0.13 * px_per_mm)
        pil_sku = ImageFont.truetype(self.font_paths['Arial Bold'], font_sku_px)
        font_sku_pt = font_sku_px * 72.0 / ppi

        _, top_mm, right_mm, bottom_mm = self._pil_bbox_mm(pil_sku, sku_text, ppi)
        sku_w_mm = right_mm
        sku_h_mm = bottom_mm - top_mm
        sku_x = x_mm + w_mm - sku_w_mm - w_mm * 0.01
        sku_y = warn_bar_y - sku_h_mm - h_mm * 0.05

        self._draw_text_top_left(pdf, sku_x, sku_y, sku_text,
                                  'Arial', 'B', font_sku_pt, pil_sku, ppi,
                                  color=(40, 40, 40))

        # 6. Box info (left, above warning bar)
        current_box = sku_config.box_number['current_box']
        img_box_info = self.resources.get(f'info_box{current_box}', self.resources['info_box1'])
        box_h_mm = h_mm * 0.15
        box_w_mm, _ = self._img_dims_mm(img_box_info, height_mm=box_h_mm)
        box_x = x_mm + w_mm * 0.02
        box_y = warn_bar_y - box_h_mm - h_mm * 0.02
        pdf.image(img_box_info, x=box_x, y=box_y, w=box_w_mm, h=box_h_mm)

        # 7. Size text (top-left)
        size_text = "10FT"
        if "10" in sku_config.sku_name:
            size_text = "10FT"
        elif "12" in sku_config.sku_name:
            size_text = "12FT"
        elif "14" in sku_config.sku_name:
            size_text = "14FT"

        font_ft_px = int(h_mm * 0.08 * px_per_mm)
        pil_ft = ImageFont.truetype(self.font_paths['Arial Bold'], font_ft_px)
        font_ft_pt = font_ft_px * 72.0 / ppi

        self._draw_text_top_left(pdf, x_mm + w_mm * 0.01, y_mm + h_mm * 0.03,
                                  size_text, 'Arial', 'B', font_ft_pt, pil_ft, ppi,
                                  color=(0, 0, 0))

        # 8. Color frame + empty frame (top-right)
        img_empty_frame = self.resources['empty_frame']
        empty_frame_h_mm = h_mm * 0.12
        empty_w_mm, _ = self._img_dims_mm(img_empty_frame, height_mm=empty_frame_h_mm)

        img_col_frame = self.resources['color_frame']
        col_frame_h_mm = h_mm * 0.08
        col_frame_w_mm = empty_w_mm  # force same width as empty frame

        right_margin = w_mm * 0.02
        top_margin = h_mm * 0.05

        col_x = x_mm + w_mm - col_frame_w_mm - right_margin
        col_y = y_mm + top_margin

        pdf.image(img_col_frame, x=col_x, y=col_y, w=col_frame_w_mm, h=col_frame_h_mm)

        # Color text on frame
        color_text = "Turquoise"
        full_color_text = f"COL : {color_text}"
        font_col_px = int(col_frame_h_mm * 0.5 * px_per_mm)
        pil_col = ImageFont.truetype(self.font_paths['Arial Bold'], font_col_px)
        font_col_pt = font_col_px * 72.0 / ppi

        self._draw_text_mid_center(
            pdf,
            col_x + col_frame_w_mm / 2.0,
            col_y + col_frame_h_mm / 2.0 - col_frame_h_mm * 0.1,
            full_color_text,
            'Arial', 'B', font_col_pt, pil_col, ppi,
            color=(161, 142, 102))

        # Empty frame below color frame
        empty_x = col_x + (col_frame_w_mm - empty_w_mm) / 2.0
        empty_y = col_y + col_frame_h_mm + h_mm * 0.02
        pdf.image(img_empty_frame, x=empty_x, y=empty_y, w=empty_w_mm, h=empty_frame_h_mm)

    # ── Long side panel (L×H) ───────────────────────────────────────────────

    def _draw_long_side_panel_v(self, pdf: FPDF, sku_config,
                                 x_mm, y_mm, w_mm, h_mm, rotate_180=False):
        """Draw front/back long side panel using native fpdf2."""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        def _render():
            if sku_config.h_cm < 11:
                self._draw_long_side_compact(pdf, sku_config, x_mm, y_mm, w_mm, h_mm)
            else:
                self._draw_long_side_full(pdf, sku_config, x_mm, y_mm, w_mm, h_mm)

        if rotate_180:
            cx = x_mm + w_mm / 2.0
            cy = y_mm + h_mm / 2.0
            with pdf.rotation(180, cx, cy):
                _render()
        else:
            _render()

    def _draw_long_side_compact(self, pdf: FPDF, sku_config,
                                 x_mm, y_mm, w_mm, h_mm):
        """Long side for h_cm < 11: left warning images, center info, right text."""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        # Left: two warning images stacked
        img_left = self.resources['side_warning_left']
        img_right_warn = self.resources['side_warning']
        left_w_mm = w_mm * 0.24
        left1_w, left1_h = self._img_dims_mm(img_left, width_mm=left_w_mm)
        left2_w, left2_h = self._img_dims_mm(img_right_warn, width_mm=left_w_mm)

        left_col = engine.Column(
            align='center',
            spacing=h_mm * 0.05,
            children=[
                engine.Image(img_left, width=left1_w),
                engine.Image(img_right_warn, width=left2_w),
            ]
        )

        # Center: side info image
        img_info = self.resources['side_info']
        info_w_mm = w_mm * 0.32
        info_iw, info_ih = self._img_dims_mm(img_info, width_mm=info_w_mm)
        max_info_h = h_mm * 0.75
        if info_ih > max_info_h:
            info_iw, info_ih = self._img_dims_mm(img_info, height_mm=max_info_h)

        # Right: text block (COLOUR, G.W./N.W., BOX SIZE)
        font_size_bold_px = int(h_mm * 0.132 * px_per_mm)
        font_size_normal_px = int(h_mm * 0.123 * px_per_mm)

        pil_bold = ImageFont.truetype(self.font_paths['Arial Bold'], font_size_bold_px)
        pil_normal = ImageFont.truetype(self.font_paths['Arial Regular'], font_size_normal_px)

        bold_pt = font_size_bold_px * 72.0 / ppi
        normal_pt = font_size_normal_px * 72.0 / ppi

        spacing_middle_mm = w_mm * 0.005
        spacing_row_mm = h_mm * 0.05

        gw_bbox = pil_bold.getbbox("G.W./N.W. :", anchor='ls')
        gw_indent_mm = (gw_bbox[2] - gw_bbox[0]) / px_per_mm

        row_color = engine.Row(
            spacing=spacing_middle_mm,
            children=[
                engine.Text("COLOUR  :", 'Arial', 'B', bold_pt,
                            pil_font=pil_bold, ppi=ppi),
                engine.Text(sku_config.color, 'Arial', '', normal_pt,
                            pil_font=pil_normal, ppi=ppi),
            ]
        )
        row_weight_lbs = engine.Row(
            spacing=spacing_middle_mm,
            children=[
                engine.Text("G.W./N.W. :", 'Arial', 'B', bold_pt,
                            pil_font=pil_bold, ppi=ppi),
                engine.Text(f"{sku_config.side_text['gw_value']} / {sku_config.side_text['nw_value']} LBS",
                            'Arial', '', normal_pt, pil_font=pil_normal, ppi=ppi),
            ]
        )
        row_weight_kg = engine.Row(
            spacing=spacing_middle_mm,
            children=[
                engine.Spacer(width=gw_indent_mm, height=0.001),
                engine.Text(f"{sku_config.side_text['gw_value'] / 2.20462:.1f} / "
                            f"{sku_config.side_text['nw_value'] / 2.20462:.1f} KG",
                            'Arial', '', normal_pt, pil_font=pil_normal, ppi=ppi),
            ]
        )
        row_box_inch = engine.Row(
            spacing=spacing_middle_mm,
            children=[
                engine.Text("BOX SIZE :", 'Arial', 'B', bold_pt,
                            pil_font=pil_bold, ppi=ppi),
                engine.Text(f"{sku_config.l_cm / 2.54:.1f}\" x {sku_config.w_cm / 2.54:.1f}\" x {sku_config.h_cm / 2.54:.1f}\"",
                            'Arial', '', normal_pt, pil_font=pil_normal, ppi=ppi),
            ]
        )
        row_box_cm = engine.Row(
            spacing=spacing_middle_mm,
            children=[
                engine.Spacer(width=gw_indent_mm, height=0.001),
                engine.Text(f"{sku_config.l_cm:.1f}cm x {sku_config.w_cm:.1f}cm x {sku_config.h_cm:.1f}cm",
                            'Arial', '', normal_pt, pil_font=pil_normal, ppi=ppi),
            ]
        )

        right_text_block = engine.Column(
            align='left',
            spacing=spacing_row_mm,
            children=[row_color, row_weight_lbs, row_weight_kg,
                      row_box_inch, row_box_cm],
        )

        padding_row_mm = w_mm * 0.023

        row = engine.Row(
            fixed_width=w_mm,
            justify='space-between',
            align='center',
            padding=padding_row_mm,
            children=[
                left_col,
                engine.Image(img_info, width=info_iw if info_ih <= h_mm * 0.75 else None,
                             height=info_ih if info_ih <= h_mm * 0.75 else max_info_h,
                             nudge_x=-w_mm * 0.03),
                right_text_block,
            ]
        )

        row.layout(x_mm, y_mm + (h_mm - row.height) / 2.0)
        row.render(pdf)

    def _draw_long_side_full(self, pdf: FPDF, sku_config,
                              x_mm, y_mm, w_mm, h_mm):
        """Long side for h_cm >= 11: three images (warning_left, info, warning)."""
        img_info = self.resources['side_info']
        info_w_mm = w_mm * 0.32
        info_iw, info_ih = self._img_dims_mm(img_info, width_mm=info_w_mm)
        max_info_h = h_mm * 0.75
        if info_ih > max_info_h:
            info_iw, info_ih = self._img_dims_mm(img_info, height_mm=max_info_h)

        img_left = self.resources['side_warning_left']
        left_w_mm = w_mm * 0.27
        left_iw, left_ih = self._img_dims_mm(img_left, width_mm=left_w_mm)

        img_right = self.resources['side_warning']
        right_w_mm = w_mm * 0.29
        right_iw, right_ih = self._img_dims_mm(img_right, width_mm=right_w_mm)

        padding_row_mm = w_mm * 0.023

        row = engine.Row(
            fixed_width=w_mm,
            justify='space-between',
            align='center',
            padding=padding_row_mm,
            children=[
                engine.Image(img_left, width=left_iw),
                engine.Image(img_info, width=info_iw if info_ih <= max_info_h else None,
                             height=info_ih if info_ih <= max_info_h else max_info_h),
                engine.Image(img_right, width=right_iw),
            ]
        )

        row.layout(x_mm, y_mm + (h_mm - row.height) / 2.0)
        row.render(pdf)

    # ── Short side panel (H×W) ──────────────────────────────────────────────

    def _draw_short_side_panel_v(self, pdf: FPDF, sku_config,
                                  x_mm, y_mm, w_mm, h_mm, rotation_deg):
        """
        Draw left/right short side panel.
        On-page: w_mm = h_cm×10, h_mm = w_cm×10.
        Natural canvas (before rotation): nat_w = h_mm, nat_h = w_mm.
        """
        nat_w = h_mm
        nat_h = w_mm

        cx = x_mm + w_mm / 2.0
        cy = y_mm + h_mm / 2.0
        nat_x = cx - nat_w / 2.0
        nat_y = cy - nat_h / 2.0

        with pdf.rotation(rotation_deg, cx, cy):
            if sku_config.h_cm < 14:
                self._draw_short_side_compact_v(pdf, sku_config, nat_x, nat_y, nat_w, nat_h)
            else:
                self._draw_short_side_full_v(pdf, sku_config, nat_x, nat_y, nat_w, nat_h)

    def _draw_short_side_full_v(self, pdf: FPDF, sku_config,
                                 nat_x, nat_y, nat_w, nat_h):
        """Full side label for h_cm >= 14, with text/barcodes overlaid on label template."""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        label_src = self.resources['icon_side_label']
        lbl_w_mm = nat_w * 0.80
        lbl_w_actual, lbl_h_mm = self._img_dims_mm(label_src, width_mm=lbl_w_mm)

        lbl_x = nat_x + (nat_w - lbl_w_actual) / 2.0
        lbl_y = nat_y + (nat_h - lbl_h_mm) / 2.0

        pdf.image(label_src, x=lbl_x, y=lbl_y, w=lbl_w_actual, h=lbl_h_mm)

        # Left text block (COLOUR, G.W./N.W., BOX SIZE)
        bold_px = int(lbl_h_mm * 0.052 * px_per_mm)
        normal_px = int(lbl_h_mm * 0.043 * px_per_mm)

        pil_bold = ImageFont.truetype(self.font_paths['Arial Bold'], bold_px)
        pil_normal = ImageFont.truetype(self.font_paths['Arial Regular'], normal_px)

        bold_pt = bold_px * 72.0 / ppi
        normal_pt = normal_px * 72.0 / ppi

        spacing_mm = 25.0 / px_per_mm
        row_spacing = 10.0 / px_per_mm

        gw_bbox = pil_bold.getbbox("G.W./N.W. :", anchor='ls')
        gw_indent_mm = (gw_bbox[2] - gw_bbox[0]) / px_per_mm

        row_color = engine.Row(spacing=row_spacing, children=[
            engine.Text("COLOUR  :", 'Arial', 'B', bold_pt, pil_font=pil_bold, ppi=ppi),
            engine.Text(sku_config.color, 'Arial', '', normal_pt, pil_font=pil_normal, ppi=ppi),
        ])
        row_weight_lbs = engine.Row(spacing=row_spacing, children=[
            engine.Text("G.W./N.W. :", 'Arial', 'B', bold_pt, pil_font=pil_bold, ppi=ppi),
            engine.Text(f"{sku_config.side_text['gw_value']} / {sku_config.side_text['nw_value']} LBS",
                        'Arial', '', normal_pt, pil_font=pil_normal, ppi=ppi),
        ])
        row_weight_kg = engine.Row(spacing=row_spacing, children=[
            engine.Spacer(width=gw_indent_mm, height=0.001),
            engine.Text(f"{sku_config.side_text['gw_value'] / 2.20462:.1f} / "
                        f"{sku_config.side_text['nw_value'] / 2.20462:.1f} KG",
                        'Arial', '', normal_pt, pil_font=pil_normal, ppi=ppi),
        ])
        row_box_inch = engine.Row(spacing=row_spacing, children=[
            engine.Text("BOX SIZE :", 'Arial', 'B', bold_pt, pil_font=pil_bold, ppi=ppi),
            engine.Text(f"{sku_config.l_cm / 2.54:.1f}\" x {sku_config.w_cm / 2.54:.1f}\" x {sku_config.h_cm / 2.54:.1f}\"",
                        'Arial', '', normal_pt, pil_font=pil_normal, ppi=ppi),
        ])
        row_box_cm = engine.Row(spacing=row_spacing, children=[
            engine.Spacer(width=gw_indent_mm, height=0.001),
            engine.Text(f"{sku_config.l_cm:.1f}cm x {sku_config.w_cm:.1f}cm x {sku_config.h_cm:.1f}cm",
                        'Arial', '', normal_pt, pil_font=pil_normal, ppi=ppi),
        ])
        left_text_block = engine.Column(
            align='left', spacing=spacing_mm,
            children=[row_color, row_weight_lbs, row_weight_kg,
                      row_box_inch, row_box_cm],
        )
        left_text_block.layout(lbl_x + 26.0 / px_per_mm, lbl_y + 250.0 / px_per_mm)
        left_text_block.render(pdf)

        # Top SKU name (background color = transparent on dark label area)
        sku_target_w = lbl_w_actual * 0.730
        font_sku_px = general_functions.get_max_font_size(
            sku_config.sku_name, self.font_paths['Arial Bold'], int(sku_target_w * px_per_mm))
        pil_sku = ImageFont.truetype(self.font_paths['Arial Bold'], font_sku_px)
        font_sku_pt = font_sku_px * 72.0 / ppi

        self._draw_text_top_center(
            pdf, lbl_x + lbl_w_actual / 2.0, lbl_y + 20.0 / px_per_mm,
            sku_config.sku_name,
            'Arial', 'B', font_sku_pt, pil_sku, ppi,
            color=sku_config.background_color)

        # Barcodes
        bc_font_px = int(lbl_h_mm * 0.05 * px_per_mm)
        pil_bc = ImageFont.truetype(self.font_paths['Arial Regular'], bc_font_px)
        bc_font_pt = bc_font_px * 72.0 / ppi

        bc_h_mm = lbl_h_mm * 0.30
        bc_w_left_mm = bc_h_mm * 2.9
        bc_w_right_mm = bc_h_mm * 2.0

        img_bc_left = generate_barcode_image(
            sku_config.sku_name, int(bc_w_left_mm * px_per_mm), int(bc_h_mm * px_per_mm))
        img_bc_right = generate_barcode_image(
            sku_config.side_text['sn_code'], int(bc_w_right_mm * px_per_mm), int(bc_h_mm * px_per_mm))

        bc_spacing = 40.0 / px_per_mm

        bc_block = engine.Row(
            justify='center', align='bottom', padding=50.0 / px_per_mm,
            children=[
                engine.Column(align='center', spacing=10.0 / px_per_mm, children=[
                    engine.Image(self._barcode_on_white(img_bc_left)),
                    engine.Text(sku_config.sku_name, 'Arial', '', bc_font_pt,
                                pil_font=pil_bc, ppi=ppi),
                ]),
                engine.Spacer(width=bc_spacing, height=0.001),
                engine.Column(align='center', spacing=10.0 / px_per_mm, children=[
                    engine.Image(self._barcode_on_white(img_bc_right)),
                    engine.Text(sku_config.side_text['sn_code'], 'Arial', '', bc_font_pt,
                                pil_font=pil_bc, ppi=ppi),
                ]),
            ]
        )
        bc_block.layout(lbl_x + 560.0 / px_per_mm, lbl_y + 195.0 / px_per_mm)
        bc_block.render(pdf)

    def _draw_short_side_compact_v(self, pdf: FPDF, sku_config,
                                    nat_x, nat_y, nat_w, nat_h):
        """Compact side label for h_cm < 14, with text/barcodes overlaid."""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        label_src = self.resources['icon_compact_side_label']
        lbl_w_mm = nat_w * 0.79
        lbl_w_actual, lbl_h_mm = self._img_dims_mm(label_src, width_mm=lbl_w_mm)

        lbl_x = nat_x + (nat_w - lbl_w_actual) / 2.0
        lbl_y = nat_y + (nat_h - lbl_h_mm) / 2.0

        pdf.image(label_src, x=lbl_x, y=lbl_y, w=lbl_w_actual, h=lbl_h_mm)

        # Top SKU name (background-colored text for transparency effect)
        sku_target_w = lbl_w_actual * 0.820
        sku_target_h_px = int(lbl_h_mm * 0.39 * px_per_mm)
        font_sku_px = general_functions.get_max_font_size(
            sku_config.sku_name, self.font_paths['Arial Bold'],
            int(sku_target_w * px_per_mm), max_height=sku_target_h_px)
        pil_sku = ImageFont.truetype(self.font_paths['Arial Bold'], font_sku_px)
        font_sku_pt = font_sku_px * 72.0 / ppi

        self._draw_text_top_center(
            pdf, lbl_x + lbl_w_actual / 2.0, lbl_y + 15.0 / px_per_mm,
            sku_config.sku_name,
            'Arial', 'B', font_sku_pt, pil_sku, ppi,
            color=sku_config.background_color)

        # Barcodes
        bc_font_px = int(lbl_h_mm * 0.07 * px_per_mm)
        pil_bc = ImageFont.truetype(self.font_paths['Arial Regular'], bc_font_px)
        bc_font_pt = bc_font_px * 72.0 / ppi

        bc_h_mm = lbl_h_mm * 0.41
        bc_w_left_mm = bc_h_mm * 2.9
        bc_w_right_mm = bc_h_mm * 2.0

        img_bc_left = generate_barcode_image(
            sku_config.sku_name, int(bc_w_left_mm * px_per_mm), int(bc_h_mm * px_per_mm))
        img_bc_right = generate_barcode_image(
            sku_config.side_text['sn_code'], int(bc_w_right_mm * px_per_mm), int(bc_h_mm * px_per_mm))

        bc_block = engine.Row(
            justify='center', align='bottom', padding=15.0 / px_per_mm,
            children=[
                engine.Column(align='center', spacing=7.0 / px_per_mm, children=[
                    engine.Image(self._barcode_on_white(img_bc_left)),
                    engine.Text(sku_config.sku_name, 'Arial', '', bc_font_pt,
                                pil_font=pil_bc, ppi=ppi),
                ]),
                engine.Spacer(width=26.0 / px_per_mm, height=0.001),
                engine.Column(align='center', spacing=7.0 / px_per_mm, children=[
                    engine.Image(self._barcode_on_white(img_bc_right)),
                    engine.Text(sku_config.side_text['sn_code'], 'Arial', '', bc_font_pt,
                                pil_font=pil_bc, ppi=ppi),
                ]),
            ]
        )
        bc_block.layout(lbl_x, lbl_y + 82.0 / px_per_mm)
        bc_block.render(pdf)

    def generate_all_panels(self, sku_config):
        canvas_main = self.generate_exacme_main_panel(sku_config)
        canvas_long_side = self.generate_exacme_long_side_panel(sku_config)
        canvas_short_left, canvas_short_right = self.generate_exacme_short_side_panels(sku_config)

        # 生成 Upper (Back) 需要旋转 180 度
        canvas_long_upper = canvas_long_side.rotate(180)
        canvas_long_lower = canvas_long_side

        return {
            'main_panel': canvas_main,
            'long_side_upper': canvas_long_upper,
            'long_side_lower': canvas_long_lower,
            'short_side_left': canvas_short_left,
            'short_side_right': canvas_short_right
        }

    def _load_resources(self):
        """加载 Exacme 双圈和埋地蹦床天地盖样式的图片资源"""
        res_base = self.base_dir / 'assets' / 'Exacme' / '双圈和埋地蹦床天地盖' / '矢量文件'

        self.resources = {
            'logo': Image.open(res_base / '1.6185-D正唛logo.png').convert('RGBA'),
            'line_drawing': Image.open(res_base / '2.6185-D正唛线描图.png').convert('RGBA'),
            'color_frame': Image.open(res_base / '3.正唛颜色底框.png').convert('RGBA'),
            'empty_frame': Image.open(res_base / '4.正唛空白框.png').convert('RGBA'),
            'info_box1': Image.open(res_base / '5.1正唛公司信息及box1.png').convert('RGBA'),
            'info_box2': Image.open(res_base / '5.2正唛公司信息及box2.png').convert('RGBA'),
            'info_box3': Image.open(res_base / '5.3正唛公司信息及box3.png').convert('RGBA'),
            'warning_1': Image.open(res_base / '6.正唛底部提示1.png').convert('RGBA'),
            'warning_2': Image.open(res_base / '7.正唛底部提示2.png').convert('RGBA'),
            'warning_3': Image.open(res_base / '8.正唛底部提示3.png').convert('RGBA'),
            'warning_bg': Image.open(res_base / '9.正唛底部提示底框.png').convert('RGBA'),
            'side_sku_box': Image.open(res_base / '11.侧唛标签SKU旁BOX底框.png').convert('RGBA'),
            'side_info': Image.open(res_base / '12.侧唛箱子信息.png').convert('RGBA'),
            'side_warning': Image.open(res_base / '13.侧唛提示语.png').convert('RGBA'),
            'side_warning_left': Image.open(res_base / '14.侧唛提示语左.png').convert('RGBA'),
            'icon_side_label': Image.open(res_base / '侧唛标签.png').convert('RGBA'),
            'icon_compact_side_label': Image.open(res_base / '侧唛标签-小.png').convert('RGBA'),
        }

    def _load_fonts(self):
        """加载字体路径 """
        font_base = self.base_dir / 'assets' / 'Exacme' / '双圈和埋地蹦床天地盖' / '箱唛字体'
        self.font_paths = {
            'CentSchbook BT': str(font_base / 'arialbd.ttf'), # Century Schoolbook
            'Calibri Bold': str(font_base / 'arialbd.ttf'),
            'CENSBKB': str(font_base / 'arialbd.ttf'),
            'Arial Regular': str(font_base / 'arial.ttf'),
            'Arial Bold': str(font_base / 'arialbd.ttf'),
        }

    def generate_exacme_main_panel(self, sku_config):
        """生成 Exacme 中间主面板 (L x W)"""
        # 注意: 这里是主页面，尺寸 L x W
        canvas = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.w_px), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)
        canvas_w, canvas_h = canvas.size

        # 1. 顶部 Logo (移除此处绘制，移至线描图后层绘制)
        img_logo = self.resources['logo']
        logo_h = int(canvas_h * 0.30)  # 稍微加大
        img_logo_resized = general_functions.scale_by_height(img_logo, logo_h)

        # 2. 中间线描图
        # 修正: 样图中 线描图很大，作为背景一样的存在，EXACME字样在中间。
        # 优先使用用户上传的线描图（来自 app_v2.py 的 img_line_drawing 上传口），否则退回资源文件
        if hasattr(sku_config, 'img_line_drawing') and sku_config.img_line_drawing is not None:
            img_line = Image.open(sku_config.img_line_drawing).convert('RGBA')
        else:
            img_line = self.resources['line_drawing']
        line_h = int(canvas_h * 0.68) # 增大到 68%
        img_line_resized = general_functions.scale_by_height(img_line, line_h)
        
        # 居中，稍微往上挪一点 (0.10 -> 0.10) 以免被底部遮挡
        canvas.paste(img_line_resized, ((canvas_w - img_line_resized.width) // 2, int(canvas_h * 0.10)),
                     mask=img_line_resized)


        ################ 中间的 logo 和 product 组成容器 需要放在线描图的上层 ################

        product_lines = sku_config.product.split('\n')
        font_product_size_target_w = img_logo_resized.width * 1 # 字体宽度占 logo 宽度的 100%
        longest_line = max(product_lines, key=len)
        font_product_size = general_functions.get_max_font_size(longest_line, self.font_paths['Arial Regular'], font_product_size_target_w)
        font_product = ImageFont.truetype(self.font_paths['Arial Regular'], font_product_size)
        padding_col = int(canvas_h * 0.05) # 列间距占画布宽度的 2%
        
        product_text_children = [engine.Text(text=line, font=font_product, color=(0, 0, 0)) for line in product_lines]
        
        column = engine.Column(
            fixed_width=canvas_w,
            align='center',
            spacing=padding_col,
            children=[
                engine.Image(img_logo_resized),
                *product_text_children
            ]
        )

        column_y = int((canvas_h * 0.9 - column.height) // 2) # 因为底部黑框占了10%的高度，所以这里乘以0.9来计算剩余空间的垂直居中
        column.layout(0, column_y)
        column.render(draw)
        ################################################################################

        # 3. 底部黑色警告背景条
        img_warning_bg = self.resources['warning_bg']
        warn_bar_h = int(canvas_h * 0.10)
        img_warning_bg_resized = img_warning_bg.resize((canvas_w, warn_bar_h), Image.Resampling.LANCZOS)
        warn_bar_y = canvas_h - warn_bar_h
        canvas.paste(img_warning_bg_resized, (0, warn_bar_y), mask=img_warning_bg_resized)

        # 4. 警告图标排列
        icons = [self.resources['warning_1'], self.resources['warning_2'], self.resources['warning_3']]
        icon_h = int(warn_bar_h * 0.6)


        max_icon_w = int(canvas_w * 0.305)
        for i, icon in enumerate(icons):
            res_icon = general_functions.scale_by_height(icon, icon_h)
            if res_icon.width > max_icon_w:
                res_icon = general_functions.scale_by_width(icon, max_icon_w)
            pos_y = warn_bar_y + (warn_bar_h - res_icon.height) // 2

            if i == 0:
                # 左边图标：往左靠 (例如左边距 2% + 稍微一点偏移)
                pos_x = int(canvas_w * 0.02)
            elif i == 1:
                # 中间图标：保持绝对居中
                pos_x = (canvas_w - res_icon.width) // 2
            else:
                # 右边图标：靠右
                pos_x = canvas_w - res_icon.width - int(canvas_w * 0.02)

            canvas.paste(res_icon, (pos_x, pos_y), mask=res_icon)
        

        # 5. SKU (右下角，警告条上方)
        sku_text = sku_config.sku_name
        font_sku_size = int(canvas_h * 0.13)
        font_sku = ImageFont.truetype(self.font_paths['Calibri Bold'], font_sku_size)

        bbox = draw.textbbox((0,0), sku_text, font=font_sku)
        sku_w = bbox[2] - bbox[0]
        sku_h = bbox[3] - bbox[1]

        sku_x = canvas_w - sku_w - int(canvas_w * 0.01)
        sku_y = warn_bar_y - sku_h - int(canvas_h * 0.05)

        draw.text((sku_x, sku_y), sku_text, font=font_sku, fill=(40, 40, 40))

        # 6. Box 信息 (左下角)
        current_box = sku_config.box_number['current_box']
        img_box_info = self.resources.get(f'info_box{current_box}', self.resources['info_box1'])
        box_h = int(canvas_h * 0.15)
        img_box_resized = general_functions.scale_by_height(img_box_info, box_h)
        # 放在左下，警告条上方
        box_x = int(canvas_w * 0.02) # 调整为 0.02，更靠左
        box_y = warn_bar_y - img_box_resized.height - int(canvas_h * 0.02)
        canvas.paste(img_box_resized, (box_x, box_y), mask=img_box_resized)

        # 7. 左上角 10FT
        size_text = "10FT"
        if "10" in sku_config.sku_name: size_text = "10FT"
        elif "12" in sku_config.sku_name: size_text = "12FT"
        elif "14" in sku_config.sku_name: size_text = "14FT"

        font_ft = ImageFont.truetype(self.font_paths['Calibri Bold'], int(canvas_h * 0.08))
        # 靠左纯黑色
        draw.text((int(canvas_w * 0.01), int(canvas_h * 0.03)), size_text, font=font_ft, fill=(0, 0, 0))

        # 8. 右上角 (COL: 颜色 + 虚线框)
        # 调整逻辑：先确定下方虚线框的大小，然后让颜色框跟它一样宽

        # 8.2 下方虚线框 (先计算尺寸)
        img_empty_frame = self.resources['empty_frame']
        empty_frame_h = int(canvas_h * 0.12)
        img_empty_frame_resized = general_functions.scale_by_height(img_empty_frame, empty_frame_h)

        # 8.1 颜色底框
        img_col_frame = self.resources['color_frame']

        # 确定尺寸: 高度按比例，但宽度强制与虚线框一致
        col_frame_h = int(canvas_h * 0.08) # 原始高度计算
        # img_col_frame_resized = general_functions.scale_by_height(img_col_frame, col_frame_h)
        # 强制宽度一致
        img_col_frame_resized = img_col_frame.resize((img_empty_frame_resized.width, col_frame_h), Image.Resampling.LANCZOS)

        # 确定位置: 右上角，留出边距
        right_margin = int(canvas_w * 0.02)
        top_margin = int(canvas_h * 0.05)

        # 对齐虚线框的位置 (虚线框在下，颜色框在上)
        # 颜色框的位置
        col_x = canvas_w - img_col_frame_resized.width - right_margin
        col_y = top_margin

        canvas.paste(img_col_frame_resized, (col_x, col_y), mask=img_col_frame_resized)

        # 绘制颜色文字 "COL : Turquoise"
        # 从配置中获取颜色，去掉括号
        color_text = "Turquoise"
        full_color_text = f"COL : {color_text}"

        # 字体颜色: 浅色/白色? 样图中 fondo 是深色，字是浅色
        font_col = ImageFont.truetype(self.font_paths['Calibri Bold'], int(col_frame_h * 0.5))

        # 文字居中于底框
        bbox_col = draw.textbbox((0,0), full_color_text, font=font_col)
        text_w = bbox_col[2] - bbox_col[0]
        text_h = bbox_col[3] - bbox_col[1]

        text_x = col_x + (img_col_frame_resized.width - text_w) // 2
        text_y = col_y + (img_col_frame_resized.height - text_h) // 2
        # 微调y
        text_y -= int(col_frame_h * 0.1)

        draw.text((text_x, text_y), full_color_text, font=font_col, fill=(161, 142, 102)) # 白色

        # 8.2 绘制下方虚线框 (位置依赖于颜色框)
        empty_x = col_x + (img_col_frame_resized.width - img_empty_frame_resized.width) // 2
        empty_y = col_y + img_col_frame_resized.height + int(canvas_h * 0.02) # 间隔

        canvas.paste(img_empty_frame_resized, (empty_x, empty_y), mask=img_empty_frame_resized)

        return canvas

    def generate_exacme_icon_side_label(self, sku_config):
        """生成绘制完成的侧唛标签图片（横向，未缩放），供短侧面板使用"""
        icon_side_label = self.resources['icon_side_label'].rotate(0, expand=True)
        draw = ImageDraw.Draw(icon_side_label)
        
        ############ 左侧文字区 ############
        # 1. 准备字体
        font_size_bold = int(icon_side_label.height * 0.052) # 字体大小占侧身高度的 5%
        font_size_normal = int(icon_side_label.height * 0.043) # 字体大小占侧身高度的 4%
        
        font_bold = ImageFont.truetype(self.font_paths['Arial Bold'], font_size_bold)
        font_normal = ImageFont.truetype(self.font_paths['Arial Regular'], font_size_normal)

        # 2. 像串糖葫芦一样拼装每一行 (Row)
        row_color = engine.Row(
            spacing=10, # 粗体和细体中间隔 10 个像素
            children=[
                engine.Text("COLOUR  :", font=font_bold),
                engine.Text(sku_config.color, font=font_normal) # 动态颜色
            ]
        )

        row_weight_lbs = engine.Row(
            spacing=10,
            children=[
                engine.Text("G.W./N.W. :", font=font_bold),
                engine.Text(f"{sku_config.side_text['gw_value']} / {sku_config.side_text['nw_value']} LBS", font=font_normal)
            ]
        )

        # 【小魔法】：对于第二行需要缩进的 KG 重量，
        # 你可以直接塞一个不可见的 Element 进去当“隐形砖块”占位！
        # 先获取 "G.W./N.W. :" 这串字在当前动态字号下的真实包围盒
        gw_bbox = font_bold.getbbox("G.W./N.W. :")
        # 真实宽度 = 右边界 - 左边界
        gw_text_width = gw_bbox[2] - gw_bbox[0] 
        
        # 制造一个绝对精准的隐形砖块！
        indent_spacer = engine.Spacer(width=gw_text_width, height=1)

        row_weight_kg = engine.Row(
            spacing=10,
            children=[
                indent_spacer, # 隐形砖块在左边顶着
                engine.Text(f"{sku_config.side_text['gw_value']/ 2.20462:.1f} / {sku_config.side_text['nw_value']/ 2.20462:.1f} KG", font=font_normal)
            ]
        )

        row_box_size_inch = engine.Row(
            spacing=10,
            children=[
                engine.Text("BOX SIZE :", font=font_bold),
                engine.Text(f"{sku_config.l_cm/2.54:.1f}\" x {sku_config.w_cm/2.54:.1f}\" x {sku_config.h_cm/2.54:.1f}\"", font=font_normal)
            ]
        )
        
        row_box_size_cm = engine.Row(
            spacing=10,
            children=[
                indent_spacer, # 同样的隐形砖块，保持和重量信息的对齐
                engine.Text(f"{sku_config.l_cm:.1f}cm x {sku_config.w_cm:.1f}cm x {sku_config.h_cm:.1f}cm", font=font_normal)
            ]
        )

        # 3. 把所有行装进大垂直容器 (Column)
        left_text_block = engine.Column(
            align='left',  # 【关键】所有行统一靠左对齐
            spacing=25,    # 行与行之间的上下间距
            children=[
                row_color,
                row_weight_lbs,
                row_weight_kg,
                row_box_size_inch,
                row_box_size_cm
            ]
        )

        # ================= 渲染 =================
        # 最后，只需指定这个大方块的左上角起点，一键渲染！
        left_text_block.layout(x=26, y=250) 
        left_text_block.render(draw)
        
        ############ 顶部SKU_name区 ############
        text_sku_name = sku_config.sku_name
        # sku_name字号占侧身宽度的 78%
        font_sku_name_target_width = int(icon_side_label.width * 0.730) 
        font_size_sku_name = general_functions.get_max_font_size(text_sku_name, self.font_paths['Arial Bold'], font_sku_name_target_width) # 获取最大字号
        font_sku_name = ImageFont.truetype(self.font_paths['Arial Bold'], font_size_sku_name)
        
        ## 直接渲染在侧唛标签的顶部中心位置
        bbox = draw.textbbox((0, 0), text_sku_name, font=font_sku_name)
        text_width = bbox[2] - bbox[0]
        text_x = (icon_side_label.width - text_width) / 2
        text_y = -bbox[1] + 20  # 用字体内部偏移抵消，让文字真正贴顶
        draw.text((text_x, text_y), text_sku_name, font=font_sku_name, fill=(0, 0, 0, 0)) # 颜色为透明色，用背景色填充，达到隐藏文字的效果
        
        ############ 中间条码区 ############
        barcode_image_left_text = sku_config.sku_name # 条码下方的文字和侧唛顶部SKU_name保持一致
        barcodee_image_right_right = sku_config.side_text['sn_code'] # 条码下方右侧的文字来自side_text里的sn_code
        
        # 条码文字大小
        font_barcode_size = int(icon_side_label.height * 0.05) # 条码文字大小占侧身高度的 5%
        font_barcode = ImageFont.truetype(self.font_paths['Arial Regular'], font_barcode_size)
        
        # 条码高度
        barcode_height = int(icon_side_label.height * 0.30) # 条码高度占侧身高度的 30%
        
        # 条码宽度
        barcode_image_left_width = int(barcode_height * 2.9) # 条码宽度是高度的 2.7 倍
        barcode_image_right_width = int(barcode_height * 2.0)
        
        # 生成条码图片
        barcode_image_left = general_functions.generate_barcode_image(barcode_image_left_text, width=barcode_image_left_width, height=barcode_height)
        barcode_image_right = general_functions.generate_barcode_image(barcodee_image_right_right, width=barcode_image_right_width, height=barcode_height)
        
        # 生成两个垂直容器分别放左侧和右侧的条码图片+文字
        barcode_block_left = engine.Column(
            align='center',
            spacing=10,
            children=[
                engine.Image(barcode_image_left),
                engine.Text(barcode_image_left_text, font=font_barcode)
            ]
        )
        barcode_block_right = engine.Column(
            align='center',
            spacing=10,
            children=[
                engine.Image(barcode_image_right),
                engine.Text(barcodee_image_right_right, font=font_barcode)
            ]
        )
        
        # 把条码区放在侧唛标签的底部中心位置
        barcode_block = engine.Row(
            justify='center',
            align='bottom',
            padding=50, # 距离底部 50 像素的安全
            children=[
                barcode_block_left,
                engine.Spacer(width=40, height=1), # 条码之间的水平间距
                barcode_block_right
            ]
        )
        
        
        barcode_block.layout(x=560, y=195) # 先布局，获取整体宽高
        barcode_block.render(draw) # 再渲染

        return icon_side_label
    
    def generate_exacme_icon_small_side_label(self, sku_config):
        """生成适用于高度小于11cm的 Exacme 短侧面板的侧唛标签（横向，未缩放）"""
        icon_compact_side_label = self.resources['icon_compact_side_label'].rotate(0, expand=True)
        draw = ImageDraw.Draw(icon_compact_side_label)
        
        ############ 顶部SKU_name区 ############
        text_sku_name = sku_config.sku_name
        # sku_name字号占侧身宽度的 80%
        font_sku_name_target_width = int(icon_compact_side_label.width * 0.820) 
        font_sku_name_target_height = int(icon_compact_side_label.height * 0.39) # 字体高度占侧身高度的 39%
        font_size_sku_name = general_functions.get_max_font_size(text_sku_name, self.font_paths['Arial Bold'], font_sku_name_target_width, max_height=font_sku_name_target_height) # 获取最大字号
        font_sku_name = ImageFont.truetype(self.font_paths['Arial Bold'], font_size_sku_name)
        
        ## 直接渲染在侧唛标签的顶部中心位置
        bbox = draw.textbbox((0, 0), text_sku_name, font=font_sku_name)
        text_width = bbox[2] - bbox[0]
        text_x = (icon_compact_side_label.width - text_width) // 2
        text_y = - bbox[1] + 15  # 用字体内部偏移抵消，让文字真正贴顶
        draw.text((text_x, text_y), text_sku_name, font=font_sku_name, fill=sku_config.background_color)
        
        ############ 中间条码区 ############
        barcode_image_left_text = sku_config.sku_name # 条码下方的文字和侧唛顶部SKU_name保持一致
        barcodee_image_right_text = sku_config.side_text['sn_code'] # 条码下方右侧的文字来自side_text里的sn_code
        
        # 条码文字大小
        font_barcode_size = int(icon_compact_side_label.height * 0.07) # 条码文字大小占侧身高度的 7%
        font_barcode = ImageFont.truetype(self.font_paths['Arial Regular'], font_barcode_size)
        
        # 条码高度
        barcode_height = int(icon_compact_side_label.height * 0.41) # 条码高度占侧身高度的 41%
        
        # 条码宽度
        barcode_image_left_width = int(barcode_height * 2.9) # 条码宽度是高度的 2.9 倍
        barcode_image_right_width = int(barcode_height * 2.0)
        
        # 生成条码图片
        barcode_image_left = general_functions.generate_barcode_image(barcode_image_left_text, width=barcode_image_left_width, height=barcode_height)
        barcode_image_right = general_functions.generate_barcode_image(barcodee_image_right_text, width=barcode_image_right_width, height=barcode_height)
        
        # 生成两个垂直容器分别放左侧和右侧的条码图片+文字
        barcode_block_left = engine.Column(
            align='center',
            spacing=7,
            children=[
                engine.Image(barcode_image_left),
                engine.Text(barcode_image_left_text, font=font_barcode)
            ]
        )
        barcode_block_right = engine.Column(
            align='center',
            spacing=7,
            children=[
                engine.Image(barcode_image_right),
                engine.Text(barcodee_image_right_text, font=font_barcode)
            ]
        )
        
        # 把条码区放在侧唛标签的底部中心位置
        barcode_block = engine.Row(
            justify='center',
            align='bottom',
            padding=15,
            children=[
                barcode_block_left,
                engine.Spacer(width=26, height=1), # 条码之间的水平间距
                barcode_block_right
            ]
        )
        
        barcode_block.layout(x=0, y= 82)
        barcode_block.render(draw)
        
        # icon_compact_side_label.show()  # 临时调试：查看绘制完成后的紧凑侧唛标签
        
        return icon_compact_side_label

    def generate_exacme_short_side_panels(self, sku_config):
        """生成 Exacme 短侧面板 (左右侧，H x W)"""

        # 准备画布（侧身尺寸：宽=w_px, 高=h_px）
        canvas = Image.new(sku_config.color_mode, (sku_config.w_px, sku_config.h_px), sku_config.background_color)
        
        if sku_config.h_cm < 14:
            icon_side_label = self.generate_exacme_icon_small_side_label(sku_config)
            # 把绘制好的横向 icon_side_label 缩放后居中贴到画布上
            target_width  = int(sku_config.w_px * 0.79) # 紧凑版侧唛标签占侧身宽度的 79%
        else:
            icon_side_label = self.generate_exacme_icon_side_label(sku_config)
            # 把绘制好的横向 icon_side_label 缩放后居中贴到画布上
            target_width  = int(sku_config.w_px * 0.80)

        icon_side_label_resized = general_functions.scale_by_width(icon_side_label, target_width)
        # icon_side_label.show()  # 临时调试：查看绘制完成后的侧唛标签
        general_functions.paste_image_center_with_heightorwidth(canvas, icon_side_label_resized, width=target_width)

        canvas_short_left = canvas.rotate(-90, expand=True)
        canvas_short_right = canvas.rotate(90, expand=True)
        return canvas_short_left, canvas_short_right

    def generate_exacme_long_side_panel(self, sku_config):
        """生成 Exacme 长侧面板 (上下侧，L x H) - 显示 SHIP IN 3 BOXES + 左右提示语"""
        canvas = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.h_px), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)
        canvas_w, canvas_h = canvas.size

        if sku_config.h_cm < 11:
            # 左侧两个提示信息组成一个垂直容器
            if 'side_warning_left' in self.resources:
                img_left = self.resources['side_warning_left']
                img_left_w = int(canvas_w * 0.24) # 调小
                img_left_resized = general_functions.scale_by_width(img_left, img_left_w)
                
            if 'side_warning' in self.resources:
                img_right = self.resources['side_warning']
                img_right_w = int(canvas_w * 0.24) # 调小
                img_right_resized = general_functions.scale_by_width(img_right, img_right_w)
            
            left_col = engine.Column(
                align='center',
                padding=0,
                spacing= int(canvas_h * 0.05), # 图片之间的垂直间距占侧身高度的 5%
                children=[
                    engine.Image(img_left_resized),
                    engine.Image(img_right_resized)
                ]
            )
        
            # 中间部分 总箱数图片 放在中间
            if 'side_info' in self.resources:
                img_info = self.resources['side_info']
                # side_info 在短侧是 0.7 H. 在这里也类似
                img_info_w = int(canvas_w * 0.32) # 调小
                img_info_resized = general_functions.scale_by_width(img_info, img_info_w)
                max_info_h = int(canvas_h * 0.75)
                if img_info_resized.height > max_info_h:
                    img_info_resized = general_functions.scale_by_height(img_info, max_info_h)
        
            ############ 右侧文字区 ############
            # 右侧颜色、重量、尺寸信息等组成一个垂直容器
            # 1. 准备字体
            font_size_bold = int(canvas_h * 0.132) # 字体大小占侧身高度的 5%
            font_size_normal = int(canvas_h * 0.123) # 字体大小占侧身高度的 4%
            
            font_bold = ImageFont.truetype(self.font_paths['Arial Bold'], font_size_bold)
            font_normal = ImageFont.truetype(self.font_paths['Arial Regular'], font_size_normal)

            # 2. 像串糖葫芦一样拼装每一行 (Row)
            spacing_middle = int(canvas_w * 0.005) # 粗体和细体之间的间距占侧身高度的 6%
            spacing_row = int(canvas_h * 0.05) # 行间距占侧身高度的 4% 
            
            row_color = engine.Row(
                spacing=spacing_middle, # 粗体和细体中间隔 10 个像素
                children=[
                    engine.Text("COLOUR  :", font=font_bold),
                    engine.Text(sku_config.color, font=font_normal) # 动态颜色
                ]
            )

            row_weight_lbs = engine.Row(
                spacing=spacing_middle,
                children=[
                    engine.Text("G.W./N.W. :", font=font_bold),
                    engine.Text(f"{sku_config.side_text['gw_value']} / {sku_config.side_text['nw_value']} LBS", font=font_normal)
                ]
            )

            # 【小魔法】：对于第二行需要缩进的 KG 重量，
            # 你可以直接塞一个不可见的 Element 进去当“隐形砖块”占位！
            # 先获取 "G.W./N.W. :" 这串字在当前动态字号下的真实包围盒
            gw_bbox = font_bold.getbbox("G.W./N.W. :")
            # 真实宽度 = 右边界 - 左边界
            gw_text_width = gw_bbox[2] - gw_bbox[0] 
            
            # 制造一个绝对精准的隐形砖块！
            indent_spacer = engine.Spacer(width=gw_text_width, height=1)

            row_weight_kg = engine.Row(
                spacing=spacing_middle,
                children=[
                    indent_spacer, # 隐形砖块在左边顶着
                    engine.Text(f"{sku_config.side_text['gw_value']/ 2.20462:.1f} / {sku_config.side_text['nw_value']/ 2.20462:.1f} KG", font=font_normal)
                ]
            )

            row_box_size_inch = engine.Row(
                spacing=spacing_middle,
                children=[
                    engine.Text("BOX SIZE :", font=font_bold),
                    engine.Text(f"{sku_config.l_cm/2.54:.1f}\" x {sku_config.w_cm/2.54:.1f}\" x {sku_config.h_cm/2.54:.1f}\"", font=font_normal)
                ]
            )
            
            row_box_size_cm = engine.Row(
                spacing=spacing_middle,
                children=[
                    indent_spacer, # 同样的隐形砖块，保持和重量信息的对齐
                    engine.Text(f"{sku_config.l_cm:.1f}cm x {sku_config.w_cm:.1f}cm x {sku_config.h_cm:.1f}cm", font=font_normal)
                ]
            )

            # 3. 把所有行装进大垂直容器 (Column)
            right_text_block = engine.Column(
                align='left',  # 【关键】所有行统一靠左对齐
                spacing=spacing_row,    # 行与行之间的上下间距
                children=[
                    row_color,
                    row_weight_lbs,
                    row_weight_kg,
                    row_box_size_inch,
                    row_box_size_cm
                ]
            )
            
            padding_row = int(canvas_w * 0.023) # 行内左右间距占画布宽度的 2.3%
            
            row = engine.Row(
                fixed_width=canvas_w,
                justify='space-between',
                align='center',
                padding=padding_row,
                children=[
                    left_col,
                    engine.Image(img_info_resized, nudge_x = -int(canvas_w * 0.03)), # 中间信息往左微调一点，和左侧提示语更靠近
                    right_text_block
                ]
            )
        else:
            # 1. 中间部分 side_info (使用图片 side_info)
            # 放在中间
            if 'side_info' in self.resources:
                img_info = self.resources['side_info']
                # side_info 在短侧是 0.7 H. 在这里也类似
                img_info_w = int(canvas_w * 0.32) # 调小
                img_info_resized = general_functions.scale_by_width(img_info, img_info_w)
                max_info_h = int(canvas_h * 0.75)
                if img_info_resized.height > max_info_h:
                    img_info_resized = general_functions.scale_by_height(img_info, max_info_h)

            # 2. 左侧提示语 (使用图片 side_warning_left)
            # 放在左侧
            if 'side_warning_left' in self.resources:
                img_left = self.resources['side_warning_left']
                img_left_w = int(canvas_w * 0.27) # 调小
                img_left_resized = general_functions.scale_by_width(img_left, img_left_w)

            # 3. 右侧提示语 (使用图片 side_warning)
            # 放在右侧
            if 'side_warning' in self.resources:
                img_right = self.resources['side_warning']
                img_right_w = int(canvas_w * 0.29) # 调小
                img_right_resized = general_functions.scale_by_width(img_right, img_right_w)

            padding_row = int(canvas_w * 0.023) # 行内左右间距占画布宽度的 2.3%
            
            row = engine.Row(
                fixed_width=canvas_w,
                justify='space-between',
                align='center',
                padding=padding_row,
                children=[
                    engine.Image(img_left_resized),
                    engine.Image(img_info_resized),
                    engine.Image(img_right_resized)
                ]
            )
        
        row.layout(x=0, y=(canvas_h - row.height) // 2) # 垂直居中
        row.render(draw)

        return canvas
