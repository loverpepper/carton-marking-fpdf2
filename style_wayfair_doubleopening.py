# -*- coding: utf-8 -*-
"""
Wayfair 对开盖样式 - fpdf2 版
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
class WayfairDoubleOpeningStyle(BoxMarkStyle):
    """Wayfair 对开盖样式 (fpdf2 版)"""

    def get_style_name(self):
        return "wayfair_doubleopening"

    def get_style_description(self):
        return "Wayfair 对开盖样式"

    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'ppi', 'color', 'product',
            'side_text', 'sku_name', 'box_number']

    def get_layout_config_mm(self, sku_config):
        """Wayfair 对开盖样式 - 12块布局（4列3行），单位 mm"""
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
        res_base = self.base_dir / 'assets' / 'Wayfair' / '对开盖' / '矢量文件'
        self.res_base = res_base
        self.resources = {
            'icon_attention':         res_base / 'icon-attention.png',
            'icon_box-2-1':           res_base / 'BOX-2-1.png',
            'icon_box-2-2':           res_base / 'BOX-2-2.png',
            'icon_side_label':        res_base / '条码框.png',
        }

    def _load_fonts(self):
        """加载字体路径"""
        font_base = self.base_dir / 'assets' / 'Wayfair' / '对开盖' / '箱唛字体'
        self.font_paths = {
            'Calibri-Bold':      str(font_base / 'calibri-bold.ttf'),
            'AvantGardeLT-Demi': str(font_base / 'avantgardelt-demi.ttf'),
            'Calibri':           str(font_base / 'calibri.ttf'),
        }

    # ── fpdf2 字体注册 ──────────────────────────────────────────────────────────

    def register_fonts(self, pdf: FPDF):
        """向 FPDF 对象注册本样式使用的所有字体"""
        # Calibri-Bold / AvantGardeLT-Demi 是 Illustrator 可识别的 PostScript 名
        pdf.add_font('Calibri-Bold',      '', self.font_paths['Calibri-Bold'])
        pdf.add_font('AvantGardeLT-Demi', '', self.font_paths['AvantGardeLT-Demi'])
        pdf.add_font('Calibri',           '', self.font_paths['Calibri'])

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

    # ── 翻盖面板 ─────────────────────────────────────────────────────────────
    
    def _draw_flap_left_up(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm):
        """左翻盖（上）：顶盖 logo，宽 55%，居中"""
        icon_attention_path = self.resources['icon_attention']
        icon_attention_target_w_mm = w_mm * 0.25
        
        icon_box_number_path = self.resources[f'icon_box-{sku_config.box_number["total_boxes"]}-{sku_config.box_number["current_box"]}']
        icon_box_number_target_w_mm = w_mm * 0.23
        
        spacing_mm = w_mm * 0.07
        
        main_row = engine.Row(
            align="center",
            justify="center",
            spacing=spacing_mm,
            fixed_width=w_mm,
            fixed_height=h_mm,
            children=[
                engine.Image(icon_attention_path, width=icon_attention_target_w_mm),
                engine.Image(icon_box_number_path, width=icon_box_number_target_w_mm),
            ],
            nudge_y =  h_mm * 0.15
        )
        
        main_row.layout(x_mm, y_mm)
        main_row.render(pdf)
        
    def _draw_side_panel(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm):
        
        """侧面板：SKU + 尺寸重量信息 + 侧唛网址 + 侧唛标签"""
        
        # Model 文字 + SKU 文字 + 箱号图标
        model_pt, pil_model = self._get_font_size(
            "Model:", 'Calibri-Bold', w_mm * 0.16, sku_config.ppi, h_mm * 0.13,)
        
        sku_text = sku_config.sku_name
        sku_pt, pil_sku = self._get_font_size(
            sku_text, 'Calibri-Bold', w_mm * 0.705, sku_config.ppi, h_mm * 0.08)

        # 箱号图片
        icon_box_number_path = self.resources[f'icon_box-{sku_config.box_number["total_boxes"]}-{sku_config.box_number["current_box"]}']
        icon_box_number_target_w_mm = w_mm * 0.283
        
        # 侧唛标签尺寸（按图片实际比例计算，放在侧面板底部）
        label_img_pil = Image.open(str(self.resources['icon_side_label']))
        aspect_ratio = label_img_pil.width / label_img_pil.height
        label_w_mm = w_mm * 0.80
        label_h_mm = label_w_mm / aspect_ratio
        label_x = x_mm + (w_mm - label_w_mm) / 2
        label_y = y_mm + h_mm * 0.71

        main_col = engine.Column(
            align="center",
            justify="center",
            spacing= h_mm * 0.05,
            fixed_width=w_mm, 
            fixed_height=h_mm - label_h_mm,
            children=[
                engine.Text("Model:", font_family="Calibri-Bold", font_style="", font_size_pt=model_pt, font_path=self.font_paths['Calibri-Bold'], ppi=sku_config.ppi,
                            nudge_y = - h_mm * 0.02
                            ),
                engine.Text(sku_text, font_family="Calibri-Bold", font_style="", font_size_pt=sku_pt, font_path=self.font_paths['Calibri-Bold'], ppi=sku_config.ppi),
                engine.Image(icon_box_number_path, width=icon_box_number_target_w_mm),
            ],
        )
        
        main_col.layout(x_mm, y_mm)
        main_col.render(pdf)

        # 侧唛标签底图
        pdf.image(str(self.resources['icon_side_label']), x=label_x, y=label_y, w=label_w_mm, h=label_h_mm)

        # 叠加条形码
        self._draw_label_overlay(
            pdf, sku_config, label_x, label_y, label_w_mm, label_h_mm
        )
    

    def _draw_front_panel(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm):
        """正面板：仅 SKU，居中"""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4
        margin_top = 50.0
        margin_left = 50.0
        margin_right = 50.0

        # 顶层row, 包含箱号和 颜色文字
        # 1. 箱号（左上角）
        icon_box_number_path = self.resources[f'icon_box-{sku_config.box_number["total_boxes"]}-{sku_config.box_number["current_box"]}']
        logo_box_number_w_mm = w_mm * 0.23

        # 2. 颜色文字（右上角）
        pad_x = 6.0
        pad_y = 4.4
        
        color_text = sku_config.color.title()
        color_pt, _ = self._get_font_size(
            color_text, 'Calibri', w_mm * 0.05, ppi, h_mm * 0.11)
        color_el = engine.Text(
            color_text,
            font_family="Calibri",
            font_style="",
            font_size_pt=color_pt,
            font_path=self.font_paths['Calibri'],
            ppi=ppi,
            color=sku_config.background_color,
            draw_background=True,
            background_color=(0, 0, 0),
            padding_x = pad_x, padding_y=pad_y,
            border_radius= 20 * 25.4 / ppi,
            nudge_y = - 1 * pad_y
        )
        
        upper_row = engine.Row(
            align="top",
            justify="space-between",
            fixed_width=w_mm,
            padding_x=margin_left,
            padding_y=margin_top,
            children=[
                engine.Image(icon_box_number_path, width=logo_box_number_w_mm),
                color_el,
            ]
        )
        upper_row.layout(x_mm, y_mm)
        upper_row.render(pdf)
        
        # Product + SKU
        # 3. 产品名称（正中，较大）
        product_text = sku_config.product
        prod_pt, _ = self._get_font_size(
            product_text, 'AvantGardeLT-Demi', w_mm * 0.79, ppi, h_mm * 0.28)
        
        # 4. SKU文字 (产品名称下方，较小)
        sku_text = sku_config.sku_name
        sku_pt, _ = self._get_font_size(
            sku_text, 'Calibri-Bold', w_mm * 0.45, ppi, h_mm * 0.16)
        sku_el = engine.Text(
            sku_text,
            font_family="Calibri-Bold",
            font_style="",
            font_size_pt=sku_pt,
            font_path=self.font_paths['Calibri-Bold'],
            ppi=ppi,
        )

        middle_col = engine.Column(
            align="center",
            justify="center",
            fixed_height= h_mm,
            fixed_width=w_mm,
            spacing= h_mm * 0.07,
            children=[
                engine.Text(product_text, font_family="AvantGardeLT-Demi", font_style="", font_size_pt=prod_pt, font_path=self.font_paths['AvantGardeLT-Demi'], ppi=ppi),
                engine.Text(sku_text, font_family="Calibri-Bold", font_style="", font_size_pt=sku_pt, font_path=self.font_paths['Calibri-Bold'], ppi=ppi,)
            ],
            nudge_y = - h_mm * 0.05
        )
        
        middle_col.layout(x_mm, y_mm)
        middle_col.render(pdf)

        # 正面标签底图 + 条形码叠加（底部全宽）
        label_img_pil = Image.open(str(self.resources['icon_side_label']))
        aspect_ratio = label_img_pil.width / label_img_pil.height
        label_w_mm = w_mm * 0.70
        label_h_mm = label_w_mm / aspect_ratio
        label_x = x_mm + (w_mm - label_w_mm) / 2
        label_y = y_mm + h_mm * 0.71

        pdf.image(str(self.resources['icon_side_label']), x=label_x, y=label_y, w=label_w_mm, h=label_h_mm)

        self._draw_label_overlay(
            pdf, sku_config, label_x, label_y, label_w_mm, label_h_mm
        )
       
    def _draw_label_overlay(self, pdf, sku_config, label_x, label_y, label_w, label_h):
        """在标签模板上叠加绘制动态内容"""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        def fmm(xf, yf):
            return label_x + xf * label_w, label_y + yf * label_h

        # G.W./N.W. 文字
        def fmt_num(value):
            try:
                return f"{float(value):.1f}".rstrip("0").rstrip(".")
            except (TypeError, ValueError):
                return str(value)

        gw = fmt_num(sku_config.side_text.get("gw_value", ""))
        nw = fmt_num(sku_config.side_text.get("nw_value", ""))
        gw_text = f"G.W./N.W. : {gw} / {nw} lbs"
        box_text = (
            f"BOX SIZE : {fmt_num(sku_config.l_in)}\" x "
            f"{fmt_num(sku_config.w_in)}\" x "
            f"{fmt_num(sku_config.h_in)}\""
        )

        tx, ty = fmm(0.110, 0.130)
        max_w = label_x + label_w * 0.455 - tx
        font_pt, pil_f = self._get_font_size(
            gw_text, 'Calibri-Bold', max_w, ppi, label_h * 0.28)
        self._draw_text_top_left(pdf, tx, ty, gw_text, 'Calibri-Bold', '', font_pt, pil_f, ppi)

        # BOX SIZE 文字
        tx, ty = fmm(0.110, 0.620)
        max_w = label_x + label_w * 0.455 - tx
        font_pt, pil_f = self._get_font_size(
            box_text, 'Calibri-Bold', max_w, ppi, label_h * 0.26)
        self._draw_text_top_left(pdf, tx, ty, box_text, 'Calibri-Bold', '', font_pt, pil_f, ppi)

        # 条形码
        for bc_text, xf, yf, wf, hf in [
            (sku_config.sku_name, 0.500, 0.16, 0.300, 0.58),
            (sku_config.side_text["sn_code"], 0.800, 0.16, 0.190, 0.58),
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
                font_pt_bc, pil_bc = self._get_font_size(
                    bc_text, 'Calibri', bc_w_mm * 0.95, ppi, label_h * 0.115)
                font_px_bc = int(label_h * 0.115 * px_per_mm)
                if font_px_bc >= 4:
                    self._draw_text_top_center(
                        pdf, bx + bc_w_mm / 2, by + bc_h_mm + 1.0,
                        bc_text, 'Calibri', '', font_pt_bc, pil_bc, ppi)
            except Exception:
                pass

