---
name: image-stitch
description: 智能图片拼接工具，自动检测重复内容、删除多余导航栏、计算最佳拼接位置；适用于长截图拼接、滚动屏幕内容拼接、聊天记录拼接等场景
dependency:
  python:
    - Pillow>=10.0.0
    - opencv-python>=4.8.0
    - numpy>=1.24.0
---

# 智能图片拼接工具

## 任务目标
- 本 Skill 用于：将多张连续截图自动拼接成一张完整的长图
- 能力包含：
  - **自动检测重复内容**：通过图像相似度算法识别图片间的重叠区域
  - **删除导航栏**：自动识别并移除iOS/Android状态栏、底部导航栏等重复元素
  - **智能拼接点计算**：找到最佳拼接位置，避免内容错位
  - **无缝融合**：使用渐变融合消除拼接边缘
  - 支持水平拼接和垂直拼接
  - 批量处理多张图片
  - 输出高质量PNG/JPG图片
- 触发条件：用户需要拼接多张连续截图（如长网页、聊天记录、长文档等）

## 前置准备
- 依赖说明：需安装图像处理库
  ```
  Pillow>=10.0.0
  opencv-python>=4.8.0
  numpy>=1.24.0
  ```

## 操作步骤

### 基础拼接模式
1. **参数准备**
   - 输入图片：多张连续截图（按顺序命名或按字母顺序排序）
   - 输出路径：拼接后的图片保存路径
   - 拼接方向：vertical（垂直）或 horizontal（水平）

2. **执行拼接**
   - 调用 `scripts/stitch_images.py` 进行拼接
   - 示例参数：
     ```bash
     python scripts/stitch_images.py \
       --input-dir ./screenshots/ \
       --output ./stitched_result.png \
       --direction vertical
     ```

### 智能去重拼接模式（推荐）
1. **功能说明**
   - 自动检测图片间的重叠区域
   - 删除重复内容，只保留唯一部分
   - 自动识别和移除导航栏
   - 计算最佳拼接位置

2. **参数准备**
   - 输入图片目录：包含连续截图的文件夹
   - 匹配阈值：相似度阈值（0-1），默认0.8
     - 阈值越高：匹配越严格，需要更相似才能重叠
     - 阈值越低：匹配较宽松，可能有轻微误差
   - 导航栏检测：自动开启

3. **执行智能拼接**
   - 调用脚本进行智能拼接
   - 示例参数：
     ```bash
     python scripts/stitch_images.py \
       --input-dir ./screenshots/ \
       --output ./stitched_result.png \
       --direction vertical \
       --auto-detect \
       --threshold 0.8
     ```

### 导航栏移除模式
1. **功能说明**
   - 自动识别iOS/Android状态栏（顶部时间、信号、电量等）
   - 自动识别底部导航栏（Home指示器、导航按钮等）
   - 在拼接前自动删除这些重复区域

2. **参数准备**
   - 状态栏高度：自动检测（默认iOS 44px，Android不同设备）
   - 底部导航栏：自动检测（默认34px）

3. **执行拼接**
   - 示例参数：
     ```bash
     python scripts/stitch_images.py \
       --input-dir ./screenshots/ \
       --output ./stitched_result.png \
       --direction vertical \
       --auto-detect \
       --remove-navbar
     ```

### 高级拼接参数
1. **融合宽度**：拼接边缘的渐变融合宽度（像素）
   - 默认：50像素
   - 增大值：融合更平滑，但可能模糊
   - 减小值：更锐利，但可能有明显接缝

2. **最小重叠**：最小重叠像素数（防止误匹配）
   - 默认：100像素
   - 增大值：减少误匹配，但可能遗漏部分重叠

3. **最大重叠**：最大重叠像素数（控制拼接精度）
   - 默认：图片高度的30%
   - 减小值：提高拼接速度，但可能降低精度

### 批量处理
- 当需要对多个文件夹的图片进行拼接时，可循环调用脚本处理
- 每个文件夹的图片按文件名排序后拼接

## 资源索引
- 核心脚本：[scripts/stitch_images.py](scripts/stitch_images.py)（实现智能拼接算法）
- 算法说明：[references/algorithm-guide.md](references/algorithm-guide.md)（拼接算法详细说明）

## 注意事项
- 输入图片必须按顺序排列（按文件名字母序）
- 图片尺寸应该相同或相近
- 建议：
  - 使用相同设备和分辨率拍摄
  - 截图时保留适当重叠（至少50-100像素）
  - 避免快速滚动导致的模糊
- 导航栏移除对固定布局（如状态栏）效果最好
- 如果图片内容变化大（如动态内容），建议提高匹配阈值
- 输出格式默认PNG（无损），可指定JPG（有损但体积小）

## 使用示例

### 示例1：基础垂直拼接
```bash
python scripts/stitch_images.py \
  --input-dir ./chat_screenshots/ \
  --output ./chat_history.png \
  --direction vertical
```

### 示例2：智能去重拼接（长网页）
```bash
python scripts/stitch_images.py \
  --input-dir ./webpage_screenshots/ \
  --output ./full_webpage.png \
  --direction vertical \
  --auto-detect \
  --threshold 0.85
```

### 示例3：移除导航栏拼接
```bash
python scripts/stitch_images.py \
  --input-dir ./app_screenshots/ \
  --output ./app_full_view.png \
  --direction vertical \
  --auto-detect \
  --remove-navbar \
  --navbar-top-height 44 \
  --navbar-bottom-height 34
```

### 示例4：水平拼接（横向内容）
```bash
python scripts/stitch_images.py \
  --input-dir ./horizontal_views/ \
  --output ./wide_view.png \
  --direction horizontal \
  --auto-detect
```

### 示例5：调整融合效果
```bash
python scripts/stitch_images.py \
  --input-dir ./screenshots/ \
  --output ./result.png \
  --direction vertical \
  --auto-detect \
  --blend-width 100 \
  --threshold 0.8
```

### 示例6：处理多组截图
```bash
# 拼接第一组
python scripts/stitch_images.py \
  --input-dir ./group1/ \
  --output ./stitched_group1.png \
  --direction vertical \
  --auto-detect

# 拼接第二组
python scripts/stitch_images.py \
  --input-dir ./group2/ \
  --output ./stitched_group2.png \
  --direction vertical \
  --auto-detect
```

## 算法原理

### 1. 重复内容检测
- 使用多尺度模板匹配算法
- 在相邻图片间寻找最佳重叠区域
- 计算归一化交叉相关系数(NCC)评估相似度

### 2. 拼接点计算
- 在匹配区域内寻找最佳拼接点
- 考虑图像梯度和边缘信息
- 选择最小差异的边界位置

### 3. 导航栏检测
- 基于固定高度假设（iOS/Android标准）
- 检测均匀区域（状态栏通常纯色或渐变）
- 对比多张图片的顶部/底部区域

### 4. 边缘融合
- 使用加权渐变融合
- 重叠区域内像素按距离权重混合
- 消除可见拼接缝
