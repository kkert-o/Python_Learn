# 课程内容更新接口

App 会优先读取以下位置的内容文件：

```text
files/content/course_content.json
```

如果文件不存在、JSON 无效或结构校验失败，会自动回退到 APK 内置资源：

```text
assets/content/course_content.json
```

## 清单格式

服务端先提供一个 HTTPS JSON 清单：

```json
{
  "version": 2,
  "updatedAt": "2026-09-15",
  "contentUrl": "https://example.com/content/course_content-v2.json",
  "sha256": "内容文件的 SHA-256 小写十六进制值",
  "minAppVersion": 1
}
```

字段规则：

- `version` 必须大于当前内容版本才会更新。
- `contentUrl` 和清单地址都必须使用 HTTPS。
- `sha256` 启用内容完整性校验。
- `minAppVersion` 高于当前安装版本时不会安装。

## 调用入口

`PythonLearningApplication.contentUpdateManager` 提供：

```kotlin
val check = contentUpdateManager.checkForUpdate(manifestUrl)
val result = contentUpdateManager.downloadAndInstall(manifestUrl)
val activeContent = contentUpdateManager.loadActiveContent()
```

检查结果和安装结果都是密封类型，正式 UI 接入时可以直接区分：

```text
UPDATE_AVAILABLE
UP_TO_DATE
INCOMPATIBLE
INVALID
NETWORK_ERROR
INSTALLED
FAILED
```

## 安装流程

```text
下载清单
↓
检查 App 最低版本
↓
比较内容版本
↓
下载内容
↓
SHA-256 校验
↓
JSON 解析和结构校验
↓
临时文件写入
↓
旧文件备份
↓
原子替换
↓
失败时保留旧版本或回退内置内容
```

更新内容不会修改 APK，重新启动 App 后继续读取已安装的新版本。

## 后台自动检查

默认不启用联网检查。发布构建时通过 Gradle 参数或环境变量配置清单地址：

```powershell
.\gradlew.bat :app:assembleRelease -PcontentManifestUrl="https://example.com/content/manifest.json"
```

也可以设置：

```text
CONTENT_MANIFEST_URL=https://example.com/content/manifest.json
```

启用后由 WorkManager 每 24 小时检查一次，要求网络可用；失败时使用指数退避，最多重试 3 次。
未配置地址时不会创建后台任务。
