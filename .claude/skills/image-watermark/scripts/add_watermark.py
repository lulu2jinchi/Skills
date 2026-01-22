#!/usr/bin/env python3
"""
图片水印添加工具
支持文字水印和图片水印两种模式
"""

import argparse
import math
import os
import sys
from PIL import Image, ImageDraw, ImageFont


def contains_emoji(text):
    """
    检测文本中是否包含emoji字符
    
    参数:
        text: 要检测的文本
    
    返回:
        bool: 是否包含emoji
    """
    if not text:
        return False
    
    for char in text:
        code = ord(char)
        # 常见emoji Unicode范围
        if (
            (0x1F600 <= code <= 0x1F64F) or  # 表情符号
            (0x1F300 <= code <= 0x1F5FF) or  # 符号和图形
            (0x1F680 <= code <= 0x1F6FF) or  # 交通和地图
            (0x1F700 <= code <= 0x1F77F) or  # 字母符号
            (0x1F780 <= code <= 0x1F7FF) or  # 几何符号扩展
            (0x1F800 <= code <= 0x1F8FF) or  # 补充箭头
            (0x1F900 <= code <= 0x1F9FF) or  # 补充符号
            (0x1FA00 <= code <= 0x1FA6F) or  # 棋类符号
            (0x1FA70 <= code <= 0x1FAFF) or  # 符号和图形扩展-A
            (0x2600 <= code <= 0x26FF) or   # 杂项符号（包括⭐⚡等）
            (0x2700 <= code <= 0x27BF) or   # 装饰符号
            (0x2B50 <= code <= 0x2B55) or   # 星号和心形等
            (0xFE0F == code)                # 变体选择器
        ):
            return True
    return False


def get_available_font(check_emoji=False):
    """
    获取系统可用的字体
    
    参数:
        check_emoji: 是否优先查找emoji字体
    
    返回:
        字体文件路径
    """
    # 如果需要emoji字体，优先查找
    if check_emoji:
        emoji_font_paths = [
            "/System/Library/Fonts/Apple Color Emoji.ttc",  # macOS 彩色emoji（优先）
            "C:/Windows/Fonts/seguiemj.ttf",  # Windows Segoe UI Emoji（彩色）
            "/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf",  # Linux Symbola（单色）
        ]
        for emoji_font in emoji_font_paths:
            if os.path.exists(emoji_font):
                return emoji_font
    
    # 常见中文字体列表
    font_names = [
        "wqy-microhei.ttc",  # 文泉驿微米黑
        "wqy-zenhei.ttc",   # 文泉驿正黑
        "simhei.ttf",       # 黑体
        "simsun.ttc",       # 宋体
        "simkai.ttf",       # 楷体
        "simfang.ttf",      # 仿宋
        "msyh.ttc",         # 微软雅黑
        "arial.ttf",        # Arial
        "arialuni.ttf",     # Arial Unicode
    ]
    
    # Windows 系统字体路径
    windows_font_path = "C:/Windows/Fonts/"
    
    # Linux 系统字体路径
    linux_font_paths = [
        "/usr/share/fonts/truetype/wqy/",  # 文泉驿中文字体
        "/usr/share/fonts/truetype/dejavu/",
        "/usr/share/fonts/truetype/liberation/",
        "/usr/share/fonts/truetype/droid/",
        "/System/Library/Fonts/PingFang.ttc",  # macOS
    ]
    
    for font_name in font_names:
        if os.path.exists(os.path.join(windows_font_path, font_name)):
            return os.path.join(windows_font_path, font_name)
    
    for font_path in linux_font_paths:
        if os.path.exists(font_path):
            files = os.listdir(font_path)
            for f in files:
                if f.endswith('.ttf') or f.endswith('.ttc'):
                    return os.path.join(font_path, f)
    
    return None


def calculate_position(img_size, wm_size, position, margin=0):
    """
    计算水印位置
    
    参数:
        img_size: 原图尺寸 (width, height)
        wm_size: 水印尺寸 (width, height)
        position: 位置名称 (center/top-left/top-right/等)
        margin: 边距
    
    返回:
        (x, y) 水印左上角坐标
    """
    img_w, img_h = img_size
    wm_w, wm_h = wm_size
    
    positions = {
        'center': (img_w // 2 - wm_w // 2, img_h // 2 - wm_h // 2),
        'top-left': (margin, margin),
        'top-center': (img_w // 2 - wm_w // 2, margin),
        'top-right': (img_w - wm_w - margin, margin),
        'middle-left': (margin, img_h // 2 - wm_h // 2),
        'middle-right': (img_w - wm_w - margin, img_h // 2 - wm_h // 2),
        'bottom-left': (margin, img_h - wm_h - margin),
        'bottom-center': (img_w // 2 - wm_w // 2, img_h - wm_h - margin),
        'bottom-right': (img_w - wm_w - margin, img_h - wm_h - margin),
    }
    
    return positions.get(position, positions['center'])


def create_tiled_pattern(watermark_img, target_size, angle=30, spacing=2.0):
    """
    创建平铺图案
    
    参数:
        watermark_img: 单个水印图片
        target_size: 目标尺寸 (width, height)
        angle: 旋转角度（度）
        spacing: 间距倍数
    
    返回:
        平铺后的图层
    """
    wm_w, wm_h = watermark_img.size
    
    # 不旋转，直接使用原始水印
    rotated_wm = watermark_img
    rot_w, rot_h = wm_w, wm_h
    
    # 调试：检查原始水印的alpha
    alpha_nonzero = sum(1 for p in rotated_wm.getdata() if p[3] > 0)
    print(f"[DEBUG] 原始水印alpha>0的像素: {alpha_nonzero}/{rotated_wm.size[0]*rotated_wm.size[1]}")
    
    print(f"[DEBUG] 旋转后尺寸: {rotated_wm.size}")
    rot_w, rot_h = rotated_wm.size
    
    # 计算平铺间距
    spacing_x = int(rot_w * spacing)
    spacing_y = int(rot_h * spacing)
    
    # 计算需要平铺的数量
    # 添加额外的边距确保覆盖
    cols = math.ceil(target_size[0] / spacing_x) + 4
    rows = math.ceil(target_size[1] / spacing_y) + 4
    
    # 创建足够大的画布
    canvas_w = cols * spacing_x
    canvas_h = rows * spacing_y
    
    tiled_layer = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    
    # 平铺水印
    # 调试：记录平铺次数
    tile_count = 0
    for i in range(cols):
        for j in range(rows):
            # 交错排列（偶数行偏移一半）
            offset_x = (spacing_x // 2) if j % 2 == 1 else 0
            x = i * spacing_x + offset_x
            y = j * spacing_y
            tiled_layer.alpha_composite(rotated_wm, (x, y))
            tile_count += 1
    
    # 调试：输出平铺次数
    print(f"[DEBUG] 平铺了{tile_count}次, cols={cols}, rows={rows}, spacing=({spacing_x},{spacing_y})")
    
    # 计算裁剪区域（从中心裁剪到目标尺寸，确保覆盖完整）
    # 移除边缘多余的水印，保留中心区域
    crop_x = (canvas_w - target_size[0]) // 2
    crop_y = (canvas_h - target_size[1]) // 2
    cropped = tiled_layer.crop((crop_x, crop_y, crop_x + target_size[0], crop_y + target_size[1]))
    
    return cropped


def add_text_watermark(input_path, output_path, text, position='bottom-right',
                      opacity=0.5, font_size=48, margin=20, color=(255, 255, 255),
                      tile=False, tile_angle=30, tile_spacing=2.0, tile_opacity=0.15,
                      text_angle=0):
    """
    添加文字水印
    
    参数:
        input_path: 输入图片路径
        output_path: 输出图片路径
        text: 水印文字
        position: 水印位置
        opacity: 透明度 (0-1)
        font_size: 字体大小
        margin: 边距
        color: 颜色 (R, G, B)
        tile: 是否平铺
        tile_angle: 平铺角度（度）
        tile_spacing: 平铺间距倍数
        tile_opacity: 平铺透明度 (0-1)
        text_angle: 文字倾斜角度（度），默认0度不倾斜
    """
    try:
        # 打开原图
        img = Image.open(input_path).convert('RGBA')
        
        # 检测是否包含emoji，选择合适的字体
        has_emoji = contains_emoji(text)
        font_path = get_available_font(check_emoji=has_emoji)
        
        # 调试：输出字体信息
        print(f"[DEBUG] text={text}, has_emoji={has_emoji}, font={font_path}")
        
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            print(f"[WARNING] 无法加载字体，使用默认字体")
            font = ImageFont.load_default()
        
        # 计算文字尺寸
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), text, font=font)
        
        # 增加padding确保文字完整显示
        text_w = bbox[2] - bbox[0] + 20  # 左右各10像素padding
        text_h = bbox[3] - bbox[1] + 20  # 上下各10像素padding
        
        # 平铺模式
        if tile:
            # 创建单个文字水印
            wm_opacity = tile_opacity
            
            # 计算文字在画布中的位置
            text_x = 10
            text_y = 10
            
            # 在白色背景上绘制黑色文字
            text_layer_temp = Image.new('RGB', (text_w, text_h), (255, 255, 255))
            text_draw_temp = ImageDraw.Draw(text_layer_temp)
            text_draw_temp.text((text_x, text_y), text, font=font, fill=(0, 0, 0))
            
            # 转换为RGBA
            text_layer_single = text_layer_temp.convert('RGBA')
            
            # 把黑色变成指定颜色并应用透明度
            # 方法：使用矩阵变换
            r, g, b, a = text_layer_single.split()
            
            # 调试：检查颜色参数
            print(f"[DEBUG] color参数: {color}, wm_opacity: {wm_opacity}")
            
            # 如果像素是黑色(R<128)，设为目标颜色
            r_layer = r.point(lambda x: color[0] if x < 128 else 255)
            g_layer = g.point(lambda x: color[1] if x < 128 else 255)
            b_layer = b.point(lambda x: color[2] if x < 128 else 255)
            a_layer = r.point(lambda x: int(255 * wm_opacity) if x < 128 else 0)
            
            text_layer_single = Image.merge('RGBA', (r_layer, g_layer, b_layer, a_layer))
            
            # 文字倾斜（如果指定了角度）
            if text_angle != 0:
                # 分离alpha通道
                r, g, b, a = text_layer_single.split()
                
                # 旋转每个通道，使用NEAREST避免插值产生半透明
                rotated_r = r.rotate(text_angle, expand=True, resample=Image.NEAREST)
                rotated_g = g.rotate(text_angle, expand=True, resample=Image.NEAREST)
                rotated_b = b.rotate(text_angle, expand=True, resample=Image.NEAREST)
                rotated_a = a.rotate(text_angle, expand=True, resample=Image.NEAREST)
                
                # 合并旋转后的通道
                text_layer_single = Image.merge('RGBA', (rotated_r, rotated_g, rotated_b, rotated_a))
                
                print(f"[DEBUG] 文字已旋转 {text_angle} 度")
            
            # 调试：保存单个水印
            text_layer_single.save('/tmp/debug_single_watermark.png')
            
            # 调试：检查原始水印
            alpha_orig = sum(1 for p in text_layer_single.getdata() if p[3] > 0)
            print(f"[DEBUG] 原始水印alpha>0的像素: {alpha_orig}/{text_layer_single.size[0]*text_layer_single.size[1]}")
            
            # 创建平铺图案
            tiled_layer = create_tiled_pattern(text_layer_single, img.size, tile_angle, tile_spacing)
            
            # 合成平铺水印
            result = Image.alpha_composite(img, tiled_layer)
            result = result.convert('RGB')
            result.save(output_path, quality=95, optimize=True)
            print(f"平铺水印添加成功，输出至 {output_path}")
            return True, f"平铺水印添加成功，输出至 {output_path}"
        
        # 单水印模式
        if not tile:
            # 创建单个文字水印
            text_temp = Image.new('RGB', (text_w, text_h), (255, 255, 255))
            text_draw_temp = ImageDraw.Draw(text_temp)
            text_draw_temp.text((10, 10), text, font=font, fill=(0, 0, 0))
            
            # 转换为RGBA并设置颜色
            text_layer_single = text_temp.convert('RGBA')
            r, g, b, a = text_layer_single.split()
            r_layer = r.point(lambda x: color[0] if x < 128 else 255)
            g_layer = g.point(lambda x: color[1] if x < 128 else 255)
            b_layer = b.point(lambda x: color[2] if x < 128 else 255)
            a_layer = r.point(lambda x: int(255 * opacity) if x < 128 else 0)
            text_layer_single = Image.merge('RGBA', (r_layer, g_layer, b_layer, a_layer))
            
            # 文字倾斜（如果指定了角度）
            if text_angle != 0:
                r, g, b, a = text_layer_single.split()
                rotated_r = r.rotate(text_angle, expand=True, resample=Image.NEAREST)
                rotated_g = g.rotate(text_angle, expand=True, resample=Image.NEAREST)
                rotated_b = b.rotate(text_angle, expand=True, resample=Image.NEAREST)
                rotated_a = a.rotate(text_angle, expand=True, resample=Image.NEAREST)
                text_layer_single = Image.merge('RGBA', (rotated_r, rotated_g, rotated_b, rotated_a))
                print(f"[DEBUG] 文字已旋转 {text_angle} 度")
            
            # 计算位置（考虑旋转后的尺寸）
            wm_w, wm_h = text_layer_single.size
            x, y = calculate_position(img.size, (wm_w, wm_h), position, margin)
            
            # 创建目标位置的透明图层
            text_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
            
            # 将旋转后的水印粘贴到目标位置
            text_layer.paste(text_layer_single, (x, y))
            
            # 合成
            result = Image.alpha_composite(img, text_layer)
            
            # 保存
            result = result.convert('RGB')
            result.save(output_path, quality=95, optimize=True)
        
        return True, f"文字水印添加成功，输出至 {output_path}"
        
    except FileNotFoundError:
        return False, f"错误: 文件不存在 - {input_path}"
    except Exception as e:
        return False, f"错误: {str(e)}"


def add_image_watermark(input_path, output_path, watermark_path, position='bottom-right',
                       opacity=0.7, scale=0.15, margin=20,
                       tile=False, tile_angle=30, tile_spacing=2.0, tile_opacity=0.15,
                       wm_angle=0):
    """
    添加图片水印
    
    参数:
        input_path: 输入图片路径
        output_path: 输出图片路径
        watermark_path: 水印图片路径
        position: 水印位置
        opacity: 透明度 (0-1)
        scale: 水印缩放比例 (相对于原图宽度)
        margin: 边距
        tile: 是否平铺
        tile_angle: 平铺角度（度）
        tile_spacing: 平铺间距倍数
        tile_opacity: 平铺透明度 (0-1)
        wm_angle: 水印旋转角度（度），默认0度不旋转，支持负数表示逆时针旋转
    """
    try:
        # 打开原图
        img = Image.open(input_path).convert('RGBA')
        
        # 打开水印
        watermark = Image.open(watermark_path).convert('RGBA')
        
        # 缩放水印
        wm_width = int(img.width * scale)
        wm_height = int(watermark.height * (wm_width / watermark.width))
        watermark = watermark.resize((wm_width, wm_height), Image.Resampling.LANCZOS)
        
        # 水印旋转（如果指定了角度）
        if wm_angle != 0:
            # 分离alpha通道
            r, g, b, a = watermark.split()
            
            # 旋转每个通道，使用NEAREST避免插值产生半透明
            rotated_r = r.rotate(wm_angle, expand=True, resample=Image.NEAREST)
            rotated_g = g.rotate(wm_angle, expand=True, resample=Image.NEAREST)
            rotated_b = b.rotate(wm_angle, expand=True, resample=Image.NEAREST)
            rotated_a = a.rotate(wm_angle, expand=True, resample=Image.NEAREST)
            
            # 合并旋转后的通道
            watermark = Image.merge('RGBA', (rotated_r, rotated_g, rotated_b, rotated_a))
            print(f"[DEBUG] 水印已旋转 {wm_angle} 度")
        
        # 平铺模式
        if tile:
            # 调整透明度
            watermark_alpha = watermark.split()[3]
            watermark_alpha = watermark_alpha.point(lambda p: int(p * tile_opacity))
            watermark.putalpha(watermark_alpha)
            
            # 创建平铺图案
            tiled_layer = create_tiled_pattern(watermark, img.size, tile_angle, tile_spacing)
            
            # 合成
            result = Image.alpha_composite(img, tiled_layer)
        else:
            # 单水印模式
            # 调整透明度
            watermark_alpha = watermark.split()[3]
            watermark_alpha = watermark_alpha.point(lambda p: int(p * opacity))
            watermark.putalpha(watermark_alpha)
            
            # 计算位置
            x, y = calculate_position(img.size, watermark.size, position, margin)
            
            # 创建空白图层
            wm_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
            wm_layer.paste(watermark, (x, y), watermark)
            
            # 合成
            result = Image.alpha_composite(img, wm_layer)
        
        # 保存
        result = result.convert('RGB')
        result.save(output_path, quality=95, optimize=True)
        
        return True, f"图片水印添加成功，输出至 {output_path}"
        
    except FileNotFoundError as e:
        return False, f"错误: 文件不存在 - {str(e)}"
    except Exception as e:
        return False, f"错误: {str(e)}"


def extract_transparent_background(input_path, output_path, tolerance=30):
    """
    提取图片背景为透明
    
    参数:
        input_path: 输入图片路径
        output_path: 输出PNG图片路径（透明背景）
        tolerance: 颜色容差（0-255），默认30，用于判断相似颜色
    
    返回:
        (bool, str): (是否成功, 消息)
    """
    try:
        # 打开图片
        img = Image.open(input_path)
        
        # 转换为RGBA模式
        img = img.convert('RGBA')
        
        # 获取图片数据
        data = img.getdata()
        
        # 假设左上角的像素为背景色
        bg_color = data[0][:3]
        
        print(f"[DEBUG] 背景色: {bg_color}, 容差: {tolerance}")
        
        # 转换数据，将背景色像素设为透明
        new_data = []
        bg_r, bg_g, bg_b = bg_color
        
        for pixel in data:
            r, g, b, a = pixel
            # 判断是否为背景色（考虑容差）
            if (abs(r - bg_r) <= tolerance and 
                abs(g - bg_g) <= tolerance and 
                abs(b - bg_b) <= tolerance):
                # 设置为透明
                new_data.append((r, g, b, 0))
            else:
                # 保持原样
                new_data.append((r, g, b, a))
        
        # 更新图片数据
        img.putdata(new_data)
        
        # 保存为PNG格式
        img.save(output_path, 'PNG')
        
        return True, f"透明背景提取成功，输出至 {output_path}"
        
    except FileNotFoundError as e:
        return False, f"错误: 文件不存在 - {str(e)}"
    except Exception as e:
        return False, f"错误: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description='给图片添加水印')
    parser.add_argument('--input', required=True, help='输入图片路径')
    parser.add_argument('--output', required=True, help='输出图片路径')
    parser.add_argument('--mode', required=True, choices=['text', 'image', 'extract'], 
                        help='模式: text(文字水印), image(图片水印), extract(提取透明背景)')
    
    # 提取透明背景参数
    parser.add_argument('--tolerance', type=int, default=30,
                        help='颜色容差（0-255），默认30，用于判断相似颜色，值越大容差越大')
    
    # 文字水印参数
    parser.add_argument('--text', help='水印文字 (text模式必填)')
    parser.add_argument('--font-size', type=int, default=48, help='字体大小')
    parser.add_argument('--color', type=str, default='255,255,255', 
                        help='文字颜色 (R,G,B)，默认白色')
    
    # 图片水印参数
    parser.add_argument('--watermark', help='水印图片路径 (image模式必填)')
    parser.add_argument('--scale', type=float, default=0.15, 
                        help='水印缩放比例 (相对于原图宽度)')
    
    # 通用参数
    parser.add_argument('--position', default='bottom-right',
                        choices=['center', 'top-left', 'top-center', 'top-right',
                                'middle-left', 'middle-right',
                                'bottom-left', 'bottom-center', 'bottom-right'],
                        help='水印位置 (默认: bottom-right)')
    parser.add_argument('--opacity', type=float, default=0.5,
                        help='透明度 0-1 (默认: 0.5)')
    parser.add_argument('--margin', type=int, default=20,
                        help='边距 (默认: 20)')
    
    # 平铺参数
    parser.add_argument('--tile', action='store_true',
                        help='启用平铺模式')
    parser.add_argument('--tile-angle', type=float, default=30,
                        help='平铺角度（度），默认30度')
    parser.add_argument('--tile-spacing', type=float, default=2.0,
                        help='平铺间距倍数，默认2.0')
    parser.add_argument('--tile-opacity', type=float, default=0.15,
                        help='平铺透明度 (0-1)，默认0.15')
    
    # 文字倾斜参数
    parser.add_argument('--text-angle', type=float, default=0,
                        help='文字倾斜角度（度），默认0度不倾斜，支持负数表示逆时针旋转')
    
    # 图片水印旋转参数
    parser.add_argument('--wm-angle', type=float, default=0,
                        help='图片水印旋转角度（度），默认0度不旋转，支持负数表示逆时针旋转')
    
    args = parser.parse_args()
    
    # 验证参数
    if args.mode == 'text' and not args.text:
        print("错误: text模式需要指定 --text 参数")
        sys.exit(1)
    
    if args.mode == 'image' and not args.watermark:
        print("错误: image模式需要指定 --watermark 参数")
        sys.exit(1)
    
    # 解析颜色（仅text/image模式需要）
    color = (255, 255, 255)
    if args.mode in ['text', 'image']:
        try:
            color = tuple(map(int, args.color.split(',')))
            if len(color) != 3:
                raise ValueError
        except:
            color = (255, 255, 255)
    
    # 执行相应操作
    if args.mode == 'extract':
        success, msg = extract_transparent_background(args.input, args.output, args.tolerance)
    elif args.mode == 'text':
        success, msg = add_text_watermark(
            args.input, args.output, args.text, 
            args.position, args.opacity, args.font_size, args.margin, color,
            args.tile, args.tile_angle, args.tile_spacing, args.tile_opacity,
            args.text_angle
        )
    else:  # image mode
        success, msg = add_image_watermark(
            args.input, args.output, args.watermark,
            args.position, args.opacity, args.scale, args.margin,
            args.tile, args.tile_angle, args.tile_spacing, args.tile_opacity,
            args.wm_angle
        )
    
    print(msg)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
