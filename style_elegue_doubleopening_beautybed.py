# -*- coding: utf-8 -*-
"""
德国ELEGUE Barberpub 美容床 对开盖样式 - fpdf2 版
"""
from fpdf import FPDF
from PIL import Image, ImageFont
import pathlib
import fitz  # PyMuPDF
from style_base import BoxMarkStyle, StyleRegistry
import general_functions
from general_functions import generate_barcode_image


@StyleRegistry.register
class ElegueBarberpubDoubleOpeningStyle(BoxMarkStyle):
    """德国ELEGUE Barberpub 美容床 对开盖样式 (fpdf2 版)"""

    def get_style_name(self):
        return "elegue_barberpub_doubleopening_beautybed"

    def get_style_description(self):
        return "德国ELEGUE Barberpub 美容床对开盖箱唛样式"

    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'ppi', 'color', 'product',
                'side_text', 'sku_name', 'box_number', 'img_line_drawing']

    def get_layout_config_mm(self, sku_config):
        """德国ELEGUE Barberpub 美容床 对开盖样式 - 12块布局（4列3行），单位 mm"""
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
        """返回可直接传给 fpdf2 pdf.image() 的对象。
        PDF 文件用 fitz 转换为 SVG（保持矢量），写入临时文件后返回路径；其他格式原样返回路径。
        """
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

    # ── 翻盖面板 ─────────────────────────────────────────────────────────────