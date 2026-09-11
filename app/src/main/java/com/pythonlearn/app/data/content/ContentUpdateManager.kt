package com.pythonlearn.app.data.content

import com.google.gson.Gson
import com.google.gson.JsonSyntaxException
import java.io.File
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

data class ContentManifestDto(
    val version: Int,
    val updatedAt: String,
    val contentUrl: String,
    val sha256: String = "",
    val minAppVersion: Int = 0,
)

sealed interface ContentUpdateCheck {
    data class UpdateAvailable(
        val manifest: ContentManifestDto,
        val manifestUrl: String,
    ) : ContentUpdateCheck

    data class UpToDate(val version: Int) : ContentUpdateCheck

    data class Incompatible(
        val manifest: ContentManifestDto,
        val manifestUrl: String,
    ) : ContentUpdateCheck

    data class Invalid(val message: String) : ContentUpdateCheck

    data class NetworkError(val message: String) : ContentUpdateCheck
}

sealed interface ContentInstallResult {
    data class Installed(
        val version: Int,
        val path: String,
    ) : ContentInstallResult

    data class UpToDate(val version: Int) : ContentInstallResult

    data class Failed(val message: String) : ContentInstallResult
}

fun interface ContentDownloader {
    fun download(url: String): String
}

class HttpContentDownloader(
    private val connectTimeoutMillis: Int = 12_000,
    private val readTimeoutMillis: Int = 25_000,
) : ContentDownloader {
    override fun download(url: String): String {
        require(url.startsWith("https://")) { "内容更新必须使用 HTTPS" }
        val connection = URL(url).openConnection() as HttpURLConnection
        return try {
            connection.requestMethod = "GET"
            connection.connectTimeout = connectTimeoutMillis
            connection.readTimeout = readTimeoutMillis
            connection.setRequestProperty("Accept", "application/json, text/plain")
            val responseCode = connection.responseCode
            val stream = if (responseCode in 200..299) {
                connection.inputStream
            } else {
                connection.errorStream
            }
            val bytes = stream?.use { input ->
                input.readBytes()
            } ?: ByteArray(0)
            if (responseCode !in 200..299) {
                throw IOException("HTTP $responseCode: ${bytes.toString(Charsets.UTF_8).take(300)}")
            }
            if (bytes.size > MAX_RESPONSE_BYTES) {
                throw IOException("内容文件超过允许大小")
            }
            bytes.toString(Charsets.UTF_8)
        } finally {
            connection.disconnect()
        }
    }

    private companion object {
        const val MAX_RESPONSE_BYTES = 5 * 1024 * 1024
    }
}

class ContentUpdateManager(
    private val installedFile: File,
    private val bundledContent: () -> CourseContent,
    private val downloader: ContentDownloader,
    private val appVersionCode: Int,
    private val gson: Gson = Gson(),
) {
    fun loadActiveContent(): CourseContent {
        val bundled = bundledContent()
        val installed = readAndValidate(installedFile)
        return when {
            installed == null -> bundled
            installed.version > bundled.version -> installed
            else -> bundled
        }
    }

    fun checkForUpdate(manifestUrl: String): ContentUpdateCheck {
        if (!manifestUrl.startsWith("https://")) {
            return ContentUpdateCheck.Invalid("内容清单地址必须使用 HTTPS")
        }
        val json = try {
            downloader.download(manifestUrl)
        } catch (error: Throwable) {
            return ContentUpdateCheck.NetworkError(error.message ?: "无法下载内容清单")
        }
        val manifest = try {
            parseManifest(json)
        } catch (error: Throwable) {
            return ContentUpdateCheck.Invalid(error.message ?: "内容清单无法解析")
        }
        validateManifest(manifest)?.let { message ->
            return ContentUpdateCheck.Invalid(message)
        }
        if (manifest.minAppVersion > appVersionCode) {
            return ContentUpdateCheck.Incompatible(
                manifest = manifest,
                manifestUrl = manifestUrl,
            )
        }
        val currentVersion = loadActiveContent().version
        return if (manifest.version <= currentVersion) {
            ContentUpdateCheck.UpToDate(currentVersion)
        } else {
            ContentUpdateCheck.UpdateAvailable(
                manifest = manifest,
                manifestUrl = manifestUrl,
            )
        }
    }

    fun downloadAndInstall(manifestUrl: String): ContentInstallResult {
        return when (val check = checkForUpdate(manifestUrl)) {
            is ContentUpdateCheck.UpToDate -> ContentInstallResult.UpToDate(check.version)
            is ContentUpdateCheck.Incompatible -> {
                ContentInstallResult.Failed("新内容要求 App 版本至少为 ${check.manifest.minAppVersion}")
            }
            is ContentUpdateCheck.Invalid -> ContentInstallResult.Failed(check.message)
            is ContentUpdateCheck.NetworkError -> ContentInstallResult.Failed(check.message)
            is ContentUpdateCheck.UpdateAvailable -> {
                installCheckedManifest(check)
            }
        }
    }

    private fun installCheckedManifest(
        check: ContentUpdateCheck.UpdateAvailable,
    ): ContentInstallResult {
        val manifest = check.manifest
        val rawContent = try {
            downloader.download(manifest.contentUrl)
        } catch (error: Throwable) {
            return ContentInstallResult.Failed(error.message ?: "无法下载课程内容")
        }
        if (manifest.sha256.isNotBlank()) {
            val actualHash = rawContent.toByteArray(Charsets.UTF_8).sha256()
            if (!actualHash.equals(manifest.sha256.trim(), ignoreCase = true)) {
                return ContentInstallResult.Failed("课程内容校验失败")
            }
        }
        val content = try {
            CourseContentJsonCodec.decode(rawContent, gson)
        } catch (error: Throwable) {
            return ContentInstallResult.Failed(error.message ?: "课程内容无法解析")
        }
        val validationErrors = CourseContentValidator.validate(content)
        if (validationErrors.isNotEmpty()) {
            return ContentInstallResult.Failed(validationErrors.joinToString("；"))
        }
        if (content.version != manifest.version) {
            return ContentInstallResult.Failed("清单版本与内容版本不一致")
        }

        return try {
            writeAtomically(rawContent)
            ContentInstallResult.Installed(
                version = content.version,
                path = installedFile.absolutePath,
            )
        } catch (error: Throwable) {
            ContentInstallResult.Failed(error.message ?: "保存课程内容失败")
        }
    }

    private fun readAndValidate(file: File): CourseContent? {
        if (!file.isFile) return null
        return runCatching {
            val content = CourseContentJsonCodec.decode(file.readText(Charsets.UTF_8), gson)
            if (CourseContentValidator.validate(content).isEmpty()) content else null
        }.getOrNull()
    }

    private fun parseManifest(json: String): ContentManifestDto {
        return try {
            gson.fromJson(json, ContentManifestDto::class.java)
                ?: throw IllegalArgumentException("内容清单为空")
        } catch (error: JsonSyntaxException) {
            throw IllegalArgumentException("内容清单不是有效的 JSON", error)
        }
    }

    private fun validateManifest(manifest: ContentManifestDto): String? {
        return when {
            manifest.version <= 0 -> "内容版本必须大于 0"
            manifest.updatedAt.isBlank() -> "内容清单缺少更新时间"
            !manifest.contentUrl.startsWith("https://") -> "内容地址必须使用 HTTPS"
            manifest.minAppVersion < 0 -> "最低 App 版本不能小于 0"
            else -> null
        }
    }

    private fun writeAtomically(content: String) {
        val parent = installedFile.parentFile
            ?: throw IOException("无法创建内容目录")
        if (!parent.exists() && !parent.mkdirs()) {
            throw IOException("无法创建内容目录")
        }
        val temporary = File(parent, "${installedFile.name}.download")
        val backup = File(parent, "${installedFile.name}.backup")
        temporary.writeText(content, Charsets.UTF_8)
        if (backup.exists() && !backup.delete()) {
            temporary.delete()
            throw IOException("无法清理旧的内容备份")
        }
        if (installedFile.exists() && !installedFile.renameTo(backup)) {
            temporary.delete()
            throw IOException("无法备份旧内容")
        }
        if (!temporary.renameTo(installedFile)) {
            if (backup.exists()) {
                backup.renameTo(installedFile)
            }
            temporary.delete()
            throw IOException("无法启用新内容")
        }
        backup.delete()
    }

    private fun ByteArray.sha256(): String {
        return MessageDigest.getInstance("SHA-256")
            .digest(this)
            .joinToString("") { byte -> "%02x".format(byte) }
    }
}
