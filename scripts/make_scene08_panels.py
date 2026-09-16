import os, math
from PIL import Image, ImageDraw, ImageFont

brain_dir = r'C:\Users\pink0\.gemini\antigravity\brain\a835a13b-300f-4228-9146-ed73f327da63'
font_bold = r"C:\Windows\Fonts\msjhbd.ttc"
f_badge = ImageFont.truetype(font_bold, 28)
f_sub = ImageFont.truetype(font_bold, 24)

# 1. Panel 1: Lemon Slice
im1 = Image.new('RGB', (405, 405), (255, 252, 235))
d1 = ImageDraw.Draw(im1)
# Lemon slice centered
cx, cy, r = 202, 202, 130
d1.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill="#FFA000", outline="#E65100", width=6)
d1.ellipse([(cx - r + 10, cy - r + 10), (cx + r - 10, cy + r - 10)], fill="#FFFFFF")
d1.ellipse([(cx - r + 18, cy - r + 18), (cx + r - 18, cy + r - 18)], fill="#FFEE58")
for i in range(8):
    ang = math.radians(i * 45)
    x2 = cx + int((r - 20) * math.cos(ang))
    y2 = cy + int((r - 20) * math.sin(ang))
    d1.line([(cx, cy), (x2, y2)], fill="#FFFFFF", width=5)
d1.ellipse([(cx - 10, cy - 10), (cx + 10, cy + 10)], fill="#FFFFFF")
# Juice drops
d1.polygon([(cx + 120, cy - 80), (cx + 140, cy - 50), (cx + 100, cy - 50)], fill="#FFD54F")
d1.ellipse([(cx + 100, cy - 60), (cx + 140, cy - 35)], fill="#FFD54F")
# Text banner inside
d1.rounded_rectangle([(30, 330), (375, 385)], radius=12, fill=(245, 124, 0))
d1.text((70, 340), '★ 含薄檸檬片・生津解渴', font=f_sub, fill=(255, 255, 255))
im1.save(os.path.join(brain_dir, 's8_p1_lemon.png'))

# 2. Panel 2: Ice Cube
im2 = Image.new('RGB', (405, 405), (235, 248, 255))
d2 = ImageDraw.Draw(im2)
# Ice cubes
cx, cy, sz = 202, 195, 160
# 3D isometric ice cube
pts_top = [(cx, cy - sz//2), (cx + sz//2, cy - sz//4), (cx, cy), (cx - sz//2, cy - sz//4)]
d2.polygon(pts_top, fill="#E1F5FE", outline="#0288D1", width=3)
pts_left = [(cx - sz//2, cy - sz//4), (cx, cy), (cx, cy + sz//2), (cx - sz//2, cy + sz//4)]
d2.polygon(pts_left, fill="#B3E5FC", outline="#0288D1", width=3)
pts_right = [(cx, cy), (cx + sz//2, cy - sz//4), (cx + sz//2, cy + sz//4), (cx, cy + sz//2)]
d2.polygon(pts_right, fill="#81D4FA", outline="#0288D1", width=3)
# Shimmer stars
for sx, sy in [(cx - 70, cy - 90), (cx + 90, cy - 70), (cx + 100, cy + 50)]:
    d2.line([(sx - 15, sy), (sx + 15, sy)], fill="#FFFFFF", width=4)
    d2.line([(sx, sy - 15), (sx, sy + 15)], fill="#FFFFFF", width=4)
d2.rounded_rectangle([(30, 330), (375, 385)], radius=12, fill=(2, 136, 209))
d2.text((70, 340), '★ 口含小冰塊・清涼解燥', font=f_sub, fill=(255, 255, 255))
im2.save(os.path.join(brain_dir, 's8_p2_ice.png'))

# 3. Panel 3: Mint Gum
im3 = Image.new('RGB', (405, 405), (240, 255, 244))
d3 = ImageDraw.Draw(im3)
# Mint leaves & gum blister
cx, cy = 202, 185
# Two mint leaves
d3.polygon([(cx - 90, cy + 20), (cx - 40, cy - 50), (cx + 20, cy), (cx - 30, cy + 40)], fill="#66BB6A", outline="#2E7D32", width=3)
d3.line([(cx - 90, cy + 20), (cx + 20, cy)], fill="#2E7D32", width=3)
d3.polygon([(cx, cy), (cx + 70, cy - 60), (cx + 100, cy + 10), (cx + 30, cy + 30)], fill="#81C784", outline="#2E7D32", width=3)
d3.line([(cx, cy), (cx + 100, cy + 10)], fill="#2E7D32", width=3)
# Chewing gum stick - perfectly centered box and text
box_w, box_h = 190, 58
bx1, by1 = cx - box_w // 2, cy + 28
bx2, by2 = cx + box_w // 2, by1 + box_h
d3.rounded_rectangle([(bx1, by1), (bx2, by2)], radius=12, fill="#FFFFFF", outline="#388E3C", width=3)
f_gum = ImageFont.truetype(font_bold, 24)
tw3 = d3.textlength('無糖口香糖', font=f_gum)
d3.text((cx - tw3 / 2, by1 + 13), '無糖口香糖', font=f_gum, fill="#2E7D32")
d3.rounded_rectangle([(30, 330), (375, 385)], radius=12, fill=(46, 125, 50))
tw_bot3 = d3.textlength('★ 嚼無糖口香糖・生津轉移', font=f_sub)
d3.text((202 - tw_bot3 / 2, 342), '★ 嚼無糖口香糖・生津轉移', font=f_sub, fill=(255, 255, 255))
im3.save(os.path.join(brain_dir, 's8_p3_mint.png'))

# 4. Panel 4: Water Rinse
im4 = Image.new('RGB', (405, 405), (248, 240, 255))
d4 = ImageDraw.Draw(im4)
cx, cy = 202, 180
# Cup & water splash
d4.polygon([(cx - 70, cy - 60), (cx + 70, cy - 60), (cx + 50, cy + 80), (cx - 50, cy + 80)], fill="#E1F5FE", outline="#0288D1", width=4)
d4.polygon([(cx - 65, cy - 10), (cx + 65, cy - 10), (cx + 47, cy + 76), (cx - 47, cy + 76)], fill="#29B6F6")
# Rinse reminder badge - ample width and centered text
f_rinse = ImageFont.truetype(font_bold, 21)
rinse_text = '【漱完務必吐掉】'
tw4 = d4.textlength(rinse_text, font=f_rinse)
badge_w = int(tw4 + 44)
badge_h = 50
d4.rounded_rectangle([(cx - badge_w // 2, cy - 110), (cx + badge_w // 2, cy - 110 + badge_h)], radius=12, fill="#D32F2F", outline="#FFFFFF", width=2)
d4.text((cx - tw4 / 2, cy - 110 + 11), rinse_text, font=f_rinse, fill=(255, 255, 255))
d4.rounded_rectangle([(30, 330), (375, 385)], radius=12, fill=(106, 27, 154))
tw_bot4 = d4.textlength('★ 清水漱口法・潤唇不喝水', font=f_sub)
d4.text((202 - tw_bot4 / 2, 342), '★ 清水漱口法・潤唇不喝水', font=f_sub, fill=(255, 255, 255))
im4.save(os.path.join(brain_dir, 's8_p4_rinse.png'))

print('Scene 8 4-panel artworks created successfully!')
