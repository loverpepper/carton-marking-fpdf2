# -*- coding: utf-8 -*-
"""
样式基类 (fpdf2 版) - 所有箱唛样式的抽象基类
"""
from abc import ABC, abstractmethod
from fpdf import FPDF
import pathlib


class BoxMarkStyle(ABC):
    """箱唛样式抽象基类 (fpdf2 版)"""

    def __init__(self, base_dir, ppi=300):
        self.base_dir = pathlib.Path(base_dir)
        self.ppi = ppi
        self.dpi = ppi / 2.54        # 像素/cm，供 PIL 尺寸换算使用
        self.resources = {}
        self.font_paths = {}
        self._load_resources()
        self._load_fonts()

    # ── 子类必须实现 ──────────────────────────────────────────────────────────

    @abstractmethod
    def _load_resources(self):
        """加载样式所需的资源路径（pathlib.Path）到 self.resources"""
        pass

    @abstractmethod
    def _load_fonts(self):
        """加载字体路径到 self.font_paths"""
        pass

    @abstractmethod
    def get_style_name(self) -> str:
        """返回样式唯一名称（用于注册表 key）"""
        pass

    @abstractmethod
    def get_style_description(self) -> str:
        """返回可读的样式描述"""
        pass

    @abstractmethod
    def get_required_params(self) -> list:
        """返回该样式所需的额外参数名列表"""
        return []

    @abstractmethod
    def get_layout_config_mm(self, sku_config) -> dict:
        """
        返回布局配置（单位：mm）
        格式: {"区域名": (x, y, w, h), ...}
        """
        pass

    @abstractmethod
    def register_fonts(self, pdf: FPDF):
        """
        在 FPDF 对象上注册本样式所需的全部字体。
        须在 draw_to_pdf() 之前调用。
        """
        pass

    @abstractmethod
    def draw_to_pdf(self, pdf: FPDF, sku_config):
        """将所有面板直接绘制到传入的 FPDF 页面上"""
        pass

    # ── 可选覆写 ──────────────────────────────────────────────────────────────

    def get_preview_images(self):
        """
        返回样式预览图列表（PIL Image），默认空列表。
        子类可覆写，从 assets 对应目录读取实例生成图。
        返回格式: [(filename, PIL.Image), ...]
        """
        return []


class StyleRegistry:
    """样式注册表 - 管理所有可用的样式"""

    _styles = {}
    _style_info = {}

    @classmethod
    def _read_style_info(cls, style_class):
        """
        Read lightweight metadata without running BoxMarkStyle.__init__().
        Initializing a style loads image/font resources, which is expensive in
        Streamlit because the page reruns on every widget interaction.
        """
        temp = style_class.__new__(style_class)
        temp.base_dir = pathlib.Path(__file__).parent
        temp.ppi = 72
        temp.dpi = 72 / 2.54
        temp.resources = {}
        temp.font_paths = {}
        return {
            'name': temp.get_style_name(),
            'description': temp.get_style_description(),
            'required_params': temp.get_required_params(),
        }

    @classmethod
    def register(cls, style_class):
        """注册样式类（用作装饰器 @StyleRegistry.register）"""
        info = cls._read_style_info(style_class)
        cls._styles[info['name']] = style_class
        cls._style_info[info['name']] = info
        return style_class

    @classmethod
    def get_style(cls, style_name: str, base_dir, ppi=300) -> 'BoxMarkStyle':
        """根据名称获取已注册的样式实例"""
        if style_name not in cls._styles:
            raise ValueError(
                f"未找到样式: '{style_name}'。可用样式: {list(cls._styles.keys())}"
            )
        return cls._styles[style_name](base_dir=base_dir, ppi=ppi)

    @classmethod
    def get_style_class(cls, style_name: str):
        """根据名称获取已注册的样式类，不实例化资源。"""
        if style_name not in cls._styles:
            raise ValueError(
                f"未找到样式: '{style_name}'。可用样式: {list(cls._styles.keys())}"
            )
        return cls._styles[style_name]

    @classmethod
    def get_all_styles(cls) -> list:
        """获取所有已注册样式的信息列表"""
        return [dict(cls._style_info[name]) for name in cls._styles]
