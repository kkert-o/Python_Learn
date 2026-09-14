# Python 学习 App 开发文档

## 1. 文档目的

本文档面向后续参与本项目的开发者、维护者和内容编辑者，说明当前项目的：

- 产品范围与开发目标
- Android 工程结构和技术选型
- 应用启动、导航、状态管理和数据流
- 课程、项目、训练、错误博物馆和工具库的数据结构
- Room 数据库、迁移规则和本地设置
- Python 3.11 运行时、代码编辑器和大模型接入方式
- 内容在线更新、测试、构建、签名和发布流程
- 新增功能时的推荐扩展步骤
- 已知限制、风险点和发布前检查清单

当前文档基于以下开发状态：

| 项目 | 当前值 |
| --- | --- |
| App 版本 | `0.3.1` |
| versionCode | `4` |
| applicationId | `com.pythonlearn.app` |
| UI | Kotlin + Jetpack Compose Material 3 |
| 最低 Android | API 26 |
| 目标 Android | API 36 |
| Python | Chaquopy 3.11 |
| 课程内容版本 | `2` |
| 课程阶段 | 16 |
| 知识点 | 56 |
| 项目 | 13 |
| 单元测试 | 35 |
| 数据库版本 | 2 |

文档更新时间：2026-09-11。

---

## 2. 项目定位

本项目的目标不是只展示 Python 教程，而是帮助用户完成以下能力递进：

```text
看懂代码
  ↓
理解代码
  ↓
修改代码
  ↓
独立编写代码
  ↓
独立完成项目
```

项目重点包含：

- Python 基础、控制流程、数据结构和函数
- 文件、模块、对象和异常处理
- 网络、HTTP、API 和合规数据采集
- 数据分析、数据库和 Web API
- AI 应用、机器学习基础和负责任使用
- Git、自动化测试和代码质量
- 从 Lv.1 入门项目到毕业项目
- 知识掌握度、复习调度和个性化推荐
- 本地 Python 运行、错误解释和代码训练

开发新功能时，应优先回答以下问题：

1. 这个功能是否帮助用户更独立地理解和完成代码？
2. 功能是否有真实数据、持久化和可验证结果？
3. 是否会让用户过度依赖直接答案或 AI？
4. 是否引入法律、隐私、版权或安全风险？
5. 是否可以在当前工程中复用已有数据模型和组件？

---

## 3. 快速开始

### 3.1 环境要求

- Android Studio，建议使用支持 API 36 的稳定版
- JDK 17 或更高版本
- Android SDK 36
- Android Build Tools 和 Platform Tools
- Python 3.11，用于 Chaquopy 构建 Python 依赖
- Gradle 9.7.1，工程已经包含 Wrapper
- Windows、macOS 或 Linux 均可开发

当前工程在 Windows 环境下使用的本地 JDK 示例：

```text
D:\Codex_File\Python_learn\.tools\jdk17\jdk-17.0.20.1+1
```

`local.properties` 中需要配置 Android SDK，并根据本机情况配置 Chaquopy Python：

```properties
sdk.dir=C\:\\Users\\<user>\\AppData\\Local\\Android\\Sdk
chaquopy.python=C\:\\Path\\To\\Python311\\python.exe
```

如果没有配置 `chaquopy.python`，构建脚本会尝试环境变量 `CHAQUOPY_PYTHON`，最后回退到命令 `python`。

### 3.2 使用 Android Studio

1. 打开目录 `D:\Codex_File\Python_learn\PythonApp`。
2. 等待 Gradle Sync 完成。
3. 选择 `app` 运行配置。
4. 选择 API 26 及以上的模拟器或手机。
5. 点击 Run。

### 3.3 使用命令行

Windows PowerShell：

```powershell
cd D:\Codex_File\Python_learn\PythonApp
.\gradlew.bat :app:assembleDebug
```

运行单元测试：

```powershell
.\gradlew.bat :app:testDebugUnitTest
```

构建 Release：

```powershell
.\gradlew.bat :app:assembleRelease
```

如果本机使用独立 JDK，可以先设置：

```powershell
$env:JAVA_HOME="D:\Codex_File\Python_learn\.tools\jdk17\jdk-17.0.20.1+1"
```

### 3.4 安装到模拟器

```powershell
adb install -r app\build\outputs\apk\debug\app-debug.apk
```

启动应用：

```powershell
adb shell monkey -p com.pythonlearn.app -c android.intent.category.LAUNCHER 1
```

---

## 4. 技术栈

| 领域 | 技术 |
| --- | --- |
| 语言 | Kotlin |
| UI | Jetpack Compose、Material 3 |
| Android | Activity Compose、Lifecycle Compose |
| 本地数据库 | Room 2.7.2 |
| 后台任务 | WorkManager 2.10.1 |
| JSON | Gson 2.13.1 |
| 图片加载 | Coil Compose 2.7.0 |
| Python | Chaquopy 3.11 |
| Python 第三方库 | requests 2.32.4、beautifulsoup4 4.13.4 |
| 单元测试 | JUnit 4 |
| 构建 | Gradle Kotlin DSL、AGP、KSP |

当前 APK 内置的主要 Python 包：

```text
requests
beautifulsoup4
httpx
numpy
pandas
matplotlib
SQLAlchemy
pydantic
fastapi
flask
uvicorn
pytest
openai
click
rich
```

在“搜索与工具库”中可以运行“检查全部已内置库”，确认当前设备能否成功导入这些包。scikit-learn 和 Ruff 因 Chaquopy Android 轮子限制，标记为开发机工具。

依赖统一声明在：

```text
app/build.gradle.kts
```

新增依赖时优先使用稳定版本，并在升级依赖后同时验证：

- 单元测试
- Python 运行时
- Room 数据库迁移
- 内容更新
- Release 构建

---

## 5. 目录结构

```text
PythonApp/
├── app/
│   ├── build.gradle.kts
│   ├── proguard-rules.pro
│   └── src/
│       ├── main/
│       │   ├── AndroidManifest.xml
│       │   ├── assets/content/course_content.json
│       │   ├── java/com/pythonlearn/app/
│       │   │   ├── MainActivity.kt
│       │   │   ├── PythonLearningApplication.kt
│       │   │   ├── data/
│       │   │   │   ├── Catalog.kt
│       │   │   │   ├── KnowledgeModels.kt
│       │   │   │   ├── TrainingCatalog.kt
│       │   │   │   ├── V2Catalog.kt
│       │   │   │   ├── content/
│       │   │   │   ├── local/
│       │   │   │   └── repository/
│       │   │   ├── runtime/
│       │   │   │   ├── AiTeacher.kt
│       │   │   │   └── PythonRun.kt
│       │   │   └── ui/
│       │   │       ├── PythonApp.kt
│       │   │       ├── components/
│       │   │       ├── screens/
│       │   │       └── theme/
│       │   └── python/runner.py
│       └── test/java/com/pythonlearn/app/
├── docs/
│   ├── content-update.md
│   ├── development-guide.md
│   └── release-signing.md
├── gradle/
├── build.gradle.kts
├── settings.gradle.kts
├── gradle.properties
├── gradlew
├── gradlew.bat
├── keystore.properties.example
└── README.md
```

---

## 6. 总体架构

### 6.1 分层

```text
Compose UI
  ↓
PythonLearningApp / Screen
  ↓
MainActivity 状态与事件回调
  ↓
ProgressRepository
  ↓
Room DAO / SharedPreferences
```

课程和项目等内容：

```text
assets JSON 或 files 已安装 JSON
  ↓
CourseContentJsonCodec
  ↓
CourseContentValidator
  ↓
CourseCatalog / ProjectCatalog
  ↓
Compose UI
```

Python 执行：

```text
CodeWorkbenchScreen
  ↓
PythonRunner
  ↓
Chaquopy Java API
  ↓
runner.py
  ↓
PythonRunResult
  ↓
PythonErrorExplainer
```

### 6.2 应用启动过程

入口类是：

```text
PythonLearningApplication
```

启动顺序：

1. 初始化 Chaquopy。
2. 从 APK 资源读取 `course_content.json`。
3. 如果 JSON 加载失败，使用 Kotlin 内置兜底内容。
4. 创建 `ContentUpdateManager`。
5. 优先读取已经安装到 `files/content/course_content.json` 的更新版本。
6. 将内容安装到 `CourseCatalog` 和 `ProjectCatalog`。
7. 按 `BuildConfig.CONTENT_MANIFEST_URL` 决定是否注册后台更新任务。
8. 初始化 Room 数据库。
9. 创建 `ProgressRepository`。

关键文件：

```text
app/src/main/java/com/pythonlearn/app/PythonLearningApplication.kt
```

### 6.3 Activity 和全局状态

`MainActivity` 负责：

- 读取 SharedPreferences
- 创建 Compose 根节点
- 初始化主题、壁纸、法律地区、AI 配置
- 收集 Room 进度
- 收集学习仪表盘
- 向 UI 提供事件回调
- 把 UI 操作写入 Repository 和 SharedPreferences

当前全局状态包括：

```text
主题
主色
壁纸
自定义壁纸 URI
已完成课程
已完成项目
已完成训练
训练错题
课程错题
法律地区
收藏内容
AI-Free Challenge
AI 提问次数
AI 接口配置
学习仪表盘
```

关键文件：

```text
app/src/main/java/com/pythonlearn/app/MainActivity.kt
```

### 6.4 Compose 根导航

当前没有引入 Navigation Compose。主页面由底部导航控制，详情页使用显式的层级栈：

```kotlin
var destination by remember { mutableStateOf(Destination.HOME) }
var overlays by remember { mutableStateOf<List<AppOverlay>>(emptyList()) }
```

底部导航：

```text
首页
课程
练习
项目
我的
```

“我的”内部页面：

```text
主页面
外观
壁纸
学习中心
搜索与工具库
错误博物馆
AI 独立能力
```

`AppOverlay` 当前包含：

```text
Lesson
Workbench
Profile
AiTeacher
```

每一层进入时压栈，系统返回键弹出栈顶。页面内部详情还会先使用自己的 `BackHandler`：

```text
搜索详情或项目详情
  ↓
搜索与工具库
  ↓
我的

课程详情
  ↓
课程运行台
  ↓
课程详情
  ↓
课程列表

学习中心
  ↓
训练或课程详情
  ↓
学习中心
```

关键文件：

```text
app/src/main/java/com/pythonlearn/app/ui/PythonApp.kt
```

新增根页面时，至少需要修改：

1. `Destination` 或 `ProfilePanel`
2. `PythonLearningApp` 参数
3. 页面渲染分支
4. `MainShell` 参数
5. 对应入口按钮
6. 系统返回逻辑
7. 对应测试

---

## 7. 数据模型

### 7.1 课程领域模型

主要定义在：

```text
app/src/main/java/com/pythonlearn/app/data/Catalog.kt
```

核心类型：

| 类型 | 作用 |
| --- | --- |
| `LessonState` | 未学习、学习中、已完成、未解锁 |
| `LessonSummary` | 知识树中的课程摘要 |
| `CourseStage` | 一个学习阶段 |
| `LessonDetail` | 完整知识点正文 |
| `Quiz` | 课程小练习 |
| `ErrorExample` | 常见错误 |
| `ProjectInfo` | 项目需求、提示和起始代码 |

`LessonDetail` 对应统一课程模板：

```text
知识讲解
为什么需要它
真实项目用途
Python 示例
在线运行
小练习
常见错误
项目中的实际使用
法律与合规
下一步学习
```

### 7.2 训练模型

主要定义在：

```text
app/src/main/java/com/pythonlearn/app/data/TrainingCatalog.kt
```

训练类型：

```text
READ_CODE
PREDICT_OUTPUT
COMPLETE_CODE
DEBUG_LAB
```

每个 `TrainingExercise` 可以包含：

- `starterCode`
- `requiredSnippets`
- `forbiddenSnippets`
- `stdin`
- `referenceSolution`
- `preserveIndentation`

选择题使用：

```text
options
answerIndex
```

代码题使用：

```text
TrainingGrader.checkCode
```

`preserveIndentation = true` 用于缩进训练。普通代码题会删除空白后进行结构检查。

### 7.3 功能扩展目录

主要定义在：

```text
app/src/main/java/com/pythonlearn/app/data/V2Catalog.kt
```

包含：

- `LibraryCatalog`
- `ErrorMuseumCatalog`
- `EngineeringCatalog`
- `AiIndependenceCatalog`
- `AiIndependenceEngine`
- `GlobalSearchEngine`

### 7.4 学习状态模型

主要定义在：

```text
app/src/main/java/com/pythonlearn/app/data/KnowledgeModels.kt
```

知识点状态：

```text
NOT_STARTED
LEARNING
COMPLETED
MASTERED
NEEDS_REVIEW
LOCKED
```

复习目标类型：

```text
LESSON
TRAINING
QUIZ
```

---

## 8. Room 数据库

### 8.1 数据表

数据库类：

```text
app/src/main/java/com/pythonlearn/app/data/local/PythonLearningDatabase.kt
```

当前数据库版本为 `2`。

#### lesson_progress

保存知识点完成状态。

```text
lessonId TEXT PRIMARY KEY
completed INTEGER
updatedAt INTEGER
```

#### project_progress

保存项目完成状态。

```text
projectId TEXT PRIMARY KEY
completed INTEGER
updatedAt INTEGER
```

#### training_progress

保存训练结果。

```text
exerciseId TEXT PRIMARY KEY
completed INTEGER
needsReview INTEGER
correctCount INTEGER
wrongCount INTEGER
updatedAt INTEGER
```

#### quiz_progress

保存课程练习结果。

```text
question TEXT PRIMARY KEY
resolved INTEGER
correctCount INTEGER
wrongCount INTEGER
updatedAt INTEGER
```

#### review_schedule

保存间隔复习计划。

```text
targetKey TEXT PRIMARY KEY
dueAt INTEGER
reviewStage INTEGER
lastReviewedAt INTEGER
```

`targetKey` 格式：

```text
lesson:<lessonId>
training:<exerciseId>
quiz:<question>
```

#### learning_event

保存学习事件，用于按天统计学习时长、连续天数、每日任务、统计和推荐。

```text
id INTEGER AUTOINCREMENT
eventType TEXT
targetId TEXT
correct INTEGER
occurredAt INTEGER
```

### 8.2 DAO 约定

DAO：

```text
app/src/main/java/com/pythonlearn/app/data/local/ProgressDao.kt
```

主要规则：

- 列表观察统一使用 `Flow`
- 单项读取使用 `suspend fun`
- 写入使用 `@Insert(onConflict = REPLACE)`
- UI 不直接访问 DAO，而是通过 `ProgressRepository`

### 8.3 数据库迁移

任何表结构变化都必须：

1. 提升 `@Database(version = ...)`
2. 添加 Migration
3. 在 `Room.databaseBuilder` 中注册 Migration
4. 增加迁移测试或 Fake DAO 测试
5. 在模拟器上覆盖安装验证旧数据

不要使用 `fallbackToDestructiveMigration()`，否则升级会清除用户进度。

---

## 9. 学习进度、掌握度和复习

### 9.1 Repository 入口

```text
app/src/main/java/com/pythonlearn/app/data/repository/ProgressRepository.kt
```

主要能力：

```kotlin
observeProgress()
observeKnowledgeTree()
observeLearningDashboard()
observeDailyLearningStats()
completeLesson()
completeProject()
recordTrainingResult()
recordQuizResult()
migrateLegacyProgress()
```

### 9.2 掌握度计算

当前基础权重：

| 条件 | 分数 |
| --- | ---: |
| 完成课程 | 40 |
| 无训练题 | 15 |
| 有训练题 | 完成比例 × 30 |
| 小练习答对 | 30 |
| 小练习答错但有记录 | 10 |
| 全部训练完成 | 额外 5 |

未学习和未解锁节点显示为 `0%`。

掌握度达到 80 且课程完成时，状态可进入：

```text
MASTERED
```

### 9.3 复习调度

复习间隔：

```text
1 天
3 天
7 天
14 天
30 天
```

规则：

- 答题正确：进入下一复习阶段
- 答题错误：回到第 0 阶段
- 到期时间早于当前时间：进入到期复习队列

### 9.4 推荐顺序

推荐优先级：

1. 有到期复习时优先复习
2. 没有到期复习时继续当前学习中的知识点
3. 没有学习中的知识点时推荐下一个未学习知识点
4. 所有课程完成后推荐进入项目实战

修改推荐逻辑时必须同步检查：

```text
LearningDashboardEngine
LearningHubScreen
HomeScreen
PracticeScreen
```

`observeDailyLearningStats()` 根据 `learning_event` 计算当天课程分钟、已作答题目、预测输出挑战、连续学习天数和本周学习天数。首页每日任务与本周进度不再使用手动占位状态。

---

## 10. SharedPreferences

存储文件：

```text
python_app_settings
```

主要键：

| Key | 内容 |
| --- | --- |
| `theme_preference` | 主题模式 |
| `accent_value` | 主色 |
| `wallpaper_id` | 壁纸 |
| `custom_wallpaper_uri` | 自定义壁纸 URI |
| `legal_region` | 法律地区 |
| `favorites` | 收藏键集合 |
| `ai_free_challenges` | AI-Free 已完成项 |
| `ai_prompt_count` | AI 提问次数 |
| `ai_endpoint` | AI 接口地址 |
| `ai_api_key` | AI Key |
| `ai_model` | 模型名称 |

旧版本兼容键仍保留：

```text
completed_lessons
completed_projects
completed_training_ids
wrong_training_ids
wrong_quiz_ids
```

这些旧数据会在首次启动时迁移到 Room。

注意：AI Key 当前保存在普通 SharedPreferences 中。正式发布前建议迁移到 Android Keystore 或 EncryptedSharedPreferences，并避免任何日志输出。

---

## 11. 课程内容 JSON

### 11.1 文件位置

内置内容：

```text
app/src/main/assets/content/course_content.json
```

在线更新后的内容：

```text
files/content/course_content.json
```

读取逻辑：

```text
优先使用更新文件
失败时验证
验证失败则使用 APK 内置内容
```

### 11.2 顶层结构

```json
{
  "version": 1,
  "updatedAt": "2026-09-10",
  "stages": [],
  "lessons": {},
  "projects": []
}
```

字段说明：

| 字段 | 说明 |
| --- | --- |
| `version` | 内容版本，必须大于 0 |
| `updatedAt` | 内容更新时间 |
| `stages` | 学习阶段和知识点顺序 |
| `lessons` | 知识点 ID 到完整详情的映射 |
| `projects` | 项目列表 |

### 11.3 阶段结构

```json
{
  "label": "第一阶段",
  "name": "Python 基础",
  "progress": 0,
  "special": false,
  "lessons": [
    {
      "id": "python",
      "title": "Python 是什么",
      "minutes": 8,
      "state": "TODO"
    }
  ]
}
```

说明：

- `name` 会和 `LessonDetail.stage` 对应
- `lessons` 的顺序就是解锁顺序
- `state` 只是 DTO 字段，运行时实际状态由进度计算
- `special` 用于网络与安全等特殊阶段

### 11.4 知识点结构

每个 `lessons` 条目必须包含：

```json
{
  "id": "python",
  "title": "Python 是什么",
  "stage": "Python 基础",
  "level": "入门",
  "minutes": 8,
  "knowledge": [],
  "why": [],
  "purpose": "",
  "example": "",
  "exampleNotes": [],
  "quiz": {},
  "errors": [],
  "projectCode": "",
  "legalRisk": "",
  "legalNote": "",
  "legalBasis": "",
  "legalUpdated": "2026-09-10",
  "next": []
}
```

重要约束：

- JSON 键必须和 `id` 完全一致
- `example` 不能为空
- `quiz.options` 至少两项
- `quiz.answerIndex` 必须在选项范围内
- `next` 中引用的课程最好真实存在
- 所有法律内容必须标注地区和更新时间

### 11.5 项目结构

```json
{
  "id": "guess",
  "title": "猜数字",
  "level": "Lv.1 入门项目",
  "goal": "项目目标",
  "requirements": [],
  "knowledge": [],
  "hints": [],
  "starter": "# 起始代码"
}
```

项目必须遵守：

- 不给完整答案
- 提供目标
- 提供验收要求
- 提供知识依赖
- 至少提供两到三层提示
- `starter` 是骨架，不是最终实现

### 11.6 新增知识点步骤

1. 在 `stages` 的对应阶段增加摘要。
2. 在 `lessons` 中增加同名键。
3. 填充完整 10 段模板数据。
4. 更新前后课程的 `next`。
5. 增加或调整相关训练题。
6. 增加错误博物馆条目，如果这是一个高频错误。
7. 运行：

```powershell
.\gradlew.bat :app:testDebugUnitTest
```

8. 在模拟器中打开该知识点，检查：
   - 标题和阶段
   - 代码展示
   - 小练习
   - 法律说明
   - 下一节跳转
   - 完成课程后的解锁状态

### 11.7 新增阶段步骤

1. 决定阶段放在课程顺序中的位置。
2. 添加 `CourseStage` JSON。
3. 添加所有知识点的完整详情。
4. 检查前置阶段和下一阶段解锁关系。
5. 更新 `README.md` 的阶段数量。
6. 更新测试中的阶段覆盖断言。
7. 检查“我的”页面能力数据是否显示新阶段。

### 11.8 新增项目步骤

1. 在 `projects` 数组增加项目。
2. 使用唯一 `id`。
3. 设置真实难度级别。
4. 写清楚目标、功能需求和验收标准。
5. 提供渐进式提示。
6. 只提供起始代码。
7. 如果是毕业项目，必须覆盖需求、界面、数据库、API、测试和发布要求。
8. 在模拟器中确认项目列表、详情页、运行台和完成状态。

---

## 12. 内容校验

校验器：

```text
app/src/main/java/com/pythonlearn/app/data/content/CourseContentJsonCodec.kt
```

当前校验内容：

- 版本大于 0
- 更新时间非空
- 阶段不能为空
- 知识点不能为空
- 项目不能为空
- 阶段中的知识点 ID 不能重复
- 摘要必须有对应详情
- 详情不能游离于阶段之外
- 详情 ID 和 JSON 键一致
- 标题不能为空
- 示例代码不能为空
- 小练习选项数量足够
- 答案下标合法
- 项目 ID 不能重复
- 项目标题和目标不能为空

新增内容字段后，应把字段加入 DTO、Domain 和 Validator。

---

## 13. Python 运行时

### 13.1 Java 入口

```text
app/src/main/java/com/pythonlearn/app/runtime/PythonRun.kt
```

主要类型：

```text
PythonRunner
PythonRunResult
PythonErrorExplainer
```

`PythonRunner.run()` 会同步执行代码，`runAsync()` 使用单线程执行器。

### 13.2 Python 入口

```text
app/src/main/python/runner.py
```

职责：

- 捕获标准输出和错误输出
- 替换 `input`
- 限制输入行
- 限制执行步数
- 编译和执行用户代码
- 返回 JSON 结果

当前最大执行步数：

```text
300000
```

这是防止无限循环的基本保护，不代表真正安全的沙箱。正式运营前建议增加：

- 每次运行的超时终止
- 内存限制
- 子进程隔离
- 更严格的模块白名单
- 资源配额和频率限制

### 13.3 错误解释

`PythonErrorExplainer` 当前覆盖：

```text
NameError
SyntaxError
IndentationError
TabError
TypeError
ValueError
ZeroDivisionError
IndexError
KeyError
AttributeError
ImportError
ModuleNotFoundError
UnboundLocalError
RecursionError
MemoryError
KeyboardInterrupt
EOFError
SystemExit
```

新增错误类型时：

1. 在 `explain()` 增加分支。
2. 给出初学者能理解的原因。
3. 给出一到两个修复方向。
4. 在 `CatalogAndRunnerTest` 增加测试。
5. 在错误博物馆增加对应条目。

---

## 14. 代码编辑器

入口：

```text
app/src/main/java/com/pythonlearn/app/ui/screens/CodeWorkbenchScreen.kt
```

当前支持：

- 行号
- 语法高亮
- 括号平衡状态
- 自动缩进
- 复制
- 清空
- 格式化
- 运行
- 停止界面等待
- 输入区
- 字号
- 行高
- 自动换行
- 缩进线
- Dark
- Light
- Dracula
- Monokai
- GitHub
- Solarized
- One Dark
- 自定义 9 类颜色

编辑器设置保存在：

```text
code_workbench_settings
```

自定义颜色格式：

```text
#RRGGBB
```

新增代码主题时：

1. 在 `codeThemes` 增加 `CodeTheme`。
2. 检查关键字、字符串、数字、注释、函数、类型和错误颜色。
3. 在明暗背景下检查对比度。
4. 在模拟器中实际运行代码。

修改语法高亮时要特别注意：

- 注释优先于字符串
- 字符串内的关键字不能再次着色
- 标识符边界不能切坏中文和 Unicode
- 不支持真实 AST 语法时，正则规则必须可预测
- 高亮失败不能影响原始文本编辑

---

## 15. 训练系统

页面：

```text
app/src/main/java/com/pythonlearn/app/ui/screens/TrainingSessionScreen.kt
```

流程：

```text
选择训练类型
  ↓
逐题训练
  ↓
选择题即时判题
或
代码题检查关键结构
  ↓
查看提示和参考实现
  ↓
写回训练进度
  ↓
错题进入复习
```

新增代码训练时必须：

1. 提供 `starterCode`
2. 提供 `requiredSnippets`
3. 提供 `referenceSolution`
4. 必要时提供 `forbiddenSnippets`
5. 检查参考实现能否通过 Grader
6. 检查初始错误代码不能通过
7. 为缩进训练设置 `preserveIndentation = true`

训练代码不会直接执行用户提交内容，除非任务类型是 `PREDICT_OUTPUT` 的验证运行。代码题当前主要做结构检查，不是完整语义测试。

---

## 16. 错误博物馆

数据：

```text
app/src/main/java/com/pythonlearn/app/data/V2Catalog.kt
```

每条错误包含：

```text
title
errorType
symptom
cause
brokenCode
fixedCode
prevention
lessonId
```

新增错误条目时：

1. 使用真实可复现的错误代码。
2. 提供可运行的修复代码。
3. 解释现象和根因，而不只写“这样写不对”。
4. 给出下一次避免的方法。
5. 尽量关联到课程知识点。
6. 在 `V2FeatureCatalogTest` 验证错误代码和修复代码不同。

---

## 17. 搜索、收藏和工具库

页面：

```text
app/src/main/java/com/pythonlearn/app/ui/screens/V2ToolsScreens.kt
```

搜索结果类型：

```text
LESSON
PROJECT
TRAINING
LIBRARY
ERROR
ENGINEERING
```

收藏键格式：

```text
lesson:<id>
project:<id>
training:<id>
library:<id>
error:<id>
engineering:<id>
```

收藏实际存储在 SharedPreferences。

新增搜索类型时：

1. 增加 `SearchResultKind`
2. 增加搜索数据源
3. 增加 `favoriteKey`
4. 增加结果点击路由
5. 增加收藏结果恢复逻辑
6. 增加搜索测试

第三方库分类：

```text
NETWORK
DATA
DATABASE
WEB
TESTING
AI
TOOLS
```

工程模块分类：

```text
GIT
QUALITY
TESTING
```

---

## 18. AI Python 老师

### 18.1 配置

文件：

```text
app/src/main/java/com/pythonlearn/app/runtime/AiTeacher.kt
```

默认接口：

```text
https://api.deepseek.com/chat/completions
```

默认模型：

```text
deepseek-chat
```

未配置 API Key 时，本地引导模式仍然可用。

### 18.2 学习模式

```text
老师模式
只给思路
普通提示
只指出错误
直接答案
```

默认必须保持“老师模式”，避免 AI 直接替用户完成项目。

### 18.3 隐私和安全

当前风险点：

- API Key 以明文形式存在 SharedPreferences
- 用户输入会发送给配置的第三方接口
- 没有输出内容审核
- 没有费用上限
- 没有请求级取消

正式发布前建议增加：

- Android Keystore 或 EncryptedSharedPreferences
- 服务端代理模式
- 密钥轮换
- 敏感信息检测
- 请求超时、限流和预算
- 日志脱敏
- 模型输出结构校验

### 18.4 AI 独立能力

数据：

```text
AiIndependenceCatalog
AiIndependenceEngine
```

经验值：

```text
完成课程 × 12
完成项目 × 45
完成训练 × 8
完成 AI-Free Challenge × 30
```

依赖指数由 AI 提问次数和独立实践数量估算，只作为提醒，不应作为惩罚或用户评价。

---

## 19. 法律与合规系统

法律地区：

```text
中国大陆
日本
美国
欧盟
其他
```

法律内容当前存储在课程 JSON 中，后续可以独立更新。

每条法律内容必须包含：

- 风险等级
- 司法辖区
- 适用条件
- 风险因素
- 法律依据或参考原则
- 更新时间
- 不构成法律意见的说明

开发规则：

- 不直接判断“合法”或“违法”
- 不阻止用户学习通用技术
- 不把工具本身认定为违法工具
- 强调访问对象、授权、频率、数据类型和用途
- 涉及个人信息、登录状态、访问控制或商业用途时提高风险等级

---

## 20. UI 和设计系统

主题：

```text
app/src/main/java/com/pythonlearn/app/ui/theme/Theme.kt
```

公共组件：

```text
app/src/main/java/com/pythonlearn/app/ui/components/Components.kt
```

主要组件：

```text
GlassCard
SectionTitle
ProgressTrack
Tag
CodePanel
CircleAvatar
IconAvatar
MutedText
BackBar
```

设计规则：

- 使用 Material 3
- 圆角克制的卡片
- 不使用大面积渐变
- 不使用持续动画
- 信息密度适中
- 文字颜色必须适配浅色、深色和自定义壁纸
- 平板宽度从 760dp 开始进入居中 720dp 容器
- 图标按钮必须有内容描述
- 新增页面优先复用公共组件

如果新增宽度布局，需要同时检查：

```text
411 x 914 dp 手机
1365 dp 左右平板
```

---

## 21. 内容在线更新

相关文件：

```text
app/src/main/java/com/pythonlearn/app/data/content/ContentUpdateManager.kt
app/src/main/java/com/pythonlearn/app/data/content/ContentUpdateWorker.kt
docs/content-update.md
```

清单字段：

```json
{
  "version": 3,
  "updatedAt": "2026-09-15",
  "contentUrl": "https://example.com/course_content-v3.json",
  "sha256": "sha256-value",
  "minAppVersion": 1
}
```

安全规则：

- 清单和内容必须使用 HTTPS
- 内容大小上限 5 MB
- 支持 SHA-256 校验
- 支持最低 App 版本
- 临时文件写入后原子替换
- 更新失败保留旧内容
- 本地内容无效则回退 APK 内置内容

构建时启用后台更新：

```powershell
.\gradlew.bat :app:assembleRelease `
  -PcontentManifestUrl="https://example.com/content/manifest.json"
```

或：

```text
CONTENT_MANIFEST_URL=https://example.com/content/manifest.json
```

未配置地址时不会联网检查。

---

## 22. 测试体系

### 22.1 测试文件

```text
CatalogAndRunnerTest.kt
ContentUpdateManagerTest.kt
V2FeatureCatalogTest.kt
```

主要覆盖：

- 新用户从零开始
- 所有课程都有详情
- 课程解锁
- 错误解释
- 训练目录完整性
- 参考实现通过检查
- Debug 错误代码不能通过
- Repository 训练状态
- 旧数据迁移
- 复习阶段推进
- 掌握度和推荐
- JSON 内容完整性
- 内容更新校验
- 第三方库分类
- 错误博物馆
- 全局搜索
- AI 独立能力

### 22.2 测试命令

```powershell
.\gradlew.bat :app:testDebugUnitTest
```

### 22.3 Fake DAO

`CatalogAndRunnerTest.kt` 中的 `FakeProgressDao` 使用 `MutableStateFlow` 模拟 Room。

新增 DAO 方法时，必须同步更新 Fake DAO，否则单元测试无法编译。

### 22.4 推荐测试顺序

每次修改后：

1. 单元测试
2. Debug 构建
3. 安装模拟器
4. 启动检查
5. 核心流程手动检查
6. Release 构建
7. 检查日志

---

## 23. 模拟器手动验收

### 23.1 启动模拟器

```powershell
emulator -avd medium_phone -no-snapshot-save -no-boot-anim
```

等待：

```powershell
adb wait-for-device
adb shell getprop sys.boot_completed
```

### 23.2 安装

```powershell
adb install -r app\build\outputs\apk\debug\app-debug.apk
```

### 23.3 核心检查

必须检查：

- 首页推荐卡
- 课程 16 个阶段
- 知识点详情 10 段模板
- 课程小练习和错题
- 训练四类
- 项目 Lv.1 到毕业项目
- Python 运行结果
- 中文错误解释
- 编辑器主题和字号
- 错误博物馆展开
- 全局搜索
- 收藏
- AI 独立能力
- 系统返回键

### 23.4 平板检查

可以临时修改显示参数：

```powershell
adb shell wm size 2048x1536
adb shell wm density 240
adb shell settings put system accelerometer_rotation 0
adb shell settings put system user_rotation 1
```

检查后恢复：

```powershell
adb shell wm size reset
adb shell wm density reset
adb shell settings put system accelerometer_rotation 1
adb shell settings put system user_rotation 0
```

### 23.5 崩溃检查

```powershell
adb logcat -c
adb logcat -d -t 500 | Select-String "FATAL EXCEPTION|AndroidRuntime"
```

---

## 24. 构建和签名

### 24.1 Debug

```powershell
.\gradlew.bat :app:assembleDebug
```

输出：

```text
app/build/outputs/apk/debug/app-debug.apk
```

Debug 只能用于开发，不应发布。

### 24.2 Release

未配置密钥：

```text
app/build/outputs/apk/release/app-release-unsigned.apk
```

配置密钥后：

1. 生成 keystore。
2. 复制 `keystore.properties.example` 为 `keystore.properties`。
3. 填入路径和密码。
4. 确认 `keystore.properties` 已经被 `.gitignore` 忽略。
5. 运行 Release 构建。

详细步骤见：

```text
docs/release-signing.md
```

### 24.3 App Bundle

```powershell
.\gradlew.bat :app:bundleRelease
```

正式分发优先使用 App Bundle。

---

## 25. 常见开发任务

### 25.1 新增首页卡片

1. 修改 `HomeScreen.kt`
2. 使用 `GlassCard`
3. 如果需要新导航，增加回调参数
4. 在 `PythonApp.kt` 和 `MainShell` 传递回调
5. 检查手机和平板布局

### 25.2 新增“我的”工具

1. 增加 `ProfilePanel`
2. 增加页面 Composable
3. 在 `PythonLearningApp` 增加渲染分支
4. 在 `ProfileScreen` 增加入口
5. 在 `MainShell` 增加回调
6. 确认系统返回键返回“我的”

### 25.3 新增训练类型

1. 在 `TrainingType` 增加类型
2. 确定选择题或代码题
3. 增加训练数据
4. 在 `TrainingSessionScreen` 增加交互分支
5. 增加参考实现和 Grader 测试
6. 确认为现有四类测试仍然通过

### 25.4 新增数据库字段

1. 修改 Entity
2. 更新 DAO
3. 更新 Repository
4. 更新 `ProgressSnapshot`
5. 调整数据库版本
6. 添加 Migration
7. 更新 Fake DAO
8. 增加迁移测试
9. 模拟器覆盖安装验证

### 25.5 新增内容字段

1. 修改 `LessonDto` 或 `ProjectDto`
2. 修改 Domain 类型
3. 增加 JSON 数据
4. 增加 Validator 规则
5. 检查在线更新兼容性
6. 增加测试

### 25.6 新增 AI 模式

1. 增加模式名称
2. 修改 `systemPromptFor`
3. 修改本地 `replyFor`
4. 检查默认模式不泄漏完整答案
5. 增加隐私和异常处理
6. 在模拟器中测试无 Key 和有 Key 两条路径

---

## 26. 编码规范

### Kotlin

- 使用 4 个空格缩进
- 公共 API 使用清晰命名
- 优先使用不可变 `val`
- UI 状态使用 `remember` / `mutableStateOf`
- 数据库和网络操作放到 `Dispatchers.IO`
- 不在 Composable 中直接执行阻塞操作
- 页面之间通过回调传递事件
- 数据转换集中到 DTO 或 Mapper

### Compose

- 一个 Composable 只负责一个页面或组件
- 列表使用 `LazyColumn`
- 固定尺寸控件使用 `width`、`height` 或 `widthIn`
- 不在 Composable 内创建高成本对象
- 使用 `MaterialTheme.colorScheme`
- 新增可点击图标必须提供 `contentDescription`
- 新增长文本必须确认不会覆盖周围内容

### 内容

- 先给现象，再给原因
- 先给思路，再给代码
- 代码要能运行
- 不直接给完整项目答案
- 法律说明不构成法律意见
- 更新日期必须准确

### Git

- 一次提交只做一类修改
- 提交前运行测试
- 不提交 `keystore.properties`
- 不提交 API Key
- 不提交构建产物
- 提交信息说明结果，而不是只写“update”

---

## 27. 常见故障

### Gradle 找不到 Java

设置 `JAVA_HOME` 为 JDK 17 或更高版本。

### Chaquopy 找不到 Python

检查：

```properties
chaquopy.python=C\:\\Path\\To\\Python311\\python.exe
```

或设置：

```powershell
$env:CHAQUOPY_PYTHON="C:\Path\To\Python311\python.exe"
```

### Android SDK XML 版本警告

通常由 Android Studio 和命令行工具版本不一致导致。保持 SDK、Build Tools 和 Android Studio 更新可以消除。

### 课程 JSON 加载失败

检查：

- 是否是合法 JSON
- 阶段和详情 ID 是否一致
- 是否缺少必填字段
- 小练习答案下标是否越界
- 项目 ID 是否重复

应用会回退到内置内容，但日志中会记录错误。

### 数据库升级后崩溃

检查：

- 是否提升版本号
- 是否添加 Migration
- 是否注册 Migration
- SQL 字段是否和 Entity 完全一致
- 是否使用 `INTEGER` 表示 Boolean

### Python 运行没有返回

检查：

- Chaquopy 是否初始化
- `runner.py` 是否存在
- 用户代码是否进入无限循环
- 输入行是否足够
- 是否触发最大步数限制

### 更新内容没有生效

检查：

- `CONTENT_MANIFEST_URL` 是否配置
- 是否使用 HTTPS
- 清单版本是否高于当前版本
- SHA-256 是否正确
- `minAppVersion` 是否过高
- 内容结构是否通过 Validator

---

## 28. 已知限制和技术债

1. AI Key 当前以普通 SharedPreferences 保存。
2. Python 执行没有独立进程级超时和内存隔离。
3. 代码训练主要检查关键结构，不是完整语义测试。
4. 课程内容较多，但法律说明仍需按地区持续复核。
5. 在线更新没有正式后端和发布管理后台。
6. 没有账号系统和跨设备同步。
7. 当前导航使用根级状态，页面继续增长后建议迁移 Navigation Compose。
8. `CourseCatalog.kt` 仍保留大型内置兜底内容，后续可拆分。
9. Room Schema 目前没有导出到版本控制，建议改为 `exportSchema = true`。
10. Release 签名需要外部密钥，仓库只能提供流程，不能保存正式密钥。
11. scikit-learn 和 Ruff 当前没有适用于 Chaquopy 3.11 的 Android 轮子，因此标记为开发机工具，不随 APK 打包。

---

## 29. 后续路线

建议后续按以下优先级推进：

1. 把 AI Key 迁移到加密存储。
2. 为 Python 运行增加超时和隔离。
3. 导出 Room Schema 并补充迁移测试。
4. 迁移到 Navigation Compose。
5. 增加完整周报、学习时段分析和更精细的时长记录。
6. 增加课程收藏分组和阅读历史。
7. 增加项目分步验收和测试记录。
8. 增加服务端内容发布工具。
9. 增加 AI 服务的服务端代理和费用统计。
10. 完成正式签名、真机矩阵和商店发布。

---

## 30. 发布前检查清单

### 功能

- [ ] 所有底部导航可进入
- [ ] 所有课程详情存在
- [ ] 所有项目详情存在
- [ ] 项目没有完整答案
- [ ] 训练参考实现通过
- [ ] Python 示例可以运行
- [ ] 错误代码有修复方式
- [ ] 收藏可以恢复
- [ ] AI-Free 状态可保存
- [ ] 法律说明有地区和日期

### 数据

- [ ] Room 版本和 Migration 正确
- [ ] 旧版本覆盖安装不丢失数据
- [ ] 内容更新失败回退正常
- [ ] 无 API Key 时本地 AI 模式可用
- [ ] 自定义壁纸重启后仍可用

### UI

- [ ] 手机宽度无重叠
- [ ] 平板宽度无过度拉伸
- [ ] 浅色模式可读
- [ ] 深色模式可读
- [ ] 自定义壁纸文字可读
- [ ] 系统返回键行为正确
- [ ] 键盘弹出不遮挡关键按钮

### 工程

- [ ] `testDebugUnitTest` 通过
- [ ] Debug 构建通过
- [ ] Release 构建通过
- [ ] APK 或 AAB 已签名
- [ ] `keystore.properties` 未提交
- [ ] 日志没有 FATAL EXCEPTION
- [ ] README 和开发文档已更新

---

## 31. 关键文件索引

| 文件 | 用途 |
| --- | --- |
| `MainActivity.kt` | Activity、全局状态、设置持久化 |
| `PythonLearningApplication.kt` | 应用初始化、内容加载 |
| `data/Catalog.kt` | 课程和项目领域模型、兜底目录 |
| `data/TrainingCatalog.kt` | 训练数据、Grader |
| `data/V2Catalog.kt` | 库、错误、工程、AI、搜索 |
| `data/KnowledgeModels.kt` | 知识状态、复习、推荐 |
| `data/local/ProgressEntities.kt` | Room Entity |
| `data/local/ProgressDao.kt` | Room DAO |
| `data/local/PythonLearningDatabase.kt` | Room 数据库和 Migration |
| `data/repository/ProgressRepository.kt` | 学习进度写入和观察 |
| `data/content/CourseContentDto.kt` | 内容 DTO 和 Domain 转换 |
| `data/content/CourseContentJsonCodec.kt` | JSON 解析和校验 |
| `data/content/ContentUpdateManager.kt` | 内容更新 |
| `runtime/PythonRun.kt` | Python 运行和错误解释 |
| `runtime/AiTeacher.kt` | AI 接口调用 |
| `ui/PythonApp.kt` | 根导航和页面路由 |
| `ui/screens/CodeWorkbenchScreen.kt` | 高级代码编辑器 |
| `ui/screens/LearningHubScreen.kt` | 学习中心 |
| `ui/screens/V2ToolsScreens.kt` | 搜索、错误博物馆、AI 独立能力 |
| `assets/content/course_content.json` | 当前课程和项目内容 |
| `docs/content-update.md` | 内容更新接口 |
| `docs/release-signing.md` | Release 签名 |

---

## 32. 结论

本项目当前已经具备完整的学习闭环：

```text
学习课程
  ↓
运行代码
  ↓
完成练习
  ↓
专项训练
  ↓
记录错题
  ↓
间隔复习
  ↓
更新掌握度
  ↓
推荐下一步
  ↓
完成项目
  ↓
独立开发毕业项目
```

后续开发应优先保护这条闭环，避免为了增加页面而破坏数据一致性、学习独立性、内容可更新性和发布稳定性。
