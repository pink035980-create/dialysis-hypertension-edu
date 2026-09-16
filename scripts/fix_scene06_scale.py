import os
from PIL import Image, ImageDraw, ImageFont

brain_dir = r'C:\Users\pink0\.gemini\antigravity\brain\a835a13b-300f-4228-9146-ed73f327da63'
font_path = r'C:\Windows\Fonts\msjhbd.ttc'

path = os.path.join(brain_dir, 'scale_water_bottles_zh.png')
im = Image.open(path).convert('RGB')
d = ImageDraw.Draw(im)

# 1. Clean the warning badge area completely with pure white
d.rectangle([(760, 360), (1024, 530)], fill=(255, 255, 255))

# 2. Draw warning badge with generous width (230px) aligned to bottle center (cx=890)
cx = 890
bw, bh = 230, 145
bx1 = cx - bw // 2   # 775
bx2 = cx + bw // 2   # 1005
by1 = 370
by2 = by1 + bh       # 515

d.rounded_rectangle([(bx1, by1), (bx2, by2)], radius=14, fill=(255, 245, 245), outline=(195, 35, 25), width=3)

# Fonts
f_t1 = ImageFont.truetype(font_path, 17)
f_t2 = ImageFont.truetype(font_path, 16)
f_t3 = ImageFont.truetype(font_path, 15)

t1 = "【嚴格警戒・嚴禁超標】"
t2 = "不可超過上限 3.0 kg"
t3 = "超量恐致呼吸喘・肺積水"

tw1 = d.textlength(t1, font=f_t1)
tw2 = d.textlength(t2, font=f_t2)
tw3 = d.textlength(t3, font=f_t3)

d.text((cx - tw1 / 2, by1 + 16), t1, font=f_t1, fill=(195, 35, 25))
d.text((cx - tw2 / 2, by1 + 54), t2, font=f_t2, fill=(40, 50, 60))
d.text((cx - tw3 / 2, by1 + 92), t3, font=f_t3, fill=(195, 35, 25))

im.save(path)
print("Updated scale_water_bottles_zh.png successfully!")
