# 智能图片拼接 Skill 使用示例

## 快速开始

### 1. 准备截图

将需要拼接的截图放在一个文件夹中，文件名按顺序命名：

```
screenshots/
├── 01.png
├── 02.png
├── 03.png
└── 04.png
```

### 2. 基础拼接

```bash
python .claude/skills/image-stitch/scripts/stitch_images.py \
  --input-dir ./screenshots/ \
  --output ./result.png \
  --direction vertical
```

### 3. 智能去重拼接（推荐）

```bash
python .claude/skills/image-stitch/scripts/stitch_images.py \
  --input-dir ./screenshots/ \
  --output ./result.png \
  --direction vertical \
  --auto-detect \
  --remove-navbar
```

## 截图技巧

### iOS/iPhone 截图

1. **启用辅助功能截图**
   - 设置 → 辅助功能 → 触控 → 辅助触控
   - 添加"截屏"到自定义菜单

2. **截图时保留重叠**
   - 每次截图前滚动的距离不要太大
   - 确保有50-100像素的重叠区域

3. **避免动态内容**
   - 尽量在内容静止时截图
   - 避免滚动动画还在进行时截图

### Android 截图

1. **使用滚动截图功能**
   - 部分Android系统自带滚动截图
   - 如果效果不佳，可使用本工具拼接

2. **导航栏处理**
   - Android状态栏高度：24-36px
   - 底部导航栏高度：48px（导航按钮）或8px（手势导航）

## 参数说明

### 相似度阈值 (--threshold)

控制重叠检测的严格程度：

- **0.9+**：高质量截图，内容稳定
- **0.8**：默认值，适用于大多数场景
- **0.7-0.8**：内容可能有轻微变化
- **0.6-0.7**：动态内容，需要更宽松的匹配

```bash
# 高质量截图
python .claude/skills/image-stitch/scripts/stitch_images.py \
  --input-dir ./screenshots/ \
  --output ./result.png \
  --auto-detect \
  --threshold 0.9

# 动态内容
python .claude/skills/image-stitch/scripts/stitch_images.py \
  --input-dir ./screenshots/ \
  --output ./result.png \
  --auto-detect \
  --threshold 0.7
```

### 融合宽度 (--blend-width)

控制拼接边缘的融合范围：

- **20-50px**：纯色背景，简单融合
- **50-100px**：纹理背景，需要平滑过渡
- **100-200px**：复杂内容，避免明显接缝

```bash
# 平滑融合
python .claude/skills/image-stitch/scripts/stitch_images.py \
  --input-dir ./screenshots/ \
  --output ./result.png \
  --auto-detect \
  --blend-width 100
```

### 导航栏高度

自动检测失败时可手动指定：

```bash
# iPhone X 及以上
python .claude/skills/image-stitch/scripts/stitch_images.py \
  --input-dir ./screenshots/ \
  --output ./result.png \
  --remove-navbar \
  --navbar-top-height 44 \
  --navbar-bottom-height 34

# Android
python .claude/skills/image-stitch/scripts/stitch_images.py \
  --input-dir ./screenshots/ \
  --output ./result.png \
  --remove-navbar \
  --navbar-top-height 24 \
  --navbar-bottom-height 48
```

## 常见场景

### 场景1：长网页拼接

```bash
python .claude/skills/image-stitch/scripts/stitch_images.py \
  --input-dir ./webpage/ \
  --output ./full_webpage.png \
  --direction vertical \
  --auto-detect \
  --threshold 0.85 \
  --blend-width 80
```

### 场景2：聊天记录拼接

```bash
python .claude/skills/image-stitch/scripts/stitch_images.py \
  --input-dir ./chat/ \
  --output ./chat_history.png \
  --direction vertical \
  --auto-detect \
  --remove-navbar
```

### 场景3：长文档拼接

```bash
python .claude/skills/image-stitch/scripts/stitch_images.py \
  --input-dir ./document/ \
  --output ./full_doc.png \
  --direction vertical \
  --auto-detect \
  --threshold 0.9 \
  --blend-width 50
```

### 场景4：水平拼接（宽图）

```bash
python .claude/skills/image-stitch/scripts/stitch_images.py \
  --input-dir ./horizontal/ \
  --output ./wide_view.png \
  --direction horizontal \
  --auto-detect
```

## 故障排除

### 问题1：拼接错位

**症状**：图片内容不连续，有明显错位

**解决方案**：
1. 确保图片按正确顺序命名（01.png, 02.png...）
2. 降低相似度阈值：`--threshold 0.75`
3. 增加截图时的重叠区域
4. 检查图片是否来自同一设备/分辨率

### 问题2：拼接缝明显

**症状**：拼接位置有明显边界

**解决方案**：
1. 增加融合宽度：`--blend-width 100`
2. 使用自动检测：`--auto-detect`
3. 确保截图时光照一致

### 问题3：导航栏未移除

**症状**：状态栏或底部导航栏仍存在

**解决方案**：
1. 手动指定高度：
   ```bash
   --navbar-top-height 44 --navbar-bottom-height 34
   ```
2. 使用固定高度模式

### 问题4：拼接失败

**症状**：程序报错或输出空白

**解决方案**：
1. 检查输入目录是否存在
2. 检查图片格式（支持PNG/JPG）
3. 检查图片是否损坏
4. 查看错误信息：`--auto-detect --verbose`

## 输出格式

- 默认输出PNG格式（无损）
- 可改为JPG格式（修改输出文件名后缀为.jpg）
- 输出图片尺寸取决于输入图片和重叠检测结果

## 性能建议

1. **图片数量**：建议一次拼接不超过20张
2. **图片尺寸**：建议每张不超过2000px（宽或高）
3. **重叠区域**：保持50-100像素的重叠
4. **批量处理**：多组截图分批处理

## 高级用法

### 使用脚本批量处理

```bash
#!/bin/bash
for dir in screenshots/*/; do
  dirname=$(basename "$dir")
  python .claude/skills/image-stitch/scripts/stitch_images.py \
    --input-dir "$dir" \
    --output "./results/${dirname}_stitched.png" \
    --direction vertical \
    --auto-detect \
    --remove-navbar
done
```

### Python 脚本调用

```python
from PIL import Image
import cv2
import numpy as np

# 导入拼接函数
from .claude.skills.image_stitch.scripts.stitch_images import stitch_images

# 加载图片
images = []
for i in range(1, 5):
    img = cv2.imread(f'screenshots/{i:02d}.png')
    images.append(img)

# 拼接
result = stitch_images(
    images=images,
    direction='vertical',
    auto_detect=True,
    remove_navbar=True,
    threshold=0.8,
    blend_width=50
)

# 保存
cv2.imwrite('result.png', result)
```

## 反馈与改进

如遇到问题或有改进建议，请：
1. 记录详细的错误信息
2. 提供输入图片示例（如有）
3. 说明使用场景和期望结果
