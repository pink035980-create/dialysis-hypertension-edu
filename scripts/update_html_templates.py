import re

files_to_update = [
    r"C:\AI\影片製作_透析高血壓衛教\index.html",
    r"C:\Users\pink0\OneDrive\Desktop\【成大衛教多語影片】一鍵播放總目錄.html",
    r"C:\Users\pink0\OneDrive\Desktop\成大血液透析高血壓衛教_最終成果專區\成大透析衛教_一鍵播放與查閱總目錄.html",
    r"c:\Users\pink0\OneDrive\文件\antigravity\【成大衛教多語影片】一鍵播放總目錄.html",
    r"c:\Users\pink0\OneDrive\文件\antigravity\成大血液透析高血壓衛教_最終成果專區\成大透析衛教_一鍵播放與查閱總目錄.html"
]

for file_path in files_to_update:
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 1. Update title and header subtitle (remove '10 幕無縫' and '中心')
    text = re.sub(
        r"<p>血液透析患者高血壓預防與管理・.*?</p>",
        "<p>血液透析患者高血壓預防與管理・多語言衛教影片</p>",
        text
    )
    text = re.sub(
        r"<title>.*?</title>",
        "<title>成大醫院血液透析室・血液透析高血壓多語言衛教影片</title>",
        text
    )

    # 2. Remove the 4th card "瀏覽全部成果資料夾"
    text = re.sub(
        r'<a class="doc-card" href="[^"]*" target="_blank">\s*<div class="doc-icon">📁</div>\s*<div class="doc-text">\s*<div class="name">瀏覽全部成果資料夾</div>[\s\S]*?</a>\s*',
        '',
        text
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Successfully updated: {file_path}")
