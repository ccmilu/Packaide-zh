# Packaide（中文文档）

[![Build status](https://github.com/DanielLiamAnderson/Packaide/actions/workflows/build.yml/badge.svg?branch=master)](https://github.com/DanielLiamAnderson/Packaide/actions) [![License: GPL3](https://img.shields.io/badge/License-GPL-blue.svg)](https://opensource.org/licenses/GPL-3.0)

一个用于快速且鲁棒的 2D SVG 形状套料（nesting）的库。注意，v2分支才是最新的，其他的都过时了。
ps：bias-left分支的排序偏向是左边，v2默认的是左上角。看需求选择。

### 致谢（Acknowledgements）

Packaide 来自研究项目 Fabricaide（帮助激光切割对象的设计者进行材料意识设计并充分利用边角料）。如果你在研究中使用了 Packaide，请引用：

> **Fabricaide: Fabrication-Aware Design for 2D Cutting Machines**  
> Ticha Sethapakdi, Daniel Anderson, Adrian Reginald Chua Sy, Stefanie Mueller  
> Proceedings of the 2021 ACM CHI Conference on Human Factors in Computing Systems, 2021

## 目录
- **它是什么**
- **系统要求**
  - Ubuntu 安装 CGAL
  - macOS 安装 CGAL
  - Windows 安装 CGAL
- **安装 Packaide（推荐方式，基于 conda，隔离环境）**
- **使用 Packaide**
  - 输入 / 输出格式
  - 参数说明
- **常见问题与解决方案**
- **用于开发的本地构建**
  - 测试
  - 基准测试（Benchmark）
  - 安装

## 它是什么？

<img align="right" style="height: 120px; width: 120px; margin: 5px;" src="https://danielanderson.net/images/packing-animation.gif" alt="Fast packing animation" />

Packaide 是一个 2D 套料库。给定一组形状，以及一组用于放置它们的板材（sheets），套料问题即找到一个不重叠的摆放方案。该问题在制造场景中非常常见。Packaide 优先考虑速度胜过最优性，通过快速启发式与工程实现，在保证质量的前提下实现远快于类似库的速度。

实现方面：Python 库 + C++ 后端（使用 [CGAL](https://www.cgal.org/) 进行鲁棒高效的计算几何）。与之配套的前端工具 Fabricaide 在这里：[Fabricaide](https://github.com/tichaesque/Fabricaide)。

## 系统要求
- 现代 C++(17) 编译器（GCC 7+、Clang 5+、MSVC 2019+）。
- Python 3.6+（推荐 3.9/3.10），已安装 Pip。
- [CGAL](https://www.cgal.org/)。

Packaide 在 Ubuntu 上开发并充分测试，也可在 macOS 与 Windows 上使用。

### Ubuntu 获取 CGAL
```bash
sudo apt install libcgal-dev
```

### macOS 获取 CGAL
使用 Homebrew：
```bash
brew install cgal
```
或使用 conda（推荐与本项目的 Python 依赖一起管理）：
```bash
conda install -c conda-forge cgal-cpp -y
```

### Windows 获取 CGAL
推荐使用 WSL，直接按 Ubuntu 步骤安装。若需原生 Windows：建议用 Conda：
```bash
conda.bat install -c conda-forge cgal-cpp
```
在已激活的 Conda 环境内执行，环境变量会自动配置得更好。

## 安装 Packaide（推荐：conda 隔离环境）
如果你只想安装与使用该库（而不是修改源代码），建议使用 conda 创建独立环境，不影响其他环境。

### 方式一：新建独立环境（推荐）
```bash
# 创建并激活环境（以 Python 3.9 为例，这里我用的是3.9，版本太新了可能会有问题，尤其是大于3.10的）
conda create -n packaide-env -c conda-forge python=3.9 cgal-cpp cmake ninja -y
conda activate packaide-env

# 让 CMake 在此环境优先找到 CGAL（很重要）
export CMAKE_PREFIX_PATH="$CONDA_PREFIX"

# 升级 pip 并安装 Python 依赖
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 安装本库（源代码根目录执行）
python -m pip install -v .
```

### 方式二：使用你已有的 conda Python 3.9 环境
```bash
conda activate <你的_py39_conda环境名>
conda install -c conda-forge cgal-cpp cmake ninja -y
export CMAKE_PREFIX_PATH="$CONDA_PREFIX"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -v .
```

安装完成后快速验证：
```bash
python - <<'PY'
import packaide
print("Imported:", packaide.__name__)
print("Blank sheet:", packaide.blank_sheet(10,10))
PY
```

## 使用 Packaide
安装完成后即可在 Python 中使用：

```python
# 示例：最小使用
import packaide

# 形状以 SVG 文本提供
shapes = """
<svg viewBox="0 0 432.13 593.04">
  <rect width="100" height="50" />
  <rect width="50" height="100" />
  <ellipse rx="20" ry="20" />
</svg>
"""

# 板材（sheet）也以 SVG 文本表示；其上的形状按“孔洞”处理
sheet = """
<svg width="300" height="300" viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="100" height="100" />
</svg>
"""

result, placed, fails = packaide.pack(
  [sheet],
  shapes,
  tolerance=2.5,
  offset=5,
  partial_solution=True,
  rotations=1,
  persist=True
)

print(f"placed={placed}, fails={fails}")
for i, out in result:
    with open(f'result_sheet_{i}.svg', 'w') as f_out:
        f_out.write(out)
```

### 输入 / 输出格式
- 输入的形状与板材均为 SVG 文本。解析使用 [SVGElements](https://pypi.org/project/svgelements/)。
- 输出的形状统一转换为 SVG Path 元素。
- 若需要在输出中识别输入的对应关系，输入形状上的 `class`、`id`、`name` 等属性会被保留。

### 参数说明
- **tolerance**：离散化近似误差。库总是以“外扩”方式处理离散多边形，保证不会出现欠近似导致相交。
- **offset**：每个离散多边形在套料前再额外膨胀的量（即最小间距）。
- **partial_solution**：True 时，如果无法全部放下，会返回部分可行解；False 时，要么全部放下，要么不返回解。
- **rotations**：尝试的旋转数量。1 表示仅用原始方向；大于 1 时，从 0 到 360 度均匀采样。
- **persist**：缓存部分计算结果以加速后续含重复形状的运行；会增加内存占用。也可通过 `custom_state` 传入自定义的 `State` 实例以控制复用范围。

## 常见问题与解决方案（Troubleshooting）
- **CMake 报错：Compatibility with CMake < 3.5 has been removed...**  
  现象：构建时提示 `cmake_minimum_required(VERSION 3.0)` 过旧。  
  解决（优先，无需改源码）：在安装命令前设置策略版本：
  ```bash
  export CMAKE_PREFIX_PATH="$CONDA_PREFIX"
  CMAKE_ARGS="-DCMAKE_POLICY_VERSION_MINIMUM=3.5" \
  python -m pip install -v .
  ```
  备选（若仍失败）：将项目根目录 `CMakeLists.txt` 的 `cmake_minimum_required(VERSION 3.0)` 提升到更高版本（如 `3.16`），再安装。

- **找不到 CGAL**  
  确保你在激活的 conda 环境内已安装 `cgal-cpp`，并设置：
  ```bash
  export CMAKE_PREFIX_PATH="$CONDA_PREFIX"
  ```
  之后重试 `python -m pip install -v .`。

- **编译器问题（macOS）**  
  需要可用的 Apple Clang（通常随 Xcode 命令行工具提供）。若缺失：
  ```bash
  xcode-select --install
  ```

## 用于开发的本地构建
如果你想修改源码并本地编译测试：

- 额外需要：
  - [CMake](https://cmake.org/) 与构建工具（Make 或 Ninja）。
  - Python 依赖：`python -m pip install -r requirements.txt`

### 测试（Debug 构建）
```bash
mkdir -p build/Debug && cd build/Debug
cmake -DCMAKE_BUILD_TYPE=Debug ../..
cmake --build . --config Debug
cmake --build . --target check --config Debug
```
该目标会运行一组示例并验证结果有效性。

### 基准测试（Release 构建）
```bash
mkdir -p build/Release && cd build/Release
cmake -DCMAKE_BUILD_TYPE=Release ../..
cmake --build . --config Release

# 额外需要 matplotlib
python -m pip install matplotlib

cmake --build . --target benchmarks --config Release
cmake --build . --target plots --config Release
```
生成的图表与数据在配置的构建目录下的 `benchmark/output`。

### 安装（从本地构建）
```bash
cmake --build . --target install --config Release
```
注意：如果你既通过 `pip install .` 安装过，又安装了本地构建版本，可能同时存在多个安装位置；请避免混用，或通过 `PYTHONPATH` 控制加载顺序。

---

- 文档更新：
  - 修复了安装章节中的笔误（原文误写为 `python -m pip install --user . -r -requirements.txt`）。
  - 新增了基于 conda 的隔离安装步骤与常见问题处理（包含 CMake 策略兼容报错的修复方法）。
