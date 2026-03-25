# -*- coding: utf-8 -*-
"""
Barberpub 天地盖样式 - 将原有的 BoxMarkEngine 转换为样式类
"""
from PIL import Image, ImageDraw, ImageFont
import pathlib as Path
from style_base import BoxMarkStyle, StyleRegistry
import general_functions
from general_functions import generate_barcode_image


@StyleRegistry.register
class BarberpubTopAndBottomStyle(BoxMarkStyle):
    '''Barberpub 天地盖样式'''
    
    def get_style_name(self):
        return "barberpub_topandbottom"
    
    def get_style_description(self):
        return "Barberpub 天地盖箱唛样式"
    
    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'ppi', 'color', 'product', 'side_text', 'sku_name', 'box_number']
    
    def get_layout_config(self, sku_config):
        '''
        Barberpub 天地盖样式 - 5块布局（3列3行）
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
        """生成 Barberpub 天地盖样式需要的所有面板"""
        
        canvas_front_side, canvas_back_side = self.generate_barberpub_front_and_back_side(sku_config)
        canvas_left_side, canvas_right_side = self.generate_barberpub_left_and_right_side(sku_config)
        canvas_top = self.generate_barberpub_top_panel(sku_config)
        
        return {
            'front_side': canvas_front_side,
            'back_side': canvas_back_side,
            'left_side': canvas_left_side,
            'right_side': canvas_right_side,
            'top': canvas_top
        }
    
    def _load_resources(self):
        """加载 Barberpub 天地盖样式的图片资源"""
        res_base = self.base_dir / 'assets' / 'Barberpub' / '天地盖' / '矢量文件'
        
        self.resources = {
            'icon_logo': Image.open(res_base / '正唛logo.png').convert('RGBA'),
            'icon_company': Image.open(res_base / '正唛公司信息.png').convert('RGBA'),
            'icon_webside': Image.open(res_base / '侧唛网址.png').convert('RGBA'),
            'icon_side_label': Image.open(res_base / '侧唛标签.png').convert('RGBA'),
            'icon_slogan': Image.open(res_base / '正唛宣传语.png').convert('RGBA'),
            'icon_box_info': Image.open(res_base / '正唛多箱选择框.png').convert('RGBA'),
        }
    
    def _load_fonts(self):
        """加载字体路径"""
        font_base = self.base_dir / 'assets' / 'Barberpub' / '天地盖' / '箱唛字体'
        self.font_paths = {
            'CentSchbook BT': str(font_base / '111.ttf'),
            'Droid Sans Bold': str(font_base / 'CENSBKBI.TTF'),
            'Calibri Bold': str(font_base / 'calibri_blod.ttf'),

        }
    
    def generate_barberpub_front_and_back_side(self, sku_config):
        """生成 Barberpub 天地盖样式的前后侧面板"""
        canvas_front_side = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.h_px), sku_config.background_color)
        draw = ImageDraw.Draw(canvas_front_side)
        
        canvas_w, canvas_h = canvas_front_side.size
        
        # 加载字体路径
        font_path_centschbook = self.font_paths['CentSchbook BT']
        
        # --- 区域 A: 顶部 Logo ---
        margin_top_px = int(2.5 * sku_config.dpi) # 顶部留2.5cm间距
        icon_logo_h_px = int(canvas_h * 0.26) # Logo 高度为画布高度的26%
        icon_logo = self.resources['icon_logo']
        print(f"[DEBUG] 前后侧板Logo 高度: {icon_logo_h_px}px")
        
        # 缩放并居中粘贴 Logo
        icon_logo_resized = general_functions.scale_by_height(icon_logo, icon_logo_h_px)
        icon_logo_x = (canvas_w - icon_logo_resized.width) // 2
        canvas_front_side.paste(icon_logo_resized, (icon_logo_x, margin_top_px), mask=icon_logo_resized)
        
        # --- 区域 B: 中间 SKU 文字 ---
        sku_text = sku_config.sku_name
        target_sku_w = int(canvas_w * 0.85)  # 增加到85%宽度，尽可能利用空间
        
        # 动态计算最大字号 - 移除高度限制，提高max_size上限到1000
        sku_font_size = general_functions.get_max_font_size(
            sku_text, font_path_centschbook, target_sku_w, max_height=None, max_size=1000  # 提高上限
        )
        sku_font = ImageFont.truetype(font_path_centschbook, sku_font_size)
        
        # 计算 SKU 居中坐标 (位于 Logo 下方，间距 1.0cm，减少间距留更多空间)
        sku_y = margin_top_px + icon_logo_h_px + int(1.0 * sku_config.dpi)
        sku_w = draw.textlength(sku_text, font=sku_font)
        sku_x = (canvas_w - sku_w) // 2
        draw.text((sku_x, sku_y), sku_text, font=sku_font, fill=(0, 0, 0))
        
        # --- 区域 C: 底部信息框 ---
        margin_bottom_px = int(2.4 * sku_config.dpi)
        info_font_frame_size = int(canvas_h * 0.07)  # 字体大小调整为7%高度
        info_font_without_frame_size = int(canvas_h * 0.06)  # 字体大小调整为5%高度

        info_font_frame = ImageFont.truetype(font_path_centschbook, info_font_frame_size)
        info_font_without_frame = ImageFont.truetype(font_path_centschbook, info_font_without_frame_size)
        
        # 左侧：G.W./N.W. 信息
        gw_text = "G.W./N.W."
        weight_text = f"{sku_config.side_text['gw_value']} / {sku_config.side_text['nw_value']} LBS"
        
        # 计算左侧文字框位置
        bbox_gw = draw.textbbox((0, 0), gw_text, font=info_font_frame)
        bbox_gw_width = bbox_gw[2] - bbox_gw[0]
        bbox_weight = draw.textbbox((0, 0), weight_text, font=info_font_without_frame)

        
        left_box_x = int(10 * sku_config.dpi)  # 左侧留10cm间距
        left_box_y = canvas_h - margin_bottom_px - info_font_frame_size 
        
        # 绘制左侧背景框（G.W./N.W.）
        bbox_gw_pos = (left_box_x, left_box_y)
        draw = general_functions.draw_rounded_bg_for_text(
            draw, bbox_gw, sku_config, bbox_gw_pos,
            bg_color=(0, 0, 0), padding_cm=(0.7, 0.6), radius=16
        )
        draw.text(bbox_gw_pos, gw_text, font=info_font_frame, fill= (sku_config.background_color))
        
        
        # 绘制重量文字（在G.W./N.W.右方）
        bbox_weight_x = left_box_x + bbox_gw_width + int(1.8 * sku_config.dpi)
        bbox_weight_y = left_box_y + int( (info_font_frame_size - info_font_without_frame_size) / 2 )
        bbox_weight_pos = (bbox_weight_x, bbox_weight_y)

        draw.text(bbox_weight_pos, weight_text, font=info_font_without_frame, fill= (0,0,0))
        
        # 右侧：BOX SIZE 信息
        box_size_text = "BOX SIZE"
        # 动态生成尺寸文本（英寸）
        l_in = sku_config.l_in
        w_in = sku_config.w_in
        h_in = sku_config.h_in
        dimension_text = f'{l_in:.1f}" x {w_in:.1f}" x {h_in:.1f}"'
        
        # 计算右侧文字框位置
        bbox_box = draw.textbbox((0, 0), box_size_text, font=info_font_frame)
        bbox_dim = draw.textbbox((0, 0), dimension_text, font=info_font_without_frame)
        bbox_box_w = bbox_box[2] - bbox_box[0]
        
        right_box_x = canvas_w /2 +  int(2.5 * sku_config.dpi)  # 右侧留2.5cm间距
        right_box_y = canvas_h - margin_bottom_px - info_font_frame_size 
        
        # 绘制右侧背景框（BOX SIZE）
        bbox_box_pos = (right_box_x, right_box_y)
        draw = general_functions.draw_rounded_bg_for_text(
            draw, bbox_box, sku_config, bbox_box_pos,
            bg_color=(0, 0, 0), padding_cm=(0.7, 0.6), radius=16
        )
        draw.text(bbox_box_pos, box_size_text, font=info_font_frame, fill=sku_config.background_color)
        
        # 绘制尺寸文字（在BOX SIZE右方）
        dim_y = right_box_y + int( (info_font_frame_size - info_font_without_frame_size) / 2 )
        dim_x = right_box_x + bbox_box_w + int(1.8 * sku_config.dpi)
        bbox_dim_pos = (dim_x, dim_y)

        draw.text(bbox_dim_pos, dimension_text, font=info_font_without_frame, fill=(0,0,0))
        
        # 前后侧面板是一样的，只是旋转180度
        canvas_back_side = canvas_front_side.rotate(180)
        
        return canvas_front_side, canvas_back_side
    
    
    
    def generate_barberpub_left_and_right_side(self, sku_config):
        """
        生成 Barberpub 天地盖样式的左右侧面板
        策略：先创建一个横向的画布 (Width x Height) 进行绘制，
        绘制完成后，分别旋转 90度和 -90度 得到左右侧板。
        """ 


        # 1. 建立横向画布 (宽=箱子宽w_px, 高=箱子高h_px)
        # 注意：这里宽高是反直觉的，因为我们是在“横着”画侧面
        canvas_w = sku_config.w_px
        canvas_h = sku_config.h_px
        
        canvas = Image.new(sku_config.color_mode, (canvas_w, canvas_h), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)
        
        # 加载字体
        font_path_centschbook = self.font_paths['CentSchbook BT']
        
        # --- 区域 A: 核心 SKU (上半部分) ---
        sku_text = sku_config.sku_name
        
        # 左右侧面的 SKU 非常巨大，我们将宽度限制设为 90%，高度限制放宽到 55%
        target_sku_w = int(canvas_w * 0.9)
        max_sku_h = int(canvas_h * 0.55)
        
        sku_font_size = general_functions.get_max_font_size(
            sku_text, font_path_centschbook, target_sku_w, max_height=max_sku_h
        )
        sku_font = ImageFont.truetype(font_path_centschbook, sku_font_size)
        print(f"[DEBUG] 左右侧板SKU 字体大小: {sku_font_size}px")
        
        # 居中绘制 SKU
        # 视觉修正：稍微偏上一点，给底部图标留空间，y 设为高度的 10% 开始或者居中偏上
        sku_text_w = draw.textlength(sku_text, font=sku_font)
        # 获取文字真实高度（去除基线偏移）
        bbox = draw.textbbox((0, 0), sku_text, font=sku_font)
        sku_text_h = bbox[3] - bbox[1]
        
        sku_x = (canvas_w - sku_text_w) // 2
        # 让文字视觉重心位于上半部分中心 (大约 37% 处)
        sku_y_center = int(canvas_h * 0.37)
        sku_y = sku_y_center - (sku_text_h // 2)
        
        draw.text((sku_x, sku_y), sku_text, font=sku_font, fill=(0, 0, 0))
        
        # --- 区域 B: 底部图标资源 ---
        # 我们使用资源图片 icon_webside 和 icon_side_label
        img_web = self.resources['icon_webside']     # 左下角：网址搜索条
        img_label = self.resources['icon_side_label'] # 右下角：条码和警告标
        
        # 设定图标尺寸：根据参考图，底部图标大约占面板高度的 22%
        icons_web_w_px = int(canvas_w * 0.53)  # 网址条按宽度缩放，占画布宽度53%
        icons_label_h_px = int(canvas_h * 0.22)
        
        # 缩放图片
        img_web_resized = general_functions.scale_by_width(img_web, icons_web_w_px)
        img_label_resized = general_functions.scale_by_height(img_label, icons_label_h_px)
        
        # 计算坐标
        margin_side = int(3 * sku_config.dpi)   # 左右边距 3cm
        margin_bottom = int(5.5 * sku_config.dpi) # 底部边距 4.5cm
        
        # 1. 粘贴左下角网址条 (icon_webside)
        web_x = margin_side
        web_y = canvas_h - margin_bottom - img_web_resized.height  - int(img_label_resized.height * 0.4)  # 略微上移
        canvas.paste(img_web_resized, (web_x, web_y), mask=img_web_resized)
        
        # 2. 粘贴右下角标签条 (icon_side_label)
        label_x = canvas_w - img_label_resized.width - margin_side
        label_y = canvas_h - img_label_resized.height - margin_bottom
        img_label_resized_filled = self.fill_left_and_right_label_barberpub_topandbottom(sku_config, img_label_resized, self.font_paths)
        canvas.paste(img_label_resized_filled, (label_x, label_y), mask=img_label_resized_filled)
        
        # --- 区域 C: 旋转生成最终面板 ---
        # 关键步骤：expand=True 会自动交换宽高，变成竖长的面板
        
        # 左侧面板：文字通常朝左 (顺时针旋转 90度)
        # 依据展开图逻辑，左侧面板的“底”是指向中心的，所以文字应该是“躺着”的
        canvas_left_side = canvas.rotate(-90, expand=True)
        
        # 右侧面板：文字通常朝右 (逆时针旋转 90度 )
        canvas_right_side = canvas.rotate(90, expand=True)
        
        return canvas_left_side, canvas_right_side
        
        
    
    
    
    def generate_barberpub_top_panel(self, sku_config):
        '''生成 Barberpub 天地盖样式的顶部面板'''
        canvas = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.w_px), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)
        
        canvas_w, canvas_h = canvas.size
        
        # 加载字体路径
        font_path_centschbook = self.font_paths['CentSchbook BT']
        font_path_droid = self.font_paths['Droid Sans Bold']
        
        # --- 区域 A: 左上角 Logo ---
        margin_top_px = int(2 * sku_config.dpi)  # 顶部边距2cm
        margin_left_px = int(3 * sku_config.dpi)  # 左边距3cm
        margin_right_px = int(3 * sku_config.dpi)  # 右边距3cm
        
        icon_logo = self.resources['icon_logo']
        icon_logo_h_px = int(canvas_h * 0.16)  # Logo高度约为画布高度的16%
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
        target_product_w = int(canvas_w * 0.65)  # 缩小到65%宽度
        max_product_h = int(canvas_h * 0.20)  # 缩小到20%高度
        
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
        vertical_gap = int(1.0 * sku_config.dpi)  # Product和Slogan之间间距1cm
        total_center_h = product_h + vertical_gap + icon_slogan_resized.height
        
        # 整体垂直居中（在画布的45%处）
        center_y_start = int(canvas_h * 0.45) - (total_center_h // 2)
        
        # 绘制Product（居中）
        product_x = (canvas_w - product_w) // 2
        product_y = center_y_start
        draw.text((product_x, product_y), product_text, font=product_font, fill=(0, 0, 0))
        
        # 粘贴Slogan（居中）
        icon_slogan_x = (canvas_w - icon_slogan_resized.width) // 2
        icon_slogan_y = product_y + product_h + vertical_gap
        canvas.paste(icon_slogan_resized, (icon_slogan_x, icon_slogan_y), mask=icon_slogan_resized)
        
        # --- 区域 E: 左下角颜色和SKU代码 ---
        margin_bottom_px = int(3.5 * sku_config.dpi)  # 底部边距（预留给斜纹）
        text_vertical_gap = int(0.3 * sku_config.dpi)  # 文字之间的垂直间距（增大）
        
        # SKU代码文字（大字，粗体）
        sku_code_text = sku_config.sku_name
        target_sku_code_w = int(canvas_w * 0.52)  # 宽度为面板宽度的52%
        sku_code_font_size = general_functions.get_max_font_size(
            sku_code_text, font_path_centschbook, target_sku_code_w, max_height=int(canvas_h * 0.14)
        )
        sku_code_font = ImageFont.truetype(font_path_centschbook, sku_code_font_size)
        
        # 计算SKU代码尺寸
        bbox_sku = draw.textbbox((0, 0), sku_code_text, font=sku_code_font)
        sku_code_h = bbox_sku[3] - bbox_sku[1]
        
        # SKU代码Y坐标（从底部往上算）
        sku_code_y = canvas_h - margin_bottom_px - sku_code_h - int(1.8 * sku_config.dpi)
        sku_code_x = margin_left_px
        draw.text((sku_code_x, sku_code_y), sku_code_text, font=sku_code_font, fill=(0, 0, 0))
        
        # 颜色文字（粗体，与SKU代码相同字体）
        color_text = f"({sku_config.color.upper()})"
        color_font_size = int(canvas_h * 0.06)
        color_font = ImageFont.truetype(font_path_centschbook, color_font_size)
        
        bbox_color = draw.textbbox((0, 0), color_text, font=color_font)
        color_text_h = bbox_color[3] - bbox_color[1]
        color_text_y = sku_code_y - color_text_h - text_vertical_gap  # 在SKU代码上方
        color_text_x = margin_left_px
        draw.text((color_text_x, color_text_y), color_text, font=color_font, fill=(0, 0, 0))
        
        # --- 区域 F: 右下角箱号信息 ---
        icon_box_info = self.resources['icon_box_info']
        icon_box_info_h_px = int(canvas_h * 0.10)  # 箱号信息高度约为画布高度的13%
        icon_box_info_resized = general_functions.scale_by_height(icon_box_info, icon_box_info_h_px)
        icon_box_info_x = canvas_w - icon_box_info_resized.width - margin_right_px
        icon_box_info_y = canvas_h - margin_bottom_px - icon_box_info_resized.height - int(0.5 * sku_config.dpi)
        canvas.paste(icon_box_info_resized, (icon_box_info_x, icon_box_info_y), mask=icon_box_info_resized)
        
        # 在箱号信息的黑色背景区域中绘制BOX文字（白色）
        box_text = f"BOX {sku_config.box_number['current_box']} OF {sku_config.box_number['total_boxes']}"
        box_text_font_size = int(icon_box_info_h_px * 0.40)  # 字体大小为图标高度的40%
        box_text_font = ImageFont.truetype(font_path_centschbook, box_text_font_size)
        
        # 计算文字尺寸并居中
        bbox_box_text = draw.textbbox((0, 0), box_text, font=box_text_font)
        box_text_w = bbox_box_text[2] - bbox_box_text[0]
        box_text_h = bbox_box_text[3] - bbox_box_text[1]
        
        # 在黑色区域居中（黑色区域大约占图标高度的50%，位于上半部分）
        box_text_x = icon_box_info_x + (icon_box_info_resized.width - box_text_w) // 2
        box_text_y = icon_box_info_y + int(icon_box_info_h_px * 0.12)  # 在图标顶部12%处开始
        draw.text((box_text_x, box_text_y), box_text, font=box_text_font, fill=sku_config.background_color)
        
        # 在白色区域绘制产地信息（黑色）
        font_path_calibri = self.font_paths['Calibri Bold']
        origin_text = sku_config.side_text['origin_text']
        origin_text_font_size = int(icon_box_info_h_px * 0.22)  # 字体大小为图标高度的22%，比BOX小
        origin_text_font = ImageFont.truetype(font_path_calibri, origin_text_font_size)
        
        # 计算origin文字尺寸并居中
        bbox_origin_text = draw.textbbox((0, 0), origin_text, font=origin_text_font)
        origin_text_w = bbox_origin_text[2] - bbox_origin_text[0]
        origin_text_h = bbox_origin_text[3] - bbox_origin_text[1]
        
        # 在白色区域居中（白色区域在下半部分，从55%开始）
        origin_text_x = icon_box_info_x + (icon_box_info_resized.width - origin_text_w) // 2
        origin_text_y = icon_box_info_y + int(icon_box_info_h_px * 0.68)  # 在图标68%处
        draw.text((origin_text_x, origin_text_y), origin_text, font=origin_text_font, fill=(0, 0, 0))
        
        # --- 区域 G: 底部斜纹条块 ---
        canvas = general_functions.draw_diagonal_stripes(
            canvas, 
            stripe_height_cm=1.5,  # 条纹高度1.8cm
            dpi=sku_config.dpi,
            bottom_margin_cm=1.0,  # 底部留白1cm
            stripe_width_px=150,
            stripe_color=(0, 0, 0),
            bg_color=sku_config.background_color
        )
        
        canvas_top = canvas
        return canvas_top
    
    def fill_left_and_right_label_barberpub_topandbottom(self, sku_config, img_label_resized, fonts_paths):
        """
        填充 Barberpub 天地盖样式左右侧面板的标签区域
        
        功能：只填充顶部的两个条形码（SKU + SN码），底部4个运输标识图片自带
        使用 generate_barcode_image 生成纯条形码，然后手动绘制文字
        """
        tw, th = img_label_resized.size
        draw = ImageDraw.Draw(img_label_resized)
        
        # 加载字体
        font_path = fonts_paths['CentSchbook BT']
        
        # ========== 顶部条形码区域（约35%高度）==========
        barcode_zone_h = int(th * 0.35)
        
        # 纯条形码高度（不含文字）：占条形码区域的89%（增大）
        barcode_only_h = int(barcode_zone_h * 0.89)
        # 条形码顶部间距：10% 
        barcode_y = int(barcode_zone_h * 0.10)
        
        # 文字高度：占条形码区域的22%（增大）
        text_font_size = int(barcode_zone_h * 0.22)
        text_font = ImageFont.truetype(font_path, text_font_size)
        # 文字位置：条形码下方，留出2%的小间距，让文字更靠近底部
        text_y = barcode_y + barcode_only_h + int(barcode_zone_h * 0.01)
        
        # ========== 左侧 SKU 条形码（占宽度的52%，比SN更宽）==========
        sku_name = sku_config.sku_name
        sku_barcode_w = int(tw * 0.52)
        sku_barcode_x = int(tw * 0.01)  # 左边距1%
        
        # 生成纯条形码（不带文字）
        sku_barcode_img = generate_barcode_image(sku_name, width=sku_barcode_w, height=barcode_only_h)
        img_label_resized.paste(sku_barcode_img, (sku_barcode_x, barcode_y), mask=sku_barcode_img)
        
        # 在条形码下方居中绘制文字
        sku_text_w = draw.textlength(sku_name, font=text_font)
        sku_text_x = sku_barcode_x + (sku_barcode_w - sku_text_w) // 2
        draw.text((sku_text_x, text_y), sku_name, font=text_font, fill=(0, 0, 0))
        
        # ========== 右侧 SN 条形码（占宽度的42%）==========
        sn_code = sku_config.side_text['sn_code']
        sn_barcode_w = int(tw * 0.42)
        sn_barcode_x = int(tw * 0.56)  # 从56%位置开始（留4%间距）
        
        # 生成纯条形码（不带文字）
        sn_barcode_img = generate_barcode_image(sn_code, width=sn_barcode_w, height=barcode_only_h)
        img_label_resized.paste(sn_barcode_img, (sn_barcode_x, barcode_y), mask=sn_barcode_img)
        
        # 在条形码下方居中绘制文字
        sn_text_w = draw.textlength(sn_code, font=text_font)
        sn_text_x = sn_barcode_x + (sn_barcode_w - sn_text_w) // 2
        draw.text((sn_text_x, text_y), sn_code, font=text_font, fill=(0, 0, 0))
        
        return img_label_resized