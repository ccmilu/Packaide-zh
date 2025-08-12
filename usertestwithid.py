# usertestwithid.py
# 目的：验证排列后输出的 SVG 是否保留输入零件上的中文 id/class/name 等属性。
# 注意：为了确保属性被保留，请尽量把 id/class/name 等直接写在具体图形元素上（而不是只写在 <g> 上）。

import os
import re
import time
import packaide


def unique_path(base_name: str) -> str:
    """若文件已存在，则在文件名末尾加 _1, _2, ...，避免覆盖。"""
    name, ext = os.path.splitext(base_name)
    if not os.path.exists(base_name):
        return base_name
    i = 1
    while True:
        candidate = f"{name}_{i}{ext}"
        if not os.path.exists(candidate):
            return candidate
        i += 1


def build_shapes_svg() -> str:
    # 包含：
    # - path（外轮廓 + 内孔）
    # - 矩形/椭圆等基本形状
    # - 分组 <g>（组本身也带中文 id/class），但重点是把 id/class/name 写在具体元素上
    return (
        '<svg viewBox="0 0 4000 3000" xmlns="http://www.w3.org/2000/svg">\n'
        '  <g id="家具组合" class="组-甲">\n'
        '    <path id="桌面-外轮廓" class="外轮廓 零件A" name="桌面"\n'
        '          d="M 0,0 L 1000,0 L 1000,600 L 0,600 Z\n'
        '             M 200,200 L 300,200 L 300,300 L 200,300 Z\n'
        '             M 700,250 L 800,250 L 800,350 L 700,350 Z" />\n'
        '    <path id="支撑-环件" class="零件B 环件" name="支撑环"\n'
        '          d="M 0,0 L 400,0 L 400,400 L 0,400 Z\n'
        '             M 100,100 L 300,100 L 300,300 L 100,300 Z" />\n'
        '    <rect id="挡板-矩形" class="零件C 矩形" width="500" height="300" />\n'
        '    <rect id="挡板1-矩形" class="零件C 矩形" width="500" height="300" />\n'
        '    <ellipse id="侧盖-椭圆" class="零件D 椭圆" rx="150" ry="100" />\n'
        '  </g>\n'
        '  <g id="中文测试组" class="组-乙">\n'
        '    <rect id="小块-1" class="小块 类别X" width="120" height="80" />\n'
        '    <rect id="小块-2" class="小块 类别Y" width="100" height="60" />\n'
        '    <rect id="小块-3" class="小块 类别Y" width="100" height="60" />\n'
        '    <rect id="小块-4" class="小块 类别Y" width="100" height="60" />\n'
        '    <rect id="小块-5" class="小块 类别Y" width="100" height="60" />\n'
        '    <rect id="小块-6" class="小块 类别Y" width="100" height="60" />\n'
        '  </g>\n'
        '</svg>'
    )


def build_sheet_svg(w: int, h: int) -> str:
    return f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg"></svg>'


def extract_preserved_attrs(svg_text: str):
    # 提取输出 path 上的 id/class/name，便于快速核验（人工仍建议打开 SVG 检查）
    paths = re.findall(r"<path[^>]*>", svg_text)
    out = []
    for p in paths:
        pid = re.search(r"id=\"([^\"]+)\"", p)
        pclass = re.search(r"class=\"([^\"]+)\"", p)
        pname = re.search(r"name=\"([^\"]+)\"", p)
        out.append({
            'id': pid.group(1) if pid else None,
            'class': pclass.group(1) if pclass else None,
            'name': pname.group(1) if pname else None,
        })
    return out


def main():
    print("[INFO] 开始运行中文属性保留测试...", time.strftime("%Y-%m-%d %H:%M:%S"))
    sheet = build_sheet_svg(2440, 1220)
    shapes = build_shapes_svg()

    result, placed, fails = packaide.pack(
        [sheet],
        shapes,
        tolerance=1.5,
        offset=5,
        partial_solution=True,
        rotations=8,
        persist=False
    )

    print(f"placed={placed}, fails={fails}")
    for i, out in result:
        out_path = unique_path(f"result_withid_{i}.svg")
        with open(out_path, "w") as f:
            f.write(out)
        print("wrote:", out_path)

        # 打印前若干 path 的保留属性，便于快速核查
        attrs = extract_preserved_attrs(out)
        print(f"[sheet {i}] 保留属性（前 10 个 path）:")
        for j, a in enumerate(attrs[:10]):
            print(f"  {j+1}. id={a['id']!r}, class={a['class']!r}, name={a['name']!r}")

    print("[INFO] 完成。请打开 result_withid_*.svg 手动检查属性是否保留。")


if __name__ == "__main__":
    main()

