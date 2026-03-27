# -*- coding: utf-8 -*-
"""
布局引擎 (fpdf2 版) - 所有尺寸单位为毫米 (mm)
核心改动：render() 接受 FPDF 实例，而非 ImageDraw 对象
"""
from fpdf import FPDF
from PIL import Image as PILImage
from abc import ABC, abstractmethod
import pathlib


class Element(ABC):
    def __init__(self, width, height, nudge_x=0, nudge_y=0, padding=0, padding_x=None, padding_y=None):
        """所有尺寸单位均为毫米 (mm)"""
        self.width = float(width)
        self.height = float(height)
        self.padding_x = float(padding if padding_x is None else padding_x)
        self.padding_y = float(padding if padding_y is None else padding_y)
        self.nudge_x = float(nudge_x)
        self.nudge_y = float(nudge_y)
        self.x = 0.0
        self.y = 0.0

    @abstractmethod
    def layout(self, x, y, max_width=0):
        """计算并记录元素的绝对位置（mm）"""
        self.x = x + self.padding_x + self.nudge_x
        self.y = y + self.padding_y + self.nudge_y
        return self.width + 2 * self.padding_x, self.height + 2 * self.padding_y

    @abstractmethod
    def render(self, pdf: FPDF):
        """将自身绘制到 FPDF 页面上"""
        pass


class Spacer(Element):
    """不可见占位组件，用于撑开间距"""

    def __init__(self, width=0.0, height=0.0):
        super().__init__(width=width, height=height)

    def layout(self, x, y, max_width=0):
        return super().layout(x, y, max_width)

    def render(self, pdf: FPDF):
        pass


class Text(Element):
    def __init__(self, text, font_family, font_style, font_size_pt,
                 pil_font=None, ppi=300,
                 color=(0, 0, 0),
                 draw_background=False, background_color=(0, 0, 0), border_radius=4.5,
                 **kwargs):
        """
        参数:
            font_family:   fpdf2 已注册的字体族名称
            font_style:    fpdf2 字体样式: '' / 'B' / 'I' / 'BI'
            font_size_pt:  字号（磅 pt）
            pil_font:      PIL ImageFont 对象，用于精确尺寸测量（可选）
            ppi:           像素密度，用于 px→mm 换算（pil_font 不为 None 时有效）
            color:         文字颜色 (R, G, B)
            draw_background:  是否绘制文字背景圆角矩形
            background_color: 背景颜色 (R, G, B)
            border_radius:    圆角半径（mm）
        """
        if pil_font is not None:
            # anchor='ls'：以基线为参考，top 为负值（上升部分），bottom 为正值（下降部分）
            # 默认 anchor='la' 会让 top 为正值，导致 offset_y_mm 为负，基线被置于元素顶端以上
            left, top, right, bottom = pil_font.getbbox(text, anchor='ls')
            px_per_mm = ppi / 25.4
            width = (right - left) / px_per_mm
            height = (bottom - top) / px_per_mm
            # offset_y_mm：从元素顶端（视觉顶端）到文字基线（baseline）的距离（mm）
            self.offset_y_mm = -top / px_per_mm
        else:
            # 无 PIL 字体时按字号近似计算
            height = font_size_pt * 0.352778   # 1pt = 0.352778mm
            width = len(text) * height * 0.55
            self.offset_y_mm = height * 0.78

        super().__init__(width=width, height=height, **kwargs)
        self.text = text
        self.font_family = font_family
        self.font_style = font_style
        self.font_size_pt = float(font_size_pt)
        self.color = color
        self.draw_background = draw_background
        self.background_color = background_color
        self.border_radius = border_radius

    def layout(self, x, y, max_width=0):
        return super().layout(x, y, max_width)

    def render(self, pdf: FPDF):
        if self.draw_background:
            pdf.set_fill_color(*self.background_color)
            bg_w = self.width + 2 * self.padding_x
            bg_h = self.height + 2 * self.padding_y
            r = min(self.border_radius, bg_w / 2, bg_h / 2)
            pdf.rect(
                self.x - self.padding_x,
                self.y - self.padding_y,
                bg_w, bg_h,
                style='F',
                round_corners=True,
                corner_radius=r,
            )
        r, g, b = self.color
        pdf.set_text_color(r, g, b)
        pdf.set_font(self.font_family, self.font_style, self.font_size_pt)
        # fpdf2 text(x, y) 的 y 为基线位置；offset_y_mm 将顶端对齐到 self.y
        pdf.text(self.x, self.y + self.offset_y_mm, self.text)


class Image(Element):
    def __init__(self, image, width=None, height=None, ppi=300, **kwargs):
        """
        image: PIL Image、str 路径或 pathlib.Path。
        fpdf2 三种格式均原生支持，不需要 BytesIO 中间转换。
        width / height 均为 mm；ppi 仅在两者均为 None 时用于推算自然尺寸。
        """
        if isinstance(image, (str, pathlib.Path)):
            # 仅读取文件头获取尺寸，不加载像素数据
            with PILImage.open(image) as _img:
                orig_w, orig_h = _img.size
        else:
            orig_w, orig_h = image.width, image.height

        if width is not None and height is None:
            height = width * orig_h / orig_w
        elif height is not None and width is None:
            width = height * orig_w / orig_h
        if width is None:
            width = orig_w * 25.4 / ppi
            height = orig_h * 25.4 / ppi

        self._source = image  # Path、str 或 PIL Image，fpdf2 均可直接使用
        super().__init__(width=float(width), height=float(height), **kwargs)

    def layout(self, x, y, max_width=0):
        return super().layout(x, y, max_width)

    def render(self, pdf: FPDF):
        # fpdf2 原生支持 PIL Image、文件路径、BytesIO，无需手动转换
        pdf.image(self._source, x=self.x, y=self.y, w=self.width, h=self.height)


class Column(Element):
    """垂直堆叠容器 (VStack)"""

    def __init__(self, children, spacing=0.0, align='center', padding=0.0,
                 padding_x=None, padding_y=None,
                 justify='start',
                 fixed_height=None,
                 fixed_width=None,
                 **kwargs):
        padding_x = float(padding if padding_x is None else padding_x)
        padding_y = float(padding if padding_y is None else padding_y)

        total_children_h = sum(c.height for c in children)
        total_spacing = spacing * (len(children) - 1) if len(children) > 1 else 0
        dynamic_height = total_children_h + total_spacing + 2 * padding_y

        height = float(fixed_height) if fixed_height is not None else dynamic_height
        if fixed_width is not None:
            width = float(fixed_width)
        else:
            width = max(c.width for c in children) if children else 0.0
            width += 2 * padding_x

        if justify == 'space-between' and fixed_height is None:
            raise ValueError("❌ Column 使用 justify='space-between' 时必须指定 fixed_height")

        super().__init__(width=width, height=height, padding=padding,
                         padding_x=padding_x, padding_y=padding_y, **kwargs)
        self.children = children
        self.spacing = float(spacing)
        self.align = align
        self.justify = justify

    def layout(self, x, y, max_width=None):
        super().layout(x, y, max_width)
        current_y = self.y
        actual_spacing = self.spacing

        if self.justify == 'space-between' and len(self.children) > 1:
            total_h = sum(c.height for c in self.children)
            remaining = self.height - 2 * self.padding_y - total_h
            actual_spacing = remaining / (len(self.children) - 1)

        for child in self.children:
            offset_x = 0.0
            if self.align == 'center':
                offset_x = (self.width - 2 * self.padding_x - child.width) / 2
            elif self.align == 'right':
                offset_x = self.width - 2 * self.padding_x - child.width
            child.layout(self.x + offset_x, current_y)
            current_y += child.height + actual_spacing

    def render(self, pdf: FPDF):
        for child in self.children:
            child.render(pdf)


class Row(Element):
    """水平堆叠容器 (HStack)"""

    def __init__(self, children, spacing=0.0, align='center', padding=0.0,
                 padding_x=None, padding_y=None,
                 justify='start',
                 fixed_width=None,
                 fixed_height=None,
                 **kwargs):
        padding_x = float(padding if padding_x is None else padding_x)
        padding_y = float(padding if padding_y is None else padding_y)

        dynamic_height = max(c.height for c in children) if children else 0.0
        dynamic_height += 2 * padding_y
        height = float(fixed_height) if fixed_height is not None else dynamic_height

        total_children_w = sum(c.width for c in children)
        total_spacing = spacing * (len(children) - 1) if len(children) > 1 else 0
        dynamic_width = total_children_w + total_spacing + 2 * padding_x
        width = float(fixed_width) if fixed_width is not None else dynamic_width

        if justify == 'space-between' and fixed_width is None:
            raise ValueError("❌ Row 使用 justify='space-between' 时必须指定 fixed_width")

        super().__init__(width=width, height=height, padding=padding,
                         padding_x=padding_x, padding_y=padding_y, **kwargs)
        self.children = children
        self.spacing = float(spacing)
        self.align = align
        self.justify = justify

    def layout(self, x, y, max_width=0):
        super().layout(x, y, max_width)
        current_x = self.x
        actual_spacing = self.spacing

        if self.justify == 'space-between' and len(self.children) > 1:
            total_w = sum(c.width for c in self.children)
            remaining = self.width - 2 * self.padding_x - total_w
            actual_spacing = remaining / (len(self.children) - 1)

        for child in self.children:
            offset_y = 0.0
            if self.align == 'top':
                offset_y = 0.0
            elif self.align == 'center':
                offset_y = (self.height - 2 * self.padding_y - child.height) / 2
            elif self.align == 'bottom':
                offset_y = self.height - 2 * self.padding_y - child.height
            child.layout(current_x, self.y + offset_y)
            current_x += child.width + actual_spacing

    def render(self, pdf: FPDF):
        for child in self.children:
            child.render(pdf)
