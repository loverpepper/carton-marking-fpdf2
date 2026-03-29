# -*- coding: utf-8 -*-
"""
Barberpub 全搭盖样式 - 将原有的 BoxMarkEngine 转换为样式类
"""
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import pathlib as Path
from style_base import BoxMarkStyle, StyleRegistry
import general_functions


@StyleRegistry.register
class BarberpubFullOverlapStyle(BoxMarkStyle):
    '''Barberpub 全搭盖样式'''
    
    def get_style_name(self):
        return "barberpub_fulloverlap"
    
    def get_style_description(self):
        return "Barberpub 全搭盖箱唛样式"
    
    def get_required_params(self):
        return ['length_cm', 'width_cm', 'height_cm', 'ppi', 'color', 'product', 'side_text', 'sku_name', 'box_number']
    
    def get_layout_config(self, sku_config):
        '''
        Barberpub 全搭盖样式 - 5块布局（4列3行）
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
        """生成 Barberpub 全搭盖样式需要的所有面板"""
        
        canvas_front = self.generate_barberpub_front_panel(sku_config)
        canvas_side = self.generate_barberpub_side_panel(sku_config)
        canvas_left_up, canvas_left_down, canvas_right_up, canvas_right_down = self.generate_barberpub_left_panel(sku_config)
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
        """加载 Barberpub 全搭盖样式的图片资源"""
        res_base = self.base_dir / 'assets' / 'Barberpub' / '全搭盖' / '矢量文件'
        
        self.resources = {
            'icon_logo': Image.open(res_base / '正唛logo.png').convert('RGBA'),
            'icon_top_logo': Image.open(res_base / '顶盖logo信息.png').convert('RGBA'),
            'icon_attention_info': Image.open(res_base / '全搭盖开箱注意事项.png').convert('RGBA'),
            'icon_company': Image.open(res_base / '正唛公司信息.png').convert('RGBA'),
            'icon_webside': Image.open(res_base / '侧唛网址.png').convert('RGBA'),
            'icon_side_label': Image.open(res_base / '侧唛标签_窄.png').convert('RGBA'),
            'icon_slogan': Image.open(res_base / '正唛宣传语.png').convert('RGBA'),
            'icon_box_info': Image.open(res_base / '正唛多箱选择框.png').convert('RGBA'),
        }
    
    def _load_fonts(self):
        """加载字体路径"""
        font_base = self.base_dir / 'assets' / 'Barberpub' / '全搭盖' / '箱唛字体'
        self.font_paths = {
            'CentSchbook BT': str(font_base / '111.ttf'),
            'Droid Sans Bold': str(font_base / 'CENSBKBI.TTF'),
            'Calibri Bold': str(font_base / 'calibri_blod.ttf'),

        }

    
    def generate_barberpub_left_panel(self, sku_config):
        """
        生成 Barberpub 全搭盖样式的左侧面板
        
        根据箱子宽度（w_cm）自动选择布局：
        - 宽度 > 30cm：使用上下结构（顶部注意事项、Logo、SKU、虚线、底部信息框）
        - 宽度 ≤ 30cm：使用简单结构（仅居中Logo）
        """
        # 创建空白画布，尺寸为箱子的长×宽
        canvas = Image.new(sku_config.color_mode, (sku_config.l_px, sku_config.w_px), sku_config.background_color)
        canvas_w, canvas_h = canvas.size
        
        # 准备四个面板（左上、左下、右上、右下）
        canvas_left_up = canvas.copy()
        canvas_left_down = canvas.copy()
        canvas_right_up = canvas.copy()
        icon_top_logo = self.resources['icon_top_logo']
        
        # 根据箱子宽度决定使用哪种布局结构
        if sku_config.w_cm > 30:
            # ========== 上下结构布局 ==========
            # 适用于较高的箱子（宽度>30cm），包含多个信息区域
            draw = ImageDraw.Draw(canvas_left_up)
            font_path_centschbook = self.font_paths['CentSchbook BT']
            
            # --- 区域 A: 顶部注意事项信息 ---
            # 显示开箱注意事项图标，位于顶部
            icon_attention = self.resources.get('icon_attention_info')
            if icon_attention:
                attention_w = int(canvas_w * 0.95)  # 图标宽度占画布95%
                attention_resized = general_functions.scale_by_width(icon_attention, attention_w)
                attention_h = attention_resized.height
                
                # 设置顶部边距：图标自身高度的50%
                attention_margin_top = int(attention_h * 0.50)
                attention_x = (canvas_w - attention_w) // 2  # 水平居中
                attention_y = attention_margin_top
                canvas_left_up.paste(attention_resized, (attention_x, attention_y), mask=attention_resized)
                
                # 记录注意事项底部位置，用于后续元素定位
                attention_bottom_y = attention_y + attention_h
            else:
                attention_bottom_y = 0
            
            # --- 区域 B: Logo（与注意事项间隔3cm）---
            # 显示公司Logo，位于注意事项下方
            icon_logo = self.resources['icon_logo']
            icon_logo_h_px = int(canvas_h * 0.16)  # Logo高度为画布高度的16%
            icon_logo_resized = general_functions.scale_by_height(icon_logo, icon_logo_h_px)
            
            logo_y = attention_bottom_y + int(3 * sku_config.dpi)  # 与注意事项间隔3cm
            logo_x = (canvas_w - icon_logo_resized.width) // 2  # 水平居中
            canvas_left_up.paste(icon_logo_resized, (logo_x, logo_y), mask=icon_logo_resized)
            
            # 记录Logo底部位置
            logo_bottom_y = logo_y + icon_logo_resized.height
            
            # --- 区域 C: 底部信息框（需要先计算高度）---
            # 预先计算底部信息框的尺寸，以便为SKU预留空间
            margin_bottom_px = int(canvas_h * 0.10)  # 底部边距为画布高度的10%
            info_font_frame_size = int(canvas_w * 0.030)  # 标签文字字号根据画布宽度调整（大大缩小）
            info_font_without_frame_size = int(canvas_w * 0.025)  # 具体值文字字号根据画布宽度调整（大大缩小）
            
            # 底部信息区域的总高度（包括边距）
            bottom_info_total_h = margin_bottom_px + info_font_frame_size + int(0.5 * sku_config.dpi)
            
            # --- 区域 D: SKU名称（动态计算位置）---
            # SKU名称是最重要的信息，需要尽可能大
            sku_text = sku_config.sku_name
            target_sku_w = int(canvas_w * 0.90)  # 目标宽度为画布90%
            
            # 计算SKU可用的垂直空间（Logo下方到底部信息框之间）
            available_space_for_sku = canvas_h - logo_bottom_y - bottom_info_total_h - int(4 * sku_config.dpi)
            
            # 获取在约束条件下的最大字号
            sku_font_size = general_functions.get_max_font_size(
                sku_text, font_path_centschbook, target_sku_w, max_height=int(available_space_for_sku * 0.6)
            )
            sku_font = ImageFont.truetype(font_path_centschbook, sku_font_size)
            
            # 计算SKU文字的实际尺寸
            sku_w = draw.textlength(sku_text, font=sku_font)
            bbox_sku = draw.textbbox((0, 0), sku_text, font=sku_font)
            sku_h = bbox_sku[3] - bbox_sku[1]  # 获取真实文字高度（不含基线偏移）
            
            # 在可用空间中偏上放置（35%位置），留出下方空间给虚线
            sku_y = logo_bottom_y + int((available_space_for_sku - sku_h) * 0.35)
            sku_x = (canvas_w - sku_w) // 2  # 水平居中
            draw.text((sku_x, sku_y), sku_text, font=sku_font, fill=(0, 0, 0))
            
            # --- 区域 E: 虚线（SKU下方）---
            # 在SKU下方绘制装饰性虚线
            dashed_line_y = sku_y + sku_h + int(canvas_h * 0.10)  # SKU和虚线间距为画布高度的10%
            dashed_line_x_start = sku_x  # 与SKU文字左对齐
            dashed_line_x_end = sku_x + sku_w  # 与SKU文字右对齐
            
            # 虚线样式参数
            dash_length = 20  # 每段虚线长度（像素）
            gap_length = 15   # 虚线间隙长度（像素）
            line_width = 3    # 虚线粗细（像素）
            
            # 绘制虚线
            current_x = dashed_line_x_start
            while current_x < dashed_line_x_end:
                next_x = min(current_x + dash_length, dashed_line_x_end)
                draw.line([(current_x, dashed_line_y), (next_x, dashed_line_y)], fill=(0, 0, 0), width=line_width)
                current_x = next_x + gap_length
            
            # --- 区域 F: 底部信息框 ---
            # 显示净毛重（G.W./N.W.）和箱子尺寸（BOX SIZE）
            info_font_frame = ImageFont.truetype(font_path_centschbook, info_font_frame_size)
            info_font_without_frame = ImageFont.truetype(font_path_centschbook, info_font_without_frame_size)
            
            # 左侧：净毛重信息
            gw_text = "G.W./N.W."  # 标签文字
            weight_text = f"{sku_config.side_text['gw_value']} / {sku_config.side_text['nw_value']} LBS"  # 具体值
            
            # 计算标签文字宽度
            bbox_gw = draw.textbbox((0, 0), gw_text, font=info_font_frame)
            bbox_gw_width = bbox_gw[2] - bbox_gw[0]
            
            # 定位左侧信息框（根据canvas_w动态调整，约9%位置）
            left_box_x = int(canvas_w * 0.09)  # 起始位置为画布宽度的9%
            left_box_y = canvas_h - margin_bottom_px - info_font_frame_size
            
            # 绘制黑色圆角背景框
            bbox_gw_pos = (left_box_x, left_box_y)
            draw = general_functions.draw_rounded_bg_for_text(
                draw, bbox_gw, sku_config, bbox_gw_pos,
                bg_color=(0, 0, 0), padding_cm=(0.7, 0.6), radius=16
            )
            # 在黑色背景上绘制白色标签文字
            draw.text(bbox_gw_pos, gw_text, font=info_font_frame, fill=sku_config.background_color)
            
            # 在标签右侧绘制具体重量值（黑色文字）
            bbox_weight_x = left_box_x + bbox_gw_width + int(1.8 * sku_config.dpi)  # 与标签间隔1.8cm
            bbox_weight_y = left_box_y + int((info_font_frame_size - info_font_without_frame_size) / 2)  # 垂直居中对齐
            draw.text((bbox_weight_x, bbox_weight_y), weight_text, font=info_font_without_frame, fill=(0, 0, 0))
            
            # 右侧：箱子尺寸信息
            box_size_text = "BOX SIZE"  # 标签文字
            l_in = sku_config.l_in
            w_in = sku_config.w_in
            h_in = sku_config.h_in
            dimension_text = f'{l_in:.1f}" x {w_in:.1f}" x {h_in:.1f}"'  # 尺寸值（英寸）
            
            # 计算标签文字宽度
            bbox_box = draw.textbbox((0, 0), box_size_text, font=info_font_frame)
            bbox_box_w = bbox_box[2] - bbox_box[0]
            
            # 定位右侧信息框（根据canvas_w动态调整，约57%位置）
            right_box_x = int(canvas_w * 0.54)  # 起始位置为画布宽度的54%
            right_box_y = canvas_h - margin_bottom_px - info_font_frame_size
            
            # 绘制黑色圆角背景框
            bbox_box_pos = (right_box_x, right_box_y)
            draw = general_functions.draw_rounded_bg_for_text(
                draw, bbox_box, sku_config, bbox_box_pos,
                bg_color=(0, 0, 0), padding_cm=(0.7, 0.6), radius=16
            )
            # 在黑色背景上绘制白色标签文字
            draw.text(bbox_box_pos, box_size_text, font=info_font_frame, fill=sku_config.background_color)
            
            # 在标签右侧绘制具体尺寸值（黑色文字）
            dim_y = right_box_y + int((info_font_frame_size - info_font_without_frame_size) / 2)  # 垂直居中对齐
            dim_x = right_box_x + bbox_box_w + int(1.8 * sku_config.dpi)  # 与标签间隔1.8cm
            draw.text((dim_x, dim_y), dimension_text, font=info_font_without_frame, fill=(0, 0, 0))
        else:
            # ========== 左右结构布局 ==========
            # 适用于较矮的箱子（宽度≤30cm）
            # 顶部：注意事项图标（横跨整个画布）
            # 下方左侧：Logo | 下方右侧：SKU名称、虚线、净毛重和箱号信息
            draw = ImageDraw.Draw(canvas_left_up)
            font_path_centschbook = self.font_paths['CentSchbook BT']
            
            # --- 区域 A: 顶部注意事项信息（与上下结构一致）---
            icon_attention = self.resources.get('icon_attention_info')
            if icon_attention:
                attention_w = int(canvas_w * 0.95)  # 图标宽度占画布95%
                attention_resized = general_functions.scale_by_width(icon_attention, attention_w)
                attention_h = attention_resized.height
                
                # 设置顶部边距：图标自身高度的50%
                attention_margin_top = int(attention_h * 0.50)
                attention_x = (canvas_w - attention_w) // 2  # 水平居中
                attention_y = attention_margin_top
                canvas_left_up.paste(attention_resized, (attention_x, attention_y), mask=attention_resized)
                
                # 记录注意事项底部位置，用于后续元素定位
                content_start_y = attention_y + attention_h + int(1.5 * sku_config.dpi)  # 与注意事项间隔1.5cm
            else:
                content_start_y = int(canvas_h * 0.15)
            
            # 定义左右区域分割比例（从content_start_y开始）
            left_area_ratio = 0.25  # 左侧Logo区域占25%
            right_area_ratio = 0.75  # 右侧内容区域占75%
            
            left_area_w = int(canvas_w * left_area_ratio)
            right_area_w = int(canvas_w * right_area_ratio)
            right_area_x_start = left_area_w
            
            # 可用高度（去除顶部注意事项区域）
            available_h = canvas_h - content_start_y
            
            # ========== 左侧区域：Logo ==========
            icon_logo = self.resources['icon_logo']
            # Logo高度为可用高度的40%
            icon_logo_h = int(available_h * 0.40)
            icon_logo_resized = general_functions.scale_by_height(icon_logo, icon_logo_h)
            
            # Logo在左侧区域内居中（垂直方向在可用区域内居中）
            logo_x = (left_area_w - icon_logo_resized.width) // 2
            logo_y = content_start_y + (available_h - icon_logo_resized.height) // 2
            canvas_left_up.paste(icon_logo_resized, (logo_x, logo_y), mask=icon_logo_resized)
            
            # ========== 右侧区域：内容 ==========
            # 计算字号（大幅缩小，基于画布宽度而非右侧区域宽度）
            margin_bottom_px = int(canvas_h * 0.10)  # 底部边距
            info_font_frame_size = int(canvas_w * 0.022)  # 标签文字（大幅缩小）
            info_font_without_frame_size = int(canvas_w * 0.018)  # 具体值文字（大幅缩小）
            
            # 预先计算底部信息框高度
            bottom_info_total_h = margin_bottom_px + info_font_frame_size + int(0.3 * sku_config.dpi)
            
            # --- SKU名称 ---
            sku_text = sku_config.sku_name
            target_sku_w = int(right_area_w * 0.90)  # SKU宽度为右侧区域的90%
            # SKU可用高度：从content_start_y到底部信息框之间
            available_sku_h = int((available_h - bottom_info_total_h) * 0.45)
            
            sku_font_size = general_functions.get_max_font_size(
                sku_text, font_path_centschbook, target_sku_w, max_height=available_sku_h
            )
            sku_font = ImageFont.truetype(font_path_centschbook, sku_font_size)
            
            sku_w = draw.textlength(sku_text, font=sku_font)
            bbox_sku = draw.textbbox((0, 0), sku_text, font=sku_font)
            sku_h = bbox_sku[3] - bbox_sku[1]
            
            # SKU位置：在右侧区域内偏左，从content_start_y开始偏下10%
            sku_y = content_start_y + int(available_h * 0.10)
            sku_x = right_area_x_start + int((right_area_w - sku_w) * 0.35)  # 偏左对齐（35%位置）
            draw.text((sku_x, sku_y), sku_text, font=sku_font, fill=(0, 0, 0))
            
            # --- 虚线 ---
            dashed_line_y = sku_y + sku_h + int(canvas_h * 0.12)  # SKU下方12%（增大间距）
            dashed_line_x_start = sku_x
            dashed_line_x_end = sku_x + sku_w
            
            dash_length = 20
            gap_length = 15
            line_width = 3
            
            current_x = dashed_line_x_start
            while current_x < dashed_line_x_end:
                next_x = min(current_x + dash_length, dashed_line_x_end)
                draw.line([(current_x, dashed_line_y), (next_x, dashed_line_y)], fill=(0, 0, 0), width=line_width)
                current_x = next_x + gap_length
            
            # --- 底部信息框（紧挨虚线下方）---
            info_font_frame = ImageFont.truetype(font_path_centschbook, info_font_frame_size)
            info_font_without_frame = ImageFont.truetype(font_path_centschbook, info_font_without_frame_size)
            
            # 净毛重信息（左侧）
            gw_text = "G.W./N.W."
            weight_text = f"{sku_config.side_text['gw_value']} / {sku_config.side_text['nw_value']} LBS"
            
            bbox_gw = draw.textbbox((0, 0), gw_text, font=info_font_frame)
            bbox_gw_width = bbox_gw[2] - bbox_gw[0]
            
            # 与SKU左对齐，紧贴虚线下方
            left_box_x = sku_x + int(right_area_w * 0.07) # 在右侧区域内偏右7%位置
            left_box_y = dashed_line_y + int(canvas_h * 0.07)  # 虚线下方7%（更近）
            
            bbox_gw_pos = (left_box_x, left_box_y)
            draw = general_functions.draw_rounded_bg_for_text(
                draw, bbox_gw, sku_config, bbox_gw_pos,
                bg_color=(0, 0, 0), padding_cm=(0.5, 0.8), radius=16
            )
            draw.text(bbox_gw_pos, gw_text, font=info_font_frame, fill=sku_config.background_color)
            
            bbox_weight_x = left_box_x + bbox_gw_width + int(0.8 * sku_config.dpi)
            bbox_weight_y = left_box_y + int((info_font_frame_size - info_font_without_frame_size) / 2)
            draw.text((bbox_weight_x, bbox_weight_y), weight_text, font=info_font_without_frame, fill=(0, 0, 0))
            
            # 箱号信息（右侧）
            box_size_text = "BOX SIZE"
            l_in = sku_config.l_in
            w_in = sku_config.w_in
            h_in = sku_config.h_in
            dimension_text = f'{l_in:.1f}" x {w_in:.1f}" x {h_in:.1f}"'
            
            bbox_box = draw.textbbox((0, 0), box_size_text, font=info_font_frame)
            bbox_box_w = bbox_box[2] - bbox_box[0]
            
            # 在右侧区域中间偏左位置（约52%位置）
            right_box_x = right_area_x_start + int(right_area_w * 0.52)
            right_box_y = dashed_line_y + int(canvas_h * 0.07)  # 与净毛重同高（紧贴虚线）
            
            bbox_box_pos = (right_box_x, right_box_y)
            draw = general_functions.draw_rounded_bg_for_text(
                draw, bbox_box, sku_config, bbox_box_pos,
                bg_color=(0, 0, 0), padding_cm=(0.5, 0.8), radius=16
            )
            draw.text(bbox_box_pos, box_size_text, font=info_font_frame, fill=sku_config.background_color)
            
            dim_y = right_box_y + int((info_font_frame_size - info_font_without_frame_size) / 2)
            dim_x = right_box_x + bbox_box_w + int(0.8 * sku_config.dpi)
            draw.text((dim_x, dim_y), dimension_text, font=info_font_without_frame, fill=(0, 0, 0))
        
        # 生成右下面板：将左上面板旋转180度
        canvas_right_down = canvas_left_up.rotate(180, expand=True)
        
        # 返回四个面板（目前左下、右上未使用，保持空白）
        return canvas_left_up, canvas_left_down, canvas_right_up, canvas_right_down
        
    
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
        icon_logo_h_px = int(canvas_h * 0.11)  # Logo高度约为画布高度的11%（适当缩小）
        icon_logo_resized = general_functions.scale_by_height(icon_logo, icon_logo_h_px)
        icon_logo_x = margin_left_px
        icon_logo_y = margin_top_px
        canvas.paste(icon_logo_resized, (icon_logo_x, icon_logo_y), mask=icon_logo_resized)
        
        # --- 区域 B: 右上角公司信息 ---
        icon_company = self.resources['icon_company']
        icon_company_h_px = int(canvas_h * 0.048)  # 公司信息高度约为画布高度的4.8%（适当缩小）
        icon_company_resized = general_functions.scale_by_height(icon_company, icon_company_h_px)
        icon_company_x = canvas_w - icon_company_resized.width - margin_right_px
        icon_company_y = margin_top_px
        canvas.paste(icon_company_resized, (icon_company_x, icon_company_y), mask=icon_company_resized)
        
        # --- 区域 C: 中间 Product 名称和标语作为整体居中（稍微缩小）---
        product_text = sku_config.product
        target_product_w = int(canvas_w * 0.78)  # 提高到78%宽度
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
        icon_slogan_w_px = int(canvas_w * 0.38)  # 缩小到38%宽度
        icon_slogan_resized = general_functions.scale_by_width(icon_slogan, icon_slogan_w_px)
        
        # 计算Product和Slogan的整体高度
        vertical_gap = int(2 * sku_config.dpi)  # Product和Slogan之间间距2cm
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
        stripe_height_cm = 1.6
        bottom_margin_cm = 1.2
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
        margin_bottom_px = int(5 * sku_config.dpi)  # 底部边距5cm（增大间距，确保文字在斜纹上方）
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
        sku_code_y = canvas_h - margin_bottom_px - sku_code_h - int(1.4 * sku_config.dpi)
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
        box_text_font_w = int(canvas_w * 0.155)  # 目标宽度为画布宽度的15.5%（增大）
        box_text_font_h = int(canvas_h * 0.048)  # 字体大小为画布高度的4.8%（增大）
        box_text_font_size = general_functions.get_max_font_size(
            box_text, font_path_centschbook, box_text_font_w, max_height=box_text_font_h)
        box_text_font = ImageFont.truetype(font_path_centschbook, box_text_font_size)
        
        # 计算文字尺寸
        bbox_box_text = draw.textbbox((0, 0), box_text, font=box_text_font)
        bbox_box_text_w = bbox_box_text[2] - bbox_box_text[0]
        bbox_box_text_h = bbox_box_text[3] - bbox_box_text[1]
        
        # 箱号位置（右下角，与SKU代码Y坐标对齐）
        bbox_text_x = canvas_w - margin_right_px - bbox_box_text_w
        bbox_text_y = canvas_h - margin_bottom_px - bbox_box_text_h - int(1.4 * sku_config.dpi) 
        box_text_pos = (bbox_text_x, bbox_text_y)
        
        # 绘制黑框背景
        draw = general_functions.draw_rounded_bg_for_text(
            draw, bbox_box_text, sku_config, box_text_pos,
            bg_color=(0, 0, 0), padding_cm=(0.5, 0.9), radius=16
        )
        
        # 绘制白色文字
        draw.text(box_text_pos, box_text, font=box_text_font, fill=sku_config.background_color)
        
        canvas_front = canvas
        return canvas_front
    
    def generate_barberpub_side_panel(self, sku_config):
        """
        生成 Barberpub 全搭盖样式的侧面板
        
        侧面板采用横向画布，包含三个主要元素（从上到下）：
        1. SKU名称（大号字体，居中）
        2. 网址图标（左下角）
        3. 侧唛标签（右下角，包含条形码和产地信息）
        
        这三个元素会整体居中，间距随画布高度动态调整
        """
        # ========== 创建横向画布 ==========
        # 注意：侧面板是"横着"画的，因此宽度=箱子高度，高度=箱子宽度
        canvas_w = sku_config.h_px  # 画布宽度 = 箱子高度
        canvas_h = sku_config.w_px  # 画布高度 = 箱子宽度
        
        canvas = Image.new(sku_config.color_mode, (canvas_w, canvas_h), sku_config.background_color)
        draw = ImageDraw.Draw(canvas)
        
        # 加载字体
        font_path_centschbook = self.font_paths['CentSchbook BT']
        
        # ========== 区域 A: 核心 SKU名称 ==========
        # SKU是侧面板的主要信息，需要非常大且醒目
        sku_text = sku_config.sku_name
        
        # 设置约束条件：宽度92%，高度55%
        target_sku_w = int(canvas_w * 0.92)  # 目标宽度为画布宽度的92%
        max_sku_h = int(canvas_h * 0.55)     # 最大高度为画布高度的55%
        
        # 在约束条件下计算最大字号
        sku_font_size = general_functions.get_max_font_size(
            sku_text, font_path_centschbook, target_sku_w, max_height=max_sku_h
        )
        sku_font = ImageFont.truetype(font_path_centschbook, sku_font_size)
        
        # 计算 SKU 文本的实际尺寸
        sku_text_w = draw.textlength(sku_text, font=sku_font)
        bbox = draw.textbbox((0, 0), sku_text, font=sku_font)
        sku_text_h = bbox[3] - bbox[1]  # 获取真实高度（去除基线偏移）
        
        # ========== 区域 B: 底部图标资源 ==========
        # 加载网址图标和侧唛标签图标
        img_web = self.resources['icon_webside']       # 网址搜索条（左侧）
        img_label = self.resources['icon_side_label']  # 条形码标签（右侧）
        
        # 设定图标尺寸（相对于画布宽度）
        icons_web_w_px = int(canvas_w * 0.57)    # 网址条宽度为画布的57%
        icons_label_w_px = int(canvas_w * 0.28)  # 标签宽度为画布的28%
        
        # 按宽度等比缩放图标
        img_web_resized = general_functions.scale_by_width(img_web, icons_web_w_px)
        img_label_resized = general_functions.scale_by_width(img_label, icons_label_w_px)
        
        # 填充标签内容（添加条形码、产地信息等）
        img_label_resized_filled = self.fill_side_label_barberpub_fulloverlap(sku_config, img_label_resized, self.font_paths)
        
        # ========== 整体居中布局 ==========
        # 定义动态间距（相对于画布高度），设置最小值以保持合理间距
        min_gap_cm = 7  # 最小间距7cm
        gap_sku_to_icons = max(int(canvas_h * 0.22), int(min_gap_cm * sku_config.dpi))  # SKU到底部图标的间距
        
        # 计算所有元素的总高度（两个图标并排，取较高的那个）
        bottom_icons_h = max(img_web_resized.height, img_label_resized_filled.height)
        total_content_h = sku_text_h + gap_sku_to_icons + bottom_icons_h
        
        # 整体垂直居中（起始Y坐标），稍微偏下10%以优化视觉效果
        content_start_y = int((canvas_h * 1.1 - total_content_h) // 2)
        
        # ========== 绘制所有元素 ==========
        
        # 1. 绘制 SKU 文本（水平居中）
        sku_x = (canvas_w - sku_text_w) // 2  # 水平居中
        sku_y = content_start_y               # 从计算的起始位置开始
        draw.text((sku_x, sku_y), sku_text, font=sku_font, fill=(0, 0, 0))
        
        # 2. 粘贴网址图标（位于SKU下方，左侧）
        margin_side = int(3 * sku_config.dpi)  # 左右边距 3cm
        web_x = margin_side                    # 左对齐
        web_y = sku_y + sku_text_h + gap_sku_to_icons  # 位于SKU下方
        canvas.paste(img_web_resized, (web_x, web_y), mask=img_web_resized)
        
        # 3. 粘贴标签图标（与网址图标同一水平线，右对齐）
        label_x = canvas_w - img_label_resized_filled.width - margin_side  # 右对齐
        # 让两个图标的中心在同一水平线上（垂直居中对齐）
        label_y = web_y + (img_web_resized.height - img_label_resized_filled.height) // 2
        canvas.paste(img_label_resized_filled, (label_x, label_y), mask=img_label_resized_filled)
        
        # ========== 旋转生成最终面板 ==========
        # 将横向画布旋转90度，变成竖长的侧面板
        # expand=True 会自动调整画布尺寸以容纳旋转后的内容
        canvas_right_side = canvas.rotate(90, expand=True)
        
        return canvas_right_side
    
    
    # ============================================================================
    # 侧唛标签填充函数
    # ============================================================================


    def fill_side_label_barberpub_fulloverlap(self, sku_config, img_label, fonts_paths):
        """
        填充 Barberpub 全搭盖样式的侧唛标签
        
        在空白标签图片上添加以下内容：
        1. 左侧条形码（SKU名称）
        2. 右侧条形码（SN代码）
        3. 底部产地信息条（黑底白字）
        
        参数:
            sku_config: SKU配置对象
            img_label: 空白标签图片
            fonts_paths: 字体路径字典
        
        返回:
            填充好内容的标签图片
        """
        # 复制空白标签，避免修改原图
        label_canvas = img_label.copy()
        draw = ImageDraw.Draw(label_canvas)
        
        label_w, label_h = label_canvas.size
        font_path_centschbook = fonts_paths['CentSchbook BT']
        
        # ========== 统一设置条形码参数 ==========
        barcode_h = int(label_h * 0.28)  # 条形码高度为标签高度的28%
        barcode_y = int(label_h * 0.04)  # 条形码距顶部为标签高度的4%

        # ========== 区域1: 左侧条形码（SKU名称）==========
        barcode1_text = sku_config.sku_name
        barcode1_w = int(label_w * 0.533)  # 宽度为标签宽度的53.3%
        barcode1_h = barcode_h  
        
        try:
            # 生成条形码图片
            barcode1_img = general_functions.generate_barcode_image(barcode1_text, barcode1_w, barcode1_h)
            barcode1_x = int(label_w * 0.05)  # 左边距5%
            barcode1_y = barcode_y
            label_canvas.paste(barcode1_img, (barcode1_x, barcode1_y), barcode1_img if barcode1_img.mode == 'RGBA' else None)
            
            # 在条形码下方添加文字说明
            barcode1_font_size = int(label_h * 0.04)
            barcode1_font = ImageFont.truetype(font_path_centschbook, barcode1_font_size)
            bbox_barcode1 = draw.textbbox((0, 0), barcode1_text, font=barcode1_font)
            barcode1_text_x = barcode1_x + int((barcode1_w - (bbox_barcode1[2] - bbox_barcode1[0])) / 2)  # 居中对齐
            barcode1_text_y = barcode1_y + barcode1_h + int(label_h * 0.0020)  # 条形码下方
            draw.text((barcode1_text_x, barcode1_text_y), barcode1_text, font=barcode1_font, fill=(0, 0, 0))
            
        except Exception as e:
            # 条形码生成失败时，降级显示纯文字
            draw.text((int(label_w * 0.05), barcode_y - int(1.5 * sku_config.dpi)), 
                    barcode1_text, 
                    font=ImageFont.truetype(font_path_centschbook, int(label_h * 0.05)), 
                    fill=(0, 0, 0))
        
        # ========== 区域2: 右侧条形码（SN代码）==========
        barcode2_text = sku_config.side_text['sn_code']
        barcode2_w = int(label_w * 0.36)  # 宽度为标签宽度的36%
        barcode2_h = barcode_h  
        
        try:
            # 生成条形码图片
            barcode2_img = general_functions.generate_barcode_image(barcode2_text, barcode2_w, barcode2_h)
            barcode2_x = label_w - barcode2_w - int(label_w * 0.04)  # 右边距4%
            barcode2_y = barcode_y
            label_canvas.paste(barcode2_img, (barcode2_x, barcode2_y), barcode2_img if barcode2_img.mode == 'RGBA' else None)
            
            # 在条形码下方添加文字说明
            barcode2_font_size = int(label_h * 0.04)
            barcode2_font = ImageFont.truetype(font_path_centschbook, barcode2_font_size)
            bbox_barcode2 = draw.textbbox((0, 0), barcode2_text, font=barcode2_font)
            barcode2_text_x = barcode2_x + int((barcode2_w - (bbox_barcode2[2] - bbox_barcode2[0])) / 2)  # 居中对齐
            barcode2_text_y = barcode2_y + barcode2_h + int(label_h * 0.0020)  # 条形码下方
            draw.text((barcode2_text_x, barcode2_text_y), barcode2_text, font=barcode2_font, fill=(0, 0, 0))
            
        except Exception as e:
            # 条形码生成失败时，降级显示纯文字
            draw.text((label_w - int(label_w * 0.25), barcode_y - int(1.5 * sku_config.dpi)), 
                    barcode2_text, 
                    font=ImageFont.truetype(font_path_centschbook, int(label_h * 0.05)), 
                    fill=(0, 0, 0))
        
        # ========== 区域3: 底部产地信息条 ==========
        # 在标签底部绘制黑色背景条，显示产地信息
        stripe_bottom_margin = int(label_h * 0.12)  # 底部信息条高度为标签高度的12%
        
        stripe_top_y = label_h - stripe_bottom_margin
        china_bar_y = stripe_top_y
        china_bar_height = stripe_bottom_margin
        # 绘制黑色矩形背景
        draw.rectangle([(0, china_bar_y), (label_w, label_h)], fill=(0, 0, 0))
        
        # 在黑色背景上绘制白色产地文字
        origin_text = sku_config.side_text.get('origin_text', 'MADE IN CHINA')  # 默认显示"MADE IN CHINA"
        china_font_size = int(china_bar_height * 0.5)  # 字号为信息条高度的50%
        china_font = ImageFont.truetype(font_path_centschbook, china_font_size)
        china_text_w = draw.textlength(origin_text, font=china_font)
        china_x = (label_w - china_text_w) // 2  # 水平居中
        china_y = china_bar_y + int(china_bar_height * 0.20)  # 垂直偏上20%
        draw.text((china_x, china_y), origin_text, font=china_font, fill=sku_config.background_color)
        
        # 返回填充好内容的标签
        return label_canvas