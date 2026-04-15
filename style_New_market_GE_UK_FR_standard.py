# -*- coding: utf-8 -*-
"""
MCombo 标准样式 - 将原有的 BoxMarkEngine 转换为样式类
"""
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from style_base import BoxMarkStyle, StyleRegistry
import general_functions
from layout_engine import Element, Row, Image as ImageElement

@StyleRegistry.register
class MComboStandardStyle(BoxMarkStyle):
    """MCombo 标准箱唛样式（原始样式）"""


    def get_style_name(self):
        return "new_market_standard"

    def get_style_description(self):
        return "new_market 标准箱唛样式"

    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'color', 'product', 'size', 'side_text', 'sku_name', 'box_number',
                'sponge_verified']

    def get_layout_config(self, sku_config):
        """MCombo 标准样式 - 12块布局（4列3行）"""
        # 1. 定义 X 轴的关键节点 (横向逻辑在两种模式下通常保持一致)
        x0 = 0
        x1 = sku_config.l_px
        x2 = sku_config.w_px + sku_config.l_px
        x3 = sku_config.w_px + sku_config.l_px * 2

        # --- 【水平/普通模式】坐标逻辑 ---
        y0 = 0  # 顶盖顶部
        y1 = sku_config.half_w_px  # 正身顶部
        y2 = sku_config.half_w_px + sku_config.h_px  # 底盖顶部

        return {
            # 第一行：顶盖层
            "flap_top_front1": (x0, y0, sku_config.l_px, sku_config.half_w_px),
            "flap_top_side1": (x1, y0, sku_config.w_px, sku_config.half_w_px),
            "flap_top_front2": (x2, y0, sku_config.l_px, sku_config.half_w_px),
            "flap_top_side2": (x3, y0, sku_config.w_px, sku_config.half_w_px),

            # 第二行：正身层
            "panel_front1": (x0, y1, sku_config.l_px, sku_config.h_px),
            "panel_side1": (x1, y1, sku_config.w_px, sku_config.h_px),
            "panel_front2": (x2, y1, sku_config.l_px, sku_config.h_px),
            "panel_side2": (x3, y1, sku_config.w_px, sku_config.h_px),

            # 第三行：底盖层
            "flap_btm_front1": (x0, y2, sku_config.l_px, sku_config.half_w_px),
            "flap_btm_side1": (x1, y2, sku_config.w_px, sku_config.half_w_px),
            "flap_btm_front2": (x2, y2, sku_config.l_px, sku_config.half_w_px),
            "flap_btm_side2": (x3, y2, sku_config.w_px, sku_config.half_w_px),
        }

    def get_panels_mapping(self, sku_config):
        """定义每个区域应该粘贴哪个面板"""
        return {
            "flap_top_front1": "left_up",
            "flap_top_front2": "right_up",
            "panel_front1": "front",
            "panel_side1": "side1",
            "panel_front2": "front",
            "panel_side2": "side2",
            "flap_btm_front1": "left_down",
            "flap_btm_front2": "right_down",
            "flap_top_side1": "side_up",
            "flap_top_side2": "side_up",
            "flap_btm_side1": "side_down",
            "flap_btm_side2": "side_down",
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

    def register_fonts(self, pdf: FPDF):
        pdf.add_font('Calibri',     '', self.font_paths['calibri'])
        pdf.add_font('CalibriBold', '', self.font_paths['calibri_bold'])
        pdf.add_font('ITCDemi',     '', self.font_paths['itc_demi'])
        pdf.add_font('Courier',     '', self.font_paths['courier'])

    def draw_to_pdf(self, pdf: FPDF, sku_config):
        """Render all panels as fully-vector fpdf2 output."""
        layout = self.get_layout_config_mm(sku_config)

        # Fill all panel backgrounds
        r, g, b = sku_config.background_color
        pdf.set_fill_color(r, g, b)
        for _, (x, y, w, h) in layout.items():
            pdf.rect(x, y, w, h, style='F')

        # Front panels (×2) — fully vector
        for key in ('panel_front1', 'panel_front2'):
            x, y, w, h = layout[key]
            self._draw_front_panel_v(pdf, sku_config, x, y, w, h)

        # Side panels — fully vector
        x, y, w, h = layout['panel_side1']
        self._draw_side_panel_v(pdf, sku_config, x, y, w, h,
                                show_legal=True, rotate_deg=0)
        x, y, w, h = layout['panel_side2']
        self._draw_side_panel_v(pdf, sku_config, x, y, w, h,
                                show_legal=False, rotate_deg=0)

        # Left flaps (icon images)
        self._draw_flap_left_v(pdf, sku_config, *layout['flap_top_front1'], rotate_180=False)
        self._draw_flap_left_v(pdf, sku_config, *layout['flap_btm_front1'], rotate_180=True)

        # Right flaps
        self._draw_flap_right_v(pdf, sku_config, *layout['flap_top_front2'], rotate_180=True)
        self._draw_flap_right_v(pdf, sku_config, *layout['flap_btm_front2'], rotate_180=False)

        # Side up/down — blank (already filled with background)

    def generate_all_panels(self, sku_config):
        """生成 MCombo 标准样式需要的所有面板"""
        canvas_left_up, canvas_left_down = self.generate_left_panel(sku_config)
        canvas_right_up, canvas_right_down = self.generate_right_panel(sku_config)
        canvas_front = self.generate_front_panel(sku_config)
        canvas_side1 = self.generate_side_panel(sku_config, show_legal=True)
        canvas_side2 = self.generate_side_panel(sku_config, show_legal=False)
        canvas_side_up, canvas_side_down = self.generate_side_up_down_panel(sku_config)

        return {
            "left_up": canvas_left_up,
            "left_down": canvas_left_down,
            "right_up": canvas_right_up,
            "right_down": canvas_right_down,
            "front": canvas_front,
            "side1": canvas_side1,
            "side2": canvas_side2,
            "side_up": canvas_side_up,
            "side_down": canvas_side_down
        }

    def _load_resources(self):
        """加载 MCombo 标准样式的图片资源"""

        self.res_base = self.base_dir / 'assets' / 'New-market' / '样式一' / '矢量文件'
        self.resources = {
            'icon_left_2_panel': Image.open(self.res_base / '顶部-左-2箱.png').convert('RGBA'),
            'icon_left_3_panel': Image.open(self.res_base / '顶部-左-3箱.png').convert('RGBA'),
            'icon_left_4_panel': Image.open(self.res_base / '顶部-左-4箱.png').convert('RGBA'),
            'icon_right_2-1_panel': Image.open(self.res_base / '顶部-右-2-1.png').convert('RGBA'),
            'icon_right_2-2_panel': Image.open(self.res_base / '顶部-右-2-2.png').convert('RGBA'),
            'icon_right_3-1_panel': Image.open(self.res_base / '顶部-右-3-1.png').convert('RGBA'),
            'icon_right_3-2_panel': Image.open(self.res_base / '顶部-右-3-2.png').convert('RGBA'),
            'icon_right_3-3_panel': Image.open(self.res_base / '顶部-右-3-3.png').convert('RGBA'),
            'icon_right_4-1_panel': Image.open(self.res_base / '德文-顶部-右-4-1.png').convert('RGBA'),
            'icon_right_4-2_panel': Image.open(self.res_base / '德文-顶部-右-4-1.png').convert('RGBA'),
            'icon_right_4-3_panel': Image.open(self.res_base / '德文-顶部-右-4-1.png').convert('RGBA'),
            'icon_right_4-4_panel': Image.open(self.res_base / '德文-顶部-右-4-1.png').convert('RGBA'),
            # 'icon_top_box_number_2_2': Image.open(res_base / '顶部-box-2-2.png').convert('RGBA'),
            'icon_top_box_number_3_2': Image.open(self.res_base / '顶部-box-3-2.png').convert('RGBA'),
            'icon_top_box_number_3_3': Image.open(self.res_base / '顶部-box-3-3.png').convert('RGBA'),
            # 'icon_trademark': Image.open(res_base / '正唛logo.png').convert('RGBA'),
            # 'icon_company': Image.open(res_base / '正唛公司信息.png').convert('RGBA'),
            'icon_box_number_1': Image.open(self.res_base / '正唛 Box 1.png').convert('RGBA'),
            'icon_box_number_2': Image.open(self.res_base / '正唛 Box 2.png').convert('RGBA'),
            'icon_box_number_3': Image.open(self.res_base / '正唛 Box 3.png').convert('RGBA'),
            # 'icon_side_label_box': Image.open(res_base / '侧唛标签框.png').convert('RGBA'),
            # 'icon_side_logo': Image.open(res_base / '侧唛logo.png').convert('RGBA'),
            'icon_side_text_box': general_functions.make_it_pure_black(Image.open(self.res_base / '条码框-去掉竖线.png').convert('RGBA')),
            'icon_side_sponge': Image.open(self.res_base / '海绵认证.png').convert('RGBA'),
            'icon_side_FSC': general_functions.make_it_pure_black(Image.open(self.res_base / 'FSC.png').convert('RGBA')),
            'icon_company_bg_left': general_functions.make_it_pure_black(Image.open(self.res_base / '正唛-公司名称.png').convert('RGBA')),
            'icon_company_bg_right': general_functions.make_it_pure_black(Image.open(self.res_base / '正唛-邮箱.png').convert('RGBA')),
            # 'legal_icon_2_1': make_it_pure_black(Image.open(res_base / legal_icon).convert('RGBA')),
            # 'legal_icon_2_2': general_functions.make_it_pure_black(Image.open(res_base / legal_icon).convert('RGBA')),
            'legal_icon_3_1': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-3-1.png').convert('RGBA')),
            'legal_icon_3_2': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-3-2CC.png').convert('RGBA')),
            'legal_icon_3_3': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-3-2CK.png').convert('RGBA')),
            'legal_icon_3_4': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-3-2RoHs.png').convert('RGBA')),
            'legal_icon_3_5': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-3-2回收.png').convert('RGBA')),
            'legal_icon_3_6': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-3-2绿点.png').convert('RGBA')),
            'legal_icon_4': general_functions.make_it_pure_black(Image.open(self.res_base / '法律标-4.png').convert('RGBA')),
        }

    def _load_fonts(self):
        """加载字体路径"""
        font_base = self.base_dir / 'assets' / 'Mcombo' / '样式一' / '箱唛字体'
        self.font_paths = {
            'calibri': str(font_base / 'calibri.ttf'),
            'calibri_bold': str(font_base / 'calibri-bold.ttf'),
            'itc_demi': str(font_base / 'avantgardelt-demi.ttf'),
            'courier': str(font_base / 'cour.ttf'),
            'side_font_label': str(font_base / 'avantgardelt-demi.ttf'),
            'side_font_bold': str(font_base / 'calibri-bold.ttf'),
            'side_font_barcode': str(font_base / 'calibri_blod.ttf')
        }

        # 字体大小相对比例
        self.font_ratios = {
            'color_font': 51 / 1332,
            'product_font': 180 / 1332,
            'size_font': 60 / 1332,
            'regular_font': 40 / 1332,
            'side_font': 40 / 1332
        }

        return self.font_paths
    def _get_fonts(self, sku_config):
        """根据箱子尺寸动态计算字体大小"""
        height_px = sku_config.h_px

        fonts = {
            'color_font': ImageFont.truetype(
                self.font_paths['calibri_bold'],
                size=int(height_px * self.font_ratios['color_font'])
            ),
            'product_font': ImageFont.truetype(
                self.font_paths['itc_demi'],
                size=int(height_px * self.font_ratios['product_font'])
            ),
            'size_font': ImageFont.truetype(
                self.font_paths['calibri_bold'],
                size=int(height_px * self.font_ratios['size_font'])
            ),
            'regular_font': ImageFont.truetype(
                self.font_paths['itc_demi'],
                size=int(height_px * self.font_ratios['regular_font'])
            ),
            'legal_reg': ImageFont.truetype(self.font_paths['calibri'], size=28),
            'legal_bold': ImageFont.truetype(self.font_paths['calibri_bold'], size=28),
        }
        return fonts

    def generate_left_panel(self, sku_config):

        """生成左侧面板"""
        canvas_left_up = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.half_w_px),
                                   sku_config.background_color)
        canvas_left_down = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.half_w_px),
                                     sku_config.background_color)

        total_box_number = sku_config.box_number['total_boxes']
        icon_left_panel = self.resources[f'icon_left_{total_box_number}_panel']

        icon_left_up_panel = icon_left_panel
        icon_left_down_panel = icon_left_panel.rotate(180, expand=True)

        canvas_left_up = general_functions.paste_center_with_height(
            canvas_left_up, icon_left_up_panel, height_cm=10, dpi=sku_config.dpi)
        canvas_left_down = general_functions.paste_center_with_height(
            canvas_left_down, icon_left_down_panel, height_cm=10, dpi=sku_config.dpi)

        return canvas_left_up, canvas_left_down

    def generate_right_panel(self, sku_config):

        """生成右侧面板"""
        canvas_right_up = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.half_w_px),
                                    sku_config.background_color)
        canvas_right_down = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.half_w_px),
                                      sku_config.background_color)

        total_box_number = sku_config.box_number['total_boxes']
        current_box_number = sku_config.box_number['current_box']
        icon_right_panel = self.resources[f'icon_right_{total_box_number}-{current_box_number}_panel']

        icon_right_panel_up = icon_right_panel.rotate(180, expand=True)
        icon_right_panel_down = icon_right_panel

        canvas_right_up = general_functions.paste_center_with_height(
            canvas_right_up, icon_right_panel_up, height_cm=9, dpi=sku_config.dpi)
        canvas_right_down = general_functions.paste_center_with_height(
            canvas_right_down, icon_right_panel_down, height_cm=9, dpi=sku_config.dpi)
        return canvas_right_up, canvas_right_down

    def generate_front_panel(self, sku_config):
        """生成正面面板"""
        canvas = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.h_px), sku_config.background_color)

        # res_base = self.base_dir / 'assets' / 'New-market' / '样式一' / '矢量文件'
        if getattr(sku_config, 'GE', 0) == 1:
            logo_file = self.res_base / '正唛logo-ELEGUE.png'
        elif getattr(sku_config, 'FR', 0) == 1 or getattr(sku_config, 'UK', 0) == 1:
            logo_file = self.res_base / '正唛logo-MCombo.png'
        else:
            logo_file = self.res_base / '正唛logo-MCombo.png'  # 默认值

        icon_trademark = general_functions.make_it_pure_black(Image.open(logo_file).convert('RGBA'))

        fonts = self._get_fonts(sku_config)

        # 粘贴正唛标志
        canvas_w, canvas_h = canvas.size

        target_h_by_height = canvas_h // 3
        icon_by_height = general_functions.scale_by_height(icon_trademark, target_h_by_height)
        resized_w, resized_h = icon_by_height.size

        # 2. 检查宽度是否超过箱子长度的1/3
        max_allowed_w = canvas_w // 2  # 箱子长度的1/3

        if resized_w > max_allowed_w:
            # 宽度超限，改为按宽度缩放
            icon_trademark_resized = general_functions.scale_by_width(icon_trademark, max_allowed_w)
        else:
            # 宽度未超限，使用按高度缩放的结果
            icon_trademark_resized = icon_by_height

        # icon_trademark_target_h = canvas_h // 3
        # icon_trademark_resized = general_functions.scale_by_height(icon_trademark, icon_trademark_target_h)

        icon_trademark_target_w, icon_trademark_target_h = icon_trademark_resized.size
        paste_x = (canvas_w - icon_trademark_target_w) // 2
        paste_y = 0
        canvas.paste(icon_trademark_resized, (paste_x, paste_y), mask=icon_trademark_resized)

        draw = ImageDraw.Draw(canvas)
        bottom_bg_h = int(sku_config.bottom_gb_h * sku_config.dpi)

        # 生成底部黑色底框和动态SKU文本
        fonts_paths = self._load_fonts()
        icon_company = general_functions.draw_dynamic_company_brand(
            sku_config,
            sku_config.company_name,
            sku_config.contact_info,
            fonts_paths,
            self.resources
        )
        icon_box_number = self.resources[f"icon_box_number_{sku_config.box_number['current_box']}"]
        general_functions.draw_dynamic_bottom_bg_move(canvas, sku_config, icon_company, icon_box_number, self.font_paths)

        # 写入右上角颜色信息
        color_font = fonts['color_font']
        color_text = f"{sku_config.color}"
        bbox = draw.textbbox((0, 0), color_text, font=color_font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        color_x = canvas_w - text_w - int(4 * sku_config.dpi)
        color_y = int(4 * sku_config.dpi)
        color_xy = (color_x, color_y)

        draw = general_functions.draw_rounded_bg_for_text(
            draw, bbox, sku_config, color_xy,
            bg_color=(0, 0, 0), padding_cm=(0.8, 0.4), radius=16)
        draw.text((color_x, color_y), color_text, font=color_font, fill=(161, 142, 102))

        # 写入产品名称和尺寸信息
        # ========== 修改开始：动态调整 product 字体大小 ==========
        fonts = self._get_fonts(sku_config)

        # 计算 product 文字的最大允许宽度（箱子长度的85%）
        max_product_width = int(sku_config.l_px * 0.85)

        product_text = sku_config.product
        product_font = fonts['product_font']

        # 检查当前字体是否超出限制，如果超出则缩小字体
        bbox_product = product_font.getbbox(product_text)
        product_w = bbox_product[2] - bbox_product[0]

        # 如果文字宽度超过限制，按比例缩小字体
        if product_w > max_product_width:
            scale_factor = max_product_width / product_w
            new_font_size = int(product_font.size * scale_factor)
            # 重新加载字体，使用新的大小
            product_font = ImageFont.truetype(
                self.font_paths['itc_demi'],
                size=new_font_size
            )
            # 重新计算文字宽度
            bbox_product = product_font.getbbox(product_text)
            product_w = bbox_product[2] - bbox_product[0]

        # product_text = sku_config.product
        # product_font = fonts['product_font']
        # bbox_product = draw.textbbox((0, 0), product_text, font=product_font)
        # product_w = bbox_product[2] - bbox_product[0]

        size_text = getattr(sku_config, 'size', None) or " " # 如果尺寸信息为空，则使用一个空格占位，避免后续计算出错
        size_font = fonts['size_font']
        bbox_size = draw.textbbox((0, 0), size_text, font=size_font)
        size_w = bbox_size[2] - bbox_size[0]

        gap_px = int(1 * sku_config.dpi)
        # line_height = 7 / 0.74
        line_height = int(0.3 * sku_config.dpi) # 黑线加粗到约 0.5cm
        line_width = int(product_w * 0.85)
        total_group_height = product_font.size + line_height + size_font.size + gap_px * 2

        remaining_space = canvas_h - icon_trademark_target_h - bottom_bg_h
        group_start_y = icon_trademark_target_h + (remaining_space - total_group_height) // 2

        # 绘制产品名称
        product_x = (canvas_w - product_w) // 2
        ascent, descent = product_font.getmetrics()
        # draw.text((product_x, group_start_y + ascent), product_text, font=product_font, fill=(0, 0, 0), anchor="ls")
        product_offset_y = int(0.5 * sku_config.dpi)  # 产品信息上移约 0.5cm
        draw.text((product_x, group_start_y + ascent - product_offset_y), product_text, font=product_font, fill=(0, 0, 0), anchor="ls")

        # 绘制下划线
        line_y_top = group_start_y + product_font.size + gap_px
        line_x0 = (canvas_w - line_width) // 2
        line_x1 = line_x0 + line_width
        line_box = [line_x0, line_y_top, line_x1, line_y_top + line_height]
        general_functions.draw_smooth_ellipse(draw, canvas, line_box, fill=(0, 0, 0))

        # 绘制尺寸信息
        size_x = (canvas_w - size_w) // 2
        size_y = line_y_top + gap_px + line_height
        draw.text((size_x, size_y), size_text, font=size_font, fill=(0, 0, 0))

        return canvas

    def generate_side_panel(self, sku_config, show_legal=True):
        """生成侧面面板"""
        if not hasattr(self, 'fonts') or not self.fonts:
            self.fonts = self._get_fonts(sku_config)

        canvas = Image.new(sku_config.color_mode, (sku_config.w_px, sku_config.h_px), sku_config.background_color)

        # res_base = self.base_dir / 'assets' / 'New-market' / '样式一' / '矢量文件'
        if getattr(sku_config, 'GE', 0) == 1:
            logo_file = self.res_base / '侧唛logo-ELEGUE.png'
        elif getattr(sku_config, 'FR', 0) == 1 or getattr(sku_config, 'UK', 0) == 1:
            logo_file = self.res_base / '侧唛logo-MCombo.png'
        else:
            logo_file = self.res_base / '侧唛logo-MCombo.png'  # 默认值

        icon_side_logo = general_functions.make_it_pure_black(Image.open(logo_file).convert('RGBA'))

        # 1. 初始化画布
        draw = ImageDraw.Draw(canvas)
        dpi = sku_config.dpi
        font_paths = self._load_fonts()

        # 2. 绘制底部黑色异形框 (带 S 弯逻辑)
        icon_company = general_functions.draw_dynamic_company_brand(
            sku_config, sku_config.company_name, sku_config.contact_info, font_paths, self.resources
        )
        safe_x_start = general_functions.draw_side_dynamic_bottom_bg_standard_move(canvas, sku_config, icon_company, font_paths)

        # 3. 绘制侧唛 Logo (右上角固定位置)
        # icon_side_logo = self.resources['icon_side_logo']

        icon_side_logo_resized = general_functions.scale_by_height(icon_side_logo, int(5 * dpi))
        icon_side_logo_w, icon_side_logo_h = icon_side_logo_resized.size
        icon_side_logo_x = canvas.width - icon_side_logo_w - int(3 * dpi)
        icon_side_logo_y = int(3 * dpi)

        canvas.paste(icon_side_logo_resized, (icon_side_logo_x, icon_side_logo_y), mask=icon_side_logo_resized)

        # --- 核心修改：动态组合 [海绵标 | FSC标 | 侧唛文本框] ---
        side_images = []
        table_h_px = int(8 * dpi)  # 固定高度 8cm
        gap_img = Image.new('RGBA', (int(0.3 * dpi), table_h_px), (0, 0, 0, 0))

        # A. 海绵认证标 (根据开关 show_sponge 判断)
        if getattr(sku_config, 'sponge_verified', False) == True:
            img_s_res = general_functions.scale_by_height(self.resources['icon_side_sponge'].copy(), table_h_px)
            side_images.append(img_s_res)

        # B. FSC 认证标 (根据开关 show_fsc 判断)
        if getattr(sku_config, 'show_fsc', False) == True:
            if side_images:
                side_images.append(gap_img)
            img_f_res = general_functions.scale_by_height(self.resources['icon_side_FSC'].copy(), table_h_px)
            side_images.append(img_f_res)

        # C. 侧唛文本框 (固定必有)
        if side_images:
            side_images.append(gap_img)
        raw_box = general_functions.scale_by_height(self.resources['icon_side_text_box'].copy(), table_h_px)
        filled_box = general_functions.fill_sidepanel_text_1(raw_box, sku_config, font_paths)
        side_images.append(filled_box)

        # --- 直接粘贴每个元素 ---
        target_x = int(3.0 * dpi)
        bottom_gb_h_px = int(sku_config.bottom_gb_h * dpi)
        target_y = canvas.height - bottom_gb_h_px - int(2.0 * dpi) - table_h_px
        current_x = target_x
        for img in side_images:
            paste_y = target_y + (table_h_px - img.height) // 2
            canvas.paste(img, (current_x, paste_y), mask=img if img.mode == 'RGBA' else None)
            current_x += img.width

        # --- 法律标动态放置逻辑 ---
        # res_base = self.base_dir / 'assets' / 'New-market' / '样式一' / '矢量文件'
        if getattr(sku_config, 'GE', 0) == 1:
            legal_icon = self.res_base / '法律标-2-1-GE.png'
        elif getattr(sku_config, 'FR', 0) == 1 or getattr(sku_config, 'UK', 0) == 1:
            legal_icon = self.res_base / '法律标-2-2-UK-FR.png'
        else:
            legal_icon = self.res_base / '法律标-2-2-UK-FR.png'

        self.resources['legal_icon_2_2'] = general_functions.make_it_pure_black(Image.open(legal_icon).convert('RGBA'))
        if show_legal and sku_config.legal_data:
            tw, th = canvas.size
            dpi = sku_config.dpi

            # 法律标宽度 22.4cm，距右边缘 4cm
            legal_box_w_px = int(22.4 * dpi)
            # 法律标框与侧唛右侧的距离暂定3cm
            right_margin_px = int(2.0 * dpi)

            # 计算法律标左边缘在画布上的真实 X 坐标
            target_x = tw - legal_box_w_px - right_margin_px

            # --- 核心判断：法律标左边缘 vs S弯结束点 ---
            # 我们预留 1.0cm 的物理缓冲空间
            buffer_px = int(1.0 * dpi)

            if target_x < (safe_x_start - 2 * buffer_px):
                # 如果法律标的左侧撞到了 S 弯平整段的起点
                # 说明 SKU 字符太长，S 弯被推向了右侧，此时法律标必须抬起
                target_y = th - int(12 * dpi) - int(14.0 * dpi)
            else:
                # 空间足够，法律标可以落在常规的 7cm 高度处
                target_y = th - int(7.0 * dpi) - int(14.0 * dpi)

            # 绘制法律标
            general_functions.draw_legal_label_component(
                canvas, target_x, target_y, sku_config,
                self.resources, self.fonts, sku_config.legal_data
            )

        return canvas

    def generate_side_up_down_panel(self, sku_config):

        # canvas = Image.new(sku_config.color_mode, (sku_config.h_px, sku_config.w_px), sku_config.background_color)
        canvas_side_up = Image.new(sku_config.color_mode, (sku_config.w_px, sku_config.half_w_px), sku_config.background_color)
        canvas_side_down = Image.new(sku_config.color_mode, (sku_config.w_px, sku_config.half_w_px), sku_config.background_color)
        return canvas_side_up, canvas_side_down

    # ── fpdf2 vector helper methods ─────────────────────────────────────────────

    def _get_logo_file(self, sku_config):
        """Return the front-panel logo path based on market flag (GE/FR/UK)."""
        if getattr(sku_config, 'GE', 0) == 1:
            return self.res_base / '正唛logo-ELEGUE.png'
        elif getattr(sku_config, 'FR', 0) == 1 or getattr(sku_config, 'UK', 0) == 1:
            return self.res_base / '正唛logo-MCombo.png'
        return self.res_base / '正唛logo-MCombo.png'

    def _generate_bottom_bar(self, sku_config):
        """Generate the bottom bar section of the front panel as a PIL image."""
        canvas = Image.new(sku_config.color_mode,
                           (sku_config.l_px, sku_config.h_px),
                           sku_config.background_color)
        icon_company = general_functions.draw_dynamic_company_brand(
            sku_config, sku_config.company_name, sku_config.contact_info,
            self.font_paths, self.resources)
        icon_box_number = self.resources[
            f"icon_box_number_{sku_config.box_number['current_box']}"]
        general_functions.draw_dynamic_bottom_bg_move(
            canvas, sku_config, icon_company, icon_box_number, self.font_paths)
        bottom_h_px = int(sku_config.bottom_gb_h * sku_config.dpi)
        return canvas.crop((0, canvas.height - bottom_h_px,
                            canvas.width, canvas.height))

    @staticmethod
    def _pil_bbox_mm(pil_font, text, ppi):
        """Measure text bbox using anchor='ls' and convert to mm.
        top is negative (above baseline), bottom is positive (below baseline)."""
        left, top, right, bottom = pil_font.getbbox(text, anchor='ls')
        px_per_mm = ppi / 25.4
        return left / px_per_mm, top / px_per_mm, right / px_per_mm, bottom / px_per_mm

    def _draw_text_top_left(self, pdf, x_mm, y_top_mm, text,
                             font_family, font_style, font_size_pt, pil_font, ppi,
                             color=(0, 0, 0)):
        """Draw text anchored at visual top-left (like PIL anchor='la')."""
        _, top_mm, _, _ = self._pil_bbox_mm(pil_font, text, ppi)
        baseline_y = y_top_mm + (-top_mm)
        r, g, b = color
        pdf.set_text_color(r, g, b)
        pdf.set_font(font_family, font_style, font_size_pt)
        pdf.text(x_mm, baseline_y, text)

    def _draw_text_top_center(self, pdf, x_center_mm, y_top_mm, text,
                               font_family, font_style, font_size_pt, pil_font, ppi,
                               color=(0, 0, 0)):
        """Draw text anchored at visual top-center (horizontally centered)."""
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
        """Draw text anchored at visual center (like PIL anchor='mm')."""
        left_mm, top_mm, right_mm, bottom_mm = self._pil_bbox_mm(pil_font, text, ppi)
        text_w_mm = right_mm - left_mm
        text_h_mm = bottom_mm - top_mm
        x_mm = x_center_mm - text_w_mm / 2.0
        baseline_y = y_center_mm + (-top_mm) - text_h_mm / 2.0
        r, g, b = color
        pdf.set_text_color(r, g, b)
        pdf.set_font(font_family, font_style, font_size_pt)
        pdf.text(x_mm, baseline_y, text)

    # ── vector panel drawing methods ────────────────────────────────────────────

    def _draw_front_panel_v(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm):
        """Draw the front panel with vector text and raster bottom bar."""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        # ── 1. Logo (centered top, h/3 height, max w/2 width) ──
        logo_file = self._get_logo_file(sku_config)
        icon_tm = general_functions.make_it_pure_black(
            Image.open(logo_file).convert('RGBA'))
        _tm_w, _tm_h = icon_tm.size

        tm_h_mm = h_mm / 3.0
        tm_w_mm = tm_h_mm * _tm_w / _tm_h
        max_tm_w = w_mm / 2.0
        if tm_w_mm > max_tm_w:
            tm_w_mm = max_tm_w
            tm_h_mm = tm_w_mm * _tm_h / _tm_w

        tm_x = x_mm + (w_mm - tm_w_mm) / 2.0
        tm_y = y_mm
        pdf.image(icon_tm, x=tm_x, y=tm_y, w=tm_w_mm, h=tm_h_mm)

        # ── 2. Bottom bar — fully vector ──
        bottom_h_mm = sku_config.bottom_gb_h * 10.0
        self._draw_bottom_bar_v(pdf, sku_config, x_mm, y_mm, w_mm, h_mm)

        # ── 3. Color text (right top, black rounded background) ──
        color_text = str(sku_config.color)
        color_size_px = int(h_mm * px_per_mm * self.font_ratios['color_font'])
        color_size_pt = color_size_px * 72.0 / ppi
        pil_color = ImageFont.truetype(self.font_paths['calibri_bold'],
                                       color_size_px)

        left_c, top_c, right_c, bottom_c = self._pil_bbox_mm(
            pil_color, color_text, ppi)
        text_w = right_c - left_c
        text_h = bottom_c - top_c

        color_x = x_mm + w_mm - text_w - 40.0   # 4cm from right
        color_y = y_mm + 40.0                     # 4cm from top

        pad_x_mm = 8.0             # 0.8cm
        pad_y_top_mm = 4.0 * 0.7   # match mcombo pattern
        pad_y_bot_mm = 4.0 * 1.4
        radius_mm = 16 * 25.4 / ppi

        rect_x = color_x - pad_x_mm
        rect_y = color_y - pad_y_top_mm
        rect_w = text_w + 2 * pad_x_mm
        rect_h = text_h + pad_y_top_mm + pad_y_bot_mm

        pdf.set_fill_color(0, 0, 0)
        pdf.rect(rect_x, rect_y, rect_w, rect_h,
                 style='F', round_corners=True, corner_radius=radius_mm)

        self._draw_text_top_left(pdf, color_x, color_y, color_text,
                                  'CalibriBold', '', color_size_pt, pil_color, ppi,
                                  color=(161, 142, 102))

        # ── 4. Product text (centered, dynamic size) ──
        product_text = sku_config.product
        product_size_px = int(h_mm * px_per_mm * self.font_ratios['product_font'])
        pil_product = ImageFont.truetype(self.font_paths['itc_demi'],
                                         product_size_px)

        p_left, p_top, p_right, p_bottom = pil_product.getbbox(product_text)
        product_w_px = p_right - p_left
        max_product_w_px = int(w_mm * px_per_mm * 0.85)
        if product_w_px > max_product_w_px:
            product_size_px = int(product_size_px * max_product_w_px / product_w_px)
            pil_product = ImageFont.truetype(self.font_paths['itc_demi'],
                                             product_size_px)
            p_left, p_top, p_right, p_bottom = pil_product.getbbox(product_text)
            product_w_px = p_right - p_left
        product_size_pt = product_size_px * 72.0 / ppi
        product_w_mm = product_w_px / px_per_mm

        # ── 5. Size text ──
        size_text = getattr(sku_config, 'size', None) or " "
        size_size_px = int(h_mm * px_per_mm * self.font_ratios['size_font'])
        size_size_pt = size_size_px * 72.0 / ppi
        pil_size = ImageFont.truetype(self.font_paths['calibri_bold'],
                                      size_size_px)

        # ── 6. Group layout: product + decorative line + size ──
        product_em_h_mm = product_size_px / px_per_mm   # em-square height
        size_em_h_mm = size_size_px / px_per_mm
        gap_mm = 10.0       # 1cm
        line_h_mm = 3.0     # 0.3cm
        line_w_mm = product_w_mm * 0.85
        product_offset_mm = 5.0   # 0.5cm up

        total_group_h = product_em_h_mm + line_h_mm + size_em_h_mm + gap_mm * 2
        logo_bottom = y_mm + tm_h_mm
        bottom_section_top = y_mm + h_mm - bottom_h_mm
        available_h = bottom_section_top - logo_bottom
        group_start_y = logo_bottom + (available_h - total_group_h) / 2.0

        # Product text (shifted up ~0.5cm, matching original offset)
        cx = x_mm + w_mm / 2.0
        self._draw_text_top_center(pdf, cx,
                                    group_start_y - product_offset_mm,
                                    product_text,
                                    'ITCDemi', '', product_size_pt,
                                    pil_product, ppi)

        # Decorative ellipse (black)
        line_y = group_start_y + product_em_h_mm + gap_mm
        line_x = cx - line_w_mm / 2.0
        pdf.set_fill_color(0, 0, 0)
        pdf.ellipse(line_x, line_y, line_w_mm, line_h_mm, style='F')

        # Size text
        size_y = line_y + line_h_mm + gap_mm
        self._draw_text_top_center(pdf, cx, size_y, size_text,
                                    'CalibriBold', '', size_size_pt,
                                    pil_size, ppi)

    def _draw_flap_left_v(self, pdf, sku_config,
                           x_mm, y_mm, w_mm, h_mm, rotate_180=False):
        """Draw left flap panel with icon (optionally rotated 180°)."""
        total_boxes = sku_config.box_number['total_boxes']
        icon = self.resources[f'icon_left_{total_boxes}_panel']

        target_h_mm = 100.0   # 10cm
        max_w_mm_limit = w_mm * 0.8
        icon_w = target_h_mm * icon.width / icon.height
        if icon_w > max_w_mm_limit:
            icon_w = max_w_mm_limit
            icon_h = icon_w * icon.height / icon.width
        else:
            icon_h = target_h_mm

        icon_to_use = icon.rotate(180, expand=True) if rotate_180 else icon
        ix = x_mm + (w_mm - icon_w) / 2.0
        iy = y_mm + (h_mm - icon_h) / 2.0
        pdf.image(icon_to_use, x=ix, y=iy, w=icon_w, h=icon_h)

    def _draw_flap_right_v(self, pdf, sku_config,
                            x_mm, y_mm, w_mm, h_mm, rotate_180=False):
        """Draw right flap panel with icon (optionally rotated 180°)."""
        total_boxes = sku_config.box_number['total_boxes']
        current_box = sku_config.box_number['current_box']
        icon = self.resources[f'icon_right_{total_boxes}-{current_box}_panel']

        target_h_mm = 90.0   # 9cm
        max_w_mm_limit = w_mm * 0.8
        icon_w = target_h_mm * icon.width / icon.height
        if icon_w > max_w_mm_limit:
            icon_w = max_w_mm_limit
            icon_h = icon_w * icon.height / icon.width
        else:
            icon_h = target_h_mm

        icon_to_use = icon.rotate(180, expand=True) if rotate_180 else icon
        ix = x_mm + (w_mm - icon_w) / 2.0
        iy = y_mm + (h_mm - icon_h) / 2.0
        pdf.image(icon_to_use, x=ix, y=iy, w=icon_w, h=icon_h)

    # ── fully-vector bottom bar (replaces _generate_bottom_bar raster) ─────────

    def _draw_bottom_bar_v(self, pdf, sku_config, x_mm, y_mm, panel_w_mm, panel_h_mm):
        """Draw the front-panel bottom bar entirely in fpdf2 (S-curve + vector text)."""
        import textwrap as _tw
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4

        h_right_mm = 100.0          # 10 cm — right HIGH block (contains SKU)
        h_left_mm  = 50.0           # 5 cm  — left LOW block
        icon_h_mm  = 16.0           # company brand height 1.6 cm
        sku_margin_mm  = 5.0        # 0.5 cm
        margin_1cm_mm  = 10.0       # 1 cm
        margin_4cm_mm  = 40.0       # 4 cm
        margin_10cm_mm = 100.0      # 10 cm (S-curve span)

        panel_bottom = y_mm + panel_h_mm

        # ── A. Company brand background + text placement ──────────────────────
        brand_bg, brand_texts = general_functions.draw_company_brand_for_pdf(
            sku_config, sku_config.company_name, sku_config.contact_info,
            self.font_paths, self.resources)
        brand_w_mm = brand_bg.width * icon_h_mm / brand_bg.height
        left_section_w_mm = margin_1cm_mm + brand_w_mm + margin_4cm_mm

        # ── B. SKU font size (mirrors draw_dynamic_bottom_bg_move) ────────────
        max_sku_h_mm  = h_right_mm * 0.8
        start_pt = 180
        start_px  = int(start_pt * ppi / 72)
        min_px    = int(max_sku_h_mm * px_per_mm * 0.15)
        sku_pil   = None
        sku_w_mm  = 0.0
        sku_size_pt = float(start_pt)

        current_px = start_px
        while current_px >= min_px:
            pf = ImageFont.truetype(self.font_paths['calibri_bold'], current_px)
            bb = pf.getbbox(sku_config.sku_name)
            sw_mm = (bb[2] - bb[0]) / px_per_mm
            sh_mm = (bb[3] - bb[1]) / px_per_mm
            if sw_mm <= (panel_w_mm - left_section_w_mm - 2 * sku_margin_mm) and sh_mm <= max_sku_h_mm:
                sku_pil      = pf
                sku_w_mm     = sw_mm
                sku_size_pt  = current_px * 72.0 / ppi
                break
            current_px -= 5
        if sku_pil is None:
            sku_pil     = ImageFont.truetype(self.font_paths['calibri_bold'], min_px)
            bb          = sku_pil.getbbox(sku_config.sku_name)
            sku_w_mm    = (bb[2] - bb[0]) / px_per_mm
            sku_size_pt = min_px * 72.0 / ppi

        # ── C. S-curve layout decision ────────────────────────────────────────
        sku_block_left_mm = panel_w_mm - sku_margin_mm - sku_w_mm - sku_margin_mm
        space_is_enough   = left_section_w_mm <= sku_block_left_mm

        if space_is_enough:
            x3_mm = left_section_w_mm - margin_10cm_mm
            x4_mm = left_section_w_mm
            brand_x_mm = x_mm + margin_1cm_mm
            brand_y_mm = panel_bottom - h_right_mm + (h_right_mm - h_left_mm) / 2.0 - icon_h_mm / 2.0
            sku_area_l = x_mm + x4_mm - 6 * sku_margin_mm
            sku_area_r = x_mm + panel_w_mm - sku_margin_mm
        else:
            x4_mm = max(left_section_w_mm, panel_w_mm - sku_margin_mm - sku_w_mm - sku_margin_mm)
            x3_mm = max(margin_1cm_mm, x4_mm - margin_10cm_mm)
            brand_x_mm = x_mm + margin_1cm_mm
            brand_y_mm = panel_bottom - h_left_mm / 2.0 - icon_h_mm / 2.0 - int(1.5 * 10)  # 1.5cm up
            sku_area_l = x_mm + x4_mm - 6 * sku_margin_mm
            sku_area_r = x_mm + panel_w_mm - sku_margin_mm

        abs_x3 = x_mm + x3_mm
        abs_x4 = x_mm + x4_mm
        y_left_top  = panel_bottom - h_left_mm
        y_right_top = panel_bottom - h_right_mm

        # ── D. Draw S-curve shapes ────────────────────────────────────────────
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(x_mm,   y_left_top,  x3_mm,              h_left_mm,  style='F')
        pdf.rect(abs_x4, y_right_top, panel_w_mm - x4_mm, h_right_mm, style='F')

        curve = []
        for i in range(21):
            t  = i / 20.0
            cx = abs_x3 + (abs_x4 - abs_x3) * t
            ts = t * t * (3 - 2 * t)
            cy = y_left_top + (y_right_top - y_left_top) * ts
            curve.append((cx, cy))
        curve.append((abs_x4, panel_bottom))
        curve.append((abs_x3, panel_bottom))
        pdf.polygon(curve, style='F')

        # ── E. Box-number icon (left block, vertically centred) ───────────────
        box_icon = self.resources[f"icon_box_number_{sku_config.box_number['current_box']}"]
        box_icon_h_mm = h_right_mm * 0.25          # 25 % of h_right = 25 mm
        box_icon_w_mm = box_icon_h_mm * box_icon.width / box_icon.height
        box_icon_x = x_mm + margin_1cm_mm
        box_icon_y = y_left_top + (h_left_mm - box_icon_h_mm) / 2.0
        pdf.image(box_icon, x=box_icon_x, y=box_icon_y, w=box_icon_w_mm, h=box_icon_h_mm)

        # ── F. Company brand background ───────────────────────────────────────
        pdf.image(brand_bg, x=brand_x_mm, y=brand_y_mm, w=brand_w_mm, h=icon_h_mm)

        # ── G. Company brand text (vector overlay) ────────────────────────────
        img_scale = icon_h_mm / brand_bg.height   # mm per pixel inside brand_bg
        for bt in brand_texts:
            fs_pt = bt['font_size_px'] * 72.0 / ppi
            pf    = ImageFont.truetype(bt['font_path'], bt['font_size_px'])
            txt_x = brand_x_mm + bt['x_px'] * img_scale
            txt_y = brand_y_mm + bt['y_px'] * img_scale
            self._draw_text_mid_center(pdf, txt_x, txt_y, bt['text'],
                                       'CalibriBold', '', fs_pt, pf, ppi,
                                       color=bt['color'])

        # ── H. SKU text (vector, right high block, mid-centre) ────────────────
        sku_cx = (sku_area_l + sku_area_r) / 2.0
        sku_cy = y_right_top + h_right_mm / 2.0 + 3.0   # +3 mm visual offset
        self._draw_text_mid_center(pdf, sku_cx, sku_cy, sku_config.sku_name,
                                   'CalibriBold', '', sku_size_pt, sku_pil, ppi,
                                   color=(161, 142, 102))

    # ── fully-vector side panel ──────────────────────────────────────────────

    def _draw_side_panel_v(self, pdf, sku_config, x_mm, y_mm, w_mm, h_mm,
                            show_legal, rotate_deg=0):
        """Draw the side panel entirely in fpdf2 vector text + images."""
        cx = x_mm + w_mm / 2.0
        cy = y_mm + h_mm / 2.0

        if rotate_deg == 90:
            # Vertical style: content is drawn on an effective (h_mm × w_mm) canvas
            # centred at (cx, cy), then displayed rotated 90° CCW in the PDF.
            o_x = cx - h_mm / 2.0
            o_y = cy - w_mm / 2.0
            eff_w, eff_h = h_mm, w_mm
            h_left_mm, logo_h_mm = 80.0, 40.0
        else:
            o_x, o_y = x_mm, y_mm
            eff_w, eff_h = w_mm, h_mm
            h_left_mm, logo_h_mm = 100.0, 50.0

        def _draw():
            self._draw_side_content_v(pdf, sku_config,
                                      o_x, o_y, eff_w, eff_h,
                                      show_legal, h_left_mm, logo_h_mm)

        if rotate_deg == 90:
            with pdf.rotation(angle=90, x=cx, y=cy):
                _draw()
        else:
            _draw()

    def _draw_side_content_v(self, pdf, sku_config,
                              o_x, o_y, eff_w, eff_h,
                              show_legal, h_left_mm, logo_h_mm):
        """Low-level side panel drawing in a given coordinate frame."""
        ppi        = sku_config.ppi
        px_per_mm  = ppi / 25.4
        dpi        = sku_config.dpi

        h_right_mm    = h_left_mm / 2.0
        sku_margin_mm = 5.0
        margin_10mm   = 100.0
        max_sku_h_mm  = h_left_mm * 0.8
        start_px      = int((180 if h_left_mm >= 100 else 160) * ppi / 72)
        min_px        = int(max_sku_h_mm * px_per_mm * 0.15)
        panel_bottom  = o_y + eff_h

        # ── 1. Determine SKU font size (mirror draw_side_dynamic_bottom_bg_*_move) ──
        sku_pil    = None
        sku_w_mm   = 0.0
        sku_size_pt = start_px * 72.0 / ppi
        max_sku_block_mm = eff_w - margin_10mm - 40.0   # canvas_w − 10 cm − 4 cm

        current_px = start_px
        while current_px >= min_px:
            pf   = ImageFont.truetype(self.font_paths['calibri_bold'], current_px)
            bb   = pf.getbbox(sku_config.sku_name)
            sw_mm = (bb[2] - bb[0]) / px_per_mm
            sh_mm = (bb[3] - bb[1]) / px_per_mm
            if sw_mm <= max_sku_block_mm - 2 * sku_margin_mm and sh_mm <= max_sku_h_mm:
                sku_pil    = pf
                sku_w_mm   = sw_mm
                sku_size_pt = current_px * 72.0 / ppi
                break
            current_px -= 5
        if sku_pil is None:
            sku_pil   = ImageFont.truetype(self.font_paths['calibri_bold'], min_px)
            bb        = sku_pil.getbbox(sku_config.sku_name)
            sku_w_mm  = (bb[2] - bb[0]) / px_per_mm
            sku_size_pt = min_px * 72.0 / ppi

        sku_block_w_mm = max(60.0, min(sku_w_mm + 2 * sku_margin_mm, max_sku_block_mm))
        x3_mm = sku_block_w_mm
        x4_mm = x3_mm + margin_10mm
        if x4_mm > eff_w - 10.0:
            x4_mm = eff_w - 10.0
            x3_mm = x4_mm - margin_10mm
            sku_block_w_mm = x3_mm

        abs_x3    = o_x + x3_mm
        abs_x4    = o_x + x4_mm
        y_left_top  = panel_bottom - h_left_mm
        y_right_top = panel_bottom - h_right_mm

        # ── 2. Draw S-curve bar ───────────────────────────────────────────────
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(o_x,    y_left_top,  x3_mm,           h_left_mm,  style='F')
        pdf.rect(abs_x4, y_right_top, eff_w - x4_mm,   h_right_mm, style='F')
        curve = []
        for i in range(21):
            t  = i / 20.0
            cx = abs_x3 + (abs_x4 - abs_x3) * t
            ts = t * t * (3 - 2 * t)
            cy = y_left_top + (y_right_top - y_left_top) * ts
            curve.append((cx, cy))
        curve.append((abs_x4, panel_bottom))
        curve.append((abs_x3, panel_bottom))
        pdf.polygon(curve, style='F')

        # ── 3. SKU text (left high block, mid-centre) ─────────────────────────
        sku_cx = o_x + sku_block_w_mm / 2.0 + sku_margin_mm * 3
        sku_cy = y_left_top + h_left_mm / 2.0 + 3.0
        self._draw_text_mid_center(pdf, sku_cx, sku_cy, sku_config.sku_name,
                                   'CalibriBold', '', sku_size_pt, sku_pil, ppi,
                                   color=(161, 142, 102))

        # ── 4. Side logo (top-right corner) ──────────────────────────────────
        logo_file = self._get_logo_file(sku_config)
        logo_img  = general_functions.make_it_pure_black(
            Image.open(logo_file).convert('RGBA'))
        logo_w_mm = logo_h_mm * logo_img.width / logo_img.height
        margin_side_mm = logo_h_mm * 0.6
        logo_x = o_x + eff_w - logo_w_mm - margin_side_mm
        logo_y = o_y + margin_side_mm
        pdf.image(logo_img, x=logo_x, y=logo_y, w=logo_w_mm, h=logo_h_mm)

        # ── 5. Side elements: [sponge?] [fsc?] [barcode box] ─────────────────
        table_h_mm      = 80.0   # 8 cm
        bottom_gb_h_mm  = sku_config.bottom_gb_h * 10.0
        # same y-offset formula as generate_side_panel (standard: -2cm, vertical: -1cm)
        gap_above_bar_mm = 20.0 if h_left_mm >= 100.0 else 10.0
        elem_y = panel_bottom - bottom_gb_h_mm - gap_above_bar_mm - table_h_mm
        gap_mm = 3.0   # 0.3 cm gap
        current_x = o_x + 30.0  # 3 cm from left

        def _embed_h(res_key):
            img = self.resources[res_key]
            w   = table_h_mm * img.width / img.height
            return img, w

        if getattr(sku_config, 'sponge_verified', False):
            sp_img, sp_w = _embed_h('icon_side_sponge')
            pdf.image(sp_img, x=current_x, y=elem_y, w=sp_w, h=table_h_mm)
            current_x += sp_w + gap_mm

        if getattr(sku_config, 'show_fsc', False):
            fs_img, fs_w = _embed_h('icon_side_FSC')
            pdf.image(fs_img, x=current_x, y=elem_y, w=fs_w, h=table_h_mm)
            current_x += fs_w + gap_mm

        raw_box  = self.resources['icon_side_text_box']
        box_w_mm = table_h_mm * raw_box.width / raw_box.height
        pdf.image(raw_box, x=current_x, y=elem_y, w=box_w_mm, h=table_h_mm)
        self._draw_barcode_box_v(pdf, sku_config,
                                 current_x, elem_y, box_w_mm, table_h_mm)

        # ── 6. Legal label ────────────────────────────────────────────────────
        if show_legal and getattr(sku_config, 'legal_data', None):
            if getattr(sku_config, 'GE', 0) == 1:
                legal_icon_file = self.res_base / '法律标-2-1-GE.png'
            else:
                legal_icon_file = self.res_base / '法律标-2-2-UK-FR.png'
            legal_icon_2_2 = general_functions.make_it_pure_black(
                Image.open(legal_icon_file).convert('RGBA'))

            legal_w_mm     = 224.0   # 22.4 cm
            right_margin_mm = 20.0   # 2 cm
            legal_x = o_x + eff_w - legal_w_mm - right_margin_mm

            buffer_mm = 10.0
            if legal_x < abs_x4 - 2 * buffer_mm:
                legal_y = panel_bottom - 120.0 - 140.0
            else:
                legal_y = panel_bottom - 70.0 - 140.0

            self._draw_legal_v(pdf, sku_config, legal_x, legal_y, legal_icon_2_2)

    def _draw_barcode_box_v(self, pdf, sku_config,
                             box_x, box_y, box_w_mm, box_h_mm):
        """Draw the side-panel barcode section as vector text + raster barcodes."""
        ppi       = sku_config.ppi
        px_per_mm = ppi / 25.4

        th = box_h_mm   # alias

        # Font sizes (same proportional ratios as fill_sidepanel_text_1)
        label_size_px   = int(th * px_per_mm * 0.081)
        bold_size_px    = int(th * px_per_mm * 0.095)
        barcode_txt_px  = int(th * px_per_mm * 0.058)

        label_size_pt   = label_size_px  * 72.0 / ppi
        bold_size_pt    = bold_size_px   * 72.0 / ppi
        barcode_txt_pt  = barcode_txt_px * 72.0 / ppi

        pil_label   = ImageFont.truetype(self.font_paths['side_font_label'],   label_size_px)
        pil_bold    = ImageFont.truetype(self.font_paths['side_font_bold'],    bold_size_px)
        pil_barcode = ImageFont.truetype(self.font_paths['side_font_barcode'], barcode_txt_px)

        # G.W./N.W. and BOX SIZE text
        gw  = sku_config.side_text.get('gw_value', '')
        nw  = sku_config.side_text.get('nw_value', '')
        l_in = getattr(sku_config, 'l_in', sku_config.l_cm / 2.54)
        w_in = getattr(sku_config, 'w_in', sku_config.w_cm / 2.54)
        h_in = getattr(sku_config, 'h_in', sku_config.h_cm / 2.54)
        gw_text  = f"G.W./N.W.: {gw} / {nw} lbs"
        dim_text = f"BOX SIZE: {l_in:.1f}'' x {w_in:.1f}'' x {h_in:.1f}''"

        text_x = box_x + box_w_mm * 0.55
        self._draw_text_top_left(pdf, text_x, box_y + th * 0.044,
                                  gw_text, 'ITCDemi', '', label_size_pt, pil_label, ppi)
        self._draw_text_top_left(pdf, text_x, box_y + th * 0.214,
                                  dim_text, 'ITCDemi', '', label_size_pt, pil_label, ppi)

        # Barcode images (still raster — barcode is inherently graphical)
        barcode_h_mm = th * 0.35
        barcode_h_px = int(barcode_h_mm * px_per_mm)
        barcode_y_mm = box_y + th * 0.42
        barcode_txt_y = box_y + th * 0.76

        sku_bc = general_functions.generate_barcode_image_1(
            sku_config.sku_name, height=barcode_h_px)
        sn_code = sku_config.side_text.get('sn_code', '')
        sn_bc   = general_functions.generate_barcode_image_1(
            sn_code, height=barcode_h_px) if sn_code else None

        total_bc_w = sku_bc.width + (sn_bc.width if sn_bc else sku_bc.width)
        line_frac  = sku_bc.width / total_bc_w if total_bc_w > 0 else 0.5
        line_x     = box_x + box_w_mm * line_frac

        # Vertical divider
        pdf.set_draw_color(0, 0, 0)
        lw_mm = 3.0 * 25.4 / ppi
        pdf.set_line_width(lw_mm)
        pdf.line(line_x, box_y + th * 0.36, line_x, box_y + th * 0.855)

        # SKU barcode
        sku_zone_w = line_x - box_x
        sku_bc_w   = sku_zone_w * 0.9
        sku_bc_img = sku_bc.resize(
            (int(sku_bc_w * px_per_mm), barcode_h_px), Image.Resampling.LANCZOS)
        sku_bc_x = box_x + (sku_zone_w - sku_bc_w) / 2
        pdf.image(sku_bc_img, x=sku_bc_x, y=barcode_y_mm,
                  w=sku_bc_w, h=barcode_h_mm)
        self._draw_text_top_center(
            pdf, sku_bc_x + sku_bc_w / 2, barcode_txt_y,
            sku_config.sku_name, 'CalibriBold', '', barcode_txt_pt, pil_barcode, ppi)

        # SN barcode
        if sn_bc and sn_code:
            sn_zone_w = box_x + box_w_mm - line_x
            sn_bc_w   = sn_zone_w * 0.9
            sn_bc_img = sn_bc.resize(
                (int(sn_bc_w * px_per_mm), barcode_h_px), Image.Resampling.LANCZOS)
            sn_bc_x = line_x + (sn_zone_w - sn_bc_w) / 2
            pdf.image(sn_bc_img, x=sn_bc_x, y=barcode_y_mm,
                      w=sn_bc_w, h=barcode_h_mm)
            self._draw_text_top_center(
                pdf, sn_bc_x + sn_bc_w / 2, barcode_txt_y,
                sn_code, 'CalibriBold', '', barcode_txt_pt, pil_barcode, ppi)

        # MADE IN CHINA
        made_y = box_y + th * 0.885
        self._draw_text_top_center(
            pdf, box_x + box_w_mm / 2, made_y,
            'MADE IN CHINA', 'CalibriBold', '', bold_size_pt, pil_bold, ppi)

    def _draw_legal_v(self, pdf, sku_config, x_mm, y_mm, legal_icon_2_2):
        """Draw the legal label component entirely in fpdf2 (box, lines, icons, text)."""
        ppi = sku_config.ppi

        box_w_mm = 224.0   # 22.4 cm
        box_h_mm = 140.0   # 14.0 cm
        row1_h   = 57.0    # 5.7 cm
        row2_h   = 20.0    # 2.0 cm
        row3_h   = 63.0    # 6.3 cm

        lw_thin  = 3.0 * 25.4 / ppi   # ~0.25 mm  (3 px at 300 dpi)
        lw_thick = 4.0 * 25.4 / ppi   # ~0.34 mm  (4 px)

        pdf.set_draw_color(0, 0, 0)

        # Outer box
        pdf.set_line_width(lw_thick)
        pdf.rect(x_mm, y_mm, box_w_mm, box_h_mm, style='D')

        # Horizontal dividers
        pdf.set_line_width(lw_thin)
        pdf.line(x_mm, y_mm + row1_h, x_mm + box_w_mm, y_mm + row1_h)
        pdf.line(x_mm, y_mm + row1_h + row2_h,
                 x_mm + box_w_mm, y_mm + row1_h + row2_h)

        # ── Row 1: legal text (left) + icon (right) ───────────────────────────
        scale_r1 = 0.85
        if getattr(sku_config, 'GE', 0) == 1:
            scale_r1 = scale_r1 / 2 - 0.15
        icon_r1_h = row1_h * scale_r1
        icon_r1_w = icon_r1_h * legal_icon_2_2.width / legal_icon_2_2.height

        margin_right_mm = 8.0    # 0.8 cm
        gap_mm          = 10.0   # 1.0 cm
        v_line_x_rel    = box_w_mm - margin_right_mm - icon_r1_w - gap_mm / 2
        abs_v_line_x    = x_mm + v_line_x_rel

        # Vertical divider in row 1
        pdf.set_line_width(lw_thin)
        pdf.line(abs_v_line_x, y_mm, abs_v_line_x, y_mm + row1_h)

        icon_r1_x = x_mm + box_w_mm - margin_right_mm - icon_r1_w
        icon_r1_y = y_mm + (row1_h - icon_r1_h) / 2
        pdf.image(legal_icon_2_2, x=icon_r1_x, y=icon_r1_y, w=icon_r1_w, h=icon_r1_h)

        # Legal text in row1 left area
        text_area_w = v_line_x_rel - gap_mm / 2
        if sku_config.legal_data:
            self._draw_legal_text_v(pdf, sku_config,
                                    x_mm + 7.5, y_mm, text_area_w, row1_h)

        # ── Row 2: certification icons (centred) ──────────────────────────────
        row2_icons = []
        icon_3_1 = self.resources['legal_icon_3_1']
        i31_h = row2_h * 0.85
        i31_w = i31_h * icon_3_1.width / icon_3_1.height
        row2_icons.append((icon_3_1, i31_w, i31_h))

        check_list = [
            (getattr(sku_config, 'legal_3_2', 0), 'legal_icon_3_2'),
            (getattr(sku_config, 'legal_3_3', 0), 'legal_icon_3_3'),
            (getattr(sku_config, 'legal_3_4', 0), 'legal_icon_3_4'),
            (getattr(sku_config, 'legal_3_5', 0), 'legal_icon_3_5'),
            (getattr(sku_config, 'legal_3_6', 0), 'legal_icon_3_6'),
        ]
        for is_on, key in check_list:
            if is_on == 1:
                img = self.resources[key]
                ih  = row2_h * 0.4
                iw  = ih * img.width / img.height
                row2_icons.append((img, iw, ih))

        icon_gap_mm = 7.0
        total_w = (sum(iw for _, iw, _ in row2_icons)
                   + icon_gap_mm * (len(row2_icons) - 1))
        cur_x = x_mm + (box_w_mm - total_w) / 2
        row2_y = y_mm + row1_h
        for img, iw, ih in row2_icons:
            iy = row2_y + (row2_h - ih) / 2
            pdf.image(img, x=cur_x, y=iy, w=iw, h=ih)
            cur_x += iw + icon_gap_mm

        # ── Row 3: large bottom icon (centred) ────────────────────────────────
        icon_4  = self.resources['legal_icon_4']
        i4_h    = row3_h * 0.85
        i4_w    = i4_h * icon_4.width / icon_4.height
        row3_y  = y_mm + row1_h + row2_h
        pdf.image(icon_4,
                  x=x_mm + (box_w_mm - i4_w) / 2,
                  y=row3_y + (row3_h - i4_h) / 2,
                  w=i4_w, h=i4_h)

    def _draw_legal_text_v(self, pdf, sku_config, x_mm, y_mm,
                            area_w_mm, area_h_mm):
        """Render legal key-value data as bold label + regular value in fpdf2."""
        import textwrap as _tw
        ppi       = sku_config.ppi
        px_per_mm = ppi / 25.4

        # Same base sizes as LegalTextGroup (28 px at 300 dpi ≈ 6.7 pt)
        base_px   = 28
        line_ratio = 1.3

        reg_path  = self.font_paths['calibri']
        bold_path = self.font_paths['calibri_bold']

        def _build_lines(size_px):
            pil_r  = ImageFont.truetype(reg_path,  size_px)
            pil_b  = ImageFont.truetype(bold_path, size_px)
            avg_cw = pil_r.getlength('a') / px_per_mm
            pad_l  = 30.0 / px_per_mm        # 30 px → mm (left padding)
            pad_r  = 35.0 / px_per_mm
            avail  = area_w_mm - pad_l - pad_r
            climit = max(1, int(avail / avg_cw))
            lines  = []
            for label, value in sku_config.legal_data.items():
                full_label = f'{label}: '
                lbl_w_mm   = pil_b.getlength(full_label) / px_per_mm
                wrapped    = _tw.wrap(full_label + str(value), width=climit)
                for i, ln in enumerate(wrapped):
                    lines.append(dict(
                        text=ln, is_first=(i == 0),
                        label=full_label if i == 0 else '',
                        lbl_w=lbl_w_mm   if i == 0 else 0.0,
                    ))
            return lines, size_px, pad_l

        # Auto-shrink until lines fit
        cur_px = base_px
        while cur_px > 12:
            lines, cur_px, pad_l = _build_lines(cur_px)
            line_h = cur_px * line_ratio / px_per_mm
            if len(lines) * line_h <= (area_h_mm - 5.0):
                break
            cur_px -= 2

        lines, cur_px, pad_l = _build_lines(cur_px)
        line_h   = cur_px * line_ratio / px_per_mm
        size_pt  = cur_px * 72.0 / ppi
        pil_r    = ImageFont.truetype(reg_path,  cur_px)
        pil_b    = ImageFont.truetype(bold_path, cur_px)

        total_h   = len(lines) * line_h
        extra_y   = 0.2 * 25.4     # ~0.2 cm downward offset (matches LegalTextGroup)
        curr_y    = y_mm + (area_h_mm - total_h) / 2 + extra_y
        curr_x    = x_mm + pad_l

        for ln in lines:
            if ln['is_first'] and ln['label']:
                self._draw_text_top_left(pdf, curr_x, curr_y, ln['label'],
                                         'CalibriBold', '', size_pt, pil_b, ppi)
                content = ln['text'][len(ln['label']):]
                if content:
                    self._draw_text_top_left(pdf, curr_x + ln['lbl_w'], curr_y,
                                             content, 'Calibri', '', size_pt, pil_r, ppi)
            else:
                self._draw_text_top_left(pdf, curr_x, curr_y, ln['text'],
                                         'Calibri', '', size_pt, pil_r, ppi)
            curr_y += line_h