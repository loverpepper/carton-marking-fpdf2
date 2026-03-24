# -*- coding: utf-8 -*-
"""
Macrout 天地盖样式 - 将原有的 BoxMarkEngine 转换为样式类
"""
from PIL import Image, ImageDraw, ImageFont
import pathlib as Path
from style_base import BoxMarkStyle, StyleRegistry
import general_functions
from general_functions import generate_barcode_image
import layout_engine as engine
import re


@StyleRegistry.register
class MacroutTopAndBottomStyle(BoxMarkStyle):
    ''' Macrout 天地盖样式'''
    
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
                    pass  # 跳过无法打开的文件
        return results
    
    def get_layout_config(self, sku_config):
        '''
        Macrout 天地盖样式 - 5块布局（3列3行）
        '''
        
        x0 = 0
        x1 = sku_config.h_px
        x2 = sku_config.h_px + sku_config.l_px
        
        y0 = 0
        y1 = sku_config.h_px
        y2 = sku_config.h_px + sku_config.w_px
        
        return {
            # 第一行：
            "back_side_panel": (x1, y0, sku_config.l_px, sku_config.h_px),  # 后侧面板
            
            # 第二行：
            "left_side_panel": (x0, y1, sku_config.h_px, sku_config.w_px),       # 左侧面板
            "top_panel": (x1, y1, sku_config.l_px, sku_config.w_px),        # 顶部面板
            "right_side_panel": (x2, y1, sku_config.h_px, sku_config.w_px),      # 右侧面板
            
            # 第三行：
            "front_side_panel": (x1, y2, sku_config.l_px, sku_config.h_px)  # 前侧面板
        }
    
    def get_panels_mapping(self, sku_config):
        """定义每个区域应该粘贴哪个面板"""
        
        return {
            'back_side_panel': 'back_side',
            'left_side_panel': 'left_side',
            'top_panel': 'top',
            'right_side_panel': 'right_side',
            'front_side_panel': 'front_side'  
        }
        
    def generate_all_panels(self, sku_config):
        """生成 Macrout 天地盖样式需要的所有面板"""
        
        canvas_front_side, canvas_back_side = self.generate_macrout_front_and_back_side(sku_config)
        canvas_left_side, canvas_right_side = self.generate_macrout_left_and_right_side(sku_config)
        canvas_top = self.generate_macrout_top_panel(sku_config)
        
        return {
            'front_side': canvas_front_side,
            'back_side': canvas_back_side,
            'left_side': canvas_left_side,
            'right_side': canvas_right_side,
            'top': canvas_top
        }
    
    def _load_resources(self):
        """加载 Macrout 天地盖样式的图片资源"""
        res_base = self.base_dir / 'assets' / 'Macrout' / '天地盖' / '矢量文件'
        
        self.resources = {
            # 正唛图片资源
            'icon_logo': Image.open(res_base / 'Macrout.png').convert('RGBA'),
            'icon_notice': Image.open(res_base / '箱子提示语.png').convert('RGBA'),
            'icon_web': Image.open(res_base / '公司信息.png').convert('RGBA'),
            'icon_attention': Image.open(res_base / '标签.png').convert('RGBA'),
            
            # 前后侧唛标的图标资源
            'icon_label': Image.open(res_base / '箱子信息.png').convert('RGBA'),
            
            # 左右侧唛标的图标资源
            'icon_paste_barcode': Image.open(res_base / '条形码定界框.png').convert('RGBA'),
        }
    
    def _load_fonts(self):
        """加载字体路径"""
        font_base = self.base_dir / 'assets' / 'Macrout' / '天地盖' / '箱唛字体'
        self.font_paths = {
            'Calibri': str(font_base / 'calibri.ttf'),
            'ITC Avant Garde Gothic Demi Cyrillic': str(font_base / 'itc-avant-garde-gothic-demi-cyrillic.otf'),
            'Arial Rounded MT Bold': str(font_base / 'ARLRDBD.ttf'),
            'Arial': str(font_base / 'arial.ttf'),
            'Arial Bold': str(font_base / 'arialbd.ttf'),
        }

    def generate_macrout_top_panel(self, sku_config):
        canvas = Image.new(sku_config.color_mode, (int(sku_config.l_px), int(sku_config.w_px)), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)
        
        # 左上角的公司Logo
        icon_logo = self.resources['icon_logo']
        icon_logo_target_width = int(canvas.width * 0.13)
        
        top_row = engine.Row(
            justify = 'space-between',
            fixed_width = canvas.width,
            padding = int( canvas.width * 0.023 ), 
            children=[
                engine.Image(icon_logo, width = icon_logo_target_width),
                engine.Spacer(width = icon_logo_target_width)  # 右上角留空与左上角Logo等宽的空白区域
            ]   
        )
        
        # 中间的SKU,产品名称,箱唛提示语和右边颜色
        product_text = sku_config.product
        sku_text = sku_config.sku_name
        color_text = sku_config.color
        
        product_text_target_width = int(canvas.width * 0.36)
        sku_text_target_width = int(canvas.width * 0.43)
        color_text_target_width = int(canvas.width * 0.09)
        
        icon_notice_target_width = int(canvas.width * 0.21) # 箱唛提示语图标占21%宽度
        
        font_product_size = general_functions.get_max_font_size(product_text, self.font_paths['ITC Avant Garde Gothic Demi Cyrillic'], product_text_target_width)
        font_sku_size = general_functions.get_max_font_size(sku_text, self.font_paths['Arial Rounded MT Bold'], sku_text_target_width)
        font_color_size = general_functions.get_max_font_size(color_text, self.font_paths['Arial'], color_text_target_width)

        font_product = ImageFont.truetype(self.font_paths['ITC Avant Garde Gothic Demi Cyrillic'], font_product_size)
        font_sku = ImageFont.truetype(self.font_paths['Arial Rounded MT Bold'], font_sku_size)
        font_color = ImageFont.truetype(self.font_paths['Arial'], font_color_size)
        
        spacing_middle = int(canvas.height * 0.062)
        middle_col = engine.Column(
            align = 'center',
            justify= 'start',
            spacing = spacing_middle,
            children=[
                engine.Text(product_text, font=font_product, nudge_y = int(canvas.height * 0.02)),  # 产品名称稍微往上挪一点
                engine.Text(sku_text, font=font_sku),
                engine.Row(
                    justify = 'start',
                    align = 'center',
                    spacing = int(canvas.width * 0.04),  # 箱唛提示语和颜色之间的间距
                    children=[
                        engine.Image(self.resources['icon_notice'], width = icon_notice_target_width),
                        engine.Text(color_text, font=font_color)
                    ]
                )

            ]
        )
        
        # 底部的网址和注意事项图
        icon_web = self.resources['icon_web']
        icon_attention = self.resources['icon_attention']
        
        icon_web_target_width = int(canvas.width * 0.28)
        icon_attention_target_width = int(canvas.width * 0.14)
        
        bottom_row = engine.Row(
            align= 'bottom',
            justify = 'space-between',
            fixed_width= canvas.width,
            padding = int(canvas.width * 0.023),
            children=[
                engine.Image(icon_web, width = icon_web_target_width),
                engine.Image(icon_attention, width = icon_attention_target_width)
            ]
        )
        
        # 整体布局
        main_column = engine.Column(
            align = 'center',
            justify = 'space-between',
            fixed_width = canvas.width,
            fixed_height = canvas.height,
            children=[
                top_row,
                middle_col,
                bottom_row
            ]
        )
        
        # 渲染整体布局到画布
        main_column.layout( 0 , 0 )
        main_column.render(draw)
        return canvas
    
    def generate_macrout_left_and_right_side(self, sku_config):
        canvas = Image.new(sku_config.color_mode, (int(sku_config.w_px), int(sku_config.h_px)), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)
        
        # 左右侧面板的设计相同，都是一个条形码定界框和一些文本信息
        icon_barcode_frame = self.resources['icon_paste_barcode'].rotate(90, expand=True)  # 旋转90度以适应侧面板的竖向布局
        icon_barcode_frame_target_height = int( 5 * sku_config.dpi) # 条形码定界框的高度是5厘米
        
        sku_text = sku_config.sku_name
        sku_text_target_width = int(canvas.width * 0.5)
        font_sku_size = general_functions.get_max_font_size(sku_text, self.font_paths['Arial Bold'], sku_text_target_width)
        font_sku = ImageFont.truetype(self.font_paths['Arial Bold'], font_sku_size)
        
        main_row = engine.Row(
            align = 'center',
            justify = 'space-between',
            fixed_width = canvas.width,
            padding_x = int(canvas.width * 0.07),
            children=[
                engine.Image(icon_barcode_frame, height = icon_barcode_frame_target_height),
                engine.Text(sku_text, font=font_sku),
            ]
        )
        
        # 把main_row 居中放置
        main_row.layout(0, (canvas.height - main_row.height) // 2)
        main_row.render(draw)
        
        canvas_left_side = canvas.rotate(-90, expand=True)  # 左侧面板需要逆时针旋转90度
        canvas_right_side = canvas.rotate(90, expand=True)  # 右侧面板需要顺时针旋转90度
        
        return canvas_left_side, canvas_right_side  # 左右侧面板相同，返回两份
    
    def generate_macrout_front_and_back_side(self, sku_config):
        canvas = Image.new(sku_config.color_mode, (int(sku_config.l_px), int(sku_config.h_px)), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)
        
        # 前后侧面板的设计相同，都是一个SKU名称和 包含毛重净重条形码的标签图
        
        # SKU文本
        sku_text = sku_config.sku_name
        sku_text_target_width = int(canvas.width * 0.41) # SKU文本占前后侧面板宽度
        font_sku_size = general_functions.get_max_font_size(sku_text, self.font_paths['Arial Rounded MT Bold'], sku_text_target_width)
        font_sku = ImageFont.truetype(self.font_paths['Arial Rounded MT Bold'], font_sku_size)
        
        # 包含毛重净重条形码的标签图
        icon_label = self.resources['icon_label']
        icon_label_target_width = int(canvas.width * 0.4) # 标签图占前后侧面板宽度
        icon_label_target_height = int(icon_label_target_width * icon_label.height / icon_label.width)
        # 先缩放到目标尺寸，再在目标分辨率上绘制文字和条形码，避免事后放大导致模糊
        icon_label_resized = icon_label.resize((icon_label_target_width, icon_label_target_height), Image.Resampling.LANCZOS)
        icon_label_filled = self.fill_label(icon_label_resized, sku_config)
        
        main_row = engine.Row(
            align = 'center',
            justify = 'space-between',
            fixed_width = canvas.width,
            padding = int(canvas.width * 0.05),
            children=[
                engine.Text(sku_text, font=font_sku),
                engine.Image(icon_label_filled)
            ]
        )
        
        # 把main_row 居中放置
        main_row.layout(0, (canvas.height - main_row.height) // 2)
        main_row.render(draw)
        
        canvas_front_side = canvas
        canvas_back_side = canvas.rotate(180, expand=True)  # 后侧面板需要旋转180度
        
        return canvas_front_side, canvas_back_side
    
    def fill_label(self, icon_label, sku_config):
        """在标签图上填充毛重净重条形码和文本信息"""
        canvas = icon_label.copy()
        draw = ImageDraw.Draw(canvas)
        
        # 获取画布宽高，方便按比例落位
        W, H = canvas.width, canvas.height
        
        # === 1. 准备文字内容和字体 ===
        weight_text = f"G.W./N.W. : {sku_config.side_text['gw_value']} / {sku_config.side_text['nw_value']} lbs"
        box_text = f"BOX SIZE : {sku_config.l_in:.1f}\" x {sku_config.w_in:.1f}\" x {sku_config.h_in:.1f}\""

        # 字体大小适配
        text_height = int(H * 0.21)
        font_text = ImageFont.truetype(self.font_paths['Arial Bold'], text_height)

        # === 2. 生成条形码 ===
        barcode_height = int(H * 0.44)  
        # 左边长一点，右边短一点
        barcode_sku_width = int(W * 0.17) 
        barcode_sn_width = int(W * 0.12)
        
        # generate_barcode_image 函数没有底部的条形码文字
        barcode_sku = general_functions.generate_barcode_image(sku_config.sku_name, barcode_sku_width, barcode_height)
        barcode_sn = general_functions.generate_barcode_image(sku_config.side_text['sn_code'], barcode_sn_width, barcode_height)
        
        # === 3. 填充中间文字 (左对齐，垂直居中) ===
        text_start_x = int(W * 0.388) # 从 38.8% 的宽度开始写
        
        # 落在上半格的中心高度 (约 25% 处)
        draw.text((text_start_x, int(H * 0.25)), weight_text, fill="black", font=font_text, anchor="lm")
        # 落在下半格的中心高度 (约 75% 处)
        draw.text((text_start_x, int(H * 0.75)), box_text, fill="black", font=font_text, anchor="lm")
        
        # === 4. 填充右上角条形码 及 底部文字 ===
        # 新增一个小号字体给条形码底部用
        font_barcode = ImageFont.truetype(self.font_paths['Arial'], int(H * 0.12))

        # 4.1 贴 SKU 条形码
        sku_x = int(W * 0.695)
        sku_y = int(H * 0.08)
        canvas.paste(barcode_sku, (sku_x, sku_y))
        
        # 在 SKU 条形码正下方居中打字 (anchor="mt" 意思是顶端水平居中，极其好用)
        sku_text_x = sku_x + int(barcode_sku_width / 2)
        sku_text_y = sku_y + barcode_height + int(H * 0.01) # 往下挪一点点留出缝隙
        draw.text((sku_text_x, sku_text_y), sku_config.sku_name, fill="black", font=font_barcode, anchor="mt")
        
        # 4.2 贴 SN 条形码
        sn_x = int(W * 0.877) 
        sn_y = int(H * 0.08)
        canvas.paste(barcode_sn, (sn_x, sn_y))
        
        # 在 SN 条形码正下方居中打字
        sn_text_x = sn_x + int(barcode_sn_width / 2)
        sn_text_y = sn_y + barcode_height + int(H * 0.01)
        draw.text((sn_text_x, sn_text_y), sku_config.side_text['sn_code'], fill="black", font=font_barcode, anchor="mt")
    
        return canvas