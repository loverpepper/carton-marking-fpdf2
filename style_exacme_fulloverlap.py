# -*- coding: utf-8 -*-
"""
Exacme 全搭盖样式 - fpdf2 版
"""
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import pathlib as Path
from style_base import BoxMarkStyle, StyleRegistry
import general_functions
from general_functions import generate_barcode_image
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
        
    # ── fpdf2 required abstract methods ─────────────────────────────────────

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

    # ── fpdf2 字体注册 ──────────────────────────────────────────────────────────

    def register_fonts(self, pdf: FPDF):
        """向 FPDF 对象注册本样式使用的所有字体"""
        pdf.add_font('Arial',      '',  self.font_paths['Arial Regular'])
        pdf.add_font('Arial',      'B', self.font_paths['Arial Bold'])
        pdf.add_font('ArialBlack', '',   self.font_paths['Arial Black'])

    # ── 核心绘制入口 ────────────────────────────────────────────────────────────

    def draw_to_pdf(self, pdf: FPDF, sku_config):
        """将所有面板直接绘制到已添加页面的 FPDF 对象上"""
        layout = self.get_layout_config_mm(sku_config)

        # 填充各面板背景色
        r, g, b = sku_config.background_color
        pdf.set_fill_color(r, g, b)
        for _, (x, y, w, h) in layout.items():
            pdf.rect(x, y, w, h, style='F')

        l_mm = sku_config.l_cm * 10
        w_mm = sku_config.w_cm * 10
        h_mm = sku_config.h_cm * 10

        x0 = 0.0
        x1 = l_mm
        x2 = l_mm + w_mm
        x3 = 2 * l_mm + w_mm
        y1 = w_mm
        y2 = w_mm + h_mm

        # 两块正面面板
        self._draw_front_panel(pdf, sku_config, x0, y1, l_mm, h_mm)
        self._draw_front_panel(pdf, sku_config, x2, y1, l_mm, h_mm)

        # 两块侧面面板（保留为 PIL 光栅图，因模板背景复杂）
        side_img = self._build_side_panel_image(sku_config)
        pdf.image(side_img, x=x1, y=y1, w=w_mm, h=h_mm)
        pdf.image(side_img, x=x3, y=y1, w=w_mm, h=h_mm)

        # 翻盖面板：left_up（正常）、left_down（空白）、right_up（空白）、right_down（180° 旋转）
        self._draw_flap_left_up(pdf, sku_config, x0, 0.0, l_mm, w_mm)
        self._draw_flap_right_down(pdf, sku_config, x2, y2, l_mm, w_mm)
        # left_down / right_up / side flaps 均为空白（已由背景色填充）

    # ── 内部辅助方法 ────────────────────────────────────────────────────────────

    def _get_font_size(self, text, font_key, target_width_mm, ppi):
        """返回 (font_size_pt, pil_font) 使文字适合 target_width_mm"""
        target_px = int(target_width_mm * ppi / 25.4)
        size_px = general_functions.get_max_font_size(text, self.font_paths[font_key], target_px)
        size_pt = size_px * 72.0 / ppi
        pil_font = ImageFont.truetype(self.font_paths[font_key], size_px)
        return size_pt, pil_font

    def _get_font_size_constrained(self, text, font_key, target_width_mm, max_height_mm, ppi):
        """同 _get_font_size，额外受 max_height_mm 约束"""
        target_px = int(target_width_mm * ppi / 25.4)
        max_h_px = int(max_height_mm * ppi / 25.4)
        size_px = general_functions.get_max_font_size(
            text, self.font_paths[font_key], target_px, max_height=max_h_px)
        size_pt = size_px * 72.0 / ppi
        pil_font = ImageFont.truetype(self.font_paths[font_key], size_px)
        return size_pt, pil_font

    @staticmethod
    def _pil_bbox_mm(pil_font, text, ppi):
        """使用 anchor='ls' 获取文字边框并换算为 mm"""
        left, top, right, bottom = pil_font.getbbox(text, anchor='ls')
        px_per_mm = ppi / 25.4
        return left / px_per_mm, top / px_per_mm, right / px_per_mm, bottom / px_per_mm

    def _draw_text_top_left(self, pdf, x_mm, y_top_mm, text,
                             font_family, font_style, font_size_pt, pil_font, ppi,
                             color=(0, 0, 0)):
        """以左-顶锚点绘制文字"""
        _, top_mm, _, _ = self._pil_bbox_mm(pil_font, text, ppi)
        baseline_y = y_top_mm + (-top_mm)
        r, g, b = color
        pdf.set_text_color(r, g, b)
        pdf.set_font(font_family, font_style, font_size_pt)
        pdf.text(x_mm, baseline_y, text)

    def _draw_text_top_center(self, pdf, x_center_mm, y_top_mm, text,
                               font_family, font_style, font_size_pt, pil_font, ppi,
                               color=(0, 0, 0)):
        """以中-顶锚点绘制文字"""
        left_mm, top_mm, right_mm, _ = self._pil_bbox_mm(pil_font, text, ppi)
        text_w_mm = right_mm - left_mm
        x_mm = x_center_mm - text_w_mm / 2.0
        baseline_y = y_top_mm + (-top_mm)
        r, g, b = color
        pdf.set_text_color(r, g, b)
        pdf.set_font(font_family, font_style, font_size_pt)
        pdf.text(x_mm, baseline_y, text)

    # ── 正面面板 ─────────────────────────────────────────────────────────────

    def _draw_front_panel(self, pdf: FPDF, sku_config, x_mm, y_mm, w_mm, h_mm):
        """绘制正面（正唛）面板 - 矢量文字 + 光栅图标"""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4
        margin_mm = 20.0  # 2cm 安全边距

        # ── 1. 提取尺寸编号 ─────────────────────────────────────────────────
        match = re.search(r'S(\d{2})', sku_config.sku_name)
        if match:
            product_size_number = match.group(1)
        else:
            raise ValueError("SKU 名称格式不正确，无法提取尺寸信息")

        # ── 2. 顶部行：左侧 "XXFT" + 右侧颜色文字 ─────────────────────────
        ft_text = f"{product_size_number}FT"
        ft_size_px = int(h_mm * px_per_mm * 0.12)
        ft_size_pt = ft_size_px * 72.0 / ppi
        pil_ft = ImageFont.truetype(self.font_paths['Arial Black'], ft_size_px)

        color_text = str(sku_config.color)
        color_size_px = int(h_mm * px_per_mm * 0.08)
        color_size_pt = color_size_px * 72.0 / ppi
        pil_color = ImageFont.truetype(self.font_paths['Arial Bold'], color_size_px)

        # 左侧 FT 文字
        ft_x = x_mm + margin_mm
        _, ft_top, _, ft_bot = self._pil_bbox_mm(pil_ft, ft_text, ppi)
        ft_h_mm = ft_bot - ft_top
        ft_y_top = y_mm + margin_mm
        self._draw_text_top_left(pdf, ft_x, ft_y_top, ft_text,
                                  'ArialBlack', '', ft_size_pt, pil_ft, ppi)

        # 右侧颜色文字（与 FT 垂直居中对齐）
        _, c_top, _, c_bot = self._pil_bbox_mm(pil_color, color_text, ppi)
        c_h_mm = c_bot - c_top
        cl, _, cr, _ = self._pil_bbox_mm(pil_color, color_text, ppi)
        color_w_mm = cr - cl
        color_x = x_mm + w_mm - margin_mm - color_w_mm
        color_y_top = ft_y_top + (ft_h_mm - c_h_mm) / 2.0
        self._draw_text_top_left(pdf, color_x, color_y_top, color_text,
                                  'Arial', 'B', color_size_pt, pil_color, ppi)

        # ── 3. 中间：公司 logo + 产品名称图标 ─────────────────────────────────
        icon_logo_product = self.resources['icon_logo_product']
        orig_w, orig_h = icon_logo_product.size
        logo_w_mm = w_mm * 0.37
        logo_h_mm = logo_w_mm * orig_h / orig_w
        logo_x = x_mm + (w_mm - logo_w_mm) / 2.0
        logo_y = y_mm + (h_mm - logo_h_mm) / 2.0
        pdf.image(icon_logo_product, x=logo_x, y=logo_y, w=logo_w_mm, h=logo_h_mm)

        # ── 4. 底部行：左侧公司信息 + 右侧 SKU 黑框 ──────────────────────────
        icon_company = self.resources['icon_company']
        ic_orig_w, ic_orig_h = icon_company.size
        ic_w_mm = w_mm * 0.19
        ic_h_mm = ic_w_mm * ic_orig_h / ic_orig_w
        ic_x = x_mm + margin_mm
        ic_y = y_mm + h_mm - margin_mm - ic_h_mm
        pdf.image(icon_company, x=ic_x, y=ic_y, w=ic_w_mm, h=ic_h_mm)

        # SKU 黑框 + 白字
        sku_text = sku_config.sku_name
        sku_size_px = int(h_mm * px_per_mm * 0.14)
        sku_size_pt = sku_size_px * 72.0 / ppi
        pil_sku = ImageFont.truetype(self.font_paths['Arial Bold'], sku_size_px)
        sl, st, sr, sb = self._pil_bbox_mm(pil_sku, sku_text, ppi)
        sku_w_mm = sr - sl
        sku_h_mm = sb - st

        pad_mm = 10.0 * h_mm / (sku_config.h_cm * 10)  # ~1cm 内边距，比例缩放
        radius_mm = h_mm * 0.05

        # 黑色圆角矩形背景
        box_total_w = sku_w_mm + 2 * pad_mm
        box_total_h = sku_h_mm + 2 * pad_mm
        box_x = x_mm + w_mm - margin_mm - box_total_w
        box_y = y_mm + h_mm - margin_mm - box_total_h

        pdf.set_fill_color(0, 0, 0)
        r_corner = min(radius_mm, box_total_w / 2, box_total_h / 2)
        pdf.rect(box_x, box_y, box_total_w, box_total_h,
                 style='F', round_corners=True, corner_radius=r_corner)

        # SKU 白字
        sku_text_x = box_x + pad_mm
        sku_text_y = box_y + pad_mm
        r, g, b = sku_config.background_color
        self._draw_text_top_left(pdf, sku_text_x, sku_text_y, sku_text,
                                  'Arial', 'B', sku_size_pt, pil_sku, ppi,
                                  color=(r, g, b))

    # ── 侧面面板（PIL 光栅保留） ─────────────────────────────────────────────

    def _build_side_panel_image(self, sku_config):
        """构建侧面面板 PIL 图像（保留光栅渲染，因模板背景复杂）并返回旋转后的 PIL Image"""
        return self.generate_exacme_side_panel(sku_config)

    # ── 翻盖面板 ─────────────────────────────────────────────────────────────

    def _draw_flap_left_up(self, pdf: FPDF, sku_config, x_mm, y_mm, w_mm, h_mm):
        """绘制左翻盖（上）面板 - 矢量文字 + 光栅图标"""
        ppi = sku_config.ppi
        px_per_mm = ppi / 25.4
        margin_mm = 20.0  # 2cm 安全边距

        # ── 提取尺寸编号 ────────────────────────────────────────────────────
        match = re.search(r'S(\d{2})', sku_config.sku_name)
        if match:
            product_size_number = match.group(1)
        else:
            raise ValueError("SKU 名称格式不正确，无法提取尺寸信息")

        # ── 顶部行：左侧 logo + 右侧 "XXFT" ─────────────────────────────
        icon_top_logo = self.resources['icon_top_logo']
        orig_w, orig_h = icon_top_logo.size
        logo_w_mm = w_mm * 0.15
        logo_h_mm = logo_w_mm * orig_h / orig_w
        logo_x = x_mm + margin_mm
        logo_y = y_mm + margin_mm
        pdf.image(icon_top_logo, x=logo_x, y=logo_y, w=logo_w_mm, h=logo_h_mm)

        ft_text = f"{product_size_number}FT"
        ft_size_px = int(h_mm * px_per_mm * 0.22)
        ft_size_pt = ft_size_px * 72.0 / ppi
        pil_ft = ImageFont.truetype(self.font_paths['Arial Black'], ft_size_px)
        fl, ft_top, fr, ft_bot = self._pil_bbox_mm(pil_ft, ft_text, ppi)
        ft_w_mm = fr - fl
        ft_h_mm = ft_bot - ft_top
        ft_x = x_mm + w_mm - margin_mm - ft_w_mm
        # 与 logo 底部对齐
        ft_y_top = logo_y + logo_h_mm - ft_h_mm
        self._draw_text_top_left(pdf, ft_x, ft_y_top, ft_text,
                                  'ArialBlack', '', ft_size_pt, pil_ft, ppi)

        # ── 中间：SKU 名称 ──────────────────────────────────────────────────
        sku_text = sku_config.sku_name
        sku_pt, pil_sku = self._get_font_size_constrained(
            sku_text, 'Arial Bold', w_mm * 0.50, h_mm * 0.30, ppi)
        skl, skt, skr, skb = self._pil_bbox_mm(pil_sku, sku_text, ppi)
        sku_w_mm = skr - skl
        sku_h_mm = skb - skt
        sku_x = x_mm + (w_mm - sku_w_mm) / 2.0
        nudge_y_mm = h_mm * (-0.08)
        sku_y_top = y_mm + (h_mm - sku_h_mm) / 2.0 + nudge_y_mm
        self._draw_text_top_left(pdf, sku_x, sku_y_top, sku_text,
                                  'Arial', 'B', sku_pt, pil_sku, ppi)

        # ── 底部行：三个图标 ────────────────────────────────────────────────
        icon_notice = self.resources['icon_top_notice']
        icon_attention = self.resources['icon_top_attention']
        icon_smallicons = self.resources['icon_top_smallicons']

        btm_y_base = y_mm + h_mm - margin_mm

        # icon_top_notice（左，22% 宽）
        n_orig_w, n_orig_h = icon_notice.size
        n_w_mm = w_mm * 0.22
        n_h_mm = n_w_mm * n_orig_h / n_orig_w
        n_x = x_mm + margin_mm
        n_y = btm_y_base - n_h_mm
        pdf.image(icon_notice, x=n_x, y=n_y, w=n_w_mm, h=n_h_mm)

        # icon_top_smallicons（右，12% 宽）
        s_orig_w, s_orig_h = icon_smallicons.size
        s_w_mm = w_mm * 0.12
        s_h_mm = s_w_mm * s_orig_h / s_orig_w
        s_x = x_mm + w_mm - margin_mm - s_w_mm
        s_y = btm_y_base - s_h_mm
        pdf.image(icon_smallicons, x=s_x, y=s_y, w=s_w_mm, h=s_h_mm)

        # icon_top_attention（中，35% 宽，向左偏移 5%）
        a_orig_w, a_orig_h = icon_attention.size
        a_w_mm = w_mm * 0.35
        a_h_mm = a_w_mm * a_orig_h / a_orig_w
        a_x = x_mm + (w_mm - a_w_mm) / 2.0 - w_mm * 0.05
        a_y = btm_y_base - a_h_mm
        pdf.image(icon_attention, x=a_x, y=a_y, w=a_w_mm, h=a_h_mm)

    def _draw_flap_right_down(self, pdf: FPDF, sku_config, x_mm, y_mm, w_mm, h_mm):
        """绘制右翻盖（下）面板 - left_up 旋转 180°。
        使用 pdf.rotation() 实现矢量文字 180° 旋转。"""
        cx = x_mm + w_mm / 2.0
        cy = y_mm + h_mm / 2.0
        with pdf.rotation(180, cx, cy):
            self._draw_flap_left_up(pdf, sku_config, x_mm, y_mm, w_mm, h_mm)

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