# -*- coding: utf-8 -*-
"""
Barberpub 对开盖样式 - 将原有的 BoxMarkEngine 转换为样式类
"""
from PIL import Image, ImageDraw, ImageFont
import pathlib as Path
from style_base import BoxMarkStyle, StyleRegistry
import general_functions


@StyleRegistry.register
class BarberpubDoubleOpeningStyle(BoxMarkStyle):
    '''Barberpub 对开盖样式'''
    
    def get_style_name(self):
        return "barberpub_doubleopening"
    
    def get_style_description(self):
        return "Barberpub 对开盖箱唛样式"
    
    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'ppi', 'color', 'product', 'side_text', 'sku_name', 'box_number', 'img_line_drawing']
    
    def get_layout_config(self, sku_config):
        '''
        Barberpub 对开盖样式 - 5块布局（4列3行）
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
        
    def generate_all_panels(self, sku_config):
        """生成 Barberpub 对开盖样式需要的所有面板"""
        
        canvas_front = self.generate_barberpub_front_panel(sku_config)
        canvas_side = self.generate_barberpub_side_panel(sku_config)
        canvas_left_up, canvas_left_down = self.generate_barberpub_left_panel(sku_config)
        canvas_right_up, canvas_right_down = self.generate_barberpub_right_panel(sku_config)
        canvas_blank = Image.new(sku_config.color_mode, (sku_config.w_px, sku_config.half_w_px), sku_config.background_color)


        return {
            "left_up": canvas_left_up,
            "left_down": canvas_left_down,
            "right_up": canvas_right_up,
            "right_down": canvas_right_down,
            "front": canvas_front,
            "side": canvas_side,
            "blank": canvas_blank,
        }
    
    
    def _load_resources(self):
        """加载 Barberpub 对开盖样式的图片资源"""
        res_base = self.base_dir / 'assets' / 'Barberpub' / '对开盖' / '矢量文件'
        
        self.resources = {
            'icon_logo': Image.open(res_base / '正唛logo.png').convert('RGBA'),
            'icon_top_logo': Image.open(res_base / '顶盖logo信息.png').convert('RGBA'),
            'icon_attention_info': Image.open(res_base / '对开盖开箱注意事项.png').convert('RGBA'),
            'icon_company': Image.open(res_base / '正唛公司信息.png').convert('RGBA'),
            'icon_webside': Image.open(res_base / '侧唛网址.png').convert('RGBA'),
            'icon_side_label_wide': Image.open(res_base / '侧唛标签_宽.png').convert('RGBA'),
            'icon_side_label_narrow': Image.open(res_base / '侧唛标签_窄.png').convert('RGBA'),
            'icon_slogan': Image.open(res_base / '正唛宣传语.png').convert('RGBA'),
            'icon_box_info': Image.open(res_base / '正唛多箱选择框.png').convert('RGBA'),
            'line_drawing': Image.open(res_base / '侧唛线描图.png').convert('RGBA'),
        }
    
    def _load_fonts(self):
        """加载字体路径"""
        font_base = self.base_dir / 'assets' / 'Barberpub' / '对开盖' / '箱唛字体'
        self.font_paths = {
            'CentSchbook BT': str(font_base / '111.ttf'),
            'Droid Sans Bold': str(font_base / 'CENSBKBI.TTF'),
            'Calibri Bold': str(font_base / 'calibri_blod.ttf'),

        }

    def generate_barberpub_left_panel(self, sku_config):
        """生成 Barberpub 对开盖样式的左侧面板"""
        canvas = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.half_w_px), sku_config.background_color)
        canvas_left_up = canvas.copy()
        canvas_left_down = canvas.copy()
        icon_top_logo = self.resources['icon_top_logo']
        
        # 在左侧面板顶部粘贴顶盖logo
        icon_top_loge_w = int( canvas.width * 0.55 ) # 宽度为面板宽度的60%
        icon_top_logo_resized = general_functions.scale_by_width(icon_top_logo, icon_top_loge_w)
        icon_top_logo_x = (canvas.width - icon_top_logo_resized.width) // 2
        icon_top_loge_y = (canvas.height - icon_top_logo_resized.height) // 2
        canvas_left_up.paste(icon_top_logo_resized, (icon_top_logo_x, icon_top_loge_y), icon_top_logo_resized)
        
        return canvas_left_up, canvas_left_down
        
    def generate_barberpub_right_panel(self, sku_config):
        """生成 Barberpub 对开盖样式的右侧面板"""
        canvas = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.half_w_px), sku_config.background_color)
        canvas_right_up = canvas.copy()
        canvas_right_down = canvas.copy()
        icon_attention_info = self.resources['icon_attention_info']
        
        # 在右侧面板顶部粘贴开箱注意事项
        icon_attention_info_w = int( canvas.width * 0.86 ) # 宽度为面板宽度的80%
        icon_attention_info_resized = general_functions.scale_by_width(icon_attention_info, icon_attention_info_w)
        icon_attention_info_x = (canvas.width - icon_attention_info_resized.width) // 2
        icon_attention_info_y = (canvas.height - icon_attention_info_resized.height) // 2
        canvas_right_up.paste(icon_attention_info_resized, (icon_attention_info_x, icon_attention_info_y), icon_attention_info_resized)
        
        return canvas_right_up, canvas_right_down
    
    def generate_barberpub_front_panel(self, sku_config):
        canvas = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.h_px), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)
        
        canvas_w, canvas_h = canvas.size
        
        # 加载字体路径
        font_path_centschbook = self.font_paths['CentSchbook BT']
        font_path_droid = self.font_paths['Droid Sans Bold']
        
        # --- 区域 A: 左上角 Logo ---
        margin_top_px = int(3 * sku_config.dpi)  # 顶部边距3cm
        margin_left_px = int(3 * sku_config.dpi)  # 左边距3cm
        margin_right_px = int(2.7 * sku_config.dpi)  # 右边距2.7cm
        
        icon_logo = self.resources['icon_logo']
        icon_logo_h_px = int(canvas_h * 0.14)  # Logo高度约为画布高度的14%
        icon_logo_resized = general_functions.scale_by_height(icon_logo, icon_logo_h_px)
        icon_logo_x = margin_left_px
        icon_logo_y = margin_top_px
        canvas.paste(icon_logo_resized, (icon_logo_x, icon_logo_y), mask=icon_logo_resized)
        
        # --- 区域 B: 右上角公司信息 ---
        icon_company = self.resources['icon_company']
        icon_company_h_px = int(canvas_h * 0.06)  # 公司信息高度约为画布高度的6%
        icon_company_resized = general_functions.scale_by_height(icon_company, icon_company_h_px)
        icon_company_x = canvas_w - icon_company_resized.width - margin_right_px
        icon_company_y = margin_top_px
        canvas.paste(icon_company_resized, (icon_company_x, icon_company_y), mask=icon_company_resized)
        
        # --- 区域 C: 中间 Product 名称和标语作为整体居中（稍微缩小）---
        product_text = sku_config.product
        target_product_w = int(canvas_w * 0.63)  # 缩小到68%宽度
        max_product_h = int(canvas_h * 0.28)  # 缩小到28%高度
        
        product_font_size = general_functions.get_max_font_size(
            product_text, font_path_droid, target_product_w, max_height=max_product_h
        )
        product_font = ImageFont.truetype(font_path_droid, product_font_size)
        
        # 计算Product文字尺寸
        product_w = draw.textlength(product_text, font=product_font)
        bbox = draw.textbbox((0, 0), product_text, font=product_font)
        product_h = bbox[3] - bbox[1]
        
        # --- 区域 D: 标语（小字，斜体）---
        icon_slogan = self.resources['icon_slogan']
        icon_slogan_h_px = int(canvas_h * 0.05)  # 稍微缩小到5%
        icon_slogan_resized = general_functions.scale_by_height(icon_slogan, icon_slogan_h_px)
        
        # 计算Product和Slogan的整体高度
        vertical_gap = int(1.3 * sku_config.dpi)  # Product和Slogan之间间距1.3cm
        total_center_h = product_h + vertical_gap + icon_slogan_resized.height
        
        # 整体垂直居中（在画布的48%处）
        center_y_start = int(canvas_h * 0.48) - (total_center_h // 2)
        
        # 绘制Product（居中）
        product_x = (canvas_w - product_w) // 2
        product_y = center_y_start
        draw.text((product_x, product_y), product_text, font=product_font, fill=(0, 0, 0))
        
        # 粘贴Slogan（居中）
        icon_slogan_x = (canvas_w - icon_slogan_resized.width) // 2
        icon_slogan_y = product_y + product_h + vertical_gap
        canvas.paste(icon_slogan_resized, (icon_slogan_x, icon_slogan_y), mask=icon_slogan_resized)
        
        # --- 区域 G: 底部斜纹条块（先绘制，避免遮盖文字）---
        stripe_height_cm = 1.2
        bottom_margin_cm = 0.6
        stripe_y_start = canvas_h - int(stripe_height_cm * sku_config.dpi) - int(bottom_margin_cm * sku_config.dpi)
        stripe_y_end = canvas_h - int(bottom_margin_cm * sku_config.dpi)

        
        canvas = general_functions.draw_diagonal_stripes(
            canvas, 
            stripe_height_cm=stripe_height_cm,
            dpi=sku_config.dpi,
            bottom_margin_cm=bottom_margin_cm,
            stripe_width_px=150,
            stripe_color=(0, 0, 0),
            bg_color=sku_config.background_color
        )
        draw = ImageDraw.Draw(canvas)  # 重新创建draw对象，因为canvas被更新了
        
        # --- 区域 E: 左下角颜色和SKU代码 ---
        margin_bottom_px = int(3.2 * sku_config.dpi)  # 底部边距3.2cm（增大，确保文字在斜纹上方）
        text_vertical_gap = int(0.3 * sku_config.dpi)  # 文字之间的垂直间距
        
        # SKU代码文字（大字，粗体）
        sku_code_text = sku_config.sku_name
        target_sku_code_w = int(canvas_w * 0.715)  # 宽度为面板宽度的71.5%
        sku_code_font_size = general_functions.get_max_font_size(
            sku_code_text, font_path_centschbook, target_sku_code_w, max_height=int(canvas_h * 0.14)
        )
        sku_code_font = ImageFont.truetype(font_path_centschbook, sku_code_font_size)
        
        # 计算SKU代码尺寸
        bbox_sku = draw.textbbox((0, 0), sku_code_text, font=sku_code_font)
        sku_code_h = bbox_sku[3] - bbox_sku[1]
        
        # SKU代码Y坐标（从底部往上算）
        sku_code_y = canvas_h - margin_bottom_px - sku_code_h - int(0.5 * sku_config.dpi)
        sku_code_x = margin_left_px - int(0.6 * sku_config.dpi)  # 左移0.6cm以增加边距

        draw.text((sku_code_x, sku_code_y), sku_code_text, font=sku_code_font, fill=(0, 0, 0))
        
        # 颜色文字（粗体，与SKU代码相同字体）
        color_text = f"{sku_config.color.upper()}"
        color_font_size = int(canvas_h * 0.06)
        color_font = ImageFont.truetype(font_path_centschbook, color_font_size)
        
        bbox_color = draw.textbbox((0, 0), color_text, font=color_font)
        color_text_h = bbox_color[3] - bbox_color[1]
        color_text_y = sku_code_y - color_text_h - text_vertical_gap  # 在SKU代码上方
        color_text_x = margin_left_px
      
        draw.text((color_text_x, color_text_y), color_text, font=color_font, fill=(0, 0, 0))
        
        # --- 区域 F: 右下角箱号信息（黑框文字）---
        box_text = f"BOX {sku_config.box_number['current_box']} OF {sku_config.box_number['total_boxes']}"
        box_text_font_w = int(canvas_w * 0.127)  # 目标宽度为画布宽度的12.7%
        box_text_font_h = int(canvas_h * 0.038)  # 字体大小为画布高度的3.8%
        box_text_font_size = general_functions.get_max_font_size(
            box_text, font_path_centschbook, box_text_font_w, max_height=box_text_font_h)
        box_text_font = ImageFont.truetype(font_path_centschbook, box_text_font_size)
        
        # 计算文字尺寸
        bbox_box_text = draw.textbbox((0, 0), box_text, font=box_text_font)
        bbox_box_text_w = bbox_box_text[2] - bbox_box_text[0]
        bbox_box_text_h = bbox_box_text[3] - bbox_box_text[1]
        
        # 箱号位置（右下角，与SKU代码Y坐标对齐）
        bbox_text_x = canvas_w - margin_right_px - bbox_box_text_w
        bbox_text_y = canvas_h - margin_bottom_px - bbox_box_text_h - int(0.5 * sku_config.dpi) 
        box_text_pos = (bbox_text_x, bbox_text_y)
        
        # 绘制黑框背景
        draw = general_functions.draw_rounded_bg_for_text(
            draw, bbox_box_text, sku_config, box_text_pos,
            bg_color=(0, 0, 0), padding_cm=(0.5, 0.7), radius=12
        )
        
        # 绘制白色文字
        draw.text(box_text_pos, box_text, font=box_text_font, fill=sku_config.background_color)
        
        canvas_front = canvas
        return canvas_front
    
    def generate_barberpub_side_panel(self, sku_config):
        """
        生成 Barberpub 对开盖样式的侧面板
        在这里分成了两种情况：宽侧唛和窄侧唛，根据箱子宽度决定使用哪种侧唛
            
        """
        canvas = Image.new(sku_config.color_mode, (sku_config.w_px, sku_config.h_px), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)
        
        canvas_w, canvas_h = canvas.size
        
        # 加载字体路径
        font_path_centschbook = self.font_paths['CentSchbook BT']
        
        # --- 区域 A: 侧唛网址 ---
        """ 两种情况下都放置侧唛网址，位置和大小相同 """
        icon_webside = self.resources['icon_webside']
        icon_webside_w_px = int(canvas_w * 0.5)  # 宽度为画布宽度的50%
        icon_webside_resized = general_functions.scale_by_width(icon_webside, icon_webside_w_px)
        icon_webside_x = (canvas_w - icon_webside_resized.width) // 2
        icon_webside_y = int(3 * sku_config.dpi)  # 顶部边距3cm
        canvas.paste(icon_webside_resized, (icon_webside_x, icon_webside_y), mask=icon_webside_resized)

        if sku_config.w_cm > sku_config.h_cm :
            """
            【宽侧唛的设计标准】对开盖侧唛分为两种：当侧唛的高小于等于宽10cm时，侧唛为左右结构，即分割条在底部。
            """
            
            # --- 区域 A: 底部斜纹条块（先绘制，避免遮盖文字）---
            stripe_height_cm = 1.2
            bottom_margin_cm = 0.6
            
            canvas = general_functions.draw_diagonal_stripes(
                canvas, 
                stripe_height_cm=stripe_height_cm,
                dpi=sku_config.dpi,
                bottom_margin_cm=bottom_margin_cm,
                stripe_width_px=150,
                stripe_color=(0, 0, 0),
                bg_color=sku_config.background_color
            )
            draw = ImageDraw.Draw(canvas)  # 重新创建draw对象，因为canvas被更新了
            
            # --- 区域 B: 线描图 (居左，高度为侧唛 2/3) ---
            
            # 优先使用用户上传的线描图（来自 app_v2.py 的 img_line_drawing 上传口），否则退回资源文件
            if hasattr(sku_config, 'img_line_drawing') and sku_config.img_line_drawing is not None:
                img_line_drawing = Image.open(sku_config.img_line_drawing).convert('RGBA')
            else:
                img_line_drawing = self.resources['line_drawing']
            
            line_h = int(canvas_h * 0.66) # 侧唛的三分之二
            img_line_resized = general_functions.scale_by_height(img_line_drawing, line_h)
            # 居左粘贴，留出 margin
            img_line_drawing_x = int(5 * sku_config.dpi)  # 左边距5cm
            img_line_drawing_y = (canvas_h - line_h) // 2 + int( 0.05 * sku_config.h_px) # 纵向微调，稍微下移0.05倍高度
            canvas.paste(img_line_resized, (img_line_drawing_x, img_line_drawing_y), mask=img_line_resized)
            
            # --- 区域 C: 右侧 SKU 文字 ---
            sku_text = sku_config.sku_name
            # 放在右侧中间偏上
            sku_font_size_w = int(canvas_w * 0.571)  # 字体大小为画布宽度的57.1%
            sku_font_size = general_functions.get_max_font_size(
                sku_text, font_path_centschbook, target_width = sku_font_size_w, max_height=int(canvas_h * 0.11)
            )
            sku_font = ImageFont.truetype(font_path_centschbook, sku_font_size)
            sku_box = draw.textbbox((0,0), sku_text, font=sku_font)
            bbox_sku_w = sku_box[2] - sku_box[0]
            bbox_sku_h = sku_box[3] - sku_box[1]
            bbox_sku_x = int(canvas_w * 0.38) # 右侧偏左一些
            bbox_sku_y = int(canvas_h * 0.38) # 纵向偏上一些
            draw.text((bbox_sku_x, bbox_sku_y), sku_text, font=sku_font, fill=(0,0,0))
            
            # --- 区域 D: 中间右侧颜色信息 ---
            color_text = f"{sku_config.color.upper()}"
            # 放在右侧中间,在箱号信息的后边
            color_font_h = int(canvas_h * 0.041)  # 字体大小为画布高度的3.8%
            color_font = ImageFont.truetype(font_path_centschbook, color_font_h)
            bbox_color = draw.textbbox((0,0), color_text, font=color_font)
            bbox_color_w = bbox_color[2] - bbox_color[0]
            bbox_color_h = bbox_color[3] - bbox_color[1]
            bbox_color_x = bbox_sku_x + bbox_sku_w - bbox_color_w - int(0.3 * sku_config.dpi) # 王回收1cm
            bbox_color_y = bbox_sku_y + bbox_sku_h + int(2.6 * sku_config.dpi) # 纵向间距2cm
            draw.text((bbox_color_x, bbox_color_y), color_text, font=color_font, fill=(0,0,0))
            
            # --- 区域 E: 中间右侧箱号信息（黑框文字）---
            box_text = f"BOX {sku_config.box_number['current_box']} OF {sku_config.box_number['total_boxes']}"
            box_text_font_h = int(canvas_h * 0.038)  # 字体大小为画布高度的3.8%
            box_text_font_w = int(canvas_w * 0.127)  # 目标宽度为画布宽度的12.7%
            box_text_font_size = general_functions.get_max_font_size(
                box_text, font_path_centschbook, box_text_font_w, max_height=box_text_font_h)
            box_text_font = ImageFont.truetype(font_path_centschbook, box_text_font_size)
            
            # 计算文字尺寸
            bbox_box_text = draw.textbbox((0, 0), box_text, font=box_text_font)
            bbox_box_text_w = bbox_box_text[2] - bbox_box_text[0]
            bbox_box_text_h = bbox_box_text[3] - bbox_box_text[1]
            
            # 箱号位置（SKU代码的下方）
            bbox_text_x = bbox_color_x - bbox_box_text_w  - int( 1.5 * sku_config.dpi) # 左移2cm
            bbox_text_y = bbox_sku_y + bbox_sku_h + int(2.6 * sku_config.dpi)  + int( (bbox_color_h - bbox_box_text_h ) / 3) # 纵向间距3cm
            box_text_pos = (bbox_text_x, bbox_text_y)
            
            # 绘制黑框背景
            draw = general_functions.draw_rounded_bg_for_text(
                draw, bbox_box_text, sku_config, box_text_pos,
                bg_color=(0, 0, 0), padding_cm=(0.5, 0.7), radius=12
            )
            
            # 绘制白色文字
            draw.text(box_text_pos, box_text, font=box_text_font, fill=sku_config.background_color)
            
            # --- 区域 F: 右下侧标签框---
            # 使用宽侧唛
            icon_side_label = self.resources['icon_side_label_wide']
             
            
            # 调整标签大小
            label_w_target = int(bbox_sku_w * 0.93)  # 标签宽度为SKU文字的93%
            
            # 填充标签内容
            icon_side_label_filled = self.fill_side_wide_label_barberpub_doubleopening(sku_config, icon_side_label, self.font_paths)
            icon_side_label_filled_resized = general_functions.scale_by_width(icon_side_label_filled, label_w_target)
            
            # 标签位置（底部中央，斜纹条上方）
            label_x = bbox_sku_x + int(bbox_sku_w * 0.07)
            label_y = bbox_text_y + bbox_box_text_h + int( canvas_h * 0.14)  
            canvas.paste(icon_side_label_filled_resized, (label_x, label_y), icon_side_label_filled_resized)
            

        else:
            """
            【窄侧唛的设计标准】对开盖侧唛分为两种：当侧唛的高大于等于宽10cm，侧唛为上下结构，即分割条在尺寸重量标签之上，
            """
            
            # --- 区域 B: 线描图（在网址下方间隔3cm，高度为canvas_h的46%）---
            # 优先使用用户上传的线描图（来自 app_v2.py 的 img_line_drawing 上传口），否则退回资源文件
            if hasattr(sku_config, 'img_line_drawing') and sku_config.img_line_drawing is not None:
                img_line_drawing = Image.open(sku_config.img_line_drawing).convert('RGBA')
            else:
                img_line_drawing = self.resources['line_drawing']
            
            line_h = int(canvas_h * 0.46)  # 高度为画布高度的46%
            img_line_resized = general_functions.scale_by_height(img_line_drawing, line_h)
            
            # 线描图位置（网址下方间隔3cm，水平居中）
            img_line_x = (canvas_w - img_line_resized.width) // 2
            img_line_y = icon_webside_y + icon_webside_resized.height + int(3 * sku_config.dpi)  # 间隔3cm
            canvas.paste(img_line_resized, (img_line_x, img_line_y), mask=img_line_resized)
            
            # --- 区域 C: SKU文字（在线描图下方间隔3cm）---
            sku_text = sku_config.sku_name
            
            # SKU文字位置（线描图下方间隔3cm）
            sku_text_y = img_line_y + img_line_resized.height + int(3 * sku_config.dpi)  # 间隔3cm
            
            # 最大字号：画布宽度的90%
            max_sku_w = int(canvas_w * 0.9)
            max_sku_h = int(canvas_h * 0.12)  # 限制高度为画布高度的12%
            
            sku_font_size = general_functions.get_max_font_size(
                sku_text, font_path_centschbook, max_sku_w, max_height=max_sku_h
            )
            sku_font = ImageFont.truetype(font_path_centschbook, sku_font_size)
            
            # 计算SKU文字宽度并居中
            sku_text_w = draw.textlength(sku_text, font=sku_font)
            sku_text_x = (canvas_w - sku_text_w) // 2
            draw.text((sku_text_x, sku_text_y), sku_text, font=sku_font, fill=(0, 0, 0))
            
            # --- 区域 D: 斜纹条块 ---
            stripe_height_cm = 1.2
            # 下边界距离canvas底是canvas_h的21%
            bottom_margin_px = int(canvas_h * 0.21)
            bottom_margin_cm = bottom_margin_px / sku_config.dpi
            
            canvas = general_functions.draw_diagonal_stripes(
                canvas, 
                stripe_height_cm=stripe_height_cm,
                dpi=sku_config.dpi,
                bottom_margin_cm=bottom_margin_cm,
                stripe_width_px=150,
                stripe_color=(0, 0, 0),
                bg_color=sku_config.background_color
            )
            draw = ImageDraw.Draw(canvas)  # 重新创建draw对象
            canvas_w, canvas_h = canvas.size  # 更新尺寸变量
            
            # --- 区域 E: 侧唛标签（右下方，斜纹条块下方）---
            icon_side_label = self.resources['icon_side_label_narrow']
            
            # 调整标签大小（占画布宽度的85%）
            label_h_target = int(canvas_w * 0.15)
            icon_side_label_resized = general_functions.scale_by_height(icon_side_label, label_h_target)
            
            # 填充标签内容
            icon_side_label_filled_resized = self.fill_side_narrow_label_barberpub_doubleopening(sku_config, icon_side_label_resized, self.font_paths)
            
            # 标签位置（右下方，在斜纹条下方）
            label_x = canvas_w //2 + int( (canvas_w // 2 - icon_side_label_filled_resized.width) //2 )
            label_y = canvas_h - bottom_margin_px + int((bottom_margin_px - icon_side_label_filled_resized.height ) //2 )
            canvas.paste(icon_side_label_filled_resized, (label_x, label_y), icon_side_label_filled_resized)
            
            # --- 区域 F: 净重毛重信息（左下方，斜纹条块下方）---
            
            # 设置左侧信息区域的起始位置
            info_start_x = int(canvas_w * 0.0987)  # 从canvas_w的9.87%处开始
            info_center_y = canvas_h - int(bottom_margin_px // 2)  # 斜纹条下方区域的垂直中心
            
            # --- 统一字体设置 ---
            label_font_size = int(canvas_h * 0.028)  # 标签文字字号（G.W./N.W. 和 BOX SIZE）
            value_font_size = int(canvas_h * 0.024)  # 值文字字号（比标签文字小一点）
            label_font = ImageFont.truetype(font_path_centschbook, label_font_size)
            value_font = ImageFont.truetype(font_path_centschbook, value_font_size)
            
            # 上下间隔2cm
            vertical_gap = int(2.6 * sku_config.dpi)
            
            # --- G.W./N.W. 标签和值 ---
            gw_label_text = "G.W./N.W."
            gw_value_text = f"{sku_config.side_text['gw_value']} / {sku_config.side_text['nw_value']} LBS"
            
            # 计算G.W./N.W.标签的边界框
            bbox_gw_label = draw.textbbox((0, 0), gw_label_text, font=label_font)
            gw_label_w = bbox_gw_label[2] - bbox_gw_label[0]
            gw_label_h = bbox_gw_label[3] - bbox_gw_label[1]
            
            # G.W./N.W.标签位置（上方，文字底部距虚线 vertical_gap // 2）
            gw_label_x = info_start_x 
            gw_label_y = info_center_y - vertical_gap // 2 - gw_label_h * 1.3 # 上移1.3倍高度以增加间距
            gw_label_pos = (gw_label_x, gw_label_y)
            
            # 绘制G.W./N.W.标签黑色圆角背景
            draw = general_functions.draw_rounded_bg_for_text(
                draw, bbox_gw_label, sku_config, gw_label_pos,
                bg_color=(0, 0, 0), padding_cm=(0.3, 0.7), radius=16
            )
            
            # 绘制G.W./N.W.标签文字
            draw.text(gw_label_pos, gw_label_text, font=label_font, fill=sku_config.background_color)
            
            # G.W./N.W.值位置（标签右边间隔2cm，文字中心与G.W./N.W.文字中心对齐）
            gw_value_x = gw_label_x + gw_label_w + int(2 * sku_config.dpi)
            
            # 计算G.W./N.W.值的边界框以获取高度
            bbox_gw_value = draw.textbbox((0, 0), gw_value_text, font=value_font)
            gw_value_h = bbox_gw_value[3] - bbox_gw_value[1]
            
            # 使值文字中心与标签文字中心在同一水平线上
            gw_label_center_y = gw_label_y + gw_label_h // 2
            gw_value_y = gw_label_center_y - gw_value_h // 2
            draw.text((gw_value_x, gw_value_y), gw_value_text, font=value_font, fill=(0, 0, 0))
            
            # --- BOX SIZE 标签和值 ---
            box_label_text = "BOX SIZE"
            box_value_text = f"{sku_config.l_cm:.1f}\" x {sku_config.w_cm:.1f}\" x {sku_config.h_cm:.1f}\""
            
            # 计算BOX SIZE标签的边界框
            bbox_box_label = draw.textbbox((0, 0), box_label_text, font=label_font)
            box_label_w = bbox_box_label[2] - bbox_box_label[0]
            box_label_h = bbox_box_label[3] - bbox_box_label[1]
            
            # BOX SIZE标签位置（下方，文字顶部距虚线 vertical_gap // 2）
            box_label_x = info_start_x
            box_label_y = info_center_y + vertical_gap // 2
            box_label_pos = (box_label_x, box_label_y)
            
            # 绘制BOX SIZE标签黑色圆角背景
            draw = general_functions.draw_rounded_bg_for_text(
                draw, bbox_box_label, sku_config, box_label_pos,
                bg_color=(0, 0, 0), padding_cm=(0.3, 0.7), radius=16
            )
            # 绘制BOX SIZE标签文字
            draw.text(box_label_pos, box_label_text, font=label_font, fill=sku_config.background_color)
            
            # BOX SIZE值位置（标签右边间隔2cm，文字中心与BOX SIZE文字中心对齐）
            box_value_x = gw_value_x  # 与G.W./N.W.值对齐
            
            # 计算BOX SIZE值的边界框以获取高度
            bbox_box_value = draw.textbbox((0, 0), box_value_text, font=value_font)
            box_value_h = bbox_box_value[3] - bbox_box_value[1]
            
            # 使值文字中心与标签文字中心在同一水平线上
            box_label_center_y = box_label_y + box_label_h // 2
            box_value_y = box_label_center_y - box_value_h // 2
            draw.text((box_value_x, box_value_y), box_value_text, font=value_font, fill=(0, 0, 0))
            
            # --- 绘制虚线（在G.W./N.W.和BOX SIZE之间）---
            dash_x_start = int(canvas_w * 0.101)  # 虚线起始位置
            dash_length = int(canvas_w * 0.44)  # 虚线长度约44%
            dash_y = info_center_y  # 虚线Y坐标（两行文字中间）
            
            # 绘制虚线
            dash_width = 10  # 每段虚线的宽度
            dash_gap = 12  # 虚线间隔
            current_x = dash_x_start
            while current_x < dash_x_start + dash_length:
                draw.line([(current_x, dash_y), (current_x + dash_width, dash_y)], fill=(0, 0, 0), width=3)
                current_x += dash_width + dash_gap
            
        
        canvas_side = canvas
        return canvas_side
    
    
    









    """
    以下内容为填充Barberpub对开盖侧唛标签的函数
    """



    def fill_side_wide_label_barberpub_doubleopening(self, sku_config, img_label, fonts_paths):
        """
        填充Barberpub对开盖样式的侧唛标签
        
        参数:
            sku_config: SKU配置对象
            img_label: 空白标签图片
            fonts_paths: 字体路径字典
        
        返回:
            填充好内容的标签图片
        """
        # 在空白标签上绘制内容
        label_canvas = img_label.copy()
        draw = ImageDraw.Draw(label_canvas)
        
        label_w, label_h = label_canvas.size
        font_path_centschbook = fonts_paths['CentSchbook BT']
        
        # --- 区域1: 重量信息 G.W./N.W. ---
        # 假设重量信息，实际项目中应该从sku_config获取
        gw_text = f"G.W./N.W. : {sku_config.side_text['gw_value']} / {sku_config.side_text['nw_value']} LBS"
        gw_font_size = int(label_h * 0.182)  # 字体大小为标签高度的16.2%
        gw_font = ImageFont.truetype(font_path_centschbook, gw_font_size)
        
        # 重量信息位置（顶部左侧）
        gw_x = int(label_w * 0.023)  # 左边距2%
        gw_y = int(label_h * 0.13)  # 顶部13%处
        draw.text((gw_x, gw_y), gw_text, font=gw_font, fill=(0, 0, 0))
        
        # --- 区域2: 箱子尺寸 BOX SIZE ---
        box_size_text = f"BOX SIZE : {sku_config.l_cm:.1f}\" x {sku_config.w_cm:.1f}\" x {sku_config.h_cm:.1f}\""
        box_font_size = int(label_h * 0.182)  # 字体大小为标签高度的16.2%
        box_font = ImageFont.truetype(font_path_centschbook, box_font_size)
        
        # 箱子尺寸位置（左侧，在重量信息下方）
        box_x = int(label_w * 0.023)  # 左边距2%
        box_y = int(label_h * 0.48)  # 48%处
        draw.text((box_x, box_y), box_size_text, font=box_font, fill=(0, 0, 0))
        
        # --- 区域3: 两个条形码区域 ---
        
        barcode_area_y = int(label_h * 0.05)
        barcode_area_h = int(label_h * 0.26)
        
        # 第一个条形码：使用SKU名称生成
        barcode1_text = sku_config.sku_name
        try:
            # 生成第一个条形码图片
            barcode1_img = general_functions.generate_barcode_image(
                barcode1_text, 
                int(label_w * 0.25),  # 条形码宽度为标签宽度的25%
                barcode_area_h   
            )
            
            # 第一个条形码位置（右上角）
            barcode1_x = int(label_w * 0.598)
            barcode1_y = barcode_area_y
            label_canvas.paste(barcode1_img, (barcode1_x, barcode1_y), barcode1_img if barcode1_img.mode == 'RGBA' else None)
            
            # 第一个条形码下方的编号
            number1_text = barcode1_text
            number1_font_size = int(label_h * 0.04)
            number1_font = ImageFont.truetype(font_path_centschbook, number1_font_size)
            bbox_number1 = draw.textbbox((0, 0), number1_text, font=number1_font)
            number1_x = barcode1_x + int( (barcode1_img.width - (bbox_number1[2] - bbox_number1[0])) / 2 )
            number1_y = barcode1_y + barcode1_img.height + int(label_h * 0.004)
            draw.text((number1_x, number1_y), number1_text, font=number1_font, fill=(0, 0, 0))
            
        except Exception as e:
            # 如果第一个条形码生成失败，只显示文字
            draw.text((int(label_w * 0.51), barcode_area_y), barcode1_text, 
                    font=ImageFont.truetype(font_path_centschbook, int(label_h * 0.05)), fill=(0, 0, 0))
        
        # 第二个条形码：使用sn_code生成
        barcode2_text = sku_config.side_text['sn_code']
        try:
            # 生成第二个条形码图片
            barcode2_img = general_functions.generate_barcode_image(
                barcode2_text, 
                int(label_w * 0.14),  # 条形码宽度为标签宽度的14%
                barcode_area_h   
            )
            
            # 第二个条形码位置（右边第二个）
            barcode2_x = int(label_w * 0.855)
            barcode2_y = barcode_area_y
            label_canvas.paste(barcode2_img, (barcode2_x, barcode2_y), barcode2_img if barcode2_img.mode == 'RGBA' else None)
            
            # 第二个条形码下方的编号
            number2_font_size = int(label_h * 0.04)
            number2_font = ImageFont.truetype(font_path_centschbook, number2_font_size)
            bbox_number2 = draw.textbbox((0, 0), barcode2_text, font=number2_font)
            number2_x = barcode2_x + int( (barcode2_img.width - (bbox_number2[2] - bbox_number2[0])) / 2 )
            number2_y = barcode2_y + barcode2_img.height + int(label_h * 0.004)
            draw.text((number2_x, number2_y), barcode2_text, font=number2_font, fill=(0, 0, 0))
            
        except Exception as e:
            # 如果第二个条形码生成失败，只显示文字
            draw.text((int(label_w * 0.82), int(label_h * 0.1)), barcode2_text, 
                    font=ImageFont.truetype(font_path_centschbook, int(label_h * 0.05)), fill=(0, 0, 0))
        
        # --- 区域4: 右侧物流图标区域 ---
        # 这里放置物流图标（雨伞、易碎品等标识）

        
        # 可以在这里添加各种物流图标的绘制代码
        # 目前先留空，等待具体的图标资源
        
        # --- 区域5: 底部产地信息条 ---
        china_bar_y = int(label_h * 0.78)
        china_bar_height = int(label_h * 0.18)
        draw.rectangle([(0, china_bar_y), (label_w, china_bar_y + china_bar_height)], fill=(0, 0, 0))
        
        # 产地文字（使用背景色作为文字颜色）
        origin_text = sku_config.side_text.get('origin_text', 'MADE IN CHINA')
        china_font_size = int(label_h * 0.098)
        china_font = ImageFont.truetype(font_path_centschbook, china_font_size)
        china_text_w = draw.textlength(origin_text, font=china_font)
        china_x = (label_w - china_text_w) // 2
        china_y = china_bar_y + int(china_bar_height * 0.27)
        draw.text((china_x, china_y), origin_text, font=china_font, fill=sku_config.background_color)
        
        return label_canvas

    def fill_side_narrow_label_barberpub_doubleopening(self, sku_config, img_label, fonts_paths):
        """
        填充Barberpub对开盖样式的窄侧唛标签
        
        参数:
            sku_config: SKU配置对象
            img_label: 空白标签图片
            fonts_paths: 字体路径字典
        
        返回:
            填充好内容的标签图片
        """
        # 在空白标签上绘制内容
        label_canvas = img_label.copy()
        draw = ImageDraw.Draw(label_canvas)
        
        label_w, label_h = label_canvas.size
        font_path_centschbook = fonts_paths['CentSchbook BT']
        
        
        # --- 统一设置条形码参数 ---

        barcode_h = int(label_h * 0.28)  # 统一设置条形码高度
        barcode_y = int(label_h * 0.04)  # 统一设置条形码y坐标

        
        # --- 区域1: 左侧条形码（使用SKU名称）---
        barcode1_text = sku_config.sku_name
        barcode1_w = int(label_w * 0.533)  # 宽度为标签宽度的53.3%
        barcode1_h = barcode_h  
        
        try:
            barcode1_img = general_functions.generate_barcode_image(barcode1_text, barcode1_w, barcode1_h)
            barcode1_x = int(label_w * 0.05)  # 左边距5%
            barcode1_y = barcode_y  # 统一设置条形码y坐标
            label_canvas.paste(barcode1_img, (barcode1_x, barcode1_y), barcode1_img if barcode1_img.mode == 'RGBA' else None)
            
            # 条形码下方文字
            barcode1_font_size = int(label_h * 0.04)
            barcode1_font = ImageFont.truetype(font_path_centschbook, barcode1_font_size)
            bbox_barcode1 = draw.textbbox((0, 0), barcode1_text, font=barcode1_font)
            barcode1_text_x = barcode1_x + int((barcode1_w - (bbox_barcode1[2] - bbox_barcode1[0])) / 2)
            barcode1_text_y = barcode1_y + barcode1_h + int(label_h * 0.0020)
            draw.text((barcode1_text_x, barcode1_text_y), barcode1_text, font=barcode1_font, fill=(0, 0, 0))
            
        except Exception as e:
            # 条形码生成失败时显示文字
            draw.text((int(label_w * 0.05), barcode_y - int(1.5 * sku_config.dpi)), 
                    barcode1_text, 
                    font=ImageFont.truetype(font_path_centschbook, int(label_h * 0.05)), 
                    fill=(0, 0, 0))
        
        # --- 区域2: 右侧条形码（使用sn_code）---
        # --- 区域2: 右侧条形码（使用sn_code）---
        barcode2_text = sku_config.side_text['sn_code']
        barcode2_w = int(label_w * 0.36)  # 宽度为标签宽度的37%
        barcode2_h = barcode_h  
        
        try:
            barcode2_img = general_functions.generate_barcode_image(barcode2_text, barcode2_w, barcode2_h)
            barcode2_x = label_w - barcode2_w - int(label_w * 0.04)  # 右边距5%
            barcode2_y = barcode_y  # 统一设置条形码y坐标
            label_canvas.paste(barcode2_img, (barcode2_x, barcode2_y), barcode2_img if barcode2_img.mode == 'RGBA' else None)
            
            # 条形码下方文字
            barcode2_font_size = int(label_h * 0.04)
            barcode2_font = ImageFont.truetype(font_path_centschbook, barcode2_font_size)
            bbox_barcode2 = draw.textbbox((0, 0), barcode2_text, font=barcode2_font)
            barcode2_text_x = barcode2_x + int((barcode2_w - (bbox_barcode2[2] - bbox_barcode2[0])) / 2)
            barcode2_text_y = barcode2_y + barcode2_h + int(label_h * 0.0020)
            draw.text((barcode2_text_x, barcode2_text_y), barcode2_text, font=barcode2_font, fill=(0, 0, 0))
            
        except Exception as e:
            # 条形码生成失败时显示文字
            draw.text((label_w - int(label_w * 0.25), barcode_y - int(1.5 * sku_config.dpi)), 
                    barcode2_text, 
                    font=ImageFont.truetype(font_path_centschbook, int(label_h * 0.05)), 
                    fill=(0, 0, 0))
        
        # --- 区域3: 底部产地信息条 ---
        
        stripe_bottom_margin = int(label_h * 0.12)
        
        stripe_top_y = label_h - stripe_bottom_margin
        china_bar_y = stripe_top_y
        china_bar_height = stripe_bottom_margin
        draw.rectangle([(0, china_bar_y), (label_w, label_h)], fill=(0, 0, 0))
        
        # 产地文字（使用背景色作为文字颜色）
        origin_text = sku_config.side_text.get('origin_text', 'MADE IN CHINA')
        china_font_size = int(china_bar_height * 0.5)
        china_font = ImageFont.truetype(font_path_centschbook, china_font_size)
        china_text_w = draw.textlength(origin_text, font=china_font)
        china_x = (label_w - china_text_w) // 2
        china_y = china_bar_y + int(china_bar_height * 0.20)
        draw.text((china_x, china_y), origin_text, font=china_font, fill=sku_config.background_color)
        
        return label_canvas