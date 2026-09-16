import os, sys, subprocess, time, shutil

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"C:\Users\pink0\.gemini\antigravity\brain\a835a13b-300f-4228-9146-ed73f327da63\scratch"
master_script = os.path.join(base_dir, "build_unified_manga_master.py")

scenes = [
    ("第 1 幕", os.path.join(base_dir, "render_scene01_manga.py")),
    ("第 2 幕", os.path.join(base_dir, "render_scene02_manga.py")),
    ("第 3 幕", os.path.join(base_dir, "render_scene03_manga.py")),
    ("第 4 幕", os.path.join(base_dir, "render_scene04_manga.py")),
    ("第 5 幕", os.path.join(base_dir, "render_scene05_manga.py")),
    ("第 6 幕", os.path.join(base_dir, "render_scene06_manga.py")),
    ("第 7 幕", os.path.join(base_dir, "render_scene07_manga.py")),
    ("第 8 幕", os.path.join(base_dir, "render_scene08_manga.py")),
    ("第 9 幕", os.path.join(base_dir, "render_scene09_manga.py")),
    ("第 10 幕", os.path.join(base_dir, "render_scene10_manga.py")),
]

t0 = time.time()

print("==================================================")
print("開始全自動批次渲染 10 幕日式衛教漫畫影片（左上角標籤統一）...")
print("==================================================")

for name, script_path in scenes:
    print(f"\n>>> 正在渲染【{name}】: {os.path.basename(script_path)} ...")
    s_t = time.time()
    res = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    if res.returncode != 0:
        print(f"ERROR rendering {name}:")
        print(res.stderr)
        sys.exit(1)
    print(f"--- 【{name}】渲染完成！耗時: {time.time() - s_t:.1f} 秒")

print("\n==================================================")
print("全數 10 幕個別樣片渲染完成！開始執行最終無縫總母帶串接...")
print("==================================================")

m_t = time.time()
res = subprocess.run(
    [sys.executable, master_script],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace'
)
if res.returncode != 0:
    print("ERROR in master build:")
    print(res.stderr)
    sys.exit(1)
print(res.stdout)
print(f"--- 總母帶無縫串接完成！耗時: {time.time() - m_t:.1f} 秒")

master_file = r"C:\Users\pink0\OneDrive\Desktop\血液透析患者高血壓衛教_全片10幕無縫完整版_日式衛教漫畫風.mp4"
if os.path.exists(master_file):
    print(f"\n[OK] 最終總母帶已成功更新至桌面: {master_file}")
    print(f"檔案大小: {os.path.getsize(master_file) / (1024*1024):.2f} MB")
    print(f"總耗時: {time.time() - t0:.1f} 秒")
    print("正在自動喚醒本機播放器...")
    os.startfile(master_file)
    print("播放器已啟動！")
else:
    print(f"[Warning] 找不到桌面母帶檔案: {master_file}")
