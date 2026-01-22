#!/usr/bin/env python3
"""
测试图片拼接功能
注意：此脚本需要实际的图片文件才能运行完整测试
"""

import os
import sys
import tempfile
import numpy as np
from PIL import Image

# 添加脚本路径
script_dir = os.path.join(os.path.dirname(__file__), '..', 'scripts')
sys.path.insert(0, script_dir)

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("警告: OpenCV 未安装，跳过完整测试")

try:
    from stitch_images import (
        load_images_from_dir,
        find_overlap,
        find_best_stitch_point,
        blend_overlap,
        detect_navbar,
        stitch_images
    )
    MODULES_LOADED = True
except ImportError as e:
    MODULES_LOADED = False
    print(f"警告: 无法导入模块: {e}")


def create_test_images(num_images=3, width=400, height=600):
    """
    创建测试图片
    
    参数:
        num_images: 图片数量
        width: 图片宽度
        height: 图片高度
    
    返回:
        图片列表 (OpenCV格式)
    """
    images = []
    
    for i in range(num_images):
        # 创建渐变背景
        img = np.zeros((height, width, 3), dtype=np.uint8)
        
        # 垂直渐变（不同图片颜色不同）
        for y in range(height):
            color = int(255 * (y + i * 100) / (height + num_images * 100))
            img[y, :] = [color % 256, (color + 50) % 256, (color + 100) % 256]
        
        # 添加文本标记
        text = f"Image {i + 1}"
        cv2.putText(img, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 添加一些随机噪声
        noise = np.random.randint(0, 50, (height, width, 3), dtype=np.uint8)
        img = cv2.add(img, noise)
        
        images.append(img)
    
    return images


def test_basic_functionality():
    """测试基本功能"""
    print("\n=== 测试基本功能 ===")
    
    if not MODULES_LOADED:
        print("跳过: 模块未正确加载")
        return False
    
    # 创建测试图片
    print("创建测试图片...")
    images = create_test_images(num_images=3, width=400, height=600)
    print(f"创建了 {len(images)} 张测试图片")
    
    # 测试导航栏检测
    print("\n测试导航栏检测...")
    img_with_navbar = images[0].copy()
    
    # 模拟状态栏（顶部蓝色区域）
    img_with_navbar[:44, :] = [0, 122, 255]
    
    # 模拟底部导航栏
    img_with_navbar[-34:, :] = [0, 122, 255]
    
    top_nav, bottom_nav = detect_navbar(img_with_navbar, 44, 34)
    print(f"检测到导航栏: 顶部={top_nav}px, 底部={bottom_nav}px")
    
    # 测试重叠检测
    print("\n测试重叠检测...")
    img1 = images[0]
    img2 = images[1]
    
    # 创建重叠区域（将img2的顶部50px替换为img1的底部50px）
    img2[:50, :] = img1[-50:, :]
    
    overlap, confidence = find_overlap(img1, img2, direction='vertical', threshold=0.7)
    print(f"检测到重叠: {overlap}px, 置信度: {confidence:.2f}")
    
    if overlap > 0:
        print("✓ 重叠检测成功")
    else:
        print("✗ 重叠检测失败")
        return False
    
    # 测试拼接
    print("\n测试图片拼接...")
    try:
        result = stitch_images(
            images=[img1, img2],
            direction='vertical',
            auto_detect=False
        )
        print(f"拼接成功，结果尺寸: {result.shape}")
        print("✓ 基本拼接成功")
    except Exception as e:
        print(f"✗ 拼接失败: {e}")
        return False
    
    return True


def test_file_operations():
    """测试文件操作"""
    print("\n=== 测试文件操作 ===")
    
    if not MODULES_LOADED:
        print("跳过: 模块未正确加载")
        return False
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"使用临时目录: {tmpdir}")
        
        # 创建测试图片并保存
        print("创建并保存测试图片...")
        images = create_test_images(num_images=3, width=400, height=600)
        
        for i, img in enumerate(images):
            filepath = os.path.join(tmpdir, f"image_{i:02d}.png")
            cv2.imwrite(filepath, img)
            print(f"  保存: {filepath}")
        
        # 测试从目录加载图片
        print("\n测试从目录加载图片...")
        try:
            loaded_images = load_images_from_dir(tmpdir)
            print(f"成功加载 {len(loaded_images)} 张图片")
            print("✓ 文件加载成功")
        except Exception as e:
            print(f"✗ 文件加载失败: {e}")
            return False
        
        # 测试拼接并保存
        print("\n测试拼接并保存...")
        try:
            result = stitch_images(
                images=loaded_images,
                direction='vertical',
                auto_detect=False
            )
            
            output_path = os.path.join(tmpdir, "stitched.png")
            cv2.imwrite(output_path, result)
            print(f"拼接结果已保存至: {output_path}")
            
            # 验证输出文件
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"输出文件大小: {file_size} 字节")
                print("✓ 文件保存成功")
            else:
                print("✗ 输出文件不存在")
                return False
                
        except Exception as e:
            print(f"✗ 拼接失败: {e}")
            return False
    
    return True


def main():
    """运行所有测试"""
    print("=" * 50)
    print("图片拼接 Skill 测试")
    print("=" * 50)
    
    # 检查依赖
    print("\n检查依赖...")
    print(f"OpenCV 可用: {CV2_AVAILABLE}")
    print(f"模块已加载: {MODULES_LOADED}")
    
    if not CV2_AVAILABLE or not MODULES_LOADED:
        print("\n请安装所需依赖:")
        print("  pip install Pillow>=10.0.0 opencv-python>=4.8.0 numpy>=1.24.0")
        return
    
    # 运行测试
    results = []
    
    try:
        results.append(("基本功能", test_basic_functionality()))
    except Exception as e:
        print(f"测试异常: {e}")
        results.append(("基本功能", False))
    
    try:
        results.append(("文件操作", test_file_operations()))
    except Exception as e:
        print(f"测试异常: {e}")
        results.append(("文件操作", False))
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    
    for test_name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n所有测试通过！")
    else:
        print("\n部分测试失败，请检查错误信息")
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
