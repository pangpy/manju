#!/usr/bin/env python3
# 远→近:慢速自然走路 + 街景背景缓推
import os
import numpy as np
from PIL import Image
from moviepy import ImageSequenceClip

POSES = "/Users/mac/voice/poses"
FA = os.path.join(POSES, "linwan_qian_a_cut.png")
FB = os.path.join(POSES, "linwan_qian_b_cut.png")
BG = os.path.join(POSES, "street_bg_1080.png")
OUT = "/tmp/walk_near5.mp4"

W, H, FPS, DUR = 1080, 1920, 12, 10
CHAR_H, CHAR_H_FAR = 900, 500
HEAD_LINE = 0.30
STEPS_PER_SEC = 1.8
BG_ZOOM = 0.10        # 背景最终放大幅度(镜头向人物推近10%)

def build():
    imgA = Image.open(FA).convert("RGBA")
    imgB = Image.open(FB).convert("RGBA")
    w0 = int(imgA.width * CHAR_H / imgA.height)
    imgA = imgA.resize((w0, CHAR_H), Image.Resampling.LANCZOS)
    imgB = imgB.resize((w0, CHAR_H), Image.Resampling.LANCZOS)

    bg0 = Image.open(BG).convert("RGB")

    frames = int(FPS * DUR)
    frames_per_step = FPS / STEPS_PER_SEC
    out_frames = []

    for i in range(frames):
        p = (i / FPS) / DUR
        ease = p ** 1.0

        # ---- 背景缓推:缓慢放大 + 向下略裁(地平线上移,透视一致) ----
        z = 1.0 + BG_ZOOM * ease
        zw, zh = int(W * z), int(H * z)
        frame_bg = bg0.resize((zw, zh), Image.Resampling.LANCZOS)
        ox = (zw - W) // 2
        oy = min(zh - H, int((zh - H) * 0.6))
        canvas = frame_bg.crop((ox, oy, ox + W, oy + H))

        # ---- 人物:由远及近 ----
        cur_h = int(CHAR_H_FAR + (CHAR_H - CHAR_H_FAR) * ease)
        cur_w = int(w0 * cur_h / CHAR_H)
        x = (W - cur_w) // 2
        y_start = int(H * HEAD_LINE)
        y_end = H - cur_h
        y = int(y_start + (y_end - y_start) * ease)

        ch_img = imgA if int(i / frames_per_step) % 2 == 0 else imgB
        ch = ch_img.resize((cur_w, cur_h), Image.Resampling.LANCZOS)
        alpha = ch.getchannel("A").point(lambda a: int(a * (0.85 + 0.15 * ease)))
        ch.putalpha(alpha)
        canvas.paste(ch, (x, y), mask=ch)

        out_frames.append(np.array(canvas))

    ImageSequenceClip(out_frames, fps=FPS).write_videofile(OUT, codec="libx264")
    print("完成:", OUT)

if __name__ == "__main__":
    build()
