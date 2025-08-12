# userbiastext.py
# 构造测试以判断排样“左上偏好”是否被替换为“靠左优先（并尽量靠近中线）”。
# 要点：
# - case1: 基准（空白板），通常会放在左上角（不作为通过/失败，仅输出）
# - case2: 左侧上下各有孔洞，形成两个在 x 上同为最小的候选位置，但 y 距中线不同；
#         旧逻辑（x+y）偏好较小 y（更靠上），新逻辑应更靠近中线。
# - 输出结果文件时检测重复名，自动加序号避免覆盖。

import os
import re
import time
import packaide


def unique_path(base_name: str) -> str:
    """若文件已存在，则在文件名末尾加 _1, _2, ..."""
    name, ext = os.path.splitext(base_name)
    if not os.path.exists(base_name):
        return base_name
    i = 1
    while True:
        candidate = f"{name}_{i}{ext}"
        if not os.path.exists(candidate):
            return candidate
        i += 1


def parse_first_translate(svg_text: str):
    """从输出 SVG 中提取第一个形状的 translate(tx,ty)。返回 (tx, ty) 浮点数。"""
    # 形如: transform="translate(12.345,67.890) rotate(0.000,px,py)"
    m = re.search(r"transform=\"[^\"]*translate\(([-+]?\d*\.?\d+),([-+]?\d*\.?\d+)\)", svg_text)
    if not m:
        return None
    try:
        tx = float(m.group(1))
        ty = float(m.group(2))
    except Exception:
        return None
    return tx, ty


def save_result_svgs(result, prefix: str):
    paths = []
    for i, out in result:
        path = unique_path(f"{prefix}_sheet_{i}.svg")
        with open(path, "w") as f_out:
            f_out.write(out)
        paths.append(path)
    return paths


def run_case1_blank_sheet():
    """基准：空白板 + 一个小矩形零件。通常会偏左上。"""
    W, H = 1000, 1001  # 取奇数高，便于区分与中线的距离
    sheet = packaide.blank_sheet(W, H)
    shape = '<svg viewBox="0 0 5000 3000"><rect width="120" height="100" /></svg>'

    result, placed, fails = packaide.pack(
        [sheet], shape, tolerance=1.0, offset=2.0, partial_solution=True, rotations=1, persist=False
    )
    out_paths = save_result_svgs(result, prefix="bias_case1")

    # 提取第一个 translate
    first_svg = result[0][1] if result else ""
    t = parse_first_translate(first_svg)
    print("[CASE1] placed=", placed, "fails=", fails)
    print("[CASE1] files=", out_paths)
    if t:
        tx, ty = t
        print(f"[CASE1] translate=({tx:.3f},{ty:.3f}), midY={H/2:.3f}")
    else:
        print("[CASE1] 未解析到 translate()")


def run_case2_left_edge_tie():
    """左侧上下各有孔洞，形成两个同样靠左的候选窗口，y 与中线距离不同。"""
    W, H = 2000, 1201   # 奇数高，midY 非整数
    midY = H / 2.0

    # 两个左侧孔：上孔 [0,0,300,240]，下孔 [0,H-260,300,260]
    # 中间留出较大可用带，使得靠左的可行点接近 midY。
    sheet = f'''
<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="300" height="240" />
  <rect x="0" y="{H-260}" width="300" height="260" />
</svg>
'''
    # 小矩形零件
    shape = '<svg viewBox="0 0 5000 3000"><rect width="160" height="140" /></svg>'

    result, placed, fails = packaide.pack(
        [sheet], shape, tolerance=1.0, offset=2.0, partial_solution=True, rotations=1, persist=False
    )
    out_paths = save_result_svgs(result, prefix="bias_case2")

    # 解析 translate
    first_svg = result[0][1] if result else ""
    t = parse_first_translate(first_svg)

    print("[CASE2] placed=", placed, "fails=", fails)
    print("[CASE2] files=", out_paths)
    if t:
        tx, ty = t
        print(f"[CASE2] translate=({tx:.3f},{ty:.3f}), midY={midY:.3f}")
        # 判定：是否更靠近中线（而非更靠近顶部）
        dy_mid = abs(ty - midY)
        dy_top = abs(ty - 0.0)
        # 仅做提示性判断，非严格断言
        if dy_mid + 1e-6 < dy_top:
            print("[CASE2] 判定：更靠近中线，符合“靠左且居中”的新偏好。")
        else:
            print("[CASE2] 判定：未明显靠近中线，可能仍有“靠上”倾向或几何平局。")
    else:
        print("[CASE2] 未解析到 translate()")


if __name__ == "__main__":
    print("[INFO] 开始运行偏好测试...", time.strftime("%Y-%m-%d %H:%M:%S"))
    run_case1_blank_sheet()
    print("-" * 60)
    run_case2_left_edge_tie()
    print("[INFO] 完成。")
