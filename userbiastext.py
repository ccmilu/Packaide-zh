import os
import math
import random
import time
import packaide


def make_unique_path(base_path: str) -> str:
    name, ext = os.path.splitext(base_path)
    if not os.path.exists(base_path):
        return base_path
    i = 1
    while True:
        candidate = f"{name}_{i}{ext}"
        if not os.path.exists(candidate):
            return candidate
        i += 1


def circle_path(cx: float, cy: float, r: float) -> str:
    return f"M {cx+r},{cy} A {r},{r} 0 1 0 {cx-r},{cy} A {r},{r} 0 1 0 {cx+r},{cy} Z"


def ring_path(cx: float, cy: float, r_out: float, r_in: float) -> str:
    return circle_path(cx, cy, r_out) + " " + circle_path(cx, cy, r_in)


def rect_path(x: float, y: float, w: float, h: float) -> str:
    return f"M {x},{y} L {x+w},{y} L {x+w},{y+h} L {x},{y+h} Z"


def triangle_path(x: float, y: float, w: float, h: float) -> str:
    x0, y0 = x, y + h
    x1, y1 = x + w, y + h
    x2, y2 = x + w/2.0, y
    return f"M {x0},{y0} L {x1},{y1} L {x2},{y2} Z"


def triangle_with_circular_holes_path(x: float, y: float, w: float, h: float, holes):
    d = triangle_path(x, y, w, h)
    for (cx, cy, r) in holes:
        d += " " + circle_path(cx, cy, r)
    return d


def l_bracket_path(x: float, y: float, outer_w: float, outer_h: float, thickness: float) -> str:
    pts = [
        (x, y),
        (x + outer_w, y),
        (x + outer_w, y + thickness),
        (x + thickness, y + thickness),
        (x + thickness, y + outer_h),
        (x, y + outer_h),
    ]
    segs = " ".join(f"L {px},{py}" for px, py in pts[1:])
    return f"M {pts[0][0]},{pts[0][1]} {segs} Z"


def star_path(cx: float, cy: float, R: float, r: float, n: int, hole_radius: float = 0.0) -> str:
    pts = []
    for i in range(2 * n):
        ang = math.pi * i / n
        rad = R if i % 2 == 0 else r
        px = cx + rad * math.cos(ang)
        py = cy + rad * math.sin(ang)
        pts.append((px, py))
    segs = " ".join(f"L {x},{y}" for x, y in pts[1:])
    d = f"M {pts[0][0]},{pts[0][1]} {segs} Z"
    if hole_radius and hole_radius > 0:
        d += " " + circle_path(cx, cy, hole_radius)
    return d


def window_panel_path(x: float, y: float, w: float, h: float, windows):
    d = rect_path(x, y, w, h)
    for (wx, wy, ww, wh) in windows:
        d += " " + rect_path(x + wx, y + wy, ww, wh)
    return d


def build_shapes_svg(sheet_w: int, sheet_h: int, seed: int = 7) -> str:
    random.seed(seed)
    parts = []

    # 大中小矩形
    rect_sizes = [
        (700, 480), (650, 420), (600, 380), (560, 360), (520, 340),
        (480, 320), (440, 300), (400, 280), (360, 260), (320, 240),
        (280, 200), (240, 180), (200, 150), (160, 120), (120, 80),
        (100, 60), (80, 50), (60, 40), (50, 30), (40, 25)
    ]
    for w, h in rect_sizes:
        parts.append(f'<rect width="{w}" height="{h}" />')

    # 圆角矩形
    rr_sizes = [(420, 280, 30), (360, 220, 20), (300, 180, 15), (240, 160, 12)]
    for w, h, r in rr_sizes:
        parts.append(f'<rect width="{w}" height="{h}" rx="{r}" ry="{r}" />')

    # 圆与椭圆
    circles = [220, 180, 150, 120, 90, 70]
    for r in circles:
        parts.append(f'<circle r="{r}" />')
    ellipses = [(200, 140), (180, 120), (160, 110), (140, 90), (120, 80)]
    for rx, ry in ellipses:
        parts.append(f'<ellipse rx="{rx}" ry="{ry}" />')

    # 环形
    rings = [(210, 120), (180, 90), (150, 70)]
    for ro, ri in rings:
        parts.append(f'<path d="{ring_path(0, 0, ro, ri)}" />')

    # 三角加强板（带孔）
    tri1 = triangle_with_circular_holes_path(0, 0, 520, 430, [(200, 240, 25), (320, 240, 25), (260, 150, 25)])
    tri2 = triangle_with_circular_holes_path(0, 0, 420, 360, [(160, 200, 20), (260, 200, 20), (210, 130, 20)])
    parts += [f'<path d="{tri1}" />', f'<path d="{tri2}" />']

    # 带窗洞面板
    win1 = window_panel_path(0, 0, 800, 500, [(60, 60, 220, 120), (520, 60, 220, 120), (60, 320, 220, 120), (520, 320, 220, 120)])
    win2 = window_panel_path(0, 0, 600, 360, [(40, 40, 160, 90), (400, 40, 160, 90), (40, 230, 160, 90), (400, 230, 160, 90)])
    parts += [f'<path d="{win1}" />', f'<path d="{win2}" />']

    # 星形与齿形
    parts += [
        f'<path d="{star_path(0, 0, 200, 90, 12, 40)}" />',
        f'<path d="{star_path(0, 0, 160, 70, 10, 35)}" />',
        f'<path d="{star_path(0, 0, 140, 60, 8,  30)}" />',
        f'<path d="{star_path(0, 0, 120, 50, 7,  0)}" />'
    ]

    # L 型支架
    parts += [
        f'<path d="{l_bracket_path(0, 0, 320, 320, 80)}" />',
        f'<path d="{l_bracket_path(0, 0, 260, 260, 70)}" />',
        f'<path d="{l_bracket_path(0, 0, 220, 220, 60)}" />'
    ]

    inner = "\n  ".join(parts)
    return f'''<svg viewBox="0 0 {sheet_w} {sheet_h}" width="{sheet_w}" height="{sheet_h}" xmlns="http://www.w3.org/2000/svg">
  {inner}
</svg>'''


def main():
    sheet_w, sheet_h = 4000, 2440
    sheets = [packaide.blank_sheet(sheet_w, sheet_h), packaide.blank_sheet(sheet_w, sheet_h),packaide.blank_sheet(sheet_w, sheet_h),packaide.blank_sheet(sheet_w, sheet_h),packaide.blank_sheet(sheet_w, sheet_h)]

    shapes_svg = build_shapes_svg(sheet_w, sheet_h, seed=11)

    result, placed, not_placed = packaide.pack(
        sheet_svgs=sheets,
        shapes=shapes_svg,
        tolerance=1.5,
        offset=4.0,
        partial_solution=True,
        rotations=12,
        persist=True
    )

    print(f"placed={placed}, not_placed={not_placed}")
    for i, out in result:
        out_path = make_unique_path(f"bias_mix_sheet_{i}.svg")
        with open(out_path, "w") as f_out:
            f_out.write(out)
        print("wrote:", out_path)


if __name__ == "__main__":
    print("[INFO] run at", time.strftime("%Y-%m-%d %H:%M:%S"))
    main()
