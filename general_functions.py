from PIL import Image, ImageDraw, ImageFont
import numpy as np  
import pathlib as Path
import barcode
from barcode.writer import ImageWriter
base_dir = Path.Path(__file__).parent
from layout_engine import Element, Column, Row, Image as ImageElement
import textwrap

# ────────────────────────────────────────────────────────────────────────────
# fpdf2 工具函数 (新增)
#   单位全部使用毫米 (mm)；ppi 用于 PIL 图像尺寸到 mm 的换算
# ────────────────────────────────────────────────────────────────────────────

def px_to_mm(px, ppi):
    """像素 → 毫米"""
    return px * 25.4 / ppi

def mm_to_px(mm, ppi):
    """毫米 → 像素（取整）"""
    return int(mm * ppi / 25.4)

def cm_to_mm(cm):
    return cm * 10.0

def get_max_font_size_mm(text, font_path, target_width_mm, max_height_mm=None,
                         min_size=6, max_size=500, ppi=300):
    """
    二分找出令文字宽度 ≤ target_width_mm（且高度 ≤ max_height_mm）的最大 pt 字号。
    使用 PIL 字体量测，结果转为 mm 再比对。
    """
    px_per_mm = ppi / 25.4
    temp_img = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(temp_img)

    best = min_size
    lo, hi = min_size, max_size
    while lo <= hi:
        mid = (lo + hi) // 2
        font = ImageFont.truetype(font_path, mid)
        bbox = draw.textbbox((0, 0), text, font=font)
        w_mm = (bbox[2] - bbox[0]) / px_per_mm
        h_mm = (bbox[3] - bbox[1]) / px_per_mm
        w_ok = w_mm <= target_width_mm
        h_ok = max_height_mm is None or h_mm <= max_height_mm
        if w_ok and h_ok:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best

def generate_barcode_png_bytes(code_str, width_mm, height_mm, ppi=300):
    """
    生成条形码，返回 PNG bytes（透明背景）及实际像素尺寸。
    返回值: (png_bytes: BytesIO, actual_w_px, actual_h_px)
    """
    from io import BytesIO
    Code128 = barcode.get_barcode_class("code128")
    bar = Code128(code_str, writer=ImageWriter())
    options = {"write_text": False, "module_height": 15.0, "quiet_zone": 1.0}
    img = bar.render(writer_options=options)
    img = img.convert("RGBA")

    # 白色 → 透明
    data = img.getdata()
    new_data = [
        (255, 255, 255, 0) if (r > 250 and g > 250 and b > 250) else (r, g, b, a)
        for r, g, b, a in data
    ]
    img.putdata(new_data)

    # 强制缩放到目标尺寸
    px_per_mm = ppi / 25.4
    target_w = max(1, int(width_mm * px_per_mm))
    target_h = max(1, int(height_mm * px_per_mm))
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf, target_w, target_h

def draw_s_curve_polygon_mm(pdf, x3_mm, y3_mm, x4_mm, y4_mm, canvas_h_mm, fill_rgb=(0, 0, 0)):
    """
    在 PDF 上绘制 S 弯填充多边形（平滑过渡区，从 (x3,y3) 到 (x4,y4)），
    用 smoothstep 计算 20 段折线拟合曲线，再封底形成多边形。
    所有坐标单位为 mm。
    """
    points = []
    for i in range(21):
        t = i / 20.0
        t_smooth = t * t * (3.0 - 2.0 * t)
        cx = x3_mm + (x4_mm - x3_mm) * t
        cy = y3_mm + (y4_mm - y3_mm) * t_smooth
        points.append((cx, cy))
    # 封底
    points.append((x4_mm, canvas_h_mm))
    points.append((x3_mm, canvas_h_mm))

    if not points:
        return
    pdf.set_fill_color(*fill_rgb)
    # 构造 PDF path
    pdf.move_to(*points[0])
    for pt in points[1:]:
        pdf.line_to(*pt)
    pdf.close_path()
    pdf.fill()
'''
已有的函数千万别动，但是可以调用它们，或者复制粘贴到新的函数里修改
可以在后面无限加自己的函数

'''


def paste_center_with_height(canvas, icon, height_cm, dpi):
    """
    将 icon 按照指定高度等比例缩放后，居中粘贴到 canvas 上
    """
    # 1. 计算目标高度的像素值 (10cm)
    # 300 PPI 下，1英寸=2.54cm，所以 10cm 对应的像素如下：
    target_height_px = int(height_cm * dpi)  # 10 cm 转像素

    # 2. 计算缩放比例并调整图片大小
    # 原始尺寸
    original_w, original_h = icon.size
    # 计算比例：保持长宽比不变
    ratio = target_height_px / original_h
    target_width_px = int(original_w * ratio)

    # 调整图标尺寸 (使用 Resampling.LANCZOS 保证印刷级清晰度)
    icon_resized = icon.resize((target_width_px, target_height_px), Image.Resampling.LANCZOS)

    # 3. 计算居中坐标
    # 画布尺寸 (l_px 是长，w_px 是宽)
    canvas_w, canvas_h = canvas.size
    # 居中位置 = (画布宽 - 图标宽)//2 , (画布高 - 图标高)//2
    paste_x = (canvas_w - target_width_px) // 2
    paste_y = (canvas_h - target_height_px) // 2

    # 4. 粘贴到画布 (注意：必须使用 icon_resized 自身作为 mask 以保持透明背景)
    canvas.paste(icon_resized, (paste_x, paste_y), mask=icon_resized)
    
    return canvas

def paste_center_with_width(canvas, icon, width_cm, dpi):
    """
    将 icon 按照指定宽度等比例缩放后，居中粘贴到 canvas 上
    """
    # 1. 计算目标宽度的像素值
    target_width_px = int(width_cm * dpi)

    # 2. 计算缩放比例并调整图片大小
    original_w, original_h = icon.size
    ratio = target_width_px / original_w
    target_height_px = int(original_h * ratio)

    # 调整图标尺寸
    icon_resized = icon.resize((target_width_px, target_height_px), Image.Resampling.LANCZOS)

    # 3. 计算居中坐标
    canvas_w, canvas_h = canvas.size
    paste_x = (canvas_w - target_width_px) // 2
    paste_y = (canvas_h - target_height_px) // 2

    # 4. 粘贴到画布
    canvas.paste(icon_resized, (paste_x, paste_y), mask=icon_resized)
    
    return canvas

def scale_by_height(image, target_height):
    """根据目标高度等比例缩放图片"""
    if not isinstance(image, Image.Image):
        image = Image.open(image).convert("RGBA")
    w, h = image.size
    target_width = int(w * (target_height / h))
    return image.resize((target_width, target_height), Image.Resampling.LANCZOS)

def scale_by_width(image, target_width):
    """根据目标宽度等比例缩放图片"""
    if not isinstance(image, Image.Image):
        image = Image.open(image).convert("RGBA")
    w, h = image.size
    target_height = int(h * (target_width / w))
    return image.resize((target_width, target_height), Image.Resampling.LANCZOS)

def paste_image_center_with_heightorwidth(canvas, icon, height=None, width=None, x_offset=0, y_offset=0):
    """ 推荐使用 """
    
    """
    将 icon 缩放后居中粘贴到 canvas 上。
    height 和 width 均为像素值，至少传入其中一个：
      - 只传 height：按高度缩放，宽度等比例自动计算
      - 只传 width ：按宽度缩放，高度等比例自动计算
      - 两者都传  ：同时满足两个约束，取缩放比例较小的那个（即等比例缩放到能装入指定框中）
    """
    orig_w, orig_h = icon.size

    if height is None and width is None:
        # 不传尺寸：以原始尺寸居中粘贴
        new_w, new_h = orig_w, orig_h
        icon_resized = icon
    elif height is not None and width is not None:
        # 取两个方向比例中较小的，保证图片完整装入指定框
        ratio = min(width / orig_w, height / orig_h)
        new_w = int(orig_w * ratio)
        new_h = int(orig_h * ratio)
        icon_resized = icon.resize((new_w, new_h), Image.Resampling.LANCZOS)
    elif height is not None:
        ratio = height / orig_h
        new_w = int(orig_w * ratio)
        new_h = int(orig_h * ratio)
        icon_resized = icon.resize((new_w, new_h), Image.Resampling.LANCZOS)
    else:
        ratio = width / orig_w
        new_w = int(orig_w * ratio)
        new_h = int(orig_h * ratio)
        icon_resized = icon.resize((new_w, new_h), Image.Resampling.LANCZOS)

    canvas_w, canvas_h = canvas.size
    paste_x = (canvas_w - new_w) // 2 + x_offset
    paste_y = (canvas_h - new_h) // 2 + y_offset

    if icon_resized.mode == 'RGBA':
        canvas.paste(icon_resized, (paste_x, paste_y), mask=icon_resized)
    else:
        canvas.paste(icon_resized, (paste_x, paste_y))

    return canvas

def draw_rounded_bg_for_text(draw, bbox, sku_config, color_xy,
                             bg_color=(0, 0, 0), padding_cm=(0.8, 0.3), radius=15):
    """
    只绘制圆角矩形背景，并返回建议的文字起始坐标。
    """
    # 1. 计算文字尺寸（只测量，不绘制）
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    # 2. 转换间距
    px_padding_x = int(padding_cm[0] * sku_config.dpi) #左右内边距 padding_cm[0]
    px_padding_y = int(padding_cm[1] * sku_config.dpi) #上下内边距 padding_cm[1]
    
    # 调整上下边距比例，使视觉上更平衡
    px_padding_y_top = int(px_padding_y * 0.7 )    # 上边距增加30%
    px_padding_y_bottom = int(px_padding_y * 1.4 ) # 下边距减少30%
    
    # 3. 计算黑框整体尺寸
    rect_w = text_w + 2 * px_padding_x
    rect_h = text_h + px_padding_y_top + px_padding_y_bottom
    
    # 4. 计算黑框坐标 (以右上角为锚点)
    color_x, color_y = color_xy
    rect_x0 = color_x - px_padding_x
    rect_y0 = color_y - px_padding_y_top
    rect_x1 = color_x + text_w + px_padding_x
    rect_y1 = color_y + text_h + px_padding_y_bottom
    
    # 5. 绘制圆角矩形
    draw.rounded_rectangle([rect_x0, rect_y0, rect_x1, rect_y1], radius=radius, fill=bg_color)
    return draw


def draw_smooth_ellipse(draw, canvas, box, fill=(0, 0, 0), scale=4):
    """
    可以用于Mconbo两种样式正唛产品名下方的椭圆形装饰
    在指定的 box 区域内绘制一个丝滑的椭圆形（抗锯齿）
    scale: 放大倍数，越高越丝滑，通常 4 足够。
    """
    x0, y0, x1, y1 = box
    w = int((x1 - x0) * scale)
    h = int((y1 - y0) * scale)
    
    # 创建一个透明的高清临时层
    temp_img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    
    # 在高清层画椭圆
    temp_draw.ellipse([0, 0, w, h], fill=fill)
    
    # 缩小回目标尺寸 (使用 LANCZOS 或 HAMMING 滤镜)
    smooth_line = temp_img.resize((int(x1 - x0), int(y1 - y0)), resample=Image.LANCZOS)
    
    # 粘贴回主画布
    canvas.paste(smooth_line, (int(x0), int(y0)), mask=smooth_line)
    
def draw_dynamic_bottom_bg(canvas, sku_config, icon_company, icon_box_number, font_paths):
    draw = ImageDraw.Draw(canvas)
    canvas_w, canvas_h = canvas.size
    bottom_bg_h = int(sku_config.bottom_gb_h * sku_config.dpi)
    # --- 1. 计算基础尺寸 ---
    h_right = int( 10 * sku_config.dpi)  # 10 cm 高的黑色底框
    h_left = int( 0.5 * h_right)  # 左侧底框高度为右侧的50%    
    margin_1cm = int( 1 * sku_config.dpi)
    margin_2cm = int( 2 * sku_config.dpi)  
    margin_3cm = int( 3 * sku_config.dpi)
    margin_4cm = int( 4 * sku_config.dpi)
    margin_6cm = int( 6 * sku_config.dpi)
    margin_8cm = int( 8 * sku_config.dpi)
    margin_10cm = int( 10 * sku_config.dpi)  
    
    # --- 2. 处理公司信息 Logo 并确定左侧宽度 ---
    # Logo 与底框上边缘平齐，高度设为 1.6 cm
    icon_h = int(1.6 * sku_config.dpi) 
    icon_company_res = scale_by_height(icon_company, icon_h)
    icon_company_w, _ = icon_company_res.size
    
    # 左侧“弧头”总宽度 = 1cm + Logo宽 + 4cm
    left_section_w = margin_1cm + icon_company_w + margin_4cm
    
    # --- 3. 绘制异形底框 (黑色) ---
    # A. 左侧小矩形 + 右侧大矩形 + 中间连接部分
    # 绘制贝塞尔曲线过渡部分
    
    # --- a. 准备工作 ---
    # 过渡区的起点 (x3, y3) 和 终点 (x4, y4)
    x3, y3 = left_section_w - margin_10cm, canvas_h - h_left
    x4, y4 = left_section_w , canvas_h - h_right

    # --- b. 绘制左侧和右侧的方块 ---
    # 左侧矮块
    draw.rectangle([0, canvas_h - h_left, x3, canvas_h], fill=(0, 0, 0))
    # 右侧高块
    draw.rectangle([x4, canvas_h - h_right, canvas_w, canvas_h], fill=(0, 0, 0))

    # --- c. 绘制丝滑过渡区 (关键：贝塞尔曲线模拟) ---
    # 我们在 3 到 4 之间生成 20个点，连成一个平滑的填充区域
    curve_points = []
    for i in range(21):
        t = i / 20
        # 二次方贝塞尔公式：(1-t)^2*P0 + 2t(1-t)*P1 + t^2*P2
        # 这里我们简化处理，让它形成一个 S 形
        curr_x = x3 + (x4 - x3) * t
        # 使用 smoothstep 函数使 y 的变化更平滑
        t_smooth = t * t * (3 - 2 * t) 
        curr_y = y3 + (y4 - y3) * t_smooth
        curve_points.append((curr_x, curr_y))

    # 将曲线点与底部封口，形成封闭图形填充
    curve_fill_path = curve_points + [(x4, canvas_h), (x3, canvas_h)]
    draw.polygon(curve_fill_path, fill=(0, 0, 0))
    
    # B. 粘贴公司信息 Logo
    icon_x = margin_1cm
    icon_y = canvas_h - bottom_bg_h
    canvas.paste(icon_company_res, (icon_x, icon_y), mask=icon_company_res)
    
    # C. 粘贴左下角箱号信息
    icon_box_h = int( h_right * 1/4)  # 高度为底框高度的25%
    icon_box_res = scale_by_height(icon_box_number, icon_box_h)
    icon_box_w, icon_box_h = icon_box_res.size
    icon_box_x = margin_1cm
    icon_box_y = int(canvas_h - h_left + (h_left - icon_box_h) // 2)  # 垂直居中
    canvas.paste(icon_box_res, (icon_box_x, icon_box_y), mask=icon_box_res)
    
    # --- 4. 动态 SKU 文字 (带自动缩放) ---
    # 可用宽度：从 margin_1cm + icon_company_w 到 canvas_w - margin_3cm
    max_sku_w = canvas_w - (margin_1cm + icon_company_w) - margin_3cm
    max_sku_h = margin_8cm  # 文字高度不超过 8cm（增大以让文字更显眼）
    # 初始字号应该根据高度动态计算（字号单位是像素）
    current_sku_size = int(max_sku_h * 1.2)  # 初始为最大高度的1.2倍
    min_sku_size = int(max_sku_h * 0.15)  # 最小字号为最大高度的15%
    
    print(f"[正唛SKU调试] 画布宽度: {canvas_w}px ({canvas_w/sku_config.dpi:.1f}cm)")
    print(f"[正唛SKU调试] 可用SKU宽度: {max_sku_w}px ({max_sku_w/sku_config.dpi:.1f}cm)")
    print(f"[正唛SKU调试] 可用SKU高度: {max_sku_h}px ({max_sku_h/sku_config.dpi:.1f}cm)")
    print(f"[正唛SKU调试] 初始字号: {current_sku_size}pt, 最小字号: {min_sku_size}pt")
    
    # 自动减小字号直到宽度和高度都满足要求
    sku_font = None
    while current_sku_size > min_sku_size:
        test_font = ImageFont.truetype(font_paths['calibri_bold'], size=current_sku_size)
        bbox = draw.textbbox((0, 0), sku_config.sku_name, font=test_font)
        sw = bbox[2] - bbox[0]
        sh = bbox[3] - bbox[1]
        
        # 检查宽度和高度是否都符合要求
        if sw <= max_sku_w and sh <= max_sku_h:
            sku_font = test_font
            sku_w, sku_h = sw, sh
            print(f"[正唛SKU调试] 最终字号: {current_sku_size}pt, 文字尺寸: {sw}x{sh}px ({sw/sku_config.dpi:.1f}x{sh/sku_config.dpi:.1f}cm)")
            break
        current_sku_size -= 5
    
    # 如果没有找到合适的字号，使用最小字号
    if sku_font is None:
        sku_font = ImageFont.truetype(font_paths['calibri_bold'], size=min_sku_size)
        bbox = draw.textbbox((0, 0), sku_config.sku_name, font=sku_font)
        sku_w = bbox[2] - bbox[0]
        sku_h = bbox[3] - bbox[1]

    # 绘制 SKU (在底框右侧区域中居中)
    # 计算 SKU 可用区域的中心点
    sku_area_left = margin_1cm + icon_company_w + margin_3cm
    sku_area_right = canvas_w - margin_3cm
    sku_center_x = (sku_area_left + sku_area_right) // 2
    
    # 底框高度区域的垂直中心，稍微向下偏移
    offset_y = int(0.3 * sku_config.dpi)  # 向下偏移 0.3cm
    sku_center_y = canvas_h - h_right // 2 + offset_y
    
    # 使用 "mm" anchor 让文字的中心点对齐到区域中心
    draw.text((sku_center_x, sku_center_y), sku_config.sku_name, font=sku_font, fill=(161, 142, 102), anchor="mm")


def draw_dynamic_bottom_bg_move(canvas, sku_config, icon_company, icon_box_number, font_paths):
    draw = ImageDraw.Draw(canvas)
    canvas_w, canvas_h = canvas.size
    bottom_bg_h = int(sku_config.bottom_gb_h * sku_config.dpi)
    # --- 1. 计算基础尺寸 ---
    h_right = int(10 * sku_config.dpi)  # 10 cm 高的黑色底框
    h_left = int(0.5 * h_right)  # 左侧底框高度为右侧的50%
    margin_1cm = int(1 * sku_config.dpi)
    margin_2cm = int(2 * sku_config.dpi)
    margin_3cm = int(3 * sku_config.dpi)
    margin_4cm = int(4 * sku_config.dpi)
    margin_6cm = int(6 * sku_config.dpi)
    margin_8cm = int(8 * sku_config.dpi)
    margin_10cm = int(10 * sku_config.dpi)

    # SKU区域边距（减小黑边）
    sku_margin = int(0.5 * sku_config.dpi)  # 0.5cm边距，原来是3cm
    # 公司信息上移距离（增加上移）
    company_offset_cm = 1.5  # 1.5cm，原来是0.3cm

    # --- 2. 处理公司信息 Logo 并确定左侧宽度 ---
    # Logo 与底框上边缘平齐，高度设为 1.6 cm
    icon_h = int(1.6 * sku_config.dpi)
    icon_company_res = scale_by_height(icon_company, icon_h)
    icon_company_w, _ = icon_company_res.size

    # 左侧"弧头"总宽度 = 1cm + Logo宽 + 4cm
    left_section_w = margin_1cm + icon_company_w + margin_4cm

    # --- 3. 计算SKU最小字号需求的空间 ---
    # SKU最小字号180pt对应的像素值
    min_sku_size_pt = 180
    min_sku_size_px = int(min_sku_size_pt * sku_config.ppi / 72)

    # 计算180pt字号下SKU文字的尺寸
    min_sku_font = ImageFont.truetype(font_paths['calibri_bold'], size=min_sku_size_px)
    min_sku_bbox = draw.textbbox((0, 0), sku_config.sku_name, font=min_sku_font)
    min_sku_w = min_sku_bbox[2] - min_sku_bbox[0]
    min_sku_h = min_sku_bbox[3] - min_sku_bbox[1]

    # 计算需要的总空间：左侧矮块 + S弯(10cm) + SKU区域(3cm边距+文字宽度+3cm边距)
    required_sku_area_width = sku_margin + min_sku_w + sku_margin
    # SKU黑框左边界位置（从右往左算）
    sku_block_left = canvas_w - required_sku_area_width
    # 判断是否冲突：公司区域右边界是否超过SKU黑框左边界
    space_is_enough = left_section_w <= sku_block_left

    print(f"[正唛SKU调试] 画布宽度: {canvas_w}px ({canvas_w / sku_config.dpi:.1f}cm)")
    print(f"[正唛SKU调试] 公司信息宽度: {left_section_w}px ({left_section_w / sku_config.dpi:.1f}cm)")
    print(f"[正唛SKU调试] SKU区域左边界: {sku_block_left}px ({sku_block_left / sku_config.dpi:.1f}cm)")
    print(f"[正唛SKU调试] 是否冲突: {not space_is_enough}, 公司右边界{'>' if not space_is_enough else '<='}SKU左边界")
    # --- 4. 根据空间是否足够，决定布局方式 ---
    if space_is_enough:
        # ===== 空间足够：使用原有逻辑 =====
        # 过渡区的起点 (x3, y3) 和 终点 (x4, y4)

        # 公司信息位置：与底框上边缘平齐
        icon_x = margin_1cm
        icon_y = canvas_h - bottom_bg_h

        # SKU可用区域
        # 底部黑框：左侧矮块 + S弯 + 右侧高块
        x3 = left_section_w - margin_10cm  # 左侧矮块右边界/S弯起点
        x4 = left_section_w  # S弯终点/右侧高块左边界

        # SKU在右侧高块区域内居中（使用更小的边距）
        sku_area_left = x4 - 6*sku_margin
        sku_area_right = canvas_w - sku_margin

    else:
        # ===== 空间不足：错开布局 =====
        # ===== 空间不足：错开布局，SKU黑框向左扩展 =====
        print(f"[正唛SKU调试] 使用错开布局，SKU黑框向左扩展")

        # 公司信息上移到底框上方
        icon_x = margin_1cm
        icon_y = canvas_h - bottom_bg_h - icon_h - int(company_offset_cm * sku_config.dpi)
        # SKU黑框向左扩展以容纳180pt文字
        # 右侧高块左边界向左移动
        x4 = canvas_w - sku_margin - min_sku_w - sku_margin
        # 确保右侧高块不会太小（至少6cm）
        min_x4 = margin_6cm + margin_10cm
        if x4 < min_x4:
            x4 = min_x4

        # S弯起点
        x3 = x4 - margin_10cm

        # 确保x3不会小于0
        if x3 < margin_1cm:
            x3 = margin_1cm
            x4 = x3 + margin_10cm
            # 计算S弯的y坐标（与空间足够时相同）
            # SKU在扩展后的右侧高块区域内
        sku_area_left = x4 - 6 *sku_margin
        sku_area_right = canvas_w - sku_margin

    # S弯的y坐标
    y3 = canvas_h - h_left
    y4 = canvas_h - h_right

    # --- 5. 绘制异形底框 (黑色) ---
    # 左侧矮块
    draw.rectangle([0, canvas_h - h_left, x3, canvas_h], fill=(0, 0, 0))
    # 右侧高块
    draw.rectangle([x4, canvas_h - h_right, canvas_w, canvas_h], fill=(0, 0, 0))

    # 绘制丝滑过渡区 (关键：贝塞尔曲线模拟)
    curve_points = []
    for i in range(21):
        t = i / 20
        curr_x = x3 + (x4 - x3) * t
        t_smooth = t * t * (3 - 2 * t)
        curr_y = y3 + (y4 - y3) * t_smooth
        curve_points.append((curr_x, curr_y))

    curve_fill_path = curve_points + [(x4, canvas_h), (x3, canvas_h)]
    draw.polygon(curve_fill_path, fill=(0, 0, 0))

    # B. 粘贴公司信息 Logo
    canvas.paste(icon_company_res, (icon_x, icon_y), mask=icon_company_res)

    # C. 粘贴左下角箱号信息
    icon_box_h = int(h_right * 1 / 4)  # 高度为底框高度的25%
    icon_box_res = scale_by_height(icon_box_number, icon_box_h)
    icon_box_w, icon_box_h = icon_box_res.size
    icon_box_x = margin_1cm
    icon_box_y = int(canvas_h - h_left + (h_left - icon_box_h) // 2)  # 垂直居中
    canvas.paste(icon_box_res, (icon_box_x, icon_box_y), mask=icon_box_res)

    # --- 6. 绘制 SKU 文字 ---
    # 计算 SKU 区域的中心点
    sku_center_x = (sku_area_left + sku_area_right) // 2

    # 底框高度区域的垂直中心，稍微向下偏移
    offset_y = int(0.3 * sku_config.dpi)  # 向下偏移 0.3cm
    sku_center_y = canvas_h - h_right // 2 + offset_y

    # 使用 "mm" anchor 让文字的中心点对齐到区域中心
    draw.text((sku_center_x, sku_center_y), sku_config.sku_name, font=min_sku_font,
              fill=(161, 142, 102), anchor="mm")
    print(f"[正唛SKU调试] 最终SKU字号: {min_sku_size_pt}pt, 区域: {sku_area_left}-{sku_area_right}px")

    
    
def draw_side_dynamic_bottom_bg(canvas, sku_config, icon_company, font_paths):
    draw = ImageDraw.Draw(canvas)
    canvas_w, canvas_h = canvas.size
    bottom_bg_h = int(sku_config.bottom_gb_h * sku_config.dpi)
    # --- 1. 计算基础尺寸 ---
    h_left = int( sku_config.dpi * sku_config.bottom_gb_h)  # 10 cm 高的黑色底框  
    h_right =  int( h_left * 0.5) # 右侧侧底框高度为左侧的50%
    
    margin_1cm = int( 1 * sku_config.dpi)
    margin_2cm = int( 2 * sku_config.dpi)  
    margin_3cm = int( 3 * sku_config.dpi)
    margin_4cm = int( 4 * sku_config.dpi)
    margin_6cm = int( 6 * sku_config.dpi)
    margin_8cm = int( 8 * sku_config.dpi)
    margin_10cm = int( 10 * sku_config.dpi)  
    
    # --- 2. 处理公司信息 Logo 并确定右侧宽度 ---
    # Logo 与底框上边缘平齐，高度设为 1.6 cm
    icon_h = int(1.6 * sku_config.dpi) 
    icon_company_res = scale_by_height(icon_company, icon_h)
    icon_company_w, _ = icon_company_res.size
    
    # 侧唛SKU黑框部分长度与正唛设计相同，即左侧“弧头”总宽度 = 1cm + Logo宽 + 4cm。sku_config.l_px - 该值就是右侧底框宽度
    left_section_w = sku_config.l_px - (margin_1cm + icon_company_w + margin_4cm)
    
    # 边界检查：如果正唛太宽，需要限制 left_section_w 不超过侧唛宽度
    # 确保至少留出过渡区域（10cm）和右侧一些空间
    max_left_section_w = canvas_w - margin_10cm - margin_4cm  # 留出过渡区和右侧边距
    if left_section_w > max_left_section_w:
        left_section_w = max_left_section_w
        print(f"警告：正唛宽度过大，侧唛SKU黑框已自动调整为 {left_section_w / sku_config.dpi:.1f}cm")
    
    # --- 3. 绘制异形底框 (黑色) ---
    # A. 左侧小矩形 + 右侧大矩形 + 中间连接部分
    # 绘制贝塞尔曲线过渡部分
    
    # --- a. 准备工作 ---
    # 过渡区的起点 (x3, y3) 和 终点 (x4, y4)
    x3, y3 = left_section_w, canvas_h - h_left
    x4, y4 = min(left_section_w + margin_10cm, canvas_w - margin_1cm), canvas_h - h_right  # 确保 x4 不超过画布宽度

    # --- b. 绘制左侧和右侧的方块 ---
    # 左侧高块
    draw.rectangle([0, canvas_h - h_left, x3, canvas_h], fill=(0, 0, 0))
    # 右侧矮块
    draw.rectangle([x4, canvas_h - h_right, canvas_w, canvas_h], fill=(0, 0, 0))

    # --- c. 绘制丝滑过渡区 (关键：贝塞尔曲线模拟) ---
    # 我们在 3 到 4 之间生成 20个点，连成一个平滑的填充区域
    curve_points = []
    for i in range(21):
        t = i / 20
        # 二次方贝塞尔公式：(1-t)^2*P0 + 2t(1-t)*P1 + t^2*P2
        # 这里我们简化处理，让它形成一个 S 形
        curr_x = x3 + (x4 - x3) * t
        # 使用 smoothstep 函数使 y 的变化更平滑
        t_smooth = t * t * (3 - 2 * t) 
        curr_y = y3 + (y4 - y3) * t_smooth
        curve_points.append((curr_x, curr_y))

    # 将曲线点与底部封口，形成封闭图形填充
    curve_fill_path = curve_points + [(x4, canvas_h), (x3, canvas_h)]
    draw.polygon(curve_fill_path, fill=(0, 0, 0))
    

    
    # --- 4. 动态 SKU 文字 (带自动缩放) ---
    # 可用宽度：从 margin_1cm + icon_company_w 到 canvas_w - margin_3cm
    max_sku_w = left_section_w
    max_sku_h = margin_8cm  # 文字高度不超过 8cm
    # 初始字号应该根据高度动态计算（字号单位是像素）
    current_sku_size = int(max_sku_h * 1.2)  # 初始为最大高度的1.2倍
    min_sku_size = int(max_sku_h * 0.15)  # 最小字号为最大高度的15%
    
    # 自动减小字号直到宽度和高度都满足要求
    sku_font = None
    while current_sku_size > min_sku_size:
        test_font = ImageFont.truetype(font_paths['calibri_bold'], size=current_sku_size)
        bbox = draw.textbbox((0, 0), sku_config.sku_name, font=test_font)
        sw = bbox[2] - bbox[0]
        sh = bbox[3] - bbox[1]
        
        # 检查宽度和高度是否都符合要求
        if sw <= max_sku_w and sh <= max_sku_h:
            sku_font = test_font
            sku_w, sku_h = sw, sh
            break
        current_sku_size -= 5
    
    # 如果没有找到合适的字号，使用最小字号
    if sku_font is None:
        sku_font = ImageFont.truetype(font_paths['calibri_bold'], size=min_sku_size)
        bbox = draw.textbbox((0, 0), sku_config.sku_name, font=sku_font)
        sku_w = bbox[2] - bbox[0]
        sku_h = bbox[3] - bbox[1]

    # 绘制 SKU (在底框左侧区域中居中)
    # 计算 SKU 可用区域的中心点
    sku_area_left = margin_3cm 
    sku_area_right = left_section_w
    sku_center_x = (sku_area_left + sku_area_right) // 2
    
    # 底框高度区域的垂直中心，稍微向下偏移
    offset_y = int(0.3 * sku_config.dpi)  # 向下偏移 0.3cm
    sku_center_y = canvas_h - h_left // 2 + offset_y
    
    # 使用 "mm" anchor 让文字的中心点对齐到区域中心
    draw.text((sku_center_x, sku_center_y), sku_config.sku_name, font=sku_font, fill=(161, 142, 102), anchor="mm")
    pass


def draw_side_dynamic_bottom_bg_standard(canvas, sku_config, icon_company, font_paths):
    draw = ImageDraw.Draw(canvas)
    canvas_w, canvas_h = canvas.size
    # === 如果启用旋转模式（侧唛在右侧垂直条） ===
    bottom_bg_h = int(sku_config.bottom_gb_h * sku_config.dpi)
    # --- 1. 计算基础尺寸 ---
    h_left = int(sku_config.dpi * 10)  # 10 cm 高的黑色底框
    h_right = int(h_left * 0.5)  # 右侧侧底框高度为左侧的50%

    margin_1cm = int(1 * sku_config.dpi)
    margin_2cm = int(2 * sku_config.dpi)
    margin_3cm = int(3 * sku_config.dpi)
    margin_4cm = int(4 * sku_config.dpi)
    margin_6cm = int(6 * sku_config.dpi)
    margin_8cm = int(8 * sku_config.dpi)
    margin_10cm = int(10 * sku_config.dpi)

    # --- 2. 处理公司信息 Logo 并确定右侧宽度 ---
    # Logo 与底框上边缘平齐，高度设为 1.6 cm
    icon_h = int(1.6 * sku_config.dpi)
    icon_company_res = scale_by_height(icon_company, icon_h)
    icon_company_w, _ = icon_company_res.size

    # 侧唛SKU黑框部分长度与正唛设计相同，即左侧“弧头”总宽度 = 1cm + Logo宽 + 4cm。sku_config.l_px - 该值就是右侧底框宽度
    left_section_w = sku_config.l_px - (margin_1cm + icon_company_w + margin_4cm)

    # 边界检查：如果正唛太宽，需要限制 left_section_w 不超过侧唛宽度
    # 确保至少留出过渡区域（10cm）和右侧一些空间
    max_left_section_w = canvas_w - margin_10cm - margin_4cm  # 留出过渡区和右侧边距
    if left_section_w > max_left_section_w:
        left_section_w = max_left_section_w
        print(f"警告：正唛宽度过大，侧唛SKU黑框已自动调整为 {left_section_w / sku_config.dpi:.1f}cm")

    # --- 3. 绘制异形底框 (黑色) ---
    # A. 左侧小矩形 + 右侧大矩形 + 中间连接部分
    # 绘制贝塞尔曲线过渡部分

    # --- a. 准备工作 ---
    # 过渡区的起点 (x3, y3) 和 终点 (x4, y4)
    x3, y3 = left_section_w, canvas_h - h_left
    x4, y4 = min(left_section_w + margin_10cm, canvas_w - margin_1cm), canvas_h - h_right  # 确保 x4 不超过画布宽度

    # --- b. 绘制左侧和右侧的方块 ---
    # 左侧高块
    draw.rectangle([0, canvas_h - h_left, x3, canvas_h], fill=(0, 0, 0))
    # 右侧矮块
    draw.rectangle([x4, canvas_h - h_right, canvas_w, canvas_h], fill=(0, 0, 0))

    # --- c. 绘制丝滑过渡区 (关键：贝塞尔曲线模拟) ---
    # 我们在 3 到 4 之间生成 20个点，连成一个平滑的填充区域
    curve_points = []
    for i in range(21):
        t = i / 20
        # 二次方贝塞尔公式：(1-t)^2*P0 + 2t(1-t)*P1 + t^2*P2
        # 这里我们简化处理，让它形成一个 S 形
        curr_x = x3 + (x4 - x3) * t
        # 使用 smoothstep 函数使 y 的变化更平滑
        t_smooth = t * t * (3 - 2 * t)
        curr_y = y3 + (y4 - y3) * t_smooth
        curve_points.append((curr_x, curr_y))

    # 将曲线点与底部封口，形成封闭图形填充
    curve_fill_path = curve_points + [(x4, canvas_h), (x3, canvas_h)]
    draw.polygon(curve_fill_path, fill=(0, 0, 0))

    # --- 4. 动态 SKU 文字 (带自动缩放) ---
    # 可用宽度：从 margin_1cm + icon_company_w 到 canvas_w - margin_3cm
    max_sku_w = left_section_w
    max_sku_h = margin_8cm  # 文字高度不超过 8cm
    # 初始字号应该根据高度动态计算（字号单位是像素）
    current_sku_size = int(max_sku_h * 1.2)  # 初始为最大高度的1.2倍
    min_sku_size = int(max_sku_h * 0.15)  # 最小字号为最大高度的15%

    # 自动减小字号直到宽度和高度都满足要求
    sku_font = None
    while current_sku_size > min_sku_size:
        test_font = ImageFont.truetype(font_paths['calibri_bold'], size=current_sku_size)
        bbox = draw.textbbox((0, 0), sku_config.sku_name, font=test_font)
        sw = bbox[2] - bbox[0]
        sh = bbox[3] - bbox[1]

        # 检查宽度和高度是否都符合要求
        if sw <= max_sku_w and sh <= max_sku_h:
            sku_font = test_font
            sku_w, sku_h = sw, sh
            break
        current_sku_size -= 5

    # 如果没有找到合适的字号，使用最小字号
    if sku_font is None:
        sku_font = ImageFont.truetype(font_paths['calibri_bold'], size=min_sku_size)
        bbox = draw.textbbox((0, 0), sku_config.sku_name, font=sku_font)
        sku_w = bbox[2] - bbox[0]
        sku_h = bbox[3] - bbox[1]

    # 绘制 SKU (在底框左侧区域中居中)
    # 计算 SKU 可用区域的中心点
    sku_area_left = margin_3cm
    sku_area_right = left_section_w
    sku_center_x = (sku_area_left + sku_area_right) // 2

    # 底框高度区域的垂直中心，稍微向下偏移
    offset_y = int(0.3 * sku_config.dpi)  # 向下偏移 0.3cm
    sku_center_y = canvas_h - h_left // 2 + offset_y

    # 使用 "mm" anchor 让文字的中心点对齐到区域中心
    draw.text((sku_center_x, sku_center_y), sku_config.sku_name, font=sku_font, fill=(161, 142, 102), anchor="mm")
    return x4

def draw_side_dynamic_bottom_bg_standard_move(canvas, sku_config, icon_company, font_paths):
    draw = ImageDraw.Draw(canvas)
    canvas_w, canvas_h = canvas.size

    # === 非旋转模式 ===
    bottom_bg_h = int(sku_config.bottom_gb_h * sku_config.dpi)
    # --- 1. 计算基础尺寸 ---
    h_left = int(sku_config.dpi * sku_config.bottom_gb_h)  # 10 cm 高的黑色底框
    h_right = int(h_left * 0.5)  # 右侧矮块高度为左侧的50%

    margin_1cm = int(1 * sku_config.dpi)
    margin_2cm = int(2 * sku_config.dpi)
    margin_3cm = int(3 * sku_config.dpi)
    margin_4cm = int(4 * sku_config.dpi)
    margin_6cm = int(6 * sku_config.dpi)
    margin_8cm = int(8 * sku_config.dpi)
    margin_10cm = int(10 * sku_config.dpi)

    # SKU区域边距
    sku_margin = int(0.5 * sku_config.dpi)  # 0.5cm边距

    # --- 2. 动态计算SKU字号和黑框宽度 ---
    # 最大可用宽度（留出S弯10cm + 右侧矮块4cm）
    max_sku_block_width = canvas_w - margin_10cm - margin_4cm
    max_sku_h = margin_8cm  # 文字高度不超过8cm

    # 从180pt开始尝试，逐渐减小直到宽度合适
    min_sku_size_pt = 180
    current_sku_size_px = int(min_sku_size_pt * sku_config.ppi / 72)
    min_sku_size_px = int(max_sku_h * 0.15)  # 最小字号

    sku_font = None
    sku_w = 0
    while current_sku_size_px >= min_sku_size_px:
        test_font = ImageFont.truetype(font_paths['calibri_bold'], size=current_sku_size_px)
        bbox = draw.textbbox((0, 0), sku_config.sku_name, font=test_font)
        sw = bbox[2] - bbox[0]
        sh = bbox[3] - bbox[1]

        # 检查宽度和高度是否都满足
        if sw <= max_sku_block_width - 2 * sku_margin and sh <= max_sku_h:
            sku_font = test_font
            sku_w = sw
            sku_h = sh
            min_sku_size_pt = int(current_sku_size_px * 72 / sku_config.ppi)  # 记录实际使用的字号
            break
        current_sku_size_px -= 5

    # 如果都没找到，使用最小字号
    if sku_font is None:
        sku_font = ImageFont.truetype(font_paths['calibri_bold'], size=min_sku_size_px)
        bbox = draw.textbbox((0, 0), sku_config.sku_name, font=sku_font)
        sku_w = bbox[2] - bbox[0]
        sku_h = bbox[3] - bbox[1]
        min_sku_size_pt = int(min_sku_size_px * 72 / sku_config.ppi)

    # --- 3. 根据SKU实际宽度计算黑框宽度 ---
    # 黑框宽度 = 文字宽度 + 边距(0.5cm+0.5cm)
    sku_block_width = sku_w + 2 * sku_margin

    # 限制黑框宽度范围
    if sku_block_width > max_sku_block_width:
        sku_block_width = max_sku_block_width
    if sku_block_width < margin_6cm:  # 最小6cm
        sku_block_width = margin_6cm

    # 计算S弯位置
    x3 = sku_block_width  # 左侧高块右边界/S弯起点
    x4 = x3 + margin_10cm  # S弯终点/右侧矮块左边界

    # 确保不超出画布
    if x4 > canvas_w - margin_1cm:
        x4 = canvas_w - margin_1cm
        x3 = x4 - margin_10cm
        sku_block_width = x3

    print(f"[侧唛SKU调试-普通] 画布宽度: {canvas_w}px ({canvas_w / sku_config.dpi:.1f}cm)")
    print(f"[侧唛SKU调试-普通] SKU文字宽度: {sku_w / sku_config.dpi:.1f}cm, 字号: {min_sku_size_pt}pt")
    print(f"[侧唛SKU调试-普通] 黑框宽度: {sku_block_width / sku_config.dpi:.1f}cm")

    # S弯的y坐标
    y3 = canvas_h - h_left
    y4 = canvas_h - h_right

    # --- 4. 绘制异形底框 (黑色) ---
    # 左侧高块
    draw.rectangle([0, canvas_h - h_left, x3, canvas_h], fill=(0, 0, 0))
    # 右侧矮块
    draw.rectangle([x4, canvas_h - h_right, canvas_w, canvas_h], fill=(0, 0, 0))

    # 绘制丝滑过渡区 (S弯)
    curve_points = []
    for i in range(21):
        t = i / 20
        curr_x = x3 + (x4 - x3) * t
        t_smooth = t * t * (3 - 2 * t)
        curr_y = y3 + (y4 - y3) * t_smooth
        curve_points.append((curr_x, curr_y))

    curve_fill_path = curve_points + [(x4, canvas_h), (x3, canvas_h)]
    draw.polygon(curve_fill_path, fill=(0, 0, 0))

    # --- 5. 绘制 SKU 文字 (180pt，在左侧高块中居中) ---
    sku_area_left = sku_margin
    sku_area_right = x3 +6* sku_margin
    sku_center_x = (sku_area_left + sku_area_right) // 2
    offset_y = int(0.3 * sku_config.dpi)
    sku_center_y = canvas_h - h_left // 2 + offset_y

    draw.text((sku_center_x, sku_center_y), sku_config.sku_name, font=sku_font,
              fill=(161, 142, 102), anchor="mm")
    print(f"[侧唛SKU调试-普通] 最终SKU字号: {min_sku_size_pt}pt, 区域: {sku_area_left}-{sku_area_right}px")
    return x4

def draw_side_dynamic_bottom_bg_vertical(canvas, sku_config, icon_company, font_paths):
    draw = ImageDraw.Draw(canvas)
    canvas_w, canvas_h = canvas.size
    # === 如果启用旋转模式（侧唛在右侧垂直条） ===
    bottom_bg_h = int(sku_config.bottom_gb_h * sku_config.dpi)
    # --- 1. 计算基础尺寸 ---
    h_left = int(sku_config.dpi * 8)  # 10 cm 高的黑色底框
    h_right = int(h_left * 0.5)  # 右侧侧底框高度为左侧的50%

    margin_1cm = int(1 * sku_config.dpi)
    margin_2cm = int(2 * sku_config.dpi)
    margin_3cm = int(3 * sku_config.dpi)
    margin_4cm = int(4 * sku_config.dpi)
    margin_6cm = int(6 * sku_config.dpi)
    margin_8cm = int(8 * sku_config.dpi)
    margin_10cm = int(10 * sku_config.dpi)

    # --- 2. 处理公司信息 Logo 并确定右侧宽度 ---
    # Logo 与底框上边缘平齐，高度设为 1.6 cm
    icon_h = int(1.6 * sku_config.dpi)
    icon_company_res = scale_by_height(icon_company, icon_h)
    icon_company_w, _ = icon_company_res.size

    # 侧唛SKU黑框部分长度与正唛设计相同，即左侧“弧头”总宽度 = 1cm + Logo宽 + 4cm。sku_config.l_px - 该值就是右侧底框宽度
    left_section_w = sku_config.l_px - (margin_1cm + icon_company_w + margin_4cm)

    # 边界检查：如果正唛太宽，需要限制 left_section_w 不超过侧唛宽度
    # 确保至少留出过渡区域（10cm）和右侧一些空间
    max_left_section_w = canvas_w - margin_10cm - margin_4cm  # 留出过渡区和右侧边距
    if left_section_w > max_left_section_w:
        left_section_w = max_left_section_w
        print(f"警告：正唛宽度过大，侧唛SKU黑框已自动调整为 {left_section_w / sku_config.dpi:.1f}cm")

    # --- 3. 绘制异形底框 (黑色) ---
    # A. 左侧小矩形 + 右侧大矩形 + 中间连接部分
    # 绘制贝塞尔曲线过渡部分

    # --- a. 准备工作 ---
    # 过渡区的起点 (x3, y3) 和 终点 (x4, y4)
    x3, y3 = left_section_w, canvas_h - h_left
    x4, y4 = min(left_section_w + margin_10cm, canvas_w - margin_1cm), canvas_h - h_right  # 确保 x4 不超过画布宽度

    # --- b. 绘制左侧和右侧的方块 ---
    # 左侧高块
    draw.rectangle([0, canvas_h - h_left, x3, canvas_h], fill=(0, 0, 0))
    # 右侧矮块
    draw.rectangle([x4, canvas_h - h_right, canvas_w, canvas_h], fill=(0, 0, 0))

    # --- c. 绘制丝滑过渡区 (关键：贝塞尔曲线模拟) ---
    # 我们在 3 到 4 之间生成 20个点，连成一个平滑的填充区域
    curve_points = []
    for i in range(21):
        t = i / 20
        # 二次方贝塞尔公式：(1-t)^2*P0 + 2t(1-t)*P1 + t^2*P2
        # 这里我们简化处理，让它形成一个 S 形
        curr_x = x3 + (x4 - x3) * t
        # 使用 smoothstep 函数使 y 的变化更平滑
        t_smooth = t * t * (3 - 2 * t)
        curr_y = y3 + (y4 - y3) * t_smooth
        curve_points.append((curr_x, curr_y))

    # 将曲线点与底部封口，形成封闭图形填充
    curve_fill_path = curve_points + [(x4, canvas_h), (x3, canvas_h)]
    draw.polygon(curve_fill_path, fill=(0, 0, 0))

    # --- 4. 动态 SKU 文字 (带自动缩放) ---
    # 可用宽度：从 margin_1cm + icon_company_w 到 canvas_w - margin_3cm
    max_sku_w = left_section_w
    max_sku_h = margin_8cm  # 文字高度不超过 8cm
    # 初始字号应该根据高度动态计算（字号单位是像素）
    current_sku_size = int(max_sku_h * 1.2)  # 初始为最大高度的1.2倍
    min_sku_size = int(max_sku_h * 0.15)  # 最小字号为最大高度的15%

    # 自动减小字号直到宽度和高度都满足要求
    sku_font = None
    while current_sku_size > min_sku_size:
        test_font = ImageFont.truetype(font_paths['calibri_bold'], size=current_sku_size)
        bbox = draw.textbbox((0, 0), sku_config.sku_name, font=test_font)
        sw = bbox[2] - bbox[0]
        sh = bbox[3] - bbox[1]

        # 检查宽度和高度是否都符合要求
        if sw <= max_sku_w and sh <= max_sku_h:
            sku_font = test_font
            sku_w, sku_h = sw, sh
            break
        current_sku_size -= 5

    # 如果没有找到合适的字号，使用最小字号
    if sku_font is None:
        sku_font = ImageFont.truetype(font_paths['calibri_bold'], size=min_sku_size)
        bbox = draw.textbbox((0, 0), sku_config.sku_name, font=sku_font)
        sku_w = bbox[2] - bbox[0]
        sku_h = bbox[3] - bbox[1]

    # 绘制 SKU (在底框左侧区域中居中)
    # 计算 SKU 可用区域的中心点
    sku_area_left = margin_3cm
    sku_area_right = left_section_w
    sku_center_x = (sku_area_left + sku_area_right) // 2

    # 底框高度区域的垂直中心，稍微向下偏移
    offset_y = int(0.3 * sku_config.dpi)  # 向下偏移 0.3cm
    sku_center_y = canvas_h - h_left // 2 + offset_y

    # 使用 "mm" anchor 让文字的中心点对齐到区域中心
    draw.text((sku_center_x, sku_center_y), sku_config.sku_name, font=sku_font, fill=(161, 142, 102), anchor="mm")
    return x4

def draw_side_dynamic_bottom_bg_vertical_move(canvas, sku_config, icon_company, font_paths):
    draw = ImageDraw.Draw(canvas)
    canvas_w, canvas_h = canvas.size

    bottom_bg_h = int(sku_config.bottom_gb_h * sku_config.dpi)
    # --- 1. 计算基础尺寸 ---
    h_left = int(sku_config.dpi * 8)  # 8 cm 高的黑色底框
    h_right = int(h_left * 0.5)  # 右侧矮块高度为左侧的50%

    margin_1cm = int(1 * sku_config.dpi)
    margin_2cm = int(2 * sku_config.dpi)
    margin_3cm = int(3 * sku_config.dpi)
    margin_4cm = int(4 * sku_config.dpi)
    margin_6cm = int(6 * sku_config.dpi)
    margin_8cm = int(8 * sku_config.dpi)
    margin_10cm = int(10 * sku_config.dpi)

    # SKU区域边距
    sku_margin = int(0.5 * sku_config.dpi)  # 0.5cm边距

    # --- 2. 动态计算SKU字号和黑框宽度 ---
    # 最大可用宽度（留出S弯10cm + 右侧矮块4cm）
    max_sku_block_width = canvas_w - margin_10cm - margin_4cm
    max_sku_h = margin_8cm  # 文字高度不超过8cm

    # 从160pt开始尝试，逐渐减小直到宽度合适
    min_sku_size_pt = 160
    current_sku_size_px = int(min_sku_size_pt * sku_config.ppi / 72)
    min_sku_size_px = int(max_sku_h * 0.15)  # 最小字号

    sku_font = None
    sku_w = 0
    while current_sku_size_px >= min_sku_size_px:
        test_font = ImageFont.truetype(font_paths['calibri_bold'], size=current_sku_size_px)
        bbox = draw.textbbox((0, 0), sku_config.sku_name, font=test_font)
        sw = bbox[2] - bbox[0]
        sh = bbox[3] - bbox[1]

        # 检查宽度和高度是否都满足
        if sw <= max_sku_block_width - 2 * sku_margin and sh <= max_sku_h:
            sku_font = test_font
            sku_w = sw
            sku_h = sh
            min_sku_size_pt = int(current_sku_size_px * 72 / sku_config.ppi)  # 记录实际使用的字号
            break
        current_sku_size_px -= 5

    # 如果都没找到，使用最小字号
    if sku_font is None:
        sku_font = ImageFont.truetype(font_paths['calibri_bold'], size=min_sku_size_px)
        bbox = draw.textbbox((0, 0), sku_config.sku_name, font=sku_font)
        sku_w = bbox[2] - bbox[0]
        sku_h = bbox[3] - bbox[1]
        min_sku_size_pt = int(min_sku_size_px * 72 / sku_config.ppi)

    # --- 3. 根据SKU实际宽度计算黑框宽度 ---
    # 黑框宽度 = 文字宽度 + 边距(0.5cm+0.5cm)
    sku_block_width = sku_w + 2 * sku_margin

    # 限制黑框宽度范围
    if sku_block_width > max_sku_block_width:
        sku_block_width = max_sku_block_width
    if sku_block_width < margin_6cm:  # 最小6cm
        sku_block_width = margin_6cm

    # 计算S弯位置
    x3 = sku_block_width  # 左侧高块右边界/S弯起点
    x4 = x3 + margin_10cm  # S弯终点/右侧矮块左边界

    # 确保不超出画布
    if x4 > canvas_w - margin_1cm:
        x4 = canvas_w - margin_1cm
        x3 = x4 - margin_10cm
        sku_block_width = x3

    print(f"[侧唛SKU调试-旋转] 画布宽度: {canvas_w}px ({canvas_w / sku_config.dpi:.1f}cm)")
    print(f"[侧唛SKU调试-旋转] SKU文字宽度: {sku_w / sku_config.dpi:.1f}cm, 字号: {min_sku_size_pt}pt")
    print(f"[侧唛SKU调试-旋转] 黑框宽度: {sku_block_width / sku_config.dpi:.1f}cm")

    # S弯的y坐标
    y3 = canvas_h - h_left
    y4 = canvas_h - h_right

    # --- 4. 绘制异形底框 (黑色) ---
    # 左侧高块
    draw.rectangle([0, canvas_h - h_left, x3, canvas_h], fill=(0, 0, 0))
    # 右侧矮块
    draw.rectangle([x4, canvas_h - h_right, canvas_w, canvas_h], fill=(0, 0, 0))

    # 绘制丝滑过渡区 (S弯)
    curve_points = []
    for i in range(21):
        t = i / 20
        curr_x = x3 + (x4 - x3) * t
        t_smooth = t * t * (3 - 2 * t)
        curr_y = y3 + (y4 - y3) * t_smooth
        curve_points.append((curr_x, curr_y))

    curve_fill_path = curve_points + [(x4, canvas_h), (x3, canvas_h)]
    draw.polygon(curve_fill_path, fill=(0, 0, 0))

    # --- 5. 绘制 SKU 文字 (180pt，在左侧高块中居中) ---
    sku_area_left = sku_margin
    sku_area_right = x3 +6* sku_margin
    sku_center_x = (sku_area_left + sku_area_right) // 2
    offset_y = int(0.3 * sku_config.dpi)
    sku_center_y = canvas_h - h_left // 2 + offset_y

    draw.text((sku_center_x, sku_center_y), sku_config.sku_name, font=sku_font,
              fill=(161, 142, 102), anchor="mm")
    print(f"[侧唛SKU调试-旋转] 最终SKU字号: {min_sku_size_pt}pt, 区域: {sku_area_left}-{sku_area_right}px")
    return x4

def fill_sidepanel_text(icon_side_text_box_resized, sku_config, fonts_paths):
    """
    Mcombo 两种样式专用
    用于给侧唛表格区域填充动态文字和条码 
    在侧唛的右侧表格区域内绘制动态文字和条码
    然后返回给调用者进行粘贴
    """
    # 此时 tw, th 仅代表右侧那个格子的宽高
    tw, th = icon_side_text_box_resized.size
    draw = ImageDraw.Draw(icon_side_text_box_resized)
    
    # 1. 准备字体 (保持比例科学)
    side_font_bold_path = fonts_paths['side_font_bold']
    side_font_label_path = fonts_paths['side_font_label']
    side_font_barcode_path = fonts_paths['side_font_barcode']
    
    # 比例字号：th 为 8cm 对应的像素
    font_size_label = int(th * 0.081)   # G.W./Box Size
    font_size_bold = int(th * 0.095)    # MADE IN CHINA
    font_size_barcode = int(th * 0.058) # 条码下方的数字
    
    side_font_label = ImageFont.truetype(side_font_label_path, size=font_size_label)
    side_font_bold = ImageFont.truetype(side_font_bold_path, size=font_size_bold)
    side_font_barcode_text = ImageFont.truetype(side_font_barcode_path, size=font_size_barcode)
    
    # --- 区域 1: 右上角文字区 (注意：X 轴起点要落在最右边那个格子里) ---
    # 根据目标图，右上角单元格起点大约在表格总宽的 65% 处
    text_x_start = tw * 0.651
    side_weight_text = f'G.W./N.W.: {sku_config.side_text["gw_value"]} / {sku_config.side_text["nw_value"]} lbs'
    side_dimention_text = f'BOX SIZE: {sku_config.l_in:.1f}\'\' x {sku_config.w_in:.1f}\'\' x {sku_config.h_in:.1f}\'\''
    draw.text((text_x_start, th * 0.044), side_weight_text, font=side_font_label, fill=(0,0,0))
    draw.text((text_x_start, th * 0.214), side_dimention_text, font=side_font_label, fill=(0,0,0))
    
    # --- 区域 2: 条形码区 (分为左右两个子区域) ---
    # 定义在这个局部表格内的中轴线
    left_zone_center = tw * 0.46   # 左半区中心
    right_zone_center = tw * 0.847  # 右半区中心
    
    barcode_y = th * 0.42          # 条码顶部起始，避开上方图标的横线
    barcode_text_y = th * 0.76     # 条码下方文字起始位置
    barcode_h_px = int(th * 0.35)  # 条码高度 35%
    
    # A. 左侧 SKU 条码
    # 宽度大约占局部表格的 46%，高度 35%
    sku_barcode_img = generate_barcode_image(sku_config.sku_name, width=int(tw * 0.46), height=barcode_h_px)

    print(f"[侧唛SKU调试-条码] 条码高度: {barcode_h_px}px ({barcode_h_px / sku_config.dpi:.1f}cm)")
    barcode_w_px = scale_by_height(sku_barcode_img, barcode_h_px).width
    print(f"[侧唛SKU调试-条码] 条码宽度: {barcode_w_px}px ({barcode_w_px / sku_config.dpi:.1f}cm)")
    
    sku_x = int(left_zone_center - sku_barcode_img.width / 2)
    icon_side_text_box_resized.paste(sku_barcode_img, (sku_x, int(barcode_y)))
    
    # SKU 文本文字居中
    sku_w = draw.textlength(sku_config.sku_name, font=side_font_barcode_text)
    draw.text((left_zone_center - sku_w/2, barcode_text_y), sku_config.sku_name, font=side_font_barcode_text, fill=(0,0,0))
    
    # B. 右侧 SN 条码
    sn_code = sku_config.side_text['sn_code']
    sn_barcode_img = generate_barcode_image(sn_code, width=int(tw * 0.28), height=barcode_h_px)
    sn_x = int(right_zone_center - sn_barcode_img.width / 2)
    icon_side_text_box_resized.paste(sn_barcode_img, (sn_x, int(barcode_y)))
    
    # SN 文本文字居中
    sn_w = draw.textlength(sn_code, font=side_font_barcode_text)
    draw.text((right_zone_center - sn_w/2, barcode_text_y), sn_code, font=side_font_barcode_text, fill=(0,0,0))
    
    # --- 区域 3: 底部 MADE IN CHINA (在当前局部表格内绝对居中) ---
    made_text = sku_config.side_text.get('origin_text', 'MADE IN CHINA')
    made_w = draw.textlength(made_text, font=side_font_bold)
    draw.text(( tw * 0.51 , th * 0.87 ), made_text, font=side_font_bold, fill=(0,0,0))
    
    return icon_side_text_box_resized

def fill_sidepanel_text_1(icon_side_text_box_resized, sku_config, fonts_paths):
    tw, th = icon_side_text_box_resized.size
    draw = ImageDraw.Draw(icon_side_text_box_resized)
    dpi = sku_config.dpi

    # 1. 准备字体
    side_font_label = ImageFont.truetype(fonts_paths['side_font_label'], size=int(th * 0.081))
    side_font_bold = ImageFont.truetype(fonts_paths['side_font_bold'], size=int(th * 0.095))
    side_font_barcode_text = ImageFont.truetype(fonts_paths['side_font_barcode'], size=int(th * 0.058))

    # --- 区域 1: 右上角文字区 ---
    text_x_start = tw * 0.55
    side_weight_text = f'G.W./N.W.: {sku_config.side_text["gw_value"]} / {sku_config.side_text["nw_value"]} lbs'
    side_dimention_text = f'BOX SIZE: {sku_config.l_in:.1f}\'\' x {sku_config.w_in:.1f}\'\' x {sku_config.h_in:.1f}\'\''
    draw.text((text_x_start, th * 0.044), side_weight_text, font=side_font_label, fill=(0, 0, 0))
    draw.text((text_x_start, th * 0.214), side_dimention_text, font=side_font_label, fill=(0, 0, 0))
    # --- 区域 2: 第二行条形码区 ---
    barcode_h_px = int(th * 0.35)
    barcode_y = th * 0.42
    barcode_text_y = th * 0.76

    # A. 生成两个条码图片
    # 【自适应变胖关键】：我们先获取一个原始比例的宽度，用来计算分水岭位置
    raw_sku_barcode = generate_barcode_image_1(sku_config.sku_name, height=barcode_h_px)
    sn_code = sku_config.side_text['sn_code']
    raw_sn_barcode = generate_barcode_image_1(sn_code, height=barcode_h_px)

    # B. 计算“动态分水岭”的位置 (保持你原来的比例逻辑)
    total_bc_width = raw_sku_barcode.width + raw_sn_barcode.width
    line_x = (tw * (raw_sku_barcode.width / total_bc_width)) if total_bc_width > 0 else tw / 2

    # 【手动画黑线】：保持你要求的 0.09 粗度
    draw.line([(line_x, th * 0.36), (line_x, th * 0.855)], fill=(0, 0, 0), width=int(0.09 * dpi))

    # --- C. 放置 SKU 条码并使其“自适应变胖” ---
    # 定义左侧格子的目标宽度（留出 5% 的边距防止贴线）
    sku_target_w = int(line_x * 0.9)
    # 强制拉伸条码到这个宽度，它就会变胖
    sku_barcode_img = raw_sku_barcode.resize((sku_target_w, barcode_h_px), Image.Resampling.LANCZOS)

    sku_x = (line_x - sku_barcode_img.width) // 2
    icon_side_text_box_resized.paste(sku_barcode_img, (int(sku_x), int(barcode_y)))

    sku_w = draw.textlength(sku_config.sku_name, font=side_font_barcode_text)
    draw.text((sku_x + (sku_barcode_img.width - sku_w) / 2, barcode_text_y), sku_config.sku_name,
              font=side_font_barcode_text, fill=(0, 0, 0))

    # --- D. 放置 SN 条码并使其“自适应变胖” ---
    # 定义右侧格子的目标宽度
    sn_zone_w = tw - line_x
    sn_target_w = int(sn_zone_w * 0.9)
    # 强制拉伸条码到这个宽度
    sn_barcode_img = raw_sn_barcode.resize((sn_target_w, barcode_h_px), Image.Resampling.LANCZOS)

    sn_x = line_x + (sn_zone_w - sn_barcode_img.width) // 2
    icon_side_text_box_resized.paste(sn_barcode_img, (int(sn_x), int(barcode_y)))

    sn_w = draw.textlength(sn_code, font=side_font_barcode_text)
    draw.text((sn_x + (sn_barcode_img.width - sn_w) / 2, barcode_text_y), sn_code, font=side_font_barcode_text,
              fill=(0, 0, 0))

    # --- 区域 3: 底部 MADE IN CHINA ---
    made_text = "MADE IN CHINA"
    made_w = draw.textlength(made_text, font=side_font_bold)
    draw.text(((tw - made_w) / 2, th * 0.885), made_text, font=side_font_bold, fill=(0, 0, 0))

    return icon_side_text_box_resized

def generate_barcode_image(code_str, width, height):
    """生成透明背景的条形码图片，并强制缩放到指定尺寸"""
    Code128 = barcode.get_barcode_class("code128")
    bar = Code128(code_str, writer=ImageWriter())
    # 渲染成 PIL Image (不显示文字，透明背景)
    options = {"write_text": False, "module_height": 15.0, "quiet_zone": 1.0}
    img = bar.render(writer_options=options)
    
    # 将白色背景转换为透明
    img = img.convert("RGBA")
    datas = img.getdata()
    new_data = []
    for item in datas:
        # 将白色（255, 255, 255）转换为透明
        if item[0] > 250 and item[1] > 250 and item[2] > 250:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    
    return img.resize((width, height), Image.LANCZOS)

def generate_barcode_image_1(code_str, width=None, height=100):
    """生成透明背景的条形码图片，并强制缩放到指定尺寸"""
    Code128 = barcode.get_barcode_class("code128")
    bar = Code128(code_str, writer=ImageWriter())
    # 渲染成 PIL Image
    options = {"write_text": False, "module_height": 15.0, "quiet_zone": 1.0}
    img = bar.render(writer_options=options)

    # 将白色背景转换为透明
    img = img.convert("RGBA")
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[0] > 250 and item[1] > 250 and item[2] > 250:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)

    # --- 修复报错的核心：如果没传 width，根据高度比例算一个出来 ---
    if width is None:
        orig_w, orig_h = img.size
        width = int(orig_w * (height / orig_h))

    # 现在这里不会因为 width 是 None 而报错了
    return img.resize((int(width), int(height)), Image.Resampling.LANCZOS)


def generate_barcode_with_text(code_str, width, height):
    """
    生成带文字的透明背景条形码，根据目标尺寸动态调整参数避免变形
    这个函数不推荐使用，自带的文本字体非常古早
    建议使用 generate_barcode_image 生成纯条码后手动绘制文字
    """
    import barcode
    from barcode.writer import ImageWriter
    from PIL import Image

    Code128 = barcode.get_barcode_class("code128")
    bar = Code128(code_str, writer=ImageWriter())
    
    # 根据目标尺寸动态计算参数
    # 字体大小约为高度的14%
    font_size = max(12, int(height * 0.14))
    # 条码高度大幅减小到35%（为文字留出充足空间）
    module_height = max(6.0, height * 0.35 / 10)  # module_height单位是mm
    # 文字和条码之间的距离大幅增加到15%
    text_distance = max(5.0, height * 0.15 / 10)
    
    options = {
        "write_text": True,           # 开启底部文字
        "font_size": font_size,       # 动态字体大小
        "text_distance": text_distance, # 动态文字距离（增大）
        "module_height": module_height, # 动态条码高度（减小）
        "quiet_zone": 2.0,            # 左右留白宽度
        "background": 'white',        # 显式指定背景白
        "foreground": 'black'         # 显式指定前景色黑
    }
    
    # 渲染原始图片
    img = bar.render(writer_options=options)
    
    # 转换为透明背景
    img = img.convert("RGBA")
    datas = img.getdata()
    new_data = []
    
    for item in datas:
        # 将白色背景转为透明
        if item[0] > 220 and item[1] > 220 and item[2] > 220:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    
    # 使用高质量缩放，保持长宽比
    return img.resize((width, height), Image.LANCZOS)


def get_max_font_size(text, font_path, target_width, max_height=None, min_size=10, max_size=1000):
    """
    动态寻找能让文字适应目标宽度的最大字号
    
    参数:
        text: 要绘制的文字
        font_path: 字体文件路径
        target_width: 目标宽度（像素）
        max_height: 最大高度限制（像素），可选
        min_size: 最小字号
        max_size: 最大字号
    
    返回:
        适合的字号大小
    """
    # 创建临时绘图对象用于测量
    temp_img = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(temp_img)
    
    # 二分查找最佳字号
    best_size = min_size
    low, high = min_size, max_size
    
    while low <= high:
        mid = (low + high) // 2
        font = ImageFont.truetype(font_path, mid)
        
        # 获取文字的边界框
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 检查宽度是否符合
        width_ok = text_width <= target_width
        # 检查高度是否符合（如果有高度限制）
        height_ok = max_height is None or text_height <= max_height
        
        if width_ok and height_ok:
            best_size = mid
            low = mid + 1  # 尝试更大的字号
        else:
            high = mid - 1  # 字号太大，减小
    
    return best_size
    


def draw_diagonal_stripes(canvas, stripe_height_cm, dpi, bottom_margin_cm=0, stripe_width_px=30, stripe_color=(0, 0, 0), bg_color=(255, 255, 255)):
    """
    在画布底部绘制黑白斜纹条块（通用函数）
    
    参数：
        canvas: PIL Image对象
        stripe_height_cm: 条纹区域的高度（厘米）
        dpi: 分辨率
        bottom_margin_cm: 底部留白高度（厘米），默认0
        stripe_width_px: 每条斜纹的宽度（像素），默认30
        stripe_color: 斜纹颜色，默认黑色
        bg_color: 背景颜色，默认白色
    
    返回：
        修改后的canvas
    """
    canvas_w, canvas_h = canvas.size
    draw = ImageDraw.Draw(canvas)
    
    # 计算条纹区域高度（像素）
    stripe_h_px = int(stripe_height_cm * dpi)
    bottom_margin_px = int(bottom_margin_cm * dpi)
    stripe_y_start = canvas_h - stripe_h_px - bottom_margin_px
    stripe_y_end = canvas_h - bottom_margin_px
    
    # 先绘制背景色
    draw.rectangle([0, stripe_y_start, canvas_w, stripe_y_end], fill=bg_color)
    
    # 绘制斜纹：从左到右，每个斜纹从左下到右上
    # 斜纹角度约45度
    stripe_offset = int(stripe_width_px * 1.5)  # 每条斜纹的间距（一黑一白）
    
    # 计算需要多少条斜纹（覆盖整个宽度+高度对角线）
    num_stripes = (canvas_w + stripe_h_px) // stripe_offset + 2
    
    for i in range(num_stripes):
        # 计算斜纹起始x坐标
        start_x = i * stripe_offset - stripe_h_px
        
        # 绘制斜纹：一个平行四边形
        # 左下、右下、右上、左上四个点
        points = [
            (start_x, stripe_y_end),                           # 左下
            (start_x + stripe_width_px, stripe_y_end),         # 右下
            (start_x + stripe_width_px + stripe_h_px, stripe_y_start),  # 右上
            (start_x + stripe_h_px, stripe_y_start)        # 左上
        ]
        draw.polygon(points, fill=stripe_color)
    
    return canvas

def make_it_pure_black(img):
    """强制将所有不透明且较暗的像素变为纯黑 (0,0,0)"""
    data = np.array(img.convert('RGBA'))
    # 找到 alpha > 0 且 RGB 总和较小的像素
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    black_mask = (r < 100) & (g < 100) & (b < 100) & (a > 0)
    data[black_mask, 0:3] = [0, 0, 0] # 设为 RGB 0,0,0
    return Image.fromarray(data)

def draw_dynamic_company_brand(sku_config, company_name, contact_info, font_paths, resources):
    dpi = sku_config.dpi
    h_target_px = int(1.6 * dpi)

    # 1. 准备字体
    font_left = ImageFont.truetype(font_paths['calibri_bold'], size=int(h_target_px * 0.65))
    font_right = ImageFont.truetype(font_paths['calibri_bold'], size=int(h_target_px * 0.75))

    # 2. 测量文字
    temp_draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    left_text_w = temp_draw.textbbox((0, 0), company_name, font=font_left)[2]
    right_text_w = temp_draw.textbbox((0, 0), contact_info, font=font_right)[2]

    # --- A. 处理左侧黑框 ---
    img_l = resources['icon_company_bg_left'].convert('RGBA')
    img_l = scale_by_height(img_l, h_target_px)
    w_l_orig, h_l = img_l.size
    # 设定左侧圆角区固定宽度（假设模版左侧圆角占高度的一半）
    fixed_left_corner = h_l // 1
    # 目标总宽 = 文字宽 + 左右留白 (各0.5cm)
    target_l_w = left_text_w + int(0.7 * dpi)

    left_final = Image.new('RGBA', (target_l_w, h_l), (0, 0, 0, 0))

    # 粘贴圆角 (用高质量)
    part_l_corner = img_l.crop((0, 0, fixed_left_corner, h_l))
    left_final.paste(part_l_corner, (0, 0), mask=part_l_corner)

    # 拉伸中间黑条 (【关键】使用 NEAREST 采样，严禁产生渐变)
    # 裁剪时往里收 5 像素，确保裁到的是 100% 的纯黑色
    part_l_mid = img_l.crop((fixed_left_corner + 5, 0, fixed_left_corner + 10, h_l)).resize(
        (target_l_w - fixed_left_corner, h_l), Image.Resampling.NEAREST)
    left_final.paste(part_l_mid, (fixed_left_corner, 0), mask=part_l_mid)

    # --- B. 处理右侧白框 ---
    # --- 3. 处理右侧白框 (确保矩形区足够放文字并居中) ---
    img_r = resources['icon_company_bg_right'].convert('RGBA')
    img_r = scale_by_height(img_r, h_target_px)
    w_r_orig, h_r = img_r.size

    # 保护区：依然只保护最右侧的斜角尖尖
    fixed_right_tip_w = int(w_r_orig * 0.27)

    # 【关键修改】矩形区的宽度 = 文字宽度 + 左右对等的留白
    # 这里 1.0 * dpi 表示文字左右各留约 0.5cm 的空白，确保它是视觉居中的
    rect_part_w = right_text_w + int(0.7 * dpi)

    # 右侧总宽 = 矩形区 + 尖头区
    target_r_w = rect_part_w + fixed_right_tip_w

    right_final = Image.new('RGBA', (target_r_w, h_r), (0, 0, 0, 0))

    # A. 先贴尖尖头到最右边
    part_r_tip = img_r.crop((w_r_orig - fixed_right_tip_w, 0, w_r_orig, h_r))
    right_final.paste(part_r_tip, (target_r_w - fixed_right_tip_w, 0), mask=part_r_tip)

    # B. 贴长方形区 (从 0 到 target_r_w - fixed_right_tip_w)
    # 取模版左侧纯色像素拉伸
    part_r_mid = img_r.crop((10, 0, 15, h_r)).resize(
        (rect_part_w, h_r), Image.Resampling.NEAREST)
    right_final.paste(part_r_mid, (0, 0), mask=part_r_mid)

    # --- 4. 合并 ---
    combined_img = Image.new('RGBA', (target_l_w + target_r_w, h_l), (0, 0, 0, 0))
    combined_img.paste(left_final, (0, 0), mask=left_final)
    combined_img.paste(right_final, (target_l_w - 1, 0), mask=right_final)

    # --- 5. 写字 (左右各自在自己的矩形区居中) ---
    draw = ImageDraw.Draw(combined_img)

    # 左侧：在左侧黑框(target_l_w)中心写字
    draw.text((target_l_w // 2, h_l // 2+4), company_name, font=font_left, fill=(161, 142, 102), anchor="mm")

    # 右侧：【关键】在右侧“矩形区”中心写字
    # 计算公式：左框总宽 + (矩形区宽度 // 2)
    # 这样就完全避开了尖头，且在长方形内部是完美居中的
    right_rect_center = target_l_w + (rect_part_w // 2)

    draw.text((right_rect_center, h_r // 2), contact_info, font=font_right, fill=(0, 0, 0), anchor="mm")

    return combined_img


# 自定义的文字处理组件
class LegalTextGroup(Element):
    def __init__(self, data_dict, reg_font, bold_font, width, height, dpi):
        super().__init__(width=width, height=height)
        self.data_dict = data_dict
        self.reg_font = reg_font
        self.bold_font = bold_font
        self.padding_left = 30
        self.padding_top = 20
        self.dpi = dpi

    def layout(self, x, y, max_width=0):
        self.x = int(x)
        self.y = int(y)
        return self.width, self.height

    def render(self, draw):
        font_path = getattr(self.reg_font, 'path', None)
        bold_path = getattr(self.bold_font, 'path', font_path)

        base_size = 28
        line_spacing_ratio = 1.3

        def get_all_visual_lines(size):
            f_reg = ImageFont.truetype(font_path, size) if font_path else self.reg_font
            f_bold = ImageFont.truetype(bold_path, size) if bold_path else self.bold_font
            l_h = int(size * line_spacing_ratio)
            all_lines = []

            # 可用宽度减少一些，防止换行太满
            available_w = self.width - self.padding_left - 35
            avg_w = f_reg.getlength("a")
            char_limit = max(1, int(available_w / avg_w))

            for label, value in self.data_dict.items():
                full_label = f"{label}: "
                # 预先计算标签宽度
                label_w = f_bold.getlength(full_label)

                # 处理内容换行
                full_text = full_label + str(value)
                wrapped = textwrap.wrap(full_text, width=char_limit)

                for i, line_text in enumerate(wrapped):
                    all_lines.append({
                        'text': line_text,
                        'is_label_row': (i == 0),
                        'label_text': full_label if i == 0 else "",
                        'label_w': label_w if i == 0 else 0,
                        'full_content': line_text
                    })
            return all_lines, l_h, f_reg, f_bold

        # 1. 自动缩放
        current_size = base_size
        visual_lines, final_l_h, final_reg, final_bold = get_all_visual_lines(current_size)
        while len(visual_lines) * final_l_h > (self.height - 20) and current_size > 12:
            current_size -= 2
            visual_lines, final_l_h, final_reg, final_bold = get_all_visual_lines(current_size)

        # 2. 计算居中偏移
        extra_down_offset = int(0.2 * self.dpi)  # 约等于向下移动 0.2cm
        total_content_h = len(visual_lines) * final_l_h
        curr_y = self.y + (self.height - total_content_h) // 2 + extra_down_offset
        curr_x = self.x + self.padding_left

        # 3. 渲染：分段绘制逻辑
        for line in visual_lines:
            target_pos = (int(curr_x), int(curr_y))

            if line['is_label_row']:
                # --- 关键修改：分两步画，不重叠 ---
                # A. 先画加粗标签
                draw.text(target_pos, line['label_text'], font=final_bold, fill=0)

                # B. 计算内容起始点 (标签宽 + 2像素微调间距)
                content_start_x = int(curr_x + line['label_w'])
                # 只取冒号后面的内容部分
                content_text = line['full_content'][len(line['label_text']):]

                # C. 画内容部分 (使用常规体)
                draw.text((content_start_x, int(curr_y)), content_text, font=final_reg, fill=0)
            else:
                # 非首行，直接用常规体画整行
                draw.text(target_pos, line['text'], font=final_reg, fill=0)

            curr_y += final_l_h


# 2. 重新设计的绘图函数
def draw_legal_label_component(canvas, x, y, sku_config, resources, fonts, legal_data):
    dpi = sku_config.dpi
    box_w, box_h = int(22.4 * dpi), int(14.0 * dpi)

    # 严格高度分配 (5.7 + 2.0 + 6.3 = 14cm)
    row1_h = int(5.7 * dpi)
    row2_h = int(2.0 * dpi)
    row3_h = int(6.3 * dpi)

    icon_gap_px = int(0.7 * dpi)  # 图标间距 1.3cm

    # 辅助函数：计算缩放图片并返回 Element
    def get_scaled_img_el(res_key, row_height_px, scale=0.85):
        img = resources[res_key].convert('RGBA')
        # 【核心逻辑】：如果是 GE 模式且使用的是单图 A
        # 我们将缩放比例减半，这样 A 的物理尺寸就和 A+B 里的 A 一样大
        if getattr(sku_config, 'GE', 0) == 1 and res_key == 'legal_icon_2_2':
            current_scale = scale / 2 - 0.15  # 0.425
        else:
            current_scale = scale  # 0.85
        target_h = int(row_height_px * current_scale)
        orig_w, orig_h = img.size
        target_w = int(orig_w * (target_h / orig_h))
        return ImageElement(image=img, width=target_w, height=target_h), target_w

    # --- 第一行逻辑 ---

    img1_elem, img1_w = get_scaled_img_el('legal_icon_2_2', row1_h)

    margin_right = int(0.8 * dpi)
    gap_between = int(1 * dpi)
    v_line_relative_x = box_w - margin_right - img1_w - (gap_between // 2)
    text_w = v_line_relative_x - (gap_between // 2)

    row1 = Row(
        children=[
            LegalTextGroup(legal_data, fonts['legal_reg'], fonts['legal_bold'], width=text_w, height=row1_h, dpi=dpi),
            # 【修复点】不能直接用 Element()，改用传入空数据的 LegalTextGroup 占位
            LegalTextGroup({}, fonts['legal_reg'], fonts['legal_bold'], width=box_w - text_w, height=row1_h, dpi=dpi)
        ],
        fixed_width=box_w, fixed_height=row1_h
    )

    # --- 第二行逻辑 (动态开关 + 自动居中) ---
    active_row2_children = []

    # 3-1 是基础图标，永远存在
    icon_3_1_el, _ = get_scaled_img_el('legal_icon_3_1', row2_h, scale=0.85)
    active_row2_children.append(icon_3_1_el)

    # 检查开关清单 (确保这些属性在 SKUConfig 中定义了)
    check_list = [
        (getattr(sku_config, 'legal_3_2', 0), 'legal_icon_3_2'),
        (getattr(sku_config, 'legal_3_3', 0), 'legal_icon_3_3'),
        (getattr(sku_config, 'legal_3_4', 0), 'legal_icon_3_4'),
        (getattr(sku_config, 'legal_3_5', 0), 'legal_icon_3_5'),
        (getattr(sku_config, 'legal_3_6', 0), 'legal_icon_3_6'),
    ]

    for is_on, res_key in check_list:
        if is_on == 1:
            # 先加 1.3cm 间距，再加图标
            # 【修复点】间距也改用空数据的 LegalTextGroup 占位
            active_row2_children.append(
                LegalTextGroup({}, fonts['legal_reg'], fonts['legal_bold'], width=icon_gap_px, height=row2_h, dpi=dpi)
            )
            icon_el, _ = get_scaled_img_el(res_key, row2_h, scale=0.4)
            active_row2_children.append(icon_el)

    # 计算 row2 总宽度用于手动居中补偿
    total_row2_w = sum(c.width for c in active_row2_children)
    row2_padding_val = (box_w - total_row2_w) // 2

    row2 = Row(
        children=[
            # 左侧占位实现居中
            LegalTextGroup({}, fonts['legal_reg'], fonts['legal_bold'], width=row2_padding_val, height=row2_h, dpi=dpi),
            *active_row2_children
        ],
        fixed_width=box_w, fixed_height=row2_h
    )

    # --- 第三行逻辑 (保持居中) ---
    img3_el, img3_w = get_scaled_img_el('legal_icon_4', row3_h, scale=0.85)
    row3_padding_val = (box_w - img3_w) // 2
    row3 = Row(
        children=[
            LegalTextGroup({}, fonts['legal_reg'], fonts['legal_bold'], width=row3_padding_val, height=row3_h, dpi=dpi),
            img3_el
        ],
        fixed_width=box_w, fixed_height=row3_h
    )

    # --- 组装与渲染 ---
    container = Column(children=[row1, row2, row3], fixed_width=box_w, fixed_height=box_h, spacing=0)
    container.layout(x, y)

    draw = ImageDraw.Draw(canvas)

    # 绘制外框和两条横线
    draw.rectangle([x, y, x + box_w, y + box_h], outline=0, width=4)
    draw.line([(x, y + row1_h), (x + box_w, y + row1_h)], fill=0, width=3)
    draw.line([(x, y + row1_h + row2_h), (x + box_w, y + row1_h + row2_h)], fill=0, width=3)

    # 绘制第一行黑色竖线
    final_v_line_x = x + v_line_relative_x
    draw.line([(final_v_line_x, y), (final_v_line_x, y + row1_h)], fill=0, width=3)

    # 绘制第一行右侧图标 (使用 paste)
    img1_x = x + box_w - margin_right - img1_w
    img1_y = y + (row1_h - img1_elem.height) // 2
    canvas.paste(img1_elem.image, (int(img1_x), int(img1_y)), img1_elem.image)

    # 渲染所有子组件 (包括文字和居中的图标组)
    container.render(draw)
