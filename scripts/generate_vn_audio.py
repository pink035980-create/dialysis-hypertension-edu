import os, sys, subprocess, json, asyncio
import edge_tts

out_dir = r"C:\AI\影片製作_透析高血壓衛教\output"
os.makedirs(out_dir, exist_ok=True)

vn_segments = [
    {
        "step": 0,
        "text": "Xin kính chào quý bệnh nhân lọc máu và các anh chị người chăm sóc! Chào mừng quý vị đến với chuyên mục hướng dẫn sức khỏe của Khoa Lọc Máu, Bệnh viện Đại học Quốc gia Thành Công.",
        "zh_sub": "各位腎友與照護者大家好！歡迎收看成大透析室衛教專欄",
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

async def main():
    audio_files = []
    durations = []
    for i, seg in enumerate(vn_segments):
        fpath = os.path.join(out_dir, f"vn_part_{i}.mp3")
        tts = edge_tts.Communicate(seg["text"], "vi-VN-HoaiMyNeural", rate="+4%")
        await tts.save(fpath)
        
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", fpath]
        dur = float(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip())
        durations.append(dur)
        audio_files.append(fpath)
        print(f"Part {i}: {dur:.2f}s")
        
    filter_str = ""
    concat_str = ""
    for i, f in enumerate(audio_files):
        filter_str += f"[{i}:a]apad=pad_dur=0.3[a{i}];"
        concat_str += f"[a{i}]"
    filter_str += f"{concat_str}concat=n={len(audio_files)}:v=0:a=1[aout]"

    combined_audio = os.path.join(out_dir, "vn_scene01_combined.mp3")
    cmd_concat = ["ffmpeg", "-y"]
    for f in audio_files:
        cmd_concat.extend(["-i", f])
    cmd_concat.extend(["-filter_complex", filter_str, "-map", "[aout]", combined_audio])
    subprocess.run(cmd_concat, check=True)

    cmd_probe = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", combined_audio]
    total_duration = float(subprocess.run(cmd_probe, capture_output=True, text=True, check=True).stdout.strip())
    print(f"Total Combined Audio Duration: {total_duration:.2f}s")

    timings = []
    cur_t = 0.0
    for i, dur in enumerate(durations):
        st = cur_t
        et = cur_t + dur + 0.3
        timings.append({
            "start": round(st, 2),
            "end": round(et, 2),
            "step": vn_segments[i]["step"],
            "zh_sub": vn_segments[i]["zh_sub"],
            "vn_sub": vn_segments[i]["vn_sub"]
        })
        cur_t = et

    timing_path = os.path.join(out_dir, "vn_scene01_timings.json")
    with open(timing_path, "w", encoding="utf-8") as f:
        json.dump({"total_duration": total_duration, "timings": timings}, f, ensure_ascii=False, indent=2)
    print("Timings saved:", timing_path)

if __name__ == "__main__":
    asyncio.run(main())
