# -*- coding: utf-8 -*-
"""
Exacme 全搭盖样式 - 将原有的 BoxMarkEngine 转换为样式类
"""
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import pathlib as Path
from style_base import BoxMarkStyle, StyleRegistry
import general_functions
import layout_engine as engine
import re


@StyleRegistry.register
class ExacmeFullOverlapStyle(BoxMarkStyle):
    '''Exacme 全搭盖样式'''
    
    def get_style_name(self):
        return "exacme_fulloverlap"
    
    def get_style_description(self):
        return "Exacme 全搭盖箱唛样式"
    
    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'ppi', 'color', 'side_text', 'sku_name']
    
    def get_layout_config(self, sku_config):
        '''
        Exacme 全搭盖样式 - 5块布局（4列3行）
        '''
        
        x0 = 0
        x1 = sku_config.l_px
        x2 = sku_config.l_px + sku_config.w_px
        x3 = sku_config.l_px * 2 + sku_config.w_px
        
        y0 = 0
        y1 = sku_config.w_px
        y2 = sku_config.w_px + sku_config.h_px
        
        return {
            # 第一行：顶盖层 (Top Flaps)
            "flap_top_front1":  (x0, y0, sku_config.l_px, sku_config.w_px),
            "flap_top_side1": (x1, y0, sku_config.w_px, sku_config.w_px),
            "flap_top_front2":  (x2, y0, sku_config.l_px, sku_config.w_px),
            "flap_top_side2": (x3, y0, sku_config.w_px, sku_config.w_px),

            # 第二行：正身层 (Main Body)
            "panel_front1":     (x0, y1, sku_config.l_px, sku_config.h_px),
            "panel_side1":    (x1, y1, sku_config.w_px, sku_config.h_px),
            "panel_front2":     (x2, y1, sku_config.l_px, sku_config.h_px),
            "panel_side2":    (x3, y1, sku_config.w_px, sku_config.h_px),

            # 第三行：底盖层 (Bottom Flaps)
            "flap_btm_front1":  (x0, y2, sku_config.l_px, sku_config.w_px),
            "flap_btm_side1": (x1, y2, sku_config.w_px, sku_config.w_px),
            "flap_btm_front2":  (x2, y2, sku_config.l_px, sku_config.w_px),
            "flap_btm_side2": (x3, y2, sku_config.w_px, sku_config.w_px),
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
        
    # ── fpdf2 required abstract methods (hybrid PIL → PDF) ──────────────────

    def get_layout_config_mm(self, sku_config):
        """mm-based layout for fpdf2 (mirrors get_layout_config in mm)"""
        l_mm = sku_config.l_cm * 10
        w_mm = sku_config.w_cm * 10
        h_mm = sku_config.h_cm * 10

        x0, x1 = 0.0, l_mm
        x2, x3 = l_mm + w_mm, 2 * l_mm + w_mm
        y0, y1, y2 = 0.0, w_mm, w_mm + h_mm

        return {
            "flap_top_front1": (x0, y0, l_mm, w_mm),
            "flap_top_side1":  (x1, y0, w_mm, w_mm),
            "flap_top_front2": (x2, y0, l_mm, w_mm),
            "flap_top_side2":  (x3, y0, w_mm, w_mm),
            "panel_front1":    (x0, y1, l_mm, h_mm),
            "panel_side1":     (x1, y1, w_mm, h_mm),
            "panel_front2":    (x2, y1, l_mm, h_mm),
            "panel_side2":     (x3, y1, w_mm, h_mm),
            "flap_btm_front1": (x0, y2, l_mm, w_mm),
            "flap_btm_side1":  (x1, y2, w_mm, w_mm),
            "flap_btm_front2": (x2, y2, l_mm, w_mm),
            "flap_btm_side2":  (x3, y2, w_mm, w_mm),
        }

    def register_fonts(self, pdf: FPDF):
        pass  # hybrid PIL→PDF: panels rendered as raster images, no PDF fonts needed

    def draw_to_pdf(self, pdf: FPDF, sku_config):
        """Render via PIL panels then embed as raster images in the PDF."""
        layout_mm  = self.get_layout_config_mm(sku_config)
        panels_map = self.get_panels_mapping(sku_config)
        panels     = self.generate_all_panels(sku_config)

        r, g, b = sku_config.background_color
        pdf.set_fill_color(r, g, b)
        for _, (x, y, w, h) in layout_mm.items():
            pdf.rect(x, y, w, h, style='F')

        for region, (x, y, w, h) in layout_mm.items():
            panel_key = panels_map.get(region)
            if panel_key and panel_key in panels:
                img = panels[panel_key]
                if img is not None:
                    pdf.image(img, x=x, y=y, w=w, h=h)

    def generate_all_panels(self, sku_config):
        """生成 Exacme 全搭盖样式需要的所有面板"""
        
        canvas_front = self.generate_exacme_front_panel(sku_config)
        canvas_side = self.generate_exacme_side_panel(sku_config)
        canvas_left_up, canvas_left_down, canvas_right_up, canvas_right_down = self.generate_exacme_left_panel(sku_config)
        canvas_blank = Image.new(sku_config.color_mode, (sku_config.w_px, sku_config.w_px), sku_config.background_color)


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
        """加载 Exacme 全搭盖样式的图片资源"""
        res_base = self.base_dir / 'assets' / 'Exacme' / '全搭盖' / '矢量文件'
        
        self.resources = {
            'icon_logo_product': Image.open(res_base / '正唛公司logo及产品名称.png').convert('RGBA'),
            'icon_top_logo': Image.open(res_base / '全搭盖顶部logo.png').convert('RGBA'),
            'icon_top_attention': Image.open(res_base / '全搭盖顶部提示标.png').convert('RGBA'),
            'icon_top_smallicons': Image.open(res_base / '全搭盖顶部提示图标.png').convert('RGBA'),
            'icon_top_notice': Image.open(res_base / '全搭盖顶部保留箱子提示.png').convert('RGBA'),
            'icon_company': Image.open(res_base / '正唛公司信息.png').convert('RGBA'),
            'icon_side_label': Image.open(res_base / '侧唛标签.png').convert('RGBA'),
        }
    
    def _load_fonts(self):
        """加载字体路径"""
        font_base = self.base_dir / 'assets' / 'Exacme' / '全搭盖' / '箱唛字体'
        self.font_paths = {
            'Arial Regular': str(font_base / 'arial.ttf'),
            'Arial Bold': str(font_base / 'arialbd.ttf'),
            'Arial Black': str(font_base / 'ariblk.ttf'),
        }
        
    def generate_exacme_front_panel(self, sku_config):
        # 准备画布
        canvas = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.h_px), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)
        
        # 准备字体 (根据你的设计图，左边字号大且粗，右边正常)
        font_size_top_left = int(canvas.height * 0.12) # 左上角字体大小占正身高度的 12%
        font_size_top_right = int(canvas.height * 0.08) # 右上角字体大小占正身高度的 8%
        font_top_left = ImageFont.truetype(self.font_paths['Arial Black'], font_size_top_left)
        font_top_right = ImageFont.truetype(self.font_paths['Arial Bold'], font_size_top_right)
        
        
        # 制作顶部的一整行 (魔法降临！)
        match = re.search(r'S(\d{2})', sku_config.sku_name)

        if match:
            # group(1) 代表获取括号里匹配到的那一部分
            product_size_number = match.group(1) 
            print(f"提取成功: {product_size_number}")  # 输出: 12
        else:
            print("没有找到匹配的数字")
            raise ValueError("SKU 名称格式不正确，无法提取尺寸信息")
        
        top_padding = int( 2 * sku_config.dpi )  # 顶部和左右安全距离，2厘米的像素值
        
        top_row = engine.Row(
            fixed_width = sku_config.l_px, # 锁死宽度为箱唛物理长
            justify = 'space-between',     # 开启两端对齐魔法
            padding = top_padding,         # 让文字离箱子边缘有 40px 的安全距离
            align = 'center',              # 如果左右字号不一样，让它们在同一水平中心线上
            children = [
                engine.Text(f"{product_size_number}FT", font=font_top_left),
                engine.Text(f"{sku_config.color}", font=font_top_right)
            ]
        )
        
        
        # 把正唛公司logo及产品名称放在正唛的正中间，logo的宽度占正身宽度的 37%，高度自适应
        icon_logo_product = self.resources['icon_logo_product']
        
        
        
        # 放置左下角正唛公司信息和右下角SKU_name
        icon_company = self.resources['icon_company']
        icon_company_target_width = int(canvas.width * 0.19) # 公司信息占正身宽度的 19%
        
        font_size_bottom_right = int(canvas.height * 0.14) # 右下角SKU_name字体大小占正身高度的 14%
        font_bottom_right = ImageFont.truetype(self.font_paths['Arial Bold'], font_size_bottom_right)
        # SKU 黑框内部的文字内边距 ( 1 厘米)
        sku_box_internal_padding = int(1.0  * sku_config.dpi)
        # SKU 黑框的圆角半径 (要大一点才像腰圆型)
        sku_box_radius = int(canvas.height * 0.05)
        
        bottom_row = engine.Row(
            fixed_width=sku_config.l_px,  # 锁死宽度
            justify='space-between',      # 两端对齐
            align='bottom',               # 【关键】垂直方向靠下对齐
            padding=top_padding,          # 与顶行保持一致的安全边距
            children=[
                # --- 左下角元素 ---
                # 给图片自己设置大的安全内边距，把它“撑”离左下角
                engine.Image(icon_company, width=icon_company_target_width, nudge_y=int(icon_company_target_width * icon_company.height / icon_company.width * 0.2)),  # 图片本身的高度就是它的安全边距，这样就能保证图片完全在安全区域内

                # --- 右下角元素 ---
                engine.Text(
                    sku_config.sku_name,        # 例如 "6180-S124SG"
                    font=font_bottom_right,
                    color=sku_config.background_color,              # 白字
                    padding=sku_box_internal_padding, # 文字离黑框边缘的距离
                    draw_background=True,       # 开启背景魔法
                    background_color='black',   # 黑底
                    border_radius=sku_box_radius, # 圆角
                    nudge_x = -sku_box_internal_padding, # 让整个文本块（包括背景）向左偏移，贴近右边界
                    nudge_y = -sku_box_internal_padding # 微调垂直位置，让它在视觉上更居中
                )
            ]
        )
        
        # 把 顶行、底行 全部塞进一个大 Column 里
        main_panel = engine.Column(
            fixed_height=sku_config.h_px, # 锁死整个大盒子的高度 = 箱子高度
            justify='space-between',      # 让上中下三块在垂直方向上两端对齐(中间块自动居中)
            align='center',               # 保证中间那个 center_block 在水平方向绝对居中
            padding=0,                    # 大面板也不要 padding，保证顶底贴边
            children=[
                top_row,       # 顶部行 (自带 safe padding)
                engine.Image(icon_logo_product, width=int(canvas.width * 0.37)), # 中间的公司logo和产品名称（自动居中，无需额外 padding）
                bottom_row     # 底部行 (左侧自带 padding，右侧贴边)
            ]
        )

        # ================= 渲染 =================
        # 见证奇迹：只需要告诉大管家从 (0,0) 开始干活就行了
        main_panel.layout(0, 0)
        main_panel.render(draw)
        
        return canvas
        
    def generate_exacme_side_panel(self, sku_config):
        
        icon_side_label_ori = self.resources['icon_side_label']
        # 这个面板就只放一个侧唛标签，调整它的大小，让它占满整个侧身, 所以就不单独放到一个函数里生成图片，也不用放到容器里了
        icon_side_label = icon_side_label_ori.rotate(0, expand=True) # 先旋转90度，让它变成长条形，方便后续调整宽度占满整个侧身

        # 把icon_side_label作为一个新的canvas
        draw = ImageDraw.Draw(icon_side_label)
        
        ############ 左侧文字区 ############
        # 1. 准备字体
        font_size_bold = int(icon_side_label.height * 0.052) # 字体大小占侧身高度的 5%
        font_size_normal = int(icon_side_label.height * 0.043) # 字体大小占侧身高度的 4%
        
        font_bold = ImageFont.truetype(self.font_paths['Arial Bold'], font_size_bold)
        font_normal = ImageFont.truetype(self.font_paths['Arial Regular'], font_size_normal)

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
        
        ############ 顶部SKU_name区 ############
        text_sku_name = sku_config.sku_name
        # sku_name字号占侧身宽度的 78%
        font_sku_name_target_width = int(icon_side_label.width * 0.730) 
        font_size_sku_name = general_functions.get_max_font_size(text_sku_name, self.font_paths['Arial Bold'], font_sku_name_target_width) # 获取最大字号
        font_sku_name = ImageFont.truetype(self.font_paths['Arial Bold'], font_size_sku_name)
        
        ## 直接渲染在侧唛标签的顶部中心位置
        bbox = draw.textbbox((0, 0), text_sku_name, font=font_sku_name)
        text_width = bbox[2] - bbox[0]
        text_x = (icon_side_label.width - text_width) / 2
        text_y = -bbox[1] + 20  # 用字体内部偏移抵消，让文字真正贴顶
        draw.text((text_x, text_y), text_sku_name, font=font_sku_name, fill=(0, 0, 0, 0)) # 颜色为透明色，用背景色填充，达到隐藏文字的效果
        
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
        
        
        # 准备画布（侧身尺寸：宽=w_px, 高=h_px）
        canvas = Image.new(sku_config.color_mode, (sku_config.h_px, sku_config.w_px), sku_config.background_color)
        
        # 把绘制好的横向 icon_side_label 转回竖向，再居中贴到画布上
        target_width  = int(sku_config.h_px * 0.78)
        icon_side_label_resized = general_functions.scale_by_width(icon_side_label, target_width)
        # icon_side_label.show()  # 临时调试：查看绘制完成后的侧唛标签
        general_functions.paste_image_center_with_heightorwidth(canvas, icon_side_label_resized, width=target_width)
        
        canvas = canvas.rotate(90, expand=True) # 最后再旋转回去，得到正确方向的侧身面板
        return canvas
    
    def generate_exacme_left_panel(self, sku_config):
        # 1. 准备画布
        canvas = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.w_px), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)
        
        
        ##################################top row##################################
        # 准备图片资源
        icon_top_logo = self.resources['icon_top_logo']
        
        # 准备字体 
        font_size_top_right = int(canvas.height * 0.22) # 右上角字体大小占正身高度的 22%
        font_top_right = ImageFont.truetype(self.font_paths['Arial Black'], font_size_top_right)

        # 制作顶部的一整行 (魔法降临！)
        match = re.search(r'S(\d{2})', sku_config.sku_name)

        if match:
            # group(1) 代表获取括号里匹配到的那一部分
            product_size_number = match.group(1) 
            print(f"提取成功: {product_size_number}")  # 输出: 12
        else:
            print("没有找到匹配的数字")
            raise ValueError("SKU 名称格式不正确，无法提取尺寸信息")
        
        top_padding = int( 2 * sku_config.dpi )  # 顶部和左右安全距离，2厘米的像素值
        
        top_row = engine.Row(
            fixed_width=sku_config.l_px,  # 锁死宽度
            justify='space-between',      # 两端对齐
            align='bottom',               # 【关键】垂直方向靠下对齐
            padding=top_padding,          # 与顶行保持一致的安全边距
            children=[
                # --- 左边元素 ---
                # 给图片自己设置大的安全内边距，把它“撑”离左下角
                engine.Image(icon_top_logo, width=int(canvas.width * 0.15)),
                # --- 右边元素 ---
                engine.Text(f"{product_size_number}FT", font=font_top_right)
            ]
        )
        
        
        # 两个row中间的SKU_name
        text_sku_name = sku_config.sku_name
        font_sku_name_target_width = int(canvas.width * 0.50) # SKU_name占侧身宽度的 50%
        font_sku_name_target_height = int(canvas.height * 0.30) # SKU_name占侧身高度的 30%
        font_size_sku_name = general_functions.get_max_font_size(text_sku_name, self.font_paths['Arial Bold'], font_sku_name_target_width, font_sku_name_target_height) # 获取最大字号
        font_sku_name = ImageFont.truetype(self.font_paths['Arial Bold'], font_size_sku_name)
        center_text = engine.Text(sku_config.sku_name, nudge_y = -int(canvas.height * 0.08), font=font_sku_name)
        
        
        ##################################bottom row##################################
        # 准备三个图片资源
        icon_top_notice = self.resources['icon_top_notice']
        icon_top_attention = self.resources['icon_top_attention']
        icon_top_smallicons = self.resources['icon_top_smallicons']
        
        # 加入底部容器
        bottom_row = engine.Row(
            fixed_width=sku_config.l_px,  # 锁死宽度
            justify='space-between',      # 两端对齐
            align='bottom',               # 【关键】垂直方向靠下对齐
            padding=top_padding,          # 与顶行保持一致的安全边距
            children=[
                engine.Image(icon_top_notice, width=int(canvas.width * 0.22)),
                engine.Image(icon_top_attention, width=int(canvas.width * 0.35), nudge_x=-int(canvas.width * 0.05)),
                engine.Image(icon_top_smallicons, width=int(canvas.width * 0.12)),
            ]
        )
        
        
        # ================= 渲染 =================
        # 把 顶行、底行 全部塞进一个大 Column 里
        main_panel = engine.Column(
            fixed_height=sku_config.w_px, # 锁死整个大盒子的高度 = 箱子高度
            justify='space-between',      # 让上中下三块在垂直方向上两端对齐(中间块自动居中)
            align='center',               # 保证中间那个 center_block 在水平方向绝对居中
            padding=0,                    # 大面板也不要 padding，保证顶底贴边
            children=[
                top_row,       # 顶部行 (自带 safe padding)
                center_text,   # 中间SKU_name（自动居中，无需额外 padding）
                bottom_row     # 底部行 (左侧自带 padding，右侧贴边)
            ]
        )

        # ================= 渲染 =================
        # 见证奇迹：只需要告诉大管家从 (0,0) 开始干活就行了
        main_panel.layout(0, 0)
        main_panel.render(draw)
        
        
        canvas_left_up = canvas.copy()
        canvas_right_down = canvas.rotate(180, expand=True) # 旋转180度作为右下角的面板
        # left_down 和 right_up 为空白面板，单独新建，避免引用到已绘制的 canvas
        canvas_left_down = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.w_px), sku_config.background_color)
        canvas_right_up  = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.w_px), sku_config.background_color)
        return canvas_left_up, canvas_left_down, canvas_right_up, canvas_right_down