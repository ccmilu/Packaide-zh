# usertest_complex.py
# 更复杂的 Packaide 使用示例：带曲线的桌子零件在 2440x1220 板材上排版
import packaide

# 2440 x 1220 的板材（单位视作 mm）
sheets = [packaide.blank_sheet(2440, 1220)]

# 零件清单（带圆角/曲线），通过重复元素控制数量
# 注意：各元素尺寸需小于板材尺寸；viewBox 给一个上界包住全部原始零件即可
shapes = """
<svg viewBox="0 0 3000 2000" xmlns="http://www.w3.org/2000/svg">

  <!-- 1x 桌面：1500 x 800，圆角 R60 -->
  <rect width="1500" height="800" rx="60" ry="60" />

  <!-- 2x 长边桌围：1400 x 100，圆角 R20 -->
  <rect width="1400" height="100" rx="20" ry="20" />
  <rect width="1400" height="100" rx="20" ry="20" />

  <!-- 2x 短边桌围：600 x 100，圆角 R20 -->
  <rect width="600" height="100" rx="20" ry="20" />
  <rect width="600" height="100" rx="20" ry="20" />

  <!-- 2x 拉条：1400 x 60，圆角 R15 -->
  <rect width="1400" height="60" rx="15" ry="15" />
  <rect width="1400" height="60" rx="15" ry="15" />

  <!-- 4x 桌腿：80 x 710，圆角 R15（模拟脚端圆滑过渡） -->
  <rect width="80" height="710" rx="15" ry="15" />
  <rect width="80" height="710" rx="15" ry="15" />
  <rect width="80" height="710" rx="15" ry="15" />
  <rect width="80" height="710" rx="15" ry="15" />

  <!-- 4x 角码（带圆弧倒角的直角三角形），边长约 200：
       M 0,0 -> L 200,0 -> L 0,200 -> A 200,200 0 0 0 0,0 -> Z -->
  <path d="M 0,0 L 200,0 L 0,200 A 200,200 0 0 0 0,0 Z" />
  <path d="M 0,0 L 200,0 L 0,200 A 200,200 0 0 0 0,0 Z" />
  <path d="M 0,0 L 200,0 L 0,200 A 200,200 0 0 0 0,0 Z" />
  <path d="M 0,0 L 200,0 L 0,200 A 200,200 0 0 0 0,0 Z" />

</svg>
"""

# 执行排版
result, placed, fails = packaide.pack(
    sheets,
    shapes,
    tolerance=1.5,     # 曲线离散精度；更小更精细但更慢
    offset=3,          # 形状外扩间距（安全距离/刀缝）
    partial_solution=False,  # 必须全部放下；如不强制可设 True
    rotations=8,       # 允许 8 向旋转尝试，提高填充率
    persist=True       # 启用缓存，加速相似输入
)

print(f"已放置 {placed} 个零件，未放置 {fails} 个。")

# 写出排版结果（一个或多个板）
for i, out in result:
    with open(f"result_sheet1_{i}.svg", "w") as f_out:
        f_out.write(out)

print("已输出 result_sheet1_*.svg，可用浏览器或矢量软件查看。")