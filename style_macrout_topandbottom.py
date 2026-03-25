# -*- coding: utf-8 -*-
"""
Macrout 天地盖样式 - fpdf2 版
"""
from fpdf import FPDF
from PIL import Image, ImageFont
from io import BytesIO
from style_base import BoxMarkStyle, StyleRegistry
import general_functions
from general_functions import generate_barcode_image
import layout_engine as engine


@StyleRegistry.register
class MacroutTopAndBottomStyle(BoxMarkStyle):
    """Macrout 天地盖样式 (fpdf2 版)"""

    def get_style_name(self):
        return "macrout_topandbottom"

    def get_style_description(self):
        return "Macrout 天地盖箱唛样式"

    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'ppi', 'color', 'product', 'side_text', 'sku_name']

    def get_preview_images(self):
        """
        从 assets/Macrout/天地盖/实例生成图/ 读取所有图片文件，
        返回 [(文件名, PIL.Image), ...] 列表，按文件名排序。
        若文件夹为空或不存在则返回空列表。
        """
        preview_dir = self.base_dir / 'assets' / 'Macrout' / '天地盖' / '实例生成图'
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

    # ── 布局配置（mm） ──────────────────────────────────────────────────────────

    def get_layout_config_mm(self, sku_config):
        """返回 5 块布局区域，单位 mm（cm × 10）"""
        h_mm = sku_config.h_cm * 10
        l_mm = sku_config.l_cm * 10
        w_mm = sku_config.w_cm * 10
        x0, x1, x2 = 0.0, h_mm, h_mm + l_mm
        y0, y1, y2 = 0.0, h_mm, h_mm + w_mm
        return {
            # 第一行
            "back_side_panel":  (x1, y0, l_mm, h_mm),
            # 第二行
            "left_side_panel":  (x0, y1, h_mm, w_mm),
            "top_panel":        (x1, y1, l_mm, w_mm),
            "right_side_panel": (x2, y1, h_mm, w_mm),
            # 第三行
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
        """加载 Macrout 天地盖样式的图片资源（PIL Image）"""
        res_base = self.base_dir / 'assets' / 'Macrout' / '天地盖' / '矢量文件'
        self.resources = {
            'icon_logo':          Image.open(res_base / 'Macrout.png').convert('RGBA'),
            'icon_notice':        Image.open(res_base / '箱子提示语.png').convert('RGBA'),
            'icon_web':           Image.open(res_base / '公司信息.png').convert('RGBA'),
            'icon_attention':     Image.open(res_base / '标签.png').convert('RGBA'),
            'icon_label':         Image.open(res_base / '箱子信息.png').convert('RGBA'),
            'icon_paste_barcode': Image.open(res_base / '条形码定界框.png').convert('RGBA'),
        }

    def _load_fonts(self):
        """加载字体文件路径"""
        font_base = self.base_dir / 'assets' / 'Macrout' / '天地盖' / '箱唛字体'
        self.font_paths = {
            'Calibri':                              str(font_base / 'calibri.ttf'),
            'ITC Avant Garde Gothic Demi Cyrillic': str(font_base / 'itc-avant-garde-gothic-demi-cyrillic.otf'),
            'Arial Rounded MT Bold':                str(font_base / 'ARLRDBD.ttf'),
            'Arial':                                str(font_base / 'arial.ttf'),
            'Arial Bold':                           str(font_base / 'arialbd.ttf'),
        }

    # ── fpdf2 字体注册 ──────────────────────────────────────────────────────────

    def register_fonts(self, pdf: FPDF):
        """向 FPDF 对象注册本样式使用的所有字体"""
        pdf.add_font('ITCAvantGarde', '',  self.font_paths['ITC Avant Garde Gothic Demi Cyrillic'])
        pdf.add_font('ArialRounded',  '',  self.font_paths['Arial Rounded MT Bold'])
        pdf.add_font('Arial',         '',  self.font_paths['Arial'])
        pdf.add_font('Arial',         'B', self.font_paths['Arial Bold'])

    # ── 核心绘制入口 ────────────────────────────────────────────────────────────

    def draw_to_pdf(self, pdf: FPDF, sku_config):
        """将所有面板直接绘制到已添加页面的 FPDF 对象上"""
        layout = self.get_layout_config_mm(sku_config)

        # 填充各面板背景色
        r, g, b = sku_config.background_color
        pdf.set_fill_color(r, g, b)
        for _, (x, y, w, h) in layout.items():
            pdf.rect(x, y, w, h, style='F')

        # 绘制各面板内容
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

    def _get_font_size(self, text, font_key, target_width_mm, ppi):
        """
        根据目标宽度（mm）计算字号。

        返回:
            (font_size_pt, pil_font)
            font_size_pt : 传给 fpdf2 set_font() 的磅值
            pil_font     : 同比例 PIL 字体，用于 layout_engine 精确尺寸测量
        """
        # 将 mm 目标宽度换算为图像像素（ppi 分辨率下）
        target_px = int(target_width_mm * ppi / 25.4)
        # get_max_font_size 以像素为单位搜索最大字号
        size_px = general_functions.get_max_font_size(text, self.font_paths[font_key], target_px)
        # 像素字号 → PDF 磅值：1px = 72/ppi pt
        size_pt = size_px * 72.0 / ppi
        pil_font = ImageFont.truetype(self.font_paths[font_key], size_px)
        return size_pt, pil_font

    @staticmethod
    def _pil_bbox_mm(pil_font, text, ppi):
        """返回 PIL getbbox 结果换算为 mm 的四元组 (left, top, right, bottom)
        使用 anchor='ls'：top 为负值（基线以上），bottom 为正值（基线以下），
        与 _draw_text_lm / _draw_text_mt 的数学公式保持一致。"""
        left, top, right, bottom = pil_font.getbbox(text, anchor='ls')
        px_per_mm = ppi / 25.4
        return left / px_per_mm, top / px_per_mm, right / px_per_mm, bottom / px_per_mm

    def _draw_text_lm(self, pdf, x_mm, y_center_mm, text,
                      font_family, font_style, font_size_pt, pil_font, ppi):
        """以左-中锚点绘制文字（等价于 PIL anchor='lm'）"""
        _, top_mm, _, bottom_mm = self._pil_bbox_mm(pil_font, text, ppi)
        # baseline = vertical center of bbox adjusted for font top offset
        # simplified: y_center - (top + bottom) / 2
        baseline_y = y_center_mm - (top_mm + bottom_mm) / 2.0
        pdf.set_font(font_family, font_style, font_size_pt)
        pdf.set_text_color(0, 0, 0)
        pdf.text(x_mm, baseline_y, text)

    def _draw_text_mt(self, pdf, x_center_mm, y_top_mm, text,
                      font_family, font_style, font_size_pt, pil_font, ppi):
        """以顶-中锚点绘制文字（等价于 PIL anchor='mt'）"""
        left_mm, top_mm, right_mm, _ = self._pil_bbox_mm(pil_font, text, ppi)
        width_mm   = right_mm - left_mm
        ascent_mm  = -top_mm
        x_mm       = x_center_mm - width_mm / 2.0
        baseline_y = y_top_mm + ascent_mm
        pdf.set_font(font_family, font_style, font_size_pt)
        pdf.set_text_color(0, 0, 0)
        pdf.text(x_mm, baseline_y, text)

    @staticmethod
    def _img_to_buf(pil_img):
        """将 PIL Image 转为 PNG BytesIO，供 pdf.image() 使用"""
        buf = BytesIO()
        if pil_img.mode not in ('RGB', 'RGBA'):
            pil_img = pil_img.convert('RGBA')
        pil_img.save(buf, format='PNG')
        buf.seek(0)
        return buf

    @staticmethod
    def _barcode_to_buf(barcode_img):
        """
        将条形码图片（透明背景）合并到白底后转为 PNG BytesIO。
        使用 alpha 通道作为 mask 进行正确的 alpha 合成，
        确保透明区域渲染为白色，条形码黑色部分保持不变。
        """
        bg = Image.new('RGB', barcode_img.size, (255, 255, 255))
        if barcode_img.mode == 'RGBA':
            bg.paste(barcode_img, mask=barcode_img.split()[3])
        else:
            bg.paste(barcode_img.convert('RGB'))
        buf = BytesIO()
        bg.save(buf, format='PNG')
        buf.seek(0)
        return buf

    # ── 面板绘制方法 ────────────────────────────────────────────────────────────

    def _draw_top_panel(self, pdf: FPDF, sku_config, x_mm, y_mm, w_mm, h_mm):
        """绘制顶面（Top Panel）"""
        ppi = sku_config.ppi

        # 顶部行：Logo（左）+ 等宽空白（右）
        icon_logo_w_mm = w_mm * 0.13
        top_row = engine.Row(
            justify='space-between',
            fixed_width=w_mm,
            padding=w_mm * 0.023,
            children=[
                engine.Image(self.resources['icon_logo'], width=icon_logo_w_mm),
                engine.Spacer(width=icon_logo_w_mm),
            ]
        )

        # 中间列：产品名 / SKU / 提示图 + 颜色
        product_text = sku_config.product
        sku_text     = sku_config.sku_name
        color_text   = sku_config.color

        product_pt, pil_product = self._get_font_size(
            product_text, 'ITC Avant Garde Gothic Demi Cyrillic', w_mm * 0.36, ppi)
        sku_pt, pil_sku = self._get_font_size(
            sku_text, 'Arial Rounded MT Bold', w_mm * 0.43, ppi)
        color_pt, pil_color = self._get_font_size(
            color_text, 'Arial', w_mm * 0.09, ppi)

        middle_col = engine.Column(
            align='center', justify='start',
            spacing=h_mm * 0.062,
            children=[
                engine.Text(product_text, 'ITCAvantGarde', '', product_pt,
                            pil_font=pil_product, ppi=ppi, nudge_y=h_mm * 0.02),
                engine.Text(sku_text, 'ArialRounded', '', sku_pt,
                            pil_font=pil_sku, ppi=ppi),
                engine.Row(
                    justify='start', align='center',
                    spacing=w_mm * 0.04,
                    children=[
                        engine.Image(self.resources['icon_notice'], width=w_mm * 0.21),
                        engine.Text(color_text, 'Arial', '', color_pt,
                                    pil_font=pil_color, ppi=ppi),
                    ]
                ),
            ]
        )

        # 底部行：网址图（左）+ 注意事项图（右）
        bottom_row = engine.Row(
            align='bottom', justify='space-between',
            fixed_width=w_mm,
            padding=w_mm * 0.023,
            children=[
                engine.Image(self.resources['icon_web'],       width=w_mm * 0.28),
                engine.Image(self.resources['icon_attention'], width=w_mm * 0.14),
            ]
        )

        # 整体布局
        main_col = engine.Column(
            align='center', justify='space-between',
            fixed_width=w_mm, fixed_height=h_mm,
            children=[top_row, middle_col, bottom_row]
        )
        main_col.layout(x_mm, y_mm)
        main_col.render(pdf)

    def _draw_front_back_panel(self, pdf: FPDF, sku_config,
                                x_mm, y_mm, w_mm, h_mm, rotate_180=False):
        """
        绘制前/后侧面板。
        back 面（rotate_180=True）通过 pdf.rotation(180) 上下翻转。
        """
        ppi = sku_config.ppi

        sku_text = sku_config.sku_name
        sku_pt, pil_sku = self._get_font_size(
            sku_text, 'Arial Rounded MT Bold', w_mm * 0.41, ppi)

        icon_label = self.resources['icon_label']
        label_w_mm = w_mm * 0.4
        label_h_mm = label_w_mm * icon_label.height / icon_label.width

        main_row = engine.Row(
            align='center', justify='space-between',
            fixed_width=w_mm,
            padding=w_mm * 0.05,
            children=[
                engine.Text(sku_text, 'ArialRounded', '', sku_pt,
                            pil_font=pil_sku, ppi=ppi),
                engine.Image(icon_label, width=label_w_mm, height=label_h_mm),
            ]
        )

        row_y = y_mm + (h_mm - main_row.height) / 2.0
        main_row.layout(x_mm, row_y)

        # 标签图在布局中的精确位置（layout 完成后才有效）
        lbl_x = main_row.children[1].x
        lbl_y = main_row.children[1].y

        def _render():
            main_row.render(pdf)
            self._draw_label(pdf, sku_config, lbl_x, lbl_y, label_w_mm, label_h_mm)

        if rotate_180:
            cx = x_mm + w_mm / 2.0
            cy = y_mm + h_mm / 2.0
            with pdf.rotation(180, cx, cy):
                _render()
        else:
            _render()

    def _draw_side_panel(self, pdf: FPDF, sku_config,
                          x_mm, y_mm, w_mm, h_mm, rotation_deg):
        """
        绘制左/右侧面板。

        页面上面板尺寸：w_mm = h_cm×10，h_mm = w_cm×10
        自然绘制画布（旋转前）：nat_w = w_cm×10 = h_mm，nat_h = h_cm×10 = w_mm
        通过 pdf.rotation(±90°) 将自然内容旋转后嵌入面板区域。
        旋转轴心取面板中心，自然画布中心与面板中心对齐。
        """
        ppi = sku_config.ppi

        # 自然画布尺寸（mm）
        nat_w = h_mm   # w_cm * 10
        nat_h = w_mm   # h_cm * 10

        # 旋转轴心 = 面板中心
        cx = x_mm + w_mm / 2.0
        cy = y_mm + h_mm / 2.0

        # 自然画布原点（中心对齐面板中心）
        nat_x = cx - nat_w / 2.0
        nat_y = cy - nat_h / 2.0

        # 条形码定界框：先旋转 90° 变横向，再随整体旋转回来
        icon_barcode_frame = self.resources['icon_paste_barcode'].rotate(90, expand=True)
        barcode_frame_h_mm = 50.0  # 5 cm

        sku_text = sku_config.sku_name
        sku_pt, pil_sku = self._get_font_size(
            sku_text, 'Arial Bold', nat_w * 0.5, ppi)

        main_row = engine.Row(
            align='center', justify='space-between',
            fixed_width=nat_w,
            padding_x=nat_w * 0.07,
            children=[
                engine.Image(icon_barcode_frame, height=barcode_frame_h_mm),
                engine.Text(sku_text, 'Arial', 'B', sku_pt,
                            pil_font=pil_sku, ppi=ppi),
            ]
        )

        # 在自然画布内垂直居中
        row_y = nat_y + (nat_h - main_row.height) / 2.0
        main_row.layout(nat_x, row_y)

        with pdf.rotation(rotation_deg, cx, cy):
            main_row.render(pdf)

    def _draw_label(self, pdf: FPDF, sku_config,
                     x_mm, y_mm, w_mm, h_mm):
        """
        在标签背景图上叠加绘制：
          - 毛重/净重文字（左-中对齐）
          - 箱体尺寸文字（左-中对齐）
          - SKU 条形码及其文字（顶-中对齐）
          - SN 条形码及其文字（顶-中对齐）

        标签背景图已由上层 engine.Image.render() 绘制，此处仅添加内容层。
        """
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        # —— 字体尺寸 ——
        # 原代码：text_height = int(H * 0.21)（H 为像素）
        text_size_px = int(h_mm * 0.21 * px_per_mm)
        text_size_pt = text_size_px * 72.0 / ppi
        pil_text = ImageFont.truetype(self.font_paths['Arial Bold'], text_size_px)

        # 原代码：font_barcode = int(H * 0.12)
        bc_label_size_px = int(h_mm * 0.12 * px_per_mm)
        bc_label_size_pt = bc_label_size_px * 72.0 / ppi
        pil_bc_label = ImageFont.truetype(self.font_paths['Arial'], bc_label_size_px)

        # —— 文字内容 ——
        weight_text = (f"G.W./N.W. : {sku_config.side_text['gw_value']} / "
                       f"{sku_config.side_text['nw_value']} lbs")
        box_text = (f"BOX SIZE : {sku_config.l_in:.1f}\" x "
                    f"{sku_config.w_in:.1f}\" x {sku_config.h_in:.1f}\"")

        text_x_mm = x_mm + w_mm * 0.388   # 从 38.8% 宽度开始，与原代码一致

        # 上半格中心 (H × 0.25)，左-中对齐
        self._draw_text_lm(pdf, text_x_mm, y_mm + h_mm * 0.25,
                           weight_text, 'Arial', 'B', text_size_pt, pil_text, ppi)
        # 下半格中心 (H × 0.75)，左-中对齐
        self._draw_text_lm(pdf, text_x_mm, y_mm + h_mm * 0.75,
                           box_text, 'Arial', 'B', text_size_pt, pil_text, ppi)

        # —— 条形码（mm 尺寸） ——
        bc_h_mm     = h_mm * 0.44
        sku_bc_w_mm = w_mm * 0.17
        sn_bc_w_mm  = w_mm * 0.12

        # SKU 条形码（x=W×0.695, y=H×0.08）
        sku_bc_x = x_mm + w_mm * 0.695
        sku_bc_y = y_mm + h_mm * 0.08
        sku_bc_img = generate_barcode_image(
            sku_config.sku_name,
            int(sku_bc_w_mm * px_per_mm),
            int(bc_h_mm * px_per_mm),
        )
        pdf.image(self._barcode_to_buf(sku_bc_img),
                  x=sku_bc_x, y=sku_bc_y, w=sku_bc_w_mm, h=bc_h_mm)

        # SKU 条形码下方文字（顶-中对齐）
        self._draw_text_mt(
            pdf,
            sku_bc_x + sku_bc_w_mm / 2.0,
            sku_bc_y + bc_h_mm + h_mm * 0.01,
            sku_config.sku_name,
            'Arial', '', bc_label_size_pt, pil_bc_label, ppi,
        )

        # SN 条形码（x=W×0.877, y=H×0.08）
        sn_bc_x   = x_mm + w_mm * 0.877
        sn_bc_y   = y_mm + h_mm * 0.08
        sn_code   = sku_config.side_text['sn_code']
        sn_bc_img = generate_barcode_image(
            sn_code,
            int(sn_bc_w_mm * px_per_mm),
            int(bc_h_mm * px_per_mm),
        )
        pdf.image(self._barcode_to_buf(sn_bc_img),
                  x=sn_bc_x, y=sn_bc_y, w=sn_bc_w_mm, h=bc_h_mm)

        # SN 条形码下方文字（顶-中对齐）
        self._draw_text_mt(
            pdf,
            sn_bc_x + sn_bc_w_mm / 2.0,
            sn_bc_y + bc_h_mm + h_mm * 0.01,
            sn_code,
            'Arial', '', bc_label_size_pt, pil_bc_label, ppi,
        )