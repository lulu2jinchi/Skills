#!/usr/bin/env python3
"""
智能图片拼接工具
支持自动检测重复内容、删除导航栏、智能拼接
"""

import argparse
import cv2
import numpy as np
from PIL import Image
import os
import sys
from typing import List, Tuple, Optional


def load_images_from_dir(input_dir: str) -> List[np.ndarray]:
    """
    从目录加载图片，按文件名排序
    
    参数:
        input_dir: 输入目录路径
    
    返回:
        图片列表（OpenCV格式，BGR）
    """
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"目录不存在: {input_dir}")
    
    # 获取所有图片文件
    image_files = []
    for ext in ['*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG', '*.JPEG']:
        image_files.extend([f for f in os.listdir(input_dir) if f.endswith(ext[2:])])
    
    if not image_files:
        raise FileNotFoundError(f"目录中没有找到图片: {input_dir}")
    
    # 按文件名排序
    image_files.sort()
    
    # 加载图片
    images = []
    for filename in image_files:
        filepath = os.path.join(input_dir, filename)
        img = cv2.imread(filepath)
        if img is None:
            print(f"警告: 无法加载图片 {filepath}")
            continue
        images.append(img)
    
    print(f"成功加载 {len(images)} 张图片")
    return images


def find_overlap(img1: np.ndarray, img2: np.ndarray, 
                 direction: str = 'vertical',
                 threshold: float = 0.8,
                 max_overlap_ratio: float = 0.3) -> Tuple[int, float]:
    """
    寻找两张图片之间的重叠区域
    
    参数:
        img1: 第一张图片（上/左）
        img2: 第二张图片（下/右）
        direction: 拼接方向 'vertical' 或 'horizontal'
        threshold: 相似度阈值
        max_overlap_ratio: 最大重叠比例
    
    返回:
        (overlap_pixels, confidence) 重叠像素数和置信度
    """
    if direction == 'vertical':
        # 垂直拼接：在img1底部和img2顶部寻找重叠
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        
        max_overlap = int(min(h1, h2) * max_overlap_ratio)
        min_overlap = 50
        
        # 从img1底部提取不同高度的模板
        best_overlap = 0
        best_confidence = 0.0
        
        for overlap in range(min_overlap, max_overlap + 1, 10):
            # 从img1底部提取重叠区域
            template = img1[h1 - overlap:h1, :]
            # 在img2顶部搜索匹配
            search_region = img2[:overlap, :]
            
            # 使用多尺度模板匹配
            result = cv2.matchTemplate(search_region, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_confidence and max_val >= threshold:
                best_confidence = max_val
                best_overlap = overlap
        
        return best_overlap, best_confidence
    
    else:  # horizontal
        # 水平拼接：在img1右侧和img2左侧寻找重叠
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        
        max_overlap = int(min(w1, w2) * max_overlap_ratio)
        min_overlap = 50
        
        best_overlap = 0
        best_confidence = 0.0
        
        for overlap in range(min_overlap, max_overlap + 1, 10):
            # 从img1右侧提取重叠区域
            template = img1[:, w1 - overlap:w1]
            # 在img2左侧搜索匹配
            search_region = img2[:, :overlap]
            
            result = cv2.matchTemplate(search_region, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_confidence and max_val >= threshold:
                best_confidence = max_val
                best_overlap = overlap
        
        return best_overlap, best_confidence


def detect_navbar(img: np.ndarray, 
                  top_height: int = 44,
                  bottom_height: int = 34) -> Tuple[int, int]:
    """
    检测图片的顶部和底部导航栏高度
    
    参数:
        img: 输入图片
        top_height: 预估顶部导航栏高度
        bottom_height: 预估底部导航栏高度
    
    返回:
        (top_nav, bottom_nav) 实际检测到的导航栏高度
    """
    h, w = img.shape[:2]
    
    # 检测顶部导航栏
    # 方法：检测颜色方差，导航栏通常颜色单一
    top_region = img[:top_height, :]
    top_variance = np.var(top_region)
    
    if top_variance < 1000:  # 颜色单一，可能是导航栏
        actual_top = top_height
    else:
        actual_top = 0
    
    # 检测底部导航栏
    bottom_region = img[h - bottom_height:h, :]
    bottom_variance = np.var(bottom_region)
    
    if bottom_variance < 1000:
        actual_bottom = bottom_height
    else:
        actual_bottom = 0
    
    print(f"检测导航栏: 顶部={actual_top}px, 底部={actual_bottom}px")
    return actual_top, actual_bottom


def find_best_stitch_point(img1: np.ndarray, img2: np.ndarray,
                          overlap: int,
                          direction: str = 'vertical') -> int:
    """
    在重叠区域内找到最佳拼接点
    
    参数:
        img1: 第一张图片
        img2: 第二张图片
        overlap: 重叠区域大小
        direction: 拼接方向
    
    返回:
        最佳拼接点的偏移量（从重叠区域边界开始）
    """
    if direction == 'vertical':
        h1, w = img1.shape[:2]
        h2 = img2.shape[0]
        
        # 重叠区域
        overlap_region1 = img1[h1 - overlap:h1, :]
        overlap_region2 = img2[:overlap, :]
        
        # 计算每个位置的差异
        best_offset = 0
        min_diff = float('inf')
        
        for offset in range(0, overlap, 5):
            # 在offset处计算差异
            region1 = overlap_region1[offset:, :]
            region2 = overlap_region2[:overlap - offset, :]
            
            # 计算SSD差异
            diff = np.sum((region1.astype(float) - region2.astype(float)) ** 2)
            
            if diff < min_diff:
                min_diff = diff
                best_offset = offset
        
        return best_offset
    
    else:  # horizontal
        w1, h = img1.shape[:2]
        w2 = img2.shape[1]
        
        overlap_region1 = img1[:, w1 - overlap:w1]
        overlap_region2 = img2[:, :overlap]
        
        best_offset = 0
        min_diff = float('inf')
        
        for offset in range(0, overlap, 5):
            region1 = overlap_region1[:, offset:]
            region2 = overlap_region2[:, :overlap - offset]
            
            diff = np.sum((region1.astype(float) - region2.astype(float)) ** 2)
            
            if diff < min_diff:
                min_diff = diff
                best_offset = offset
        
        return best_offset


def blend_overlap(img1: np.ndarray, img2: np.ndarray,
                 overlap: int,
                 blend_width: int = 50,
                 direction: str = 'vertical') -> np.ndarray:
    """
    融合重叠区域
    
    参数:
        img1: 第一张图片
        img2: 第二张图片
        overlap: 重叠区域大小
        blend_width: 融合宽度
        direction: 拼接方向
    
    返回:
        融合后的图片
    """
    if direction == 'vertical':
        h1, w = img1.shape[:2]
        h2 = img2.shape[0]
        
        # 创建结果画布
        total_h = h1 + h2 - overlap
        result = np.zeros((total_h, w, 3), dtype=np.uint8)
        
        # 复制img1的非重叠部分
        result[:h1 - overlap, :] = img1[:h1 - overlap, :]
        
        # 融合重叠区域
        overlap_region1 = img1[h1 - overlap:h1, :]
        overlap_region2 = img2[:overlap, :]
        
        # 创建权重渐变
        for i in range(overlap):
            if i < blend_width:
                # 渐变融合
                weight1 = 1.0 - i / blend_width
                weight2 = i / blend_width
            elif i > overlap - blend_width:
                # 底部渐变融合
                weight1 = (overlap - i) / blend_width
                weight2 = 1.0 - (overlap - i) / blend_width
            else:
                # 中间区域平均
                weight1 = weight2 = 0.5
            
            blended = overlap_region1[i] * weight1 + overlap_region2[i] * weight2
            result[h1 - overlap + i, :] = blended.astype(np.uint8)
        
        # 复制img2的非重叠部分
        result[overlap:, :] = img2[overlap:, :]
        
        return result
    
    else:  # horizontal
        w1, h = img1.shape[:2]
        w2 = img2.shape[1]
        
        total_w = w1 + w2 - overlap
        result = np.zeros((h, total_w, 3), dtype=np.uint8)
        
        result[:, :w1 - overlap] = img1[:, :w1 - overlap]
        
        overlap_region1 = img1[:, w1 - overlap:w1]
        overlap_region2 = img2[:, :overlap]
        
        for i in range(overlap):
            if i < blend_width:
                weight1 = 1.0 - i / blend_width
                weight2 = i / blend_width
            elif i > overlap - blend_width:
                weight1 = (overlap - i) / blend_width
                weight2 = 1.0 - (overlap - i) / blend_width
            else:
                weight1 = weight2 = 0.5
            
            blended = overlap_region1[:, i] * weight1 + overlap_region2[:, i] * weight2
            result[:, w1 - overlap + i] = blended.astype(np.uint8)
        
        result[:, overlap:] = img2[:, overlap:]
        
        return result


def stitch_images(images: List[np.ndarray],
                  direction: str = 'vertical',
                  auto_detect: bool = False,
                  remove_navbar: bool = False,
                  navbar_top_height: int = 44,
                  navbar_bottom_height: int = 34,
                  threshold: float = 0.8,
                  blend_width: int = 50) -> np.ndarray:
    """
    拼接多张图片
    
    参数:
        images: 图片列表
        direction: 拼接方向
        auto_detect: 是否自动检测重叠
        remove_navbar: 是否移除导航栏
        navbar_top_height: 顶部导航栏高度
        navbar_bottom_height: 底部导航栏高度
        threshold: 匹配阈值
        blend_width: 融合宽度
    
    返回:
        拼接后的图片
    """
    if len(images) < 2:
        raise ValueError("至少需要2张图片才能拼接")
    
    # 移除导航栏
    if remove_navbar:
        print("移除导航栏...")
        processed_images = []
        for i, img in enumerate(images):
            top_nav, bottom_nav = detect_navbar(img, navbar_top_height, navbar_bottom_height)
            h, w = img.shape[:2]
            # 裁剪掉导航栏
            if top_nav > 0 or bottom_nav > 0:
                cropped = img[top_nav:h - bottom_nav, :]
                processed_images.append(cropped)
            else:
                processed_images.append(img)
        images = processed_images
    
    # 开始拼接
    result = images[0].copy()
    
    for i in range(1, len(images)):
        print(f"拼接第 {i+1}/{len(images)} 张图片...")
        
        img1 = result
        img2 = images[i]
        
        if auto_detect:
            # 自动检测重叠
            overlap, confidence = find_overlap(img1, img2, direction, threshold)
            print(f"检测到重叠: {overlap}px, 置信度: {confidence:.2f}")
            
            if overlap > 0:
                # 融合拼接
                result = blend_overlap(img1, img2, overlap, blend_width, direction)
            else:
                # 直接拼接（无重叠）
                if direction == 'vertical':
                    result = np.vstack([img1, img2])
                else:
                    result = np.hstack([img1, img2])
        else:
            # 直接拼接
            if direction == 'vertical':
                result = np.vstack([img1, img2])
            else:
                result = np.hstack([img1, img2])
    
    return result


def main():
    parser = argparse.ArgumentParser(description='智能图片拼接工具')
    parser.add_argument('--input-dir', required=True, help='输入图片目录')
    parser.add_argument('--output', required=True, help='输出图片路径')
    parser.add_argument('--direction', choices=['vertical', 'horizontal'], 
                        default='vertical', help='拼接方向（默认: vertical）')
    parser.add_argument('--auto-detect', action='store_true',
                        help='自动检测重复内容并智能拼接')
    parser.add_argument('--remove-navbar', action='store_true',
                        help='移除导航栏（状态栏、底部导航）')
    parser.add_argument('--navbar-top-height', type=int, default=44,
                        help='顶部导航栏高度（默认: 44px，iOS）')
    parser.add_argument('--navbar-bottom-height', type=int, default=34,
                        help='底部导航栏高度（默认: 34px，iOS）')
    parser.add_argument('--threshold', type=float, default=0.8,
                        help='相似度阈值 0-1（默认: 0.8）')
    parser.add_argument('--blend-width', type=int, default=50,
                        help='融合宽度（默认: 50px）')
    
    args = parser.parse_args()
    
    try:
        # 加载图片
        images = load_images_from_dir(args.input_dir)
        
        # 拼接图片
        result = stitch_images(
            images=images,
            direction=args.direction,
            auto_detect=args.auto_detect,
            remove_navbar=args.remove_navbar,
            navbar_top_height=args.navbar_top_height,
            navbar_bottom_height=args.navbar_bottom_height,
            threshold=args.threshold,
            blend_width=args.blend_width
        )
        
        # 保存结果
        cv2.imwrite(args.output, result)
        print(f"拼接成功，输出至 {args.output}")
        print(f"最终尺寸: {result.shape[1]}x{result.shape[0]}")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
