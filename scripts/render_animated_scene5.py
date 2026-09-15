import os
import sys
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

base_dir = r"C:\AI\影片製作_透析高血壓衛教"
brain_dir = r"C:\Users\pink0\.gemini\antigravity\brain\a835a13b-300f-4228-9146-ed73f327da63"
audio_path = os.path.join(base_dir, "audio", "scene_05.mp3")
out_mp4 = os.path.join(base_dir, "output", "樣片_第5幕_心臟像氣球_動態升級版.mp4")

# Font paths
font_bold = r"C:\Windows\Fonts\msjhbd.ttc"
font_reg = r"C:\Windows\Fonts\msjh.ttc"

# Load source images
img_over_p = os.path.join(brain_dir, "heart_balloon_overfill_1789391372959.jpg")
img_deflate_p = os.path.join(brain_dir, "heart_balloon_deflate_1789391388074.jpg")
img_balance_p = os.path.join(brain_dir, "heart_healthy_balanced_1789391403949.jpg")

im_over = Image.open(img_over_p).convert("RGBA")
im_deflate = Image.open(img_deflate_p).convert("RGBA")
im_balance = Image.open(img_balance_p).convert("RGBA")

# Crop deflated heart to remove bottom English text
w_d, h_d = im_deflate.size
im_deflate = im_deflate.crop((0, 0, w_d, int(h_d * 0.72)))

# Crop balance heart to remove speech bubble on right if needed or keep clean
w_b, h_b = im_balance.size
im_balance = im_balance.crop((0, 0, int(w_b * 0.85), int(h_b * 0.85)))

def make_transparent(im, thresh=242):
    """Remove white background cleanly with soft alpha"""
    im = im.convert("RGBA")
    data = im.getdata()
    new_data = []
    for item in data:
        r, g, b, a = item
        if r > thresh and g > thresh and b > thresh:
            # smooth feathering
            avg = (r + g + b) / 3.0
            diff = avg - thresh
            new_a = max(0, int(255 - diff * (255 / (255 - thresh))))
            new_data.append((r, g, b, new_a))
        else:
            new_data.append((r, g, b, a))
    im.putdata(new_data)
    return im

print("Processing transparent cutout illustrations...")
im_over_trans = make_transparent(im_over)
im_deflate_trans = make_transparent(im_deflate)
im_balance_trans = make_transparent(im_balance)

# Target dimensions for placing in 1920x1080 layout
# Left card balloon: base size 380x380
# Right card balloon: base size 320x320
# Bottom card heart: base size 150x150
im_over_base = im_over_trans.resize((380, 380), Image.Resampling.LANCZOS)
im_deflate_base = im_deflate_trans.resize((320, 240), Image.Resampling.LANCZOS)
im_balance_base = im_balance_trans.resize((150, 150), Image.Resampling.LANCZOS)

# Animation parameters
FPS = 30
DURATION = 17.52
TOTAL_FRAMES = int(FPS * DURATION) + 1 # ~526 frames
WIDTH, HEIGHT = 1920, 1080

f_title = ImageFont.truetype(font_bold, 44)
f_card_title = ImageFont.truetype(font_bold, 34)
f_bullet = ImageFont.truetype(font_bold, 25)
f_alert = ImageFont.truetype(font_bold, 28)
f_foot = ImageFont.truetype(font_bold, 24)
f_sub = ImageFont.truetype(font_bold, 30)

def draw_wrapped_text(d, text, pos, font, fill, max_width=750, line_spacing=8):
    lines = text.split("\n")
    x, y = pos
    for line in lines:
        d.text((x, y), line, font=font, fill=fill)
        bbox = d.textbbox((x, y), line, font=font)
        y += (bbox[3] - bbox[1]) + line_spacing

def get_subtitle(t):
    if t < 3.2:
        return "【第二招】 心臟像氣球：認識「乾體重」與體液平衡"
    elif t < 8.5:
        return "喝水過多 → 氣球過度吹大 → 血管被水撐緊、血壓直線飆高！"
    elif t < 11.5:
        return "心肌過度拉扯彈性疲乏，長期將導致心臟肥大與衰竭！"
    else:
        return "洗腎脫水太快 → 氣球急速扁縮 → 容易劇烈抽筋與引發低血壓！"

# Setup FFmpeg pipe for high-speed rendering
ffmpeg_cmd = [
    "ffmpeg", "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", f"{WIDTH}x{HEIGHT}",
    "-pix_fmt", "rgb24",
    "-r", str(FPS),
    "-i", "-", # Pipe input
    "-i", audio_path,
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    out_mp4
]

print(f"Starting animation rendering ({TOTAL_FRAMES} frames @ {FPS} FPS)...")
proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

for frame_idx in range(TOTAL_FRAMES):
    t = frame_idx / float(FPS)
    
    # 1. Base Canvas
    frame = Image.new("RGB", (WIDTH, HEIGHT), "#F5F7FA")
    d = ImageDraw.Draw(frame)
    
    # Top banner bar
    d.rectangle([(0, 0), (WIDTH, 110)], fill="#0D47A1")
    d.text((60, 25), "國立成功大學醫學院附設醫院 血液透析室", font=ImageFont.truetype(font_bold, 36), fill="#FFFFFF")
    d.rounded_rectangle([(WIDTH - 280, 25), (WIDTH - 50, 85)], radius=15, fill="#1976D2")
    d.text((WIDTH - 250, 36), "透析衛教短片", font=ImageFont.truetype(font_bold, 28), fill="#FFFFFF")
    
    # Title
    d.text((60, 130), "【第二招】心臟像氣球：認識「乾體重」與體液平衡", font=f_title, fill="#0D47A1")
    
    # Dynamic emphasis colors
    is_left_focus = (3.2 <= t < 11.5)
    is_right_focus = (t >= 11.5)
    
    # Left Card
    left_outline = "#D32F2F" if is_left_focus else "#EF9A9A"
    left_border_w = 5 if is_left_focus else 3
    d.rounded_rectangle([(60, 200), (930, 770)], radius=25, fill="#FFFFFF", outline=left_outline, width=left_border_w)
    d.rounded_rectangle([(60, 200), (930, 290)], radius=25, fill="#D32F2F")
    d.text((120, 222), "【喝水過多：氣球過度吹大】", font=f_card_title, fill="#FFFFFF")
    
    # Right Card
    right_outline = "#F57C00" if is_right_focus else "#FFE082"
    right_border_w = 5 if is_right_focus else 3
    d.rounded_rectangle([(980, 200), (1850, 770)], radius=25, fill="#FFFFFF", outline=right_outline, width=right_border_w)
    d.rounded_rectangle([(980, 200), (1850, 290)], radius=25, fill="#F57C00")
    d.text((1040, 222), "【脫水過急：氣球快速扁縮】", font=f_card_title, fill="#FFFFFF")
    
    # -------------------------------------------------------------
    # ANIMATION 1: Left Balloon Heartbeat Pulsing & Water Swell
    # -------------------------------------------------------------
    if is_left_focus:
        # Organic heartbeat pulse (double beat: lub-dub)
        beat_phase = (t - 3.2) * 4.5 # ~70 bpm
        pulse = 0.08 * math.sin(beat_phase * math.pi) * (1.0 if math.sin(beat_phase * math.pi) > 0 else 0.2)
        scale_over = 1.0 + pulse
        # Warning flash box on left
        warn_alpha = int(128 + 127 * math.sin(t * 8))
        d.rounded_rectangle([(90, 680), (900, 745)], radius=15, fill="#FFEBEE", outline="#D32F2F", width=2)
        d.rounded_rectangle([(110, 688), (200, 737)], radius=8, fill="#D32F2F")
        d.text((120, 696), "警 訊", font=ImageFont.truetype(font_bold, 22), fill="#FFFFFF")
        d.text((215, 694), "體液超載！心肌過度擴張，引發高血壓！", font=f_alert, fill="#C62828")
    else:
        scale_over = 1.0
        
    cur_w_over = int(380 * scale_over)
    cur_h_over = int(380 * scale_over)
    im_over_cur = im_over_base.resize((cur_w_over, cur_h_over), Image.Resampling.LANCZOS)
    # Center position of left illustration
    cx_l, cy_l = 495, 460
    frame.paste(im_over_cur, (cx_l - cur_w_over // 2, cy_l - cur_h_over // 2), im_over_cur)
    
    # Left Bullets
    b_text1 = "• 體內多餘水份滯留，血管被水分強力撐緊！\n• 血壓直線飆高 → 容量型高血壓\n• 心肌反覆拉扯彈性疲乏，長期導致心臟肥大與衰竭！"
    draw_wrapped_text(d, b_text1, (100, 580 if is_left_focus else 610), f_bullet, "#263238", max_width=760, line_spacing=10)
    
    # -------------------------------------------------------------
    # ANIMATION 2: Right Balloon Cramp Vibration & Lightning Glow
    # -------------------------------------------------------------
    if is_right_focus:
        # Cramp tremor shake effect
        shake_x = int(3 * math.sin(t * 30))
        shake_y = int(2 * math.cos(t * 25))
        scale_def = 0.95 + 0.05 * math.sin(t * 12)
        d.rounded_rectangle([(1010, 680), (1820, 745)], radius=15, fill="#FFF3E0", outline="#F57C00", width=2)
        d.rounded_rectangle([(1030, 688), (1120, 737)], radius=8, fill="#F57C00")
        d.text((1040, 696), "危 險", font=ImageFont.truetype(font_bold, 22), fill="#FFFFFF")
        d.text((1135, 694), "脫水太快！血液循環驟降，引發抽筋與休克！", font=f_alert, fill="#E65100")
    else:
        shake_x, shake_y = 0, 0
        scale_def = 1.0
        
    cur_w_def = int(320 * scale_def)
    cur_h_def = int(240 * scale_def)
    im_def_cur = im_deflate_base.resize((cur_w_def, cur_h_def), Image.Resampling.LANCZOS)
    cx_r, cy_r = 1410 + shake_x, 460 + shake_y
    frame.paste(im_def_cur, (cx_r - cur_w_def // 2, cy_r - cur_h_def // 2), im_def_cur)
    
    # Right Bullets
    b_text2 = "• 洗腎短時間內拉出過多水分，血管瞬間扁縮！\n• 脫水速度過快引發「透析中低血壓」\n• 導致劇烈小腿抽筋、噁心嘔吐、甚至心肌缺血損傷！"
    draw_wrapped_text(d, b_text2, (1020, 580 if is_right_focus else 610), f_bullet, "#263238", max_width=780, line_spacing=10)
    
    # -------------------------------------------------------------
    # Bottom Card: Dry Weight & Balance Target
    # -------------------------------------------------------------
    d.rounded_rectangle([(60, 795), (1850, 955)], radius=22, fill="#E8F5E9", outline="#66BB6A", width=3)
    # Paste happy balance character on left of bottom card
    frame.paste(im_balance_base, (80, 800), im_balance_base)
    
    d.text((250, 820), "★ 什麼是最適「乾體重」(Dry Weight)？", font=ImageFont.truetype(font_bold, 36), fill="#1B5E20")
    d.text((250, 880), "透析後身上沒有多餘水腫、肺部無積水、呼吸順暢、血壓平穩時的最適理想體重！", font=ImageFont.truetype(font_bold, 28), fill="#2E7D32")
    
    # -------------------------------------------------------------
    # Dynamic Single-Line Subtitle Banner (Bottom)
    # -------------------------------------------------------------
    sub_txt = get_subtitle(t)
    sub_bbox = d.textbbox((0, 0), sub_txt, font=f_sub)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_h = sub_bbox[3] - sub_bbox[1]
    
    # Subtitle background capsule
    pad_x, pad_y = 35, 12
    box_x1 = (WIDTH - sub_w) // 2 - pad_x
    box_x2 = (WIDTH + sub_w) // 2 + pad_x
    box_y1 = 980
    box_y2 = box_y1 + sub_h + pad_y * 2
    
    d.rounded_rectangle([(box_x1, box_y1), (box_x2, box_y2)], radius=20, fill="#0A387E")
    d.text(((WIDTH - sub_w) // 2, box_y1 + pad_y), sub_txt, font=f_sub, fill="#FFFFFF")
    
    # Send RGB bytes to FFmpeg stdin
    proc.stdin.write(frame.tobytes())
    
    if frame_idx % 60 == 0:
        print(f"Rendered frame {frame_idx}/{TOTAL_FRAMES} ({(frame_idx/TOTAL_FRAMES)*100:.1f}%)")

proc.stdin.close()
proc.wait()
print("\n=== Sample Animated Scene 5 Generated Successfully! ===")
print("Output:", out_mp4)