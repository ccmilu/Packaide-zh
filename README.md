# Packaide

[![Build status](https://github.com/DanielLiamAnderson/Packaide/actions/workflows/build.yml/badge.svg?branch=master)](https://github.com/DanielLiamAnderson/Packaide/actions) [![License: GPL3](https://img.shields.io/badge/License-GPL-blue.svg)](https://opensource.org/licenses/GPL-3.0)

一个用于快速且稳健的 2D SVG 形状排样（nesting）的库。

<img align="right" style="height: 120px; width: 120px; margin: 5px;" src="https://danielanderson.net/images/packing-animation.gif" alt="Fast packing animation" />

Packaide 由 C++ 实现的核心排样引擎与 Python 封装组成。底层使用 [CGAL](https://www.cgal.org/) 提供高效且鲁棒的计算几何能力。对于需要交互式前端工具的用户，可参考配套的前端项目 Fabricaide（见 [Fabricaide 仓库](https://github.com/tichaesque/Fabricaide)）。

## 目录

- [Packaide](#packaide)
  - [目录](#目录)
  - [简介](#简介)
  - [鸣谢](#鸣谢)
  - [环境与依赖](#环境与依赖)
    - [在 Ubuntu 安装 CGAL](#在-ubuntu-安装-cgal)
    - [在 macOS 安装 CGAL](#在-macos-安装-cgal)
    - [在 Windows 安装 CGAL](#在-windows-安装-cgal)
  - [只安装并使用（推荐）](#只安装并使用推荐)
  - [使用示例](#使用示例)
    - [输入/输出格式](#输入输出格式)
    - [参数说明](#参数说明)
  - [面向开发者的构建](#面向开发者的构建)
    - [测试](#测试)
    - [基准测试](#基准测试)
    - [安装（本地构建产物）](#安装本地构建产物)
  - [常见问题 FAQ](#常见问题-faq)

## 简介

给定一组形状（SVG）和若干张承载它们的板材（也是 SVG），Packaide 以启发式算法在保证不重叠的前提下快速求解可行的排样方案。Packaide 更注重速度而非全局最优，但在绝大多数实际场景下可以在极短时间内得到高质量方案。

## 鸣谢

Packaide 源自研究项目 Fabricaide，该系统帮助激光切割设计者进行材料意识设计决策并更好地利用边角料。如果你在研究中使用 Packaide，请引用：

> **Fabricaide: Fabrication-Aware Design for 2D Cutting Machines**  
> Ticha Sethapakdi, Daniel Anderson, Adrian Reginald Chua Sy, Stefanie Mueller  
> Proceedings of the 2021 ACM CHI Conference on Human Factors in Computing Systems, 2021

## 环境与依赖

- 现代 C++(17) 编译器（GCC 7+、Clang 5+、MSVC 2019+ 及以上版本均可）
- Python 3.6+（推荐 3.9/3.10）
- [CGAL](https://www.cgal.org/)
- CMake 与构建工具（Make 或 Ninja）

Packaide 在 Ubuntu 上开发与测试充分，同时也支持 macOS 与 Windows。

### 在 Ubuntu 安装 CGAL

```bash
sudo apt install libcgal-dev
```

### 在 macOS 安装 CGAL

```bash
brew install cgal
```

或者使用 conda（推荐与 Python 环境隔离）

```bash
conda install -c conda-forge cgal-cpp
```

### 在 Windows 安装 CGAL

- 推荐 [WSL](https://docs.microsoft.com/en-us/windows/wsl/) 后按 Ubuntu 方式安装；
- 或使用 [Conda](https://docs.conda.io/en/latest/) 安装 `cgal-cpp`；
- 若必须原生 Windows，可参考 CGAL 官方文档（可能需要额外配置）。

## 只安装并使用（推荐）

以下步骤适用于“只想安装库并在 Python 中使用，不想改源码”的用户。建议使用 conda 独立环境，避免污染其他环境。

以创建 Python 3.9/3.10 环境为例（任选其一，我用的是3.9，太新了可能有问题）：

```bash
# 创建并激活环境（包含 CGAL 与构建工具）
conda create -n packaide-env -c conda-forge python=3.10 cgal-cpp cmake ninja -y
conda activate packaide-env

# 让 CMake 在当前 conda 环境内优先找到 CGAL
export CMAKE_PREFIX_PATH="$CONDA_PREFIX"

# 升级 pip 并安装 Python 依赖
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 构建并安装本库（若遇到 CMake 策略报错，见 FAQ）
CMAKE_ARGS="-DCMAKE_POLICY_VERSION_MINIMUM=3.5" \
python -m pip install -v .
```

快速验证：

```bash
python - <<'PY'
import packaide
print("Imported:", packaide.__name__)
print("Blank sheet:", packaide.blank_sheet(10,10))
PY
```

如果更倾向于 Homebrew 安装 CGAL（macOS），也可：

```bash
# 使用 brew 安装 CGAL
brew install cgal

# 然后只需：
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
CMAKE_ARGS="-DCMAKE_POLICY_VERSION_MINIMUM=3.5" \
python -m pip install -v .
```

## 使用示例

```python
# 示例：最小化调用
import packaide

# 输入：形状（作为一个 SVG 文档字符串）
shapes = """
<svg viewBox="0 0 432.13 593.04">
  <rect width="100" height="50" />
  <rect width="50" height="100" />
  <ellipse rx="20" ry="20" />
</svg>
"""

# 输入：板材（同样是 SVG 文档字符串）。
# 板材中的形状视为“孔洞”，新放置的零件需避开这些区域。
sheet = """
<svg width="300" height="300" viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="100" height="100" />
</svg>
"""

# 进行排样（尽可能多地放置零件）
result, placed, fails = packaide.pack(
  [sheet],                  # 板材列表（每个是一个 SVG 文档）
  shapes,                   # 待放置的形状（一个 SVG 文档）
  tolerance = 2.5,          # 离散化与近似的容差
  offset = 5,               # 形状之间的额外安全间距（膨胀量）
  partial_solution = True,  # 允许返回部分可行解
  rotations = 1,            # 尝试的旋转数量（1 表示仅保持原朝向）
  persist = True            # 启用缓存以加速相似任务的后续运行
)

print(f"已放置 {placed} 个，未放置 {fails} 个")

# 输出结果为若干 (i, out) 对，i 是板材索引，out 是该板材上的 SVG 结果
for i, out in result:
  with open(f'result_sheet_{i}.svg', 'w') as f_out:
    f_out.write(out)
```

### 输入/输出格式

- 输入的板材与形状都以 SVG 文档表示；
- 使用 [SVGElements](https://pypi.org/project/svgelements/) 解析；
- 输出中所有形状都会标准化为 SVG Path；
- 为方便识别，输入元素的 `class`、`id`、`name` 属性将尽可能在输出中保留。

### 参数说明

- **tolerance**：形状离散化为折线时允许的近似误差。Packaide 会对多边形进行膨胀，确保不会低估原形状，避免误判“无重叠”。
- **offset**：在离散化后对多边形额外膨胀的量，用于保证零件之间的最小安全间距。
- **partial_solution**：若为 True，当所有零件无法全部放置时，将返回尽可能多的部分解；若为 False，则要么全部放置成功，要么全部失败。
- **rotations**：每个零件尝试的旋转姿态数量。值为 1 表示仅使用原始姿态；>1 时从 0~360 度均匀取样。
- **persist**：是否启用持久化缓存（会占用更多内存）。若需要跨多次任务复用缓存，可传入自定义 `State` 到 `custom_state`。

## 面向开发者的构建

如果你希望修改源码并从本地构建开始，请先安装构建依赖：

- CMake 与构建工具（如 Ninja 或 Make）
- Python 依赖（位于 `requirements.txt`）

```bash
python -m pip install -r requirements.txt
```

初始化 CMake 构建（推荐分别配置 Debug 和 Release）

### 测试

```bash
mkdir -p build/Debug && cd build/Debug
cmake -DCMAKE_BUILD_TYPE="Debug" ../..
cmake --build . --config Debug
cmake --build . --target check --config Debug
```

上述 `check` 目标会运行示例输入以验证排样结果的有效性。

### 基准测试

```bash
mkdir -p build/Release && cd build/Release
cmake -DCMAKE_BUILD_TYPE="Release" ../..
cmake --build . --config Release

# 生成基准与绘图（需要 matplotlib）
python -m pip install matplotlib
cmake --build . --target benchmarks --config Release
cmake --build . --target plots --config Release
```

基准图与原始数据可在已配置的 CMake 构建目录下的 `benchmark/output` 中找到。

### 安装（本地构建产物）

```bash
cmake --build . --target install --config Release
```

注意：若你既从源码安装，又用 `pip install` 安装，可能在不同路径存在两份安装；请确保 `PATH`/`PYTHONPATH` 指向你期望的版本，避免冲突。

## 常见问题 FAQ

- **CMake 报错：Compatibility with CMake < 3.5 has been removed**  
  原因是当前使用的 CMake 版本较新，而项目的 `cmake_minimum_required` 太低。推荐做法：在安装命令前设置
  
  ```bash
  CMAKE_ARGS="-DCMAKE_POLICY_VERSION_MINIMUM=3.5" \
  python -m pip install -v .
  ```
  
  或者（面向开发者）提升根目录 `CMakeLists.txt` 的 `cmake_minimum_required` 至更高版本（例如 `3.16`）。

- **CMake 找不到 CGAL**  
  请确认已安装 `cgal-cpp`（或系统已安装 CGAL），并在激活的 conda 环境中设置：
  
  ```bash
  export CMAKE_PREFIX_PATH="$CONDA_PREFIX"
  ```

- **Shapely/GEOS 相关问题**  
  通过 `pip install -r requirements.txt` 一般可满足；若仍有问题，可在激活环境内重新安装并用 `python -c "import shapely; print(shapely.__version__)"` 验证。

- **编译器不可用**  
  macOS 需安装 Xcode 命令行工具：`xcode-select --install`；Linux/WSL 环境请安装常见编译工具链。

---

版权：GPL-3.0。更多信息见 `LICENSE`。
