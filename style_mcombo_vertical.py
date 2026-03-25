# -*- coding: utf-8 -*-
"""
MCombo 标准样式 - 将原有的 BoxMarkEngine 转换为样式类
"""
from PIL import Image, ImageDraw, ImageFont
import pathlib as Path
from style_base import BoxMarkStyle, StyleRegistry
import general_functions


@StyleRegistry.register
class MComboStandardStyle(BoxMarkStyle):
    """MCombo 标准箱唛样式（原始样式）"""

    def get_style_name(self):
        return "mcombo_vertical"

    def get_style_description(self):
        return "MCombo 第二箱三箱 箱唛样式 "

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
            "panel_side1": "side",
            "panel_front2": "front",
            "panel_side2": "side",
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
        canvas_side = self.generate_side_panel(sku_config)
        canvas_side_up, canvas_side_down = self.generate_side_up_down_panel(sku_config)

        return {
            "left_up": canvas_left_up,
            "left_down": canvas_left_down,
            "right_up": canvas_right_up,
            "right_down": canvas_right_down,
            "front": canvas_front,
            "side": canvas_side,
            "side_up": canvas_side_up,
            "side_down": canvas_side_down
        }

    def _load_resources(self):
        """加载 MCombo 标准样式的图片资源"""
        res_base = self.base_dir / 'assets' / 'Mcombo' / '样式一' / '矢量文件'
        self.resources = {
            'icon_left_2_panel': Image.open(res_base / '顶部-左-2箱.png').convert('RGBA'),
            'icon_left_3_panel': Image.open(res_base / '顶部-左-3箱.png').convert('RGBA'),
            'icon_right_2-1_panel': Image.open(res_base / '顶部-右-2-1.png').convert('RGBA'),
            'icon_right_2-2_panel': Image.open(res_base / '顶部-右-2-2.png').convert('RGBA'),
            'icon_right_3-1_panel': Image.open(res_base / '顶部-右-3-1.png').convert('RGBA'),
            'icon_right_3-2_panel': Image.open(res_base / '顶部-右-3-2.png').convert('RGBA'),
            'icon_right_3-3_panel': Image.open(res_base / '顶部-右-3-3.png').convert('RGBA'),
            # 'icon_top_box_number_2_2': Image.open(res_base / '顶部-box-2-2.png').convert('RGBA'),
            'icon_top_box_number_3_2': Image.open(res_base / '顶部-box-3-2.png').convert('RGBA'),
            'icon_top_box_number_3_3': Image.open(res_base / '顶部-box-3-3.png').convert('RGBA'),
            'icon_trademark': Image.open(res_base / '正唛logo.png').convert('RGBA'),
            'icon_company': Image.open(res_base / '正唛公司信息.png').convert('RGBA'),
            'icon_box_number_1': Image.open(res_base / '正唛 Box 1.png').convert('RGBA'),
            'icon_box_number_2': Image.open(res_base / '正唛 Box 2.png').convert('RGBA'),
            'icon_box_number_3': Image.open(res_base / '正唛 Box 3.png').convert('RGBA'),
            'icon_side_label_box': Image.open(res_base / '侧唛标签框.png').convert('RGBA'),
            'icon_side_logo': Image.open(res_base / '侧唛logo.png').convert('RGBA'),
            'icon_side_text_box': Image.open(res_base / '侧唛文本框.png').convert('RGBA'),
            'icon_side_sponge': Image.open(res_base / '海绵认证.png').convert('RGBA')
        }

    def _load_fonts(self):
        """加载字体路径"""
        font_base = self.base_dir / 'assets' / 'Mcombo' / '样式一' / '箱唛字体'
        self.font_paths = {
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
            )
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

        # 计算图标的目标高度（厘米）
        target_height_cm = 18  # 默认高度18cm
        max_width_cm = sku_config.l_px * 0.8 / sku_config.dpi  # 面板长度的85%转换为cm
        
        # 获取原始尺寸（像素），计算按高度18cm缩放后的宽度（厘米）
        icon_w_px, icon_h_px = icon_left_panel.size
        scaled_width_cm = icon_w_px / icon_h_px * target_height_cm  # 宽高比 × 目标高度
        print(f"左侧面板原始宽度: {scaled_width_cm:.2f}cm ")
        # 如果按18cm高度缩放后，宽度超过面板长度的85%，则改用宽度限制
        if scaled_width_cm > max_width_cm:
            canvas_left_up = general_functions.paste_center_with_width(
                canvas_left_up, icon_left_up_panel, width_cm=max_width_cm, dpi=sku_config.dpi)
        else:
            # 宽度没超过限制，按18cm高度缩放
            canvas_left_up = general_functions.paste_center_with_height(
                canvas_left_up, icon_left_up_panel, height_cm=target_height_cm, dpi=sku_config.dpi)



        # canvas_left_up = general_functions.paste_center_with_height(
        #     canvas_left_up, icon_left_up_panel, height_cm=18, dpi=sku_config.dpi)
        # canvas_left_down = general_functions.paste_center_with_height(
        #     canvas_left_down, icon_left_down_panel, height_cm=10, dpi=sku_config.dpi)

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

        target_height_cm = 18  # 默认高度18cm
        max_width_cm = sku_config.l_px * 0.8 / sku_config.dpi  # 面板长度的85%转换为cm
        
        # 获取原始尺寸（像素），计算按高度18cm缩放后的宽度（厘米）
        icon_w_px, icon_h_px = icon_right_panel_down.size
        scaled_width_cm = icon_w_px / icon_h_px * target_height_cm  # 宽高比 × 目标高度
        
        # 如果按18cm高度缩放后，宽度超过面板长度的85%，则改用宽度限制
        if scaled_width_cm > max_width_cm:
            # canvas_right_up = general_functions.paste_center_with_width(
            #     canvas_right_up, icon_right_panel_down, width_cm=max_width_cm, dpi=sku_config.dpi)
            canvas_right_down = general_functions.paste_center_with_width(
                canvas_right_down, icon_right_panel_down, width_cm=max_width_cm, dpi=sku_config.dpi)
        else:
            # 宽度没超过限制，按18cm高度缩放
            # canvas_right_up = general_functions.paste_center_with_height(
            #     canvas_right_up, icon_right_panel_up, height_cm=target_height_cm, dpi=sku_config.dpi)
            canvas_right_down = general_functions.paste_center_with_height(
                canvas_right_down, icon_right_panel_down, height_cm=target_height_cm, dpi=sku_config.dpi)


        # canvas_right_up = general_functions.paste_center_with_height(
        #     canvas_right_up, icon_right_panel_up, height_cm=9, dpi=sku_config.dpi)
        # canvas_right_down = general_functions.paste_center_with_height(
        #     canvas_right_down, icon_right_panel_down, height_cm=17, dpi=sku_config.dpi)

        return canvas_right_up, canvas_right_down

    def generate_front_panel(self, sku_config):
        """生成正面面板"""
        canvas = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.h_px), sku_config.background_color)
        icon_trademark = self.resources['icon_trademark']

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

        icon_trademark_target_w, icon_trademark_target_h = icon_trademark_resized.size
        paste_x = (canvas_w - icon_trademark_target_w) // 2
        paste_y = 0
        canvas.paste(icon_trademark_resized, (paste_x, paste_y), mask=icon_trademark_resized)

        draw = ImageDraw.Draw(canvas)
        bottom_bg_h = int(sku_config.bottom_gb_h * sku_config.dpi)

        # 生成底部黑色底框和动态SKU文本
        icon_company = self.resources['icon_company']
        icon_box_number = self.resources[f"icon_box_number_{sku_config.box_number['current_box']}"]
        general_functions.draw_dynamic_bottom_bg(canvas, sku_config, icon_company, icon_box_number, self.font_paths)

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
        # size_y = line_y_top + gap_px + line_height
        size_y = line_y_top + gap_px + line_height + int(0.5 * sku_config.dpi)  # 尺寸信息下移约 0.5cm
        draw.text((size_x, size_y), size_text, font=size_font, fill=(0, 0, 0))

        return canvas

    def generate_side_panel(self, sku_config):
        """生成侧面面板"""

        canvas = Image.new(sku_config.color_mode, (sku_config.h_px, sku_config.w_px), sku_config.background_color)
        self.bottom_gb_h_px1 = int(8 * sku_config.dpi)


        general_functions.draw_side_dynamic_bottom_bg_vertical(
            canvas, sku_config, self.resources['icon_company'], self.font_paths)

        # 放置侧唛标签框
        icon_side_label_box = self.resources['icon_side_label_box']
        icon_side_label_box_resized = general_functions.scale_by_height(
            icon_side_label_box, int(5 * sku_config.dpi))
        icon_side_label_box_x, icon_side_label_box_y = int(3 * sku_config.dpi), int(4 * sku_config.dpi)
        canvas.paste(icon_side_label_box_resized, (icon_side_label_box_x, icon_side_label_box_y),
                     mask=icon_side_label_box_resized)

        # 放置侧唛 logo
        icon_side_logo = self.resources['icon_side_logo']
        side_logo_height = int(4 * sku_config.dpi)  # 修正拼写：heigft → height
        # logo宽度不能超过 (侧唛宽度 - 8cm) 的一半
        max_side_logo_width = int((sku_config.h_px - 8 * sku_config.dpi) * 0.5)
        # 先按高度5cm缩放
        icon_side_logo_resized = general_functions.scale_by_height(icon_side_logo, side_logo_height)
        icon_side_logo_w, icon_side_logo_h = icon_side_logo_resized.size
        # 如果按高度缩放后，宽度超过限制，则按宽度限制重新缩放
        if icon_side_logo_w > max_side_logo_width:
            icon_side_logo_resized = general_functions.scale_by_width(icon_side_logo, max_side_logo_width)
            icon_side_logo_w, icon_side_logo_h = icon_side_logo_resized.size
        icon_side_logo_x = canvas.width - icon_side_logo_w - int(4 * sku_config.dpi)
        icon_side_logo_y = int(4 * sku_config.dpi)
        canvas.paste(icon_side_logo_resized, (icon_side_logo_x, icon_side_logo_y), mask=icon_side_logo_resized)

        # 放置侧唛文字信息框
        icon_side_text_box_spacing_left = int(2.81 * sku_config.dpi)
        icon_side_text_box_spacing_bottom = int(1 * sku_config.dpi)

        table_height_px = int(8 * sku_config.dpi)

        base_x = icon_side_text_box_spacing_left

        base_y = canvas.height - self.bottom_gb_h_px1 - icon_side_text_box_spacing_bottom - table_height_px


        icon_side_text_box = self.resources['icon_side_text_box'].copy()
        icon_side_text_box_resized = general_functions.scale_by_height(icon_side_text_box, table_height_px)

        if sku_config.sponge_verified:
            icon_side_sponge = self.resources['icon_side_sponge'].copy()
            icon_side_sponge_resized = general_functions.scale_by_height(icon_side_sponge, table_height_px)
            canvas.paste(icon_side_sponge_resized, (base_x, base_y), mask=icon_side_sponge_resized)

            base_x += icon_side_sponge_resized.size[0] + int(0.1 * sku_config.dpi)
            fill_image = general_functions.fill_sidepanel_text(
                icon_side_text_box_resized, sku_config, self.font_paths)
            canvas.paste(fill_image, (base_x, base_y), mask=icon_side_text_box_resized)
        else:
            base_x = icon_side_text_box_spacing_left
            base_y = canvas.height - sku_config.bottom_gb_h_px - icon_side_text_box_spacing_bottom - \
                     icon_side_text_box_resized.size[1]

            fill_image = general_functions.fill_sidepanel_text(
                icon_side_text_box_resized, sku_config, self.font_paths)
            canvas.paste(fill_image, (base_x, base_y), mask=icon_side_text_box_resized)

        canvas = canvas.rotate(90, expand=True)
        return canvas

    def generate_side_up_down_panel(self, sku_config):

        # canvas = Image.new(sku_config.color_mode, (sku_config.h_px, sku_config.w_px), sku_config.background_color)
        canvas_side_up = Image.new(sku_config.color_mode, (sku_config.w_px, sku_config.half_w_px), sku_config.background_color)
        canvas_side_down = Image.new(sku_config.color_mode, (sku_config.w_px, sku_config.half_w_px), sku_config.background_color)
        return canvas_side_up, canvas_side_down