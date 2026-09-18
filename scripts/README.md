# 数据处理脚本（scripts/）

本目录存放从原始视频 / 数据转换成 EndoNeRF 格式的工具脚本。

## 当前脚本

### `extract_frames.py` —— MP4 抽帧 + 裁剪

把手术视频（MP4）抽成帧，并按需裁剪掉画面上的无关信息（文字栏、黑边、UI 等），输出到 `images/` 目录。

```bash
# 查看帮助
python scripts/extract_frames.py -h

# 抽帧 + 裁剪（示例：裁掉顶部 80px 的文字栏，保留 1280x720）
python scripts/extract_frames.py --video /mnt/t-1/video.mp4 \
    --outdir data/endonerf/my_scene/images \
    --crop 0 80 1280 720 \
    --save-first
```

**确定裁剪区域的小技巧**（无图形界面时）：

```bash
# 1. 查看视频分辨率
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height -of csv=p=0 /mnt/t-1/video.mp4

# 2. 导出第一帧，目测无关信息的位置
ffmpeg -i /mnt/t-1/video.mp4 -vframes 1 first_frame.png
```

也可以直接用 ffmpeg 一步完成抽帧 + 裁剪：

```bash
ffmpeg -i video.mp4 -vf "crop=W:H:X:Y" images/%05d.png
# crop=宽:高:左上角x:左上角y
```

## ⚠️ 重要提醒

1. **裁剪尽量对称 / 居中**：`scene/endo_loader.py` 把相机主点硬编码在图像中心
   `(W//2, H//2)`，只裁掉一侧会导致主点偏移、几何不准。
2. **记住裁剪后的 H、W**：后续生成 `poses_bounds.npy` 时需要用裁剪后的分辨率与焦距。
3. **输出文件名必须连续**：代码按文件名字典序读取，`00000.png, 00001.png, ...`
   要和位姿逐帧对应。

## EndoNeRF 完整数据格式

```
data/endonerf/你的场景名/
├── images/            # 原始帧（本脚本生成）
├── masks/             # 器械掩码（白色=器械，可用 GroundedSAM 生成）
├── depth/             # 双目模式深度（STTR）；单目模式则放 monodepth/（DepthAnything）
└── poses_bounds.npy   # 相机位姿（LLFF 格式，COLMAP / EndoNeRF SfM 生成）
```

> 待办：位姿 `poses_bounds.npy` 生成脚本、掩码 / 深度组织脚本将陆续补充到本目录。
