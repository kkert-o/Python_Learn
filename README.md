# Python Learn

这个仓库同时维护两套互相独立的 Python 学习产品：

| 目录 | 项目类型 | 技术栈 | 运行平台 |
| --- | --- | --- | --- |
| `android-app/` | 原生 Android App | Kotlin、Jetpack Compose、Material 3、Room | Android |
| `windows-exe/` | Windows 桌面 App 源码 | Python 3.11、PySide6、SQLite | Windows |
| `releases/windows/` | Windows 已打包程序 | PyInstaller 便携包 | Windows |

`android-app/` 和 `windows-exe/` 是两套独立工程，不会共用构建目录或运行环境。
这样更新其中一个平台时，不会覆盖或影响另一个平台。

## Android App

位置：

```text
android-app/
```

这是原来的 Android 原生工程，使用 Android Studio 打开 `android-app` 目录。

主要特点：

- Kotlin + Jetpack Compose
- 手机端内置 Python 运行环境
- 课程、练习、项目、训练、AI 教师和学习进度
- Room 本地数据持久化
- 支持主题、壁纸和内容独立更新

运行测试：

```powershell
cd android-app
.\gradlew.bat :app:testDebugUnitTest
```

详细说明见 [android-app/README.md](android-app/README.md)。

## Windows EXE 源码

位置：

```text
windows-exe/
```

这是完整的 Windows 桌面源码，不只是可执行文件。

主要特点：

- Python 3.11 + PySide6
- 独立 Python 工作台和代码高亮
- PowerShell 终端与库安装
- AI 教师、课程、训练、项目和爬虫实验室
- 壁纸、主题、毛玻璃和字体设置
- SQLite 本地进度保存

源码运行：

```powershell
cd windows-exe
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python main.py
```

重新打包：

```powershell
cd windows-exe
pyinstaller packaging\python-learner.spec --clean
```

## Windows 已打包程序

位置：

```text
releases/windows/PythonLearner-1.1.0-portable.zip
```

这是供普通用户直接使用的便携版本，不是源码。

使用方式：

1. 下载 `PythonLearner-1.1.0-portable.zip`
2. 解压到一个不会被系统清理的目录
3. 双击 `PythonLearner.exe`

不要只把 ZIP 中的 `PythonLearner.exe` 单独移动出来，它需要同目录下的 `_internal`
及其他运行文件。

## 两套程序的区别

| 对比项 | Android App | Windows EXE |
| --- | --- | --- |
| 目标设备 | 手机、平板 | Windows 电脑 |
| 源码目录 | `android-app/` | `windows-exe/` |
| 分发文件 | APK / AAB | `releases/windows/*.zip` |
| 构建工具 | Gradle / Android Studio | PyInstaller |
| 运行环境 | Android 内嵌 Python | Windows 内置 Python Worker |
| 数据存储 | Android Room | Windows SQLite |

## 发布规则

- Android 源码只修改 `android-app/`
- Windows 源码只修改 `windows-exe/`
- 编译后的 Windows 程序放在 `releases/windows/`
- 不建议把编译缓存、`build/`、`dist/` 或临时截图提交到 Git
