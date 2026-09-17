import re

files = [
    r"C:\AI\影片製作_透析高血壓衛教\index.html",
    r"C:\Users\pink0\OneDrive\Desktop\【成大衛教多語影片】一鍵播放總目錄.html",
    r"C:\Users\pink0\OneDrive\Desktop\成大血液透析高血壓衛教_最終成果專區\成大透析衛教_一鍵播放與查閱總目錄.html",
    r"c:\Users\pink0\OneDrive\文件\antigravity\【成大衛教多語影片】一鍵播放總目錄.html",
    r"c:\Users\pink0\OneDrive\文件\antigravity\成大血液透析高血壓衛教_最終成果專區\成大透析衛教_一鍵播放與查閱總目錄.html"
]

for f in files:
    with open(f, "r", encoding="utf-8") as fp:
        content = fp.read()
    
    # 1. Update section title
    content = content.replace("<h2>📄 成大標準版型衛教單張與完整指導手冊</h2>", "<h2>📄 成大標準版型衛教單張</h2>")
    
    # 2. Remove '完整衛教指導專書 (全六篇)' card
    content = re.sub(r'<a class="doc-card" href="[^"]*完整衛教手冊\.docx" target="_blank">\s*<div class="doc-icon">📙</div>\s*<div class="doc-text">\s*<div class="name">完整衛教指導專書 \(全六篇\)</div>[\s\S]*?</a>\s*', '', content)
    
    # 3. Ensure '瀏覽全部成果資料夾' is also gone if present
    content = re.sub(r'<a class="doc-card" href="[^"]*" target="_blank">\s*<div class="doc-icon">📁</div>\s*<div class="doc-text">\s*<div class="name">瀏覽全部成果資料夾</div>[\s\S]*?</a>\s*', '', content)
    
    with open(f, "w", encoding="utf-8") as fp:
        fp.write(content)
    print(f"Successfully updated: {f}")
