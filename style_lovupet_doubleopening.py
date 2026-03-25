# -*- coding: utf-8 -*-
"""
Lovupet 对开盖样式 - 将原有的 BoxMarkEngine 转换为样式类
"""
from PIL import Image, ImageDraw, ImageFont
import pathlib as Path
from style_base import BoxMarkStyle, StyleRegistry
import general_functions
import layout_engine as engine
import re


@StyleRegistry.register
class LovupetDoubleOpeningStyle(BoxMarkStyle):
    '''Lovupet 对开盖样式'''
    
    def get_style_name(self):
        return "lovupet_doubleopening"
    
    def get_style_description(self):
        return "Lovupet 对开盖箱唛样式"
    
    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'ppi', 'color', 'product', 'side_text', 'sku_name']
    
    def get_layout_config(self, sku_config):
        '''
        Lovupet 对开盖样式 - 5块布局（4列3行）
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
        """生成 Lovupet 对开盖样式需要的所有面板"""
        
        canvas_front = self.generate_lovupet_front_panel(sku_config)
        canvas_side = self.generate_lovupet_side_panel(sku_config)
        canvas_left_up, canvas_left_down = self.generate_lovupet_left_panel(sku_config)
        canvas_right_up, canvas_right_down = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.half_w_px), sku_config.background_color), Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.half_w_px), sku_config.background_color)
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
        """加载 Lovupet 对开盖样式的图片资源"""
        res_base = self.base_dir / 'assets' / 'Lovupet' / '对开盖' / '矢量文件'
        
        self.resources = {
            
            # 正唛有网址、logo、猫抓图、宠物图
            'icon_logo': Image.open(res_base / 'logo.png').convert('RGBA'),
            'icon_web': Image.open(res_base / '网址框.png').convert('RGBA'),
            'icon_product': Image.open(res_base / '宠物.png').convert('RGBA'),
            'icon_catclaw': Image.open(res_base / '猫抓.png').convert('RGBA'),
            
            # 侧唛有宠物图、标签框
            'icon_paste_barcode': Image.open(res_base / '条形码定界框.png').convert('RGBA'),
            'icon_product': Image.open(res_base / '宠物.png').convert('RGBA'),
            'icon_side_label': Image.open(res_base / '注意事项.png').convert('RGBA'),
            
            # 左上盖有一个箱子提示语
            'icon_box_hint': Image.open(res_base / '箱子提示语.png').convert('RGBA'),
        }
    
    def _load_fonts(self):
        """加载字体路径"""
        font_base = self.base_dir / 'assets' / 'Lovupet' / '对开盖' / '箱唛字体'
        self.font_paths = {
            'Arial Regular': str(font_base / 'arial.ttf'),
            'Arial Bold': str(font_base / 'arialbd.ttf'),
            'Arial Black': str(font_base / 'ariblk.ttf'),
            'Calibri Regular': str(font_base / 'calibri.ttf'),
            'Calibri Bold': str(font_base / 'calibri bold.ttf'),
            'Calibri Light': str(font_base / 'Calibri_Light.ttf'),
        }
    
    def generate_lovupet_left_panel(self, sku_config):
        """生成 Lovupet 对开盖样式的左侧盖面板（包含箱子提示语）"""
        canvas_up = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.half_w_px), sku_config.background_color)
        canvas_down = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.half_w_px), sku_config.background_color)
        
        # 粘贴箱子提示语
        hint_img = self.resources['icon_box_hint']
        hint_img_target_width = int(canvas_up.width * 0.8)
        
        general_functions.paste_image_center_with_heightorwidth(canvas_up, hint_img, width=hint_img_target_width)
        
        return canvas_up, canvas_down
    
    def generate_lovupet_front_panel(self, sku_config):
        """生成 Lovupet 对开盖样式的正面板（包含网址、logo、猫抓图、宠物图）"""
        canvas = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.h_px), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)

        ####### 顶部column #########
        # 粘贴 logo
        logo_img = self.resources['icon_logo']
        logo_img_target_width = int(canvas.width * 0.72)
        
        # 画三个实心圆，然后在上面加入sku_name文本
        cloud_color_img = generate_cloud_color_image(
            sku_config=sku_config,
            font_path=self.font_paths['Arial Bold'], # 用个粗体字更显眼
            base_size=int(canvas.width * 0.47)        # 三个圆重叠后的长
        )
        cloud_color_img_target_width = int(canvas.width * 0.40)
        
        upper_col = engine.Column(
            align = 'center',
            spacing = int(canvas.height * 0.03),
            children = [
                engine.Image(logo_img, width=logo_img_target_width),
                engine.Image(cloud_color_img, width=cloud_color_img_target_width)
            ]
        )
        
        ####### 中部column #########
        # 粘贴宠物图
        product_img = self.resources['icon_product']
        product_img_target_width = int(canvas.width * 0.95)
        
        # 粘贴网址框
        web_img = self.resources['icon_web'] 
        web_img_target_width = int(canvas.width * 0.78)
        
        middle_col = engine.Column(
            align = 'center',
            spacing = int(canvas.height * 0.018),
            children = [
                engine.Image(product_img, width=product_img_target_width),
                engine.Image(web_img, width=web_img_target_width)
            ]
        )
        
        # ####### 底部column #########
        # 粘贴猫抓图
        catclaw_img = self.resources['icon_catclaw']
        catclaw_img_target_width = int(canvas.width * 0.5)
        
        # 计算黑色矩形框的实际像素高度 (精准 10cm)
        box_height_cm = 10
        total_box_height_px = int(box_height_cm * sku_config.dpi)

        # 创建纯黑色底框并绘制 SKU 文字
        box_image_obj = Image.new('RGBA', (canvas.width, total_box_height_px), (0, 0, 0, 255))
        box_draw = ImageDraw.Draw(box_image_obj)
        sku_text = sku_config.sku_name if sku_config.sku_name else "SKU12345"
        font_sku_max_width = int(box_image_obj.width * 0.95)
        font_sku_max_height = int(box_image_obj.height * 0.7)
        font_sku_size = general_functions.get_max_font_size(
            sku_text,
            self.font_paths['Arial Bold'],
            font_sku_max_width,
            font_sku_max_height
        )
        font_obj = ImageFont.truetype(self.font_paths['Arial Bold'], font_sku_size)
        box_draw.text(
            (box_image_obj.width // 2, box_image_obj.height // 2),
            sku_text,
            fill=sku_config.background_color,
            font=font_obj,
            anchor="mm"
        )

        # 黑框绝对贴底，脱离布局引擎，确保猫抓图下边缘与黑框上边缘精准对齐
        canvas.paste(box_image_obj, (0, canvas.height - total_box_height_px), mask=box_image_obj)

        ####### 整体布局 #########
        upper_blank_height_px = int(7 * sku_config.dpi)

        # fixed_height 扣除底框高度，使猫抓图底部恰好对接黑框顶部
        main_layout = engine.Column(
            justify = 'space-between',
            fixed_height = int(canvas.height - upper_blank_height_px - total_box_height_px),
            align = 'center',
            spacing = int(canvas.height * 0.05),
            children = [
                upper_col,
                middle_col,
                engine.Image(catclaw_img, width=catclaw_img_target_width)
            ]
        )
        
        main_layout.layout( x = 0, y = upper_blank_height_px )
        main_layout.render(draw)
        
        return canvas
    
    def generate_lovupet_side_panel(self, sku_config):
        """ 生成 Lovupet 对开盖样式的侧面板（包含注意事项标签和Logo）"""
        canvas = Image.new(sku_config.color_mode, (sku_config.w_px, sku_config.h_px), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)
        
        # === 1. 右上角：条形码定界框 ===
        icon_barcode = self.resources['icon_paste_barcode'].rotate(90, expand=True) # 旋转90度适应侧唛竖向布局
        barcode_height = int(sku_config.dpi * 5) # 条形码高度固定为5cm
        
        # 用 Row 容器，左边用 Spacer 撑开，实现绝对靠右排版
        top_row = engine.Row(
            justify='space-between',
            fixed_width=canvas.width,
            padding_x=int(canvas.width * 0.08), # 右边留出 8% 的边距
            children=[
                engine.Spacer(width=1), # 左边隐形砖块
                engine.Image(icon_barcode, height=barcode_height)
            ]
        )
        
        # === 2. 中部：Lovupet Logo ===
        icon_logo = self.resources['icon_logo']
        logo_width = int(canvas.width * 0.71)
        
        # === 3. 下部：包含动态数据的标签框 ===
        icon_label = self.resources['icon_side_label']
        label_width = int(canvas.width * 0.92)
        label_height = int(icon_label.height * (label_width / icon_label.width))
        icon_label_resized = icon_label.resize((label_width, label_height), Image.Resampling.LANCZOS)
        
        # 调用我们专门写的函数，把文字和条形码填进去
        icon_label_filled = self.fill_lovupet_side_label(icon_label_resized, sku_config)
        
        # === 4. 最底部：10 厘米黑色底框 ===
        box_height_cm = 10
        total_box_height_px = int(box_height_cm * sku_config.dpi)
        box_image_obj = Image.new('RGBA', (canvas.width, total_box_height_px), (0, 0, 0, 255))
        box_draw = ImageDraw.Draw(box_image_obj)

        sku_text = sku_config.sku_name if sku_config.sku_name else "SKU12345"
        font_sku_max_width = int(box_image_obj.width * 0.95)
        font_sku_max_height = int(box_image_obj.height * 0.7) 
        font_sku_size = general_functions.get_max_font_size(
            sku_text, self.font_paths['Arial Bold'], font_sku_max_width, font_sku_max_height)
        font_obj = ImageFont.truetype(self.font_paths['Arial Bold'], font_sku_size)

        box_draw.text(
            (box_image_obj.width // 2, box_image_obj.height // 2), 
            sku_text, 
            fill=sku_config.background_color, # 黑色底框写背景色文字
            font=font_obj, 
            anchor="mm"
        )
        
        # 黑框绝对贴底，确保注意事项标签下边缘不被遮挡
        canvas.paste(box_image_obj, (0, canvas.height - total_box_height_px), mask=box_image_obj)

        # === 5. 组装整体排版引擎 ===
        upper_blank_height_px = int(5 * sku_config.dpi)

        # fixed_height 扣除底框高度，内容在底框上方布局
        main_layout = engine.Column(
            justify='space-between',
            fixed_height=int(canvas.height - upper_blank_height_px - total_box_height_px),
            align='center',
            children=[
                top_row,
                engine.Image(icon_logo, width=logo_width, nudge_y = int(canvas.height * 0.03)), # logo稍微往上挪一点，避免和条形码贴得太紧
                engine.Image(icon_label_filled, nudge_y = -int(canvas.height * 0.11)) # 标签框稍微往上挪一点，避免和底框贴得太紧,
            ]
        )
        
        main_layout.layout(0, upper_blank_height_px)
        main_layout.render(draw)
        
        return canvas

    def fill_lovupet_side_label(self, label_img, sku_config):
        """专属辅助函数：在侧唛标签上精准填入文字和条形码"""
        canvas = label_img.copy()
        draw = ImageDraw.Draw(canvas)
        W, H = canvas.size
        
        # --- 1. 准备文本 ---
        gw_val = sku_config.side_text.get('gw_value', '0.0')
        nw_val = sku_config.side_text.get('nw_value', '0.0')
        weight_text = f"G.W./N.W. : {gw_val} / {nw_val} lbs"
        
        # 注意原图这里是英寸
        box_text = f"BOX SIZE : {sku_config.l_in:.1f}\"x{sku_config.w_in:.1f}\"x{sku_config.h_in:.1f}\""
        
        font_text = ImageFont.truetype(self.font_paths['Arial Bold'], int(H * 0.08))
        
        # 在左下角格子里写重量和尺寸 (左对齐)
        text_start_x = int(W * 0.016)
        draw.text((text_start_x, int(H * 0.72)), weight_text, fill="black", font=font_text, anchor="lm")
        draw.text((text_start_x, int(H * 0.90)), box_text, fill="black", font=font_text, anchor="lm")
        
        # --- 2. 准备条形码 ---
        barcode_h = int(H * 0.18)
        barcode_sku_w = int(W * 0.26)
        barcode_sn_w = int(W * 0.20)
        
        # 调用 general_functions 里没文字的纯条码函数
        barcode_sku = general_functions.generate_barcode_image(sku_config.sku_name, barcode_sku_w, barcode_h)
        sn_code = sku_config.side_text.get('sn_code', '0000000000')
        barcode_sn = general_functions.generate_barcode_image(sn_code, barcode_sn_w, barcode_h)
        
        # 落位坐标：右下角的格子里
        sku_x = int(W * 0.51)
        sn_x = int(W * 0.79)
        barcode_y = int(H * 0.635)
        
        canvas.paste(barcode_sku, (sku_x, barcode_y))
        canvas.paste(barcode_sn, (sn_x, barcode_y))
        
        # --- 3. 补充条形码底部的极其微小的文字 ---
        font_barcode = ImageFont.truetype(self.font_paths['Arial Regular'], int(H * 0.045))
        draw.text((sku_x + barcode_sku_w//2, barcode_y + barcode_h + int(H*0.01)), 
                  sku_config.sku_name, fill="black", font=font_barcode, anchor="mt")
        draw.text((sn_x + barcode_sn_w//2, barcode_y + barcode_h + int(H*0.01)), 
                  sn_code, fill="black", font=font_barcode, anchor="mt")
                  
        # --- 4. 补充最底部的 MADE IN CHINA ---
        font_made_in = ImageFont.truetype(self.font_paths['Arial Bold'], int(H * 0.075))
        # 在两个条码的正中央下方绝对居中
        center_x = int((sku_x + sn_x + barcode_sn_w) / 2)
        draw.text((center_x, int(H * 0.92)), "MADE IN CHINA", fill="black", font=font_made_in, anchor="mm")
        
        return canvas
        
        
    


def generate_cloud_color_image(sku_config, font_path, base_size=500, bg_color=None):
    """
    生成一个包含产品颜色（如 "White"）的水平三圆重叠“云朵/胶囊”形状图片。
    不再会被切边！
    """
    if bg_color is None:
        bg_color = (0, 0, 0, 255)  # 默认黑色圆圈

    color_text = sku_config.color if sku_config.color else "White"

    # === 1. 动态数学计算 (绝对防切边魔法) ===
    # 我们把 base_size 视为你期望的最终总宽度，反推圆的半径和间距
    # 假设总宽度 W = 左圆半径 + 两个间距 + 右圆半径 = 2*R + 2*offset
    # 如果 offset = 1.3 * R，那么 W = 4.6 * R
    R = int(base_size / 4.6)
    offset = int(R * 1.3)  # 控制间距，1.3 刚好有漂亮的凹槽
    
    # 算出一个极其精准的画布尺寸，一像素都不多，一像素都不被切！
    total_w = 2 * R + 2 * offset
    total_h = 2 * R
    
    # 2. 创建精准大小的透明画布
    img = Image.new('RGBA', (total_w, total_h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 3. 计算三个圆的圆心坐标 (Y轴全部在正中间)
    Cy = R
    C1_x = R                  # 左圆心
    C2_x = R + offset         # 中圆心
    C3_x = R + 2 * offset     # 右圆心
    
    def get_circle_bbox(cx, cy, r):
        return (cx-r, cy-r, cx+r, cy+r)
        
    # 4. 绘制三个实心圆
    draw.ellipse(get_circle_bbox(C1_x, Cy, R), fill=bg_color, outline=None)
    draw.ellipse(get_circle_bbox(C2_x, Cy, R), fill=bg_color, outline=None)
    draw.ellipse(get_circle_bbox(C3_x, Cy, R), fill=bg_color, outline=None)
    
    # 5. 动态计算文字大小
    max_text_w = int(offset * 2 + R * 1.67)
    font_size = int(total_h * 0.55)  # 字号稍微小一点点，给上下留出呼吸感
    font = ImageFont.truetype(font_path, font_size)
    
    while font_size > 10:
        bbox = draw.textbbox((0, 0), color_text, font=font)
        text_w = bbox[2] - bbox[0]
        if text_w <= max_text_w:
            break
        font_size -= 2
        font = ImageFont.truetype(font_path, font_size)
        
    # 6. 绝对居中绘制文字（X轴为画布一半，Y轴为圆心）
    draw.text((total_w // 2, Cy), color_text, fill=sku_config.background_color, font=font, anchor="mm")
    
    # 7. 裁掉可能残留的极其微小的透明边缘
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    return img