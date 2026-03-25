# -*- coding: utf-8 -*-
"""
简化样式示例 - 演示如何创建新样式
这是一个简单的样式模板，用于快速创建新的箱唛样式
"""
from PIL import Image, ImageDraw, ImageFont
import pathlib as Path
from style_base import BoxMarkStyle, StyleRegistry
import general_functions


@StyleRegistry.register
class SimpleStyle(BoxMarkStyle):
    """简化箱唛样式 - 极简设计，只有基本文字信息"""
    
    def get_style_name(self):
        return "simple"
    
    def get_style_description(self):
        return "箱唛样式 - 极简设计，只包含基本文字信息和 SKU"
    
    def get_required_params(self):
        return ['product', 'box_number']  # 只需要产品名称和箱号
    
    def get_layout_config(self, sku_config):
        """简化样式 - 5块布局（示例）"""
        # 示例：简单的5块布局
        # 可以根据实际需求调整
        x0 = 0
        x1 = sku_config.l_px
        
        y0 = 0
        y1 = sku_config.half_w_px
        y2 = sku_config.half_w_px + sku_config.h_px
        
        return {
            "top_flap": (x0, y0, sku_config.l_px, sku_config.half_w_px),
            "main_front": (x0, y1, sku_config.l_px, sku_config.h_px),
            "main_side": (x1, y1, sku_config.w_px, sku_config.h_px),
            "bottom_flap": (x0, y2, sku_config.l_px, sku_config.half_w_px),
            "back_panel": (x1 + sku_config.w_px, y1, sku_config.l_px, sku_config.h_px),
        }
    
    def get_panels_mapping(self, sku_config):
        """定义每个区域应该粘贴哪个面板"""
        return {
            "top_flap": "top",
            "main_front": "front",
            "main_side": "side",
            "bottom_flap": "bottom",
            "back_panel": "front",  # 复用 front 面板
        }
    
    def generate_all_panels(self, sku_config):
        """生成简化样式需要的所有面板（只需要4个）"""
        canvas_left_up, canvas_left_down = self.generate_left_panel(sku_config)
        canvas_front = self.generate_front_panel(sku_config)
        canvas_side = self.generate_side_panel(sku_config)
        
        return {
            "top": canvas_left_up,      # 顶部
            "front": canvas_front,       # 正面
            "side": canvas_side,         # 侧面
            "bottom": canvas_left_down,  # 底部
        }
    
    def _load_resources(self):
        """简化样式不需要太多图片资源"""
        # 可以留空或只加载必要的资源
        self.resources = {}
    
    def _load_fonts(self):
        """加载字体路径"""
        font_base = self.base_dir / 'MCombo箱唛打样文件' / '箱唛字体'
        self.font_paths = {
            'calibri_bold': str(font_base / 'calibri_blod.ttf'),
            'itc_demi': str(font_base / 'ITC Avant Garde Gothic LT Demi.ttf'),
        }
    
    def generate_left_panel(self, sku_config):
        """生成左侧面板 - 纯色"""
        canvas_left_up = Image.new('RGB', (sku_config.l_px, sku_config.half_w_px), (200, 200, 200))
        canvas_left_down = Image.new('RGB', (sku_config.l_px, sku_config.half_w_px), (200, 200, 200))
        return canvas_left_up, canvas_left_down
    
    def generate_right_panel(self, sku_config):
        """生成右侧面板 - 纯色"""
        canvas_right_up = Image.new('RGB', (sku_config.l_px, sku_config.half_w_px), (200, 200, 200))
        canvas_right_down = Image.new('RGB', (sku_config.l_px, sku_config.half_w_px), (200, 200, 200))
        return canvas_right_up, canvas_right_down
    
    def generate_front_panel(self, sku_config):
        """生成正面面板 - 只显示 SKU 和产品名称"""
        canvas = Image.new('RGB', (sku_config.l_px, sku_config.h_px), (255, 255, 255))
        draw = ImageDraw.Draw(canvas)
        
        canvas_w, canvas_h = canvas.size
        
        # 大号字体显示 SKU
        sku_font_size = int(canvas_h * 0.15)
        sku_font = ImageFont.truetype(self.font_paths['calibri_bold'], size=sku_font_size)
        
        # 中号字体显示产品名称
        product_font_size = int(canvas_h * 0.08)
        product_font = ImageFont.truetype(self.font_paths['itc_demi'], size=product_font_size)
        
        # 绘制 SKU（居中偏上）
        sku_bbox = draw.textbbox((0, 0), sku_config.sku_name, font=sku_font)
        sku_w = sku_bbox[2] - sku_bbox[0]
        sku_x = (canvas_w - sku_w) // 2
        sku_y = canvas_h // 3
        draw.text((sku_x, sku_y), sku_config.sku_name, font=sku_font, fill=(0, 0, 0))
        
        # 绘制产品名称（居中偏下）
        product_text = sku_config.product
        product_bbox = draw.textbbox((0, 0), product_text, font=product_font)
        product_w = product_bbox[2] - product_bbox[0]
        product_x = (canvas_w - product_w) // 2
        product_y = canvas_h * 2 // 3
        draw.text((product_x, product_y), product_text, font=product_font, fill=(0, 0, 0))
        
        # 绘制箱号信息（右下角）
        box_text = f"Box {sku_config.box_number['current_box']}/{sku_config.box_number['total_boxes']}"
        box_font = ImageFont.truetype(self.font_paths['calibri_bold'], size=int(canvas_h * 0.05))
        box_bbox = draw.textbbox((0, 0), box_text, font=box_font)
        box_w = box_bbox[2] - box_bbox[0]
        box_x = canvas_w - box_w - int(2 * sku_config.dpi)
        box_y = canvas_h - int(3 * sku_config.dpi)
        draw.text((box_x, box_y), box_text, font=box_font, fill=(0, 0, 0))
        
        return canvas
    
    def generate_side_panel(self, sku_config):
        """生成侧面面板 - 只显示 SKU"""
        canvas = Image.new('RGB', (sku_config.w_px, sku_config.h_px), (240, 240, 240))
        draw = ImageDraw.Draw(canvas)
        
        canvas_w, canvas_h = canvas.size
        
        # 中号字体显示 SKU（垂直居中）
        sku_font_size = int(canvas_h * 0.1)
        sku_font = ImageFont.truetype(self.font_paths['calibri_bold'], size=sku_font_size)
        
        sku_bbox = draw.textbbox((0, 0), sku_config.sku_name, font=sku_font)
        sku_w = sku_bbox[2] - sku_bbox[0]
        sku_h = sku_bbox[3] - sku_bbox[1]
        
        sku_x = (canvas_w - sku_w) // 2
        sku_y = (canvas_h - sku_h) // 2
        
        draw.text((sku_x, sku_y), sku_config.sku_name, font=sku_font, fill=(0, 0, 0))
        
        return canvas
