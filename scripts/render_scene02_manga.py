import os, sys, subprocess, math, shutil
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

brain_dir = r'C:\Users\pink0\.gemini\antigravity\brain\a835a13b-300f-4228-9146-ed73f327da63'
output_dir = r'C:\AI\影片製作_透析高血壓衛教\output'
os.makedirs(output_dir, exist_ok=True)

# 1. Prepare 27.8s padded audio
audio_src = r"C:\AI\影片製作_透析高血壓衛教\audio\audio_scene02_synced.mp3"
audio_synced = os.path.join(output_dir, 'scene_02_manga_27s.mp3')
cmd_audio = ['ffmpeg', '-y', '-i', audio_src, '-af', 'apad=whole_dur=27.8', '-t', '27.8', audio_synced]
subprocess.run(cmd_audio, check=True)
print('27.8s padded audio prepared.')

# 2. Panels for Scene 2
p1_path = os.path.join(brain_dir, 's2_p1_general_bp_1789453029507.jpg')
p2_path = os.path.join(brain_dir, 's2_p2_clinic_bp_1789453051168.jpg')
p3_path = os.path.join(brain_dir, 's10_p1_bp_clean_1789452006932.jpg')
p4_path = os.path.join(brain_dir, 'pose4_thumbs_up_1789430850748.jpg')

panel_size = 405
spacing = 26
total_w = panel_size * 4 + spacing * 3
start_x = (1920 - total_w) // 2
panel_y = 168
badge_h = 56
badge_y = 108
card_y = 590
card_h = 240
bot_y1 = 845
bot_y2 = 985

im1 = Image.open(p1_path).convert('RGB').resize((panel_size, panel_size), Image.Resampling.LANCZOS)
im2 = Image.open(p2_path).convert('RGB').resize((panel_size, panel_size), Image.Resampling.LANCZOS)
im3 = Image.open(p3_path).convert('RGB').resize((panel_size, panel_size), Image.Resampling.LANCZOS)
im4 = Image.open(p4_path).convert('RGB').resize((panel_size, panel_size), Image.Resampling.LANCZOS)
raw_panels = [im1, im2, im3, im4]
dim_enhancer = [ImageEnhance.Brightness(im).enhance(0.55) for im in raw_panels]

font_path = r'C:\Windows\Fonts\msjhbd.ttc'
f_header = ImageFont.truetype(font_path, 38)
f_sub = ImageFont.truetype(font_path, 20)
f_badge = ImageFont.truetype(font_path, 19)
f_step_tag = ImageFont.truetype(font_path, 26)
f_card_sub = ImageFont.truetype(font_path, 26)
f_card_body = ImageFont.truetype(font_path, 24)
f_bot_title = ImageFont.truetype(font_path, 28)
f_bot_body = ImageFont.truetype(font_path, 25)

steps_meta = [
    {
        'title': '指標 1：一般大眾標準',
        'sub': '【國健署標準・<120/80】',
        'lines': [
            '• 一般健康大眾標準值',
            '• 收縮壓 ＜ 120 mmHg',
            '• 舒張壓 ＜ 80 mmHg'
        ],
        'color': (33, 115, 175),
        'bg_card': (242, 248, 255)
    },
    {
        'title': '指標 2：透析診間血壓',
        'sub': '【成大標準・<140/90】',
        'lines': [
            '• 腎友血管硬化與體液波動',
            '• 透析前診間控制 ＜ 140/90',
            '• 診間由專業護理師量測'
        ],
        'color': (215, 90, 15),
        'bg_card': (255, 250, 242)
    },
    {
        'title': '指標 3：透析居家血壓',
        'sub': '【放鬆標準・120~135】',
        'lines': [
            '• 居家放鬆量測最平穩真實',
            '• 收縮壓 120 ～ 135 mmHg',
            '• 舒張壓 60 ～ 80 mmHg'
        ],
        'color': (35, 145, 75),
        'bg_card': (242, 255, 246)
    },
    {
        'title': '指標 4：血壓平穩最優',
        'sub': '【破除迷思・平穩最適】',
        'lines': [
            '• 血壓絕非「越低越好」',
            '• 過低易暈眩、抽筋、掉血壓',
            '• 數值平穩保護心血管最安心'
        ],
        'color': (125, 45, 150),
        'bg_card': (253, 245, 255)
    }
]

def draw_frame(active_step, pulse):
    canvas = Image.new('RGB', (1920, 1080), (243, 246, 250))
    draw = ImageDraw.Draw(canvas)
    
        # 1. Hospital Header with 【透析室高血壓專題】 Top-Left Badge
    draw.rectangle([0, 0, 1920, 96], fill=(20, 70, 115))
    badge_text = '【透析室高血壓專題】'
    tw = draw.textlength(badge_text, font=f_badge)
    draw.rounded_rectangle([(60, 10), (60 + tw + 20, 38)], radius=8, fill='#E3F2FD')
    draw.text((70, 13), badge_text, font=f_badge, fill='#0D47A1')
    draw.text((60 + tw + 32, 13), '國立成功大學醫學院附設醫院 血液透析室', font=f_sub, fill=(180, 220, 250))
    draw.text((60, 46), '【標準對照】透析血壓控制標準：診間<140/90・居家120~135・平穩最適當！', font=f_header, fill=(255, 255, 255))
    
    # 2. Panels and Badges
    for i, meta in enumerate(steps_meta):
        px = start_x + i * (panel_size + spacing)
        is_cur = (i == active_step)
        is_finale = (active_step == -1)
        
        # Badge
        badge_bg = meta['color'] if (is_cur or is_finale) else (205, 215, 225)
        badge_tc = (255, 255, 255) if (is_cur or is_finale) else (110, 125, 140)
        draw.rounded_rectangle([px, badge_y, px + panel_size, badge_y + badge_h], radius=14, fill=badge_bg)
        tw = draw.textlength(meta['title'], font=f_step_tag)
        draw.text((px + (panel_size - tw)/2, badge_y + 11), meta['title'], font=f_step_tag, fill=badge_tc)
        
        # Arrow
        if i < 3:
            ax = px + panel_size + spacing / 2
            ay = badge_y + badge_h / 2
            arr_c = (80, 100, 120) if (active_step > i or is_finale) else (185, 195, 210)
            draw.polygon([(ax - 9, ay - 12), (ax + 9, ay), (ax - 9, ay + 12)], fill=arr_c)
            
        # Panel Artwork
        panel_to_paste = raw_panels[i] if (is_cur or is_finale) else dim_enhancer[i]
        
        if is_cur:
            bw_glow = int(5 + 3 * pulse)
            draw.rounded_rectangle([px - bw_glow, panel_y - bw_glow, px + panel_size + bw_glow, panel_y + panel_size + bw_glow],
                                   radius=12, fill=meta['color'])
        elif is_finale:
            draw.rounded_rectangle([px - 4, panel_y - 4, px + panel_size + 4, panel_y + panel_size + 4],
                                   radius=10, fill=(241, 196, 15))
        else:
            draw.rounded_rectangle([px - 2, panel_y - 2, px + panel_size + 2, panel_y + panel_size + 2],
                                   radius=8, fill=(200, 210, 220))
            
        canvas.paste(panel_to_paste, (px, panel_y))
        
        # Action Card beneath
        card_bg = meta['bg_card'] if (is_cur or is_finale) else (248, 250, 252)
        card_bord = meta['color'] if (is_cur or is_finale) else (215, 225, 235)
        card_lw = 4 if (is_cur or is_finale) else 2
        draw.rounded_rectangle([px, card_y, px + panel_size, card_y + card_h], radius=16, fill=card_bg, outline=card_bord, width=card_lw)
        
        sw = draw.textlength(meta['sub'], font=f_card_sub)
        sub_c = meta['color'] if (is_cur or is_finale) else (120, 135, 150)
        draw.text((px + (panel_size - sw)/2, card_y + 16), meta['sub'], font=f_card_sub, fill=sub_c)
        
        line_y = card_y + 64
        for line in meta['lines']:
            text_c = (35, 45, 55) if (is_cur or is_finale) else (140, 150, 160)
            draw.text((px + 20, line_y), line, font=f_card_body, fill=text_c)
            line_y += 44

        # 3. Bottom Reminder Banner (Dynamically Calculated Width, Zero Text Clipping)
    if active_step != -1:
        draw.rounded_rectangle([start_x, bot_y1, start_x + total_w, bot_y2], radius=16, fill=(255, 252, 242), outline=(243, 156, 18), width=3)
        b_title = "血壓標準重點"
        tw = draw.textlength(b_title, font=f_bot_title)
        bw = max(240, int(tw + 44))
        bx = start_x + 24
        by = bot_y1 + 18
        bh = 104
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12, fill=(243, 156, 18))
        draw.text((bx + (bw - tw) / 2, by + (bh - 28) / 2), b_title, font=f_bot_title, fill=(255, 255, 255))
        
        rx = bx + bw + 24
        draw.text((rx, bot_y1 + 18), '① 腎友診間血壓因環境因素易偏高，成大醫院建議透析前控制在 ＜ 140/90 mmHg！', font=f_bot_body, fill=(40, 50, 60))
        draw.text((rx, bot_y1 + 54), '② 居家放鬆測量建議維持於 120～135 / 60～80 mmHg，平穩不劇烈起伏，保護心血管！', font=f_bot_body, fill=(185, 40, 25))
        draw.text((rx, bot_y1 + 90), '★ 成大醫院血液透析室諮詢專線：(06) 235-3535 分機 2591・成大醫護團隊守護您的健康！', font=f_bot_body, fill=(24, 76, 120))
    else:
        draw.rounded_rectangle([start_x, bot_y1, start_x + total_w, bot_y2], radius=16, fill=(255, 248, 225), outline=(241, 196, 15), width=4)
        b_title = "★ 控壓標準心訣"
        tw = draw.textlength(b_title, font=f_bot_title)
        bw = max(260, int(tw + 48))
        bx = start_x + 24
        by = bot_y1 + 18
        bh = 104
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12, fill=(211, 84, 0))
        draw.text((bx + (bw - tw) / 2, by + (bh - 28) / 2), b_title, font=f_bot_title, fill=(255, 255, 255))
        
        rx = bx + bw + 24
        draw.text((rx, bot_y1 + 22), '「診間140、居家135、平穩最適當！」血壓不是越低越好，平穩不波動才是健康王道！', font=f_bot_title, fill=(192, 57, 43))
        draw.text((rx, bot_y1 + 64), '• 國立成功大學醫學院附設醫院 血液透析室（分機 2591）關心您與家人的健康！', font=f_bot_body, fill=(40, 50, 60))
        
    return canvas

fps = 30
duration = 27.8
total_frames = int(fps * duration)
out_video = os.path.join(output_dir, '樣片_第2幕_血壓標準值_日式衛教漫畫連續動作版.mp4')

cmd = [
    'ffmpeg', '-y',
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-s', '1920x1080',
    '-pix_fmt', 'rgb24',
    '-r', str(fps),
    '-i', '-',
    '-i', audio_synced,
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-c:a', 'aac',
    '-b:a', '192k',
    '-shortest',
    out_video
]

print('Rendering Scene 2 Japanese Manga Video...')
pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE)

for f in range(total_frames):
    t = f / fps
    if t < 6.5:
        active_step = 0
    elif t < 13.0:
        active_step = 1
    elif t < 20.0:
        active_step = 2
    elif t < 25.0:
        active_step = 3
    else:
        active_step = -1
        
    pulse = 0.5 + 0.5 * math.sin(t * 7.0)
    frame_img = draw_frame(active_step, pulse)
    pipe.stdin.write(frame_img.tobytes())

pipe.stdin.close()
pipe.wait()
print('Scene 2 Video rendered successfully:', out_video)
