# -*- coding: utf-8 -*-
"""
Exacme 方形蹦床天地盖样式 - fpdf2 版
"""
from fpdf import FPDF
from PIL import Image, ImageFont
from style_base import BoxMarkStyle, StyleRegistry
import general_functions
from general_functions import generate_barcode_image
import layout_engine as engine
import re


@StyleRegistry.register
class ExacmeTopAndBottomSquareTrampolineStyle(BoxMarkStyle):
    """Exacme 方形蹦床天地盖样式 (fpdf2 版)"""

    def get_style_name(self):
        return "exacme_topandbottom_squaretrampoline"

    def get_style_description(self):
        return "Exacme 方形蹦床天地盖箱唛样式"

    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'ppi', 'color', 'product',
                'side_text', 'sku_name', 'box_number']

    def get_preview_images(self):
        preview_dir = self.base_dir / 'assets' / 'Exacme' / '方形蹦床天地盖' / '实例生成图'
        if not preview_dir.exists():
            return []
        supported_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}
        results = []
        for img_path in sorted(preview_dir.iterdir()):
            if img_path.suffix.lower() in supported_exts:
                try:
                    img = Image.open(img_path).convert('RGB')
                    results.append((img_path.name, img))
                except Exception:
                    pass
        return results

    # ── 布局配置（mm）───────────────────────────────────────────────────────────

    def get_layout_config_mm(self, sku_config):
        h_mm = sku_config.h_cm * 10
        l_mm = sku_config.l_cm * 10
        w_mm = sku_config.w_cm * 10
        x0, x1, x2 = 0.0, h_mm, h_mm + l_mm
        y0, y1, y2 = 0.0, h_mm, h_mm + w_mm
        return {
            "back_side_panel":  (x1, y0, l_mm, h_mm),
            "left_side_panel":  (x0, y1, h_mm, w_mm),
            "top_panel":        (x1, y1, l_mm, w_mm),
            "right_side_panel": (x2, y1, h_mm, w_mm),
            "front_side_panel": (x1, y2, l_mm, h_mm),
        }

    def get_panels_mapping(self, sku_config):
        return {
            'back_side_panel':  'back_side',
            'left_side_panel':  'left_side',
            'top_panel':        'top',
            'right_side_panel': 'right_side',
            'front_side_panel': 'front_side',
        }

    # ── 资源 / 字体加载 ─────────────────────────────────────────────────────────

    def _load_resources(self):
        res_base = self.base_dir / 'assets' / 'Exacme' / '方形蹦床天地盖' / '矢量文件'
        self.resources = {
            'icon_logo':                res_base / 'logo.png',
            'icon_middle_info_vertical':   res_base / '正唛中间信息-1.png',
            'icon_middle_info_horizontal': res_base / '正唛中间信息-2.png',
            'icon_bottom_info':         res_base / '正唛底部提示信息.png',
            'icon_company':             res_base / '上下侧唛公司信息.png',
            'icon_side_label_high':     res_base / '侧唛标签_高.png',
            'icon_side_label_wide':     res_base / '侧唛标签_宽.png',
        }

    def _load_fonts(self):
        font_base = self.base_dir / 'assets' / 'Exacme' / '方形蹦床天地盖' / '箱唛字体'
        self.font_paths = {
            'Arial':      str(font_base / 'arialmt.ttf'),
            'Arial Bold': str(font_base / 'arial-boldmt.ttf'),
            'Arial Black': str(font_base / 'ariblk.ttf'),
        }

    # ── fpdf2 字体注册 ──────────────────────────────────────────────────────────

    def register_fonts(self, pdf: FPDF):
        pdf.add_font('Arial',      '', self.font_paths['Arial'])
        pdf.add_font('Arial',      'B', self.font_paths['Arial Bold'])
        pdf.add_font('ArialBlack', '', self.font_paths['Arial Black'])

    # ── 核心绘制入口 ────────────────────────────────────────────────────────────

    def draw_to_pdf(self, pdf: FPDF, sku_config):
        layout = self.get_layout_config_mm(sku_config)

        r, g, b = sku_config.background_color
        pdf.set_fill_color(r, g, b)
        for _, (x, y, w, h) in layout.items():
            pdf.rect(x, y, w, h, style='F')

        x, y, w, h = layout['top_panel']
        self._draw_top_panel(pdf, sku_config, x, y, w, h)

        x, y, w, h = layout['front_side_panel']
        self._draw_front_back_panel(pdf, sku_config, x, y, w, h, rotate_180=False)

        x, y, w, h = layout['back_side_panel']
        self._draw_front_back_panel(pdf, sku_config, x, y, w, h, rotate_180=True)

        x, y, w, h = layout['left_side_panel']
        self._draw_side_panel(pdf, sku_config, x, y, w, h, rotation_deg=-90)

        x, y, w, h = layout['right_side_panel']
        self._draw_side_panel(pdf, sku_config, x, y, w, h, rotation_deg=90)

    # ── 内部辅助方法 ────────────────────────────────────────────────────────────

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

    @staticmethod
    def _img_dims_mm(img_path_or_pil, height_mm=None, width_mm=None):
        """Return (w_mm, h_mm) for an image given a target height or width."""
        if isinstance(img_path_or_pil, (str, __import__('pathlib').Path)):
            with Image.open(img_path_or_pil) as img:
                orig_w, orig_h = img.size
        else:
            orig_w, orig_h = img_path_or_pil.width, img_path_or_pil.height
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

    @staticmethod
    def _extract_size_text(sku_name):
        """从 SKU 名称中提取尺寸字符串，如 H812 → 8x12FT。"""
        match = re.search(r'H(\d)(\d{1,2})', sku_name, re.IGNORECASE)
        if match:
            dim1 = match.group(1)
            dim2 = match.group(2)
            if dim2 == '1':
                dim2 = '10'
            return f"{dim1}x{dim2}FT"
        return "SIZE"

    # ── 面板绘制方法 ────────────────────────────────────────────────────────────

    def _draw_front_back_panel(self, pdf: FPDF, sku_config,
                                x_mm, y_mm, w_mm, h_mm, rotate_180=False):
        """
        绘制前/后侧面板（l×h）。
        三行文字 + 两侧 Logo/公司信息。
        back 面通过 pdf.rotation(180) 翻转。
        """
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        size_text = self._extract_size_text(sku_config.sku_name)

        # 字体尺寸（proportional to h_mm）
        row1_px    = int(h_mm * 0.15 * px_per_mm)
        row2_sku_px  = int(h_mm * 0.34 * px_per_mm)
        row2_col_px  = int(h_mm * 0.12 * px_per_mm)
        row3_px    = int(h_mm * 0.10 * px_per_mm)

        pil_row1      = ImageFont.truetype(self.font_paths['Arial'], row1_px)
        pil_row2_sku  = ImageFont.truetype(self.font_paths['Arial Black'], row2_sku_px)
        pil_row2_col  = ImageFont.truetype(self.font_paths['Arial'], row2_col_px)
        pil_row3      = ImageFont.truetype(self.font_paths['Arial'], row3_px)
        pil_row3_bold = ImageFont.truetype(self.font_paths['Arial Bold'], row3_px)

        row1_pt    = row1_px    * 72.0 / ppi
        row2_sku_pt  = row2_sku_px  * 72.0 / ppi
        row2_col_pt  = row2_col_px  * 72.0 / ppi
        row3_pt    = row3_px    * 72.0 / ppi

        # 间距和边距
        spacing_mm  = h_mm * 0.10
        side_pad_mm = 25.0  # 2.5 cm
        box_pad_mm  = 0.6 * 10   # 6.0 mm
        box_radius  = h_mm * 0.05

        logo_w_mm, logo_h_mm = self._img_dims_mm(self.resources['icon_logo'],
                                                  width_mm=w_mm * 0.15)
        company_w_mm, company_h_mm = self._img_dims_mm(self.resources['icon_company'],
                                                       width_mm=w_mm * 0.18)

        # ---- Row 1: size_text + product ----
        row1_text = f"{size_text} {sku_config.product}"
        row1_elem = engine.Text(row1_text, 'Arial', '', row1_pt,
                                pil_font=pil_row1, ppi=ppi)

        # ---- Row 2: SKU (huge) + Color ----
        color_text = f"({sku_config.color.title()})"
        row2_col_elem = engine.Text(color_text, 'Arial', '', row2_col_pt,
                                    pil_font=pil_row2_col, ppi=ppi,
                                    nudge_y=-(h_mm * 0.03))
        # Invisible left spacer to keep SKU centred when colour is appended
        row2_spacer = engine.Spacer(width=row2_col_elem.width, height=0.001)
        row2 = engine.Row(
            align='bottom',
            spacing=0.001,
            children=[
                engine.Text(sku_config.sku_name, 'ArialBlack', '', row2_sku_pt,
                            pil_font=pil_row2_sku, ppi=ppi),
                row2_col_elem,
            ]
        )

        # ---- Row 3: left text + right "Box X of Y" (black bg) ----
        box_text_left  = (f"{sku_config.box_number['total_boxes']} Boxes in Total, "
                          f"May Deliver Separately.")
        box_text_right = (f"Box {sku_config.box_number['current_box']} of "
                          f"{sku_config.box_number['total_boxes']}")
        row3 = engine.Row(
            align='center',
            spacing=w_mm * 0.01,
            children=[
                engine.Text(box_text_left, 'Arial', '', row3_pt,
                            pil_font=pil_row3, ppi=ppi),
                engine.Text(box_text_right, 'Arial', 'B', row3_pt,
                            pil_font=pil_row3_bold, ppi=ppi,
                            color=sku_config.background_color,
                            draw_background=True, background_color=(0, 0, 0),
                            border_radius=box_radius,
                            padding=box_pad_mm,
                            nudge_x=-(box_pad_mm + w_mm * 0.02),
                            nudge_y=-(box_pad_mm + h_mm * 0.01)),
            ]
        )

        middle_col = engine.Column(
            align='left',
            spacing=spacing_mm,
            children=[row1_elem, row2, row3],
        )

        main_row = engine.Row(
            fixed_width=w_mm,
            fixed_height=h_mm,
            justify='space-between',
            align='center',
            padding_x=side_pad_mm,
            children=[
                engine.Image(self.resources['icon_logo'], width=logo_w_mm),
                middle_col,
                engine.Image(self.resources['icon_company'], width=company_w_mm),
            ]
        )

        def _render():
            main_row.layout(x_mm, y_mm)
            main_row.render(pdf)

        if rotate_180:
            cx = x_mm + w_mm / 2.0
            cy = y_mm + h_mm / 2.0
            with pdf.rotation(180, cx, cy):
                _render()
        else:
            _render()

    def _draw_top_panel(self, pdf: FPDF, sku_config, x_mm, y_mm, w_mm, h_mm):
        """绘制顶面（l×w）。"""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        size_text    = self._extract_size_text(sku_config.sku_name)
        top_pad_mm   = 20.0  # 2 cm

        # ── 1. 顶部行：Logo（居中）+ 右侧尺寸框 ────────────────────────────────
        font_top_px   = int(h_mm * 0.05 * px_per_mm)
        font_top_pt   = font_top_px * 72.0 / ppi
        pil_top       = ImageFont.truetype(self.font_paths['Arial Bold'], font_top_px)

        box_int_pad   = 8.0   # 0.8 cm
        box_radius    = h_mm * 0.05

        logo_img = engine.Image(self.resources['icon_logo'], width=w_mm * 0.22)

        size_box = engine.Text(
            size_text, 'Arial', 'B', font_top_pt,
            pil_font=pil_top, ppi=ppi,
            color=sku_config.background_color,
            draw_background=True, background_color=(0, 0, 0),
            border_radius=box_radius,
            padding=box_int_pad,
            nudge_x=-(box_int_pad + w_mm * 0.02),
            nudge_y=-box_int_pad,
        )

        top_row = engine.Row(
            fixed_width=w_mm,
            justify='space-between',
            align='top',
            padding_x=top_pad_mm,
            padding_y=top_pad_mm,
            children=[
                engine.Spacer(width=size_box.width, height=0.001),
                logo_img,
                size_box,
            ]
        )

        # ── 2. 中间：依据尺寸选图 ──────────────────────────────────────────────
        if sku_config.l_cm > 130 and sku_config.w_cm < 40:
            middle_img = engine.Image(self.resources['icon_middle_info_horizontal'],
                                      width=w_mm * 0.93,
                                      nudge_y=h_mm * 0.04)
            occupied_top = top_pad_mm + top_row.height
            target_y     = (h_mm - middle_img.height) / 2.0 + h_mm * 0.06
            safe_spacing = max(target_y - occupied_top, h_mm * 0.03)
        else:
            middle_img   = engine.Image(self.resources['icon_middle_info_vertical'],
                                        width=w_mm * 0.53)
            safe_spacing = h_mm * 0.03

        # ── 3. 底部：全宽黑色警示条 ────────────────────────────────────────────
        bar_height_mm = h_mm * 0.13
        bar_icon_w_mm = w_mm * 0.80
        bar_icon_h_mm, _ = self._img_dims_mm(self.resources['icon_bottom_info'],
                                              width_mm=bar_icon_w_mm)
        # 将警示图标嵌入预先绘制的黑条中（通过 Column 合成）
        # 先绘制黑条，再居中绘制图标
        black_bar = engine.Column(
            fixed_width=w_mm,
            fixed_height=bar_height_mm,
            align='center',
            justify='start',
            padding=0,
            children=[
                engine.Image(self.resources['icon_bottom_info'], width=bar_icon_w_mm),
            ]
        )

        # ── 4. 整体布局 ─────────────────────────────────────────────────────────
        safe_area = engine.Column(
            align='center',
            spacing=safe_spacing,
            padding_y=top_pad_mm,
            children=[top_row, middle_img],
        )

        main_col = engine.Column(
            fixed_width=w_mm,
            fixed_height=h_mm,
            justify='space-between',
            align='center',
            padding=0,
            children=[safe_area, black_bar],
        )

        # 绘制主体布局
        main_col.layout(x_mm, y_mm)
        main_col.render(pdf)

        # 黑条背景（黑色，全宽，贴底）
        bar_y = y_mm + h_mm - bar_height_mm
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(x_mm, bar_y, w_mm, bar_height_mm, style='F')
        # 在黑条内居中绘制警示图标
        icon_x = x_mm + (w_mm - bar_icon_w_mm) / 2.0
        icon_y = bar_y + (bar_height_mm - bar_icon_h_mm) / 2.0
        pdf.image(self.resources['icon_bottom_info'],
                  x=icon_x, y=icon_y, w=bar_icon_w_mm, h=bar_icon_h_mm)

    def _draw_side_panel(self, pdf: FPDF, sku_config,
                          x_mm, y_mm, w_mm, h_mm, rotation_deg):
        """
        绘制左/右侧面板。

        页面上面板尺寸：w_mm = h_cm×10，h_mm = w_cm×10
        自然画布（旋转前）：nat_w = h_mm，nat_h = w_mm
        """
        nat_w = h_mm
        nat_h = w_mm

        cx = x_mm + w_mm / 2.0
        cy = y_mm + h_mm / 2.0
        nat_x = cx - nat_w / 2.0
        nat_y = cy - nat_h / 2.0

        # 选择宽标签或高标签
        use_high = sku_config.l_cm > 130 and sku_config.w_cm < 40

        if use_high:
            label_src = self.resources['icon_side_label_high']
        else:
            label_src = self.resources['icon_side_label_wide']

        # 标签目标宽度 = 90% 自然宽
        lbl_w_mm = nat_w * 0.9
        lbl_h_mm, _ = self._img_dims_mm(label_src, width_mm=lbl_w_mm)

        if use_high:
            # 高标签在 PIL 中需先旋转 -90°；在 fpdf2 中以横向展示：
            # 使用原图的转置宽高来正确放置
            with Image.open(label_src) as _img:
                orig_w, orig_h = _img.size
            # 旋转后纵横比 = orig_h / orig_w（宽变高互换）
            lbl_h_mm = lbl_w_mm * orig_w / orig_h

        lbl_x = nat_x + (nat_w - lbl_w_mm) / 2.0
        lbl_y = nat_y + nat_h * 0.05

        with pdf.rotation(rotation_deg, cx, cy):
            if use_high:
                # 将高标签旋转为横向后作为 PIL Image 传入
                lbl_pil = Image.open(label_src).rotate(-90, expand=True)
                pdf.image(lbl_pil, x=lbl_x, y=lbl_y, w=lbl_w_mm, h=lbl_h_mm)
                self._draw_side_label_high_content(
                    pdf, sku_config, lbl_x, lbl_y, lbl_w_mm, lbl_h_mm)
            else:
                pdf.image(label_src, x=lbl_x, y=lbl_y, w=lbl_w_mm, h=lbl_h_mm)
                self._draw_side_label_wide_content(
                    pdf, sku_config, lbl_x, lbl_y, lbl_w_mm, lbl_h_mm)

    def _draw_side_label_wide_content(self, pdf: FPDF, sku_config,
                                       lbl_x, lbl_y, lbl_w, lbl_h):
        """在宽标签上叠加绘制文字、条形码（fpdf2 版）。"""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        content_w = lbl_w * 0.95
        content_h = lbl_h * 0.78

        # 字体大小（比例于 content_h）
        huge_px   = int(content_h * 0.5088 * px_per_mm)
        box_px    = int(content_h * 0.18   * px_per_mm)
        info_px   = int(content_h * 0.14   * px_per_mm)
        bc_px     = int(content_h * 0.08   * px_per_mm)

        pil_huge  = ImageFont.truetype(self.font_paths['Arial Black'], huge_px)
        pil_box   = ImageFont.truetype(self.font_paths['Arial Bold'],  box_px)
        pil_bold  = ImageFont.truetype(self.font_paths['Arial Bold'],  info_px)
        pil_reg   = ImageFont.truetype(self.font_paths['Arial'],       info_px)
        pil_bc    = ImageFont.truetype(self.font_paths['Arial'],       bc_px)

        huge_pt = huge_px * 72.0 / ppi
        box_pt  = box_px  * 72.0 / ppi
        info_pt = info_px * 72.0 / ppi
        bc_pt   = bc_px   * 72.0 / ppi

        box_pad  = 0.26 * 10   # 2.6 mm

        # ── Row 1：SKU（huge）+ 箱数黑框 ────────────────────────────────────────
        box_txt = (f"Box {sku_config.box_number['current_box']} of "
                   f"{sku_config.box_number['total_boxes']}")
        row1 = engine.Row(
            fixed_width=content_w,
            justify='space-between',
            align='center',
            children=[
                engine.Text(sku_config.sku_name, 'ArialBlack', '', huge_pt,
                            pil_font=pil_huge, ppi=ppi),
                engine.Text(box_txt, 'Arial', 'B', box_pt,
                            pil_font=pil_box, ppi=ppi,
                            color=sku_config.background_color,
                            draw_background=True, background_color=(0, 0, 0),
                            border_radius=0.0,
                            padding=box_pad,
                            nudge_x=-(box_pad + content_w * 0.02),
                            nudge_y=-box_pad),
            ]
        )

        # ── Row 2 左：重量和尺寸信息 ────────────────────────────────────────────
        gw_label  = "G.W./N.W. : "
        box_label = "BOX SIZE : "
        gw_bbox   = pil_bold.getbbox(gw_label, anchor='ls')
        box_bbox  = pil_bold.getbbox(box_label, anchor='ls')
        gw_w_px   = gw_bbox[2]  - gw_bbox[0]
        box_w_px  = box_bbox[2] - box_bbox[0]
        indent_w  = max(0.0, (gw_w_px - box_w_px) / px_per_mm)

        row_gw = engine.Row(
            align='bottom', spacing=10.0 / px_per_mm,
            children=[
                engine.Text(gw_label, 'Arial', 'B', info_pt, pil_font=pil_bold, ppi=ppi),
                engine.Text(
                    (f"{sku_config.side_text['gw_value']} / "
                     f"{sku_config.side_text['nw_value']} LBS"),
                    'Arial', '', info_pt, pil_font=pil_reg, ppi=ppi),
            ]
        )
        row_box = engine.Row(
            align='bottom', spacing=10.0 / px_per_mm,
            children=[
                engine.Text(box_label, 'Arial', 'B', info_pt, pil_font=pil_bold, ppi=ppi),
                engine.Spacer(width=indent_w, height=0.001),
                engine.Text(
                    (f"{sku_config.l_in:.1f}\" x "
                     f"{sku_config.w_in:.1f}\" x {sku_config.h_in:.1f}\""),
                    'Arial', '', info_pt, pil_font=pil_reg, ppi=ppi),
            ]
        )
        info_col = engine.Column(
            align='left',
            spacing=content_h * 0.08,
            children=[row_gw, row_box],
        )

        # ── Row 2 右：双条码 ─────────────────────────────────────────────────────
        bc_h_mm     = content_h * 0.28
        bc_w_sku_mm = bc_h_mm * 3.5
        bc_w_sn_mm  = bc_h_mm * 2.7

        img_bc_sku = generate_barcode_image(sku_config.sku_name,
                                            int(bc_w_sku_mm * px_per_mm),
                                            int(bc_h_mm * px_per_mm))
        img_bc_sn  = generate_barcode_image(sku_config.side_text['sn_code'],
                                            int(bc_w_sn_mm * px_per_mm),
                                            int(bc_h_mm * px_per_mm))

        bc_col_left = engine.Column(
            align='center', spacing=content_h * 0.02,
            children=[
                engine.Image(self._barcode_on_white(img_bc_sku)),
                engine.Text(sku_config.sku_name, 'Arial', '', bc_pt,
                            pil_font=pil_bc, ppi=ppi),
            ]
        )
        bc_col_right = engine.Column(
            align='center', spacing=content_h * 0.02,
            children=[
                engine.Image(self._barcode_on_white(img_bc_sn)),
                engine.Text(sku_config.side_text['sn_code'], 'Arial', '', bc_pt,
                            pil_font=pil_bc, ppi=ppi),
            ]
        )
        bc_row = engine.Row(
            spacing=content_w * 0.014, align='bottom',
            children=[bc_col_left, bc_col_right],
        )

        row2 = engine.Row(
            fixed_width=content_w,
            justify='start',
            spacing=content_w * 0.02,
            align='center',
            children=[info_col, bc_row],
        )

        # ── 总体布局 ─────────────────────────────────────────────────────────────
        main_panel = engine.Column(
            align='left',
            spacing=content_h * 0.11,
            children=[row1, row2],
        )
        start_x = lbl_x + (lbl_w - content_w) / 2.0
        start_y = lbl_y + lbl_h * 0.11
        main_panel.layout(start_x, start_y)
        main_panel.render(pdf)

    def _draw_side_label_high_content(self, pdf: FPDF, sku_config,
                                       lbl_x, lbl_y, lbl_w, lbl_h):
        """
        在高标签（旋转后横向）上叠加绘制文字和条形码（fpdf2 版）。
        坐标以标签横向渲染后的左上角 (lbl_x, lbl_y) 为原点。
        """
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        # 字体大小（比例于 lbl_h）
        bold_px   = int(lbl_h * 0.052 * px_per_mm)
        normal_px = int(lbl_h * 0.043 * px_per_mm)

        pil_bold   = ImageFont.truetype(self.font_paths['Arial Bold'], bold_px)
        pil_normal = ImageFont.truetype(self.font_paths['Arial'], normal_px)

        bold_pt   = bold_px   * 72.0 / ppi
        normal_pt = normal_px * 72.0 / ppi

        spacing_px = 25  # 行间距（原始 px），换算为 mm
        spacing_mm = spacing_px / px_per_mm
        row_spacing = 10.0 / px_per_mm  # Row 内元素水平间距

        gw_bbox = pil_bold.getbbox("G.W./N.W. :", anchor='ls')
        gw_indent_mm = (gw_bbox[2] - gw_bbox[0]) / px_per_mm

        # ── 左侧文字块 ──────────────────────────────────────────────────────────
        row_color = engine.Row(spacing=row_spacing, children=[
            engine.Text("COLOUR  :", 'Arial', 'B', bold_pt, pil_font=pil_bold, ppi=ppi),
            engine.Text(sku_config.color, 'Arial', '', normal_pt, pil_font=pil_normal, ppi=ppi),
        ])
        row_weight_lbs = engine.Row(spacing=row_spacing, children=[
            engine.Text("G.W./N.W. :", 'Arial', 'B', bold_pt, pil_font=pil_bold, ppi=ppi),
            engine.Text(
                (f"{sku_config.side_text['gw_value']} / "
                 f"{sku_config.side_text['nw_value']} LBS"),
                'Arial', '', normal_pt, pil_font=pil_normal, ppi=ppi),
        ])
        row_weight_kg = engine.Row(spacing=row_spacing, children=[
            engine.Spacer(width=gw_indent_mm, height=0.001),
            engine.Text(
                (f"{sku_config.side_text['gw_value'] / 2.20462:.1f} / "
                 f"{sku_config.side_text['nw_value'] / 2.20462:.1f} KG"),
                'Arial', '', normal_pt, pil_font=pil_normal, ppi=ppi),
        ])
        row_box_inch = engine.Row(spacing=row_spacing, children=[
            engine.Text("BOX SIZE :", 'Arial', 'B', bold_pt, pil_font=pil_bold, ppi=ppi),
            engine.Text(
                (f"{sku_config.l_cm/2.54:.1f}\" x "
                 f"{sku_config.w_cm/2.54:.1f}\" x {sku_config.h_cm/2.54:.1f}\""),
                'Arial', '', normal_pt, pil_font=pil_normal, ppi=ppi),
        ])
        row_box_cm = engine.Row(spacing=row_spacing, children=[
            engine.Spacer(width=gw_indent_mm, height=0.001),
            engine.Text(
                (f"{sku_config.l_cm:.1f}cm x "
                 f"{sku_config.w_cm:.1f}cm x {sku_config.h_cm:.1f}cm"),
                'Arial', '', normal_pt, pil_font=pil_normal, ppi=ppi),
        ])
        left_text_block = engine.Column(
            align='left', spacing=spacing_mm,
            children=[row_color, row_weight_lbs, row_weight_kg,
                      row_box_inch, row_box_cm],
        )
        # 原代码：layout(x=26, y=250) px → mm
        left_text_block.layout(lbl_x + 26.0 / px_per_mm, lbl_y + 250.0 / px_per_mm)
        left_text_block.render(pdf)

        # ── 顶部 SKU + 箱号（透明文字，叠在标签已有的暗色区域，用背景色绘制）──
        sku_target_w  = lbl_w * 0.670
        box_target_w  = lbl_w * 0.30

        sku_name_px  = general_functions.get_max_font_size(
            sku_config.sku_name, self.font_paths['Arial Bold'], int(sku_target_w * px_per_mm))
        box_num_px   = general_functions.get_max_font_size(
            sku_config.sku_name, self.font_paths['Arial Bold'], int(box_target_w * px_per_mm))

        pil_sku_name  = ImageFont.truetype(self.font_paths['Arial Bold'], sku_name_px)
        pil_box_num   = ImageFont.truetype(self.font_paths['Arial'], box_num_px)
        sku_name_pt   = sku_name_px * 72.0 / ppi
        box_num_pt    = box_num_px  * 72.0 / ppi

        box_number_text = (f"Box {sku_config.box_number['current_box']} of "
                           f"{sku_config.box_number['total_boxes']}")
        top_pad_x = lbl_h * 0.12
        top_pad_y = lbl_h * 0.06

        top_text_row = engine.Row(
            fixed_width=lbl_w,
            justify='space-between',
            align='bottom',
            spacing=lbl_w * 0.7,
            padding_x=top_pad_x,
            padding_y=top_pad_y,
            children=[
                engine.Text(sku_config.sku_name, 'Arial', 'B', sku_name_pt,
                            pil_font=pil_sku_name, ppi=ppi,
                            color=sku_config.background_color),
                engine.Text(box_number_text, 'Arial', '', box_num_pt,
                            pil_font=pil_box_num, ppi=ppi,
                            color=sku_config.background_color),
            ]
        )
        top_text_row.layout(lbl_x, lbl_y)
        top_text_row.render(pdf)

        # ── 条形码区 ────────────────────────────────────────────────────────────
        bc_font_px  = int(lbl_h * 0.05 * px_per_mm)
        pil_bc_font = ImageFont.truetype(self.font_paths['Arial'], bc_font_px)
        bc_font_pt  = bc_font_px * 72.0 / ppi

        bc_h_mm        = lbl_h * 0.30
        bc_w_left_mm   = bc_h_mm * 2.9
        bc_w_right_mm  = bc_h_mm * 2.0

        img_bc_left  = generate_barcode_image(sku_config.sku_name,
                                              int(bc_w_left_mm  * px_per_mm),
                                              int(bc_h_mm * px_per_mm))
        img_bc_right = generate_barcode_image(sku_config.side_text['sn_code'],
                                              int(bc_w_right_mm * px_per_mm),
                                              int(bc_h_mm * px_per_mm))

        bc_spacing = 40.0 / px_per_mm

        bc_block = engine.Row(
            justify='center',
            align='bottom',
            padding=50.0 / px_per_mm,
            children=[
                engine.Column(align='center', spacing=10.0 / px_per_mm, children=[
                    engine.Image(self._barcode_on_white(img_bc_left)),
                    engine.Text(sku_config.sku_name, 'Arial', '', bc_font_pt,
                                pil_font=pil_bc_font, ppi=ppi),
                ]),
                engine.Spacer(width=bc_spacing, height=0.001),
                engine.Column(align='center', spacing=10.0 / px_per_mm, children=[
                    engine.Image(self._barcode_on_white(img_bc_right)),
                    engine.Text(sku_config.side_text['sn_code'], 'Arial', '', bc_font_pt,
                                pil_font=pil_bc_font, ppi=ppi),
                ]),
            ]
        )
        # 原代码：layout(x=560, y=195) px → mm
        bc_block.layout(lbl_x + 560.0 / px_per_mm, lbl_y + 195.0 / px_per_mm)
        bc_block.render(pdf)
