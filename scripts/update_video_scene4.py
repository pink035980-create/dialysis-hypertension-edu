import os
import subprocess
import shutil

base_dir = r"C:\AI\影片製作_透析高血壓衛教"
audio_dir = os.path.join(base_dir, "audio")
slides_dir = os.path.join(base_dir, "slides")
out_dir = os.path.join(base_dir, "output")

tts_exe = os.path.expandvars(r"%USERPROFILE%\.ai-voice\.venv\Scripts\edge-tts.exe")

# 1. Regenerate Scene 4 Audio with explicit 七二二
scene4_text = "請大家牢記居家血壓七二二原則：連續測量 7 天；每天早晚各量 1 次；每次量 2 遍取平均值。居家血壓建議目標維持在收縮壓 120 到 135、舒張壓 60 到 80 之間，並請把紀錄本帶來透析室給醫師參考。"
scene4_audio = os.path.join(audio_dir, "scene_04.mp3")

cmd_tts = [
    tts_exe,
    "--voice", "zh-TW-HsiaoChenNeural",
    "--text", scene4_text,
    "--write-media", scene4_audio
]
subprocess.run(cmd_tts, check=True)
print("Regenerated scene_04.mp3 with 七二二 (qi-er-er)")

# Measure scene 4 duration
cmd_probe = [
    "ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1", scene4_audio
]
res = subprocess.run(cmd_probe, capture_output=True, text=True, check=True)
dur4 = float(res.stdout.strip())
print(f"Scene 04 new duration: {dur4:.2f}s")

# Durations dictionary
durations = {
    1: 13.92,
    2: 20.57,
    3: 15.62,
    4: dur4,
    5: 17.52,
    6: 15.50,
    7: 18.98,
    8: 13.70,
    9: 16.49,
    10: 15.02
}

# 2. Render segment_v2_04.mp4
seg4_out = os.path.join(out_dir, "segment_v2_04.mp4")
slide4_img = os.path.join(slides_dir, "slide_04.png")
cmd_seg4 = [
    "ffmpeg", "-y",
    "-loop", "1", "-i", slide4_img,
    "-i", scene4_audio,
    "-c:v", "libx264", "-tune", "stillimage",
    "-c:a", "aac", "-b:a", "192k",
    "-pix_fmt", "yuv420p",
    "-t", str(dur4),
    seg4_out
]
subprocess.run(cmd_seg4, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("Re-rendered segment_v2_04.mp4")

# 3. Concatenate master video
concat_list_path = os.path.join(base_dir, "concat_list_v2.txt")
with open(concat_list_path, "w", encoding="utf-8") as cl:
    for i in range(1, 11):
        seg = os.path.join(out_dir, f"segment_v2_{i:02d}.mp4").replace("\\", "/")
        cl.write(f"file '{seg}'\n")

master_mp4 = os.path.join(out_dir, "血液透析高血壓衛教_無字幕_v2.mp4")
cmd_concat = [
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0",
    "-i", concat_list_path,
    "-c", "copy",
    master_mp4
]
subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("Master video concatenated successfully!")

# 4. Generate updated SRT file with exact timestamps
key_subtitles = [
    (1, "護腎保心・血液透析 3 分鐘控壓自我照護秘笈"),
    (2, "診間血壓 ＜ 140/90 mmHg・居家血壓 120～135/60～80 mmHg"),
    (3, "破除洗腎室白袍緊張・居家測量血壓數值最真實"),
    (4, "居家量血壓 722 原則：連續 7 天・早晚各 1 次・每次量 2 遍"),
    (5, "心臟像氣球：嚴防水分過多水腫・洗腎避免脫水太急"),
    (6, "兩次洗腎間體重增加 ＜ 乾體重 5%（60kg 最多 3kg）"),
    (7, "每日食鹽 ＜ 5 公克・嚴禁食用低鈉鹽、美味鹽（防高血鉀猝死）"),
    (8, "解渴 4 妙招：含薄檸檬片、含小冰塊、嚼無糖口香糖、漱口"),
    (9, "降壓藥按時服不擅停・洗腎當天服藥遵照醫囑"),
    (10, "控壓四字訣：722、＜5%、忌低鈉、遵醫囑・健康同行")
]

def format_timestamp(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

full_srt_path = os.path.join(out_dir, "血液透析高血壓衛教.srt")
cur_time = 0.0
with open(full_srt_path, "w", encoding="utf-8") as srt_f:
    for idx, text in key_subtitles:
        d_val = durations[idx]
        start_t = cur_time
        end_t = cur_time + d_val
        srt_f.write(f"{idx}\n")
        srt_f.write(f"{format_timestamp(start_t)} --> {format_timestamp(end_t)}\n")
        srt_f.write(f"{text}\n\n")
        cur_time = end_t

print(f"Updated SRT created: {full_srt_path}")

# 5. Burn subtitles (FontSize 18, Outline 1.5, transparent shadow, clean positioning)
subbed_mp4 = os.path.join(out_dir, "血液透析高血壓衛教_3分鐘完整版.mp4")
srt_filter_path = full_srt_path.replace("\\", "/").replace(":", "\\:")
cmd_burn = [
    "ffmpeg", "-y",
    "-i", master_mp4,
    "-vf", f"subtitles='{srt_filter_path}':force_style='FontSize=18,FontName=Microsoft JhengHei,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00111111,BorderStyle=1,Outline=1.5,Shadow=1,MarginV=18'",
    "-c:a", "copy",
    subbed_mp4
]
subprocess.run(cmd_burn, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"Burned video recreated: {subbed_mp4}")

# 6. Copy to Desktop & Downloads
desk_dir = os.path.expandvars(r"%USERPROFILE%\OneDrive\Desktop")
if not os.path.exists(desk_dir):
    desk_dir = os.path.expandvars(r"%USERPROFILE%\Desktop")
down_dir = os.path.expandvars(r"%USERPROFILE%\Downloads")

dest_video_desk = os.path.join(desk_dir, "血液透析高血壓衛教_3分鐘完整版.mp4")
dest_video_down = os.path.join(down_dir, "血液透析高血壓衛教_3分鐘完整版.mp4")
dest_srt_desk = os.path.join(desk_dir, "血液透析高血壓衛教.srt")
dest_srt_down = os.path.join(down_dir, "血液透析高血壓衛教.srt")

shutil.copy2(subbed_mp4, dest_video_desk)
shutil.copy2(subbed_mp4, dest_video_down)
shutil.copy2(full_srt_path, dest_srt_desk)
shutil.copy2(full_srt_path, dest_srt_down)

print("Copied updated video & SRT to Desktop and Downloads!")
print("ALL DONE!")
