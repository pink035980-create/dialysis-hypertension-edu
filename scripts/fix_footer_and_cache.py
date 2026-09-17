import re

# Template with anti-cache, mobile styling, and clean 2-line footer
footer_replacement = '''    <footer>
        <div class="footer-hospital">國立成功大學醫學院附設醫院 血液透析室</div>
        <div class="footer-phone">諮詢專線：<span class="nowrap">(06) 235-3535 分機 2591</span> ｜ 衛教版權所有</div>
    </footer>'''

meta_tags = '''    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">'''

extra_css = '''        .footer-hospital { font-weight: 700; margin-bottom: 4px; color: #475569; }
        .footer-phone { color: #64748b; font-size: 13px; }
        .nowrap { white-space: nowrap; }
        @media (max-width: 640px) {
            header h1 { font-size: 20px; line-height: 1.35; }
            header p { font-size: 13px; }
            .footer-hospital { font-size: 13px; }
            .footer-phone { font-size: 12px; }
            .player-info { flex-direction: column; align-items: flex-start; gap: 6px; }
        }'''

files = [
    r"C:\AI\影片製作_透析高血壓衛教\index.html",
    r"C:\Users\pink0\OneDrive\Desktop\【成大衛教多語影片】一鍵播放總目錄.html",
    r"C:\Users\pink0\OneDrive\Desktop\成大血液透析高血壓衛教_最終成果專區\成大透析衛教_一鍵播放與查閱總目錄.html",
    r"c:\Users\pink0\OneDrive\文件\antigravity\【成大衛教多語影片】一鍵播放總目錄.html",
    r"c:\Users\pink0\OneDrive\文件\antigravity\成大血液透析高血壓衛教_最終成果專區\成大透析衛教_一鍵播放與查閱總目錄.html"
]

for file_path in files:
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Add anti-cache meta if not present
    if "Cache-Control" not in html:
        html = html.replace("<head>", f"<head>\n{meta_tags}")

    # Add extra css if not present
    if ".footer-hospital" not in html:
        html = html.replace("footer { text-align: center;", f"{extra_css}\n        footer {{ text-align: center;")

    # Replace footer with 2-line clean layout
    html = re.sub(r'<footer>[\s\S]*?</footer>', footer_replacement, html)

    # Ensure no '完整衛教指導專書' card exists
    html = re.sub(r'<a class="doc-card" href="[^"]*完整衛教手冊\.docx" target="_blank">[\s\S]*?</a>\s*', '', html)
    html = re.sub(r'<a class="doc-card" href="[^"]*" target="_blank">\s*<div class="doc-icon">📁</div>[\s\S]*?</a>\s*', '', html)
    html = html.replace("成大標準版型衛教單張與完整指導手冊", "成大標準版型衛教單張")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Updated: {file_path}")

