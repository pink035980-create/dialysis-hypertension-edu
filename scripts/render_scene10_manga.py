import os, sys, subprocess, math, shutil
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

brain_dir = r'C:\Users\pink0\.gemini\antigravity\brain\a835a13b-300f-4228-9146-ed73f327da63'
output_dir = r'C:\AI\影片製作_透析高血壓衛教\output'
os.makedirs(output_dir, exist_ok=True)

# 1. Prepare 34.5s padded audio
audio_src = os.path.join(brain_dir, 'scratch', 'audio_scene10_siju.mp3')
audio_34s = os.path.join(output_dir, 'scene_10_manga_34s.mp3')
cmd_audio = ['ffmpeg', '-y', '-i', audio_src, '-af', 'apad=whole_dur=34.5', '-t', '34.5', audio_34s]
subprocess.run(cmd_audio, check=True)
print('34.5s padded audio prepared.')

# 2. Four Japanese Manga Panels for Scene 10
p1_path = os.path.join(brain_dir, 's10_p1_bp_clean_1789452006932.jpg')
p2_path = os.path.join(brain_dir, 's10_p2_weight_1789452027876.jpg')
p3_path = os.path.join(brain_dir, 's10_p3_salt_1789452044875.jpg')
p4_path = os.path.join(brain_dir, 's10_p4_adherence_1789452061044.jpg')

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
        'title': '第 1 訣：居家量七二二',
        'sub': '【掌握真實・早晚量測】',
        'lines': [
            '• 連續測量 7 天、早晚各 1 次',
            '• 每次量 2 遍取平均數值',
            '• 記錄本帶來洗腎室給醫師參考'
        ],
        'color': (33, 115, 175), # Blue
        'bg_card': (242, 248, 255)
    },
    {
        'title': '第 2 訣：體重不超五',
        'sub': '【嚴防水腫・保護心臟】',
        'lines': [
            '• 兩次洗腎間增幅 ＜ 5%',
            '• 以乾體重 60kg 為例最多 3kg',
            '• 少量多次解渴，徹底預防肺積水'
        ],
        'color': (35, 145, 75), # Green
        'bg_card': (242, 255, 246)
    },
    {
        'title': '第 3 訣：減鹽忌低鈉',
        'sub': '【嚴防高血鉀・防猝死】',
        'lines': [
            '• 每日食鹽量 ＜ 5g（約 1 平匙）',
            '• 嚴禁食用低鈉鹽與美味鹽',
            '• 低鈉鹽含高鉀，透析腎友恐猝死'
        ],
        'color': (195, 35, 25), # Red
        'bg_card': (255, 245, 244)
    },
    {
        'title': '第 4 訣：服藥遵醫囑',
        'sub': '【按時服藥・安全遵醫】',
        'lines': [
            '• 天天固定吃藥，血壓正常不擅停',
            '• 洗腎日早晨遵照透析醫師指示',
            '• 藥袋整包帶來透析室由醫護指導'
        ],
        'color': (125, 45, 150), # Purple
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
    draw.text((60, 46), '【結語總結】血液透析控壓四句訣：量722・體重<5%・忌低鈉・遵醫囑！', font=f_header, fill=(255, 255, 255))
    
    # 2. Panels and Badges
    for i, meta in enumerate(steps_meta):
        px = start_x + i * (panel_size + spacing)
        is_cur = (i == active_step)
        is_finale = (active_step == -1)
        is_opening = (active_step == -2)
        
        # Badge
        badge_bg = meta['color'] if (is_cur or is_finale or is_opening) else (205, 215, 225)
        badge_tc = (255, 255, 255) if (is_cur or is_finale or is_opening) else (110, 125, 140)
        draw.rounded_rectangle([px, badge_y, px + panel_size, badge_y + badge_h], radius=14, fill=badge_bg)
        tw = draw.textlength(meta['title'], font=f_step_tag)
        draw.text((px + (panel_size - tw)/2, badge_y + 11), meta['title'], font=f_step_tag, fill=badge_tc)
        
        # Arrow
        if i < 3:
            ax = px + panel_size + spacing / 2
            ay = badge_y + badge_h / 2
            arr_c = (80, 100, 120) if (active_step > i or is_finale or is_opening) else (185, 195, 210)
            draw.polygon([(ax - 9, ay - 12), (ax + 9, ay), (ax - 9, ay + 12)], fill=arr_c)
            
        # Panel Artwork
        panel_to_paste = raw_panels[i] if (is_cur or is_finale or is_opening) else dim_enhancer[i]
        
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
        card_bg = meta['bg_card'] if (is_cur or is_finale or is_opening) else (248, 250, 252)
        card_bord = meta['color'] if (is_cur or is_finale) else (215, 225, 235)
        card_lw = 4 if (is_cur or is_finale) else 2
        draw.rounded_rectangle([px, card_y, px + panel_size, card_y + card_h], radius=16, fill=card_bg, outline=card_bord, width=card_lw)
        
        sw = draw.textlength(meta['sub'], font=f_card_sub)
        sub_c = meta['color'] if (is_cur or is_finale or is_opening) else (120, 135, 150)
        draw.text((px + (panel_size - sw)/2, card_y + 16), meta['sub'], font=f_card_sub, fill=sub_c)
        
        line_y = card_y + 64
        for j, line in enumerate(meta['lines']):
            if not (is_cur or is_finale or is_opening):
                text_c = (140, 150, 160)
            elif j == 1 and i == 2: # 嚴禁食用低鈉鹽
                text_c = (210, 20, 20)
            elif j == 2 and i == 2: # 低鈉鹽含高鉀
                text_c = (190, 20, 20)
            else:
                text_c = (35, 45, 55)
            draw.text((px + 20, line_y), line, font=f_card_body, fill=text_c)
            line_y += 44

        # 3. Bottom Reminder Banner (Dynamically Calculated Width, Zero Text Clipping)
    if active_step != -1:
        draw.rounded_rectangle([start_x, bot_y1, start_x + total_w, bot_y2], radius=16, fill=(255, 252, 242), outline=(243, 156, 18), width=3)
        b_title = "成大同心關懷"
        tw = draw.textlength(b_title, font=f_bot_title)
        bw = max(240, int(tw + 44))
        bx = start_x + 24
        by = bot_y1 + 18
        bh = 104
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12, fill=(243, 156, 18))
        draw.text((bx + (bw - tw) / 2, by + (bh - 28) / 2), b_title, font=f_bot_title, fill=(255, 255, 255))
        
        rx = bx + bw + 24
        draw.text((rx, bot_y1 + 18), '① 建立良好居家量測、水分管理與安全服藥習慣，遠離心血管與水腫併發症！', font=f_bot_body, fill=(40, 50, 60))
        draw.text((rx, bot_y1 + 54), '② 洗腎生活健康又有品質，成大醫護團隊永遠陪伴在您身旁，守護您的心腎健康！', font=f_bot_body, fill=(185, 40, 25))
        draw.text((rx, bot_y1 + 90), '★ 成大醫院血液透析室諮詢專線：(06) 235-3535 分機 2591・同心同行守護健康！', font=f_bot_body, fill=(24, 76, 120))
    else:
        draw.rounded_rectangle([start_x, bot_y1, start_x + total_w, bot_y2], radius=16, fill=(255, 248, 225), outline=(241, 196, 15), width=4)
        b_title = "★ 醫護守護同行"
        tw = draw.textlength(b_title, font=f_bot_title)
        bw = max(260, int(tw + 48))
        bx = start_x + 24
        by = bot_y1 + 18
        bh = 104
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12, fill=(211, 84, 0))
        draw.text((bx + (bw - tw) / 2, by + (bh - 28) / 2), b_title, font=f_bot_title, fill=(255, 255, 255))
        
        rx = bx + bw + 24
        draw.text((rx, bot_y1 + 22), '成大醫院護理部與血液透析室，陪伴您安心透析、健康同行！', font=f_bot_title, fill=(192, 40, 25))
        draw.text((rx, bot_y1 + 64), '★ 控壓四句訣：居家量 722・體重 ＜ 5%・減鹽忌低鈉・服藥遵醫囑！', font=f_bot_body, fill=(40, 50, 60))
        
    return canvas

# Save high-res static slide
final_slide = draw_frame(active_step=-1, pulse=1.0)
slide_desk = os.path.join(r'C:\Users\pink0\OneDrive\Desktop', '第10幕_控壓四句訣日式漫畫全景圖卡.png')
final_slide.save(slide_desk)
subprocess.run(['attrib', '+p', '-u', slide_desk], shell=True)
print('Static slide saved and pinned to desktop:', slide_desk)

# Render 34.5s synchronized video
fps = 30
duration = 34.5
total_frames = int(fps * duration)
out_video = os.path.join(output_dir, '樣片_第10幕_控壓四字訣日式衛教漫畫連續動作版.mp4')

cmd = [
    'ffmpeg', '-y',
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-s', '1920x1080',
    '-pix_fmt', 'rgb24',
    '-r', str(fps),
    '-i', '-',
    '-i', audio_34s,
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-c:a', 'aac',
    '-b:a', '192k',
    '-shortest',
    out_video
]

print('Launching 34s ffmpeg pipe in Scene 9 style...')
pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE)

for f in range(total_frames):
    t = f / fps
    # 0.0s ~ 3.9s: Opening intro (active_step = -2)
    # 3.9s ~ 9.7s: Panel 1 (居家量七二二, active_step = 0)
    # 9.7s ~ 14.8s: Panel 2 (體重不超五, active_step = 1)
    # 14.8s ~ 20.6s: Panel 3 (減鹽忌低鈉, active_step = 2)
    # 20.6s ~ 26.3s: Panel 4 (服藥遵醫囑, active_step = 3)
    # 26.3s ~ 34.0s: Grand Finale (active_step = -1)
    if t < 3.9:
        active_step = -2
    elif t < 9.7:
        active_step = 0
    elif t < 14.8:
        active_step = 1
    elif t < 20.6:
        active_step = 2
    elif t < 26.3:
        active_step = 3
    else:
        active_step = -1
        
    pulse = 0.5 + 0.5 * math.sin(t * 7.0)
    frame_img = draw_frame(active_step, pulse)
    pipe.stdin.write(frame_img.tobytes())

pipe.stdin.close()
pipe.wait()
print('34s video in Scene 9 style rendered successfully:', out_video)

# Deploy video to desktop and videos folder
desk_video = os.path.join(r'C:\Users\pink0\OneDrive\Desktop', '樣片_第10幕_控壓四字訣日式衛教漫畫連續動作版.mp4')
vid_video = os.path.join(r'C:\Users\pink0\Videos', '樣片_第10幕_控壓四字訣日式衛教漫畫連續動作版.mp4')
shutil.copy2(out_video, desk_video)
shutil.copy2(out_video, vid_video)
subprocess.run(['attrib', '+p', '-u', desk_video], shell=True)
print('Deployed 34s video to desktop successfully.')
# Done rendering Scene 10

