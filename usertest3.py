import packaide

W, H = 2440, 1220  # 板材尺寸（建议单位一致，mm）
OFFSET = 3         # 形状之间的安全间距
TOL = 1.5          # 离散近似容差
ROTATIONS = 12      # 旋转尝试数量（1=不旋转；>1 时等角度取样）

def make_sheet(w, h):
    # 也可用 packaide.blank_sheet(w, h)
    return f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg"></svg>'

def make_shapes(w, h):
    # 多个不同尺寸的零件（大到小），使用 rect/ellipse
    # 均无 x/y，形状初始都在 (0,0)，实际位置由排样求解
    rects = [
        (600, 400),
        (550, 350),
        (500, 300),
        (450, 300),
        (400, 150),
        (350, 220),
        (300, 200),
        (250, 180),
        (200, 150),
        (150, 100),
        (120, 80),
        (100, 60),
        (80, 60),
        (60, 40),
        (40, 30),
    ]
    ellipses = [
        (220, 160),
        (180, 130),
        (150, 110),
    ]

    parts = []
    for w_, h_ in rects:
        parts.append(f'<rect width="{w_}" height="{h_}" />')
    for rx, ry in ellipses:
        parts.append(f'<ellipse rx="{rx}" ry="{ry}" />')

    # 使用与板材相同的 viewBox，便于视觉一致
    inner = "\n  ".join(parts)
    return f'''<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">
  {inner}
</svg>'''

def main():
    sheet = make_sheet(W, H)
    shapes = make_shapes(W, H)

    result, placed, fails = packaide.pack(
        [sheet],
        shapes,
        tolerance=TOL,
        offset=OFFSET,
        partial_solution=True,
        rotations=ROTATIONS,
        persist=False
    )
    print(f"placed={placed}, fails={fails}")
    for i, out in result:
        out_path = f"result_sheet3_{i}.svg"
        with open(out_path, "w") as f:
            f.write(out)
        print("wrote:", out_path)

if __name__ == "__main__":
    main()