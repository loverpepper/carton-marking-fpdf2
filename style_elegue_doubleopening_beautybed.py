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
import layout_engine as engine


@StyleRegistry.register
class ElegueBarberpubDoubleOpeningStyle(BoxMarkStyle):
    """德国ELEGUE Barberpub 美容床 对开盖样式 (fpdf2 版)"""

    def get_style_name(self):
        return "elegue_barberpub_doubleopening_beautybed"

    def get_style_description(self):
        return "德国ELEGUE Barberpub 美容床对开盖箱唛样式"

    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'ppi', 'color', 'product',
            'side_text', 'sku_name', 'box_number']

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
        res_base = self.base_dir / 'assets' / 'ELEGUE' / '对开盖' / '矢量文件'
        self.res_base = res_base
        self.resources = {
            'icon_logo':              res_base / 'logo-ELEGUE.png',
            'icon_attention_info':    res_base / '对开盖开箱注意事项.png',
            'icon_webside':           res_base / '侧唛网址.png',
            'icon_side_label':        res_base / '侧唛标签_窄.png',
            'icon_slogan':            res_base / '正唛宣传语.png',
            # 法律标素材
            'legal_icon_2': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-2-1-GE.png').convert('RGBA')),
            'legal_icon_3_1': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-3-1.png').convert('RGBA')),
            'legal_icon_CE': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-3-2CC.png').convert('RGBA')),
            'legal_icon_UKCA': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-3-2CK.png').convert('RGBA')),
            'legal_icon_RoHs': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-3-2RoHs.png').convert('RGBA')),
            'legal_icon_WEEE': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-3-2回收.png').convert('RGBA')),
            'legal_icon_GreenDot': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-3-2绿点.png').convert('RGBA')),
            'legal_icon_4': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-4.png').convert('RGBA')),

        }

    def _load_fonts(self):
        """加载字体路径"""
        font_base = self.base_dir / 'assets' / 'ELEGUE' / '对开盖' / '箱唛字体'
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

        # # Two side panels
        self._draw_side_panel(pdf, sku_config, x1, y1, w_mm, h_mm)
        self._draw_side_panel(pdf, sku_config, x3, y1, w_mm, h_mm)

        # Left-up flap
        self._draw_flap_left_up(pdf, x0, 0.0, l_mm, half_w_mm)

        # Right-up flap
        self._draw_flap_right_up(pdf, x2, 0.0, l_mm, half_w_mm)

        # Left-down and right-down are blank (already background-filled)

    # ── 内部辅助方法 ────────────────────────────────────────────────────────────

    def _get_font_size(self, text, font_key, target_width_mm, ppi, max_height_mm = None):
        """同 _get_font_size，额外受 max_height_mm 约束"""
        target_px = int(target_width_mm * ppi / 25.4)
        max_h_px = int(max_height_mm * ppi / 25.4) if max_height_mm is not None else None
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
    
    def _draw_flap_left_up(self, pdf, x_mm, y_mm, w_mm, h_mm):
        """左翻盖（上）：顶盖 logo，宽 55%，居中"""
        icon_path = self.resources['icon_logo']
        with Image.open(icon_path) as img:
            orig_w, orig_h = img.size
        img_w_mm = w_mm * 0.55
        img_h_mm = img_w_mm * orig_h / orig_w
        img_x = x_mm + (w_mm - img_w_mm) / 2
        img_y = y_mm + (h_mm - img_h_mm) / 2
        pdf.image(icon_path, x=img_x, y=img_y, w=img_w_mm, h=img_h_mm)

    def _draw_flap_right_up(self, pdf, x_mm, y_mm, w_mm, h_mm):
        """右翻盖（上）：开箱注意事项，宽 86%，居中"""
        icon_path = self.resources['icon_attention_info']
        with Image.open(icon_path) as img:
            orig_w, orig_h = img.size
        img_w_mm = w_mm * 0.86
        img_h_mm = img_w_mm * orig_h / orig_w
        img_x = x_mm + (w_mm - img_w_mm) / 2
        img_y = y_mm + (h_mm - img_h_mm) / 2
        pdf.image(icon_path, x=img_x, y=img_y, w=img_w_mm, h=img_h_mm)
        
    def _draw_side_panel(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm):
        
        """侧面板：SKU + 尺寸重量信息 + 侧唛网址 + 侧唛标签"""

        # 文字来源
        sku_text = sku_config.sku_name
        weight_text = f"{sku_config.side_text['gw_value'] * 0.4536 :.0f} / {sku_config.side_text['nw_value'] * 0.4536 :.0f} kg"
        dimension_text = f"{sku_config.l_cm:.0f}cm x {sku_config.w_cm:.0f}cm x {sku_config.h_cm:.0f}cm"
        
        # SKU文字 Label文字 详细信息文字的大小
        sku_pt, pil_sku = self._get_font_size(
            sku_text, 'CentSchbook', w_mm * 0.9, sku_config.ppi, h_mm * 0.13,)
        
        label_pt, pil_lbl = self._get_font_size(
            "G.W./N.W.", 'CentSchbook', w_mm * 0.103, sku_config.ppi, h_mm * 0.04)

        value_pt, pil_val = self._get_font_size(
            dimension_text, 'CentSchbook', w_mm * 0.203, sku_config.ppi, h_mm * 0.032)
        
        # Label文字 和 详细信息文字 row
        padding_y = 3.1

        def value_baseline_nudge(label_text, value_text):
            _, label_top, _, label_bottom = self._pil_bbox_mm(pil_lbl, label_text, sku_config.ppi)
            _, value_top, _, value_bottom = self._pil_bbox_mm(pil_val, value_text, sku_config.ppi)
            label_total_h = (label_bottom - label_top) + 2 * padding_y
            value_h = value_bottom - value_top
            label_baseline_from_row_bottom = -label_total_h + padding_y - label_top
            value_baseline_from_row_bottom = -value_h - value_top
            return label_baseline_from_row_bottom - value_baseline_from_row_bottom + padding_y * 2 

        weight_row = engine.Row(
            align="bottom",
            justify="start",
            spacing = 20,
            children=[
                engine.Text("G.W./N.W.", font_family="CentSchbook", font_style="", font_size_pt=label_pt, font_path=self.font_paths['CentSchbook'],
                            color = sku_config.background_color,
                            draw_background=True,
                            border_radius=20 * 25.4 / sku_config.ppi, padding_x = 4.7, padding_y = padding_y
                            ),
                engine.Text(weight_text, font_family="CentSchbook", font_style="", font_size_pt=value_pt, font_path=self.font_paths['CentSchbook'],
                            nudge_y=value_baseline_nudge("G.W./N.W.", weight_text)),
            ]
        )

        dimention_row = engine.Row(
            align="bottom",
            justify="start",
            spacing = 20,
            children=[
                engine.Text("BOX SIZE", font_family="CentSchbook", font_style="", font_size_pt=label_pt, font_path=self.font_paths['CentSchbook'],
                            color = sku_config.background_color,
                            draw_background=True,
                            border_radius=20 * 25.4 / sku_config.ppi, padding_x = 4.7, padding_y = padding_y
                            ),
                engine.Text(dimension_text, font_family="CentSchbook", font_style="", font_size_pt=value_pt, font_path=self.font_paths['CentSchbook'],
                            nudge_y=value_baseline_nudge("BOX SIZE", dimension_text)),
            ]
        )
        
        # Label文字 和 详细信息文字 row 与网址组合
        icon_webside = self.resources['icon_webside']
        icon_webside_target_width = w_mm * 0.61
        
        left_col = engine.Column(
            align="center",
            justify="start",
            spacing=25,
            children=[
                engine.Row(
                    align="bottom",
                    justify="start",
                    spacing=10,
                    children=[
                        weight_row,
                        dimention_row,
                    ]
                ),
                engine.Image(icon_webside, width=icon_webside_target_width),
            ]
        )
        
        # 窄侧唛标签（右侧）
        label_h_mm = h_mm * 0.19
        label_w_mm = label_h_mm * 2076 / 1073
        # label_y = bottom_area_top + (bottom_margin_mm - label_h_mm) / 2
        # label_x = x_mm + w_mm / 2 + (w_mm / 2 - label_w_mm) / 2
        # pdf.image(self.resources['icon_side_label_narrow'],
        #           x=label_x, y=label_y, w=label_w_mm, h=label_h_mm)
        lower_row = engine.Row(
            align="center",
            justify="space-between",
            fixed_width=w_mm,
            padding_x = w_mm * 0.04,
            spacing=10,
            children=[
                left_col,
                engine.Image(self.resources['icon_side_label'], width=label_w_mm),
            ]
        )
        
        main_col = engine.Column(
            align="center",
            justify="center",
            fixed_height=h_mm,
            fixed_width=w_mm,
            spacing=25,
            children=[
                engine.Text(sku_text, font_family="CentSchbook", font_style="", font_size_pt=sku_pt, font_path=self.font_paths['CentSchbook'], ppi=sku_config.ppi),
                lower_row,
            ]
        )
        main_col.layout(x_mm, y_mm)
        main_col.render(pdf)

        self._draw_label_overlay(
            pdf, sku_config,
            lower_row.children[1].x, lower_row.children[1].y, label_w_mm, label_h_mm,
            barcode1_text=sku_config.sku_name,
            barcode2_text=sku_config.side_text['sn_code'],
            bc1_xf=0.05,  bc1_yf=0.04, bc1_wf=0.533, bc1_hf=0.28,
            bc2_xf=0.60,  bc2_yf=0.04, bc2_wf=0.36,  bc2_hf=0.28,
            bar_yf=0.88,  bar_hf=0.12,
            origin_yf=0.2 # 产地文字的 y 位置相对于标签高度的比例（窄侧唛需要微调）
        )
    
    
    def _draw_label_overlay(self, pdf, sku_config, label_x, label_y, label_w, label_h,
                             barcode1_text, barcode2_text,
                             bc1_xf, bc1_yf, bc1_wf, bc1_hf,
                             bc2_xf, bc2_yf, bc2_wf, bc2_hf,
                             bar_yf, bar_hf,
                             gw_text=None, gw_xf=None, gw_yf=None, gw_hf=None,
                             box_text=None, box_xf=None, box_yf=None, box_hf=None,
                             origin_yf=0.2):
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
        # 这里不需要画底部黑条，因为标签模板已经包含了黑色底条的设计元素，直接在上面绘制文字即可。
        # pdf.rect(label_x, bar_y, label_w, bar_h, style='F')

        origin_text = sku_config.side_text.get('origin_text', 'MADE IN CHINA')
        font_h_mm = bar_h * 0.8
        font_px = int(font_h_mm * px_per_mm)
        font_pt = font_px * 72.0 / ppi
        if font_px >= 4:
            pil_orig = ImageFont.truetype(self.font_paths['CentSchbook'], font_px)
            origin_y = bar_y + bar_h * origin_yf
            r, g, b = sku_config.background_color
            self._draw_text_top_center(
                pdf, label_x + label_w / 2, origin_y,
                origin_text, 'CentSchbook', '', font_pt, pil_orig, ppi,
                color=(r, g, b))

    def _draw_front_legal_label(self, pdf, sku_config, x_mm, y_mm, box_w_mm, box_h_mm):
        """Draw the GE legal label in a short, wide front-panel layout."""
        ppi = float(sku_config.ppi)
        base_h_mm = 77.0
        scale = box_h_mm / base_h_mm

        left_w = min(box_w_mm * 0.72, box_h_mm * 3.8 * 0.72)
        right_w = box_w_mm - left_w
        row1_h = box_h_mm * 0.72
        row2_h = box_h_mm - row1_h

        lw_thin = max(0.12, 5.0 * 25.4 / ppi * scale)
        lw_thick = max(0.16, 7.0 * 25.4 / ppi * scale)

        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(lw_thick)
        pdf.rect(x_mm, y_mm, box_w_mm, box_h_mm, style='D')

        split_x = x_mm + left_w
        pdf.set_line_width(lw_thin)
        pdf.line(split_x, y_mm, split_x, y_mm + box_h_mm)
        pdf.line(x_mm, y_mm + row1_h, split_x, y_mm + row1_h)

        icon_2 = self.resources['legal_icon_2']
        icon_2_h = row1_h * 0.26
        icon_2_w = icon_2_h * icon_2.width / icon_2.height
        row1_icon_margin = 3.5 * scale
        icon_2_x = split_x - row1_icon_margin - icon_2_w
        icon_2_y = y_mm + (row1_h - icon_2_h) / 2.0
        divider_x = icon_2_x - row1_icon_margin / 2.0
        pdf.line(divider_x, y_mm, divider_x, y_mm + row1_h)
        pdf.image(icon_2, x=icon_2_x, y=icon_2_y, w=icon_2_w, h=icon_2_h)

        if getattr(sku_config, 'legal_data', None):
            text_x = x_mm + 3.5 * scale
            text_y = y_mm + 1.0 * scale
            text_w = max(1.0, divider_x - text_x - 2.0 * scale)
            self._draw_front_legal_text(
                pdf, sku_config, text_x, text_y, text_w, row1_h, scale)

        row2_icons = []
        icon_3_1 = self.resources['legal_icon_3_1']
        icon_3_1_h = row2_h * 0.85
        icon_3_1_w = icon_3_1_h * icon_3_1.width / icon_3_1.height
        row2_icons.append((icon_3_1, icon_3_1_w, icon_3_1_h))

        for is_on, key in [
            (getattr(sku_config, 'legal_CE', 0), 'legal_icon_CE'),
            (getattr(sku_config, 'legal_UKCA', 0), 'legal_icon_UKCA'),
            (getattr(sku_config, 'legal_RoHs', 0), 'legal_icon_RoHs'),
            (getattr(sku_config, 'legal_WEEE', 0), 'legal_icon_WEEE'),
            (getattr(sku_config, 'legal_GreenDot', 0), 'legal_icon_GreenDot'),
        ]:
            if is_on == 1:
                img = self.resources[key]
                ih = row2_h * 0.4
                iw = ih * img.width / img.height
                row2_icons.append((img, iw, ih))

        icon_gap = 5.0 * scale
        total_icons_w = sum(iw for _, iw, _ in row2_icons)
        total_icons_w += icon_gap * max(0, len(row2_icons) - 1)
        cur_x = x_mm + (left_w - total_icons_w) / 2.0
        row2_y = y_mm + row1_h
        for img, iw, ih in row2_icons:
            pdf.image(img, x=cur_x, y=row2_y + (row2_h - ih) / 2.0, w=iw, h=ih)
            cur_x += iw + icon_gap

        icon_4 = self.resources['legal_icon_4']
        icon_4_h = box_h_mm * 0.82
        icon_4_w = icon_4_h * icon_4.width / icon_4.height
        max_icon_4_w = right_w * 0.86
        if icon_4_w > max_icon_4_w:
            icon_4_w = max_icon_4_w
            icon_4_h = icon_4_w * icon_4.height / icon_4.width
        pdf.image(
            icon_4,
            x=split_x + (right_w - icon_4_w) / 2.0,
            y=y_mm + (box_h_mm - icon_4_h) / 2.0,
            w=icon_4_w,
            h=icon_4_h,
        )

    def _draw_front_legal_text(self, pdf, sku_config, x_mm, y_mm,
                               area_w_mm, area_h_mm, scale=1.0):
        """Render legal text compactly inside the front-panel legal label."""
        ppi = float(sku_config.ppi)
        px_per_mm = ppi / 25.4
        regular_font = self.font_paths['CentSchbook']
        bold_font = self.font_paths['CalibriB']
        base_px = max(4, int(round(28 * scale)))
        min_px = max(3, int(round(7 * scale)))
        step_px = max(1, int(round(1 * scale)))
        line_ratio = 1.45

        def build_lines(size_px):
            pil_r = ImageFont.truetype(regular_font, size_px)
            pil_b = ImageFont.truetype(bold_font, size_px)
            avail_w = max(1.0, area_w_mm - 2.0 * scale)

            def width_mm(text, font):
                return font.getlength(str(text)) / px_per_mm

            def wrap_text(text, first_limit, next_limit):
                words = str(text).split()
                if not words:
                    return ['']
                lines = []
                current = ''
                limit = max(1.0, first_limit)
                for word in words:
                    candidate = word if not current else f'{current} {word}'
                    if width_mm(candidate, pil_r) <= limit:
                        current = candidate
                        continue
                    if current:
                        lines.append(current)
                        current = ''
                        limit = max(1.0, next_limit)
                    if width_mm(word, pil_r) <= limit:
                        current = word
                    else:
                        chunk = ''
                        for ch in word:
                            candidate = chunk + ch
                            if chunk and width_mm(candidate, pil_r) > limit:
                                lines.append(chunk)
                                chunk = ch
                                limit = max(1.0, next_limit)
                            else:
                                chunk = candidate
                        current = chunk
                if current:
                    lines.append(current)
                return lines

            lines = []
            for label, value in sku_config.legal_data.items():
                label_text = f'{label}: '
                label_w = width_mm(label_text, pil_b)
                wrapped = wrap_text(value, avail_w - label_w, avail_w)
                for idx, line in enumerate(wrapped):
                    lines.append({
                        'label': label_text if idx == 0 else '',
                        'text': line,
                        'label_w': label_w if idx == 0 else 0.0,
                    })
            return lines, pil_r, pil_b

        size_px = base_px
        while size_px > min_px:
            lines, _, _ = build_lines(size_px)
            line_h = size_px * line_ratio / px_per_mm
            if len(lines) * line_h <= area_h_mm - 2.0 * scale:
                break
            size_px -= step_px

        lines, pil_r, pil_b = build_lines(size_px)
        line_h = size_px * line_ratio / px_per_mm
        size_pt = size_px * 72.0 / ppi
        total_h = len(lines) * line_h
        cur_y = y_mm + (area_h_mm - total_h) / 2.0
        cur_x = x_mm + 1.0 * scale

        for line in lines:
            if line['label']:
                self._draw_text_top_left(
                    pdf, cur_x, cur_y, line['label'],
                    'CalibriB', '', size_pt, pil_b, ppi)
                self._draw_text_top_left(
                    pdf, cur_x + line['label_w'], cur_y, line['text'],
                    'CentSchbook', '', size_pt, pil_r, ppi)
            else:
                self._draw_text_top_left(
                    pdf, cur_x, cur_y, line['text'],
                    'CentSchbook', '', size_pt, pil_r, ppi)
            cur_y += line_h

    def _draw_front_panel(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm):
        """正面板：仅 SKU，居中"""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4
        margin_top = 25.0
        margin_left = 30.0
        margin_right = 27.0

        # 顶层row, 包含logo和 【NewAcme GmbH】文字
        # 1. Logo（左上角）
        icon_logo = self.resources['icon_logo']
        logo_w_mm = w_mm * 0.19

        # 2. 公司信息（右上角）
        company_text = "NewAcme GmbH"
        company_pt, pil_company = self._get_font_size(
            company_text, 'CentSchbook', w_mm * 0.17, ppi, h_mm * 0.1)
        
        upper_row = engine.Row(
            align="top",
            justify="space-between",
            fixed_width=w_mm,
            padding_x=margin_left,
            padding_y=margin_top,
            children=[
                engine.Image(icon_logo, width=logo_w_mm),
                engine.Text(company_text, font_family="CentSchbook", font_style="", font_size_pt=company_pt, font_path=self.font_paths['CentSchbook'], ppi=ppi),
            ]
        )
        upper_row.layout(x_mm, y_mm)
        upper_row.render(pdf)
        
        # 底部SKU + 颜色文字 + 箱号文字
        # 3. 底部斜纹条纹
        stripe_height_mm = 15.0
        bottom_margin_mm = 6.0
        stripe_y = y_mm + h_mm - stripe_height_mm - bottom_margin_mm
        stripe_width_mm = 30.0  # 条纹宽度
        self._draw_diagonal_stripes_pdf(pdf, x_mm, stripe_y, w_mm, stripe_height_mm, stripe_width_mm)

        margin_bottom = 32.0
        bottom_text_y = y_mm + h_mm - margin_bottom - 5.0

        # 4. SKU文字 + 颜色文字（左下角）
        sku_text = sku_config.sku_name
        sku_pt, _ = self._get_font_size(
            sku_text, 'CentSchbook', w_mm * 0.505, ppi, h_mm * 0.16)
        sku_el = engine.Text(
            sku_text,
            font_family="CentSchbook",
            font_style="",
            font_size_pt=sku_pt,
            font_path=self.font_paths['CentSchbook'],
            ppi=ppi,
        )

        color_text = sku_config.color.upper()
        color_pt, _ = self._get_font_size(
            color_text, 'CentSchbook', w_mm * 0.13, ppi, h_mm * 0.11)
        color_el = engine.Text(
            color_text,
            font_family="CentSchbook",
            font_style="",
            font_size_pt=color_pt,
            font_path=self.font_paths['CentSchbook'],
            ppi=ppi,
        )

        bottom_left_row = engine.Row(
            align="bottom",
            justify="start",
            spacing=3.0,
            children=[
                sku_el,
                color_el,
            ],
        )
        
        # 5. 箱号文字（右下角）
        box_text = (f"BOX {sku_config.box_number['current_box']} "
                    f"OF {sku_config.box_number['total_boxes']}")
        box_pt, _ = self._get_font_size(
            box_text, 'CentSchbook', w_mm * 0.127, ppi, h_mm * 0.038)
        pad_x = 5.0
        pad_y = 0.7 * 1.2 * 10
        radius_mm = 20 * 25.4 / ppi
        r, g, b = sku_config.background_color
        box_el = engine.Text(
            box_text,
            font_family="CentSchbook",
            font_style="",
            font_size_pt=box_pt,
            font_path=self.font_paths['CentSchbook'],
            ppi=ppi,
            color=(r, g, b),
            draw_background=True,
            background_color=(0, 0, 0),
            border_radius=radius_mm,
            padding_x=pad_x,
            padding_y=pad_y,
            nudge_y = - pad_y * 2
        )
        
        # 底部整体组成一个row
        main_row = engine.Row(
            align="bottom",
            justify="space-between",
            fixed_width=w_mm - margin_left - margin_right + 6.0,
            children=[
                bottom_left_row,
                box_el,
            ],
        )
        main_row.layout(
            x_mm + margin_left - 6.0,
            bottom_text_y - main_row.height,
        )
        main_row.render(pdf)
        
        # 7. 绘制产品名称
        product_text = sku_config.product
        prod_pt, _ = self._get_font_size(
            product_text, 'DroidSans', w_mm * 0.52, ppi, h_mm * 0.28)
        
        # 6.  标语图片（产品名称下方，居中）
        icon_slogan = self.resources['icon_slogan']
        slogan_w_mm = w_mm * 0.27
        
        middle_col = engine.Column(
            align="center",
            justify="center",
            fixed_height= h_mm,
            fixed_width=w_mm,
            spacing= 13,
            children=[
                engine.Text(product_text, font_family="DroidSans", font_style="", font_size_pt=prod_pt, font_path=self.font_paths['DroidSans'], ppi=ppi),
                engine.Image(icon_slogan, width=slogan_w_mm),
            ],
            nudge_y = - h_mm * 0.13
        )
        
        middle_col.layout(x_mm, y_mm)
        middle_col.render(pdf)

        
        if getattr(sku_config, 'legal_data', None):
            legal_h_mm = min(h_mm * 0.18, 82.0)
            legal_w_mm = min(w_mm * 0.62, legal_h_mm * 4.5)
            legal_x = x_mm + (w_mm - legal_w_mm) / 2.0
            legal_bottom_limit = bottom_text_y - 18.0
            legal_y = min(y_mm + h_mm * 0.51, legal_bottom_limit - legal_h_mm)
            legal_y = max(y_mm + margin_top + 45.0, legal_y - 12.0)
            self._draw_front_legal_label(
                pdf, sku_config, legal_x, legal_y, legal_w_mm, legal_h_mm)

        return
