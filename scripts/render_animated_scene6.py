import os
import sys
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

base_dir = r"C:\AI\影片製作_透析高血壓衛教"
brain_dir = r"C:\Users\pink0\.gemini\antigravity\brain\a835a13b-300f-4228-9146-ed73f327da63"
audio_path = os.path.join(base_dir, "audio", "scene_06.mp3")
out_mp4 = os.path.join(base_dir, "output", "樣片_第6幕_體重增幅不超5趴_動態升級版.mp4")

font_bold = r"C:\Windows\Fonts\msjhbd.ttc"
font_reg = r"C:\Windows\Fonts\msjh.ttc"

im_bottles_raw = Image.open(os.path.join(base_dir, "output", "t_bottles_cn_v5.png"))
im_grandpa_raw = Image.open(os.path.join(base_dir, "output", "t_grandpa.png"))

bw_base, bh_base = 520, 480
bottles_base = im_bottles_raw.resize((bw_base, bh_base), Image.Resampling.LANCZOS)
grandpa_base = im_grandpa_raw.resize((320, 440), Image.Resampling.LANCZOS)

FPS = 30
DURATION = 15.50
TOTAL_FRAMES = int(FPS * DURATION) + 1
WIDTH, HEIGHT = 1920, 1080

f_title = ImageFont.truetype(font_bold, 42)
f_formula = ImageFont.truetype(font_bold, 28)
f_formula_sub = ImageFont.truetype(font_bold, 24)
f_card_title = ImageFont.truetype(font_bold, 32)
f_sub = ImageFont.truetype(font_bold, 28)

def draw_wrapped_text(d, text, pos, font, fill, max_width=500, line_spacing=8):
    lines = text.split("\n")
    x, y = pos
    for line in lines:
        d.text((x, y), line, font=font, fill=fill)
        bbox = d.textbbox((x, y), line, font=font)
        y += (bbox[3] - bbox[1]) + line_spacing

def get_subtitle(t):
    if t < 7.2:
        return "因此，兩次洗腎間的體重增加，必須嚴格控制在乾體重的百分之五以內。"
    else:
        return "例如乾體重六十公斤的病友，下次洗腎走進透析室前，體重增加絕不能超過三公斤！"

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

print(f"Starting Scene 6 rendering ({TOTAL_FRAMES} frames @ {FPS} FPS)...")
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
    d.text((60, 125), "【第二招】透析間體重增加「＜ 5% 黃金守則」", font=f_title, fill="#0D47A1")
    
    # Focus logic
    is_f1 = (t < 7.2)
    is_f2 = (t >= 7.2)
    
    # 3. Formula Banner
    d.rounded_rectangle([(60, 180), (1860, 275)], radius=18, fill="#0D47A1")
    d.text((100, 195), "黃金計算公式：兩次洗腎間體重增加 ＜ 乾體重的 5%", font=f_formula, fill="#FFFFFF")
    d.text((100, 235), "【實例計算】：乾體重 60 公斤 × 5% ＝ 最多增加 3.0 公斤（3000cc 水分）", font=f_formula_sub, fill="#FFE082")
    
    # -------------------------------------------------------------
    # LEFT CARD: 3 Water Bottles + Max Limit (x: 60 ~ 940)
    # -------------------------------------------------------------
    c1_outline = "#D84315" if is_f2 else "#FF8A65"
    c1_w = 5 if is_f2 else 3
    d.rounded_rectangle([(60, 295), (940, 955)], radius=22, fill="#FFFFFF", outline=c1_outline, width=c1_w)
    d.rounded_rectangle([(60, 295), (940, 375)], radius=22, fill="#E65100")
    d.text((120, 318), "【實物比喻】以 60 公斤為例：最多 3 大瓶水！", font=f_card_title, fill="#FFFFFF")
    
    # Center Graphic: Bottles on scale with pulse when warning active
    if is_f2:
        b_pulse = 1.0 + 0.03 * math.sin(t * 8)
    else:
        b_pulse = 1.0
    cur_bw = int(bw_base * b_pulse)
    cur_bh = int(bh_base * b_pulse)
    cur_bottles = bottles_base.resize((cur_bw, cur_bh), Image.Resampling.LANCZOS)
    by = 620
    frame.paste(cur_bottles, (500 - cur_bw // 2, by - cur_bh // 2), cur_bottles)
    
    # Flash Warning Box under bottles
    if is_f2:
        d.rounded_rectangle([(80, 840), (920, 898)], radius=14, fill="#FFEBEE", outline="#D32F2F", width=2)
        d.rounded_rectangle([(95, 848), (185, 890)], radius=8, fill="#D32F2F")
        d.text((107, 856), "嚴 格", font=ImageFont.truetype(font_bold, 20), fill="#FFFFFF")
        d.text((200, 854), "絕不能超過 3 公斤！洗腎當日體重上限 63.0 kg！", font=ImageFont.truetype(font_bold, 23), fill="#C62828")
    else:
        d.rounded_rectangle([(80, 840), (920, 898)], radius=14, fill="#E3F2FD", outline="#1976D2", width=2)
        d.rounded_rectangle([(95, 848), (185, 890)], radius=8, fill="#1565C0")
        d.text((107, 856), "標 準", font=ImageFont.truetype(font_bold, 20), fill="#FFFFFF")
        d.text((200, 854), "1 公斤體重 ＝ 1000cc 水分（最多 3 大瓶水）", font=ImageFont.truetype(font_bold, 23), fill="#0D47A1")
        
    d.text((85, 915), "• 1公斤體重 ＝ 1000cc 水分  • 即使隔兩天週末，增加量依然要守住 5%！", font=ImageFont.truetype(font_bold, 18), fill="#37474F")
    
    # -------------------------------------------------------------
    # RIGHT CARD: Weighing Rules + Grandfather Scale (x: 980 ~ 1860)
    # -------------------------------------------------------------
    c2_outline = "#2E7D32" if is_f1 else "#81C784"
    c2_w = 4 if is_f1 else 3
    d.rounded_rectangle([(980, 295), (1860, 955)], radius=22, fill="#FFFFFF", outline=c2_outline, width=c2_w)
    d.rounded_rectangle([(980, 295), (1860, 375)], radius=22, fill="#2E7D32")
    d.text((1040, 318), "【正確測量體重的三大原則】", font=f_card_title, fill="#FFFFFF")
    
    # Grandfather measuring scale
    g_scale = 1.0 + 0.02 * math.sin(t * 3)
    gw = int(320 * g_scale)
    gh = int(440 * g_scale)
    cur_grandpa = grandpa_base.resize((gw, gh), Image.Resampling.LANCZOS)
    frame.paste(cur_grandpa, (1000 - (gw - 320) // 2, 430 - (gh - 440) // 2), cur_grandpa)
    
    rules = [
        ("① 每日固定時間", "早晨起床、上完洗手間後立刻測量最精準。", "#E8F5E9", "#388E3C", "#1B5E20"),
        ("② 固定同一台體重計", "避免不同磅秤產生數值偏差誤差。", "#E3F2FD", "#1976D2", "#0D47A1"),
        ("③ 穿著相似輕便衣服", "去除厚重外套、皮帶與鞋子重量，基準一致。", "#FFF8E1", "#FFA000", "#E65100")
    ]
    rx, ry = 1330, 410
    for title, desc, bg_c, bord_c, txt_c in rules:
        d.rounded_rectangle([(rx, ry), (1830, ry + 110)], radius=15, fill=bg_c, outline=bord_c, width=2)
        d.text((rx + 25, ry + 16), title, font=ImageFont.truetype(font_bold, 24), fill=txt_c)
        d.text((rx + 25, ry + 56), desc, font=ImageFont.truetype(font_bold, 19), fill="#37474F")
        ry += 135

    d.rounded_rectangle([(1010, 875), (1830, 935)], radius=12, fill="#F1F8E9", outline="#8BC34A", width=2)
    d.text((1030, 890), "★ 成大透析室叮嚀：兩次洗腎體重增加 ＜ 5%，心臟不積水、透析不抽筋！", font=ImageFont.truetype(font_bold, 21), fill="#2E7D32")
    
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
    
    proc.stdin.write(frame.tobytes())
    
    if frame_idx % 60 == 0:
        print(f"Rendered frame {frame_idx}/{TOTAL_FRAMES} ({(frame_idx/TOTAL_FRAMES)*100:.1f}%)")

proc.stdin.close()
proc.wait()
print("\n=== Scene 6 Rendered Successfully! ===")
print("Output:", out_mp4)
