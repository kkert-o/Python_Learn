# Python 学习器 Windows EXE

这是 Python 学习器的 Windows 桌面版本。当前 V1.1 阶段 1 至 17 已完成，已经具备：

- PySide6 桌面主窗口和真实课程内容加载
- SQLite 数据库与版本迁移
- 16 个课程阶段、56 个知识点的课程列表
- 完整的知识点十段内容、小练习和顺序解锁
- 综合练习、错题记录、完成进度和学习中心
- 首页继续学习推荐
- 四类专项训练、20 道训练题和错题复习
- 选择题判题、代码结构判题和预测输出运行验证
- 13 个项目实战、验收要求、分级提示和项目工作区
- 项目进度持久化与 Python 工作台联动
- 15 个第三方库、8 类错误和工程实践资料库
- 全内容搜索、收藏和工作台联动
- AI Python 老师、四种教学模式和本地无 Key 引导
- Windows DPAPI 加密保存 API Key
- 爬虫合规检查、robots 规则判断和安全采集骨架
- 自由项目模板、最近项目和运行历史
- 毕业项目里程碑、工作区脚手架和交付检查
- 带图标的动态侧边导航、主题工作室和实时预览
- 本地壁纸上传、拖放、透明度调整和持久化
- Windows 毛玻璃背景与轻量悬停、切换动画
- 多尺寸透明应用图标、任务栏图标和 EXE 图标
- 独立 AI 接口配置栏、状态动画和可视化错误提示
- 自动草稿工作台、代码高亮、直接运行和代码字号调节
- 缓出式页面滚动、触摸惯性和主题化代码配色
- 统一的主按钮、次级按钮、答题选项、标签页和下拉框视觉
- 工作台 PowerShell 终端、库安装和持久化包目录
- 统一工作台工具栏图标、文件树操作和 AI 输入图标
- 自由项目分栏布局、原生任务栏图标和工作台视觉整理
- Python 工作台：多文件标签、行号、语法高亮、自动缩进、括号匹配
- 打开文件、保存、另存为、打开项目和新建项目
- 本地文件树：新建文件/文件夹、重命名、删除确认、刷新
- 独立 Python Worker：运行、停止、超时、stdout/stderr、input()
- 错误解释和错误行定位
- 最近项目、编辑状态和运行记录持久化

尚未进入后续阶段的训练、项目详情、第三方库、AI 老师等页面不会显示空壳按钮。

阶段验收记录见：

- [阶段 2 验收记录](docs/stage-2-acceptance.md)
- [阶段 3 验收记录](docs/stage-3-acceptance.md)
- [阶段 4 验收记录](docs/stage-4-acceptance.md)
- [阶段 5 验收记录](docs/stage-5-acceptance.md)
- [阶段 6 验收记录](docs/stage-6-acceptance.md)
- [阶段 7 验收记录](docs/stage-7-acceptance.md)
- [阶段 8 验收记录](docs/stage-8-acceptance.md)
- [阶段 9 验收记录](docs/stage-9-acceptance.md)
- [最终验收记录](docs/final-acceptance.md)
- [阶段 10 UI 验收记录](docs/stage-10-ui-acceptance.md)
- [阶段 11 主题与壁纸验收记录](docs/stage-11-theme-wallpaper-acceptance.md)
- [阶段 12 图标与 AI 配置验收记录](docs/stage-12-icon-ai-config-acceptance.md)
- [阶段 13 工作台与滚动验收记录](docs/stage-13-workbench-scroll-acceptance.md)
- [阶段 14 交互控件验收记录](docs/stage-14-controls-acceptance.md)
- [阶段 15 终端与控件验收记录](docs/stage-15-terminal-acceptance.md)
- [阶段 16 工作台与 AI 图标验收记录](docs/stage-16-workbench-ai-icons-acceptance.md)
- [阶段 17 页面布局与任务栏图标验收记录](docs/stage-17-layout-taskbar-acceptance.md)

## 开发环境

本项目按当前电脑的 Python 3.11 x64 开发。不会影响电脑上其他 Python 版本。

```powershell
cd D:\Codex_File\Python_learn_exe
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

## 启动

```powershell
python -m app
```

也可以：

```powershell
python main.py
```

## 测试

```powershell
python -m pytest
```

## 构建 Windows EXE

```powershell
pyinstaller packaging\python-learner.spec --clean
```

生成结果：

```text
dist\PythonLearner\PythonLearner.exe
```

用户数据写入 `%LOCALAPPDATA%\PythonLearner`，不会写入安装目录。
