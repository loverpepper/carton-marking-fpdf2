# -*- coding: utf-8 -*-
"""
Lovupet 对开盖样式 - fpdf2 版
"""
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import pathlib as Path
from style_base import BoxMarkStyle, StyleRegistry
import general_functions
from general_functions import generate_barcode_image
import re


@StyleRegistry.register
class LovupetDoubleOpeningStyle(BoxMarkStyle):
    '''Lovupet 对开盖样式'''
    
    def get_style_name(self):
        return "lovupet_doubleopening"
    
    def get_style_description(self):
        return "Lovupet 对开盖箱唛样式"
    
    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'ppi', 'color', 'product', 'side_text', 'sku_name']
    
    def get_layout_config(self, sku_config):
        '''
        Lovupet 对开盖样式 - 5块布局（4列3行）
        '''
        
        x0 = 0
        x1 = sku_config.l_px
        x2 = sku_config.l_px + sku_config.w_px
        x3 = sku_config.l_px * 2 + sku_config.w_px
        
        y0 = 0
        y1 = sku_config.half_w_px
        y2 = sku_config.half_w_px + sku_config.h_px
        
        return {
            # 第一行：顶盖层 (Top Flaps)
            "flap_top_front1":  (x0, y0, sku_config.l_px, sku_config.half_w_px),
            "flap_top_side1": (x1, y0, sku_config.w_px, sku_config.half_w_px),
            "flap_top_front2":  (x2, y0, sku_config.l_px, sku_config.half_w_px),
            "flap_top_side2": (x3, y0, sku_config.w_px, sku_config.half_w_px),

            # 第二行：正身层 (Main Body)
            "panel_front1":     (x0, y1, sku_config.l_px, sku_config.h_px),
            "panel_side1":    (x1, y1, sku_config.w_px, sku_config.h_px),
            "panel_front2":     (x2, y1, sku_config.l_px, sku_config.h_px),
            "panel_side2":    (x3, y1, sku_config.w_px, sku_config.h_px),

            # 第三行：底盖层 (Bottom Flaps)
            "flap_btm_front1":  (x0, y2, sku_config.l_px, sku_config.half_w_px),
            "flap_btm_side1": (x1, y2, sku_config.w_px, sku_config.half_w_px),
            "flap_btm_front2":  (x2, y2, sku_config.l_px, sku_config.half_w_px),
            "flap_btm_side2": (x3, y2, sku_config.w_px, sku_config.half_w_px),
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
        half_w_mm = w_mm / 2

        x0, x1 = 0.0, l_mm
        x2, x3 = l_mm + w_mm, 2 * l_mm + w_mm
        y0, y1, y2 = 0.0, half_w_mm, half_w_mm + h_mm

        return {
            "flap_top_front1": (x0, y0, l_mm,      half_w_mm),
            "flap_top_side1":  (x1, y0, w_mm,      half_w_mm),
            "flap_top_front2": (x2, y0, l_mm,      half_w_mm),
            "flap_top_side2":  (x3, y0, w_mm,      half_w_mm),
            "panel_front1":    (x0, y1, l_mm,      h_mm),
            "panel_side1":     (x1, y1, w_mm,      h_mm),
            "panel_front2":    (x2, y1, l_mm,      h_mm),
            "panel_side2":     (x3, y1, w_mm,      h_mm),
            "flap_btm_front1": (x0, y2, l_mm,      half_w_mm),
            "flap_btm_side1":  (x1, y2, w_mm,      half_w_mm),
            "flap_btm_front2": (x2, y2, l_mm,      half_w_mm),
            "flap_btm_side2":  (x3, y2, w_mm,      half_w_mm),
        }

    # ── fpdf2 字体注册 ──────────────────────────────────────────────────────────

    def register_fonts(self, pdf: FPDF):
        """向 FPDF 对象注册本样式使用的所有字体"""
        pdf.add_font('Arial',      '',  self.font_paths['Arial Regular'])
        pdf.add_font('Arial',      'B', self.font_paths['Arial Bold'])
        pdf.add_font('ArialBlack', '',   self.font_paths['Arial Black'])
        pdf.add_font('Calibri',    '',   self.font_paths['Calibri Regular'])
        pdf.add_font('Calibri',    'B',  self.font_paths['Calibri Bold'])
        pdf.add_font('CalibraL',   '',   self.font_paths['Calibri Light'])

    # ── 核心绘制入口 ────────────────────────────────────────────────────────────

    def draw_to_pdf(self, pdf: FPDF, sku_config):
        """将所有面板直接绘制到已添加页面的 FPDF 对象上"""
        layout = self.get_layout_config_mm(sku_config)

        # 填充各面板背景色
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

        # 两块正面面板
        self._draw_front_panel_v(pdf, sku_config, x0, y1, l_mm, h_mm)
        self._draw_front_panel_v(pdf, sku_config, x2, y1, l_mm, h_mm)

        # 两块侧面面板
        self._draw_side_panel_v(pdf, sku_config, x1, y1, w_mm, h_mm)
        self._draw_side_panel_v(pdf, sku_config, x3, y1, w_mm, h_mm)

        # 左上翻盖（箱子提示语）
        self._draw_flap_left_up_v(pdf, sku_config, x0, 0.0, l_mm, half_w_mm)

        # 其余翻盖均为空白（已由背景色填充）

    def _load_resources(self):
        """加载 Lovupet 对开盖样式的图片资源（存储 Path，按需打开）"""
        res_base = self.base_dir / 'assets' / 'Lovupet' / '对开盖' / '矢量文件'
        self.resources = {
            # 正唛有网址、logo、猫抓图、宠物图
            'icon_logo':          res_base / 'logo.png',
            'icon_web':           res_base / '网址框.png',
            'icon_product':       res_base / '宠物.png',
            'icon_catclaw':       res_base / '猫抓.png',
            # 侧唛有标签框 (条形码定界框.png 资源文件暂缺，保留 Path 供将来补充)
            'icon_paste_barcode': res_base / '条形码定界框.png',
            'icon_side_label':    res_base / '注意事项.png',
            # 左上盖有一个箱子提示语
            'icon_box_hint':      res_base / '箱子提示语.png',
        }
    
    def _load_fonts(self):
        """加载字体路径"""
        font_base = self.base_dir / 'assets' / 'Lovupet' / '对开盖' / '箱唛字体'
        self.font_paths = {
            'Arial Regular': str(font_base / 'arial.ttf'),
            'Arial Bold': str(font_base / 'arialbd.ttf'),
            'Arial Black': str(font_base / 'ariblk.ttf'),
            'Calibri Regular': str(font_base / 'calibri.ttf'),
            'Calibri Bold': str(font_base / 'calibri bold.ttf'),
            'Calibri Light': str(font_base / 'Calibri_Light.ttf'),
        }

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
        """使用 anchor='ls' 获取文字边框并换算为 mm"""
        left, top, right, bottom = pil_font.getbbox(text, anchor='ls')
        px_per_mm = ppi / 25.4
        return left / px_per_mm, top / px_per_mm, right / px_per_mm, bottom / px_per_mm

    def _draw_text_top_left(self, pdf, x_mm, y_top_mm, text,
                             font_family, font_style, font_size_pt, pil_font, ppi,
                             color=(0, 0, 0)):
        """以左-顶锚点绘制文字"""
        _, top_mm, _, _ = self._pil_bbox_mm(pil_font, text, ppi)
        baseline_y = y_top_mm + (-top_mm)
        r, g, b = color
        pdf.set_text_color(r, g, b)
        pdf.set_font(font_family, font_style, font_size_pt)
        pdf.text(x_mm, baseline_y, text)

    def _draw_text_top_center(self, pdf, x_center_mm, y_top_mm, text,
                               font_family, font_style, font_size_pt, pil_font, ppi,
                               color=(0, 0, 0)):
        """以中-顶锚点绘制文字"""
        left_mm, top_mm, right_mm, _ = self._pil_bbox_mm(pil_font, text, ppi)
        text_w_mm = right_mm - left_mm
        x_mm = x_center_mm - text_w_mm / 2.0
        baseline_y = y_top_mm + (-top_mm)
        r, g, b = color
        pdf.set_text_color(r, g, b)
        pdf.set_font(font_family, font_style, font_size_pt)
        pdf.text(x_mm, baseline_y, text)

    def _draw_text_mid_center(self, pdf, cx_mm, cy_mm, text,
                               font_family, font_style, font_size_pt, pil_font, ppi,
                               color=(0, 0, 0)):
        """以中-中锚点绘制文字"""
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
        """根据给定的 height_mm 或 width_mm 按比例计算图片尺寸 (mm)"""
        import pathlib
        if isinstance(img_or_path, (str, pathlib.Path)):
            with Image.open(img_or_path) as img:
                orig_w, orig_h = img.size
        else:
            orig_w, orig_h = img_or_path.width, img_or_path.height
        if height_mm is not None:
            return height_mm * orig_w / orig_h, height_mm
        if width_mm is not None:
            return width_mm, width_mm * orig_h / orig_w
        return orig_w, orig_h

    # ── 翻盖面板 ─────────────────────────────────────────────────────────────

    def _draw_flap_left_up_v(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm):
        """左翻盖（上）：箱子提示语图，宽 80%，居中"""
        icon_path = self.resources['icon_box_hint']
        img_w_mm, img_h_mm = self._img_dims_mm(icon_path, width_mm=w_mm * 0.8)
        img_x = x_mm + (w_mm - img_w_mm) / 2
        img_y = y_mm + (h_mm - img_h_mm) / 2
        pdf.image(icon_path, x=img_x, y=img_y, w=img_w_mm, h=img_h_mm)

    # ── 正面面板 ─────────────────────────────────────────────────────────────

    def _draw_front_panel_v(self, pdf: FPDF, sku_config, x_mm, y_mm, w_mm, h_mm):
        """绘制正面（正唛）面板 - 矢量文字 + 光栅图标"""
        ppi = sku_config.ppi

        upper_blank_mm = 70.0   # 7cm
        box_h_mm = 100.0        # 10cm black box at bottom
        content_h_mm = h_mm - upper_blank_mm - box_h_mm

        # ── 1. Logo (72% width, centered) ────────────────────────────────────
        logo_w_mm, logo_h_mm = self._img_dims_mm(
            self.resources['icon_logo'], width_mm=w_mm * 0.72)

        # ── 2. Cloud color image (40% width, PIL-generated shape) ────────────
        cloud_base_px = int(w_mm * 0.47 * ppi / 25.4)
        cloud_pil = generate_cloud_color_image(
            sku_config=sku_config,
            font_path=self.font_paths['Arial Bold'],
            base_size=cloud_base_px,
        )
        cloud_w_mm, cloud_h_mm = self._img_dims_mm(
            cloud_pil, width_mm=w_mm * 0.40)

        # ── 3. Product image (95% width) ─────────────────────────────────────
        product_w_mm, product_h_mm = self._img_dims_mm(
            self.resources['icon_product'], width_mm=w_mm * 0.95)

        # ── 4. Web frame image (78% width) ───────────────────────────────────
        web_w_mm, web_h_mm = self._img_dims_mm(
            self.resources['icon_web'], width_mm=w_mm * 0.78)

        # ── 5. Catclaw image (50% width) ─────────────────────────────────────
        catclaw_w_mm, catclaw_h_mm = self._img_dims_mm(
            self.resources['icon_catclaw'], width_mm=w_mm * 0.50)

        # ── space-between layout ─────────────────────────────────────────────
        # Three groups: upper_col (logo+cloud), middle_col (product+web), catclaw
        spacing_upper = h_mm * 0.03
        upper_h = logo_h_mm + spacing_upper + cloud_h_mm

        spacing_middle = h_mm * 0.018
        middle_h = product_h_mm + spacing_middle + web_h_mm

        groups = [upper_h, middle_h, catclaw_h_mm]
        total_groups_h = sum(groups)
        remaining = content_h_mm - total_groups_h
        if len(groups) > 1:
            gap = remaining / (len(groups) - 1)
        else:
            gap = 0.0

        content_y = y_mm + upper_blank_mm
        cx = x_mm + w_mm / 2.0

        # ── Draw upper group (logo + cloud) ──────────────────────────────────
        cur_y = content_y
        pdf.image(self.resources['icon_logo'],
                  x=cx - logo_w_mm / 2, y=cur_y,
                  w=logo_w_mm, h=logo_h_mm)
        cur_y += logo_h_mm + spacing_upper
        pdf.image(cloud_pil,
                  x=cx - cloud_w_mm / 2, y=cur_y,
                  w=cloud_w_mm, h=cloud_h_mm)

        # ── Draw middle group (product + web) ────────────────────────────────
        cur_y = content_y + upper_h + gap
        pdf.image(self.resources['icon_product'],
                  x=cx - product_w_mm / 2, y=cur_y,
                  w=product_w_mm, h=product_h_mm)
        cur_y += product_h_mm + spacing_middle
        pdf.image(self.resources['icon_web'],
                  x=cx - web_w_mm / 2, y=cur_y,
                  w=web_w_mm, h=web_h_mm)

        # ── Draw catclaw ─────────────────────────────────────────────────────
        cur_y = content_y + upper_h + gap + middle_h + gap
        pdf.image(self.resources['icon_catclaw'],
                  x=cx - catclaw_w_mm / 2, y=cur_y,
                  w=catclaw_w_mm, h=catclaw_h_mm)

        # ── 6. Black SKU box (10cm, bottom) ──────────────────────────────────
        box_y = y_mm + h_mm - box_h_mm
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(x_mm, box_y, w_mm, box_h_mm, style='F')

        sku_text = sku_config.sku_name if sku_config.sku_name else "SKU12345"
        sku_pt, pil_sku = self._get_font_size_constrained(
            sku_text, 'Arial Bold', w_mm * 0.95, box_h_mm * 0.7, ppi)
        r, g, b = sku_config.background_color
        self._draw_text_mid_center(
            pdf, x_mm + w_mm / 2, box_y + box_h_mm / 2,
            sku_text, 'Arial', 'B', sku_pt, pil_sku, ppi,
            color=(r, g, b))

    # ── 侧面面板 ─────────────────────────────────────────────────────────────

    def _draw_side_panel_v(self, pdf: FPDF, sku_config, x_mm, y_mm, w_mm, h_mm):
        """绘制侧面（侧唛）面板 - 矢量文字 + 光栅图标"""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        upper_blank_mm = 50.0   # 5cm
        box_h_mm = 100.0        # 10cm black box at bottom
        content_h_mm = h_mm - upper_blank_mm - box_h_mm

        # ── 1. Barcode frame (rotated 90°, 5cm height, right-aligned) ────────
        try:
            barcode_frame = Image.open(self.resources['icon_paste_barcode']).convert('RGBA')
            barcode_frame = barcode_frame.rotate(90, expand=True)
            bc_frame_w_mm, bc_frame_h_mm = self._img_dims_mm(
                barcode_frame, height_mm=50.0)
            padding_x_mm = w_mm * 0.08
            bc_frame_x = x_mm + w_mm - padding_x_mm - bc_frame_w_mm
            bc_frame_y = y_mm + upper_blank_mm
            pdf.image(barcode_frame,
                      x=bc_frame_x, y=bc_frame_y,
                      w=bc_frame_w_mm, h=bc_frame_h_mm)
        except FileNotFoundError:
            bc_frame_h_mm = 50.0

        # ── 2. Logo (71% width, centered) ────────────────────────────────────
        logo_w_mm, logo_h_mm = self._img_dims_mm(
            self.resources['icon_logo'], width_mm=w_mm * 0.71)

        # ── 3. Side label (92% width, filled with data) ─────────────────────
        label_w_mm, label_h_mm = self._img_dims_mm(
            self.resources['icon_side_label'], width_mm=w_mm * 0.92)

        # ── space-between layout for barcode_frame row, logo, label ──────────
        # Nudge adjustments from original PIL code:
        logo_nudge_y = h_mm * 0.03
        label_nudge_y = -h_mm * 0.11

        groups = [bc_frame_h_mm, logo_h_mm, label_h_mm]
        total_groups_h = sum(groups)
        remaining = content_h_mm - total_groups_h
        if len(groups) > 1:
            gap = remaining / (len(groups) - 1)
        else:
            gap = 0.0

        content_y = y_mm + upper_blank_mm
        cx = x_mm + w_mm / 2.0

        # Logo position (second group)
        logo_y = content_y + bc_frame_h_mm + gap + logo_nudge_y
        pdf.image(self.resources['icon_logo'],
                  x=cx - logo_w_mm / 2, y=logo_y,
                  w=logo_w_mm, h=logo_h_mm)

        # Label position (third group)
        label_y = content_y + bc_frame_h_mm + gap + logo_h_mm + gap + label_nudge_y
        label_x = cx - label_w_mm / 2

        # Embed the bare label template
        pdf.image(self.resources['icon_side_label'],
                  x=label_x, y=label_y,
                  w=label_w_mm, h=label_h_mm)

        # ── Overlay dynamic text/barcodes on label ───────────────────────────
        self._draw_side_label_overlay(
            pdf, sku_config, label_x, label_y, label_w_mm, label_h_mm)

        # ── 4. Black SKU box (10cm, bottom) ──────────────────────────────────
        box_y = y_mm + h_mm - box_h_mm
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(x_mm, box_y, w_mm, box_h_mm, style='F')

        sku_text = sku_config.sku_name if sku_config.sku_name else "SKU12345"
        sku_pt, pil_sku = self._get_font_size_constrained(
            sku_text, 'Arial Bold', w_mm * 0.95, box_h_mm * 0.7, ppi)
        r, g, b = sku_config.background_color
        self._draw_text_mid_center(
            pdf, x_mm + w_mm / 2, box_y + box_h_mm / 2,
            sku_text, 'Arial', 'B', sku_pt, pil_sku, ppi,
            color=(r, g, b))

    # ── 标签内容叠加 ─────────────────────────────────────────────────────────

    def _draw_side_label_overlay(self, pdf, sku_config, label_x, label_y,
                                  label_w, label_h):
        """在侧唛标签模板上叠加绘制动态内容（矢量文字 + 条形码图片）"""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        # ── Weight / box size text (left-bottom area of label) ───────────────
        gw_val = sku_config.side_text.get('gw_value', '0.0')
        nw_val = sku_config.side_text.get('nw_value', '0.0')
        weight_text = f"G.W./N.W. : {gw_val} / {nw_val} lbs"

        box_text = (f"BOX SIZE : {sku_config.l_in:.1f}\"x"
                    f"{sku_config.w_in:.1f}\"x{sku_config.h_in:.1f}\"")

        font_h_mm = label_h * 0.08
        font_px = max(int(font_h_mm * px_per_mm), 10)
        font_pt = font_px * 72.0 / ppi
        pil_f = ImageFont.truetype(self.font_paths['Arial Bold'], font_px)

        text_start_x = label_x + label_w * 0.016

        # weight at 72% height (anchor "lm" → left-middle → use top-left)
        _, wt_top, _, wt_bot = self._pil_bbox_mm(pil_f, weight_text, ppi)
        wt_h = wt_bot - wt_top
        weight_y = label_y + label_h * 0.72 - wt_h / 2
        self._draw_text_top_left(pdf, text_start_x, weight_y, weight_text,
                                  'Arial', 'B', font_pt, pil_f, ppi)

        # box size at 90% height
        _, bt_top, _, bt_bot = self._pil_bbox_mm(pil_f, box_text, ppi)
        bt_h = bt_bot - bt_top
        boxsize_y = label_y + label_h * 0.90 - bt_h / 2
        self._draw_text_top_left(pdf, text_start_x, boxsize_y, box_text,
                                  'Arial', 'B', font_pt, pil_f, ppi)

        # ── Barcodes (right-bottom area of label) ────────────────────────────
        barcode_h_mm = label_h * 0.18
        barcode_sku_w_mm = label_w * 0.26
        barcode_sn_w_mm = label_w * 0.20

        barcode_h_px = max(int(barcode_h_mm * px_per_mm), 10)
        barcode_sku_w_px = max(int(barcode_sku_w_mm * px_per_mm), 10)
        barcode_sn_w_px = max(int(barcode_sn_w_mm * px_per_mm), 10)

        sku_name = sku_config.sku_name
        sn_code = sku_config.side_text.get('sn_code', '0000000000')

        sku_x = label_x + label_w * 0.51
        sn_x = label_x + label_w * 0.79
        barcode_y = label_y + label_h * 0.635

        try:
            bc_sku = generate_barcode_image(sku_name, barcode_sku_w_px, barcode_h_px)
            pdf.image(bc_sku, x=sku_x, y=barcode_y,
                      w=barcode_sku_w_mm, h=barcode_h_mm)
        except Exception:
            pass

        try:
            bc_sn = generate_barcode_image(sn_code, barcode_sn_w_px, barcode_h_px)
            pdf.image(bc_sn, x=sn_x, y=barcode_y,
                      w=barcode_sn_w_mm, h=barcode_h_mm)
        except Exception:
            pass

        # ── Barcode text labels (below barcodes) ────────────────────────────
        bc_font_h_mm = label_h * 0.045
        bc_font_px = max(int(bc_font_h_mm * px_per_mm), 4)
        bc_font_pt = bc_font_px * 72.0 / ppi
        pil_bc = ImageFont.truetype(self.font_paths['Arial Regular'], bc_font_px)

        bc_text_y = barcode_y + barcode_h_mm + label_h * 0.01
        self._draw_text_top_center(
            pdf, sku_x + barcode_sku_w_mm / 2, bc_text_y,
            sku_name, 'Arial', '', bc_font_pt, pil_bc, ppi)
        self._draw_text_top_center(
            pdf, sn_x + barcode_sn_w_mm / 2, bc_text_y,
            sn_code, 'Arial', '', bc_font_pt, pil_bc, ppi)

        # ── "MADE IN CHINA" (centered between barcodes, 92% height) ─────────
        mic_font_h_mm = label_h * 0.075
        mic_font_px = max(int(mic_font_h_mm * px_per_mm), 4)
        mic_font_pt = mic_font_px * 72.0 / ppi
        pil_mic = ImageFont.truetype(self.font_paths['Arial Bold'], mic_font_px)

        center_x = (sku_x + sn_x + barcode_sn_w_mm) / 2
        mic_cy = label_y + label_h * 0.92
        self._draw_text_mid_center(
            pdf, center_x, mic_cy,
            "MADE IN CHINA", 'Arial', 'B', mic_font_pt, pil_mic, ppi)

    
def generate_cloud_color_image(sku_config, font_path, base_size=500, bg_color=None):
    """
    生成一个包含产品颜色（如 "White"）的水平三圆重叠“云朵/胶囊”形状图片。
    不再会被切边！
    """
    if bg_color is None:
        bg_color = (0, 0, 0, 255)  # 默认黑色圆圈

    color_text = sku_config.color if sku_config.color else "White"

    # === 1. 动态数学计算 (绝对防切边魔法) ===
    # 我们把 base_size 视为你期望的最终总宽度，反推圆的半径和间距
    # 假设总宽度 W = 左圆半径 + 两个间距 + 右圆半径 = 2*R + 2*offset
    # 如果 offset = 1.3 * R，那么 W = 4.6 * R
    R = int(base_size / 4.6)
    offset = int(R * 1.3)  # 控制间距，1.3 刚好有漂亮的凹槽
    
    # 算出一个极其精准的画布尺寸，一像素都不多，一像素都不被切！
    total_w = 2 * R + 2 * offset
    total_h = 2 * R
    
    # 2. 创建精准大小的透明画布
    img = Image.new('RGBA', (total_w, total_h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 3. 计算三个圆的圆心坐标 (Y轴全部在正中间)
    Cy = R
    C1_x = R                  # 左圆心
    C2_x = R + offset         # 中圆心
    C3_x = R + 2 * offset     # 右圆心
    
    def get_circle_bbox(cx, cy, r):
        return (cx-r, cy-r, cx+r, cy+r)
        
    # 4. 绘制三个实心圆
    draw.ellipse(get_circle_bbox(C1_x, Cy, R), fill=bg_color, outline=None)
    draw.ellipse(get_circle_bbox(C2_x, Cy, R), fill=bg_color, outline=None)
    draw.ellipse(get_circle_bbox(C3_x, Cy, R), fill=bg_color, outline=None)
    
    # 5. 动态计算文字大小
    max_text_w = int(offset * 2 + R * 1.67)
    font_size = int(total_h * 0.55)  # 字号稍微小一点点，给上下留出呼吸感
    font = ImageFont.truetype(font_path, font_size)
    
    while font_size > 10:
        bbox = draw.textbbox((0, 0), color_text, font=font)
        text_w = bbox[2] - bbox[0]
        if text_w <= max_text_w:
            break
        font_size -= 2
        font = ImageFont.truetype(font_path, font_size)
        
    # 6. 绝对居中绘制文字（X轴为画布一半，Y轴为圆心）
    draw.text((total_w // 2, Cy), color_text, fill=sku_config.background_color, font=font, anchor="mm")
    
    # 7. 裁掉可能残留的极其微小的透明边缘
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    return img
