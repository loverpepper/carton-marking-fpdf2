# -*- coding: utf-8 -*-
"""
MCombo 标准样式 - 将原有的 BoxMarkEngine 转换为样式类
"""
from PIL import Image, ImageDraw, ImageFont
import pathlib as Path
from style_base import BoxMarkStyle, StyleRegistry
import general_functions
from layout_engine import Element, Row, Image as ImageElement

@StyleRegistry.register
class MComboStandardStyle(BoxMarkStyle):
    """MCombo 标准箱唛样式（原始样式）"""

    def get_style_name(self):
        return "new_market_vertical"

    def get_style_description(self):
        return "new_market 侧唛垂直箱唛样式"

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

        # 2. 根据开关判断布局逻辑

        # --- 【立起来模式】坐标逻辑 ---
        # Y轴节点
        y0 = 0  # 顶盖顶部
        y1 = sku_config.half_w_px  # 部分顶盖的起始点
        y2 = sku_config.w_px  # 正身顶部 (大图占用了 w_px)
        y3 = sku_config.w_px + sku_config.h_px  # 底盖顶部

        # 返回立起来的字典结构
        return {
            # 第一行：顶盖层
            "flap_top_front1": (x0, y0, sku_config.l_px, sku_config.w_px),  # 大图盖子
            "flap_top_side1": (x1, y1, sku_config.w_px, sku_config.half_w_px),
            "flap_top_front2": (x2, y1, sku_config.l_px, sku_config.half_w_px),
            "flap_top_side2": (x3, y1, sku_config.w_px, sku_config.half_w_px),

            # 第二行：正身层
            "panel_front1": (x0, y2, sku_config.l_px, sku_config.h_px),
            "panel_side1": (x1, y2, sku_config.w_px, sku_config.h_px),
            "panel_front2": (x2, y2, sku_config.l_px, sku_config.h_px),
            "panel_side2": (x3, y2, sku_config.w_px, sku_config.h_px),

            # 第三行：底盖层
            "flap_btm_front1": (x0, y3, sku_config.l_px, sku_config.half_w_px),
            "flap_btm_side1": (x1, y3, sku_config.w_px, sku_config.half_w_px),
            "flap_btm_front2": (x2, y3, sku_config.l_px, sku_config.w_px),  # 大图盖子
            "flap_btm_side2": (x3, y3, sku_config.w_px, sku_config.half_w_px),
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
            'calibri_bold': str(font_base / 'calibri_blod.ttf'),
            'itc_demi': str(font_base / 'ITC Avant Garde Gothic LT Demi.ttf'),
            'courier': str(font_base / 'cour.ttf'),
            'side_font_label': str(font_base / 'ITC Avant Garde Gothic LT Demi.ttf'),
            'side_font_bold': str(font_base / 'calibri_blod.ttf'),
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
        canvas_left_up = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.w_px),
                                   sku_config.background_color)
        canvas_left_down = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.half_w_px),
                                     sku_config.background_color)

        total_box_number = sku_config.box_number['total_boxes']
        current_box_number = sku_config.box_number['current_box']
        icon_left_panel = self.resources[f'icon_top_box_number_{total_box_number}_{current_box_number}']

        icon_left_up_panel = icon_left_panel
        # icon_left_down_panel = icon_left_panel.rotate(180, expand=True)

        canvas_left_up = general_functions.paste_center_with_height(
            canvas_left_up, icon_left_up_panel, height_cm=18, dpi=sku_config.dpi)

        return canvas_left_up, canvas_left_down

    def generate_right_panel(self, sku_config):
        """生成右侧面板"""
        canvas_right_up = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.half_w_px),
                                    sku_config.background_color)
        canvas_right_down = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.w_px),
                                      sku_config.background_color)

        total_box_number = sku_config.box_number['total_boxes']
        current_box_number = sku_config.box_number['current_box']
        icon_left_panel = self.resources[f'icon_top_box_number_{total_box_number}_{current_box_number}']

        icon_right_panel_down = icon_left_panel.rotate(180, expand=True)

        canvas_right_down = general_functions.paste_center_with_height(
            canvas_right_down, icon_right_panel_down, height_cm=17, dpi=sku_config.dpi)

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

        canvas = Image.new(sku_config.color_mode, (sku_config.h_px, sku_config.w_px), sku_config.background_color)
        self.bottom_gb_h_px1 = int(8 * sku_config.dpi)

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
        safe_x_start = general_functions.draw_side_dynamic_bottom_bg_vertical_move(canvas, sku_config, icon_company, font_paths)

        # 3. 绘制侧唛 Logo (右上角固定位置)
        # icon_side_logo = self.resources['icon_side_logo']

        icon_side_logo_resized = general_functions.scale_by_height(icon_side_logo, int(4 * dpi))
        icon_side_logo_w, icon_side_logo_h = icon_side_logo_resized.size
        icon_side_logo_x = canvas.width - icon_side_logo_w - int(2 * dpi)
        icon_side_logo_y = int(2 * dpi)

        canvas.paste(icon_side_logo_resized, (icon_side_logo_x, icon_side_logo_y), mask=icon_side_logo_resized)

        # --- 核心修改：动态组合 [海绵标 | FSC标 | 侧唛文本框] ---
        side_elements = []
        table_h_px = int(8 * dpi)  # 固定高度 8cm
        gap_px = int(0.3 * dpi)  # 组件之间的间距 0.6cm

        # A. 海绵认证标 (根据开关 sponge_verified 判断)
        if getattr(sku_config, 'sponge_verified', False) == True:
            img_sponge = self.resources['icon_side_sponge'].copy()
            img_s_res = general_functions.scale_by_height(img_sponge, table_h_px)
            side_elements.append(ImageElement(image=img_s_res, width=img_s_res.width, height=table_h_px))

        # B. FSC 认证标 (根据开关 show_fsc 判断)
        if getattr(sku_config, 'show_fsc', False) == True:
            # 如果前面已经有海绵标了，先加一个间距占位
            if side_elements:
                side_elements.append(
                    ImageElement(image=Image.new('RGBA', (gap_px, table_h_px), (0, 0, 0, 0)), width=gap_px,
                                 height=table_h_px))
            img_fsc = self.resources['icon_side_FSC'].copy()
            img_f_res = general_functions.scale_by_height(img_fsc, table_h_px)
            side_elements.append(ImageElement(image=img_f_res, width=img_f_res.width, height=table_h_px))

        # C. 侧唛文本框 (固定必有)
        # 如果前面有任何标，加一个间距
        if side_elements:
            side_elements.append(ImageElement(image=Image.new('RGBA', (gap_px, table_h_px), (0, 0, 0, 0)), width=gap_px,
                                              height=table_h_px))

        raw_box = self.resources['icon_side_text_box'].copy()
        raw_box_res = general_functions.scale_by_height(raw_box, table_h_px)
        # 调用装饰函数：在文本框内画字、画条形码、画自适应黑线
        filled_box = general_functions.fill_sidepanel_text_1(raw_box_res, sku_config, font_paths)
        side_elements.append(ImageElement(image=filled_box, width=filled_box.width, height=table_h_px))

        # --- 布局与渲染 ---
        # 1. 创建 Row 容器将所有开启的组件横向排列
        content_row = Row(children=side_elements, align='center')

        # 2. 设置位置：距离最左侧 3cm
        target_x = int(3.0 * dpi)
        # 3. 设置高度：距离黑色底框顶部 2cm
        bottom_gb_h_px = int(sku_config.bottom_gb_h * dpi)
        target_y = canvas.height - self.bottom_gb_h_px1 - int(1.0 * dpi) - table_h_px

        # 4. 执行布局计算和绘图渲染 (这是显示出来的关键)
        content_row.layout(target_x, target_y)
        content_row.render(draw)

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
                target_y = th - int(9.0 * dpi) - int(14.0 * dpi)
            else:
                # 空间足够，法律标可以落在常规的 7cm 高度处
                target_y = th - int(5.0 * dpi) - int(14.0 * dpi)

            # 绘制法律标
            general_functions.draw_legal_label_component(
                canvas, target_x, target_y, sku_config,
                self.resources, self.fonts, sku_config.legal_data
            )

        canvas = canvas.rotate(90, expand=True)
        return canvas

    def generate_side_up_down_panel(self, sku_config):

        # canvas = Image.new(sku_config.color_mode, (sku_config.h_px, sku_config.w_px), sku_config.background_color)
        canvas_side_up = Image.new(sku_config.color_mode, (sku_config.w_px, sku_config.half_w_px), sku_config.background_color)
        canvas_side_down = Image.new(sku_config.color_mode, (sku_config.w_px, sku_config.half_w_px), sku_config.background_color)
        return canvas_side_up, canvas_side_down