import os, sys, subprocess, math, json, shutil
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

brain_dir = r"C:\Users\pink0\.gemini\antigravity\brain\a835a13b-300f-4228-9146-ed73f327da63"
output_dir = r"C:\AI\影片製作_透析高血壓衛教\output"
desk_dir = r"C:\Users\pink0\OneDrive\Desktop"

timing_path = os.path.join(output_dir, "vn_scene01_timings.json")
with open(timing_path, "r", encoding="utf-8") as f:
    timing_data = json.load(f)

total_duration = timing_data["total_duration"]
timings = timing_data["timings"]
combined_audio = os.path.join(output_dir, "vn_scene01_combined.mp3")

p1_path = os.path.join(brain_dir, 's1_p1_welcome_1789452963599.jpg')
p2_path = os.path.join(brain_dir, 's10_p1_bp_clean_1789452006932.jpg')
p3_path = os.path.join(brain_dir, 's10_p2_weight_1789452027876.jpg')
p4_path = os.path.join(brain_dir, 's10_p4_adherence_1789452061044.jpg')

panel_size = 405
spacing = 26
total_w = panel_size * 4 + spacing * 3
start_x = (1920 - total_w) // 2

panel_y = 150
badge_h = 54
badge_y = 92
card_y = 560
card_h = 216
bot_y1 = 786
bot_y2 = 886
sub_bg_y1 = 896
sub_bg_y2 = 992

im1 = Image.open(p1_path).convert('RGB').resize((panel_size, panel_size), Image.Resampling.LANCZOS)
im2 = Image.open(p2_path).convert('RGB').resize((panel_size, panel_size), Image.Resampling.LANCZOS)
im3 = Image.open(p3_path).convert('RGB').resize((panel_size, panel_size), Image.Resampling.LANCZOS)
im4 = Image.open(p4_path).convert('RGB').resize((panel_size, panel_size), Image.Resampling.LANCZOS)
raw_panels = [im1, im2, im3, im4]
dim_enhancer = [ImageEnhance.Brightness(im).enhance(0.55) for im in raw_panels]

font_zh_path = r'C:\Windows\Fonts\msjhbd.ttc'
font_vn_bold = r'C:\Windows\Fonts\arialbd.ttf'

f_header = ImageFont.truetype(font_zh_path, 34)
f_sub = ImageFont.truetype(font_zh_path, 20)
f_badge = ImageFont.truetype(font_zh_path, 19)
f_step_tag = ImageFont.truetype(font_zh_path, 25)
f_card_sub = ImageFont.truetype(font_zh_path, 24)
f_card_body = ImageFont.truetype(font_zh_path, 22)
f_bot_title = ImageFont.truetype(font_zh_path, 25)
f_bot_body = ImageFont.truetype(font_zh_path, 22)

f_sub_zh = ImageFont.truetype(font_zh_path, 28)
f_sub_vn = ImageFont.truetype(font_vn_bold, 24)
f_tag_vn = ImageFont.truetype(font_vn_bold, 18)

steps_meta = [
    {
        'title': '歡迎：成大衛教專欄',
        'sub': '【溫馨叮嚀・安心透析】',
        'lines': [
            '• 各位腎友與照護者好！',
            '• 成大血液透析室衛教專欄',
            '• 掌握透析控壓三大法寶'
        ],
        'color': (33, 115, 175),
        'bg_card': (242, 248, 255)
    },
    {
        'title': '法寶 1：居家量七二二',
        'sub': '【早晚記錄・掌握真實】',
        'lines': [
            '• 連續量 7 天、早晚各 1 次',
            '• 每次量 2 遍取平均記錄',
            '• 記錄本帶來透析室供評估'
        ],
        'color': (35, 145, 75),
        'bg_card': (242, 255, 246)
    },
    {
        'title': '法寶 2：水分體重管理',
        'sub': '【體重不超五・嚴防積水】',
        'lines': [
            '• 兩次洗腎間增幅 ＜ 5%',
            '• 限水先限鹽、禁用低鈉鹽',
            '• 保護心臟、預防肺積水'
        ],
        'color': (215, 90, 15),
        'bg_card': (255, 250, 242)
    },
    {
        'title': '法寶 3：降壓藥按時吃',
        'sub': '【安全服藥・遵從醫囑】',
        'lines': [
            '• 每天固定服藥不擅自停藥',
            '• 洗腎日早晨遵照醫師指示',
            '• 醫護同行陪伴健康長久'
        ],
        'color': (125, 45, 150),
        'bg_card': (253, 245, 255)
    }
]

def render_frame_for_time(t):
    active_step = 0
    cur_zh = ""
    cur_vn = ""
    for seg in timings:
        if seg["start"] <= t <= seg["end"]:
            active_step = seg["step"]
            cur_zh = seg["zh_sub"]
            cur_vn = seg["vn_sub"]
            break
            
    pulse = 0.5 + 0.5 * math.sin(t * math.pi * 2.5)
    
    canvas = Image.new('RGB', (1920, 1080), (243, 246, 250))
    draw = ImageDraw.Draw(canvas)
    
    draw.rectangle([0, 0, 1920, 88], fill=(20, 70, 115))
    badge_text = '【透析室高血壓專題・多語衛教】'
    tw = draw.textlength(badge_text, font=f_badge)
    draw.rounded_rectangle([(60, 8), (60 + tw + 20, 36)], radius=8, fill='#E3F2FD')
    draw.text((70, 11), badge_text, font=f_badge, fill='#0D47A1')
    draw.text((60 + tw + 32, 11), '國立成功大學醫學院附設醫院 血液透析室', font=f_sub, fill=(180, 220, 250))
    draw.text((60, 43), '【總覽開場】掌握透析控壓三大法寶：量血壓・管體重・遵醫囑！', font=f_header, fill=(255, 255, 255))
    
    for i, meta in enumerate(steps_meta):
        px = start_x + i * (panel_size + spacing)
        is_cur = (i == active_step)
        is_finale = (active_step == -1)
        
        badge_bg = meta['color'] if (is_cur or is_finale) else (205, 215, 225)
        badge_tc = (255, 255, 255) if (is_cur or is_finale) else (110, 125, 140)
        draw.rounded_rectangle([px, badge_y, px + panel_size, badge_y + badge_h], radius=14, fill=badge_bg)
        tw = draw.textlength(meta['title'], font=f_step_tag)
        draw.text((px + (panel_size - tw)/2, badge_y + 11), meta['title'], font=f_step_tag, fill=badge_tc)
        
        if i < 3:
            ax = px + panel_size + spacing / 2
            ay = badge_y + badge_h / 2
            arr_c = (80, 100, 120) if (active_step > i or is_finale) else (185, 195, 210)
            draw.polygon([(ax - 9, ay - 12), (ax + 9, ay), (ax - 9, ay + 12)], fill=arr_c)
            
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
        
        card_bg = meta['bg_card'] if (is_cur or is_finale) else (248, 250, 252)
        card_bord = meta['color'] if (is_cur or is_finale) else (215, 225, 235)
        card_lw = 4 if (is_cur or is_finale) else 2
        draw.rounded_rectangle([px, card_y, px + panel_size, card_y + card_h], radius=16, fill=card_bg, outline=card_bord, width=card_lw)
        
        sw = draw.textlength(meta['sub'], font=f_card_sub)
        sub_c = meta['color'] if (is_cur or is_finale) else (120, 135, 150)
        draw.text((px + (panel_size - sw)/2, card_y + 13), meta['sub'], font=f_card_sub, fill=sub_c)
        
        line_y = card_y + 52
        for line in meta['lines']:
            text_c = (35, 45, 55) if (is_cur or is_finale) else (140, 150, 160)
            draw.text((px + 20, line_y), line, font=f_card_body, fill=text_c)
            line_y += 38
            
    # Bottom Reminder Banner
    draw.rounded_rectangle([start_x, bot_y1, start_x + total_w, bot_y2], radius=14, fill=(255, 252, 242), outline=(243, 156, 18), width=3)
    b_title = "成大衛教重點"
    tw = draw.textlength(b_title, font=f_bot_title)
    bw = max(220, int(tw + 40))
    bx = start_x + 20
    by = bot_y1 + 12
    bh = 76
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12, fill=(243, 156, 18))
    draw.text((bx + (bw - tw) / 2, by + (bh - 25) / 2), b_title, font=f_bot_title, fill=(255, 255, 255))
    
    rx = bx + bw + 20
    draw.text((rx, bot_y1 + 10), '① 居家定時量測 722 掌握真實血壓！連續量 7 天、早晚各 2 遍取平均值', font=f_bot_body, fill=(40, 50, 60))
    draw.text((rx, bot_y1 + 40), '② 乾體重增幅嚴格控制小於 5%，飲食限鹽先限水，嚴禁食用高鉀低鈉鹽！', font=f_bot_body, fill=(185, 40, 25))
    draw.text((rx, bot_y1 + 70), '★ 成大醫院血液透析室諮詢專線：(06) 235-3535 分機 2591・專業團隊守護健康', font=f_bot_body, fill=(24, 76, 120))
    
    # Subtitles
    draw.rounded_rectangle([140, sub_bg_y1, 1920 - 140, sub_bg_y2], radius=16, fill=(15, 23, 42, 240), outline=(56, 189, 248), width=2)
    
    tag_str = "TIẾNG VIỆT"
    lw = draw.textlength(tag_str, font=f_tag_vn)
    badge_w = lw + 32
    draw.rounded_rectangle([165, sub_bg_y1 + 22, 165 + badge_w, sub_bg_y1 + 66], radius=10, fill=(225, 29, 72))
    draw.text((165 + 16, sub_bg_y1 + 31), tag_str, font=f_tag_vn, fill=(255, 255, 255))
    
    if cur_zh:
        zh_w = draw.textlength(cur_zh, font=f_sub_zh)
        vn_w = draw.textlength(cur_vn, font=f_sub_vn)
        center_x = (1920 + 200) // 2
        draw.text((center_x - zh_w / 2, sub_bg_y1 + 12), cur_zh, font=f_sub_zh, fill=(255, 255, 255))
        draw.text((center_x - vn_w / 2, sub_bg_y1 + 52), cur_vn, font=f_sub_vn, fill=(254, 240, 138))
        
    return canvas

fps = 25
total_frames = int(fps * total_duration)
out_video = os.path.join(output_dir, "樣片_第1幕_越南語醫療解說中越雙語版_上移優化版.mp4")

cmd_render = [
    'ffmpeg', '-y',
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-s', '1920x1080',
    '-pix_fmt', 'rgb24',
    '-r', str(fps),
    '-i', '-',
    '-i', combined_audio,
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-preset', 'fast',
    '-crf', '19',
    '-c:a', 'aac',
    '-b:a', '192k',
    '-shortest',
    out_video
]

print(f"Rendering {total_frames} frames to {out_video}...")
proc = subprocess.Popen(cmd_render, stdin=subprocess.PIPE)
for f_idx in range(total_frames):
    t = f_idx / fps
    frame = render_frame_for_time(t)
    proc.stdin.write(frame.tobytes())
proc.stdin.close()
proc.wait()

desk_copy = os.path.join(desk_dir, "血液透析高血壓衛教_越南語醫療解說雙語示範樣片.mp4")
shutil.copy2(out_video, desk_copy)
subprocess.run(['attrib', '+p', '-u', desk_copy], shell=True)
print("Updated video copied to Desktop successfully!")
