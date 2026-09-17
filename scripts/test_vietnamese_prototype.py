import os, sys, subprocess, math
import asyncio
import edge_tts
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

brain_dir = r"C:\Users\pink0\.gemini\antigravity\brain\a835a13b-300f-4228-9146-ed73f327da63"
output_dir = r"C:\AI\影片製作_透析高血壓衛教\output"
desk_dir = r"C:\Users\pink0\OneDrive\Desktop"
os.makedirs(output_dir, exist_ok=True)

# 1. Generate Vietnamese Audio segments with timing
# Voice: vi-VN-HoaiMyNeural (Warm, professional Vietnamese female healthcare provider)
vn_segments = [
    {
        "step": 0,
        "text": "Xin kính chào quý bệnh nhân lọc máu và các anh chị người chăm sóc! Chào mừng quý vị đến với chuyên mục hướng dẫn sức khỏe của Khoa Lọc Máu, Bệnh viện Đại học Quốc gia Thành Công.",
        "zh_sub": "各位腎友與照護者大家好！歡迎收看成大醫院血液透析室衛教專欄",
        "vn_sub": "Kính chào quý bệnh nhân và người chăm sóc! Chào mừng đến với Khoa Lọc Máu NCKUH"
    },
    {
        "step": 1,
        "text": "Để kiểm soát huyết áp hiệu quả, xin hãy ghi nhớ ba bí quyết vàng: Thứ nhất, thực hiện đo huyết áp tại nhà theo nguyên tắc bảy hai hai.",
        "zh_sub": "掌握三大法寶：第一，落實居家血壓七二二",
        "vn_sub": "Nắm vững 3 bí quyết: Thứ nhất, đo huyết áp tại nhà theo nguyên tắc 722"
    },
    {
        "step": 2,
        "text": "Thứ hai, kiểm soát cân nặng khô, mức tăng giữa hai lần lọc máu phải dưới năm phần trăm.",
        "zh_sub": "第二，乾體重增幅小於百分之五",
        "vn_sub": "Thứ hai, mức tăng cân giữa hai lần lọc máu dưới 5%"
    },
    {
        "step": 3,
        "text": "Thứ ba, uống thuốc hạ huyết áp đúng giờ và đều đặn theo chỉ định của bác sĩ.",
        "zh_sub": "第三，降壓藥規律按時服用",
        "vn_sub": "Thứ ba, uống thuốc hạ huyết áp đúng giờ theo chỉ định của bác sĩ"
    },
    {
        "step": -1,
        "text": "Chúng ta hãy cùng nhau bảo vệ tim và thận, giữ cho huyết áp luôn ổn định và an toàn!",
        "zh_sub": "讓我們一起護腎保心、血壓穩妥當！",
        "vn_sub": "Hãy cùng nhau bảo vệ tim thận, giữ huyết áp luôn ổn định và an toàn!"
    }
]

async def gen_audio():
    audio_files = []
    durations = []
    for i, seg in enumerate(vn_segments):
        fpath = os.path.join(output_dir, f"vn_part_{i}.mp3")
        tts = edge_tts.Communicate(seg["text"], "vi-VN-HoaiMyNeural", rate="+3%")
        await tts.save(fpath)
        
        # probe duration
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", fpath]
        dur = float(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip())
        durations.append(dur)
        audio_files.append(fpath)
        print(f"Part {i}: {dur:.2f}s")
    return audio_files, durations

audio_files, durations = asyncio.run(gen_audio())

# Combine audio with slight padding between phrases (0.4s)
filter_str = ""
concat_str = ""
for i, f in enumerate(audio_files):
    filter_str += f"[{i}:a]apad=pad_dur=0.4[a{i}];"
    concat_str += f"[a{i}]"
filter_str += f"{concat_str}concat=n={len(audio_files)}:v=0:a=1[aout]"

combined_audio = os.path.join(output_dir, "vn_scene01_combined.mp3")
cmd_concat = ["ffmpeg", "-y"]
for f in audio_files:
    cmd_concat.extend(["-i", f])
cmd_concat.extend(["-filter_complex", filter_str, "-map", "[aout]", combined_audio])
subprocess.run(cmd_concat, check=True)

# Probe combined audio total duration
cmd_probe = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", combined_audio]
total_duration = float(subprocess.run(cmd_probe, capture_output=True, text=True, check=True).stdout.strip())
print(f"Total Combined Audio Duration: {total_duration:.2f}s")

# Calculate timeline for video animation
timings = []
cur_t = 0.0
for i, dur in enumerate(durations):
    st = cur_t
    et = cur_t + dur + 0.4
    timings.append((st, et, vn_segments[i]))
    cur_t = et

# 2. Render Video Frames with Synchronized Bilingual Subtitles
p1_path = os.path.join(brain_dir, 's1_p1_welcome_1789452963599.jpg')
p2_path = os.path.join(brain_dir, 's10_p1_bp_clean_1789452006932.jpg')
p3_path = os.path.join(brain_dir, 's10_p2_weight_1789452027876.jpg')
p4_path = os.path.join(brain_dir, 's10_p4_adherence_1789452061044.jpg')

panel_size = 405
spacing = 26
total_w = panel_size * 4 + spacing * 3
start_x = (1920 - total_w) // 2
panel_y = 158
badge_h = 56
badge_y = 98
card_y = 575
card_h = 240
bot_y1 = 825
bot_y2 = 965

im1 = Image.open(p1_path).convert('RGB').resize((panel_size, panel_size), Image.Resampling.LANCZOS)
im2 = Image.open(p2_path).convert('RGB').resize((panel_size, panel_size), Image.Resampling.LANCZOS)
im3 = Image.open(p3_path).convert('RGB').resize((panel_size, panel_size), Image.Resampling.LANCZOS)
im4 = Image.open(p4_path).convert('RGB').resize((panel_size, panel_size), Image.Resampling.LANCZOS)
raw_panels = [im1, im2, im3, im4]
dim_enhancer = [ImageEnhance.Brightness(im).enhance(0.55) for im in raw_panels]

font_path = r'C:\Windows\Fonts\msjhbd.ttc'
font_vn_bold = r'C:\Windows\Fonts\arialbd.ttf'
font_vn_reg = r'C:\Windows\Fonts\arial.ttf'

f_header = ImageFont.truetype(font_path, 34)
f_sub = ImageFont.truetype(font_path, 20)
f_badge = ImageFont.truetype(font_path, 19)
f_step_tag = ImageFont.truetype(font_path, 26)
f_card_sub = ImageFont.truetype(font_path, 26)
f_card_body = ImageFont.truetype(font_path, 24)
f_bot_title = ImageFont.truetype(font_path, 26)
f_bot_body = ImageFont.truetype(font_path, 23)

f_sub_zh = ImageFont.truetype(font_path, 28)
f_sub_vn = ImageFont.truetype(font_vn_bold, 24)

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
    # Determine active step and current bilingual subtitles
    active_step = 0
    cur_zh = ""
    cur_vn = ""
    for st, et, seg in timings:
        if st <= t <= et:
            active_step = seg["step"]
            cur_zh = seg["zh_sub"]
            cur_vn = seg["vn_sub"]
            break
            
    pulse = 0.5 + 0.5 * math.sin(t * math.pi * 2.5)
    
    canvas = Image.new('RGB', (1920, 1080), (243, 246, 250))
    draw = ImageDraw.Draw(canvas)
    
    # Header
    draw.rectangle([0, 0, 1920, 90], fill=(20, 70, 115))
    badge_text = '【透析室高血壓專題・多語衛教】'
    tw = draw.textlength(badge_text, font=f_badge)
    draw.rounded_rectangle([(60, 8), (60 + tw + 20, 36)], radius=8, fill='#E3F2FD')
    draw.text((70, 11), badge_text, font=f_badge, fill='#0D47A1')
    draw.text((60 + tw + 32, 11), '國立成功大學醫學院附設醫院 血液透析室 (Khoa Lọc Máu NCKUH)', font=f_sub, fill=(180, 220, 250))
    draw.text((60, 44), '【總覽開場】掌握透析控壓三大法寶：量血壓・管體重・遵醫囑！', font=f_header, fill=(255, 255, 255))
    
    # 4 Panels
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
        
        # Card beneath
        card_bg = meta['bg_card'] if (is_cur or is_finale) else (248, 250, 252)
        card_bord = meta['color'] if (is_cur or is_finale) else (215, 225, 235)
        card_lw = 4 if (is_cur or is_finale) else 2
        draw.rounded_rectangle([px, card_y, px + panel_size, card_y + card_h], radius=16, fill=card_bg, outline=card_bord, width=card_lw)
        
        sw = draw.textlength(meta['sub'], font=f_card_sub)
        sub_c = meta['color'] if (is_cur or is_finale) else (120, 135, 150)
        draw.text((px + (panel_size - sw)/2, card_y + 14), meta['sub'], font=f_card_sub, fill=sub_c)
        
        line_y = card_y + 58
        for line in meta['lines']:
            text_c = (35, 45, 55) if (is_cur or is_finale) else (140, 150, 160)
            draw.text((px + 20, line_y), line, font=f_card_body, fill=text_c)
            line_y += 42
            
    # Bottom Reminder
    draw.rounded_rectangle([start_x, bot_y1, start_x + total_w, bot_y2], radius=14, fill=(255, 252, 242), outline=(243, 156, 18), width=3)
    b_title = "成大衛教重點"
    tw = draw.textlength(b_title, font=f_bot_title)
    bw = max(220, int(tw + 40))
    bx = start_x + 20
    by = bot_y1 + 14
    bh = 110
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12, fill=(243, 156, 18))
    draw.text((bx + (bw - tw) / 2, by + (bh - 28) / 2), b_title, font=f_bot_title, fill=(255, 255, 255))
    
    rx = bx + bw + 20
    draw.text((rx, bot_y1 + 14), '① 居家定時量測 722 掌握真實血壓！(Đo huyết áp tại nhà theo nguyên tắc 722)', font=f_bot_body, fill=(40, 50, 60))
    draw.text((rx, bot_y1 + 48), '② 乾體重增加不超 5%，嚴禁高鉀低鈉鹽！(Tăng cân < 5%, tuyệt đối không dùng muối giảm natri)', font=f_bot_body, fill=(185, 40, 25))
    draw.text((rx, bot_y1 + 82), '★ 成大醫院透析室電話：(06) 235-3535 分機 2591 (ĐT Khoa Lọc Máu Thành Công)', font=f_bot_body, fill=(24, 76, 120))
    
    # 4. Bilingual Subtitle Banner at the very bottom (y: 975 ~ 1070)
    sub_bg_y1 = 975
    sub_bg_y2 = 1068
    draw.rounded_rectangle([160, sub_bg_y1, 1920 - 160, sub_bg_y2], radius=14, fill=(15, 23, 42, 230), outline=(56, 189, 248), width=2)
    
    # Vietnamese Flag Icon or Language Badge on Left
    lang_badge = "🇻🇳 Tiếng Việt"
    lw = draw.textlength(lang_badge, font=f_sub)
    draw.rounded_rectangle([180, sub_bg_y1 + 18, 180 + lw + 24, sub_bg_y1 + 58], radius=8, fill=(225, 29, 72))
    draw.text((192, sub_bg_y1 + 22), lang_badge, font=f_sub, fill=(255, 255, 255))
    
    # Render Bilingual Text
    if cur_zh:
        zh_w = draw.textlength(cur_zh, font=f_sub_zh)
        vn_w = draw.textlength(cur_vn, font=f_sub_vn)
        center_x = (1920 + 200) // 2
        draw.text((center_x - zh_w / 2, sub_bg_y1 + 10), cur_zh, font=f_sub_zh, fill=(255, 255, 255))
        draw.text((center_x - vn_w / 2, sub_bg_y1 + 48), cur_vn, font=f_sub_vn, fill=(254, 240, 138))
        
    return canvas

fps = 25
total_frames = int(fps * total_duration)
out_video = os.path.join(output_dir, "樣片_第1幕_越南語醫療解說中越雙語版.mp4")

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
    if f_idx % 100 == 0:
        print(f"Rendered {f_idx}/{total_frames} frames (t={t:.1f}s)...")
proc.stdin.close()
proc.wait()

print(f"Demo video created: {out_video}")

# Copy to Desktop
desk_copy = os.path.join(desk_dir, "血液透析高血壓衛教_越南語醫療解說雙語示範樣片.mp4")
import shutil
shutil.copy2(out_video, desk_copy)
subprocess.run(['attrib', '+p', '-u', desk_copy], shell=True)
print(f"Copied to Desktop: {desk_copy}")
