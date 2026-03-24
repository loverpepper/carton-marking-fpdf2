# -*- coding: utf-8 -*-
"""
新版核心生成引擎 - 使用样式注册系统
"""
from PIL import Image, ImageDraw
from pathlib import Path
from style_base import StyleRegistry

# 导入所有样式模块以自动注册
# import style_mcombo_standard
# import style_barberpub_topandbottom
# import style_barberpub_doubleopening
# import style_barberpub_fulloverlap
# import style_exacme_fulloverlap
# import style_exacme_doubleopening
# import style_exacme_topandbottom_squaretrampoline
# import style_exacme_topandbottom_doubleringandburiedtrampoline
# import style_mcombo_vertical
# import style_New_market_GE_UK_FR_vertical
# import style_New_market_GE_UK_FR_standard
# import style_macrout_topandbottom
# 未来在这里导入更多样式:
# import style_simple
# import style_premium
# import style_custom_a
# etc.
#测试一下


class SKUConfig:
    """SKU 配置类 - 保持不变"""
    SUPPORTED_COUNTRIES = ['UK', 'FR', 'GE']
    def __init__(self, sku_name, length_cm, width_cm, height_cm, 
                 style_name="mcombo_standard", 
                 bottom_gb_h_cm=10, ppi=300,
                 company_name="NEWACME LLC", contact_info="www.mcombo.com / sale_uk@newacmellc.com",
                 legal_data=None, legal_3_2=0, legal_3_3=0, legal_3_4=0, legal_3_5=0, legal_3_6=0,
                 show_fsc=0, show_sponge=0,
                 country=None, **style_params):
        """
        Args:
            sku_name: SKU 名称
            length_cm, width_cm, height_cm: 箱子尺寸（厘米）
            style_name: 样式名称，默认 "exacme_fulloverlap"
            bottom_gb_h_cm: 底部黑色底框高度（厘米）
            ppi: 分辨率
            **style_params: 样式特定参数，如 color, product, size, side_text, box_number, sponge_verified 等
        """
        self.sku_name = sku_name
        self.l_cm = length_cm
        self.w_cm = width_cm
        self.h_cm = height_cm
        self.l_in = length_cm / 2.54
        self.w_in = width_cm / 2.54
        self.h_in = height_cm / 2.54
        self.bottom_gb_h = bottom_gb_h_cm
        self.style_name = style_name
        self.dpi = ppi / 2.54
        self.ppi = ppi
        self.color_mode = 'RGB'  # 默认颜色模式
        self.background_color = (161, 142, 102)  # 默认RGB背景色
        # self.background_color = (0, 12, 37, 37)  # 默认CMYK背景色，颜色设置还有问题
        
        # 预计算像素值
        self.l_px = int(length_cm * self.dpi)
        self.w_px = int(width_cm * self.dpi)
        self.h_px = int(height_cm * self.dpi)
        self.half_w_px = int(self.w_px / 2)
        self.bottom_gb_h_px = int(self.bottom_gb_h * self.dpi)
        self.company_name = company_name
        self.contact_info = contact_info
        self.legal_data = legal_data
        self.legal_3_2 = legal_3_2
        self.legal_3_3 = legal_3_3
        self.legal_3_4 = legal_3_4
        self.legal_3_5 = legal_3_5
        self.legal_3_6 = legal_3_6
        self.show_fsc = show_fsc
        self.show_sponge = show_sponge


        # 先设置所有可能的国家开关为默认值0（或保留传入的旧参数）
        # 但为了避免重复代码，采用如下逻辑：
        if country is not None:
            # 将国家名转为大写
            country_upper = country.upper()
            if country_upper not in self.SUPPORTED_COUNTRIES:
                raise ValueError(f"Unsupported country: {country}. Supported: {', '.join(self.SUPPORTED_COUNTRIES)}")
            # 将所有国家开关置0
            for c in self.SUPPORTED_COUNTRIES:
                setattr(self, c, 0)
            # 将选中的国家开关置1
            setattr(self, country_upper, 1)

        # 存储样式特定参数
        for key, value in style_params.items():
            setattr(self, key, value)


class BoxMarkGenerator:
    """箱唛生成器 - 使用样式系统"""
    
    def __init__(self, base_dir, style_name="mcombo_standard", ppi=300):
        """
        Args:
            base_dir: 资源基础目录
            style_name: 使用的样式名称
            ppi: 分辨率
        """
        self.base_dir = base_dir
        self.style_name = style_name
        self.ppi = ppi
        self.style = StyleRegistry.get_style(style_name, base_dir, ppi)
    
    def generate_complete_layout(self, sku_config):
        """生成完整的箱唛布局 - 动态适配不同样式的布局"""
        # 1. 从样式获取布局配置
        layout = self.style.get_layout_config(sku_config)
        panels_mapping = self.style.get_panels_mapping(sku_config)
        
        print(f"📐 开始使用样式 '{self.style_name}' 生成箱唛，布局格子: {len(layout)}")
        
        # 2. 计算画布总尺寸（根据布局的最大范围）
        max_x = max(x + w for x, y, w, h in layout.values())
        max_y = max(y + h for x, y, w, h in layout.values())
        
        # 创建画布（白色背景，未填充的区域将显示为白色）
   
        canvas = Image.new(sku_config.color_mode, (int(max_x), int(max_y)), (255, 255, 255)) # RGB白色背景
        # canvas = Image.new('CMYK', (int(max_x), int(max_y)), (0,0,0,0))  # CMYK透明背景（未填充区域为白色）
        # 3. 让样式生成它需要的所有面板（动态适配不同样式）
        panels_dict = self.style.generate_all_panels(sku_config)
        
        # 4. 根据映射关系动态粘贴面板
        for region_name, panel_type in panels_mapping.items():
            if region_name in layout and panel_type in panels_dict:
                x, y, w, h = layout[region_name]
                panel = panels_dict[panel_type]
                canvas.paste(panel, (int(x), int(y)))
        
        # 6. 画出所有格子的边框（用于调试和验证）
        draw = ImageDraw.Draw(canvas)
        for name, (x, y, w, h) in layout.items():
            shape = [x, y, x + w, y + h]
            draw.rectangle(shape, outline=(0,0,0), width=3)
        
        print(f"🖼️ 完成布局渲染，画布尺寸: {canvas.width}x{canvas.height}px")
        return canvas
    
    def save_as_pdf(self, canvas, output_path, sku_config):
        """保存为 PDF 格式（与旧版保持一致：先转CMYK再转回RGB）"""
        canvas.show()
        
        # 由RGB转CMYK以便印刷（用于颜色校准）
        # canvas_cmyk = canvas.convert('CMYK')
        # PDF需要RGB模式
        # canvas_rgb = canvas_cmyk.convert('RGB')
        canvas.save(output_path, "PDF", resolution=sku_config.ppi, quality=100)
        # canvas_rgb.save(output_path, "PDF", resolution=sku_config.ppi, quality=100)
        
        total_width, total_height = canvas.size
        print(f"✅ 箱唛已生成为PDF！文件: {output_path}")
        print(f"   样式: {self.style_name}")
        print(f"   尺寸: {total_width}x{total_height}px ({total_width/sku_config.dpi:.1f}cm x {total_height/sku_config.dpi:.1f}cm)")
        print(f"   分辨率: {sku_config.ppi} PPI")
    
    @staticmethod
    def list_available_styles():
        """列出所有可用的样式"""
        return StyleRegistry.get_all_styles()


def visualize_layout(sku_config, generator):
    """可视化布局（兼容旧接口）"""
    canvas = generator.generate_complete_layout(sku_config)
    output_filename = f"{sku_config.sku_name}_carton_marking.pdf"
    generator.save_as_pdf(canvas, output_filename, sku_config)


# --- 测试运行 ---
if __name__ == "__main__":
    # 使用新框架生成箱唛
    sku_text = {
        'gw_value': 33.72, #LBS 毛重
        'nw_value': 29.75, #LBS 净重
        'sn_code': '09429381135347',
        'origin_text':'MADE IN CHINA',
    }

    box_number = {
        'total_boxes': 3,
        'current_box': 2
    }

    legal_info = {
        "Product Name": "Lift Recliner",
        "Model": "GE-6160-LC001BG-1",
        "Batch Number": "08429381118265",
        "Country Origin": "Made in China",
        "Manufacturer": "TAIYUAN TEMARU ELECTRONICS TECHNOLOGY CO,.LTD",
        "Manufacturer Address": "NO.201-01, Zhongchuang Space, Shanxi Temaru Cross-border Industrial Park, 2nd Floor, Customs Clearance Service Center, Taiyuan Wusu",
        "Manufacturer E-mail": "cs@elegue.com"
    }

    # 创建 SKU 配置（使用新方式）
    test_sku = SKUConfig(
        sku_name="6056-ST5782W",
        length_cm=126,
        width_cm=46,
        height_cm=14,
        style_name="macrout_topandbottom",  # 指定样式
        ppi=150,
        
        color='(White)',
        product='Storage Shed Shelves', # 可选参数
        product_fullname = 'TRAMPOLINE\nPREMIUM SPRING COVER', # 可选参数，Exacme 对开盖会用到
        size='Zero Wall Hugger', # 可选参数，MCombo 标准样式的特定参数
        side_text=sku_text,
        box_number=box_number,
        sponge_verified=True, # 是否通过海绵测试, 可选参数, Mcombo 和 新市场 样式会用到

        
        # 江月加的新增参数 适用于新市场样式，其他样式会忽略这些参数
        legal_data=legal_info,
        show_fsc=True, # 是否显示FSC标志，适用于新市场
        company_name="NEWACME LLC",
        contact_info="www.mcombo.com / sale_uk@newacmellc.com",
        legal_3_2=0, legal_3_3=0, legal_3_4=0, legal_3_5=1, legal_3_6=1,
        country="GE"
    )
    
    # 创建生成器
    base_dir = Path(__file__).parent
    generator = BoxMarkGenerator(base_dir=base_dir, style_name="macrout_topandbottom", ppi=150)
    
    # 生成箱唛
    visualize_layout(test_sku, generator)
    
    # 列出所有可用样式
    print("\n📋 所有可用样式:")
    for style_info in BoxMarkGenerator.list_available_styles():
        print(f"  - {style_info['name']}: {style_info['description']}")
        print(f"    必需参数: {', '.join(style_info['required_params'])}")
