# -*- coding: utf-8 -*-
"""
Barberpub 天地盖样式 - fpdf2 版
"""
from fpdf import FPDF
from PIL import Image, ImageFont
from style_base import BoxMarkStyle, StyleRegistry
import general_functions
from general_functions import generate_barcode_image
import layout_engine as engine


@StyleRegistry.register
class BarberpubTopAndBottomStyle(BoxMarkStyle):
    """Barberpub 天地盖样式 (fpdf2 版)"""

    def get_style_name(self):
        return "barberpub_topandbottom"

    def get_style_description(self):
        return "Barberpub 天地盖箱唛样式"

    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'ppi', 'color', 'product',
                'side_text', 'sku_name', 'box_number']

    def get_preview_images(self):
        preview_dir = self.base_dir / 'assets' / 'Barberpub' / '天地盖' / '实例生成图'
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
        res_base = self.base_dir / 'assets' / 'Barberpub' / '天地盖' / '矢量文件'
        self.resources = {
            'icon_logo':       res_base / '正唛logo.png',
            'icon_company':    res_base / '正唛公司信息.png',
            'icon_webside':    res_base / '侧唛网址.png',
            'icon_side_label': res_base / '侧唛标签.png',
            'icon_slogan':     res_base / '正唛宣传语.png',
            'icon_box_info':   res_base / '正唛多箱选择框.png',
        }

    def _load_fonts(self):
        font_base = self.base_dir / 'assets' / 'Barberpub' / '天地盖' / '箱唛字体'
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

    def _get_font_size(self, text, font_key, target_width_mm, ppi,
                       max_height_mm=None, max_size=1000):
        target_px = int(target_width_mm * ppi / 25.4)
        max_height_px = int(max_height_mm * ppi / 25.4) if max_height_mm else None
        size_px = general_functions.get_max_font_size(
            text, self.font_paths[font_key], target_px,
            max_height=max_height_px, max_size=max_size)
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

    def _draw_text_mt(self, pdf, x_center_mm, y_top_mm, text,
                      font_family, font_style, font_size_pt, pil_font, ppi,
                      color=(0, 0, 0)):
        left_mm, top_mm, right_mm, _ = self._pil_bbox_mm(pil_font, text, ppi)
        width_mm = right_mm - left_mm
        x_mm = x_center_mm - width_mm / 2.0
        baseline_y = y_top_mm + (-top_mm)
        r, g, b = color
        pdf.set_text_color(r, g, b)
        pdf.set_font(font_family, font_style, font_size_pt)
        pdf.text(x_mm, baseline_y, text)

    @staticmethod
    def _img_dims_mm(img_path, height_mm=None, width_mm=None):
        """Compute the mm dimensions of an image given a target height or width."""
        with Image.open(img_path) as img:
            orig_w, orig_h = img.size
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

    def _draw_diagonal_stripes_pdf(self, pdf, x_mm, y_mm, w_mm, h_mm,
                                    stripe_w_mm=4.0, bg_color=(200, 180, 140)):
        """Draw alternating diagonal warning stripes in a rectangle using PDF polygons."""
        with pdf.rect_clip(x_mm, y_mm, w_mm, h_mm):
            r, g, b = bg_color
            pdf.set_fill_color(r, g, b)
            pdf.rect(x_mm, y_mm, w_mm, h_mm, style='F')
            pdf.set_fill_color(0, 0, 0)
            stripe_offset = stripe_w_mm * 1.5
            num = int((w_mm + h_mm) / stripe_offset) + 2
            for i in range(num):
                sx = x_mm + i * stripe_offset - h_mm
                pts = [
                    (sx,                           y_mm + h_mm),
                    (sx + stripe_w_mm,             y_mm + h_mm),
                    (sx + stripe_w_mm + h_mm,      y_mm),
                    (sx + h_mm,                    y_mm),
                ]
                pdf.polygon(pts, style='F')

    # ── 面板绘制方法 ────────────────────────────────────────────────────────────

    def _draw_front_back_panel(self, pdf: FPDF, sku_config,
                                x_mm, y_mm, w_mm, h_mm, rotate_180=False):
        """绘制前/后侧面板。back 面通过 pdf.rotation(180) 翻转。"""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        def _render():
            # --- 区域 A: 顶部 Logo (居中) ---
            logo_h_mm = h_mm * 0.26
            logo_w_mm, _ = self._img_dims_mm(self.resources['icon_logo'], height_mm=logo_h_mm)
            margin_top = 25.0  # 2.5 cm
            logo_x = x_mm + (w_mm - logo_w_mm) / 2.0
            pdf.image(self.resources['icon_logo'],
                      x=logo_x, y=y_mm + margin_top,
                      w=logo_w_mm, h=logo_h_mm)

            # --- 区域 B: SKU 文字 (居中, 位于 Logo 下方) ---
            sku_text = sku_config.sku_name
            sku_pt, pil_sku = self._get_font_size(
                sku_text, 'CentSchbook', w_mm * 0.85, ppi, max_size=1000)
            sku_y_top = y_mm + margin_top + logo_h_mm + 10.0  # +1 cm gap
            self._draw_text_mt(pdf, x_mm + w_mm / 2.0, sku_y_top,
                               sku_text, 'CentSchbook', '', sku_pt, pil_sku, ppi)

            # --- 区域 C: 底部信息框 ---
            margin_bottom = 24.0  # 2.4 cm
            info_frame_px = int(h_mm * 0.07 * px_per_mm)
            info_frame_pt = info_frame_px * 72.0 / ppi
            info_val_px   = int(h_mm * 0.06 * px_per_mm)
            info_val_pt   = info_val_px * 72.0 / ppi
            pil_frame = ImageFont.truetype(self.font_paths['CentSchbook'], info_frame_px)
            pil_val   = ImageFont.truetype(self.font_paths['CentSchbook'], info_val_px)

            info_y = y_mm + h_mm - margin_bottom - info_frame_px / px_per_mm

            gw_text    = "G.W./N.W."
            weight_val = (f"{sku_config.side_text['gw_value']} / "
                          f"{sku_config.side_text['nw_value']} LBS")
            box_text   = "BOX SIZE"
            dim_val    = (f'{sku_config.l_in:.1f}" x '
                          f'{sku_config.w_in:.1f}" x {sku_config.h_in:.1f}"')

            gw_l, gw_t, gw_r, gw_b = self._pil_bbox_mm(pil_frame, gw_text, ppi)
            gw_w_mm = gw_r - gw_l
            gw_h_mm = gw_b - gw_t
            bx_l, bx_t, bx_r, bx_b = self._pil_bbox_mm(pil_frame, box_text, ppi)
            bx_w_mm = bx_r - bx_l
            bx_h_mm = bx_b - bx_t

            pad_x      = 7.0   # 0.7 cm
            pad_y_top  = 6.0 * 0.7
            pad_y_bot  = 6.0 * 1.4
            radius_mm  = 16 * 25.4 / ppi
            val_gap    = 18.0  # ~1.8 cm gap between label and value
            frame_val_shift = (info_frame_px - info_val_px) / (2.0 * px_per_mm)

            # Left rounded bg (G.W./N.W.)
            left_box_x = x_mm + 100.0  # 10 cm from left
            pdf.set_fill_color(0, 0, 0)
            pdf.rect(left_box_x - pad_x, info_y - pad_y_top,
                     gw_w_mm + 2 * pad_x, gw_h_mm + pad_y_top + pad_y_bot,
                     style='F', round_corners=True, corner_radius=radius_mm)
            bg_r, bg_g, bg_b = sku_config.background_color
            self._draw_text_top_left(pdf, left_box_x, info_y, gw_text,
                                     'CentSchbook', '', info_frame_pt, pil_frame, ppi,
                                     color=(bg_r, bg_g, bg_b))
            # Weight value to the right
            self._draw_text_top_left(pdf, left_box_x + gw_w_mm + val_gap,
                                     info_y + frame_val_shift,
                                     weight_val, 'CentSchbook', '', info_val_pt, pil_val, ppi)

            # Right rounded bg (BOX SIZE)
            right_box_x = x_mm + w_mm / 2.0 + 25.0  # canvas_w/2 + 2.5 cm
            pdf.set_fill_color(0, 0, 0)
            pdf.rect(right_box_x - pad_x, info_y - pad_y_top,
                     bx_w_mm + 2 * pad_x, bx_h_mm + pad_y_top + pad_y_bot,
                     style='F', round_corners=True, corner_radius=radius_mm)
            self._draw_text_top_left(pdf, right_box_x, info_y, box_text,
                                     'CentSchbook', '', info_frame_pt, pil_frame, ppi,
                                     color=(bg_r, bg_g, bg_b))
            self._draw_text_top_left(pdf, right_box_x + bx_w_mm + val_gap,
                                     info_y + frame_val_shift,
                                     dim_val, 'CentSchbook', '', info_val_pt, pil_val, ppi)

        if rotate_180:
            cx = x_mm + w_mm / 2.0
            cy = y_mm + h_mm / 2.0
            with pdf.rotation(180, cx, cy):
                _render()
        else:
            _render()

    def _draw_top_panel(self, pdf: FPDF, sku_config, x_mm, y_mm, w_mm, h_mm):
        """绘制顶面（Top Panel）"""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4
        margin_top   = 20.0  # 2 cm
        margin_left  = 30.0  # 3 cm
        margin_right = 30.0  # 3 cm

        # --- 区域 A: 左上角 Logo ---
        logo_h_mm = h_mm * 0.16
        logo_w_mm, _ = self._img_dims_mm(self.resources['icon_logo'], height_mm=logo_h_mm)
        pdf.image(self.resources['icon_logo'],
                  x=x_mm + margin_left, y=y_mm + margin_top,
                  w=logo_w_mm, h=logo_h_mm)

        # --- 区域 B: 右上角公司信息 ---
        company_h_mm = h_mm * 0.06
        company_w_mm, _ = self._img_dims_mm(self.resources['icon_company'], height_mm=company_h_mm)
        pdf.image(self.resources['icon_company'],
                  x=x_mm + w_mm - company_w_mm - margin_right,
                  y=y_mm + margin_top,
                  w=company_w_mm, h=company_h_mm)

        # --- 区域 C: 中间产品名 + 宣传语 (整体垂直居中) ---
        product_text = sku_config.product
        product_pt, pil_product = self._get_font_size(
            product_text, 'DroidSans', w_mm * 0.65, ppi, max_height_mm=h_mm * 0.20)
        p_l, p_t, p_r, p_b = self._pil_bbox_mm(pil_product, product_text, ppi)
        product_h_mm = p_b - p_t

        slogan_h_mm = h_mm * 0.05
        slogan_w_mm, _ = self._img_dims_mm(self.resources['icon_slogan'], height_mm=slogan_h_mm)
        vertical_gap_mm = 10.0  # 1 cm
        total_center_h  = product_h_mm + vertical_gap_mm + slogan_h_mm
        center_y_start  = y_mm + h_mm * 0.45 - total_center_h / 2.0

        self._draw_text_mt(pdf, x_mm + w_mm / 2.0, center_y_start,
                           product_text, 'DroidSans', '', product_pt, pil_product, ppi)
        slogan_x = x_mm + (w_mm - slogan_w_mm) / 2.0
        slogan_y = center_y_start + product_h_mm + vertical_gap_mm
        pdf.image(self.resources['icon_slogan'],
                  x=slogan_x, y=slogan_y, w=slogan_w_mm, h=slogan_h_mm)

        # --- 区域 E: 左下角颜色 + SKU 代码 ---
        margin_bottom = 35.0   # 3.5 cm
        text_v_gap    = 3.0

        color_text    = f"({sku_config.color.upper()})"
        color_size_px = int(h_mm * 0.06 * px_per_mm)
        color_size_pt = color_size_px * 72.0 / ppi
        pil_color_f   = ImageFont.truetype(self.font_paths['CentSchbook'], color_size_px)
        c_l, c_t, c_r, c_b = self._pil_bbox_mm(pil_color_f, color_text, ppi)
        color_h_mm = c_b - c_t

        sku_code_pt, pil_sku_code = self._get_font_size(
            sku_config.sku_name, 'CentSchbook', w_mm * 0.52, ppi,
            max_height_mm=h_mm * 0.14)
        s_l, s_t, s_r, s_b = self._pil_bbox_mm(pil_sku_code, sku_config.sku_name, ppi)
        sku_code_h_mm = s_b - s_t

        sku_code_y_top = y_mm + h_mm - margin_bottom - sku_code_h_mm - 18.0
        color_y_top    = sku_code_y_top - color_h_mm - text_v_gap
        self._draw_text_top_left(pdf, x_mm + margin_left, color_y_top,
                                 color_text, 'CentSchbook', '', color_size_pt, pil_color_f, ppi)
        self._draw_text_top_left(pdf, x_mm + margin_left, sku_code_y_top,
                                 sku_config.sku_name, 'CentSchbook', '',
                                 sku_code_pt, pil_sku_code, ppi)

        # --- 区域 F: 右下角箱号信息图 + 叠加���字 ---
        box_info_h_mm = h_mm * 0.10
        box_info_w_mm, _ = self._img_dims_mm(self.resources['icon_box_info'],
                                             height_mm=box_info_h_mm)
        box_info_x = x_mm + w_mm - box_info_w_mm - margin_right
        box_info_y = y_mm + h_mm - margin_bottom - box_info_h_mm - 5.0
        pdf.image(self.resources['icon_box_info'],
                  x=box_info_x, y=box_info_y, w=box_info_w_mm, h=box_info_h_mm)

        # BOX 文字（白色，叠在图标黑色区域）
        box_txt = (f"BOX {sku_config.box_number['current_box']} OF "
                   f"{sku_config.box_number['total_boxes']}")
        box_txt_px = int(box_info_h_mm * 0.40 * px_per_mm)
        box_txt_pt = box_txt_px * 72.0 / ppi
        pil_box_txt = ImageFont.truetype(self.font_paths['CentSchbook'], box_txt_px)
        bg_r, bg_g, bg_b = sku_config.background_color
        self._draw_text_mt(pdf,
                           box_info_x + box_info_w_mm / 2.0,
                           box_info_y + box_info_h_mm * 0.12,
                           box_txt, 'CentSchbook', '', box_txt_pt, pil_box_txt, ppi,
                           color=(bg_r, bg_g, bg_b))

        # 产地文字（黑色，叠在图标白色区域）
        origin_text  = sku_config.side_text['origin_text']
        origin_px    = int(box_info_h_mm * 0.22 * px_per_mm)
        origin_pt    = origin_px * 72.0 / ppi
        pil_origin   = ImageFont.truetype(self.font_paths['CalibriB'], origin_px)
        self._draw_text_mt(pdf,
                           box_info_x + box_info_w_mm / 2.0,
                           box_info_y + box_info_h_mm * 0.68,
                           origin_text, 'CalibriB', '', origin_pt, pil_origin, ppi)

        # --- 区域 G: 底部斜纹条 ---
        stripe_h_mm = 15.0   # 1.5 cm
        stripe_y    = y_mm + h_mm - stripe_h_mm - 10.0  # 1.0 cm bottom margin
        self._draw_diagonal_stripes_pdf(
            pdf, x_mm, stripe_y, w_mm, stripe_h_mm,
            stripe_w_mm=4.0, bg_color=sku_config.background_color)

    def _draw_side_panel(self, pdf: FPDF, sku_config,
                          x_mm, y_mm, w_mm, h_mm, rotation_deg):
        """
        绘制左/右侧面板。

        页面上面板尺寸：w_mm = h_cm×10，h_mm = w_cm×10
        自然画布（旋转前）：nat_w = h_mm，nat_h = w_mm
        """
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        nat_w = h_mm   # 自然宽 = 高方向
        nat_h = w_mm   # 自然高 = 宽方向

        cx = x_mm + w_mm / 2.0
        cy = y_mm + h_mm / 2.0
        nat_x = cx - nat_w / 2.0
        nat_y = cy - nat_h / 2.0

        # --- SKU 大字（居中，视觉重心在高度37%处）---
        sku_text = sku_config.sku_name
        sku_pt, pil_sku = self._get_font_size(
            sku_text, 'CentSchbook', nat_w * 0.9, ppi, max_height_mm=nat_h * 0.55)
        s_l, s_t, s_r, s_b = self._pil_bbox_mm(pil_sku, sku_text, ppi)
        sku_h_mm  = s_b - s_t
        sku_y_top = nat_y + nat_h * 0.37 - sku_h_mm / 2.0

        # --- 侧唛网址图（左下角）---
        web_path  = self.resources['icon_webside']
        web_w_mm, web_h_mm = self._img_dims_mm(web_path, width_mm=nat_w * 0.53)
        margin_side   = 30.0  # 3 cm
        margin_bottom = 55.0  # 5.5 cm
        web_x = nat_x + margin_side
        web_y = nat_y + nat_h - margin_bottom - web_h_mm * 1.4 - web_h_mm * 0.4

        # --- 侧唛标签图（右下角）+ 条形码叠加 ---
        label_path = self.resources['icon_side_label']
        label_h_mm = nat_h * 0.22
        label_w_mm, _ = self._img_dims_mm(label_path, height_mm=label_h_mm)
        label_x = nat_x + nat_w - label_w_mm - margin_side
        label_y = nat_y + nat_h - label_h_mm - margin_bottom

        with pdf.rotation(rotation_deg, cx, cy):
            self._draw_text_mt(pdf, nat_x + nat_w / 2.0, sku_y_top,
                               sku_text, 'CentSchbook', '', sku_pt, pil_sku, ppi)
            pdf.image(web_path, x=web_x, y=web_y, w=web_w_mm, h=web_h_mm)
            pdf.image(label_path, x=label_x, y=label_y, w=label_w_mm, h=label_h_mm)
            self._draw_side_label_barcodes(
                pdf, sku_config, label_x, label_y, label_w_mm, label_h_mm, ppi)

    def _draw_side_label_barcodes(self, pdf: FPDF, sku_config,
                                   lbl_x, lbl_y, lbl_w, lbl_h, ppi):
        """在侧唛标签背景上叠加绘制两个条形码及其文字。"""
        px_per_mm = ppi / 25.4

        barcode_zone_h  = lbl_h * 0.35
        barcode_only_h  = barcode_zone_h * 0.89
        barcode_y       = lbl_y + barcode_zone_h * 0.10
        text_size_px    = int(barcode_zone_h * 0.22 * px_per_mm)
        text_size_pt    = text_size_px * 72.0 / ppi
        pil_txt         = ImageFont.truetype(self.font_paths['CentSchbook'], text_size_px)
        text_y          = barcode_y + barcode_only_h + barcode_zone_h * 0.01

        # SKU 条形码（52% 宽，1% 左边距）
        sku_name  = sku_config.sku_name
        sku_bc_w  = lbl_w * 0.52
        sku_bc_x  = lbl_x + lbl_w * 0.01
        sku_bc_img = generate_barcode_image(
            sku_name,
            int(sku_bc_w * px_per_mm),
            int(barcode_only_h * px_per_mm),
        )
        pdf.image(self._barcode_on_white(sku_bc_img),
                  x=sku_bc_x, y=barcode_y, w=sku_bc_w, h=barcode_only_h)
        self._draw_text_mt(pdf, sku_bc_x + sku_bc_w / 2.0, text_y,
                           sku_name, 'CentSchbook', '', text_size_pt, pil_txt, ppi)

        # SN 条形码（42% 宽，从 56% 开始）
        sn_code  = sku_config.side_text['sn_code']
        sn_bc_w  = lbl_w * 0.42
        sn_bc_x  = lbl_x + lbl_w * 0.56
        sn_bc_img = generate_barcode_image(
            sn_code,
            int(sn_bc_w * px_per_mm),
            int(barcode_only_h * px_per_mm),
        )
        pdf.image(self._barcode_on_white(sn_bc_img),
                  x=sn_bc_x, y=barcode_y, w=sn_bc_w, h=barcode_only_h)
        self._draw_text_mt(pdf, sn_bc_x + sn_bc_w / 2.0, text_y,
                           sn_code, 'CentSchbook', '', text_size_pt, pil_txt, ppi)
