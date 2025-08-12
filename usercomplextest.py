# usertest_model_complex.py
# 复杂模型示例：多类曲线/孔/复杂轮廓零件在 2440x1220 板上排版
import math
import packaide

def circle_subpath(cx, cy, r):
    # 闭合圆：两段大弧
    return f"M {cx+r},{cy} A {r},{r} 0 1 0 {cx-r},{cy} A {r},{r} 0 1 0 {cx+r},{cy} Z"

def rect_subpath(x, y, w, h):
    return f"M {x},{y} L {x+w},{y} L {x+w},{y+h} L {x},{y+h} Z"

def ring_path(cx, cy, r_out, r_in):
    outer = circle_subpath(cx, cy, r_out)
    inner = circle_subpath(cx, cy, r_in)
    return outer + " " + inner

def triangle_with_holes_path(x, y, w, h, holes):
    # 等腰三角外轮廓 + 圆孔子路径
    x0, y0 = x, y + h
    x1, y1 = x + w, y + h
    x2, y2 = x + w/2, y
    d = f"M {x0},{y0} L {x1},{y1} L {x2},{y2} Z"
    for (cx, cy, r) in holes:
        d += " " + circle_subpath(cx, cy, r)
    return d

def star_path(cx, cy, R, r, n=10, hole_radius=None):
    pts = []
    for i in range(2*n):
        ang = math.pi * i / n
        rad = R if i % 2 == 0 else r
        px = cx + rad * math.cos(ang)
        py = cy + rad * math.sin(ang)
        pts.append((px, py))
    d = f"M {pts[0][0]},{pts[0][1]} " + " ".join(f"L {x},{y}" for x, y in pts[1:]) + " Z"
    if hole_radius and hole_radius > 0:
        d += " " + circle_subpath(cx, cy, hole_radius)
    return d

def window_panel_path(x, y, w, h, windows):
    # 外轮廓矩形 + 多个内窗洞矩形（同一 path 的多个子路径）
    d = rect_subpath(x, y, w, h)
    for (wx, wy, ww, wh) in windows:
        d += " " + rect_subpath(x + wx, y + wy, ww, wh)
    return d

def l_bracket_path(x, y, outer_w, outer_h, thickness):
    # L 形支架（凹多边形，无孔）
    x0, y0 = x, y
    ow, oh, t = outer_w, outer_h, thickness
    # 轮廓顺时针
    pts = [
        (x0, y0),
        (x0 + ow, y0),
        (x0 + ow, y0 + t),
        (x0 + t, y0 + t),
        (x0 + t, y0 + oh),
        (x0, y0 + oh),
    ]
    d = f"M {pts[0][0]},{pts[0][1]} " + " ".join(f"L {px},{py}" for px, py in pts[1:]) + " Z"
    return d

# 目标板（海洋板）2440x1220（单位 mm）
sheets = [packaide.blank_sheet(2440, 1220)]

# 生成复杂零件集合（使用同一 SVG 文档，必须提供 viewBox）
parts = []

# 1) 大桌面（圆角）
parts.append('<rect width="1600" height="900" rx="80" ry="80" />')

# 2) 长/短边桌围（圆角）
parts += [
    '<rect width="1600" height="80" rx="20" ry="20" />',
    '<rect width="1600" height="80" rx="20" ry="20" />',
    '<rect width="700" height="80" rx="20" ry="20" />',
    '<rect width="700" height="80" rx="20" ry="20" />',
]

# 3) 桌腿（圆角矩形）
for _ in range(6):
    parts.append('<rect width="80" height="730" rx="15" ry="15" />')

# 4) 圆环（带孔的圆形零件）
parts.append(f'<path d="{ring_path(0,0,220,120)}" />')
parts.append(f'<path d="{ring_path(0,0,180,90)}" />')

# 5) 三角加强板（3 孔）
tri_d = triangle_with_holes_path(
    x=0, y=0, w=520, h=430,
    holes=[(200, 240, 25), (320, 240, 25), (260, 150, 25)]
)
parts += [f'<path d="{tri_d}" />', f'<path d="{tri_d}" />']

# 6) 带窗洞的面板（外 800x500，4 个窗洞）
panel_d = window_panel_path(
    x=0, y=0, w=800, h=500,
    windows=[(60,60,220,120), (520,60,220,120), (60,320,220,120), (520,320,220,120)]
)
parts.append(f'<path d="{panel_d}" />')

# 7) 星形齿板（中心孔）
parts.append(f'<path d="{star_path(0,0, R=180, r=75, n=12, hole_radius=40)}" />')
parts.append(f'<path d="{star_path(0,0, R=150, r=65, n=10, hole_radius=35)}" />')

# 8) 胶囊形（圆角大矩形）
for _ in range(3):
    parts.append('<rect width="300" height="120" rx="60" ry="60" />')

# 9) 圆盘与椭圆
for _ in range(4):
    parts.append('<circle r="100" />')
parts += ['<ellipse rx="150" ry="100" />', '<ellipse rx="120" ry="90" />']

# 10) L 型支架（凹多边形）
parts += [
    f'<path d="{l_bracket_path(0,0, outer_w=300, outer_h=300, thickness=80)}" />',
    f'<path d="{l_bracket_path(0,0, outer_w=260, outer_h=260, thickness=70)}" />',
]

# 11) 带孔的“环形五边形”（外五边星近似 + 中孔）
pentastar = star_path(0,0, R=200, r=120, n=5, hole_radius=60)
parts.append(f'<path d="{pentastar}" />')

# 汇总到 SVG 文档（注意 viewBox，给足范围即可）
shapes_svg = f'''
<svg viewBox="0 0 5000 3000" xmlns="http://www.w3.org/2000/svg">
  {"".join(parts)}
</svg>
'''

# 执行排版
result, placed, fails = packaide.pack(
    sheet_svgs=sheets,
    shapes=shapes_svg,
    tolerance=1.5,        # 曲线离散精度
    offset=3,             # 零件间/边界安全距离
    partial_solution=True,# 若过多放不下，仍返回可行子集
    rotations=12,         # 多方向尝试提升紧凑度
    persist=True
)

print(f"已放置 {placed} 个零件，未放置 {fails} 个。")

for i, out in result:
    with open(f"result_complex_sheet_{i}.svg", "w") as f_out:
        f_out.write(out)

print("输出 result_complex_sheet_*.svg，可用浏览器或矢量软件查看。")