import os
import sys
import subprocess
import shutil
import math
from PIL import Image, ImageDraw, ImageFont

base_dir = r"C:\AI\影片製作_透析高血壓衛教"
audio_dir = os.path.join(base_dir, "audio")
slides_dir = os.path.join(base_dir, "slides")
sub_dir = os.path.join(base_dir, "subtitles")
out_dir = os.path.join(base_dir, "output")

for d in [audio_dir, slides_dir, sub_dir, out_dir]:
    os.makedirs(d, exist_ok=True)

font_bold = r"C:\Windows\Fonts\msjhbd.ttc"
font_regular = r"C:\Windows\Fonts\msjh.ttc"

# Reusable base canvas with strictly ONLY 分機 2591
def create_base_canvas():
    im = Image.new("RGB", (1920, 1080), "#F4F7FB")
    draw = ImageDraw.Draw(im)
    
    # Top banner bar (Deep Medical Blue)
    draw.rectangle([(0, 0), (1920, 110)], fill="#0D47A1")
    f_hosp = ImageFont.truetype(font_bold, 36)
    draw.text((70, 32), "國立成功大學醫學院附設醫院 血液透析室", font=f_hosp, fill="#FFFFFF")
    
    # Tag right
    f_tag = ImageFont.truetype(font_bold, 28)
    draw.rounded_rectangle([(1560, 24), (1850, 86)], radius=31, fill="#1976D2")
    draw.text((1590, 37), "透析衛教短片", font=f_tag, fill="#FFFFFF")
    
    # Bottom footer bar - ONLY 分機 2591
    draw.rectangle([(0, 1000), (1920, 1080)], fill="#0A387E")
    f_foot = ImageFont.truetype(font_bold, 25)
    draw.text((70, 1024), "成大醫院血液透析室 關心您 | 諮詢專線：(06) 235-3535 分機 2591", font=f_foot, fill="#E3F2FD")
    return im, draw

def wrap_text(text, font, max_width, draw):
    lines = []
    paragraphs = text.split("\n")
    for para in paragraphs:
        if not para:
            lines.append("")
            continue
        current_line = ""
        for char in para:
            test_line = current_line + char
            bbox = draw.textbbox((0, 0), test_line, font=font)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)
    return lines

def draw_wrapped_text(draw, text, xy, font, fill, max_width, line_spacing=10):
    lines = wrap_text(text, font, max_width, draw)
    x, y = xy
    cur_y = y
    for line in lines:
        draw.text((x, cur_y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line if line else "A", font=font)
        h = bbox[3] - bbox[1]
        cur_y += h + line_spacing
    return cur_y

# Helper drawing functions for graphics & icons (NO EMOJIS TO PREVENT SQUARES)
def draw_heart_icon(draw, cx, cy, size, color):
    r = size // 2
    draw.ellipse([(cx - size, cy - size), (cx, cy)], fill=color)
    draw.ellipse([(cx, cy - size), (cx + size, cy)], fill=color)
    draw.polygon([(cx - size, cy - size // 3), (cx + size, cy - size // 3), (cx, cy + size)], fill=color)

def draw_pill_icon(draw, cx, cy, w, h, col1, col2):
    x1, y1 = cx - w//2, cy - h//2
    x2, y2 = cx + w//2, cy + h//2
    draw.rectangle([(x1, y1 + h//4), (x2, y2 - h//4)], fill=col1)
    draw.ellipse([(x1, y1), (x2, y1 + h//2)], fill=col1)
    draw.rectangle([(x1, cy), (x2, y2 - h//4)], fill=col2)
    draw.ellipse([(x1, y2 - h//2), (x2, y2)], fill=col2)
    draw.line([(x1, cy), (x2, cy)], fill="#FFFFFF", width=3)

def draw_water_bottle(draw, x, y, w, h, fill_pct=0.85, label="1000 cc"):
    cap_w, cap_h = int(w * 0.4), int(h * 0.08)
    neck_w, neck_h = int(w * 0.3), int(h * 0.08)
    body_y = y + cap_h + neck_h
    body_h = h - cap_h - neck_h
    
    draw.rounded_rectangle([(x + (w - cap_w)//2, y), (x + (w + cap_w)//2, y + cap_h)], radius=5, fill="#1565C0")
    draw.rectangle([(x + (w - neck_w)//2, y + cap_h), (x + (w + neck_w)//2, body_y)], fill="#90CAF9")
    draw.rounded_rectangle([(x, body_y), (x + w, y + h)], radius=18, fill="#E3F2FD", outline="#1E88E5", width=3)
    water_h = int(body_h * fill_pct)
    water_top = (y + h) - water_h
    draw.rounded_rectangle([(x + 4, water_top), (x + w - 4, y + h - 4)], radius=15, fill="#42A5F5")
    draw.arc([(x + 8, water_top - 6), (x + w - 8, water_top + 10)], 0, 180, fill="#FFFFFF", width=3)
    for i in range(1, 4):
        mark_y = body_y + int(body_h * (i / 4.0))
        draw.line([(x + 8, mark_y), (x + 28, mark_y)], fill="#0D47A1", width=2)
    f_lbl = ImageFont.truetype(font_bold, 22)
    bbox = draw.textbbox((0, 0), label, font=f_lbl)
    lw = bbox[2] - bbox[0]
    draw.text((x + (w - lw)//2, y + h - 45), label, font=f_lbl, fill="#FFFFFF")

def draw_balloon(draw, cx, cy, size, color, string_len=60, deflated=False):
    if not deflated:
        draw.ellipse([(cx - size, cy - int(size * 1.2)), (cx + size, cy + int(size * 0.9))], fill=color)
        draw.ellipse([(cx - int(size*0.6), cy - int(size*0.9)), (cx - int(size*0.3), cy - int(size*0.4))], fill="#FFFFFF")
        draw.polygon([(cx - 12, cy + int(size * 0.9)), (cx + 12, cy + int(size * 0.9)), (cx, cy + int(size * 0.9) + 16)], fill=color)
        draw.line([(cx, cy + int(size*0.9) + 16), (cx - 10, cy + int(size*0.9) + string_len)], fill="#78909C", width=3)
    else:
        draw.ellipse([(cx - int(size*0.6), cy - int(size*0.5)), (cx + int(size*0.6), cy + int(size*0.5))], fill=color)
        draw.polygon([(cx - 10, cy + int(size*0.5)), (cx + 10, cy + int(size*0.5)), (cx, cy + int(size*0.5) + 14)], fill=color)
        draw.line([(cx, cy + int(size*0.5) + 14), (cx + 12, cy + int(size*0.5) + string_len)], fill="#78909C", width=3)

def draw_warning_sign(draw, cx, cy, r):
    pts = []
    for i in range(8):
        ang = math.radians(i * 45 + 22.5)
        pts.append((cx + int(r * math.cos(ang)), cy + int(r * math.sin(ang))))
    draw.polygon(pts, fill="#D32F2F", outline="#B71C1C")
    inner_pts = []
    for i in range(8):
        ang = math.radians(i * 45 + 22.5)
        inner_pts.append((cx + int((r-8) * math.cos(ang)), cy + int((r-8) * math.sin(ang))))
    draw.polygon(inner_pts, fill="#D32F2F", outline="#FFFFFF")
    lw = max(10, r // 4)
    draw.line([(cx - r//2, cy - r//2), (cx + r//2, cy + r//2)], fill="#FFFFFF", width=lw)
    draw.line([(cx - r//2, cy + r//2), (cx + r//2, cy - r//2)], fill="#FFFFFF", width=lw)

def draw_gauge_meter(draw, cx, cy, r, val_angle_deg, low_color="#42A5F5", good_color="#4CAF50", high_color="#E53935"):
    bbox = [(cx - r, cy - r), (cx + r, cy + r)]
    draw.arc(bbox, 140, 200, fill=low_color, width=22)
    draw.arc(bbox, 200, 310, fill=good_color, width=22)
    draw.arc(bbox, 310, 400, fill=high_color, width=22)
    rad = math.radians(val_angle_deg)
    nx = cx + int((r - 20) * math.cos(rad))
    ny = cy + int((r - 20) * math.sin(rad))
    draw.line([(cx, cy), (nx, ny)], fill="#212121", width=6)
    draw.ellipse([(cx - 14, cy - 14), (cx + 14, cy + 14)], fill="#212121")

def draw_hospital_icon(draw, cx, cy, size, color="#D32F2F"):
    # Hospital building with cross
    w, h = size, int(size * 0.9)
    draw.rectangle([(cx - w//2, cy - h//2), (cx + w//2, cy + h//2)], fill="#FFFFFF", outline=color, width=3)
    # Cross
    cw = max(4, size // 8)
    ch = int(size * 0.45)
    draw.rectangle([(cx - cw, cy - ch//2), (cx + cw, cy + ch//2)], fill=color)
    draw.rectangle([(cx - ch//2, cy - cw), (cx + ch//2, cy + cw)], fill=color)

def draw_home_icon(draw, cx, cy, size, color="#2E7D32"):
    # House roof and body
    w = size
    roof = [(cx, cy - size//2), (cx - w//2 - 6, cy), (cx + w//2 + 6, cy)]
    draw.polygon(roof, fill=color)
    draw.rectangle([(cx - w//2 + 4, cy), (cx + w//2 - 4, cy + size//2)], fill="#FFFFFF", outline=color, width=3)
    # Door
    dw, dh = size // 4, size // 3
    draw.rectangle([(cx - dw//2, cy + size//2 - dh), (cx + dw//2, cy + size//2)], fill=color)

def draw_lemon_icon(draw, cx, cy, r):
    # Lemon slice
    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill="#FBC02D", outline="#F57F17", width=3)
    inner_r = r - 8
    draw.ellipse([(cx - inner_r, cy - inner_r), (cx + inner_r, cy + inner_r)], fill="#FFF9C4")
    # Segments
    for i in range(8):
        ang = math.radians(i * 45)
        x2 = cx + int((inner_r - 4) * math.cos(ang))
        y2 = cy + int((inner_r - 4) * math.sin(ang))
        draw.line([(cx, cy), (x2, y2)], fill="#FFFFFF", width=2)

def draw_ice_icon(draw, cx, cy, size):
    # Ice cube
    draw.rectangle([(cx - size//2, cy - size//2), (cx + size//2, cy + size//2)], fill="#B3E5FC", outline="#0288D1", width=3)
    draw.line([(cx - size//2, cy - size//4), (cx + size//4, cy - size//2)], fill="#FFFFFF", width=3)
    draw.line([(cx - size//4, cy + size//2), (cx + size//2, cy - size//4)], fill="#FFFFFF", width=3)

def draw_mint_icon(draw, cx, cy, size):
    # Mint leaf
    draw.ellipse([(cx - size//2, cy - size//3), (cx + size//2, cy + size//3)], fill="#81C784", outline="#2E7D32", width=3)
    draw.line([(cx - size//2 + 5, cy), (cx + size//2 - 5, cy)], fill="#2E7D32", width=2)

def draw_water_drop_icon(draw, cx, cy, size):
    # Water droplet
    draw.ellipse([(cx - size//2, cy - size//4), (cx + size//2, cy + size//2)], fill="#4FC3F7")
    draw.polygon([(cx - size//3, cy), (cx + size//3, cy), (cx, cy - size//2)], fill="#4FC3F7")

def draw_shield_icon(draw, cx, cy, size, color="#1976D2"):
    pts = [
        (cx - size//2, cy - size//2),
        (cx + size//2, cy - size//2),
        (cx + size//2, cy + size//8),
        (cx, cy + size//2),
        (cx - size//2, cy + size//8)
    ]
    draw.polygon(pts, fill=color)
    inner_pts = [
        (cx - size//2 + 6, cy - size//2 + 6),
        (cx + size//2 - 6, cy - size//2 + 6),
        (cx + size//2 - 6, cy + size//8 - 2),
        (cx, cy + size//2 - 8),
        (cx - size//2 + 6, cy + size//8 - 2)
    ]
    draw.polygon(inner_pts, fill="#FFFFFF")
    draw_heart_icon(draw, cx, cy + 4, size//5, color)

def draw_clock_icon(draw, cx, cy, r, color="#D32F2F"):
    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill="#FFFFFF", outline=color, width=4)
    # Clock hands
    draw.line([(cx, cy), (cx, cy - int(r * 0.6))], fill=color, width=4)
    draw.line([(cx, cy), (cx + int(r * 0.45), cy)], fill=color, width=3)
    draw.ellipse([(cx - 4, cy - 4), (cx + 4, cy + 4)], fill=color)

def draw_arrow_right(draw, cx, cy, length, color="#6A1B9A"):
    w = length // 2
    draw.line([(cx - w, cy), (cx + w, cy)], fill=color, width=5)
    draw.polygon([(cx + w + 10, cy), (cx + w - 5, cy - 10), (cx + w - 5, cy + 10)], fill=color)

print("Building 10 Redesigned Visual Slides (v3)...")

# ==============================================================================
# SLIDE 1: COVER SLIDE
# ==============================================================================
im, d = create_base_canvas()
f_t = ImageFont.truetype(font_bold, 30)
d.rounded_rectangle([(70, 150), (450, 210)], radius=15, fill="#E3F2FD")
d.text((95, 163), "成大醫院透析高血壓專題", font=f_t, fill="#0D47A1")

f_m = ImageFont.truetype(font_bold, 70)
d.text((70, 240), "護腎保心，血壓穩妥當！", font=f_m, fill="#0D47A1")

f_sub = ImageFont.truetype(font_bold, 40)
d.text((70, 345), "血液透析病友 3 分鐘控壓自我照護秘笈", font=f_sub, fill="#37474F")

cards = [
    ("7 2 2", "居家血壓量測", "連續 7 天・早晚量・各 2 遍\n在熟悉家中量測最真實", "#1976D2", "meter"),
    ("< 5%", "體重水分管理", "兩次洗腎增加 < 乾體重 5%\n嚴格限鹽、嚴禁食用低鈉鹽", "#2E7D32", "scale"),
    ("按時服", "降壓用藥安全", "按時服藥不擅停\n洗腎當日遵從醫師指示", "#C2185B", "pill")
]
for i, (tag, title, desc, col, icon_type) in enumerate(cards):
    x1 = 70 + i * 600
    x2 = x1 + 560
    y1 = 440
    y2 = 940
    d.rounded_rectangle([(x1, y1), (x2, y2)], radius=25, fill="#FFFFFF", outline=col, width=3)
    d.rounded_rectangle([(x1, y1), (x2, y1 + 130)], radius=25, fill=col)
    
    draw_cx = x1 + 100
    draw_cy = y1 + 65
    d.ellipse([(draw_cx - 45, draw_cy - 45), (draw_cx + 45, draw_cy + 45)], fill="#FFFFFF")
    f_tag = ImageFont.truetype(font_bold, 30)
    tb = d.textbbox((0, 0), tag, font=f_tag)
    d.text((draw_cx - (tb[2]-tb[0])//2, draw_cy - (tb[3]-tb[1])//2 - 2), tag, font=f_tag, fill=col)
    
    f_ct = ImageFont.truetype(font_bold, 36)
    d.text((x1 + 175, y1 + 45), title, font=f_ct, fill="#FFFFFF")
    
    mid_y = y1 + 240
    if icon_type == "meter":
        draw_gauge_meter(d, (x1 + x2)//2, mid_y + 30, 80, 240)
        f_gt = ImageFont.truetype(font_bold, 28)
        d.text(((x1+x2)//2 - 80, mid_y + 85), "居家放鬆量測", font=f_gt, fill="#1976D2")
    elif icon_type == "scale":
        sx = (x1 + x2)//2
        sy = mid_y + 40
        d.rounded_rectangle([(sx - 80, sy - 30), (sx + 80, sy + 70)], radius=15, fill="#E8F5E9", outline="#2E7D32", width=3)
        d.ellipse([(sx - 40, sy - 15), (sx + 40, sy + 45)], fill="#FFFFFF", outline="#2E7D32", width=2)
        f_st = ImageFont.truetype(font_bold, 28)
        d.text((sx - 35, sy + 5), "< 5%", font=f_st, fill="#2E7D32")
    elif icon_type == "pill":
        sx = (x1 + x2)//2
        sy = mid_y + 40
        draw_pill_icon(d, sx - 35, sy, 35, 75, "#E91E63", "#F8BBD0")
        draw_heart_icon(d, sx + 45, sy, 28, "#E91E63")

    f_cd = ImageFont.truetype(font_bold, 30)
    draw_wrapped_text(d, desc, (x1 + 40, y1 + 370), f_cd, "#37474F", max_width=480, line_spacing=15)

im.save(os.path.join(slides_dir, "slide_01.png"))
print("Saved slide_01.png")

# ==============================================================================
# SLIDE 2: GENERAL VS DIALYSIS BP
# ==============================================================================
im, d = create_base_canvas()
f_t = ImageFont.truetype(font_bold, 50)
d.text((70, 145), "【核心觀念】一般人 vs 洗腎病友的血壓大不同", font=f_t, fill="#0D47A1")

# Left Box: General Population
d.rounded_rectangle([(70, 240), (920, 780)], radius=25, fill="#FFFFFF", outline="#90CAF9", width=3)
d.rounded_rectangle([(70, 240), (920, 350)], radius=25, fill="#1565C0")
f_bt = ImageFont.truetype(font_bold, 38)
d.text((120, 270), "一般成年人 (國健署標準)", font=f_bt, fill="#FFFFFF")

draw_gauge_meter(d, 495, 470, 75, 230)
f_num = ImageFont.truetype(font_bold, 54)
d.text((270, 580), "< 120 / 80 mmHg", font=f_num, fill="#1565C0")

f_desc = ImageFont.truetype(font_bold, 30)
desc_gen = "• 血管彈性良好健康族群\n• 追求平穩、預防長期動脈硬化"
draw_wrapped_text(d, desc_gen, (120, 670), f_desc, "#455A64", max_width=720, line_spacing=12)

# Right Box: Dialysis Patients
d.rounded_rectangle([(970, 240), (1850, 780)], radius=25, fill="#FFFFFF", outline="#81C784", width=3)
d.rounded_rectangle([(970, 240), (1850, 350)], radius=25, fill="#2E7D32")
d.text((1020, 270), "血液透析病友 (成大/腎醫會標準)", font=f_bt, fill="#FFFFFF")

# Target Block 1: Clinic
d.rounded_rectangle([(1010, 380), (1810, 500)], radius=18, fill="#F1F8E9", outline="#A5D6A7", width=2)
draw_hospital_icon(d, 1055, 440, 44, color="#2E7D32")
f_t1 = ImageFont.truetype(font_bold, 32)
d.text((1095, 420), "洗腎前診間血壓：", font=f_t1, fill="#2E7D32")
f_t1_num = ImageFont.truetype(font_bold, 44)
d.text((1400, 420), "< 140 / 90 mmHg", font=f_t1_num, fill="#1B5E20")

# Target Block 2: Home
d.rounded_rectangle([(1010, 520), (1810, 640)], radius=18, fill="#E8F5E9", outline="#81C784", width=2)
draw_home_icon(d, 1055, 580, 44, color="#1B5E20")
d.text((1095, 560), "透析間居家血壓：", font=f_t1, fill="#1B5E20")
d.text((1400, 560), "120～135 / 60～80", font=f_t1_num, fill="#2E7D32")

desc_dia = "• 洗腎血管多有鈣化硬化，體液波動大\n• 警訊：血壓過低 (< 120) 易引發心肌缺氧！"
draw_wrapped_text(d, desc_dia, (1020, 670), f_desc, "#37474F", max_width=780, line_spacing=12)

# Bottom alert
d.rounded_rectangle([(70, 815), (1850, 945)], radius=20, fill="#FFF8E1", outline="#FFE082", width=3)
draw_cx = 120
draw_cy = 880
d.ellipse([(draw_cx - 30, draw_cy - 30), (draw_cx + 30, draw_cy + 30)], fill="#FFA000")
d.text((draw_cx - 8, draw_cy - 22), "!", font=ImageFont.truetype(font_bold, 36), fill="#FFFFFF")

f_alt = ImageFont.truetype(font_bold, 34)
alert_text = "重要醫學叮嚀：洗腎病友血壓「不是越低越好」！\n維持平穩最適區間，才能保護心臟大腦不缺氧！"
draw_wrapped_text(d, alert_text, (180, 835), f_alt, "#B76E00", max_width=1620, line_spacing=8)

im.save(os.path.join(slides_dir, "slide_02.png"))
print("Saved slide_02.png")

# ==============================================================================
# SLIDE 3: WHY HOME BP IS BETTER
# ==============================================================================
im, d = create_base_canvas()
d.text((70, 145), "【第一招】為什麼「在家量」比在洗腎室更準確？", font=f_t, fill="#0D47A1")

# Left Box: Dialysis Clinic
d.rounded_rectangle([(70, 240), (920, 780)], radius=25, fill="#FFFFFF", outline="#EF9A9A", width=3)
d.rounded_rectangle([(70, 240), (920, 350)], radius=25, fill="#C62828")
draw_hospital_icon(d, 120, 295, 45, color="#FFFFFF")
d.text((160, 270), "【洗腎室量測的限制】", font=f_bt, fill="#FFFFFF")

d.rounded_rectangle([(120, 370), (870, 480)], radius=15, fill="#FFEBEE")
pts_stress = [(150, 425), (200, 425), (220, 390), (240, 460), (260, 400), (280, 440), (310, 425), (360, 425)]
d.line(pts_stress, fill="#D32F2F", width=4)
f_warn_t = ImageFont.truetype(font_bold, 30)
d.text((380, 405), "「白袍效應」緊張飆高！", font=f_warn_t, fill="#C62828")

clinic_text = "• 進醫院容易心情焦慮、緊張使血壓假性上升\n• 洗腎前後脫水讓體液驟變，數值起伏劇烈\n• 偶發性量測無法代表平日真實血壓"
draw_wrapped_text(d, clinic_text, (120, 510), f_desc, "#37474F", max_width=740, line_spacing=18)

# Right Box: Home BP
d.rounded_rectangle([(970, 240), (1850, 780)], radius=25, fill="#FFFFFF", outline="#A5D6A7", width=3)
d.rounded_rectangle([(970, 240), (1850, 350)], radius=25, fill="#2E7D32")
draw_home_icon(d, 1020, 295, 45, color="#FFFFFF")
d.text((1060, 270), "【居家測量 (HBPM) 的優勢】", font=f_bt, fill="#FFFFFF")

d.rounded_rectangle([(1020, 370), (1770, 480)], radius=15, fill="#E8F5E9")
pts_calm = [(1050, 425), (1120, 425), (1140, 405), (1160, 445), (1180, 425), (1250, 425)]
d.line(pts_calm, fill="#2E7D32", width=4)
d.text((1280, 405), "居家放鬆，數值最真實！", font=f_warn_t, fill="#2E7D32")

home_text = "• 在熟悉放鬆環境測量，排除外在壓力干擾\n• 醫學研究證實：居家血壓與心臟健康及存活率關聯最高！\n• 提供醫師最可靠依據，精準調整降壓藥與乾體重"
draw_wrapped_text(d, home_text, (1020, 510), f_desc, "#263238", max_width=740, line_spacing=18)

# Bottom banner
d.rounded_rectangle([(70, 815), (1850, 945)], radius=20, fill="#E3F2FD", outline="#90CAF9", width=2)
f_bot = ImageFont.truetype(font_bold, 34)
b_text = "成大醫院與各國指引一致推崇：透析病友應以「居家血壓」作為常態監測金標準！"
draw_wrapped_text(d, b_text, (120, 855), f_bot, "#0D47A1", max_width=1650, line_spacing=6)

im.save(os.path.join(slides_dir, "slide_03.png"))
print("Saved slide_03.png")

# ==============================================================================
# SLIDE 4: 722 PROTOCOL (CLEAN ARROWS & NO SQUARES)
# ==============================================================================
im, d = create_base_canvas()
d.text((70, 145), "【第一招】居家血壓量測黃金口訣：「7 2 2 原則」", font=f_t, fill="#0D47A1")

p722_cards = [
    {
        "num": "7",
        "title": "連續 7 天",
        "sub": "透析日與非透析日",
        "bullets": "• 連續記錄一整週\n• 透析日與平日皆量\n• 掌握血壓每週波動規律",
        "color": "#1565C0",
        "bg": "#E3F2FD",
        "icon": "calendar"
    },
    {
        "num": "2",
        "title": "每天 2 回",
        "sub": "晨起排尿後・睡前",
        "bullets": "• 第一回：晨起排尿後\n  (未吃早餐、未服藥前)\n• 第二回：上床就寢前",
        "color": "#2E7D32",
        "bg": "#E8F5E9",
        "icon": "sunmoon"
    },
    {
        "num": "2",
        "title": "每回 2 遍",
        "sub": "間隔1分鐘・取平均",
        "bullets": "• 每次量測間隔 1 分鐘\n• 兩次數值填入記錄本\n• 計算平均值作為依據",
        "color": "#6A1B9A",
        "bg": "#F3E5F5",
        "icon": "repeat"
    }
]

for i, c in enumerate(p722_cards):
    x1 = 70 + i * 600
    x2 = x1 + 560
    y1 = 235
    y2 = 740
    d.rounded_rectangle([(x1, y1), (x2, y2)], radius=25, fill="#FFFFFF", outline=c["color"], width=3)
    d.rounded_rectangle([(x1, y1), (x2, y1 + 130)], radius=25, fill=c["color"])
    
    nb_cx = x1 + 80
    nb_cy = y1 + 65
    d.ellipse([(nb_cx - 40, nb_cy - 40), (nb_cx + 40, nb_cy + 40)], fill="#FFFFFF")
    f_bignum = ImageFont.truetype(font_bold, 50)
    tb = d.textbbox((0, 0), c["num"], font=f_bignum)
    d.text((nb_cx - (tb[2]-tb[0])//2, nb_cy - (tb[3]-tb[1])//2 - 4), c["num"], font=f_bignum, fill=c["color"])
    
    f_t7 = ImageFont.truetype(font_bold, 36)
    d.text((x1 + 140, y1 + 30), c["title"], font=f_t7, fill="#FFFFFF")
    f_sub7 = ImageFont.truetype(font_regular, 24)
    d.text((x1 + 140, y1 + 80), c["sub"], font=f_sub7, fill="#FFFFFF")
    
    iy = y1 + 150
    d.rounded_rectangle([(x1 + 25, iy), (x2 - 25, iy + 75)], radius=12, fill=c["bg"])
    if c["icon"] == "calendar":
        for bx in range(7):
            cb_x = x1 + 45 + bx * 68
            d.rounded_rectangle([(cb_x, iy + 15), (cb_x + 50, iy + 60)], radius=6, fill="#FFFFFF", outline=c["color"], width=2)
            d.text((cb_x + 10, iy + 22), ["一","二","三","四","五","六","日"][bx], font=ImageFont.truetype(font_bold, 20), fill=c["color"])
    elif c["icon"] == "sunmoon":
        d.ellipse([(x1 + 120, iy + 18), (x1 + 160, iy + 58)], fill="#FFA000")
        d.text((x1 + 175, iy + 22), "早晨", font=ImageFont.truetype(font_bold, 24), fill="#2E7D32")
        d.ellipse([(x1 + 320, iy + 18), (x1 + 360, iy + 58)], fill="#5C6BC0")
        d.text((x1 + 375, iy + 22), "睡前", font=ImageFont.truetype(font_bold, 24), fill="#2E7D32")
    elif c["icon"] == "repeat":
        d.text((x1 + 60, iy + 22), "第 1 次", font=ImageFont.truetype(font_bold, 24), fill="#6A1B9A")
        draw_arrow_right(d, x1 + 225, iy + 36, 40, color="#8E24AA")
        d.text((x1 + 270, iy + 24), "(隔1分)", font=ImageFont.truetype(font_bold, 20), fill="#8E24AA")
        draw_arrow_right(d, x1 + 395, iy + 36, 40, color="#8E24AA")
        d.text((x1 + 440, iy + 22), "第 2 次", font=ImageFont.truetype(font_bold, 24), fill="#6A1B9A")

    f_b7 = ImageFont.truetype(font_bold, 28)
    draw_wrapped_text(d, c["bullets"], (x1 + 35, y1 + 250), f_b7, "#263238", max_width=490, line_spacing=14)

# Bottom Target
d.rounded_rectangle([(70, 765), (1850, 955)], radius=22, fill="#FFFFFF", outline="#CFD8DC", width=2)
f_gt = ImageFont.truetype(font_bold, 36)
d.text((110, 790), "★ 成大透析室居家控制目標：收縮壓 120～135 mmHg / 舒張壓 60～80 mmHg", font=f_gt, fill="#C62828")

f_gd = ImageFont.truetype(font_bold, 28)
tip_str = "• 量測要訣：靜坐5分鐘、背靠椅、雙腳著地不翹腳、壓脈帶與心臟同高、不說話。\n• 回診叮嚀：務必攜帶『血壓紀錄本』，醫師才能依據精準調整降壓藥與乾體重！"
draw_wrapped_text(d, tip_str, (110, 850), f_gd, "#455A64", max_width=1680, line_spacing=10)

im.save(os.path.join(slides_dir, "slide_04.png"))
print("Saved slide_04.png")

# ==============================================================================
# SLIDE 5: BALLOON METAPHOR
# ==============================================================================
im, d = create_base_canvas()
d.text((70, 145), "【第二招】心臟像氣球：認識「乾體重」與體液平衡", font=f_t, fill="#0D47A1")

# Left: Overfilled Balloon
d.rounded_rectangle([(70, 240), (920, 760)], radius=25, fill="#FFFFFF", outline="#EF9A9A", width=3)
d.rounded_rectangle([(70, 240), (920, 350)], radius=25, fill="#D32F2F")
d.text((120, 270), "【喝水過多：氣球過度吹大】", font=f_bt, fill="#FFFFFF")

draw_balloon(d, 495, 490, 85, "#E53935", string_len=40)
d.ellipse([(430, 420), (445, 445)], fill="#42A5F5")
d.ellipse([(540, 400), (555, 425)], fill="#42A5F5")

b_text1 = "• 體內水份滯留，血管被水撐緊\n• 血壓直線飆高 (容量型高血壓)\n• 心肌彈性疲乏，長期導致心臟肥大與衰竭！"
draw_wrapped_text(d, b_text1, (110, 600), f_desc, "#263238", max_width=750, line_spacing=12)

# Right: Deflated Balloon
d.rounded_rectangle([(970, 240), (1850, 760)], radius=25, fill="#FFFFFF", outline="#FFE082", width=3)
d.rounded_rectangle([(970, 240), (1850, 350)], radius=25, fill="#F57C00")
d.text((1020, 270), "【脫水過急：氣球快速扁縮】", font=f_bt, fill="#FFFFFF")

draw_balloon(d, 1410, 490, 60, "#FB8C00", string_len=40, deflated=True)
pts_lt = [(1480, 440), (1505, 465), (1495, 475), (1520, 505), (1490, 495), (1498, 480)]
d.polygon(pts_lt, fill="#E53935")

b_text2 = "• 洗腎短時間拉出過多水分\n• 脫水速度太快引發「透析中低血壓」\n• 導致劇烈肌肉抽筋、噁心嘔吐與心肌損傷！"
draw_wrapped_text(d, b_text2, (1010, 600), f_desc, "#263238", max_width=780, line_spacing=12)

# Bottom: Dry Weight balance
d.rounded_rectangle([(70, 790), (1850, 950)], radius=22, fill="#E8F5E9", outline="#81C784", width=3)
scx, scy = 140, 870
d.line([(scx - 40, scy + 10), (scx + 40, scy + 10)], fill="#2E7D32", width=6)
d.polygon([(scx, scy - 30), (scx - 15, scy + 10), (scx + 15, scy + 10)], fill="#2E7D32")
d.line([(scx, scy - 30), (scx, scy + 40)], fill="#1B5E20", width=4)
d.rectangle([(scx - 30, scy + 40), (scx + 30, scy + 50)], fill="#1B5E20")

f_dry = ImageFont.truetype(font_bold, 34)
d.text((220, 820), "★ 什麼是乾體重 (Dry Weight)？", font=f_dry, fill="#1B5E20")
f_dry_d = ImageFont.truetype(font_bold, 28)
d_text = "透析後身上沒有多餘水腫、肺部無積水、血壓平穩時的最適理想體重！"
draw_wrapped_text(d, d_text, (220, 875), f_dry_d, "#2E7D32", max_width=1580, line_spacing=6)

im.save(os.path.join(slides_dir, "slide_05.png"))
print("Saved slide_05.png")

# ==============================================================================
# SLIDE 6: 5% RULE WITH 3 BOTTLES & CLEAR < SYMBOL
# ==============================================================================
im, d = create_base_canvas()
d.text((70, 145), "【第二招】透析間體重增加「< 5% 黃金守則」", font=f_t, fill="#0D47A1")

# Top Big Banner with CLEAR < 5%
d.rounded_rectangle([(70, 230), (1850, 420)], radius=25, fill="#1976D2")
f_f_t = ImageFont.truetype(font_bold, 44)
d.text((120, 260), "黃金計算公式：兩次洗腎間體重增加 ＜ 乾體重的 5%", font=f_f_t, fill="#FFFFFF")
f_f_d = ImageFont.truetype(font_bold, 38)
d.text((120, 335), "【實例計算】：乾體重 60 公斤 × 5% = 最多增加 3 公斤", font=f_f_d, fill="#FFF176")

# Left Box: 3 Water Bottles Graphic
d.rounded_rectangle([(70, 450), (1050, 940)], radius=25, fill="#FFFFFF", outline="#90CAF9", width=3)
f_box_t = ImageFont.truetype(font_bold, 36)
d.text((110, 480), "【實物比喻】以 60 公斤為例：最多 3 大瓶水！", font=f_box_t, fill="#0D47A1")

bw, bh = 150, 280
for bi in range(3):
    bx = 140 + bi * 190
    by = 540
    draw_water_bottle(d, bx, by, bw, bh, fill_pct=0.9, label=f"第 {bi+1} 瓶 1000cc")

d.rounded_rectangle([(730, 560), (1010, 800)], radius=20, fill="#FFEBEE", outline="#D32F2F", width=3)
draw_warning_sign(d, 870, 630, 40)
f_stop = ImageFont.truetype(font_bold, 30)
d.text((760, 690), "【嚴格上限】", font=f_stop, fill="#D32F2F")
d.text((750, 735), "絕不能超過 3kg", font=ImageFont.truetype(font_bold, 26), fill="#C62828")

f_btm_tip = ImageFont.truetype(font_bold, 28)
d.text((110, 860), "• 每次走進洗腎室，體重絕不能超過 63 公斤！\n• 即使是隔兩天的週末長間隔，增加量依然要守住 5%！", font=f_btm_tip, fill="#37474F")

# Right Box: Weighing Tips
d.rounded_rectangle([(1100, 450), (1850, 940)], radius=25, fill="#FFFFFF", outline="#A5D6A7", width=3)
d.text((1140, 480), "【正確測量體重的三大原則】", font=f_box_t, fill="#2E7D32")

weigh_tips = [
    ("① 每日固定時間", "早晨起床上完洗手間後立刻測量最精準。"),
    ("② 固定同一台體重計", "避免不同磅秤產生數值偏差誤差。"),
    ("③ 穿著相似輕便衣服", "去除厚重外套、皮帶與鞋子重量。")
]
for wi, (wt, wd) in enumerate(weigh_tips):
    wy = 550 + wi * 125
    d.rounded_rectangle([(1140, wy), (1810, wy + 105)], radius=15, fill="#F1F8E9", outline="#C8E6C9", width=2)
    f_wt = ImageFont.truetype(font_bold, 30)
    d.text((1160, wy + 15), wt, font=f_wt, fill="#2E7D32")
    f_wd = ImageFont.truetype(font_bold, 26)
    d.text((1160, wy + 55), wd, font=f_wd, fill="#37474F")

im.save(os.path.join(slides_dir, "slide_06.png"))
print("Saved slide_06.png")

# ==============================================================================
# SLIDE 7: SALT & LOW-SODIUM WARNING
# ==============================================================================
im, d = create_base_canvas()
d.text((70, 145), "【第二招】控水先控鹽：嚴禁「低鈉鹽」致命陷阱！", font=f_t, fill="#0D47A1")

# Left Box: Salt Control
d.rounded_rectangle([(70, 240), (920, 940)], radius=25, fill="#FFFFFF", outline="#90CAF9", width=3)
d.rounded_rectangle([(70, 240), (920, 350)], radius=25, fill="#1565C0")
d.text((120, 270), "【為什麼要嚴格限制鹽分？】", font=f_bt, fill="#FFFFFF")

d.rounded_rectangle([(120, 380), (870, 500)], radius=18, fill="#E3F2FD")
d.ellipse([(150, 420), (220, 460)], fill="#B0BEC5", outline="#78909C", width=2)
d.line([(210, 440), (330, 440)], fill="#78909C", width=8)
d.polygon([(170, 420), (185, 400), (200, 420)], fill="#FFFFFF")
f_sp = ImageFont.truetype(font_bold, 32)
d.text((350, 415), "每日食鹽 ＜ 5 公克 (約 1 平匙)", font=f_sp, fill="#0D47A1")

salt_desc = "• 「吃太鹹」會強烈刺激大腦口渴中樞想狂灌水！\n• 想成功控水，關鍵第一步就是『控鹽』！\n• 必須嚴格避開的高鈉隱形地雷：\n   - 香腸、臘肉、肉鬆、醃製醬菜\n   - 泡麵、油麵、麵線、滷味\n   - 濃郁火鍋高湯、牛肉麵湯、沾醬醬油膏"
draw_wrapped_text(d, salt_desc, (120, 530), f_desc, "#263238", max_width=750, line_spacing=14)

# Right Box: DANGER LOW SODIUM SALT
d.rounded_rectangle([(970, 240), (1850, 940)], radius=25, fill="#FFF5F5", outline="#D32F2F", width=4)
d.rounded_rectangle([(970, 240), (1850, 350)], radius=25, fill="#D32F2F")
d.text((1020, 270), "【絕對禁忌：嚴禁食用低鈉鹽！】", font=f_bt, fill="#FFFFFF")

draw_warning_sign(d, 1070, 430, 50)
f_ws = ImageFont.truetype(font_bold, 36)
d.text((1150, 410), "市售低鈉鹽、美味鹽、薄鹽醬油", font=f_ws, fill="#B71C1C")

danger_desc = "• 致命原因：市售低鈉鹽是用『鉀』取代鈉！\n• 洗腎病友腎臟無排鉀功能，鉀離子迅速在體內累積！\n• 一旦血鉀過高，將直接引發：\n   - 嚴重四肢肌肉無力、呼吸困難\n   - 致死性惡性心律不整\n   - 心跳驟停與猝死！\n\n★ 護理師提醒：請安心使用「普通精鹽」，但減量烹調！"
draw_wrapped_text(d, danger_desc, (1020, 510), f_desc, "#B71C1C", max_width=780, line_spacing=14)

im.save(os.path.join(slides_dir, "slide_07.png"))
print("Saved slide_07.png")

# ==============================================================================
# SLIDE 8: 4 THIRST TIPS WITH CUSTOM DRAWN ICONS
# ==============================================================================
im, d = create_base_canvas()
d.text((70, 145), "【日常照護】口渴不灌水：護理師推薦 4 大解渴妙招", font=f_t, fill="#0D47A1")

tips_grid = [
    {
        "type": "lemon",
        "title": "含新鮮薄檸檬片",
        "desc": "切一小片新鮮檸檬含在口中，果酸能強烈刺激唾液分泌，生津止渴又不需要吞水！",
        "color": "#F57F17",
        "bg": "#FFFDE7"
    },
    {
        "type": "ice",
        "title": "自製小冰塊口含",
        "desc": "將開水製成彈珠大小的小冰塊含在嘴裡慢慢融化，緩解喉嚨乾燥，水分攝取極低！",
        "color": "#0288D1",
        "bg": "#E1F5FE"
    },
    {
        "type": "mint",
        "title": "嚼食無糖口香糖",
        "desc": "嚼無糖口香糖或酸味薄荷糖，促進唾液自然分泌，維持口腔濕潤並轉移喝水注意力！",
        "color": "#2E7D32",
        "bg": "#E8F5E9"
    },
    {
        "type": "water",
        "title": "冷開水漱口法",
        "desc": "覺得口乾時用冷開水漱漱口後吐掉，或是用棉花棒沾水濕潤雙唇，有效消除乾燥感！",
        "color": "#7B1FA2",
        "bg": "#F3E5F5"
    }
]

for i, tg in enumerate(tips_grid):
    col = i % 2
    row = i // 2
    x1 = 70 + col * 900
    x2 = x1 + 860
    y1 = 240 + row * 360
    y2 = y1 + 330
    
    d.rounded_rectangle([(x1, y1), (x2, y2)], radius=25, fill="#FFFFFF", outline=tg["color"], width=3)
    d.rounded_rectangle([(x1, y1), (x2, y1 + 100)], radius=25, fill=tg["color"])
    
    # Draw custom vector icon in header
    icx = x1 + 65
    icy = y1 + 50
    if tg["type"] == "lemon":
        draw_lemon_icon(d, icx, icy, 28)
    elif tg["type"] == "ice":
        draw_ice_icon(d, icx, icy, 40)
    elif tg["type"] == "mint":
        draw_mint_icon(d, icx, icy, 42)
    elif tg["type"] == "water":
        draw_water_drop_icon(d, icx, icy, 42)
        
    f_tgt = ImageFont.truetype(font_bold, 38)
    d.text((x1 + 120, y1 + 25), tg["title"], font=f_tgt, fill="#FFFFFF")
    
    d.rounded_rectangle([(x1 + 25, y1 + 120), (x2 - 25, y2 - 25)], radius=15, fill=tg["bg"])
    f_tgd = ImageFont.truetype(font_bold, 30)
    draw_wrapped_text(d, tg["desc"], (x1 + 50, y1 + 145), f_tgd, "#263238", max_width=760, line_spacing=14)

im.save(os.path.join(slides_dir, "slide_08.png"))
print("Saved slide_08.png")

# ==============================================================================
# SLIDE 9: MEDICATION SAFETY WITH DRAWN ICONS
# ==============================================================================
im, d = create_base_canvas()
d.text((70, 145), "【第三招】降壓藥按時服，洗腎當天遵醫囑", font=f_t, fill="#0D47A1")

meds_cards = [
    {
        "type": "shield",
        "title": "按時規律服藥，絕不擅自停藥",
        "desc": "降壓藥是保護心臟與大腦血管的盾牌！切勿因為在家量血壓正常就自行停藥或減藥，以免引發反彈性高血壓與中風！",
        "col": "#1976D2"
    },
    {
        "type": "clock",
        "title": "洗腎當日用藥，個別遵循醫囑",
        "desc": "部分降壓藥在透析時容易被清除，或可能引起透析中血壓驟降。洗腎當天早晨服藥時間，請務必諮詢主治醫師指示！",
        "col": "#D32F2F"
    },
    {
        "type": "rest",
        "title": "感到頭暈不適，先坐下量測再應變",
        "desc": "頭暈可能是血壓過高，也可能是脫水太快導致的低血壓！請立即坐下或躺平並量測血壓，切勿在未量測前盲目吞藥！",
        "col": "#F57C00"
    }
]

for i, mc in enumerate(meds_cards):
    y1 = 240 + i * 245
    y2 = y1 + 215
    d.rounded_rectangle([(70, y1), (1850, y2)], radius=25, fill="#FFFFFF", outline=mc["col"], width=3)
    d.rounded_rectangle([(90, y1 + 20), (850, y1 + 90)], radius=15, fill=mc["col"])
    
    # Custom icon
    icx = 130
    icy = y1 + 55
    if mc["type"] == "shield":
        draw_shield_icon(d, icx, icy, 40, color="#FFFFFF")
    elif mc["type"] == "clock":
        draw_clock_icon(d, icx, icy, 22, color="#FFFFFF")
    elif mc["type"] == "rest":
        # Draw seat / resting icon
        d.line([(icx - 15, icy - 15), (icx - 15, icy + 15)], fill="#FFFFFF", width=4)
        d.line([(icx - 15, icy + 5), (icx + 15, icy + 5)], fill="#FFFFFF", width=4)
        d.line([(icx + 15, icy + 5), (icx + 15, icy + 18)], fill="#FFFFFF", width=4)
        d.ellipse([(icx - 2, icy - 18), (icx + 12, icy - 4)], fill="#FFFFFF")
        
    f_mct = ImageFont.truetype(font_bold, 36)
    d.text((170, y1 + 32), mc["title"], font=f_mct, fill="#FFFFFF")
    
    f_mcd = ImageFont.truetype(font_bold, 30)
    draw_wrapped_text(d, mc["desc"], (110, y1 + 115), f_mcd, "#263238", max_width=1680, line_spacing=12)

im.save(os.path.join(slides_dir, "slide_09.png"))
print("Saved slide_09.png")

# ==============================================================================
# SLIDE 10: CONCLUSION & 4 FORMULA BADGES
# ==============================================================================
im, d = create_base_canvas()
d.text((70, 145), "【結語總結】血液透析控壓四字訣——成大透析守護您", font=f_t, fill="#0D47A1")

four_badges = [
    ("7 2 2", "居家量 722", "連續 7 天、早晚量、各量 2 遍\n記錄帶來洗腎室給醫師看", "#1565C0"),
    ("< 5%", "體重不超五", "兩次洗腎間體重增幅 ＜ 5%\n以乾體重 60kg 為例最多 3kg", "#2E7D32"),
    ("忌低鈉", "減鹽忌低鈉", "每天食鹽 ＜ 5g (約 1 平匙)\n嚴禁食用低鈉鹽/美味鹽", "#C62828"),
    ("遵醫囑", "服藥遵醫囑", "規律服藥不擅自停藥\n洗腎當日遵從醫師個別指示", "#6A1B9A")
]

for i, (emblem, b_title, b_desc, col) in enumerate(four_badges):
    col_idx = i % 2
    row_idx = i // 2
    x1 = 70 + col_idx * 900
    x2 = x1 + 860
    y1 = 240 + row_idx * 240
    y2 = y1 + 215
    
    d.rounded_rectangle([(x1, y1), (x2, y2)], radius=25, fill="#FFFFFF", outline=col, width=3)
    
    # Emblem badge
    d.ellipse([(x1 + 30, y1 + 35), (x1 + 160, y1 + 165)], fill=col)
    f_emb = ImageFont.truetype(font_bold, 32)
    tb = d.textbbox((0, 0), emblem, font=f_emb)
    d.text((x1 + 95 - (tb[2]-tb[0])//2, y1 + 100 - (tb[3]-tb[1])//2 - 2), emblem, font=f_emb, fill="#FFFFFF")
    
    # Title
    f_fbt = ImageFont.truetype(font_bold, 38)
    d.text((x1 + 190, y1 + 40), b_title, font=f_fbt, fill=col)
    
    # Description
    f_fbd = ImageFont.truetype(font_bold, 28)
    draw_wrapped_text(d, b_desc, (x1 + 190, y1 + 95), f_fbd, "#37474F", max_width=630, line_spacing=10)

# Bottom warm banner with drawn heart
d.rounded_rectangle([(70, 745), (1850, 955)], radius=25, fill="#E3F2FD", outline="#90CAF9", width=2)
draw_heart_icon(d, 130, 810, 26, "#E91E63")
f_warm = ImageFont.truetype(font_bold, 38)
d.text((180, 785), "成大醫院護理部・血液透析室 關心您", font=f_warm, fill="#0D47A1")
f_subw = ImageFont.truetype(font_bold, 30)
d.text((120, 855), "建立良好居家量測與水分管理習慣，遠離併發症，透析生活健康又有品質！", font=f_subw, fill="#37474F")

im.save(os.path.join(slides_dir, "slide_10.png"))
print("Saved slide_10.png")

print("\n=== All 10 slides v3 generated successfully! ===")
