import os, sys, subprocess, shutil

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"C:\AI\影片製作_透析高血壓衛教"
out_dir = os.path.join(base_dir, "output")
desk_dir = r"C:\Users\pink0\OneDrive\Desktop"
vid_dir = r"C:\Users\pink0\Videos"

# 10 Unified Japanese Manga Scenes with Pacing & Subtitle Synchronization
segments_info = [
    {
        'scene': 1,
        'name': '第 1 幕：片頭總覽',
        'file': os.path.join(out_dir, '樣片_第1幕_片頭總覽_日式衛教漫畫連續動作版.mp4'),
        'subtitles': [
            (0.1, 5.5, '各位腎友與家屬大家好！歡迎收看成大醫院血液透析室衛教專欄。'),
            (5.5, 10.5, '掌握三大法寶：第一，落實居家血壓七二二。'),
            (10.5, 15.0, '第二，乾體重增幅小於百分之五。'),
            (15.0, 19.5, '第三，降壓藥規律按時服用。'),
            (19.5, 24.5, '讓我們一起護腎保心、血壓穩妥當！')
        ]
    },
    {
        'scene': 2,
        'name': '第 2 幕：血壓標準值',
        'file': os.path.join(out_dir, '樣片_第2幕_血壓標準值_日式衛教漫畫連續動作版.mp4'),
        'subtitles': [
            (0.1, 6.5, '一般成年人的血壓標準，國健署建議小於 120/80 毫米汞柱。'),
            (6.5, 13.0, '但洗腎病友體液波動大，成大醫院建議診間血壓控制在小於 140/90。'),
            (13.0, 20.0, '而在家的居家血壓，維持在 120 到 135、60 到 80 最適當。'),
            (20.0, 27.8, '血壓不是越低越好，平穩最適當，預防心肌缺氧！')
        ]
    },
    {
        'scene': 3,
        'name': '第 3 幕：破除白袍緊張',
        'file': os.path.join(out_dir, '樣片_第3幕_破除白袍緊張_日式衛教漫畫連續動作版.mp4'),
        'subtitles': [
            (0.1, 5.5, '許多病友在洗腎室量的血壓起伏很大，容易有緊張的白袍效應。'),
            (5.5, 11.5, '在熟悉家中放鬆測量，更能精準反映心臟真實負擔。'),
            (11.5, 17.5, '詳細記錄居家血壓，能幫助醫療團隊精準調整治療計畫。'),
            (17.5, 23.5, '破除緊張、看見真實，居家量測最安心！')
        ]
    },
    {
        'scene': 4,
        'name': '第 4 幕：居家血壓722原則',
        'file': os.path.join(out_dir, '樣片_第4幕_居家血壓722原則_日式衛教漫畫連續動作版.mp4'),
        'subtitles': [
            (0.1, 5.0, '請大家務必牢記居家血壓黃金七二二原則！'),
            (5.0, 10.0, '七：連續測量七天，掌握一週血壓走勢。'),
            (10.0, 15.0, '二：每天早晚各量一次，晨起如廁後與睡前量。'),
            (15.0, 20.0, '二：每次量兩遍，間隔一分鐘取平均值。'),
            (20.0, 26.0, '血壓紀錄本請定期帶來透析室，由成大醫師評估指導！')
        ]
    },
    {
        'scene': 5,
        'name': '第 5 幕：心臟像氣球',
        'file': os.path.join(out_dir, '樣片_第5幕_心臟像氣球_日式衛教漫畫連續動作版.mp4'),
        'subtitles': [
            (0.1, 5.2, '第二個關鍵是乾體重管理。我們的心臟就像一顆氣球。'),
            (5.2, 11.5, '洗腎間如果喝水過量，氣球被反覆吹大，心臟彈性疲乏、血壓飆高！'),
            (11.5, 17.5, '而如果洗腎脫水太急促，又容易引發肌肉抽筋與低血壓。'),
            (17.5, 26.2, '唯有維持乾體重水分平衡，才能保護心臟、長青健康！')
        ]
    },
    {
        'scene': 6,
        'name': '第 6 幕：體重增幅不超5%',
        'file': os.path.join(out_dir, '樣片_第6幕_體重增幅不超5趴_日式衛教漫畫連續動作版.mp4'),
        'subtitles': [
            (0.1, 6.0, '因此，兩次洗腎之間的體重增加，必須嚴格控制在百分之五以內。'),
            (6.0, 13.0, '以乾體重六十公斤為例，最多只能增加三公斤，相當於三瓶一千西西飲用水。'),
            (13.0, 18.5, '每天清晨固定量體重，及早掌握水分變化。'),
            (18.5, 25.8, '體重達標，洗腎輕鬆順暢不抽筋，守護心臟無負擔！')
        ]
    },
    {
        'scene': 7,
        'name': '第 7 幕：控水控鹽嚴禁低鈉鹽',
        'file': os.path.join(out_dir, '樣片_第7幕_控水先控鹽嚴禁低鈉鹽_日式衛教漫畫連續動作版.mp4'),
        'subtitles': [
            (0.1, 6.0, '想要成功控水，一定要先控鹽！每日食鹽量控制在五公克以內。'),
            (6.0, 11.5, '每天食鹽約一平匙，少吃醃漬加工高鹽食品。'),
            (11.5, 19.5, '特別鄭重警告：洗腎病友嚴禁食用低鈉鹽與美味鹽，高鉀會引發猝死！'),
            (19.5, 28.8, '多利用青蔥、生薑、大蒜與鮮黃檸檬等天然辛香食材提味，減鹽美味又安心！')
        ]
    },
    {
        'scene': 8,
        'name': '第 8 幕：口渴不灌水四大妙招',
        'file': os.path.join(out_dir, '樣片_第8幕_口渴不灌水四大妙招_日式衛教漫畫連續動作版.mp4'),
        'subtitles': [
            (0.1, 5.5, '平時如果覺得口渴，切勿大口灌水。第一招：口含薄檸檬片。'),
            (5.5, 10.5, '第二招：含一小塊冰塊在口中慢慢融化。'),
            (10.5, 15.5, '第三招：嚼無糖口香糖促進唾液分泌。'),
            (15.5, 20.5, '第四招：用常溫清水漱口後吐掉，有效解渴。'),
            (20.5, 26.6, '靈活運用四妙招，輕鬆告別口乾煩惱！')
        ]
    },
    {
        'scene': 9,
        'name': '第 9 幕：服藥動作四部曲',
        'file': os.path.join(out_dir, '樣片_第9幕_服藥動作四部曲_日式衛教漫畫連續動作版.mp4'),
        'subtitles': [
            (0.1, 6.2, '第三招：降壓藥按時服！第一步，核對當天透明藥格。'),
            (6.2, 12.3, '第二步，手拿處方籤核對劑量，取出藥盒內的藥物，放於手掌心。'),
            (12.3, 17.4, '第三步，配常溫開水順暢嚥下，放緩動作防嗆咳。'),
            (17.4, 20.4, '第四步，撫胸順氣比個讚！'),
            (20.4, 25.0, '血壓正常是藥物在保護，絕不擅自停藥；洗腎早晨遵醫囑！')
        ]
    },
    {
        'scene': 10,
        'name': '第 10 幕：控壓四句訣大結語',
        'file': os.path.join(out_dir, '樣片_第10幕_控壓四字訣日式衛教漫畫連續動作版.mp4'),
        'subtitles': [
            (0.1, 3.9, '最後讓我們複習血液透析控壓四句訣！'),
            (3.9, 9.7, '第一，居家量七二二：連續七天、早晚量、各量兩遍。'),
            (9.7, 14.8, '第二，體重不超五：兩次洗腎間增幅小於百分之五。'),
            (14.8, 20.6, '第三，減鹽忌低鈉：每天鹽分少於五公克，嚴禁低鈉鹽。'),
            (20.6, 26.3, '第四，服藥遵醫囑：規律服藥不擅停，洗腎早晨遵醫囑。'),
            (26.3, 34.5, '成大醫院護理部與血液透析室，陪伴您安心透析、健康同行！')
        ]
    }
]

print("Verifying 10 unified manga segments...")
actual_durations = []
for seg in segments_info:
    fpath = seg['file']
    if not os.path.exists(fpath):
        raise FileNotFoundError(f"Missing segment file: {fpath}")
    probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', fpath]
    dur = float(subprocess.run(probe_cmd, capture_output=True, text=True, check=True).stdout.strip())
    actual_durations.append(dur)
    seg['actual_duration'] = dur
    print(f"  {seg['name']}: {dur:.2f}s ({fpath})")

total_length = sum(actual_durations)
print(f"\nTotal video length: {total_length:.2f}s ({total_length/60:.2f} minutes)")

inputs = []
filter_parts = []
for i, seg in enumerate(segments_info):
    inputs.extend(['-i', seg['file']])
    filter_parts.append(f"[{i}:v]fps=30,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[v{i}];")
    filter_parts.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo[a{i}];")

concat_inputs = "".join(f"[v{i}][a{i}]" for i in range(len(segments_info)))
concat_filter = "".join(filter_parts) + f"{concat_inputs}concat=n={len(segments_info)}:v=1:a=1[vout][aout]"

master_out = os.path.join(out_dir, "血液透析患者高血壓衛教_全片10幕無縫完整版_日式衛教漫畫風.mp4")

cmd_concat = [
    'ffmpeg', '-y',
    *inputs,
    '-filter_complex', concat_filter,
    '-map', '[vout]',
    '-map', '[aout]',
    '-c:v', 'libx264',
    '-preset', 'medium',
    '-crf', '18',
    '-pix_fmt', 'yuv420p',
    '-c:a', 'aac',
    '-b:a', '192k',
    master_out
]

print("\nStarting seamless broadcast-grade concatenation of all 10 unified scenes...")
subprocess.run(cmd_concat, check=True)
print(f"Master video rendered successfully: {master_out}")

# Build Full Master SRT Subtitles
def format_srt_time(sec):
    hrs = int(sec // 3600)
    mins = int((sec % 3600) // 60)
    secs = int(sec % 60)
    millis = int(round((sec - int(sec)) * 1000))
    if millis >= 1000:
        millis = 999
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

master_srt = os.path.join(out_dir, "血液透析患者高血壓衛教_全片10幕無縫完整版_日式衛教漫畫風.srt")
srt_counter = 1
timeline_offset = 0.0

with open(master_srt, 'w', encoding='utf-8') as f_srt:
    for seg in segments_info:
        for (st, et, txt) in seg['subtitles']:
            start_str = format_srt_time(timeline_offset + st)
            end_str = format_srt_time(timeline_offset + et)
            f_srt.write(f"{srt_counter}\n")
            f_srt.write(f"{start_str} --> {end_str}\n")
            f_srt.write(f"{txt}\n\n")
            srt_counter += 1
        timeline_offset += seg['actual_duration']

print(f"Master SRT subtitle generated successfully: {master_srt}")

# Deploy to Desktop and Videos folder
dst_master_desk = os.path.join(desk_dir, "血液透析患者高血壓衛教_全片10幕無縫完整版_日式衛教漫畫風.mp4")
dst_srt_desk = os.path.join(desk_dir, "血液透析患者高血壓衛教_全片10幕無縫完整版_日式衛教漫畫風.srt")
dst_master_vid = os.path.join(vid_dir, "血液透析患者高血壓衛教_全片10幕無縫完整版_日式衛教漫畫風.mp4")

shutil.copy2(master_out, dst_master_desk)
shutil.copy2(master_srt, dst_srt_desk)
try:
    shutil.copy2(master_out, dst_master_vid)
except Exception:
    pass

subprocess.run(['attrib', '+p', '-u', dst_master_desk], shell=True)
subprocess.run(['attrib', '+p', '-u', dst_srt_desk], shell=True)

print("Deployed master video & subtitle to desktop successfully:")
print("  " + dst_master_desk)
print("  " + dst_srt_desk)
