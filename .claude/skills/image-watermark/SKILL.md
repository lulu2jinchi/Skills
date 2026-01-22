---
name: image-watermark
description: 给图片添加文字或图片水印，支持自定义位置、透明度、字体大小等参数；适用于版权保护、品牌标识、内容标记等场景
dependency:
  python:
    - Pillow>=10.0.0
---

# 图片水印添加工具

## 任务目标
- 本 Skill 用于：为图片添加文字水印或图片水印，以及提取图片透明背景
- 能力包含：
  - **文字水印**（自定义内容、字体大小、颜色、倾斜角度，含emoji支持）
  - **图片水印**（叠加PNG透明图片、旋转角度）
  - **透明背景提取**（将普通图片转换为透明背景PNG）
  - 单水印模式：9宫格位置选择 + 自定义边距
  - 平铺模式：斜向重复覆盖，适用于版权保护和防泄露
  - Emoji水印：自动检测并优先使用系统emoji字体
    - macOS: Apple Color Emoji（彩色）
    - Windows: Segoe UI Emoji（彩色）
    - Linux: Symbola（单色）
  - 透明度控制
  - 批量处理
- 触发条件：用户需要给图片添加水印、版权标识、品牌logo，或将普通图片转换为透明背景PNG

## 前置准备
- 依赖说明：需安装 Pillow 图像处理库
  ```
  Pillow>=10.0.0
  ```

## 操作步骤

### 文字水印模式
1. **参数准备**
   - 水印文字：确定要添加的文字内容（支持emoji）
   - 位置：从9宫格位置中选择（center/top-left/bottom-right等）
   - 字体大小：根据图片尺寸选择合适的字号
   - 透明度：建议0.3-0.7，避免过度遮挡

2. **字体选择**（自动）
   - **包含emoji时**：自动优先使用系统emoji字体
     - **macOS**: Apple Color Emoji（🎨 彩色渲染）
     - **Windows**: Segoe UI Emoji（🎨 彩色渲染）
     - **Linux**: Symbola（⚫ 单色渲染）
   - 纯中文：使用中文字体（文泉驿/微软雅黑/PingFang等）
   - 纯英文：使用Arial或其他系统字体

3. **执行加水印**
   - 调用 `scripts/add_watermark.py` 添加文字水印
   - 示例参数：
     ```bash
     python scripts/add_watermark.py \
       --input ./input.jpg \
       --output ./output.jpg \
       --mode text \
       --text "版权所有" \
       --position center \
       --opacity 0.5 \
       --font-size 48
     ```

### 提取透明背景模式
1. **功能说明**
   - 将普通图片（JPG、PNG等）转换为透明背景的PNG图片
   - 自动检测背景色（默认左上角像素颜色）
   - 将背景色及相似颜色设置为透明
   - 支持调整颜色容差参数

2. **参数准备**
   - 输入图片：可以是JPG、PNG等任意格式
   - 容差范围：0-255，默认30
     - 容差越小：只提取与背景色完全一致的颜色
     - 容差越大：提取更多接近背景色的颜色

3. **执行提取**
   - 调用 `scripts/add_watermark.py` 提取透明背景
   - 示例参数：
     ```bash
     python scripts/add_watermark.py \
       --input ./logo.jpg \
       --output ./logo.png \
       --mode extract \
       --tolerance 30
     ```
   - 调整容差的示例：
     ```bash
     # 较小容差，只提取纯白色背景
     python scripts/add_watermark.py \
       --input ./logo.jpg \
       --output ./logo_strict.png \
       --mode extract \
       --tolerance 10
     
     # 较大容差，提取浅色背景
     python scripts/add_watermark.py \
       --input ./logo.jpg \
       --output ./logo_loose.png \
       --mode extract \
       --tolerance 50
     ```

### 图片水印模式
1. **参数准备**
   - 水印图片：准备透明背景的PNG图片（可先使用extract模式提取）
   - 位置：选择放置位置
   - 透明度：建议0.5-0.8
   - 缩放比例：根据原图大小调整水印尺寸
   - 水印旋转角度：可选，用于倾斜水印图片（新增）

2. **执行加水印**
   - 调用 `scripts/add_watermark.py` 添加图片水印
   - 示例参数：
     ```bash
     python scripts/add_watermark.py \
       --input ./photo.jpg \
       --output ./photo_watermarked.jpg \
       --mode image \
       --watermark ./logo.png \
       --position bottom-right \
       --opacity 0.7 \
       --scale 0.15
     ```
   - 带旋转的示例：
     ```bash
     python scripts/add_watermark.py \
       --input ./photo.jpg \
       --output ./photo_rotated.jpg \
       --mode image \
       --watermark ./logo.png \
       --position bottom-right \
       --opacity 0.7 \
       --scale 0.15 \
       --wm-angle 30
     ```

### 平铺水印模式（推荐用于版权保护）
1. **参数准备**
   - 水印内容：文字或图片
   - 平铺角度：建议20-45度（默认30度）
   - 平铺间距：1.5-3.0倍水印尺寸（默认2.0）
   - 平铺透明度：建议0.1-0.3（比单水印更淡）

2. **执行平铺水印**
   - 调用 `scripts/add_watermark.py` 添加平铺水印
   - 文字平铺示例：
     ```bash
     python scripts/add_watermark.py \
       --input ./photo.jpg \
       --output ./photo_tiled.jpg \
       --mode text \
       --text "机密文件" \
       --tile \
       --font-size 36 \
       --tile-angle 30 \
       --tile-spacing 2.0 \
       --tile-opacity 0.2
     ```
   - 图片平铺示例：
     ```bash
     python scripts/add_watermark.py \
       --input ./document.jpg \
       --output ./document_protected.jpg \
       --mode image \
       --watermark ./logo.png \
       --tile \
       --scale 0.1 \
       --tile-angle 25 \
       --tile-spacing 2.5 \
       --tile-opacity 0.15
     ```

### 批量处理
- 当需要对多张图片添加相同水印时，智能体可循环调用脚本处理每个文件
- 保持水印参数一致性，仅改变输入输出路径

## 资源索引
- 核心脚本：[scripts/add_watermark.py](scripts/add_watermark.py)（实现文字和图片水印功能）
- 参数说明：[references/watermark-guide.md](references/watermark-guide.md)（位置参数、透明度、字体等详细说明）

## 注意事项
- 文字水印自动选择系统字体，支持中文
- **emoji字体支持**（取决于运行环境）：
  - **macOS环境**：自动使用Apple Color Emoji，支持完整彩色emoji渲染 ✨
  - **Windows环境**：自动使用Segoe UI Emoji，支持完整彩色emoji渲染 ✨
  - **云端Linux环境**：使用Symbola字体，**单色emoji渲染**（黑色图形）⚠️
    - ⭐ 支持常见emoji字符（⭐😀🎨🎉⚡❤️🔥等）
    - ⚠️ 不支持彩色emoji
    - 💡 使用建议：深色字体 + 不透明/低透明度(0.7-1.0) + 大字号(50-80)
- 图片水印建议使用PNG格式（带透明通道），可使用extract模式从JPG转换
- **透明背景提取**：
  - 自动以左上角像素颜色作为背景色进行识别
  - 容差参数(`--tolerance`)控制背景识别范围：
    - 小容差(10-20)：适合纯色背景
    - 中等容差(30-50)：适合轻微渐变的背景
    - 大容差(50-100)：适合有明显颜色差异的背景
  - 输出格式强制为PNG，保持透明通道
- 输出格式与原图保持一致，质量不降低（extract模式除外，输出PNG）
- 透明度为0时水印不可见，建议范围0.3-0.7
- 浅色背景建议使用深色文字（`--color "0,0,0"`）
- 深色背景建议使用浅色文字（`--color "255,255,255"`）

## 使用示例

### 示例1：添加版权文字水印
```bash
python scripts/add_watermark.py \
  --input ./product.jpg \
  --output ./product_watermarked.jpg \
  --mode text \
  --text "© 2024 我的品牌" \
  --position bottom-right \
  --opacity 0.4 \
  --font-size 32 \
  --margin 20
```

### 示例2：平铺水印（版权保护）
```bash
python scripts/add_watermark.py \
  --input ./photo.jpg \
  --output ./photo_protected.jpg \
  --mode text \
  --text "版权所有 · 严禁复制" \
  --tile \
  --font-size 40 \
  --tile-angle 30 \
  --tile-spacing 2.0 \
  --tile-opacity 0.15
```

### 示例3：添加品牌Logo水印
```bash
python scripts/add_watermark.py \
  --input ./banner.png \
  --output ./banner_branded.png \
  --mode image \
  --watermark ./logo.png \
  --position top-left \
  --opacity 0.8 \
  --scale 0.1 \
  --margin 15
```

### 示例3.1：添加倾斜品牌Logo水印
```bash
python scripts/add_watermark.py \
  --input ./banner.png \
  --output ./banner_branded_tilted.png \
  --mode image \
  --watermark ./logo.png \
  --position bottom-right \
  --opacity 0.7 \
  --scale 0.15 \
  --wm-angle 30 \
  --margin 20
```

### 示例4：防泄露平铺水印
```bash
python scripts/add_watermark.py \
  --input ./confidential.jpg \
  --output ./confidential_protected.jpg \
  --mode text \
  --text "内部机密 · 仅限内部使用" \
  --tile \
  --font-size 50 \
  --tile-angle 45 \
  --tile-spacing 2.5 \
  --tile-opacity 0.1
```

### 示例5：从JPG提取透明背景PNG
```bash
# 将白底JPG logo转换为透明背景PNG
python scripts/add_watermark.py \
  --input ./logo_white_bg.jpg \
  --output ./logo_transparent.png \
  --mode extract \
  --tolerance 30

# 将提取的透明PNG作为水印添加到图片上
python scripts/add_watermark.py \
  --input ./product.jpg \
  --output ./product_branded.jpg \
  --mode image \
  --watermark ./logo_transparent.png \
  --position top-left \
  --opacity 0.8 \
  --scale 0.12
```

### 示例6：Emoji水印
```bash
python scripts/add_watermark.py \
  --input ./photo.jpg \
  --output ./photo_emoji.jpg \
  --mode text \
  --text "⭐ Premium · 原创" \
  --position bottom-right \
  --font-size 40 \
  --opacity 0.6
```

### Emoji水印（云端环境说明）

**重要提示：云端执行环境是Linux，使用Symbola字体渲染单色emoji**

云端emoji渲染特点：
- ✅ Symbola字体支持emoji字符（⭐😀🎨等）
- ⚠️ 单色渲染（黑色图形）
- ⚠️ 不支持彩色emoji

**使用建议**：

1. **浅色背景**：使用深色emoji或配合深色文字
   ```bash
   python scripts/add_watermark.py \
     --input ./photo.jpg \
     --output ./emoji.jpg \
     --mode text \
     --text "⭐ Premium" \
     --color "0,0,0" \
     --opacity 0.8
   ```

2. **深色背景**：使用浅色emoji或配合浅色文字
   ```bash
   python scripts/add_watermark.py \
     --input ./photo.jpg \
     --output ./emoji.jpg \
     --mode text \
     --text "⭐ Premium" \
     --color "255,255,255" \
     --opacity 0.8
   ```

3. **提高可见性**：
   - 使用不透明或低透明度（0.7-1.0）
   - 确保颜色与背景有足够对比度
   - 增大字体大小（建议50-80）

### 示例6：Emoji平铺水印
```bash
python scripts/add_watermark.py \
  --input ./design.jpg \
  --output ./design_tiled.jpg \
  --mode text \
  --text "🎨 艺术作品" \
  --tile \
  --tile-angle 25 \
  --tile-opacity 0.15
```
