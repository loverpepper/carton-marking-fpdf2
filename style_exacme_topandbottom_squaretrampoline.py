# -*- coding: utf-8 -*-
"""
Exacme 方形蹦床天地盖样式 - 将原有的 BoxMarkEngine 转换为样式类
"""
from PIL import Image, ImageDraw, ImageFont
import pathlib as Path
from style_base import BoxMarkStyle, StyleRegistry
import general_functions
from general_functions import generate_barcode_image
import layout_engine as engine
import re


@StyleRegistry.register
class ExacmeTopAndBottomSquareTrampolineStyle(BoxMarkStyle):
    '''Exacme 方形蹦床天地盖样式'''
    
    def get_style_name(self):
        return "exacme_topandbottom_squaretrampoline"
    
    def get_style_description(self):
        return "Exacme 方形蹦床天地盖箱唛样式"
    
    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'ppi', 'color', 'product', 'side_text', 'sku_name', 'box_number']
    
    def get_preview_images(self):
        """
        从 assets/Exacme/方形蹦床天地盖/实例生成图/ 读取所有图片文件，
        返回 [(文件名, PIL.Image), ...] 列表，按文件名排序。
        若文件夹为空或不存在则返回空列表。
        """
        preview_dir = self.base_dir / 'assets' / 'Exacme' / '方形蹦床天地盖' / '实例生成图'
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
        Exacme 方形蹦床天地盖样式 - 5块布局（3列3行）
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
        """生成 Exacme 方形蹦床天地盖样式需要的所有面板"""
        
        canvas_front_side, canvas_back_side = self.generate_exacme_front_and_back_side(sku_config)
        canvas_left_side, canvas_right_side = self.generate_exacme_left_and_right_side(sku_config)
        canvas_top = self.generate_exacme_top_panel(sku_config)
        
        return {
            'front_side': canvas_front_side,
            'back_side': canvas_back_side,
            'left_side': canvas_left_side,
            'right_side': canvas_right_side,
            'top': canvas_top
        }
    
    def _load_resources(self):
        """加载 Exacme 方形蹦床天地盖样式的图片资源"""
        res_base = self.base_dir / 'assets' / 'Exacme' / '方形蹦床天地盖' / '矢量文件'
        
        self.resources = {
            # 正唛图片资源
            'icon_logo': Image.open(res_base / 'logo.png').convert('RGBA'),
            'icon_middle_info_vertical': Image.open(res_base / '正唛中间信息-1.png').convert('RGBA'),
            'icon_middle_info_horizontal': Image.open(res_base / '正唛中间信息-2.png').convert('RGBA'),
            'icon_bottom_info': Image.open(res_base / '正唛底部提示信息.png').convert('RGBA'),
            
            # 前后侧唛标的图标资源
            'icon_logo': Image.open(res_base / 'logo.png').convert('RGBA'),
            'icon_company': Image.open(res_base / '上下侧唛公司信息.png').convert('RGBA'),
            
            # 左右侧唛标的图标资源
            'icon_side_label_high': Image.open(res_base / '侧唛标签_高.png').convert('RGBA'),
            'icon_side_label_wide': Image.open(res_base / '侧唛标签_宽.png').convert('RGBA'),
        }
    
    def _load_fonts(self):
        """加载字体路径"""
        font_base = self.base_dir / 'assets' / 'Exacme' / '方形蹦床天地盖' / '箱唛字体'
        self.font_paths = {
            'Arial Regular': str(font_base / 'arial.ttf'),
            'Arial Bold': str(font_base / 'arialbd.ttf'),
            'Arial Black': str(font_base / 'ariblk.ttf'),
        }
    
    def generate_exacme_front_and_back_side(self, sku_config):
        """生成 Exacme 方形蹦床天地盖样式的前后侧面板"""
        canvas = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.h_px), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)
        
        # ================= 1. 提取动态信息 =================
        # 提取尺寸文字 (带有 H1 -> H10 的特殊规则)
        size_text = "" 
        match = re.search(r'H(\d)(\d{1,2})', sku_config.sku_name, re.IGNORECASE)
        if match:
            dim1 = match.group(1)
            dim2 = match.group(2)
            if dim2 == '1':
                dim2 = '10'
            size_text = f"{dim1}x{dim2}FT"
            
        # ================= 2. 准备字体 =================
        # 第一排：尺寸 + 产品名 (常规体)
        font_size_row1 = int(canvas.height * 0.15) 
        font_row1 = ImageFont.truetype(self.font_paths['Arial Regular'], font_size_row1)
        
        # 第二排：SKU (超大粗体) + 颜色 (中等常规体)
        font_size_row2_sku = int(canvas.height * 0.34) 
        font_row2_sku = ImageFont.truetype(self.font_paths['Arial Black'], font_size_row2_sku)
        font_size_row2_color = int(canvas.height * 0.12) 
        font_row2_color = ImageFont.truetype(self.font_paths['Arial Regular'], font_size_row2_color)
        
        # 第三排：箱数提示 (较小常规体 + 粗体黑框)
        font_size_row3 = int(canvas.height * 0.10) 
        font_row3 = ImageFont.truetype(self.font_paths['Arial Regular'], font_size_row3)
        font_row3_bold = ImageFont.truetype(self.font_paths['Arial Bold'], font_size_row3)

        # ================= 3. 组装中间文字块 (Column) =================
        # 3.1 第一排：直接把尺寸和产品名拼成一句话，保证底边完美对齐
        row1 = engine.Text(f"{size_text} {sku_config.product}", font=font_row1)
        
        # 3.2 第二排：SKU 和颜色，底部对齐
        row2_color_element = engine.Text(f"({sku_config.color.title()})", font=font_row2_color, nudge_y=-int(canvas.height * 0.03)) # 括号视觉上往往偏下，稍微往上提一点点
        row2_left_spacer = engine.Spacer(width=row2_color_element.width, height=1) # 左侧隐形配重砖块，宽度和颜色元素一样，保证右侧颜色信息不会挤压 SKU 的位置
        
        row2 = engine.Row(
            align='bottom',
            spacing=int(canvas.width * 0.000001), # 一点点小间距
            children=[
                # row2_left_spacer, # 左侧隐形配重砖块
                engine.Text(sku_config.sku_name, font=font_row2_sku),
                row2_color_element
            ]
        )
        
        # 3.3 第三排：左边提示文字 + 右边黑框白字
        box_text_left = f"{sku_config.box_number['total_boxes']} Boxes in Total, May Deliver Separately."
        box_text_right = f"Box {sku_config.box_number['current_box']} of {sku_config.box_number['total_boxes']}"
        box_padding = int(0.6 * sku_config.dpi) # 黑框内边距
        
        row3 = engine.Row(
            align='center',
            spacing=int(canvas.width * 0.01),
            children=[
                engine.Text(box_text_left, font=font_row3),
                engine.Text(
                    box_text_right,
                    font=font_row3_bold,
                    color=sku_config.background_color, # 牛皮纸色文字
                    draw_background=True,
                    background_color='black',
                    padding=box_padding,
                    border_radius=int(canvas.height * 0.02),
                    nudge_x=-box_padding, # 让背景框紧贴文字，向左微调
                    nudge_y=-box_padding - int(canvas.height * 0.01) # 向上微调，让背景框紧贴文字
                
                )
            ]
        )
        
        # 把三排文字打包成一个靠左对齐的垂直容器
        middle_column = engine.Column(
            align='left',
            spacing=int(canvas.height * 0.10), # 三排文字之间的行间距
            children=[row1, row2, row3]
        )

        # ================= 4. 组装最外层大管家 (Row) =================
        icon_logo = self.resources['icon_logo']
        icon_company = self.resources['icon_company']
        
        # 左右 Logo，根据设计图估算一下宽度比例
        left_logo = engine.Image(icon_logo, width=int(canvas.width * 0.15))
        right_logo = engine.Image(icon_company, width=int(canvas.width * 0.18))
        
        side_padding = int(2.5 * sku_config.dpi) # 左右安全边距
        
        main_panel = engine.Row(
            fixed_width=canvas.width,
            fixed_height=canvas.height,
            justify='space-between', # 两端对齐魔法，把左右 Logo 顶到两边
            align='center',          # 整体垂直居中
            padding_x=side_padding,  # 只设左右 padding，因为已经锁死了 height，不需要上下 padding
            children=[
                left_logo,
                middle_column,
                right_logo
            ]
        )

        # ================= 5. 一键渲染 =================
        main_panel.layout(0, 0)
        main_panel.render(draw)
       
        
        # 前后侧面板是一样的，只是旋转180度
        canvas_front_side = canvas.copy()
        canvas_back_side = canvas_front_side.rotate(180)
        
        return canvas_front_side, canvas_back_side
    
    
    
    def generate_exacme_left_and_right_side(self, sku_config):
        """
        生成 Exacme 方形蹦床天地盖样式的左右侧面板
        策略：先创建一个横向的画布 (Width x Height) 进行绘制，
        绘制完成后，分别旋转 90度和 -90度 得到左右侧板。
        """ 

        # 建立横向画布 (宽=箱子宽w_px, 高=箱子高h_px)
        # 注意：这里宽高是反直觉的，因为我们是在“横着”画侧面
        canvas_w = sku_config.w_px
        canvas_h = sku_config.h_px
        
        canvas = Image.new(sku_config.color_mode, (canvas_w, canvas_h), sku_config.background_color)
        # draw = ImageDraw.Draw(canvas)
        
        if sku_config.l_cm > 130 and sku_config.w_cm < 40:
            """
                依据长宽条件选择高竖标签还是宽横标签：
                长大于130cm且宽小于40cm的，使用高竖标签；其他情况使用宽横标签。
                这个条件是根据 Exacme 的设计图和实际产品尺寸总结出来的经验规则，目的是让标签在侧面看起来更协调。
            """
            print("使用高竖标签")
            img_label_filled = self.fill_left_and_right_label_high(sku_config, self.resources['icon_side_label_high'], self.font_paths)
        else:
            print("使用宽横标签")
            img_label_filled = self.fill_left_and_right_label_wide(sku_config, self.resources['icon_side_label_wide'], self.font_paths)

        """填充 Exacme 天地盖样式左右侧面板的标签区域"""
        
        img_label_filled_target_width = int(canvas.width * 0.9) # 标签占侧身宽度的90%，留一点边距
        img_label_filled_target_resized = img_label_filled.resize((img_label_filled_target_width, int(img_label_filled.height * (img_label_filled_target_width / img_label_filled.width))), Image.Resampling.LANCZOS)   
        
        general_functions.paste_image_center_with_heightorwidth(canvas, img_label_filled_target_resized, y_offset=int(canvas.height * 0.05)) # 标签距离顶部5%的位置
        
        # 关键步骤：expand=True 会自动交换宽高，变成竖长的面板
        # 左侧面板：文字通常朝左 (顺时针旋转 90度)
        # 依据展开图逻辑，左侧面板的“底”是指向中心的，所以文字应该是“躺着”的
        canvas_left_side = canvas.rotate(-90, expand=True)
        
        # 右侧面板：文字通常朝右 (逆时针旋转 90度 )
        canvas_right_side = canvas.rotate(90, expand=True)
        
        return canvas_left_side, canvas_right_side
        
    
    def generate_exacme_top_panel(self, sku_config):
        '''生成 Exacme 方形蹦床天地盖样式的顶部面板'''
        canvas = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.w_px), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)
        
        # ================= 1. 顶部：天平布局 (Logo居中，右侧尺寸框) =================
        icon_logo = self.resources['icon_logo']
        logo_img = engine.Image(icon_logo, width=int(canvas.width * 0.22)) # Logo占宽22%
        
        # 尝试从 SKU_name 中提取尺寸 (例如: 6184-H812B-1 -> 8x12FT, 6184-H81B-1 -> 8x10FT)
        size_text = "SIZE" # 兜底文字
        
        # 正则魔法：找字母 H (忽略大小写)，后面跟着 1个数字，然后再跟着 1到2个数字
        match = re.search(r'H(\d)(\d{1,2})', sku_config.sku_name, re.IGNORECASE)
        
        if match:
            dim1 = match.group(1)  # 第一位数字，例如 '8'
            dim2 = match.group(2)  # 第二/三位数字，例如 '12' 或者 '1'
            
            # 触发特殊隐藏规则：如果没有第三位数字，且第二位是 '1'，那它其实代表 '10'
            if dim2 == '1':
                dim2 = '10'
                
            # 拼接成最终需要的字符串
            size_text = f"{dim1}x{dim2}FT"
            
        font_size_top = int(canvas.height * 0.05) # 尺寸文字占高5%
        font_top = ImageFont.truetype(self.font_paths['Arial Bold'], font_size_top)
        
        box_internal_padding = int(0.8 * sku_config.dpi)
        box_radius = int(canvas.height * 0.05)
        
        # 右上角的黑色倒角尺寸框
        size_box = engine.Text(
            size_text,
            font=font_top,
            color=sku_config.background_color, # 文字颜色为背景的牛皮纸色
            padding=box_internal_padding,
            draw_background=True,
            background_color='black',
            border_radius=box_radius,
            nudge_x=-box_internal_padding - int(canvas.width * 0.02), # 让背景框紧贴文字，向左微调
            nudge_y=-box_internal_padding  # 向上微调，让背景框紧贴文字
            
        )

        top_padding = int(2 * sku_config.dpi) 

        top_row = engine.Row(
            fixed_width=canvas.width,
            justify='space-between',
            align='top',
            padding_x=top_padding, # 左右安全距离
            padding_y=top_padding, # 顶部安全距离
            children=[
                engine.Spacer(width=size_box.width, height=1), # 左侧隐形配重砖块
                logo_img,                                      # 绝对居中的主角 Logo
                size_box                                       # 右侧的小尾巴
            ]
        )

        # ================= 2. 中间：条件判定替换信息图 =================
        # 依据长宽条件选择垂直或水平的图标
        if sku_config.l_cm > 130 and sku_config.w_cm < 40:
            
            icon_middle_ori = self.resources['icon_middle_info_horizontal']
            # 中间信息图宽度大约占画布的 55%
            middle_img = engine.Image(icon_middle_ori, width=int(canvas.width * 0.93), nudge_y=int(canvas.height * 0.04)) # 水平图需要往下微调，让它看起来更靠近底部
            
            # 【魔法降临：计算绝对居中的动态间距】
            # 2.1 我们的目标：让 middle_img 的顶部，刚好落在需要的那个 Y 坐标上
            target_y = (canvas.height - middle_img.height) // 2 + int(canvas.height * 0.06) # 目标位置：绝对居中 + 向下微调3%高度，让它看起来更靠近底部
            
            # 2.2 我们算一下，在它上面，已经有哪些东西占据了空间？
            # 占据的空间 = safe_area 顶部的内边距 + top_row 自己算出来的真实总高度
            occupied_top_space = top_padding + top_row.height
            
            # 2.3 目标高度 - 被占据的高度 = 我们需要的间距！
            dynamic_spacing = target_y - occupied_top_space
            
            # 2.4 设一个防爆底线（万一图纸特别矮，防止算出来是负数导致元素重叠）
            safe_spacing = max(dynamic_spacing, int(canvas.height * 0.03))
            
        else:
            icon_middle_ori = self.resources['icon_middle_info_vertical']
            # 中间信息图宽度大约占画布的 55%
            middle_img = engine.Image(icon_middle_ori, width=int(canvas.width * 0.53))
            
            # 竖版图本身就很高，不需要强行拉开间距，继续用原来的紧凑默认值
            safe_spacing = int(canvas.height * 0.03)

        # ================= 3. 底部：全宽贴边警示条 =================
        icon_bottom_ori = self.resources['icon_bottom_info']
        
        # 3.1 制作一个纯黑的矩形底板 (宽 = 画布宽，高 = 画布高的 13%)
        bar_height = int(canvas.height * 0.13)
        bar_width = canvas.width
        black_bar = Image.new('RGBA', (bar_width, bar_height), 'black')
        
        # 3.2 缩放警示条的图标，让它适应黑框的高度 (让图标占黑框宽度的 80%，留出上下黑边)
        icon_target_width = int(bar_width * 0.80)
        icon_target_height = int(icon_bottom_ori.height * (icon_target_width / icon_bottom_ori.width))
        icon_bottom_resized = icon_bottom_ori.resize((icon_target_width, icon_target_height), Image.Resampling.LANCZOS)
        
        # 3.3 把警示图标贴在黑板的正中间 (完美居中计算)
        paste_x = (bar_width - icon_target_width) // 2
        paste_y = (bar_height - icon_target_height) // 2
        black_bar.paste(icon_bottom_resized, (paste_x, paste_y), mask=icon_bottom_resized) # 用 mask 保证透明背景正常显示
        
        # 3.4 把它变成引擎可以识别的组件
        bottom_block = engine.Image(black_bar)

        # ================= 4. 终极防爆大管家 =================
        top_padding = int(1.5 * sku_config.dpi) # 1.5厘米安全内边距
        
        # 为了让顶部的 Logo 和中间的图不贴边，我们给它们单独套一个小盒子加 padding
        safe_area_column = engine.Column(
            
            align='center',
            spacing = safe_spacing, # 顶部和中间图的间距
            padding_y=top_padding,             # 上下留出安全距离
            children=[
                top_row,
                middle_img,
            ]
        )
        
        # 最外层大管家：绝对纯洁，padding=0！
        main_panel = engine.Column(
            fixed_width=canvas.width,
            fixed_height=canvas.height,
            justify='space-between', # 让 safe_area 顶在上面，黑条踩在最底线
            align='center',          
            padding=0,               # 【关键】大管家 0 padding，保证黑条 100% 贴边！
            children=[
                safe_area_column,    # 上半部分（自带安全区）
                bottom_block         # 下半部分（全宽黑条，完美贴边）
            ]
        )
        
        # 5. 一键渲染
        main_panel.layout(0, 0)
        main_panel.render(draw)
        
        canvas_top = canvas
        return canvas_top
    
    
    def fill_left_and_right_label_wide(self, sku_config, img_label, fonts_paths):
        """
        填充 Exacme 天地盖样式左右侧面板的宽标签区域
        使用 generate_barcode_image 生成纯条形码，然后手动绘制文字
        """
        # 【救命级修复】一定要 copy！否则会污染资源字典里的原图模板！
        icon_side_label = img_label.copy()
        draw = ImageDraw.Draw(icon_side_label)
        
        # 1. 动态基础尺寸
        content_w = int(icon_side_label.width * 0.95)  
        content_h = int(icon_side_label.height * 0.78)
        
        # 2. 准备所有需要的字体
        font_size_huge = int(content_h * 0.5088) 
        font_huge = ImageFont.truetype(fonts_paths['Arial Black'], font_size_huge)
        
        font_size_box = int(content_h * 0.18)
        font_box = ImageFont.truetype(fonts_paths['Arial Bold'], font_size_box)
        
        font_size_info = int(content_h * 0.14)
        font_info_bold = ImageFont.truetype(fonts_paths['Arial Bold'], font_size_info)
        font_info_regular = ImageFont.truetype(fonts_paths['Arial Regular'], font_size_info) # 新增常规体
        
        font_size_barcode = int(content_h * 0.08)
        font_barcode = ImageFont.truetype(fonts_paths['Arial Regular'], font_size_barcode)

        # ================= 3. 组装第一排：SKU 和 箱数 =================
        box_text = f"Box {sku_config.box_number['current_box']} of {sku_config.box_number['total_boxes']}"
        box_padding = int(0.26 * sku_config.dpi) 
        
        row1 = engine.Row(
            fixed_width=content_w,
            justify='space-between', 
            align='center', 
            children=[
                engine.Text(sku_config.sku_name, font=font_huge),
                engine.Text(
                    box_text, 
                    font=font_box, 
                    color=sku_config.background_color, 
                    draw_background=True,
                    background_color='black',
                    border_radius=0,                   
                    padding=box_padding,
                    nudge_x=-box_padding - int(content_w * 0.02), # 向左微调，让黑框右边缘紧贴下方图标，同时留出一点点间距让它不至于太挤
                    nudge_y=-box_padding
                )
            ]
        )

        # ================= 4. 组装第二排：文字信息 和 双条码 =================
        # 4.1 左侧：重量与尺寸垂直排列 (粗细拆分 + 完美对齐)
        gw_label = "G.W./N.W. : "
        box_label = "BOX SIZE : "
        
        # 量一下两个粗体标签的真实宽度
        gw_w = font_info_bold.getbbox(gw_label)[2] - font_info_bold.getbbox(gw_label)[0]
        box_w = font_info_bold.getbbox(box_label)[2] - font_info_bold.getbbox(box_label)[0]
        
        row_gw = engine.Row(
            align='bottom',
            spacing=10,
            children=[
                engine.Text(gw_label, font=font_info_bold),
                engine.Text(f"{sku_config.side_text['gw_value']} / {sku_config.side_text['nw_value']} LBS", font=font_info_regular)
            ]
        )
        
        row_box = engine.Row(
            align='bottom',
            spacing=10,
            children=[
                engine.Text(box_label, font=font_info_bold),
                engine.Spacer(width=gw_w - box_w, height=1), # 填补宽度差，让后面的数值完美对齐！
                engine.Text(f"{sku_config.l_in:.1f}\" x {sku_config.w_in:.1f}\" x {sku_config.h_in:.1f}\"", font=font_info_regular)
            ]
        )

        info_column = engine.Column(
            align='left',
            spacing=int(content_h * 0.08), 
            children=[row_gw, row_box]
        )
        
        # 4.2 右侧：生成双条码
        barcode_h = int(content_h * 0.28)
        barcode_w_sku = int(barcode_h * 3.5) 
        barcode_w_sn = int(barcode_h * 2.7) 
        
        img_barcode_sku = general_functions.generate_barcode_image(sku_config.sku_name, width=barcode_w_sku, height=barcode_h)
        img_barcode_sn = general_functions.generate_barcode_image(sku_config.side_text['sn_code'], width=barcode_w_sn, height=barcode_h)
        
        barcode_col_left = engine.Column(
            align='center',
            spacing=int(content_h * 0.02),
            children=[
                engine.Image(img_barcode_sku),
                engine.Text(sku_config.sku_name, font=font_barcode)
            ]
        )
        barcode_col_right = engine.Column(
            align='center',
            spacing=int(content_h * 0.02),
            children=[
                engine.Image(img_barcode_sn),
                engine.Text(sku_config.side_text['sn_code'], font=font_barcode)
            ]
        )
        
        barcodes_row = engine.Row(
            spacing=int(content_w * 0.014), 
            align='bottom',
            children=[barcode_col_left, barcode_col_right]
        )
        
        # 4.3 组装完整的第二排
        row2 = engine.Row(
            fixed_width=content_w,
            justify='start',
            spacing=int(content_w * 0.02),   # 文字和条码之间固定间距
            align='center', 
            children=[
                info_column,
                barcodes_row
            ]
        )

        # ================= 5. 总管家合体与居中渲染 =================
        main_panel = engine.Column(
            align='left',
            spacing=int(content_h * 0.11), 
            children=[
                row1, 
                row2
            ]
        )
        
        main_panel.layout(0, 0)
        
        start_x = (icon_side_label.width - content_w) // 2
        start_y = int(icon_side_label.height * 0.11) 
        
        main_panel.layout(start_x, start_y)
        main_panel.render(draw)
        
        # icon_side_label.show()
        
        return icon_side_label
    
    def fill_left_and_right_label_high(self, sku_config, img_label, fonts_paths):
        """填充 Exacme 天地盖样式左右侧面板的高标签区域
        使用 generate_barcode_image 生成纯条形码，然后手动绘制文字
        """
        
        icon_side_label_ori = img_label
        # 这个面板就只放一个侧唛标签，调整它的大小，让它占满整个侧身, 所以就不单独放到一个函数里生成图片，也不用放到容器里了
        icon_side_label = icon_side_label_ori.rotate(-90, expand=True) # 先旋转90度，让它变成长条形，方便后续调整宽度占满整个侧身

        # 把icon_side_label作为一个新的canvas
        draw = ImageDraw.Draw(icon_side_label)
        
        ############ 左侧文字区 ############
        # 1. 准备字体
        font_size_bold = int(icon_side_label.height * 0.052) # 字体大小占侧身高度的 5%
        font_size_normal = int(icon_side_label.height * 0.043) # 字体大小占侧身高度的 4%
        
        font_bold = ImageFont.truetype(fonts_paths['Arial Bold'], font_size_bold)
        font_normal = ImageFont.truetype(fonts_paths['Arial Regular'], font_size_normal)

        # 2. 像串糖葫芦一样拼装每一行 (Row)
        row_color = engine.Row(
            spacing=10, # 粗体和细体中间隔 10 个像素
            children=[
                engine.Text("COLOUR  :", font=font_bold),
                engine.Text(sku_config.color, font=font_normal) # 动态颜色
            ]
        )

        row_weight_lbs = engine.Row(
            spacing=10,
            children=[
                engine.Text("G.W./N.W. :", font=font_bold),
                engine.Text(f"{sku_config.side_text['gw_value']} / {sku_config.side_text['nw_value']} LBS", font=font_normal)
            ]
        )

        # 【小魔法】：对于第二行需要缩进的 KG 重量，
        # 你可以直接塞一个不可见的 Element 进去当“隐形砖块”占位！
        # 先获取 "G.W./N.W. :" 这串字在当前动态字号下的真实包围盒
        gw_bbox = font_bold.getbbox("G.W./N.W. :")
        # 真实宽度 = 右边界 - 左边界
        gw_text_width = gw_bbox[2] - gw_bbox[0] 
        
        # 制造一个绝对精准的隐形砖块！
        indent_spacer = engine.Spacer(width=gw_text_width, height=1)

        row_weight_kg = engine.Row(
            spacing=10,
            children=[
                indent_spacer, # 隐形砖块在左边顶着
                engine.Text(f"{sku_config.side_text['gw_value']/ 2.20462:.1f} / {sku_config.side_text['nw_value']/ 2.20462:.1f} KG", font=font_normal)
            ]
        )

        row_box_size_inch = engine.Row(
            spacing=10,
            children=[
                engine.Text("BOX SIZE :", font=font_bold),
                engine.Text(f"{sku_config.l_cm/2.54:.1f}\" x {sku_config.w_cm/2.54:.1f}\" x {sku_config.h_cm/2.54:.1f}\"", font=font_normal)
            ]
        )
        
        row_box_size_cm = engine.Row(
            spacing=10,
            children=[
                indent_spacer, # 同样的隐形砖块，保持和重量信息的对齐
                engine.Text(f"{sku_config.l_cm:.1f}cm x {sku_config.w_cm:.1f}cm x {sku_config.h_cm:.1f}cm", font=font_normal)
            ]
        )

        # 3. 把所有行装进大垂直容器 (Column)
        left_text_block = engine.Column(
            align='left',  # 【关键】所有行统一靠左对齐
            spacing=25,    # 行与行之间的上下间距
            children=[
                row_color,
                row_weight_lbs,
                row_weight_kg,
                row_box_size_inch,
                row_box_size_cm
            ]
        )

        # ================= 渲染 =================
        # 最后，只需指定这个大方块的左上角起点，一键渲染！
        left_text_block.layout(x=26, y=250) 
        left_text_block.render(draw)
        
        
        ############ 顶部SKU_name 和 箱号区 ############
        text_sku_name = sku_config.sku_name
        text_box_number = f"Box {sku_config.box_number['current_box']} of {sku_config.box_number['total_boxes']}"
        # sku_name字号占侧身宽度的 78%
        font_sku_name_target_width = int(icon_side_label.width * 0.670)
        font_box_number_target_width = int(icon_side_label.width * 0.30)
        
        font_size_sku_name = general_functions.get_max_font_size(text_sku_name, self.font_paths['Arial Regular'], font_sku_name_target_width) # 获取最大字号 
        font_size_box_number = general_functions.get_max_font_size(text_sku_name, self.font_paths['Arial Bold'], font_box_number_target_width) # 获取最大字号
        
        font_sku_name = ImageFont.truetype(self.font_paths['Arial Bold'], font_size_sku_name)
        font_box_number = ImageFont.truetype(self.font_paths['Arial Regular'], font_size_box_number) # 箱号和 SKU_name 字体大小一致，但使用常规体
        
        ## 直接渲染在侧唛标签的顶部中心位置
        # bbox = draw.textbbox((0, 0), text_sku_name, font=font_sku_name)
        # text_width = bbox[2] - bbox[0]
        # text_x = (icon_side_label.width - text_width) / 2
        # text_y = -bbox[1] + 20  # 用字体内部偏移抵消，让文字真正贴顶
        # draw.text((text_x, text_y), text_sku_name, font=font_sku_name, fill=(0, 0, 0, 0)) # 颜色为透明色，用背景色填充，达到隐藏文字的效果
        
        sku_name_block = engine.Text(text_sku_name, font=font_sku_name, color=sku_config.background_color) # 颜色为背景色，达到隐藏文字的效果
        box_number_block = engine.Text(text_box_number, font=font_box_number, color=sku_config.background_color) # 颜色为背景色，达到隐藏文字的效果
        
        spacing_top_text_block = int(icon_side_label.width * 0.7) # 顶部安全距离
        
        padding_x_top_text_block = int(icon_side_label.height * 0.12) # 左右安全距离
        padding_y_top_text_block = int(icon_side_label.height * 0.06) # 顶部安全距离
        top_text_block = engine.Row(
            justify='space-between',
            fixed_width=icon_side_label.width,
            align='bottom',
            spacing=spacing_top_text_block,
            padding_x = padding_x_top_text_block, # 距离左右边缘的安全距离
            padding_y = padding_y_top_text_block, # 距离底部 50 像素的安全
            children=[
                sku_name_block,
                box_number_block
            ]
        )
        
        top_text_block.layout(x=0, y=0) # 先布局，获取整体宽高
        top_text_block.render(draw) # 再渲染
        
        ############ 中间条码区 ############
        barcode_image_left_text = sku_config.sku_name # 条码下方的文字和侧唛顶部SKU_name保持一致
        barcodee_image_right_right = sku_config.side_text['sn_code'] # 条码下方右侧的文字来自side_text里的sn_code
        
        # 条码文字大小
        font_barcode_size = int(icon_side_label.height * 0.05) # 条码文字大小占侧身高度的 5%
        font_barcode = ImageFont.truetype(self.font_paths['Arial Regular'], font_barcode_size)
        
        # 条码高度
        barcode_height = int(icon_side_label.height * 0.30) # 条码高度占侧身高度的 30%
        
        # 条码宽度
        barcode_image_left_width = int(barcode_height * 2.9) # 条码宽度是高度的 2.7 倍
        barcode_image_right_width = int(barcode_height * 2.0)
        
        # 生成条码图片
        barcode_image_left = general_functions.generate_barcode_image(barcode_image_left_text, width=barcode_image_left_width, height=barcode_height)
        barcode_image_right = general_functions.generate_barcode_image(barcodee_image_right_right, width=barcode_image_right_width, height=barcode_height)
        
        # 生成两个垂直容器分别放左侧和右侧的条码图片+文字
        barcode_block_left = engine.Column(
            align='center',
            spacing=10,
            children=[
                engine.Image(barcode_image_left),
                engine.Text(barcode_image_left_text, font=font_barcode)
            ]
        )
        barcode_block_right = engine.Column(
            align='center',
            spacing=10,
            children=[
                engine.Image(barcode_image_right),
                engine.Text(barcodee_image_right_right, font=font_barcode)
            ]
        )
        
        # 把条码区放在侧唛标签的底部中心位置
        barcode_block = engine.Row(
            justify='center',
            align='bottom',
            padding=50, # 距离底部 50 像素的安全
            children=[
                barcode_block_left,
                engine.Spacer(width=40, height=1), # 条码之间的水平间距
                barcode_block_right
            ]
        )
        
        
        barcode_block.layout(x=560, y=195) # 先布局，获取整体宽高
        barcode_block.render(draw) # 再渲染
        
        # icon_side_label.show()
        
        return icon_side_label