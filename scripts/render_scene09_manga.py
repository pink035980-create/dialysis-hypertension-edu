import os, sys, subprocess, math, shutil
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

brain_dir = r'C:\Users\pink0\.gemini\antigravity\brain\a835a13b-300f-4228-9146-ed73f327da63'
output_dir = r'C:\AI\影片製作_透析高血壓衛教\output'
audio_raw = r'C:\AI\影片製作_透析高血壓衛教\audio\scene_09.mp3'

# 1. Prepare 25s padded audio
audio_25s = os.path.join(output_dir, 'scene_09_25s.mp3')
cmd_audio = ['ffmpeg', '-y', '-i', audio_raw, '-af', 'apad=whole_dur=25', '-t', '25', audio_25s]
subprocess.run(cmd_audio, check=True)

# 2. Image assets
p1_path = os.path.join(brain_dir, 'pose1_take_box_1789430800530.jpg')
p2_path = os.path.join(brain_dir, 'pose2_prescription_1789440828417.jpg')
p3_path = os.path.join(brain_dir, 'pose3_no_box_1789440804133.jpg')
p4_path = os.path.join(brain_dir, 'pose4_thumbs_up_1789430850748.jpg')

panel_size = 405
spacing = 26
total_w = panel_size * 4 + spacing * 3 # 1698
start_x = (1920 - total_w) // 2 # 111
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
        'title': '第 1 步：核對當天藥格',
        'sub': '【拿取藥盒・不吃錯】',
        'lines': ['• 每天固定時間量測血壓', '• 按星期檢查當日透明藥格', '• 確認藥品種類與份量無誤'],
        'color': (33, 115, 175), # Blue
        'bg_card': (242, 248, 255)
    },
    {
        'title': '第 2 步：倒出規定劑量',
        'sub': '【核對處方・備溫水】',
        'lines': ['• 核對處方藥袋規定劑量', '• 倒出藥物於乾淨掌心', '• 身旁備妥一杯常溫開水'],
        'color': (35, 155, 86), # Green
        'bg_card': (242, 255, 246)
    },
    {
        'title': '第 3 步：仰頭溫水吞服',
        'sub': '【順暢吞服・不急躁】',
        'lines': ['• 頭部微仰順勢吞下', '• 配一口常溫開水嚥服', '• 動作放緩、不嗆咳卡喉'],
        'color': (215, 90, 15), # Orange
        'bg_card': (255, 250, 242)
    },
    {
        'title': '第 4 步：拍胸開懷比讚',
        'sub': '【心腦防護・大平安】',
        'lines': ['• 輕撫胸口順氣深呼吸', '• 開懷笑顏、大拇指比讚', '• 降壓藥啟動隱形保護罩'],
        'color': (130, 60, 160), # Purple
        'bg_card': (253, 245, 255)
    }
]

fps = 30
duration = 25.0
total_frames = int(fps * duration)
out_video = os.path.join(output_dir, '樣片_第9幕_服藥動作四部曲_日式衛教漫畫連續動作版.mp4')

cmd = [
    'ffmpeg', '-y',
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-s', '1920x1080',
    '-pix_fmt', 'rgb24',
    '-r', str(fps),
    '-i', '-',
    '-i', audio_25s,
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-c:a', 'aac',
    '-b:a', '192k',
    '-shortest',
    out_video
]

print('Launching 25s ffmpeg pipe...')
pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE)

for f in range(total_frames):
    t = f / fps
    
    # Timeline for 25 seconds:
    # Step 1: 0.0s ~ 5.5s
    # Step 2: 5.5s ~ 11.0s
    # Step 3: 11.0s ~ 16.5s
    # Step 4: 16.5s ~ 21.5s
    # Finale: 21.5s ~ 25.0s
    if t < 5.5:
        active_step = 0
    elif t < 11.0:
        active_step = 1
    elif t < 16.5:
        active_step = 2
    elif t < 21.5:
        active_step = 3
    else:
        active_step = -1 # Finale all active
        
    canvas = Image.new('RGB', (1920, 1080), (243, 246, 250))
    draw = ImageDraw.Draw(canvas)
    
        # 1. Hospital Header with 【透析室高血壓專題】 Top-Left Badge
    draw.rectangle([0, 0, 1920, 96], fill=(20, 70, 115))
    badge_text = '【透析室高血壓專題】'
    tw = draw.textlength(badge_text, font=f_badge)
    draw.rounded_rectangle([(60, 10), (60 + tw + 20, 38)], radius=8, fill='#E3F2FD')
    draw.text((70, 13), badge_text, font=f_badge, fill='#0D47A1')
    draw.text((60 + tw + 32, 13), '國立成功大學醫學院附設醫院 血液透析室', font=f_sub, fill=(180, 220, 250))
    draw.text((60, 46), '【第三招】降壓藥按時服：血壓正常代表保護中，洗腎早晨遵醫囑！', font=f_header, fill=(255, 255, 255))
    
    pulse = 0.5 + 0.5 * math.sin(t * 7.0) # 0.0 to 1.0
    
    # 2. Panels and Badges
    for i, meta in enumerate(steps_meta):
        px = start_x + i * (panel_size + spacing)
        is_cur = (i == active_step) or (active_step == -1)
        
        # Badge
        badge_bg = meta['color'] if is_cur else (205, 215, 225)
        badge_tc = (255, 255, 255) if is_cur else (110, 125, 140)
        draw.rounded_rectangle([px, badge_y, px + panel_size, badge_y + badge_h], radius=14, fill=badge_bg)
        tw = draw.textlength(meta['title'], font=f_step_tag)
        draw.text((px + (panel_size - tw)/2, badge_y + 11), meta['title'], font=f_step_tag, fill=badge_tc)
        
        # Arrow
        if i < 3:
            ax = px + panel_size + spacing / 2
            ay = badge_y + badge_h / 2
            arr_c = (80, 100, 120) if (active_step > i or active_step == -1) else (185, 195, 210)
            draw.polygon([(ax - 9, ay - 12), (ax + 9, ay), (ax - 9, ay + 12)], fill=arr_c)
            
        # Panel Artwork
        panel_to_paste = raw_panels[i] if is_cur else dim_enhancer[i]
        
        if is_cur and active_step != -1:
            # Active panel glowing border
            bw_glow = int(5 + 3 * pulse)
            draw.rounded_rectangle([px - bw_glow, panel_y - bw_glow, px + panel_size + bw_glow, panel_y + panel_size + bw_glow],
                                   radius=12, fill=meta['color'])
        elif active_step == -1:
            # Finale celebration outline
            draw.rounded_rectangle([px - 4, panel_y - 4, px + panel_size + 4, panel_y + panel_size + 4],
                                   radius=10, fill=(241, 196, 15))
        else:
            draw.rounded_rectangle([px - 2, panel_y - 2, px + panel_size + 2, panel_y + panel_size + 2],
                                   radius=8, fill=(200, 210, 220))
            
        canvas.paste(panel_to_paste, (px, panel_y))
        
        # Action Card beneath
        card_bg = meta['bg_card'] if is_cur else (248, 250, 252)
        card_bord = meta['color'] if is_cur else (215, 225, 235)
        card_lw = 4 if is_cur else 2
        draw.rounded_rectangle([px, card_y, px + panel_size, card_y + card_h], radius=16, fill=card_bg, outline=card_bord, width=card_lw)
        
        sw = draw.textlength(meta['sub'], font=f_card_sub)
        sub_c = meta['color'] if is_cur else (120, 135, 150)
        draw.text((px + (panel_size - sw)/2, card_y + 16), meta['sub'], font=f_card_sub, fill=sub_c)
        
        line_y = card_y + 64
        for line in meta['lines']:
            text_c = (35, 45, 55) if is_cur else (140, 150, 160)
            draw.text((px + 20, line_y), line, font=f_card_body, fill=text_c)
            line_y += 44

    # 3. Bottom Reminder Banner (Dynamically Calculated Width, Zero Text Clipping)
    if active_step != -1:
        draw.rounded_rectangle([start_x, bot_y1, start_x + total_w, bot_y2], radius=16, fill=(255, 252, 242), outline=(243, 156, 18), width=3)
        b_title = "腎友服藥守則"
        tw = draw.textlength(b_title, font=f_bot_title)
        bw = max(240, int(tw + 44))
        bx = start_x + 24
        by = bot_y1 + 18
        bh = 104
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12, fill=(243, 156, 18))
        draw.text((bx + (bw - tw) / 2, by + (bh - 28) / 2), b_title, font=f_bot_title, fill=(255, 255, 255))
        
        rx = bx + bw + 24
        draw.text((rx, bot_y1 + 18), '① 每天定時量血壓並固定服藥，血壓正常代表降壓藥正在發揮保護作用，絕不可自行停藥！', font=f_bot_body, fill=(40, 50, 60))
        draw.text((rx, bot_y1 + 54), '② 洗腎日早晨切勿盲目吞服強效降壓藥，請整袋帶來透析室，遵照成大醫師護理師指導服用！', font=f_bot_body, fill=(185, 40, 25))
        draw.text((rx, bot_y1 + 90), '★ 成大醫院血液透析室諮詢專線：(06) 235-3535 分機 2591・成大醫護團隊守護您的健康！', font=f_bot_body, fill=(24, 76, 120))
    else:
        # Finale Celebration
        draw.rounded_rectangle([start_x, bot_y1, start_x + total_w, bot_y2], radius=16, fill=(255, 248, 225), outline=(241, 196, 15), width=4)
        b_title = "★ 服藥黃金四字訣"
        tw = draw.textlength(b_title, font=f_bot_title)
        bw = max(260, int(tw + 48))
        bx = start_x + 24
        by = bot_y1 + 18
        bh = 104
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12, fill=(211, 84, 0))
        draw.text((bx + (bw - tw) / 2, by + (bh - 28) / 2), b_title, font=f_bot_title, fill=(255, 255, 255))
        
        rx = bx + bw + 24
        draw.text((rx, bot_y1 + 22), '「拿・倒・吞・讚」服藥動作四部曲！天天定時定量服藥，啟動心腦血管隱形防護罩！', font=f_bot_title, fill=(192, 57, 43))
        draw.text((rx, bot_y1 + 64), '• 降壓藥按時服・洗腎當天遵醫囑！成大醫院血液透析室（分機 2591）關心您的健康！', font=f_bot_body, fill=(40, 50, 60))

        
    pipe.stdin.write(canvas.tobytes())

pipe.stdin.close()
pipe.wait()
print('25s video rendered successfully:', out_video)

# Also save the final static slide directly from rendered frame
out_slide_brain = os.path.join(brain_dir, 'manga_4panel_logic_refined.png')
out_slide_desk = os.path.join(r'C:\Users\pink0\OneDrive\Desktop', '第9幕_服藥四部曲日式漫畫全景圖卡.png')
canvas.save(out_slide_brain)
canvas.save(out_slide_desk)
subprocess.run(['attrib', '+p', '-u', out_slide_desk], shell=True)

# Deploy video to desktop
desk_video = os.path.join(r'C:\Users\pink0\OneDrive\Desktop', '樣片_第9幕_服藥動作四部曲_日式衛教漫畫連續動作版.mp4')
vid_video = os.path.join(r'C:\Users\pink0\Videos', '樣片_第9幕_服藥動作四部曲_日式衛教漫畫連續動作版.mp4')
shutil.copy2(out_video, desk_video)
shutil.copy2(out_video, vid_video)
subprocess.run(['attrib', '+p', '-u', desk_video], shell=True)
print('Deployed 25s video to desktop successfully')
# Done rendering Scene 9

