# Claude Code 工作状态红绿灯 🚦

一个浮在 Windows 桌面右上角的小窗口，实时显示 [Claude Code](https://claude.ai/code) 的工作状态：

- 🟢 **绿 — 工作中**：Claude 正在执行工具
- 🟡 **黄 — 思考中**：刚执行完工具、正在生成回复
- 🔴 **红 — 空闲**：空闲等待（超过 10 秒没有任何操作）

同时开多个 Claude Code 窗口也能反映——任一窗口在工作就亮绿/黄。

---

## 下载（三选一）

去 [Releases](../../releases) 页面下载：

| 版本 | 文件名 | 适合 | 需要装 Python？ | 体积 |
|---|---|---|---|---|
| **PyInstaller 版** | `traffic-light-pyinstaller.zip` | 大多数人 👈 | 否 | ~35 MB |
| **Nuitka 版** | `traffic-light-nuitka.zip` | 杀软误报 PyInstaller 版时换这个 | 否 | ~57 MB |
| **Python 源码版** | `traffic-light-source.zip` | 想自己跑/改代码的开发者 | 是（Python 3 + PyQt5）| 极小 |

> 不知道选哪个？**下 PyInstaller 版**。

## 安装（约 30 秒）

1. 解压下载的 zip；
2. **双击 `install.bat`**；
3. 完成。桌面出现快捷方式，红绿灯自动启动。

安装器自动完成：把程序放到 `%USERPROFILE%\.claude\traffic-light\` → 把钩子写进你的 Claude Code 配置（会**自动备份**原配置）→ 建桌面快捷方式 → 启动。

> ⚠️ 装完后，重启任何**已经开着的** Claude Code 窗口，新钩子才会生效。

## 要求

- Windows 10 / 11
- 已安装 Claude Code（https://claude.ai/code）
- exe 版**无需** Python；源码版需要 Python 3 + `pip install PyQt5`

---

## 工作原理

两部分协作：

1. **浮窗**（`traffic_light.exe` / `traffic_light.py`）：一个 PyQt5 无边框置顶窗口，每 0.5 秒读一次状态文件，按内容变色。
2. **钩子**（`update_status.ps1`）：Claude Code 在工具调用前/后/结束时调用它，把当前状态写进状态文件：
   - `PreToolUse` → `working`（绿）
   - `PostToolUse` → `thinking`（黄）
   - （窗口结束/超过 10 秒无操作 → 红）

状态文件固定在 `%LOCALAPPDATA%\ClaudeTrafficLight\status.json`。浮窗和钩子无论从哪运行、是不是打包成 exe，都读写这**同一个**文件，所以永远对得上；多个 Claude 窗口也共享这一个文件，任一窗口在工作就显示工作。

## 从源码构建（开发者）

```bash
pip install PyQt5

# PyInstaller 版（把 Python + PyQt5 打进单个 exe）
pip install pyinstaller
pyinstaller --onefile --noconsole --name traffic_light traffic_light.py

# Nuitka 版（编译成 C 机器码）
pip install nuitka
python -m nuitka --onefile --windows-console-mode=disable --enable-plugin=pyqt5 traffic_light.py
```

## 卸载

1. 右键红绿灯 → 退出；
2. 删除文件夹 `%USERPROFILE%\.claude\traffic-light\`；
3. 删除桌面快捷方式；
4. 打开 `%USERPROFILE%\.claude\settings.json`，删掉 `hooks` 里含 `traffic-light` 字样的几条（或用同目录的 `settings.json.bak` 还原）。

## 说明

- 杀毒软件**可能误报** exe（尤其 PyInstaller 版，是打包工具的通病），加白名单即可，**不是病毒**。Nuitka 版编成机器码，误报概率低，但体积更大、启动需解压略慢。
- 本项目与 Anthropic / Claude 官方无关，是一个第三方状态指示小工具。
