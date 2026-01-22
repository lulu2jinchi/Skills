# 水印参数说明指南

## 目录
- [位置参数](#位置参数)
- [透明度](#透明度)
- [字体大小](#字体大小)
- [缩放比例](#缩放比例)
- [颜色设置](#颜色设置)
- [边距设置](#边距设置)
- [平铺水印](#平铺水印)

## 概览
本指南详细说明水印工具的各项参数，帮助用户根据不同场景选择合适的参数组合。

---

## 位置参数

水印支持9宫格位置选择：

```
  top-left     top-center     top-right
     |             |              |
     |    center    |              |
     |             |              |
middle-left   middle-center  middle-right
     |             |              |
bottom-left  bottom-center  bottom-right
```

**参数值说明**：
- `center`: 居中放置
- `top-left`: 左上角
- `top-center`: 顶部居中
- `top-right`: 右上角
- `middle-left`: 左侧居中
- `middle-right`: 右侧居中
- `bottom-left`: 左下角
- `bottom-center`: 底部居中
- `bottom-right`: 右下角（推荐用于版权文字）

**使用建议**：
- 版权文字/Logo：`bottom-right` 或 `top-left`
- 促销信息：`center` 或 `top-center`
- 保密标记：`center` 且使用较大透明度

---

## 透明度

**取值范围**：0.0（完全透明） - 1.0（完全不透明）

**推荐值参考**：

| 场景 | 透明度 | 说明 |
|------|--------|------|
| 品牌Logo | 0.6 - 0.9 | 保持清晰可见 |
| 版权文字 | 0.3 - 0.5 | 不干扰主体内容 |
| 促销信息 | 0.5 - 0.7 | 突出但不过分 |
| 保密标记 | 0.2 - 0.4 | 清晰但不遮挡内容 |

**注意事项**：
- 透明度过低可能导致水印看不清
- 透明度过高会遮挡原图内容
- 浅色背景图片建议使用较低透明度

---

## 字体大小

**取值范围**：整数，单位为像素

**推荐值参考**：

| 图片宽度 | 推荐字体大小 |
|----------|--------------|
| < 800px  | 16 - 24      |
| 800 - 1200px | 24 - 36   |
| 1200 - 2000px | 36 - 48  |
| > 2000px | 48 - 72     |

**计算公式**：
```
字体大小 ≈ 图片宽度 × (0.02 ~ 0.035)
```

**使用建议**：
- 保持水印文字宽度不超过图片宽度的30%
- 多行文字可适当减小字号
- 标语类文字可适当加大字号

---

## 缩放比例

**适用范围**：仅图片水印模式

**参数含义**：水印图片宽度占原图宽度的比例

**推荐值参考**：

| 场景 | 缩放比例 | 说明 |
|------|----------|------|
| 小图标Logo | 0.05 - 0.1 | 辅助标识 |
| 品牌Logo | 0.1 - 0.15 | 主要标识 |
| 宣传水印 | 0.15 - 0.25 | 突出展示 |

**注意事项**：
- 缩放比例过大可能遮挡图片主体
- 比例过小导致水印不清晰
- 可先测试多个比例找到最佳值

---

## 颜色设置

**参数格式**：`R,G,B`（0-255）

**常用颜色参考**：

| 颜色 | RGB值 | 使用场景 |
|------|-------|----------|
| 纯白 | 255,255,255 | 深色背景图片 |
| 纯黑 | 0,0,0 | 浅色背景图片 |
| 浅灰 | 200,200,200 | 中性色调图片 |
| 金色 | 255,215,0 | 高端品牌标识 |
| 红色 | 255,0,0 | 警示或强调 |

**使用建议**：
- 选择与原图对比度高的颜色
- 避免与原图主色调过于相近
- 可结合透明度微调视觉效果

---

## 边距设置

**参数单位**：像素

**推荐值参考**：

| 场景 | 边距 |
|------|------|
| 紧贴边缘 | 0 - 10 |
| 标准留白 | 10 - 30 |
| 宽松留白 | 30 - 50 |

**使用建议**：
- 边距过小可能导致水印被裁剪
- 边距过大会显得过于孤立
- 保持与边框的适当距离

**使用建议**：
- 边距过小可能导致水印被裁剪
- 边距过大会显得过于孤立
- 保持与边框的适当距离

---

## 平铺水印

平铺水印将单个水印重复排列覆盖整个图片，适用于版权保护和防泄露场景。

### 平铺参数

| 参数 | 说明 | 默认值 | 推荐范围 |
|------|------|--------|----------|
| `--tile` | 启用平铺模式 | false | - |
| `--tile-angle` | 平铺角度（度） | 30 | 20-45 |
| `--tile-spacing` | 间距倍数 | 2.0 | 1.5-3.0 |
| `--tile-opacity` | 平铺透明度 | 0.15 | 0.1-0.3 |

### 平铺角度

平铺角度控制水印的倾斜方向：

| 角度 | 效果 | 适用场景 |
|------|------|----------|
| 0度 | 水平垂直对齐 | 品牌标识 |
| 20-30度 | 轻微倾斜 | 版权保护 |
| 45度 | 标准斜向 | 防泄露（推荐） |
| 60度 | 较大倾斜 | 特殊效果 |

**注意**：角度过大可能导致水印覆盖效果不佳。

### 平铺间距

间距倍数控制水印之间的距离：

| 倍数 | 效果 | 适用场景 |
|------|------|----------|
| 1.5 | 紧密排列 | 强保护 |
| 2.0 | 标准间距（默认） | 版权保护 |
| 2.5 | 宽松排列 | 平衡保护与美观 |
| 3.0 | 稀疏排列 | 轻度保护 |

**计算公式**：
```
实际间距 = 水印尺寸 × 间距倍数
```

### 平铺透明度

平铺透明度通常比单水印更淡，避免过度干扰原图：

| 场景 | 透明度 | 说明 |
|------|--------|------|
| 强保护 | 0.2-0.3 | 防泄露，水印清晰可见 |
| 版权保护 | 0.15-0.25 | 平衡保护与美观 |
| 轻度标识 | 0.1-0.15 | 不干扰内容展示 |

**重要**：平铺水印叠加多个副本，即使单个透明度较低，整体效果也会累积增强。

### 平铺模式使用示例

**版权保护（斜向平铺）**：
```bash
python scripts/add_watermark.py \
  --input ./photo.jpg \
  --output ./photo_protected.jpg \
  --mode text \
  --text "© 2024 版权所有" \
  --tile \
  --tile-angle 30 \
  --tile-spacing 2.0 \
  --tile-opacity 0.15
```

**防泄露（高密度平铺）**：
```bash
python scripts/add_watermark.py \
  --input ./document.jpg \
  --output ./document_secure.jpg \
  --mode text \
  --text "机密文件 · 严禁外传" \
  --tile \
  --tile-angle 45 \
  --tile-spacing 1.5 \
  --tile-opacity 0.2
```

**品牌Logo平铺**：
```bash
python scripts/add_watermark.py \
  --input ./banner.jpg \
  --output ./banner_branded.jpg \
  --mode image \
  --watermark ./logo.png \
  --tile \
  --scale 0.08 \
  --tile-angle 20 \
  --tile-spacing 2.5 \
  --tile-opacity 0.1
```

---

## 完整示例

### 示例1：版权保护
```bash
python scripts/add_watermark.py \
  --input ./product.jpg \
  --output ./product_protected.jpg \
  --mode text \
  --text "© 2024 我的品牌 保留所有权利" \
  --position bottom-right \
  --font-size 24 \
  --opacity 0.3 \
  --margin 15 \
  --color 255,255,255
```

### 示例2：品牌标识
```bash
python scripts/add_watermark.py \
  --input ./banner.png \
  --output ./banner_branded.png \
  --mode image \
  --watermark ./logo.png \
  --position top-left \
  --opacity 0.8 \
  --scale 0.1 \
  --margin 20
```

### 示例3：平铺水印（防泄露）
```bash
python scripts/add_watermark.py \
  --input ./confidential.jpg \
  --output ./confidential_protected.jpg \
  --mode text \
  --text "机密文件 · 严禁外传" \
  --tile \
  --tile-angle 45 \
  --tile-spacing 2.0 \
  --tile-opacity 0.15 \
  --color 255,0,0
```

### 示例4：斜向版权平铺
```bash
python scripts/add_watermark.py \
  --input ./gallery.jpg \
  --output ./gallery_watermarked.jpg \
  --mode text \
  --text "版权所有 · 禁止转载" \
  --tile \
  --tile-angle 30 \
  --tile-spacing 2.5 \
  --tile-opacity 0.12
```
