import os
import sys
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

base_dir = r"C:\AI\影片製作_透析高血壓衛教"
brain_dir = r"C:\Users\pink0\.gemini\antigravity\brain\a835a13b-300f-4228-9146-ed73f327da63"
audio_path = os.path.join(base_dir, "audio", "scene_04.mp3")
out_mp4 = os.path.join(base_dir, "output", "樣片_第4幕_居家血壓722原則_動態升級版.mp4")

font_bold = r"C:\Windows\Fonts\msjhbd.ttc"
font_reg = r"C:\Windows\Fonts\msjh.ttc"

im_posture_raw = Image.open(os.path.join(brain_dir, "bp_correct_posture_1789392288777.jpg"))
im_logbook_raw = Image.open(os.path.join(brain_dir, "bp_logbook_record_1789392303649.jpg"))

def make_transparent(im, thresh=240):
    im = im.convert("RGBA")
    data = im.getdata()
    new_data = []
    for item in data:
        r, g, b, a = item
        if r > thresh and g > thresh and b > thresh:
            avg = (r + g + b) / 3.0
            diff = avg - thresh
            new_a = max(0, int(255 - diff * (255 / (255 - thresh))))
            new_data.append((r, g, b, new_a))
        else:
            new_data.append((r, g, b, a))
    im.putdata(new_data)
    return im

print("Processing high-resolution cutout illustrations...")
t_posture = make_transparent(im_posture_raw.crop((60, 40, 980, 980)))
t_logbook = make_transparent(im_logbook_raw.crop((50, 60, 960, 960)))

posture_base = t_posture.resize((260, 240), Image.Resampling.LANCZOS)
logbook_base = t_logbook.resize((260, 230), Image.Resampling.LANCZOS)

FPS = 30
DURATION = 20.23
TOTAL_FRAMES = int(FPS * DURATION) + 1
WIDTH, HEIGHT = 1920, 1080

f_title = ImageFont.truetype(font_bold, 42)
f_h2 = ImageFont.truetype(font_bold, 30)
f_sub_h2 = ImageFont.truetype(font_bold, 20)
f_num = ImageFont.truetype(font_bold, 46)
f_bullet = ImageFont.truetype(font_bold, 21)
f_badge = ImageFont.truetype(font_bold, 20)
f_target = ImageFont.truetype(font_bold, 28)
f_target_sub = ImageFont.truetype(font_bold, 21)
f_sub = ImageFont.truetype(font_bold, 28)

def draw_checkmark(draw, cx, cy, size=16, color="#2E7D32", width=4):
    p1 = (cx - size * 0.5, cy)
    p2 = (cx - size * 0.1, cy + size * 0.45)
    p3 = (cx + size * 0.6, cy - size * 0.5)
    draw.line([p1, p2, p3], fill=color, width=width)

def draw_wrapped_text(d, text, pos, font, fill, max_width=500, line_spacing=8):
    lines = text.split("\n")
    x, y = pos
    for line in lines:
        d.text((x, y), line, font=font, fill=fill)
        bbox = d.textbbox((x, y), line, font=font)
        y += (bbox[3] - bbox[1]) + line_spacing

def get_subtitle(t):
    if t < 9.7:
        return "請大家牢記居家血壓 722 原則：連續測量 7 天、每天早晚各量 1 次、每次量 2 遍取平均值。"
    else:
        return "居家血壓建議目標：收縮壓 120～135、舒張壓 60～80，並請把紀錄本帶來透析室！"

ffmpeg_cmd = [
    "ffmpeg", "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", f"{WIDTH}x{HEIGHT}",
    "-pix_fmt", "rgb24",
    "-r", str(FPS),
    "-i", "-",
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

print(f"Starting Scene 4 rendering ({TOTAL_FRAMES} frames @ {FPS} FPS)...")
proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

for frame_idx in range(TOTAL_FRAMES):
    t = frame_idx / float(FPS)
    frame = Image.new("RGB", (WIDTH, HEIGHT), "#F4F7F9")
    d = ImageDraw.Draw(frame)
    
    # 1. Top Hospital Header
    d.rectangle([(0, 0), (WIDTH, 105)], fill="#0D47A1")
    d.text((60, 24), "國立成功大學醫學院附設醫院 血液透析室", font=ImageFont.truetype(font_bold, 36), fill="#FFFFFF")
    d.rounded_rectangle([(WIDTH - 270, 24), (WIDTH - 50, 82)], radius=15, fill="#1976D2")
    d.text((WIDTH - 240, 35), "透析衛教短片", font=ImageFont.truetype(font_bold, 26), fill="#FFFFFF")
    
    # 2. Main Title
    d.text((60, 125), "【第一招】居家血壓量測黃金口訣：「７２２原則」", font=f_title, fill="#0D47A1")
    
    # Dynamic focus logic
    is_f1 = (t < 3.3)
    is_f2 = (3.3 <= t < 6.8)
    is_f3 = (6.8 <= t < 9.7)
    is_f4 = (t >= 9.7)
    
    # -------------------------------------------------------------
    # CARD 1: 7 連續 7 天 (x: 60 ~ 630)
    # -------------------------------------------------------------
    c1_outline = "#1565C0" if is_f1 else "#BBDEFB"
    c1_w = 5 if is_f1 else 3
    d.rounded_rectangle([(60, 185), (630, 675)], radius=22, fill="#FFFFFF", outline=c1_outline, width=c1_w)
    d.rounded_rectangle([(60, 185), (630, 290)], radius=22, fill="#1565C0")
    
    # Circle badge with pulse when active
    c1_scale = (1.0 + 0.05 * math.sin(t * 8)) if is_f1 else 1.0
    r_cx, r_cy = 125, 237
    rw, rh = int(40 * c1_scale), int(35 * c1_scale)
    d.ellipse([(r_cx - rw, r_cy - rh), (r_cx + rw, r_cy + rh)], fill="#FFFFFF")
    d.text((r_cx - 15, r_cy - 31), "7", font=f_num, fill="#1565C0")
    d.text((185, 205), "連續 ７ 天", font=f_h2, fill="#FFFFFF")
    d.text((185, 248), "透析日與非透析日皆量", font=f_sub_h2, fill="#E3F2FD")
    
    # 7 Days Calendar Row
    days = ["一", "二", "三", "四", "五", "六", "日"]
    active_checks = min(7, int(t / 0.45) + 1) if is_f1 else 7
    for idx, day in enumerate(days):
        dx = 80 + idx * 76
        dy = 310
        is_active = (idx < active_checks)
        bg_col = "#E8F5E9" if is_active else "#F5F5F5"
        border_col = "#4CAF50" if is_active else "#BDBDBD"
        d.rounded_rectangle([(dx, dy), (dx + 66, dy + 70)], radius=12, fill=bg_col, outline=border_col, width=2)
        d.text((dx + 20, dy + 8), day, font=ImageFont.truetype(font_bold, 22), fill="#1B5E20" if is_active else "#757575")
        if is_active:
            draw_checkmark(d, dx + 33, dy + 48, size=18, color="#2E7D32", width=4)
        else:
            d.text((dx + 26, dy + 40), "-", font=ImageFont.truetype(font_bold, 20), fill="#9E9E9E")
            
    # Highlight pill
    d.rounded_rectangle([(80, 400), (610, 448)], radius=12, fill="#E3F2FD", outline="#90CAF9", width=2)
    d.text((95, 412), "【每週規律】", font=f_badge, fill="#0D47A1")
    d.text((230, 412), "掌握每週血壓真實全貌", font=f_badge, fill="#1565C0")
    
    b1_text = "• 連續記錄一整週（透析日與非透析日）\n• 評估兩次透析間水份蓄積對血壓影響\n• 杜絕『白袍高血壓』或偶發波動誤判"
    draw_wrapped_text(d, b1_text, (85, 475), f_bullet, "#263238", max_width=520, line_spacing=14)
    
    # -------------------------------------------------------------
    # CARD 2: 2 每天 2 回 (x: 675 ~ 1245)
    # -------------------------------------------------------------
    c2_outline = "#2E7D32" if is_f2 else "#C8E6C9"
    c2_w = 5 if is_f2 else 3
    d.rounded_rectangle([(675, 185), (1245, 675)], radius=22, fill="#FFFFFF", outline=c2_outline, width=c2_w)
    d.rounded_rectangle([(675, 185), (1245, 290)], radius=22, fill="#2E7D32")
    
    c2_scale = (1.0 + 0.05 * math.sin(t * 8)) if is_f2 else 1.0
    r_cx2, r_cy2 = 740, 237
    rw2, rh2 = int(40 * c2_scale), int(35 * c2_scale)
    d.ellipse([(r_cx2 - rw2, r_cy2 - rh2), (r_cx2 + rw2, r_cy2 + rh2)], fill="#FFFFFF")
    d.text((r_cx2 - 15, r_cy2 - 31), "2", font=f_num, fill="#2E7D32")
    d.text((800, 205), "每天 ２ 回", font=f_h2, fill="#FFFFFF")
    d.text((800, 248), "晨起排尿後 ＆ 睡前量測", font=f_sub_h2, fill="#E8F5E9")
    
    # Morning Pill
    m_active = is_f2 and (t < 5.0)
    m_border = "#E65100" if m_active else "#FFA000"
    m_bw = 3 if m_active else 2
    d.rounded_rectangle([(695, 310), (1225, 385)], radius=15, fill="#FFF8E1", outline=m_border, width=m_bw)
    d.rounded_rectangle([(710, 322), (800, 372)], radius=8, fill="#FF8F00")
    d.text((720, 332), "早 晨", font=ImageFont.truetype(font_bold, 20), fill="#FFFFFF")
    d.text((815, 332), "晨起排尿後（空腹、未服降壓藥前）", font=ImageFont.truetype(font_bold, 20), fill="#E65100")
    
    # Evening Pill
    e_active = is_f2 and (t >= 5.0)
    e_border = "#4527A0" if e_active else "#7E57C2"
    e_bw = 3 if e_active else 2
    d.rounded_rectangle([(695, 400), (1225, 475)], radius=15, fill="#EDE7F6", outline=e_border, width=e_bw)
    d.rounded_rectangle([(710, 412), (800, 462)], radius=8, fill="#5E35B1")
    d.text((720, 422), "睡 前", font=ImageFont.truetype(font_bold, 20), fill="#FFFFFF")
    d.text((815, 422), "心情放鬆、就寢入睡前測量", font=ImageFont.truetype(font_bold, 20), fill="#4527A0")
    
    b2_text = "• 晨起量測：反映夜間與清晨血壓危險峰值\n• 睡前量測：確認全天血壓控制是否平穩\n• 注意：避開剛洗澡、剛運動或飲用濃茶後"
    draw_wrapped_text(d, b2_text, (700, 505), f_bullet, "#263238", max_width=520, line_spacing=14)
    
    # -------------------------------------------------------------
    # CARD 3: 2 每回 2 遍 (x: 1290 ~ 1860)
    # -------------------------------------------------------------
    c3_outline = "#6A1B9A" if is_f3 else "#E1BEE7"
    c3_w = 5 if is_f3 else 3
    d.rounded_rectangle([(1290, 185), (1860, 675)], radius=22, fill="#FFFFFF", outline=c3_outline, width=c3_w)
    d.rounded_rectangle([(1290, 185), (1860, 290)], radius=22, fill="#6A1B9A")
    
    c3_scale = (1.0 + 0.05 * math.sin(t * 8)) if is_f3 else 1.0
    r_cx3, r_cy3 = 1355, 237
    rw3, rh3 = int(40 * c3_scale), int(35 * c3_scale)
    d.ellipse([(r_cx3 - rw3, r_cy3 - rh3), (r_cx3 + rw3, r_cy3 + rh3)], fill="#FFFFFF")
    d.text((r_cx3 - 15, r_cy3 - 31), "2", font=f_num, fill="#6A1B9A")
    d.text((1415, 205), "每回 ２ 遍", font=f_h2, fill="#FFFFFF")
    d.text((1415, 248), "間隔 1 分鐘取平均值", font=f_sub_h2, fill="#F3E5F5")
    
    # Sequence badges
    d.rounded_rectangle([(1310, 310), (1430, 375)], radius=12, fill="#F3E5F5", outline="#AB47BC", width=2)
    d.text((1328, 330), "第 1 遍", font=ImageFont.truetype(font_bold, 22), fill="#6A1B9A")
    
    d.text((1448, 328), "→", font=ImageFont.truetype(font_bold, 28), fill="#8E24AA")
    
    d.rounded_rectangle([(1485, 310), (1635, 375)], radius=12, fill="#EDE7F6", outline="#7E57C2", width=2)
    d.text((1498, 325), "間隔 1 分鐘", font=ImageFont.truetype(font_bold, 18), fill="#4527A0")
    d.text((1518, 348), "靜坐放鬆", font=ImageFont.truetype(font_bold, 16), fill="#5E35B1")
    
    d.text((1650, 328), "→", font=ImageFont.truetype(font_bold, 28), fill="#8E24AA")
    
    d.rounded_rectangle([(1690, 310), (1810, 375)], radius=12, fill="#F3E5F5", outline="#AB47BC", width=2)
    d.text((1708, 330), "第 2 遍", font=ImageFont.truetype(font_bold, 22), fill="#6A1B9A")
    
    # Average calculation pill
    d.rounded_rectangle([(1310, 400), (1840, 460)], radius=12, fill="#E8F5E9", outline="#4CAF50", width=2)
    d.text((1330, 416), "【精準關鍵】", font=f_badge, fill="#1B5E20")
    d.text((1465, 416), "取兩遍平均值，據實記錄！", font=f_badge, fill="#2E7D32")
    
    b3_text = "• 第一次量測常因情緒或坐姿未定而偏高\n• 稍作深呼吸，間隔 1 分鐘再量第二次\n• 若兩次差距 ＞ 5 mmHg，可量第三次取平均"
    draw_wrapped_text(d, b3_text, (1310, 485), f_bullet, "#263238", max_width=520, line_spacing=12)
    
    # -------------------------------------------------------------
    # BOTTOM CARD: Posture + Target Blood Pressure + Logbook
    # -------------------------------------------------------------
    b_outline = "#0D47A1" if is_f4 else "#90CAF9"
    b_border_w = 4 if is_f4 else 2
    d.rounded_rectangle([(60, 695), (1860, 955)], radius=22, fill="#FFFFFF", outline=b_outline, width=b_border_w)
    
    # 1. Left Grandmother illustration (sitting properly)
    p_scale = (1.0 + 0.02 * math.sin(t * 3)) if is_f4 else 1.0
    pw, ph = int(260 * p_scale), int(240 * p_scale)
    cur_posture = posture_base.resize((pw, ph), Image.Resampling.LANCZOS)
    frame.paste(cur_posture, (75 - (pw - 260) // 2, 705 - (ph - 240) // 2), cur_posture)
    
    # 2. Middle Content (Target BP & Posture Rules)
    t_fill = "#E8F5E9" if is_f4 else "#F1F8E9"
    t_outline = "#2E7D32" if is_f4 else "#66BB6A"
    d.rounded_rectangle([(350, 712), (1540, 772)], radius=15, fill=t_fill, outline=t_outline, width=3 if is_f4 else 2)
    d.text((370, 725), "★ 成大透析室居家控制目標：", font=f_target, fill="#1B5E20")
    d.text((750, 723), "收縮壓 120～135 mmHg  /  舒張壓 60～80 mmHg", font=ImageFont.truetype(font_bold, 30), fill="#C62828")
    
    # Posture guidelines
    p_txt = "【量測要訣】 靜坐5分鐘、背靠椅背、雙腳平放不翹腳、壓脈帶與心臟同高、量測過程勿交談。\n【回診叮嚀】 門診或透析時請務必攜帶『血壓紀錄本』，醫師才能精準調整降壓藥物與乾體重！"
    draw_wrapped_text(d, p_txt, (360, 790), f_target_sub, "#263238", max_width=1160, line_spacing=12)
    
    # 3. Right Logbook illustration
    if is_f4:
        lb_pulse = 1.0 + 0.05 * math.sin(t * 6)
    else:
        lb_pulse = 1.0
    cur_lb_w = int(260 * lb_pulse)
    cur_lb_h = int(230 * lb_pulse)
    cur_lb = logbook_base.resize((cur_lb_w, cur_lb_h), Image.Resampling.LANCZOS)
    frame.paste(cur_lb, (1570 - (cur_lb_w - 260) // 2, 715 - (cur_lb_h - 230) // 2), cur_lb)
    
    # -------------------------------------------------------------
    # Bottom Subtitle Capsule
    # -------------------------------------------------------------
    sub_txt = get_subtitle(t)
    sub_bbox = d.textbbox((0, 0), sub_txt, font=f_sub)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_h = sub_bbox[3] - sub_bbox[1]
    
    pad_x, pad_y = 35, 12
    box_x1 = (WIDTH - sub_w) // 2 - pad_x
    box_x2 = (WIDTH + sub_w) // 2 + pad_x
    box_y1 = 980
    box_y2 = box_y1 + sub_h + pad_y * 2
    
    d.rounded_rectangle([(box_x1, box_y1), (box_x2, box_y2)], radius=20, fill="#0A387E")
    d.text(((WIDTH - sub_w) // 2, box_y1 + pad_y), sub_txt, font=f_sub, fill="#FFFFFF")
    
    # Send frame
    proc.stdin.write(frame.tobytes())
    
    if frame_idx % 60 == 0:
        print(f"Rendered frame {frame_idx}/{TOTAL_FRAMES} ({(frame_idx/TOTAL_FRAMES)*100:.1f}%)")

proc.stdin.close()
proc.wait()
print("\n=== Scene 4 Rendered Successfully! ===")
print("Output:", out_mp4)
