import os
import sys
import shutil
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from PIL import Image, ImageDraw, ImageFont

base_dir = r"C:\AI\影片製作_透析高血壓衛教"
desk_dir = os.path.expandvars(r"%USERPROFILE%\OneDrive\Desktop")
if not os.path.exists(desk_dir):
    desk_dir = os.path.expandvars(r"%USERPROFILE%\Desktop")
down_dir = os.path.expandvars(r"%USERPROFILE%\Downloads")

# ==============================================================================
# 1. GENERATE DOCX LEAFLET
# ==============================================================================
doc = Document()

# Page setup: A4 Landscape or Portrait
for section in doc.sections:
    section.top_margin = Cm(1.5)
    section.bottom_margin = Cm(1.5)
    section.left_margin = Cm(1.8)
    section.right_margin = Cm(1.8)

# Styles & Fonts
normal_style = doc.styles['Normal']
normal_style.font.name = 'Microsoft JhengHei'
normal_style.font.size = Pt(11)
normal_style.font.color.rgb = RGBColor(0x26, 0x32, 0x38)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

# Header Title Block
p_top = doc.add_paragraph()
p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_hosp = p_top.add_run("國立成功大學醫學院附設醫院 護理部・血液透析室\n")
r_hosp.font.name = 'Microsoft JhengHei'
r_hosp.font.size = Pt(15)
r_hosp.font.bold = True
r_hosp.font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)

r_title = p_top.add_run("血液透析患者的高血壓預防與管理 護理指導單")
r_title.font.name = 'Microsoft JhengHei'
r_title.font.size = Pt(20)
r_title.font.bold = True
r_title.font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)

# Tagline Box
tbl_tag = doc.add_table(rows=1, cols=1)
tbl_tag.alignment = WD_TABLE_ALIGNMENT.CENTER
c_tag = tbl_tag.cell(0, 0)
set_cell_background(c_tag, "E3F2FD")
set_cell_margins(c_tag, top=120, bottom=120, left=200, right=200)
p_tag = c_tag.paragraphs[0]
p_tag.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_tag = p_tag.add_run("★ 核心口訣：居家量 722、體重增幅 < 5%、減鹽忌低鈉、服藥遵醫囑 ★")
r_tag.font.name = 'Microsoft JhengHei'
r_tag.font.size = Pt(12)
r_tag.font.bold = True
r_tag.font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)

doc.add_paragraph() # Spacer

# Section 1
def add_section_header(title):
    p = doc.add_paragraph()
    r = p.add_run(f"■ {title}")
    r.font.name = 'Microsoft JhengHei'
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x15, 0x65, 0xC0)
    return p

add_section_header("一、 為何血液透析病友需要特別注意血壓？")
p = doc.add_paragraph(
    "高血壓是透析病友最常見的併發症之一。透析病友因血管硬化及兩次洗腎間體液蓄積，血壓控制目標與一般人不同：\n"
    "• 一般成年人：建議控制在 ＜ 120 / 80 mmHg。\n"
    "• 血液透析病友（成大醫院與腎臟醫學會指引）：\n"
    "   1. 洗腎前診間血壓：＜ 140 / 90 mmHg\n"
    "   2. 透析間居家血壓：120～135 / 60～80 mmHg\n"
    "★ 重要觀念：洗腎病友血壓並非越低越好！收縮壓低於 120 mmHg 易引發心肌缺氧與透析中低血壓，維持平穩最適區間最安全。"
)

add_section_header("二、 為什麼「在家量」比在洗腎室更準確？")
p = doc.add_paragraph(
    "• 排除白袍效應：走進醫院或面對醫護容易緊張焦慮，使診間血壓假性飆高。\n"
    "• 反映真實負荷：洗腎前後體液快速變化，單次測量起伏劇烈；而在熟悉的家中放鬆測量，更能反映心臟真實負荷。\n"
    "• 國際指引共識：各國指引一致證實，居家血壓與左心室肥大及存活率關聯最高，是醫師調整降壓藥與乾體重的黃金依據。"
)

add_section_header("三、 居家血壓量測「7 2 2 原則」")
tbl_722 = doc.add_table(rows=4, cols=2)
tbl_722.alignment = WD_TABLE_ALIGNMENT.CENTER
headers = [("原則", "執行方式與說明")]
data_722 = [
    ("【 7 】 連續 7 天", "包含透析日與非透析日，完整記錄一週 7 天的血壓數值變化。"),
    ("【 2 】 每天 2 回", "早晚各量一回：\n• 早晨：起床排尿後（未吃早餐與降壓藥前）\n• 晚間：上床就寢前一小時內"),
    ("【 2 】 每回 2 遍", "每次測量間隔 1 分鐘，兩次數值填入記錄本並取平均值。")
]
for row_idx, (c1_txt, c2_txt) in enumerate(data_722, start=1):
    c1 = tbl_722.cell(row_idx, 0)
    c2 = tbl_722.cell(row_idx, 1)
    set_cell_margins(c1, 80, 80, 120, 120)
    set_cell_margins(c2, 80, 80, 120, 120)
    c1.paragraphs[0].add_run(c1_txt).font.bold = True
    c2.paragraphs[0].add_run(c2_txt)

# Header styling
c00 = tbl_722.cell(0, 0)
c01 = tbl_722.cell(0, 1)
set_cell_background(c00, "1565C0")
set_cell_background(c01, "1565C0")
set_cell_margins(c00, 100, 100, 120, 120)
set_cell_margins(c01, 100, 100, 120, 120)
r1 = c00.paragraphs[0].add_run("722 原則")
r1.font.bold = True
r1.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
r2 = c01.paragraphs[0].add_run("執行要領")
r2.font.bold = True
r2.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

doc.add_paragraph() # Spacer

add_section_header("四、 心臟像氣球：認識乾體重與水分控制（< 5% 原則）")
p = doc.add_paragraph(
    "1. 氣球比喻：心臟就像一顆氣球，兩次洗腎間喝太多水，氣球被反覆吹大，心臟彈性疲乏、血壓飆高；若洗腎脫水太快，氣球急速扁縮，易引發抽筋與心肌缺血。\n"
    "2. 什麼是乾體重（Dry Weight）？\n"
    "   透析後身上沒有多餘水腫、肺部無積水、血壓平穩時的最適體重。\n"
    "3. 黃金守則：兩次洗腎間體重增加 ＜ 乾體重的 5%！\n"
    "   【計算範例】：若乾體重為 60 公斤，60 × 5% = 3 公斤。\n"
    "   每次走進洗腎室前，體重增加絕不能超過 3 公斤（約 3 大瓶 1000cc 礦泉水）！\n"
    "4. 磅體重秘訣：每日固定早晨起床排尿後、使用同一台磅秤、穿著相似輕便衣服秤重。"
)

add_section_header("五、 控水先控鹽：嚴禁「低鈉鹽」致命陷阱！")
p = doc.add_paragraph(
    "• 控水先控鹽：吃太鹹會刺激大腦口渴中樞狂灌水。每日食鹽攝取量請控制在 5 公克（約 1 平匙）以內。\n"
    "• 避開高鈉食品：醃製食品（香腸、臘肉、肉鬆、醬菜）、泡麵、油麵、火鍋濃湯底、牛肉麵高湯、醬油膏。\n"
    "⚠️ 嚴正警告：洗腎病友絕對嚴禁食用市售「低鈉鹽」、「美味鹽」、「薄鹽醬油」！\n"
    "   原因：市售低鈉鹽是用「鉀」代替「鈉」！洗腎病友腎臟無排鉀能力，一旦食用，血鉀迅速飆高，會直接引發四肢無力、呼吸困難、惡性心律不整甚至心跳驟停猝死！請安心使用「普通精鹽」，但減量料理。"
)

add_section_header("六、 護理師推薦 4 大解渴妙招（口渴不灌水）")
p = doc.add_paragraph(
    "① 含新鮮薄檸檬片：果酸強烈刺激唾液腺分泌，迅速生津止渴。\n"
    "② 自製小冰塊口含：將開水製成彈珠大小小冰塊含在嘴裡慢慢融化，緩解喉嚨燥乾且水份極少。\n"
    "③ 嚼食無糖口香糖：嚼無糖口香糖或酸味薄荷糖，刺激唾液自然分泌，維持口腔濕潤。\n"
    "④ 冷開水漱口法：覺得口乾時用冷開水漱漱口後吐掉，或以棉棒沾水濕潤雙唇。"
)

add_section_header("七、 降壓藥物安全守則")
p = doc.add_paragraph(
    "① 按時規律服藥：降壓藥是保護心臟與大腦血管的盾牌，切勿因在家量血壓正常就自行停藥，以免引發反彈性高血壓引發中風。\n"
    "② 洗腎當日用藥遵醫囑：部分降壓藥在透析中會被清除，或易引起洗腎中低血壓。當天早晨服藥時間請務必遵從主治醫師個別指示。\n"
    "③ 感到頭暈先坐下：頭暈可能是血壓過高，也可能是脫水低血壓！請立即坐下或躺平並測量血壓，切勿在未量血壓前盲目服藥。"
)

# Footer info block
doc.add_paragraph()
tbl_foot = doc.add_table(rows=1, cols=1)
tbl_foot.alignment = WD_TABLE_ALIGNMENT.CENTER
c_foot = tbl_foot.cell(0, 0)
set_cell_background(c_foot, "F5F5F5")
set_cell_margins(c_foot, top=140, bottom=140, left=200, right=200)
p_foot = c_foot.paragraphs[0]
p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_f1 = p_foot.add_run("國立成功大學醫學院附設醫院 血液透析室 關心您\n")
r_f1.font.bold = True
r_f1.font.size = Pt(11)
r_f1.font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)
r_f2 = p_foot.add_run("諮詢專線：(06) 235-3535 分機 2591  |  製作日期：115 年 01 月  |  單張編號：HR_115-001")
r_f2.font.size = Pt(10)
r_f2.font.color.rgb = RGBColor(0x54, 0x6E, 0x7A)

docx_path = os.path.join(base_dir, "HR_115_血液透析患者高血壓預防與管理_成大衛教單張.docx")
doc.save(docx_path)
print(f"Saved DOCX: {docx_path}")

# ==============================================================================
# 2. GENERATE HIGH-RES PRINTABLE PDF & PREVIEW IMAGES (PIL / A4 300DPI)
# ==============================================================================
print("Generating Printable High-Res Leaflet Pages with PIL (A4 300DPI)...")

# A4 at 300 DPI: 2480 x 3508 pixels
PAGE_W, PAGE_H = 2480, 3508
font_bold = r"C:\Windows\Fonts\msjhbd.ttc"
font_regular = r"C:\Windows\Fonts\msjh.ttc"

def create_leaflet_canvas():
    im = Image.new("RGB", (PAGE_W, PAGE_H), "#FFFFFF")
    draw = ImageDraw.Draw(im)
    
    # Top banner bar
    draw.rectangle([(0, 0), (PAGE_W, 220)], fill="#0D47A1")
    f_h = ImageFont.truetype(font_bold, 54)
    draw.text((120, 55), "國立成功大學醫學院附設醫院 血液透析室", font=f_h, fill="#FFFFFF")
    f_sub_h = ImageFont.truetype(font_bold, 38)
    draw.text((120, 135), "護理部健康識能護理指導單", font=f_sub_h, fill="#BBDEFB")
    
    # Title Ribbon
    draw.rounded_rectangle([(100, 260), (PAGE_W - 100, 410)], radius=30, fill="#E3F2FD", outline="#1976D2", width=4)
    f_title = ImageFont.truetype(font_bold, 64)
    draw.text((160, 295), "血液透析患者的高血壓預防與管理", font=f_title, fill="#0D47A1")
    
    # Tag right
    f_num = ImageFont.truetype(font_bold, 36)
    draw.rounded_rectangle([(PAGE_W - 520, 305), (PAGE_W - 140, 375)], radius=20, fill="#1976D2")
    draw.text((PAGE_W - 490, 322), "編號：HR_115", font=f_num, fill="#FFFFFF")
    
    # Bottom footer
    draw.rectangle([(0, PAGE_H - 180), (PAGE_W, PAGE_H)], fill="#0A387E")
    f_foot = ImageFont.truetype(font_bold, 38)
    draw.text((120, PAGE_H - 120), "成大醫院血液透析室 關心您 | 諮詢專線：(06) 235-3535 分機 2591", font=f_foot, fill="#E3F2FD")
    
    return im, draw

def draw_card(draw, x1, y1, x2, y2, title, col="#1565C0"):
    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=25, fill="#FFFFFF", outline=col, width=4)
    draw.rounded_rectangle([(x1, y1), (x2, y1 + 90)], radius=25, fill=col)
    f_ct = ImageFont.truetype(font_bold, 42)
    draw.text((x1 + 40, y1 + 22), title, font=f_ct, fill="#FFFFFF")

# ----------------- PAGE 1 -----------------
im1, d1 = create_leaflet_canvas()

# Card 1: Target Blood Pressure
draw_card(d1, 100, 450, PAGE_W - 100, 1150, "■ 一、 一般人 vs 洗腎病友的血壓標準大不同", col="#0D47A1")
f_body = ImageFont.truetype(font_bold, 36)
f_regular_txt = ImageFont.truetype(font_regular, 34)

# Sub boxes inside Card 1
# Box General
d1.rounded_rectangle([(150, 580), (1180, 850)], radius=20, fill="#E3F2FD", outline="#1976D2", width=3)
d1.text((190, 610), "一般成年人 (國健署標準)", font=ImageFont.truetype(font_bold, 40), fill="#0D47A1")
d1.text((190, 680), "＜ 120 / 80 mmHg", font=ImageFont.truetype(font_bold, 54), fill="#1565C0")
d1.text((190, 760), "追求平穩血壓，預防動脈硬化與中風。", font=f_regular_txt, fill="#37474F")

# Box Dialysis
d1.rounded_rectangle([(1250, 580), (PAGE_W - 150, 850)], radius=20, fill="#E8F5E9", outline="#2E7D32", width=3)
d1.text((1290, 610), "血液透析病友 (成大/腎醫會標準)", font=ImageFont.truetype(font_bold, 40), fill="#2E7D32")
d1.text((1290, 670), "• 洗腎前診間：＜ 140 / 90 mmHg", font=ImageFont.truetype(font_bold, 42), fill="#1B5E20")
d1.text((1290, 735), "• 透析間居家：120～135 / 60～80 mmHg", font=ImageFont.truetype(font_bold, 42), fill="#2E7D32")

# Medical Alert Box inside Card 1
d1.rounded_rectangle([(150, 890), (PAGE_W - 150, 1100)], radius=20, fill="#FFF8E1", outline="#FFA000", width=3)
f_alert = ImageFont.truetype(font_bold, 36)
alert_msg = (
    "★ 醫學叮嚀：洗腎病友血壓「不是越低越好」！\n"
    "透析病友血管多已有硬化，體液波動大，收縮壓若低於 120 mmHg 反而容易引發心肌缺氧與透析低血壓！\n"
    "維持平穩最適區間，才能保護心血管與重要器官！"
)
y_cur = 920
for line in alert_msg.split("\n"):
    d1.text((200, y_cur), line, font=f_alert, fill="#B76E00")
    y_cur += 52

# Card 2: 722 Protocol
draw_card(d1, 100, 1200, PAGE_W - 100, 2200, "■ 二、 居家血壓量測黃金口訣：「7 2 2 原則」", col="#1565C0")

p1_desc = (
    "為什麼在家量比洗腎室更準？\n"
    "走進洗腎室容易有「白袍效應」緊張飆高，且透析前後體液劇變。實證醫學證實：居家血壓數值最真實，\n"
    "與左心室肥大及存活率關聯最高！請大家牢記『722 原則』："
)
y_cur = 1320
for line in p1_desc.split("\n"):
    d1.text((150, y_cur), line, font=f_body, fill="#263238")
    y_cur += 48

# 3 columns for 7, 2, 2
c_w = 700
c_gap = 50
c_y = 1500
c_h = 480
cards_722 = [
    ("7", "連續 7 天", "包含透析日與非透析日\n完整記錄一整週血壓趨勢\n掌握每週波動規律", "#1565C0", "#E3F2FD"),
    ("2", "每天 2 回", "早晚各量一回：\n• 晨起排尿後 (未進食/未服藥)\n• 睡前一小時內", "#2E7D32", "#E8F5E9"),
    ("2", "每回 2 遍", "每次測量間隔 1 分鐘\n兩次數值記錄於本子\n計算平均值作為依據", "#6A1B9A", "#F3E5F5")
]
for ci, (c_num, c_tit, c_det, c_col, c_bg) in enumerate(cards_722):
    cx1 = 150 + ci * (c_w + c_gap)
    cx2 = cx1 + c_w
    d1.rounded_rectangle([(cx1, c_y), (cx2, c_y + c_h)], radius=20, fill="#FFFFFF", outline=c_col, width=3)
    d1.rounded_rectangle([(cx1, c_y), (cx2, c_y + 110)], radius=20, fill=c_col)
    
    # Big Number circle
    d1.ellipse([(cx1 + 30, c_y + 15), (cx1 + 110, c_y + 95)], fill="#FFFFFF")
    d1.text((cx1 + 52, c_y + 20), c_num, font=ImageFont.truetype(font_bold, 54), fill=c_col)
    d1.text((cx1 + 135, c_y + 30), c_tit, font=ImageFont.truetype(font_bold, 44), fill="#FFFFFF")
    
    # Detail
    d1.rounded_rectangle([(cx1 + 20, c_y + 130), (cx2 - 20, c_y + c_h - 20)], radius=15, fill=c_bg)
    y_dt = c_y + 160
    for dt_line in c_det.split("\n"):
        d1.text((cx1 + 45, y_dt), dt_line, font=ImageFont.truetype(font_bold, 32), fill="#263238")
        y_dt += 50

# Target Box inside Card 2
d1.rounded_rectangle([(150, 2020), (PAGE_W - 150, 2150)], radius=18, fill="#FCE4EC", outline="#C2185B", width=2)
d1.text((190, 2045), "★ 成大透析室居家控制目標：收縮壓 120～135 mmHg / 舒張壓 60～80 mmHg", font=ImageFont.truetype(font_bold, 38), fill="#C2185B")
d1.text((190, 2095), "※ 回診叮嚀：每次回診務必攜帶『血壓紀錄本』，供醫師精準調整降壓藥物與乾體重！", font=ImageFont.truetype(font_bold, 30), fill="#880E4F")

# Card 3: Balloon & Dry Weight (< 5%)
draw_card(d1, 100, 2250, PAGE_W - 100, 3250, "■ 三、 心臟像氣球：乾體重與透析間體重增加「< 5% 守則」", col="#2E7D32")

balloon_intro = (
    "心臟就像一顆氣球：喝水太多，氣球過度吹大，心臟彈性疲乏、血壓飆高；洗腎脫水太快，氣球快速扁縮，\n"
    "容易抽筋與低血壓。因此維持最適「乾體重」是保護心血管的關鍵！"
)
y_cur = 2370
for line in balloon_intro.split("\n"):
    d1.text((150, y_cur), line, font=f_body, fill="#263238")
    y_cur += 48

# Golden Formula Box
d1.rounded_rectangle([(150, 2490), (PAGE_W - 150, 2680)], radius=25, fill="#1976D2")
d1.text((200, 2520), "黃金計算公式：兩次洗腎間體重增加 ＜ 乾體重的 5%", font=ImageFont.truetype(font_bold, 50), fill="#FFFFFF")
d1.text((200, 2600), "【實例】：乾體重 60 公斤 × 5% = 最多增加 3 公斤 (約 3 大瓶 1000cc 礦泉水)！", font=ImageFont.truetype(font_bold, 42), fill="#FFF176")

# Dry weight & Weighing Tips
d1.rounded_rectangle([(150, 2720), (1180, 3180)], radius=20, fill="#F1F8E9", outline="#A5D6A7", width=3)
d1.text((190, 2750), "【什麼是乾體重 (Dry Weight)？】", font=ImageFont.truetype(font_bold, 40), fill="#1B5E20")
dw_details = (
    "• 透析後身體沒有多餘水腫、肺部無積水。\n"
    "• 血壓平穩、呼吸順暢時的最適理想體重。\n"
    "• 每次洗腎走進洗腎室前，體重絕不能超過乾體重+5%！\n"
    "• 即使隔兩天的週末長間隔，增加量依然要嚴格守住 5%！"
)
y_dw = 2820
for line in dw_details.split("\n"):
    d1.text((190, y_dw), line, font=ImageFont.truetype(font_bold, 34), fill="#2E7D32")
    y_dw += 52

d1.rounded_rectangle([(1250, 2720), (PAGE_W - 150, 3180)], radius=20, fill="#E8F5E9", outline="#81C784", width=3)
d1.text((1290, 2750), "【正確秤體重的三大原則】", font=ImageFont.truetype(font_bold, 40), fill="#2E7D32")
wt_details = (
    "① 每日固定時間：早晨起床上完洗手間後立刻秤量。\n"
    "② 固定同一台磅秤：避免不同機器產生測量誤差。\n"
    "③ 穿著相似輕便衣服：去除厚重外套、皮帶與鞋子。\n"
    "★ 每日體重增加建議不超過 1 公斤 (約 1000cc 水分)！"
)
y_wt = 2820
for line in wt_details.split("\n"):
    d1.text((1290, y_wt), line, font=ImageFont.truetype(font_bold, 34), fill="#37474F")
    y_wt += 52

page1_path = os.path.join(base_dir, "衛教單張_第1頁.png")
im1.save(page1_path)
print(f"Saved Leaflet Page 1: {page1_path}")

# ----------------- PAGE 2 -----------------
im2, d2 = create_leaflet_canvas()

# Card 4: Salt & Low Sodium Salt Warning
draw_card(d2, 100, 450, PAGE_W - 100, 1380, "■ 四、 控水先控鹽：嚴禁「低鈉鹽」致命陷阱！", col="#D32F2F")

# Left: Salt control
d2.rounded_rectangle([(150, 570), (1180, 1320)], radius=20, fill="#FFFFFF", outline="#90CAF9", width=3)
d2.rounded_rectangle([(150, 570), (1180, 660)], radius=20, fill="#1565C0")
d2.text((190, 590), "【為什麼要嚴格限制鹽分？】", font=ImageFont.truetype(font_bold, 40), fill="#FFFFFF")

salt_txt = (
    "• 「吃太鹹」會強烈刺激大腦口渴中樞狂灌水！\n"
    "• 想成功控水，關鍵第一步就是『嚴格控鹽』。\n"
    "• 每日食鹽攝取量應控制在 5 公克 (約 1 平匙) 以內。\n\n"
    "★ 必須避開的高鈉隱形地雷食品：\n"
    "   • 香腸、臘肉、肉鬆、火腿、貢丸等加工品\n"
    "   • 醃製醬菜、泡菜、豆腐乳、蜜餞\n"
    "   • 泡麵、油麵、麵線、滷味\n"
    "   • 濃郁火鍋高湯、牛肉麵湯、沾醬醬油膏"
)
y_st = 690
for line in salt_txt.split("\n"):
    d2.text((190, y_st), line, font=ImageFont.truetype(font_bold, 34), fill="#263238")
    y_st += 48

# Right: Danger Low Sodium Salt
d2.rounded_rectangle([(1250, 570), (PAGE_W - 150, 1320)], radius=20, fill="#FFF5F5", outline="#D32F2F", width=4)
d2.rounded_rectangle([(1250, 570), (PAGE_W - 150, 660)], radius=20, fill="#D32F2F")
d2.text((1290, 590), "【絕對禁忌】嚴禁食用「低鈉鹽」！", font=ImageFont.truetype(font_bold, 40), fill="#FFFFFF")

danger_txt = (
    "【市售低鈉鹽、美味鹽、薄鹽醬油是大地雷！】\n\n"
    "• 致命原因：低鈉鹽是用『鉀』取代鈉！\n"
    "• 洗腎病友腎臟無排鉀功能，鉀離子迅速在體內累積！\n"
    "• 一旦引發高血鉀症，將直接導致：\n"
    "   • 四肢無力、嘴麻、呼吸困難\n"
    "   • 致死性惡性心律不整\n"
    "   • 心跳驟停與猝死！\n\n"
    "★ 護理師提醒：料理請安心使用「普通精鹽」，\n"
    "  但要減量清淡烹調，千萬別買低鈉鹽！"
)
y_dg = 690
for line in danger_txt.split("\n"):
    d2.text((1290, y_dg), line, font=ImageFont.truetype(font_bold, 34), fill="#B71C1C")
    y_dg += 48

# Card 5: 4 Thirst Management Tips
draw_card(d2, 100, 1430, PAGE_W - 100, 2200, "■ 五、 口渴不灌水：護理師推薦 4 大解渴妙招", col="#F57F17")

t_cards = [
    ("【妙招 1】含新鮮薄檸檬片", "切一小片新鮮薄檸檬含在口中，\n果酸強烈刺激唾液分泌，生津止渴又不需要吞水！", "#F57F17", "#FFFDE7"),
    ("【妙招 2】自製小冰塊口含", "將開水製成彈珠大小小冰塊含在嘴裡，\n慢慢融化緩解喉嚨乾燥，水分攝取極低！", "#0288D1", "#E1F5FE"),
    ("【妙招 3】嚼食無糖口香糖", "嚼無糖口香糖或酸味薄荷糖，\n促進唾液自然分泌，維持口腔濕潤轉移喝水慾！", "#2E7D32", "#E8F5E9"),
    ("【妙招 4】冷開水漱口法", "覺得口乾時用冷開水漱漱口後吐掉，\n或用棉花棒沾水濕潤雙唇，有效消除乾燥感！", "#7B1FA2", "#F3E5F5")
]

for ti, (ttit, tdesc, tcol, tbg) in enumerate(t_cards):
    t_col_idx = ti % 2
    t_row_idx = ti // 2
    tx1 = 150 + t_col_idx * 1100
    tx2 = tx1 + 1040
    ty1 = 1550 + t_row_idx * 300
    ty2 = ty1 + 270
    
    d2.rounded_rectangle([(tx1, ty1), (tx2, ty2)], radius=20, fill="#FFFFFF", outline=tcol, width=3)
    d2.rounded_rectangle([(tx1, ty1), (tx2, ty1 + 80)], radius=20, fill=tcol)
    d2.text((tx1 + 30, ty1 + 18), ttit, font=ImageFont.truetype(font_bold, 38), fill="#FFFFFF")
    
    d2.rounded_rectangle([(tx1 + 15, ty1 + 95), (tx2 - 15, ty2 - 15)], radius=15, fill=tbg)
    y_td = ty1 + 115
    for td_line in tdesc.split("\n"):
        d2.text((tx1 + 35, y_td), td_line, font=ImageFont.truetype(font_bold, 32), fill="#263238")
        y_td += 48

# Card 6: Medication Safety & 4 Formulas
draw_card(d2, 100, 2250, PAGE_W - 100, 3250, "■ 六、 降壓藥物安全守則 ＆ 控壓四字訣總結", col="#6A1B9A")

med_pts = [
    ("【守則一】按時規律服藥", "降壓藥是保護心血管的防護盾！切勿因在家量血壓正常就自行停藥或減藥，以免反彈性高血壓引發中風！", "#1565C0"),
    ("【守則二】洗腎日遵照醫囑", "部分降壓藥在透析中會被清除，或易引起透析低血壓。當天早晨服藥時間，請務必遵從主治醫師個別指示！", "#D32F2F"),
    ("【守則三】頭暈先坐下測量", "頭暈可能是血壓過高，也可能是脫水太快導致的低血壓！請立即坐下或躺平並測量血壓，切勿盲目吞藥！", "#F57C00")
]

for mi, (mtit, mdesc, mcol) in enumerate(med_pts):
    my = 2370 + mi * 170
    d2.rounded_rectangle([(150, my), (PAGE_W - 150, my + 145)], radius=18, fill="#FFFFFF", outline=mcol, width=3)
    d2.rounded_rectangle([(170, my + 15), (600, my + 75)], radius=12, fill=mcol)
    d2.text((190, my + 22), mtit, font=ImageFont.truetype(font_bold, 34), fill="#FFFFFF")
    d2.text((170, my + 88), mdesc, font=ImageFont.truetype(font_bold, 30), fill="#263238")

# 4 Formula Emblem Summary Box
d2.rounded_rectangle([(150, 2900), (PAGE_W - 150, 3180)], radius=20, fill="#E3F2FD", outline="#1976D2", width=3)
d2.text((200, 2920), "★ 血液透析控壓四字訣總結（牢記健康口訣）：", font=ImageFont.truetype(font_bold, 38), fill="#0D47A1")

four_summary = [
    ("7 2 2", "居家量 722", "早晚量血壓記錄", "#1565C0"),
    ("< 5%", "體重不超五", "體重增幅 < 5%", "#2E7D32"),
    ("忌低鈉", "減鹽忌低鈉", "每天鹽<5g禁低鈉", "#C62828"),
    ("遵醫囑", "服藥遵醫囑", "安心透析護心腎", "#6A1B9A")
]
for fi, (fem, ftit, fsub, fcol) in enumerate(four_summary):
    fx = 200 + fi * 530
    fy = 2990
    d2.ellipse([(fx, fy), (fx + 100, fy + 100)], fill=fcol)
    d2.text((fx + 15, fy + 30), fem, font=ImageFont.truetype(font_bold, 28), fill="#FFFFFF")
    d2.text((fx + 120, fy + 15), ftit, font=ImageFont.truetype(font_bold, 34), fill=fcol)
    d2.text((fx + 120, fy + 60), fsub, font=ImageFont.truetype(font_bold, 28), fill="#37474F")

page2_path = os.path.join(base_dir, "衛教單張_第2頁.png")
im2.save(page2_path)
print(f"Saved Leaflet Page 2: {page2_path}")

# ==============================================================================
# 3. CONVERT HIGH-RES LEAFLET PAGES TO PRINTABLE PDF
# ==============================================================================
pdf_path = os.path.join(base_dir, "HR_115_血液透析患者高血壓預防與管理_成大衛教單張.pdf")
im1_rgb = im1.convert('RGB')
im2_rgb = im2.convert('RGB')
im1_rgb.save(pdf_path, "PDF", resolution=300.0, save_all=True, append_images=[im2_rgb])
print(f"Saved Leaflet Printable PDF: {pdf_path}")

# Copy DOCX, PDF, and PNGs to Desktop and Downloads
for p in [docx_path, pdf_path, page1_path, page2_path]:
    shutil.copy2(p, os.path.join(desk_dir, os.path.basename(p)))
    shutil.copy2(p, os.path.join(down_dir, os.path.basename(p)))

print("\n=== All Education Leaflets Generated & Copied to Desktop/Downloads! ===")
