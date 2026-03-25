"""
@author: Yushu&Cankun
"""


from PIL import Image, ImageDraw, ImageFont
from style_base import BoxMarkStyle, StyleRegistry
import general_functions
import layout_engine as engine

@StyleRegistry.register
class ExacmeTopAndBottomDoubleRingAndBuriedTrampolineStyle(BoxMarkStyle):
    '''Exacme 双圈和埋地天地盖样式'''

    def get_style_name(self):
        return "exacme_topandbottom_doubleringandburiedtrampoline"

    def get_style_description(self):
        return "Exacme 双圈和埋地蹦床天地盖样式"

    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'product', 'color', 'side_text', 'sku_name', 'box_number']

    def get_layout_config(self, sku_config):
        '''
        Exacme 双圈和埋地天地盖样式 - 5块布局（3列3行）
        修正布局：中间大面 (L x W)，上下侧面 (L x H)，左右侧面 (H x W)
        '''
        x0 = 0
        x1 = sku_config.h_px
        x2 = sku_config.h_px + sku_config.l_px

        y0 = 0
        y1 = sku_config.h_px
        y2 = sku_config.h_px + sku_config.w_px

        return {
            "back_side_panel": (x1, y0, sku_config.l_px, sku_config.h_px),
            "left_side_panel": (x0, y1, sku_config.h_px, sku_config.w_px),
            "top_panel": (x1, y1, sku_config.l_px, sku_config.w_px),
            "right_side_panel": (x2, y1, sku_config.h_px, sku_config.w_px),
            "front_side_panel": (x1, y2, sku_config.l_px, sku_config.h_px)
        }

    def get_panels_mapping(self, sku_config):
        return {
            'top_panel': 'main_panel',
            'back_side_panel': 'long_side_upper',
            'front_side_panel': 'long_side_lower',
            'left_side_panel': 'short_side_left',
            'right_side_panel': 'short_side_right'
        }

    def generate_all_panels(self, sku_config):
        canvas_main = self.generate_exacme_main_panel(sku_config)
        canvas_long_side = self.generate_exacme_long_side_panel(sku_config)
        canvas_short_left, canvas_short_right = self.generate_exacme_short_side_panels(sku_config)

        # 生成 Upper (Back) 需要旋转 180 度
        canvas_long_upper = canvas_long_side.rotate(180)
        canvas_long_lower = canvas_long_side

        return {
            'main_panel': canvas_main,
            'long_side_upper': canvas_long_upper,
            'long_side_lower': canvas_long_lower,
            'short_side_left': canvas_short_left,
            'short_side_right': canvas_short_right
        }

    def _load_resources(self):
        """加载 Exacme 双圈和埋地蹦床天地盖样式的图片资源"""
        res_base = self.base_dir / 'assets' / 'Exacme' / '双圈和埋地蹦床天地盖' / '矢量文件'

        self.resources = {
            'logo': Image.open(res_base / '1.6185-D正唛logo.png').convert('RGBA'),
            'line_drawing': Image.open(res_base / '2.6185-D正唛线描图.png').convert('RGBA'),
            'color_frame': Image.open(res_base / '3.正唛颜色底框.png').convert('RGBA'),
            'empty_frame': Image.open(res_base / '4.正唛空白框.png').convert('RGBA'),
            'info_box1': Image.open(res_base / '5.1正唛公司信息及box1.png').convert('RGBA'),
            'info_box2': Image.open(res_base / '5.2正唛公司信息及box2.png').convert('RGBA'),
            'info_box3': Image.open(res_base / '5.3正唛公司信息及box3.png').convert('RGBA'),
            'warning_1': Image.open(res_base / '6.正唛底部提示1.png').convert('RGBA'),
            'warning_2': Image.open(res_base / '7.正唛底部提示2.png').convert('RGBA'),
            'warning_3': Image.open(res_base / '8.正唛底部提示3.png').convert('RGBA'),
            'warning_bg': Image.open(res_base / '9.正唛底部提示底框.png').convert('RGBA'),
            'side_sku_box': Image.open(res_base / '11.侧唛标签SKU旁BOX底框.png').convert('RGBA'),
            'side_info': Image.open(res_base / '12.侧唛箱子信息.png').convert('RGBA'),
            'side_warning': Image.open(res_base / '13.侧唛提示语.png').convert('RGBA'),
            'side_warning_left': Image.open(res_base / '14.侧唛提示语左.png').convert('RGBA'),
            'icon_side_label': Image.open(res_base / '侧唛标签.png').convert('RGBA'),
            'icon_compact_side_label': Image.open(res_base / '侧唛标签-小.png').convert('RGBA'),
        }

    def _load_fonts(self):
        """加载字体路径 """
        font_base = self.base_dir / 'assets' / 'Exacme' / '双圈和埋地蹦床天地盖' / '箱唛字体'
        self.font_paths = {
            'CentSchbook BT': str(font_base / 'arialbd.ttf'), # Century Schoolbook
            'Calibri Bold': str(font_base / 'arialbd.ttf'),
            'CENSBKB': str(font_base / 'arialbd.ttf'),
            'Arial Regular': str(font_base / 'arial.ttf'),
            'Arial Bold': str(font_base / 'arialbd.ttf'),
        }

    def generate_exacme_main_panel(self, sku_config):
        """生成 Exacme 中间主面板 (L x W)"""
        # 注意: 这里是主页面，尺寸 L x W
        canvas = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.w_px), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)
        canvas_w, canvas_h = canvas.size

        # 1. 顶部 Logo (移除此处绘制，移至线描图后层绘制)
        img_logo = self.resources['logo']
        logo_h = int(canvas_h * 0.30)  # 稍微加大
        img_logo_resized = general_functions.scale_by_height(img_logo, logo_h)

        # 2. 中间线描图
        # 修正: 样图中 线描图很大，作为背景一样的存在，EXACME字样在中间。
        # 优先使用用户上传的线描图（来自 app_v2.py 的 img_line_drawing 上传口），否则退回资源文件
        if hasattr(sku_config, 'img_line_drawing') and sku_config.img_line_drawing is not None:
            img_line = Image.open(sku_config.img_line_drawing).convert('RGBA')
        else:
            img_line = self.resources['line_drawing']
        line_h = int(canvas_h * 0.68) # 增大到 68%
        img_line_resized = general_functions.scale_by_height(img_line, line_h)
        
        # 居中，稍微往上挪一点 (0.10 -> 0.10) 以免被底部遮挡
        canvas.paste(img_line_resized, ((canvas_w - img_line_resized.width) // 2, int(canvas_h * 0.10)),
                     mask=img_line_resized)


        ################ 中间的 logo 和 product 组成容器 需要放在线描图的上层 ################

        product_lines = sku_config.product.split('\n')
        font_product_size_target_w = img_logo_resized.width * 1 # 字体宽度占 logo 宽度的 100%
        longest_line = max(product_lines, key=len)
        font_product_size = general_functions.get_max_font_size(longest_line, self.font_paths['Arial Regular'], font_product_size_target_w)
        font_product = ImageFont.truetype(self.font_paths['Arial Regular'], font_product_size)
        padding_col = int(canvas_h * 0.05) # 列间距占画布宽度的 2%
        
        product_text_children = [engine.Text(text=line, font=font_product, color=(0, 0, 0)) for line in product_lines]
        
        column = engine.Column(
            fixed_width=canvas_w,
            align='center',
            spacing=padding_col,
            children=[
                engine.Image(img_logo_resized),
                *product_text_children
            ]
        )

        column_y = int((canvas_h * 0.9 - column.height) // 2) # 因为底部黑框占了10%的高度，所以这里乘以0.9来计算剩余空间的垂直居中
        column.layout(0, column_y)
        column.render(draw)
        ################################################################################

        # 3. 底部黑色警告背景条
        img_warning_bg = self.resources['warning_bg']
        warn_bar_h = int(canvas_h * 0.10)
        img_warning_bg_resized = img_warning_bg.resize((canvas_w, warn_bar_h), Image.Resampling.LANCZOS)
        warn_bar_y = canvas_h - warn_bar_h
        canvas.paste(img_warning_bg_resized, (0, warn_bar_y), mask=img_warning_bg_resized)

        # 4. 警告图标排列
        icons = [self.resources['warning_1'], self.resources['warning_2'], self.resources['warning_3']]
        icon_h = int(warn_bar_h * 0.6)


        max_icon_w = int(canvas_w * 0.305)
        for i, icon in enumerate(icons):
            res_icon = general_functions.scale_by_height(icon, icon_h)
            if res_icon.width > max_icon_w:
                res_icon = general_functions.scale_by_width(icon, max_icon_w)
            pos_y = warn_bar_y + (warn_bar_h - res_icon.height) // 2

            if i == 0:
                # 左边图标：往左靠 (例如左边距 2% + 稍微一点偏移)
                pos_x = int(canvas_w * 0.02)
            elif i == 1:
                # 中间图标：保持绝对居中
                pos_x = (canvas_w - res_icon.width) // 2
            else:
                # 右边图标：靠右
                pos_x = canvas_w - res_icon.width - int(canvas_w * 0.02)

            canvas.paste(res_icon, (pos_x, pos_y), mask=res_icon)
        

        # 5. SKU (右下角，警告条上方)
        sku_text = sku_config.sku_name
        font_sku_size = int(canvas_h * 0.13)
        font_sku = ImageFont.truetype(self.font_paths['Calibri Bold'], font_sku_size)

        bbox = draw.textbbox((0,0), sku_text, font=font_sku)
        sku_w = bbox[2] - bbox[0]
        sku_h = bbox[3] - bbox[1]

        sku_x = canvas_w - sku_w - int(canvas_w * 0.01)
        sku_y = warn_bar_y - sku_h - int(canvas_h * 0.05)

        draw.text((sku_x, sku_y), sku_text, font=font_sku, fill=(40, 40, 40))

        # 6. Box 信息 (左下角)
        current_box = sku_config.box_number['current_box']
        img_box_info = self.resources.get(f'info_box{current_box}', self.resources['info_box1'])
        box_h = int(canvas_h * 0.15)
        img_box_resized = general_functions.scale_by_height(img_box_info, box_h)
        # 放在左下，警告条上方
        box_x = int(canvas_w * 0.02) # 调整为 0.02，更靠左
        box_y = warn_bar_y - img_box_resized.height - int(canvas_h * 0.02)
        canvas.paste(img_box_resized, (box_x, box_y), mask=img_box_resized)

        # 7. 左上角 10FT
        size_text = "10FT"
        if "10" in sku_config.sku_name: size_text = "10FT"
        elif "12" in sku_config.sku_name: size_text = "12FT"
        elif "14" in sku_config.sku_name: size_text = "14FT"

        font_ft = ImageFont.truetype(self.font_paths['Calibri Bold'], int(canvas_h * 0.08))
        # 靠左纯黑色
        draw.text((int(canvas_w * 0.01), int(canvas_h * 0.03)), size_text, font=font_ft, fill=(0, 0, 0))

        # 8. 右上角 (COL: 颜色 + 虚线框)
        # 调整逻辑：先确定下方虚线框的大小，然后让颜色框跟它一样宽

        # 8.2 下方虚线框 (先计算尺寸)
        img_empty_frame = self.resources['empty_frame']
        empty_frame_h = int(canvas_h * 0.12)
        img_empty_frame_resized = general_functions.scale_by_height(img_empty_frame, empty_frame_h)

        # 8.1 颜色底框
        img_col_frame = self.resources['color_frame']

        # 确定尺寸: 高度按比例，但宽度强制与虚线框一致
        col_frame_h = int(canvas_h * 0.08) # 原始高度计算
        # img_col_frame_resized = general_functions.scale_by_height(img_col_frame, col_frame_h)
        # 强制宽度一致
        img_col_frame_resized = img_col_frame.resize((img_empty_frame_resized.width, col_frame_h), Image.Resampling.LANCZOS)

        # 确定位置: 右上角，留出边距
        right_margin = int(canvas_w * 0.02)
        top_margin = int(canvas_h * 0.05)

        # 对齐虚线框的位置 (虚线框在下，颜色框在上)
        # 颜色框的位置
        col_x = canvas_w - img_col_frame_resized.width - right_margin
        col_y = top_margin

        canvas.paste(img_col_frame_resized, (col_x, col_y), mask=img_col_frame_resized)

        # 绘制颜色文字 "COL : Turquoise"
        # 从配置中获取颜色，去掉括号
        color_text = "Turquoise"
        full_color_text = f"COL : {color_text}"

        # 字体颜色: 浅色/白色? 样图中 fondo 是深色，字是浅色
        font_col = ImageFont.truetype(self.font_paths['Calibri Bold'], int(col_frame_h * 0.5))

        # 文字居中于底框
        bbox_col = draw.textbbox((0,0), full_color_text, font=font_col)
        text_w = bbox_col[2] - bbox_col[0]
        text_h = bbox_col[3] - bbox_col[1]

        text_x = col_x + (img_col_frame_resized.width - text_w) // 2
        text_y = col_y + (img_col_frame_resized.height - text_h) // 2
        # 微调y
        text_y -= int(col_frame_h * 0.1)

        draw.text((text_x, text_y), full_color_text, font=font_col, fill=(161, 142, 102)) # 白色

        # 8.2 绘制下方虚线框 (位置依赖于颜色框)
        empty_x = col_x + (img_col_frame_resized.width - img_empty_frame_resized.width) // 2
        empty_y = col_y + img_col_frame_resized.height + int(canvas_h * 0.02) # 间隔

        canvas.paste(img_empty_frame_resized, (empty_x, empty_y), mask=img_empty_frame_resized)

        return canvas

    def generate_exacme_icon_side_label(self, sku_config):
        """生成绘制完成的侧唛标签图片（横向，未缩放），供短侧面板使用"""
        icon_side_label = self.resources['icon_side_label'].rotate(0, expand=True)
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

        return icon_side_label
    
    def generate_exacme_icon_small_side_label(self, sku_config):
        """生成适用于高度小于11cm的 Exacme 短侧面板的侧唛标签（横向，未缩放）"""
        icon_compact_side_label = self.resources['icon_compact_side_label'].rotate(0, expand=True)
        draw = ImageDraw.Draw(icon_compact_side_label)
        
        ############ 顶部SKU_name区 ############
        text_sku_name = sku_config.sku_name
        # sku_name字号占侧身宽度的 80%
        font_sku_name_target_width = int(icon_compact_side_label.width * 0.820) 
        font_sku_name_target_height = int(icon_compact_side_label.height * 0.39) # 字体高度占侧身高度的 39%
        font_size_sku_name = general_functions.get_max_font_size(text_sku_name, self.font_paths['Arial Bold'], font_sku_name_target_width, max_height=font_sku_name_target_height) # 获取最大字号
        font_sku_name = ImageFont.truetype(self.font_paths['Arial Bold'], font_size_sku_name)
        
        ## 直接渲染在侧唛标签的顶部中心位置
        bbox = draw.textbbox((0, 0), text_sku_name, font=font_sku_name)
        text_width = bbox[2] - bbox[0]
        text_x = (icon_compact_side_label.width - text_width) // 2
        text_y = - bbox[1] + 15  # 用字体内部偏移抵消，让文字真正贴顶
        draw.text((text_x, text_y), text_sku_name, font=font_sku_name, fill=sku_config.background_color)
        
        ############ 中间条码区 ############
        barcode_image_left_text = sku_config.sku_name # 条码下方的文字和侧唛顶部SKU_name保持一致
        barcodee_image_right_text = sku_config.side_text['sn_code'] # 条码下方右侧的文字来自side_text里的sn_code
        
        # 条码文字大小
        font_barcode_size = int(icon_compact_side_label.height * 0.07) # 条码文字大小占侧身高度的 7%
        font_barcode = ImageFont.truetype(self.font_paths['Arial Regular'], font_barcode_size)
        
        # 条码高度
        barcode_height = int(icon_compact_side_label.height * 0.41) # 条码高度占侧身高度的 41%
        
        # 条码宽度
        barcode_image_left_width = int(barcode_height * 2.9) # 条码宽度是高度的 2.9 倍
        barcode_image_right_width = int(barcode_height * 2.0)
        
        # 生成条码图片
        barcode_image_left = general_functions.generate_barcode_image(barcode_image_left_text, width=barcode_image_left_width, height=barcode_height)
        barcode_image_right = general_functions.generate_barcode_image(barcodee_image_right_text, width=barcode_image_right_width, height=barcode_height)
        
        # 生成两个垂直容器分别放左侧和右侧的条码图片+文字
        barcode_block_left = engine.Column(
            align='center',
            spacing=7,
            children=[
                engine.Image(barcode_image_left),
                engine.Text(barcode_image_left_text, font=font_barcode)
            ]
        )
        barcode_block_right = engine.Column(
            align='center',
            spacing=7,
            children=[
                engine.Image(barcode_image_right),
                engine.Text(barcodee_image_right_text, font=font_barcode)
            ]
        )
        
        # 把条码区放在侧唛标签的底部中心位置
        barcode_block = engine.Row(
            justify='center',
            align='bottom',
            padding=15,
            children=[
                barcode_block_left,
                engine.Spacer(width=26, height=1), # 条码之间的水平间距
                barcode_block_right
            ]
        )
        
        barcode_block.layout(x=0, y= 82)
        barcode_block.render(draw)
        
        # icon_compact_side_label.show()  # 临时调试：查看绘制完成后的紧凑侧唛标签
        
        return icon_compact_side_label

    def generate_exacme_short_side_panels(self, sku_config):
        """生成 Exacme 短侧面板 (左右侧，H x W)"""

        # 准备画布（侧身尺寸：宽=w_px, 高=h_px）
        canvas = Image.new(sku_config.color_mode, (sku_config.w_px, sku_config.h_px), sku_config.background_color)
        
        if sku_config.h_cm < 14:
            icon_side_label = self.generate_exacme_icon_small_side_label(sku_config)
            # 把绘制好的横向 icon_side_label 缩放后居中贴到画布上
            target_width  = int(sku_config.w_px * 0.79) # 紧凑版侧唛标签占侧身宽度的 79%
        else:
            icon_side_label = self.generate_exacme_icon_side_label(sku_config)
            # 把绘制好的横向 icon_side_label 缩放后居中贴到画布上
            target_width  = int(sku_config.w_px * 0.80)

        icon_side_label_resized = general_functions.scale_by_width(icon_side_label, target_width)
        # icon_side_label.show()  # 临时调试：查看绘制完成后的侧唛标签
        general_functions.paste_image_center_with_heightorwidth(canvas, icon_side_label_resized, width=target_width)

        canvas_short_left = canvas.rotate(-90, expand=True)
        canvas_short_right = canvas.rotate(90, expand=True)
        return canvas_short_left, canvas_short_right

    def generate_exacme_long_side_panel(self, sku_config):
        """生成 Exacme 长侧面板 (上下侧，L x H) - 显示 SHIP IN 3 BOXES + 左右提示语"""
        canvas = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.h_px), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)
        canvas_w, canvas_h = canvas.size

        if sku_config.h_cm < 11:
            # 左侧两个提示信息组成一个垂直容器
            if 'side_warning_left' in self.resources:
                img_left = self.resources['side_warning_left']
                img_left_w = int(canvas_w * 0.24) # 调小
                img_left_resized = general_functions.scale_by_width(img_left, img_left_w)
                
            if 'side_warning' in self.resources:
                img_right = self.resources['side_warning']
                img_right_w = int(canvas_w * 0.24) # 调小
                img_right_resized = general_functions.scale_by_width(img_right, img_right_w)
            
            left_col = engine.Column(
                align='center',
                padding=0,
                spacing= int(canvas_h * 0.05), # 图片之间的垂直间距占侧身高度的 5%
                children=[
                    engine.Image(img_left_resized),
                    engine.Image(img_right_resized)
                ]
            )
        
            # 中间部分 总箱数图片 放在中间
            if 'side_info' in self.resources:
                img_info = self.resources['side_info']
                # side_info 在短侧是 0.7 H. 在这里也类似
                img_info_w = int(canvas_w * 0.32) # 调小
                img_info_resized = general_functions.scale_by_width(img_info, img_info_w)
                max_info_h = int(canvas_h * 0.75)
                if img_info_resized.height > max_info_h:
                    img_info_resized = general_functions.scale_by_height(img_info, max_info_h)
        
            ############ 右侧文字区 ############
            # 右侧颜色、重量、尺寸信息等组成一个垂直容器
            # 1. 准备字体
            font_size_bold = int(canvas_h * 0.132) # 字体大小占侧身高度的 5%
            font_size_normal = int(canvas_h * 0.123) # 字体大小占侧身高度的 4%
            
            font_bold = ImageFont.truetype(self.font_paths['Arial Bold'], font_size_bold)
            font_normal = ImageFont.truetype(self.font_paths['Arial Regular'], font_size_normal)

            # 2. 像串糖葫芦一样拼装每一行 (Row)
            spacing_middle = int(canvas_w * 0.005) # 粗体和细体之间的间距占侧身高度的 6%
            spacing_row = int(canvas_h * 0.05) # 行间距占侧身高度的 4% 
            
            row_color = engine.Row(
                spacing=spacing_middle, # 粗体和细体中间隔 10 个像素
                children=[
                    engine.Text("COLOUR  :", font=font_bold),
                    engine.Text(sku_config.color, font=font_normal) # 动态颜色
                ]
            )

            row_weight_lbs = engine.Row(
                spacing=spacing_middle,
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
                spacing=spacing_middle,
                children=[
                    indent_spacer, # 隐形砖块在左边顶着
                    engine.Text(f"{sku_config.side_text['gw_value']/ 2.20462:.1f} / {sku_config.side_text['nw_value']/ 2.20462:.1f} KG", font=font_normal)
                ]
            )

            row_box_size_inch = engine.Row(
                spacing=spacing_middle,
                children=[
                    engine.Text("BOX SIZE :", font=font_bold),
                    engine.Text(f"{sku_config.l_cm/2.54:.1f}\" x {sku_config.w_cm/2.54:.1f}\" x {sku_config.h_cm/2.54:.1f}\"", font=font_normal)
                ]
            )
            
            row_box_size_cm = engine.Row(
                spacing=spacing_middle,
                children=[
                    indent_spacer, # 同样的隐形砖块，保持和重量信息的对齐
                    engine.Text(f"{sku_config.l_cm:.1f}cm x {sku_config.w_cm:.1f}cm x {sku_config.h_cm:.1f}cm", font=font_normal)
                ]
            )

            # 3. 把所有行装进大垂直容器 (Column)
            right_text_block = engine.Column(
                align='left',  # 【关键】所有行统一靠左对齐
                spacing=spacing_row,    # 行与行之间的上下间距
                children=[
                    row_color,
                    row_weight_lbs,
                    row_weight_kg,
                    row_box_size_inch,
                    row_box_size_cm
                ]
            )
            
            padding_row = int(canvas_w * 0.023) # 行内左右间距占画布宽度的 2.3%
            
            row = engine.Row(
                fixed_width=canvas_w,
                justify='space-between',
                align='center',
                padding=padding_row,
                children=[
                    left_col,
                    engine.Image(img_info_resized, nudge_x = -int(canvas_w * 0.03)), # 中间信息往左微调一点，和左侧提示语更靠近
                    right_text_block
                ]
            )
        else:
            # 1. 中间部分 side_info (使用图片 side_info)
            # 放在中间
            if 'side_info' in self.resources:
                img_info = self.resources['side_info']
                # side_info 在短侧是 0.7 H. 在这里也类似
                img_info_w = int(canvas_w * 0.32) # 调小
                img_info_resized = general_functions.scale_by_width(img_info, img_info_w)
                max_info_h = int(canvas_h * 0.75)
                if img_info_resized.height > max_info_h:
                    img_info_resized = general_functions.scale_by_height(img_info, max_info_h)

            # 2. 左侧提示语 (使用图片 side_warning_left)
            # 放在左侧
            if 'side_warning_left' in self.resources:
                img_left = self.resources['side_warning_left']
                img_left_w = int(canvas_w * 0.27) # 调小
                img_left_resized = general_functions.scale_by_width(img_left, img_left_w)

            # 3. 右侧提示语 (使用图片 side_warning)
            # 放在右侧
            if 'side_warning' in self.resources:
                img_right = self.resources['side_warning']
                img_right_w = int(canvas_w * 0.29) # 调小
                img_right_resized = general_functions.scale_by_width(img_right, img_right_w)

            padding_row = int(canvas_w * 0.023) # 行内左右间距占画布宽度的 2.3%
            
            row = engine.Row(
                fixed_width=canvas_w,
                justify='space-between',
                align='center',
                padding=padding_row,
                children=[
                    engine.Image(img_left_resized),
                    engine.Image(img_info_resized),
                    engine.Image(img_right_resized)
                ]
            )
        
        row.layout(x=0, y=(canvas_h - row.height) // 2) # 垂直居中
        row.render(draw)

        return canvas
