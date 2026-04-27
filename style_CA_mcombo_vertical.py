# -*- coding: utf-8 -*-
"""
加拿大 MCombo 第二箱三箱样式 - fpdf2 版
"""
from fpdf import FPDF
from PIL import Image, ImageFont
from style_base import BoxMarkStyle, StyleRegistry
import general_functions
from general_functions import generate_barcode_image
from layout_engine import Image as LEImage, Column
import layout_engine as engine


@StyleRegistry.register
class MComboVerticalStyle(BoxMarkStyle):
    """加拿大 MCombo 第二箱三箱箱唛样式 (fpdf2 版)"""

    def get_style_name(self):
        return "CA-mcombo_vertical"

    def get_style_description(self):
        return "加拿大 MCombo 转口第二箱三箱 箱唛"

    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'color', 'product',
                'size', 'side_text', 'sku_name', 'box_number', 'sponge_verified', 'company_name', 'contact_info']

    def get_layout_config_mm(self, sku_config):
        """MCombo 第二三箱样式 - 12块布局（4列3行），单位 mm。
        与标准样式的区别：flap_top_front1 和 flap_btm_front2 高度为 w_mm（完整宽度）。"""
        l_mm = sku_config.l_cm * 10
        w_mm = sku_config.w_cm * 10
        h_mm = sku_config.h_cm * 10
        half_w_mm = w_mm / 2

        x0 = 0.0
        x1 = l_mm
        x2 = l_mm + w_mm
        x3 = 2 * l_mm + w_mm

        # y1 使用完整 w_mm（大盖子占满整个宽度），而非 half_w_mm
        y0 = 0.0
        y1 = w_mm
        y2 = w_mm + h_mm

        return {
            # 第一行：顶盖层 (Top Flaps)
            # flap_top_front1 是大盖子，高度为 w_mm（完整宽度）
            "flap_top_front1": (x0, y0,          l_mm, w_mm),
            "flap_top_side1":  (x1, half_w_mm,   w_mm, half_w_mm),
            "flap_top_front2": (x2, half_w_mm,   l_mm, half_w_mm),
            "flap_top_side2":  (x3, half_w_mm,   w_mm, half_w_mm),
            # 第二行：正身层 (Main Body)
            "panel_front1":    (x0, y1, l_mm, h_mm),
            "panel_side1":     (x1, y1, w_mm, h_mm),
            "panel_front2":    (x2, y1, l_mm, h_mm),
            "panel_side2":     (x3, y1, w_mm, h_mm),
            # 第三行：底盖层 (Bottom Flaps)
            "flap_btm_front1": (x0, y2, l_mm, half_w_mm),
            "flap_btm_side1":  (x1, y2, w_mm, half_w_mm),
            # flap_btm_front2 是大盖子，高度为 w_mm（完整宽度）
            "flap_btm_front2": (x2, y2, l_mm, w_mm),
            "flap_btm_side2":  (x3, y2, w_mm, half_w_mm),
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

    def get_preview_images(self):
        preview_dir = self.base_dir / 'assets' / 'Mcombo' / '样式一' / '实例生成图'
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

    # ── 资源 / 字体加载 ─────────────────────────────────────────────────────────

    def _load_resources(self):
        """加载 MCombo 第二三箱样式的图片资源（与标准样式相同）"""
        res_base = self.base_dir / 'assets' / 'Mcombo' / '样式一' / '矢量文件'
        self.resources = {
            # 翻盖图标需要 PIL 旋转，保留为 PIL Image
            'icon_left_2_panel':    Image.open(res_base / '顶部-左-2箱.png').convert('RGBA'),
            'icon_left_3_panel':    Image.open(res_base / '顶部-左-3箱.png').convert('RGBA'),
            'icon_right_2-1_panel': Image.open(res_base / '顶部-右-2-1-32KG.png').convert('RGBA'),
            'icon_right_2-2_panel': Image.open(res_base / '顶部-右-2-2.png').convert('RGBA'),
            'icon_right_3-1_panel': Image.open(res_base / '顶部-右-3-1-32KG.png').convert('RGBA'),
            'icon_right_3-2_panel': Image.open(res_base / '顶部-右-3-2.png').convert('RGBA'),
            'icon_right_3-3_panel': Image.open(res_base / '顶部-右-3-3.png').convert('RGBA'),
            # 静态图标存储为路径，fpdf2 直接接受路径，无需 PIL 预加载
            'icon_trademark':       res_base / '正唛logo.png',
            'icon_company':         res_base / '正唛公司信息.png',
            'icon_box_number_1':    res_base / '正唛 Box 1.png',
            'icon_box_number_2':    res_base / '正唛 Box 2.png',
            'icon_box_number_3':    res_base / '正唛 Box 3.png',
            'icon_side_label_box':  res_base / '侧唛标签框.png',
            'icon_side_logo':       res_base / '侧唛logo.png',
            'icon_side_text_box':   res_base / '侧唛文本框.png',
            # 海绵认证图需要颜色处理，保留为 PIL Image
            'icon_company_bg_left': general_functions.make_it_pure_black(Image.open(res_base / '正唛-公司名称.png').convert('RGBA')),
            'icon_company_bg_right': general_functions.make_it_pure_black(Image.open(res_base / '正唛-邮箱.png').convert('RGBA')),
            
            
            'icon_side_sponge':     general_functions.make_it_pure_black(
                                        Image.open(res_base / '海绵认证.png').convert('RGBA')),
        }

    def _load_fonts(self):
        font_base = self.base_dir / 'assets' / 'Mcombo' / '样式一' / '箱唛字体'
        self.font_paths = {
            'Calibri-Bold':      str(font_base / 'calibri-bold.ttf'),
            'AvantGardeLT-Demi': str(font_base / 'avantgardelt-demi.ttf'),
        }

    # ── fpdf2 字体注册 ──────────────────────────────────────────────────────────

    def register_fonts(self, pdf: FPDF):
        pdf.add_font('Calibri-Bold',      '', self.font_paths['Calibri-Bold'])
        pdf.add_font('AvantGardeLT-Demi', '', self.font_paths['AvantGardeLT-Demi'])

    # ── 核心绘制入口 ────────────────────────────────────────────────────────────

    def draw_to_pdf(self, pdf: FPDF, sku_config):
        """将所有面板直接绘制到已添加页面的 FPDF 对象上"""
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

        y1 = w_mm
        y2 = w_mm + h_mm

        # 两块正面面板
        self._draw_front_panel(pdf, sku_config, x0, y1, l_mm, h_mm)
        self._draw_front_panel(pdf, sku_config, x2, y1, l_mm, h_mm)

        # 两块侧面面板：
        # 1. 先在以面板中心为原点、顺时针旋转90°的坐标系里，
        #    用交换后的尺寸(h_mm 宽 × w_mm 高)绘制所有元素（位置/尺寸全按横向计算）
        # 2. pdf.rotation(-90) 再逆时针旋转90°，把内容放回原来的竖向面板区域
        cy_side = y1 + h_mm / 2
        for sx in (x1, x3):
            cx = sx + w_mm / 2
            with pdf.rotation(90, cx, cy_side):
                self._draw_side_panel(pdf, sku_config,
                                      cx - h_mm / 2, cy_side - w_mm / 2,
                                      h_mm, w_mm)

        # 翻盖面板
        # flap_top_front1（左侧大盖子，高 w_mm）：不旋转
        self._draw_flap(pdf, sku_config, x0, 0.0, l_mm, w_mm, rotate_180 = False)

        # flap_btm_front2（右侧大盖子，高 w_mm）：旋转 180°
        self._draw_flap(pdf, sku_config, x2, y2, l_mm, w_mm, rotate_180 = True)

    # ── 内部辅助方法（与 mcombo_standard 相同）──────────────────────────────────

    def _get_font_size(self, text, font_key, target_width_mm, ppi, target_height_mm = None):
        """
        根据目标宽度（mm）计算字号，返回 (font_size_pt, pil_font)。
        """
        target_width_px = int(target_width_mm * ppi / 25.4)
        target_height_px = int(target_height_mm * ppi / 25.4) if target_height_mm else None # 预设一个高度约束，避免过高的字体
        size_px = general_functions.get_max_font_size(text, self.font_paths[font_key], target_width_px, target_height_px)
        size_pt = size_px * 72.0 / ppi
        pil_font = ImageFont.truetype(self.font_paths[font_key], size_px)
        return size_pt, pil_font

    @staticmethod
    def _pil_bbox_mm(pil_font, text, ppi):
        """使用 anchor='ls' 获取文字边框并换算为 mm。
        top 为负值（基线以上），bottom 为正值（基线以下）。"""
        left, top, right, bottom = pil_font.getbbox(text, anchor='ls')
        px_per_mm = ppi / 25.4
        return left / px_per_mm, top / px_per_mm, right / px_per_mm, bottom / px_per_mm

    def _draw_text_top_left(self, pdf, x_mm, y_top_mm, text,
                             font_family, font_style, font_size_pt, pil_font, ppi,
                             color=(0, 0, 0)):
        """以左-顶锚点绘制文字（等价于 PIL anchor='la'，y 对齐文字视觉顶端）"""
        _, top_mm, _, _ = self._pil_bbox_mm(pil_font, text, ppi)
        baseline_y = y_top_mm + (-top_mm)
        r, g, b = color
        pdf.set_text_color(r, g, b)
        pdf.set_font(font_family, font_style, font_size_pt)
        pdf.text(x_mm, baseline_y, text)

    def _draw_text_top_center(self, pdf, x_center_mm, y_top_mm, text,
                               font_family, font_style, font_size_pt, pil_font, ppi,
                               color=(0, 0, 0)):
        """以中-顶锚点绘制文字（水平居中，y 对齐文字视觉顶端）"""
        left_mm, top_mm, right_mm, _ = self._pil_bbox_mm(pil_font, text, ppi)
        text_w_mm = right_mm - left_mm
        x_mm = x_center_mm - text_w_mm / 2.0
        baseline_y = y_top_mm + (-top_mm)
        r, g, b = color
        pdf.set_text_color(r, g, b)
        pdf.set_font(font_family, font_style, font_size_pt)
        pdf.text(x_mm, baseline_y, text)

    def _draw_text_mid_center(self, pdf, x_center_mm, y_center_mm, text,
                               font_family, font_style, font_size_pt, pil_font, ppi,
                               color=(0, 0, 0)):
        """以中-中锚点绘制文字（等价于 PIL anchor='mm'）"""
        left_mm, top_mm, right_mm, bottom_mm = self._pil_bbox_mm(pil_font, text, ppi)
        text_w_mm = right_mm - left_mm
        text_h_mm = bottom_mm - top_mm
        x_mm = x_center_mm - text_w_mm / 2.0
        baseline_y = y_center_mm + (-top_mm) - text_h_mm / 2.0
        r, g, b = color
        pdf.set_text_color(r, g, b)
        pdf.set_font(font_family, font_style, font_size_pt)
        pdf.text(x_mm, baseline_y, text)

    @staticmethod
    def _draw_s_curve_bottom(pdf, panel_x, panel_y, panel_w, panel_h,
                              x3_rel, h_left, x4_rel, h_right):
        """在面板底部绘制 S 形过渡黑色底框"""
        x3 = panel_x + x3_rel
        y3 = panel_y + panel_h - h_left
        x4 = panel_x + x4_rel
        y4 = panel_y + panel_h - h_right
        panel_bottom = panel_y + panel_h

        pdf.set_fill_color(0, 0, 0)

        if x3_rel > 0:
            pdf.rect(panel_x, y3, x3_rel, h_left, style='F')

        right_w = panel_w - x4_rel
        if right_w > 0:
            pdf.rect(x4, y4, right_w, h_right, style='F')

        curve_pts = []
        for i in range(21):
            t = i / 20.0
            cx = x3 + (x4 - x3) * t
            t_s = t * t * (3.0 - 2.0 * t)
            cy = y3 + (y4 - y3) * t_s
            curve_pts.append((cx, cy))
        curve_pts.append((x4, panel_bottom))
        curve_pts.append((x3, panel_bottom))
        pdf.polygon(curve_pts, style='F')

    # ── 面板绘制方法（与 mcombo_standard 相同）──────────────────────────────────
    def _draw_flap(self, pdf: FPDF, sku_config,
                         x_mm, y_mm, w_mm, h_mm, rotate_180 = False):
        
        # 统一一下三个元素的宽度
        target_width = w_mm * 0.53
        
        # 最上方的SKU名称
        sku_target_width_mm = target_width
        sku_target_height_mm = 100 #  最大高度是100mm，避免过高字体导致的布局问题
        size_sku_pt, _ = self._get_font_size(sku_config.sku_name, 'AvantGardeLT-Demi',target_width_mm = sku_target_width_mm, target_height_mm = sku_target_height_mm, ppi=sku_config.ppi)
        sku_elem = engine.Text(
            text=sku_config.sku_name,
            font_family='AvantGardeLT-Demi',
            font_size_pt=size_sku_pt,
            color=(0, 0, 0),
        )

        total_boxes = sku_config.box_number['total_boxes']
        current_box = sku_config.box_number['current_box']
        icon_upper  = self.resources[f'icon_left_{total_boxes}_panel']
        icon_lower = self.resources[f'icon_right_{total_boxes}-{current_box}_panel']

        icon_upper_elem = LEImage(icon_upper, width=target_width)
        icon_lower_elem = LEImage(icon_lower, width=target_width)

        col = Column(
            [
                sku_elem, 
                icon_upper_elem, 
                icon_lower_elem
                ], 
            spacing=18.0,
            fixed_height= h_mm,
            fixed_width= w_mm,
            justify= 'center', 
            align='center',
            )
        
        col.layout(x_mm, y_mm)
        
        if rotate_180:
            cx = x_mm + w_mm / 2.0
            cy = y_mm + h_mm / 2.0
            with pdf.rotation(180, cx, cy):
                col.render(pdf)
        else:
            col.render(pdf)

    def _draw_front_panel(self, pdf: FPDF, sku_config, x_mm, y_mm, w_mm, h_mm):
        """绘制正面（正唛）面板"""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        # ── 1. 商标 Logo（居中顶部，高度 = 面板高度 / 3）──────────────────────
        icon_trademark = self.resources['icon_trademark']
        tm_h_mm = h_mm * 0.28
        with Image.open(icon_trademark) as _img:
            _tm_w, _tm_h = _img.size
        tm_w_mm = tm_h_mm * _tm_w / _tm_h
        if tm_w_mm > w_mm * 0.9:
            tm_w_mm = w_mm * 0.9
            tm_h_mm = tm_w_mm * _tm_h / _tm_w
        tm_x = x_mm + (w_mm - tm_w_mm) / 2.0
        tm_y = y_mm
        pdf.image(icon_trademark, x=tm_x, y=tm_y, w=tm_w_mm, h=tm_h_mm)

        # ── 2. 颜色标签（右上角，黑色圆角背景 + 金色文字）──────────────────────
        color_text = str(sku_config.color)
        color_size_px = int(h_mm * px_per_mm * 0.0382)
        color_size_pt = color_size_px * 72.0 / ppi
        pil_color = ImageFont.truetype(self.font_paths['Calibri-Bold'], color_size_px)

        _, top_c, _, bottom_c = self._pil_bbox_mm(pil_color, color_text, ppi)
        left_c, _, right_c, _ = self._pil_bbox_mm(pil_color, color_text, ppi)
        text_w_mm = right_c - left_c
        text_h_mm = bottom_c - top_c

        color_x = x_mm + w_mm - text_w_mm - 40.0
        color_y_top = y_mm + 40.0

        pad_x_mm = 8.0
        pad_y_top_mm = 4.0 * 0.7
        pad_y_bot_mm = 4.0 * 1.4
        radius_mm = 16 * 25.4 / ppi

        rect_x = color_x - pad_x_mm
        rect_y = color_y_top - pad_y_top_mm
        rect_w = text_w_mm + 2 * pad_x_mm
        rect_h = text_h_mm + pad_y_top_mm + pad_y_bot_mm

        pdf.set_fill_color(0, 0, 0)
        pdf.rect(rect_x, rect_y, rect_w, rect_h,
                 style='F', round_corners=True, corner_radius=radius_mm)

        self._draw_text_top_left(pdf, color_x, color_y_top, color_text,
                                 'Calibri-Bold', '', color_size_pt, pil_color, ppi,
                                 color=(161, 142, 102))

        # ── 3. 产品名称 + 装饰椭圆 + 尺寸文字 ──────────────────────────────────
        product_text = sku_config.product
        size_text = getattr(sku_config, 'size', None) or " "

        product_size_px = int(h_mm * px_per_mm * 0.1238 )
        size_size_px    = int(h_mm * px_per_mm * 0.045 )

        pil_product = ImageFont.truetype(self.font_paths['AvantGardeLT-Demi'], product_size_px)
        p_left, p_top, p_right, p_bottom = pil_product.getbbox(product_text)
        product_w_px = p_right - p_left
        max_product_w_px = int(w_mm * px_per_mm * 0.85)
        if product_w_px > max_product_w_px:
            product_size_px = int(product_size_px * max_product_w_px / product_w_px)
            pil_product = ImageFont.truetype(self.font_paths['AvantGardeLT-Demi'], product_size_px)
            p_left, p_top, p_right, p_bottom = pil_product.getbbox(product_text)
            product_w_px = p_right - p_left
        product_size_pt = product_size_px * 72.0 / ppi
        product_w_mm = product_w_px / px_per_mm
        product_h_mm = (p_bottom - p_top) / px_per_mm

        pil_size = ImageFont.truetype(self.font_paths['Calibri-Bold'], size_size_px)
        s_left, s_top, s_right, s_bottom = pil_size.getbbox(size_text)
        size_w_mm = (s_right - s_left) / px_per_mm
        size_h_mm = (s_bottom - s_top) / px_per_mm
        size_size_pt = size_size_px * 72.0 / ppi

        h_right_mm = 100.0
        gap_mm = 10.0
        line_h_mm = 3.0
        line_w_mm = product_w_mm * 0.85
        size_offset_mm = 5.0

        total_group_h = (product_h_mm + gap_mm +
                         line_h_mm + gap_mm +
                         size_h_mm + size_offset_mm)
        bottom_section_top = y_mm + h_mm - h_right_mm
        logo_bottom        = y_mm + tm_h_mm
        available_h        = bottom_section_top - logo_bottom
        
        # 中间整体垂直居中，略微向上调整 3%（0.03）以视觉上更贴近 logo
        group_start_y      = logo_bottom + (available_h - total_group_h) / 2.0 - h_mm * 0.03 

        product_offset_mm = 5.0
        product_x = x_mm + (w_mm - product_w_mm) / 2.0
        self._draw_text_top_left(pdf, product_x,
                                 group_start_y - product_offset_mm,
                                 product_text,
                                 'AvantGardeLT-Demi', '', product_size_pt, pil_product, ppi)

        line_y = group_start_y + product_h_mm + gap_mm
        line_x = x_mm + (w_mm - line_w_mm) / 2.0
        pdf.set_fill_color(0, 0, 0)
        pdf.ellipse(line_x, line_y, line_w_mm, line_h_mm, style='F')

        size_y_top = line_y + line_h_mm + gap_mm + size_offset_mm
        size_x = x_mm + (w_mm - size_w_mm) / 2.0
        self._draw_text_top_left(pdf, size_x, size_y_top,
                                 size_text, 'Calibri-Bold', '', size_size_pt, pil_size, ppi)

        # ── 4. 底部黑色底框（S 形过渡）──────────────────────────────────────────
        self._load_fonts()
        fonts_paths = self.font_paths  # 确保字体路径已加载，供后续使用
        icon_company = general_functions.draw_dynamic_company_brand(
            sku_config,
            sku_config.company_name,
            sku_config.contact_info,
            fonts_paths,
            self.resources
        )
        
        icon_company_h_mm = 16.0   # 1.6 cm
        icon_company_w_mm = icon_company_h_mm * icon_company.width / icon_company.height

        left_section_w_mm = 10.0 + icon_company_w_mm + 40.0
        h_left_mm  = 50.0
        x3_rel = left_section_w_mm - 100.0
        x4_rel = left_section_w_mm

        self._draw_s_curve_bottom(
            pdf, x_mm, y_mm, w_mm, h_mm,
            x3_rel=x3_rel, h_left=h_left_mm,
            x4_rel=x4_rel, h_right=h_right_mm,
        )

        bottom_gb_h_mm = sku_config.bottom_gb_h * 10.0
        company_y = y_mm + h_mm - bottom_gb_h_mm
        pdf.image(icon_company,
                  x=x_mm + 10.0, y=company_y,
                  w=icon_company_w_mm, h=icon_company_h_mm)

        current_box = sku_config.box_number['current_box']
        icon_box = self.resources[f'icon_box_number_{current_box}']
        box_icon_h_mm = h_right_mm / 4.0
        with Image.open(icon_box) as _img:
            _bw, _bh = _img.size
        box_icon_w_mm = box_icon_h_mm * _bw / _bh
        box_icon_y = y_mm + h_mm - h_left_mm + (h_left_mm - box_icon_h_mm) / 2.0
        pdf.image(icon_box,
                  x=x_mm + 10.0, y=box_icon_y,
                  w=box_icon_w_mm, h=box_icon_h_mm)

        sku_text = sku_config.sku_name
        sku_area_left_mm  = 10.0 + icon_company_w_mm + 30.0
        sku_area_right_mm = w_mm - 30.0
        sku_max_w_mm = sku_area_right_mm - sku_area_left_mm
        sku_max_h_mm = 80.0

        sku_size_pt, pil_sku = self._get_font_size(
            sku_text, 'Calibri-Bold', sku_max_w_mm, ppi)
        _, sku_top, _, sku_bottom = self._pil_bbox_mm(pil_sku, sku_text, ppi)
        sku_h_mm = sku_bottom - sku_top
        if sku_h_mm > sku_max_h_mm:
            sku_size_pt, pil_sku = self._get_font_size(
                sku_text, 'Calibri-Bold',
                sku_max_w_mm * sku_max_h_mm / sku_h_mm, ppi)

        sku_center_x = x_mm + (sku_area_left_mm + sku_area_right_mm) / 2.0
        sku_center_y = y_mm + h_mm - h_right_mm / 2.0 + 3.0

        self._draw_text_mid_center(pdf, sku_center_x, sku_center_y,
                                   sku_text, 'Calibri-Bold', '', sku_size_pt, pil_sku, ppi,
                                   color=(161, 142, 102))

    def _draw_side_panel(self, pdf: FPDF, sku_config, x_mm, y_mm, w_mm, h_mm):
        """绘制侧面（侧唛）面板"""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4
        l_mm = sku_config.l_cm * 10
        
        bottom_gb_h = 8.0 # 侧唛底部边框的高度，设置为8厘米

        # ── 1. 底部黑色底框（S 形过渡）──────────────────────────────────────────
        icon_company = self.resources['icon_company']
        icon_company_h_mm = 16.0
        with Image.open(icon_company) as _img:
            _cw, _ch = _img.size
        icon_company_w_mm = icon_company_h_mm * _cw / _ch

        h_left_mm  = bottom_gb_h * 10.0
        h_right_mm = h_left_mm * 0.5

        left_section_w_mm = l_mm - (10.0 + icon_company_w_mm + 40.0)
        max_left_mm = w_mm - 100.0 - 10.0
        if left_section_w_mm > max_left_mm:
            left_section_w_mm = max_left_mm

        x3_rel = left_section_w_mm
        x4_rel = min(left_section_w_mm + 100.0, w_mm - 10.0)

        self._draw_s_curve_bottom(
            pdf, x_mm, y_mm, w_mm, h_mm,
            x3_rel=x3_rel, h_left=h_left_mm,
            x4_rel=x4_rel, h_right=h_right_mm,
        )

        sku_text = sku_config.sku_name
        sku_max_w_mm = left_section_w_mm
        sku_max_h_mm = 80.0

        sku_size_pt, pil_sku = self._get_font_size(
            sku_text, 'Calibri-Bold', sku_max_w_mm, ppi)
        _, sku_top, _, sku_bottom = self._pil_bbox_mm(pil_sku, sku_text, ppi)
        sku_h_mm = sku_bottom - sku_top
        if sku_h_mm > sku_max_h_mm:
            sku_size_pt, pil_sku = self._get_font_size(
                sku_text, 'Calibri-Bold',
                sku_max_w_mm * sku_max_h_mm / sku_h_mm, ppi)

        sku_area_left_mm  = 30.0
        sku_area_right_mm = left_section_w_mm
        sku_center_x = x_mm + (sku_area_left_mm + sku_area_right_mm) / 2.0
        sku_center_y = y_mm + h_mm - h_left_mm / 2.0 + 3.0

        self._draw_text_mid_center(pdf, sku_center_x, sku_center_y,
                                   sku_text, 'Calibri-Bold', '', sku_size_pt, pil_sku, ppi,
                                   color=(161, 142, 102))

        # ── 2. 侧唛标签框（左上角 3cm, 3cm）──────────────────────────────────
        # 加拿大样式不需要这个

        # ── 3. 侧唛 Logo（右上角，高 5cm，宽不超过 (w-8cm)/2）─────────────────
        icon_side_logo = self.resources['icon_side_logo']
        side_logo_h_mm = 50.0
        max_logo_w_mm  = (w_mm - 80.0) * 0.5
        with Image.open(icon_side_logo) as _img:
            _sw, _sh = _img.size
        side_logo_w_mm = side_logo_h_mm * _sw / _sh
        if side_logo_w_mm > max_logo_w_mm:
            side_logo_w_mm = max_logo_w_mm
            side_logo_h_mm = side_logo_w_mm * _sh / _sw
        logo_x = x_mm + w_mm - side_logo_w_mm - 40.0
        logo_y = y_mm + 25.0
        pdf.image(icon_side_logo,
                  x=logo_x, y=logo_y,
                  w=side_logo_w_mm, h=side_logo_h_mm)

        # ── 4. 侧唛文本框（含 G.W.、尺寸、条形码）──────────────────────────────
        icon_text_box = self.resources['icon_side_text_box']
        table_h_mm = 80.0
        with Image.open(icon_text_box) as _img:
            _tw, _th = _img.size
        table_w_mm = table_h_mm * _tw / _th

        spacing_left_mm   = 28.1
        spacing_bottom_mm = 15.0
        table_y = (y_mm + h_mm
                   - bottom_gb_h * 10.0
                   - spacing_bottom_mm
                   - table_h_mm)

        if sku_config.sponge_verified:
            icon_sponge = self.resources['icon_side_sponge']
            sponge_w_mm = table_h_mm * icon_sponge.width / icon_sponge.height
            sponge_x = x_mm + spacing_left_mm
            pdf.image(icon_sponge,
                      x=sponge_x, y=table_y,
                      w=sponge_w_mm, h=table_h_mm)
            table_x = sponge_x + sponge_w_mm + 1.0
        else:
            table_x = x_mm + spacing_left_mm

        pdf.image(icon_text_box,
                  x=table_x, y=table_y,
                  w=table_w_mm, h=table_h_mm)

        self._draw_side_text_content(
            pdf, sku_config, table_x, table_y, table_w_mm, table_h_mm)

    def _draw_side_text_content(self, pdf: FPDF, sku_config,
                                 x_mm, y_mm, w_mm, h_mm):
        """在侧唛文本框区域叠加绘制动态文字和条形码"""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        label_px   = int(h_mm * px_per_mm * 0.076)
        bold_px    = int(h_mm * px_per_mm * 0.095)
        barcode_px = int(h_mm * px_per_mm * 0.058)

        pil_label   = ImageFont.truetype(self.font_paths['AvantGardeLT-Demi'], label_px)
        pil_bold    = ImageFont.truetype(self.font_paths['Calibri-Bold'],      bold_px)
        pil_barcode = ImageFont.truetype(self.font_paths['Calibri-Bold'],      barcode_px)

        label_pt   = label_px   * 72.0 / ppi
        bold_pt    = bold_px    * 72.0 / ppi
        barcode_pt = barcode_px * 72.0 / ppi

        text_x = x_mm + w_mm * 0.651

        weight_text = (f'G.W./N.W.: {sku_config.side_text["gw_value"] * 0.4535:.1f} / '
                       f'{sku_config.side_text["nw_value"] * 0.4535:.1f} Kg')
        dim_text = (f'BOX SIZE: {sku_config.l_cm:.0f}cm x '
                    f'{sku_config.w_cm:.0f}cm x {sku_config.h_cm:.0f}cm')

        self._draw_text_top_left(pdf, text_x, y_mm + h_mm * 0.063,
                                 weight_text, 'AvantGardeLT-Demi', '', label_pt, pil_label, ppi)
        self._draw_text_top_left(pdf, text_x, y_mm + h_mm * 0.237,
                                 dim_text, 'AvantGardeLT-Demi', '', label_pt, pil_label, ppi)

        left_center_mm  = x_mm + w_mm * 0.46
        right_center_mm = x_mm + w_mm * 0.847
        barcode_y_mm    = y_mm + h_mm * 0.42
        barcode_text_y  = y_mm + h_mm * 0.76
        barcode_h_mm    = h_mm * 0.35

        sku_bc_w_mm = w_mm * 0.46
        sku_bc_img = generate_barcode_image(
            sku_config.sku_name,
            int(sku_bc_w_mm * px_per_mm),
            int(barcode_h_mm * px_per_mm),
        )
        pdf.image(sku_bc_img,
                  x=left_center_mm - sku_bc_w_mm / 2.0,
                  y=barcode_y_mm,
                  w=sku_bc_w_mm, h=barcode_h_mm)
        self._draw_text_top_center(pdf, left_center_mm, barcode_text_y,
                                   sku_config.sku_name,
                                   'Calibri-Bold', '', barcode_pt, pil_barcode, ppi)

        sn_code = sku_config.side_text['sn_code']
        sn_bc_w_mm = w_mm * 0.28
        sn_bc_img = generate_barcode_image(
            sn_code,
            int(sn_bc_w_mm * px_per_mm),
            int(barcode_h_mm * px_per_mm),
        )
        pdf.image(sn_bc_img,
                  x=right_center_mm - sn_bc_w_mm / 2.0,
                  y=barcode_y_mm,
                  w=sn_bc_w_mm, h=barcode_h_mm)
        self._draw_text_top_center(pdf, right_center_mm, barcode_text_y,
                                   sn_code,
                                   'Calibri-Bold', '', barcode_pt, pil_barcode, ppi)

        made_text = sku_config.side_text.get('origin_text', 'MADE IN CHINA')
        self._draw_text_top_left(pdf, x_mm + w_mm * 0.51, y_mm + h_mm * 0.87,
                                 made_text, 'Calibri-Bold', '', bold_pt, pil_bold, ppi)
