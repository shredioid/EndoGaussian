#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从 MP4 视频抽帧并裁剪，输出为 EndoNeRF 格式的 images/ 目录。

用法示例
--------
# 全部抽帧，不裁剪
python scripts/extract_frames.py --video /mnt/t-1/video.mp4 \
    --outdir data/endonerf/my_scene/images

# 裁掉顶部文字栏：保留区域左上角 (0, 80)，宽 1280 高 720
python scripts/extract_frames.py --video /mnt/t-1/video.mp4 \
    --outdir data/endonerf/my_scene/images --crop 0 80 1280 720

# 每隔 5 帧抽 1 帧（抽稀）
python scripts/extract_frames.py --video /mnt/t-1/video.mp4 \
    --outdir data/endonerf/my_scene/images --stride 5

# 只处理第 100 到 500 帧
python scripts/extract_frames.py --video /mnt/t-1/video.mp4 \
    --outdir data/endonerf/my_scene/images --start 100 --end 500

参数说明
--------
--crop X Y W H  保留区域：左上角坐标 (X, Y)，宽 W，高 H；不传则原图输出
--stride N      每隔 N 帧抽 1 帧（默认 1，即逐帧导出）
--start/--end   只处理 [start, end) 区间内的帧
--save-first    额外把第一帧存为 first_frame.png，便于目测确定裁剪区域
"""

import argparse
import os

import cv2


def parse_args():
    parser = argparse.ArgumentParser(description="MP4 抽帧 + 裁剪")
    parser.add_argument("--video", "-v", required=True, help="输入 MP4 路径")
    parser.add_argument("--outdir", "-o", required=True,
                        help="输出目录，例如 data/endonerf/scene/images")
    parser.add_argument("--crop", nargs=4, type=int, metavar=("X", "Y", "W", "H"),
                        help="保留区域：左上角 X Y，宽 W 高 H")
    parser.add_argument("--stride", type=int, default=1, help="每隔 N 帧抽 1 帧")
    parser.add_argument("--start", type=int, default=0, help="起始帧（含）")
    parser.add_argument("--end", type=int, default=None, help="结束帧（不含）")
    parser.add_argument("--save-first", action="store_true",
                        help="额外保存第一帧 first_frame.png，用于确定裁剪区域")
    return parser.parse_args()


def main():
    args = parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        raise SystemExit(f"无法打开视频: {args.video}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"视频信息: fps={fps:.2f}, total_frames={total}")
    print(f"裁剪区域: {tuple(args.crop) if args.crop else '不裁剪'}, stride={args.stride}")

    # 校验裁剪区域是否越界（用第一帧判断）
    _, first = cap.read()
    if first is None:
        raise SystemExit("无法读取视频第一帧")
    h, w = first.shape[:2]
    if args.crop:
        x, y, cw, ch = args.crop
        if x < 0 or y < 0 or x + cw > w or y + ch > h:
            print(f"警告: 裁剪区域 {args.crop} 超出画面尺寸 ({w}x{h})，将自动截断")
    # 重置到开头
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    saved = 0
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx < args.start or (args.end is not None and frame_idx >= args.end):
            frame_idx += 1
            continue

        if args.save_first and saved == 0:
            parent = os.path.dirname(args.outdir.rstrip("/")) or "."
            first_path = os.path.join(parent, "first_frame.png")
            cv2.imwrite(first_path, frame)
            print(f"已保存第一帧 → {first_path}")

        if (frame_idx - args.start) % args.stride == 0:
            if args.crop:
                x, y, cw, ch = args.crop
                frame = frame[y:y + ch, x:x + cw]
            out_path = os.path.join(args.outdir, f"{saved:05d}.png")
            cv2.imwrite(out_path, frame)
            saved += 1
        frame_idx += 1

    cap.release()
    print(f"完成: 共导出 {saved} 帧 → {args.outdir}")


if __name__ == "__main__":
    main()
