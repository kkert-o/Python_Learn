package com.pythonlearn.app

import com.google.gson.Gson
import com.pythonlearn.app.data.content.ContentDownloader
import com.pythonlearn.app.data.content.ContentInstallResult
import com.pythonlearn.app.data.content.ContentManifestDto
import com.pythonlearn.app.data.content.ContentPayloadDto
import com.pythonlearn.app.data.content.ContentUpdateCheck
import com.pythonlearn.app.data.content.ContentUpdateManager
import com.pythonlearn.app.data.content.CourseContentJsonCodec
import com.pythonlearn.app.data.content.CourseContentValidator
import java.io.File
import java.nio.file.Files
import java.security.MessageDigest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ContentUpdateManagerTest {
    private val gson = Gson()

    @Test
    fun missingInstalledFileUsesBundledContent() {
        val directory = Files.createTempDirectory("content-manager").toFile()
        val bundled = bundledContent()
        val manager = manager(directory, bundled, ContentDownloader { error("不应发起下载") })

        assertEquals(1, manager.loadActiveContent().version)
    }

    @Test
    fun validUpdateIsInstalledAndBecomesActive() {
        val directory = Files.createTempDirectory("content-manager").toFile()
        val bundled = bundledContent()
        val updatedJson = contentJson(version = 2)
        val manifestJson = manifestJson(
            version = 2,
            contentUrl = CONTENT_URL,
            sha256 = updatedJson.sha256(),
            minAppVersion = 1,
        )
        val downloader = ContentDownloader { url ->
            when (url) {
                MANIFEST_URL -> manifestJson
                CONTENT_URL -> updatedJson
                else -> error("Unexpected URL: $url")
            }
        }
        val installedFile = File(directory, "content/course_content.json")
        val manager = manager(directory, bundled, downloader)

        val check = manager.checkForUpdate(MANIFEST_URL)
        assertTrue(check is ContentUpdateCheck.UpdateAvailable)
        val result = manager.downloadAndInstall(MANIFEST_URL)
        assertTrue(result is ContentInstallResult.Installed)
        assertEquals(2, manager.loadActiveContent().version)
        assertTrue(installedFile.isFile)
    }

    @Test
    fun checksumFailureKeepsBundledContent() {
        val directory = Files.createTempDirectory("content-manager").toFile()
        val bundled = bundledContent()
        val updatedJson = contentJson(version = 2)
        val manifestJson = manifestJson(
            version = 2,
            contentUrl = CONTENT_URL,
            sha256 = "bad-hash",
            minAppVersion = 1,
        )
        val downloader = ContentDownloader { url ->
            when (url) {
                MANIFEST_URL -> manifestJson
                CONTENT_URL -> updatedJson
                else -> error("Unexpected URL: $url")
            }
        }
        val manager = manager(directory, bundled, downloader)

        val result = manager.downloadAndInstall(MANIFEST_URL)
        assertTrue(result is ContentInstallResult.Failed)
        assertEquals(1, manager.loadActiveContent().version)
    }

    @Test
    fun incompatibleManifestIsRejectedBeforeDownload() {
        val directory = Files.createTempDirectory("content-manager").toFile()
        val bundled = bundledContent()
        val manifestJson = manifestJson(
            version = 2,
            contentUrl = CONTENT_URL,
            sha256 = "",
            minAppVersion = 99,
        )
        val manager = manager(
            directory = directory,
            bundled = bundled,
            downloader = ContentDownloader { url ->
                if (url == MANIFEST_URL) manifestJson else error("不应下载内容")
            },
        )

        assertTrue(manager.checkForUpdate(MANIFEST_URL) is ContentUpdateCheck.Incompatible)
    }

    @Test
    fun malformedManifestIsRejectedAsInvalid() {
        val directory = Files.createTempDirectory("content-manager").toFile()
        val manager = manager(
            directory = directory,
            bundled = bundledContent(),
            downloader = ContentDownloader { "{ not-json" },
        )

        assertTrue(manager.checkForUpdate(MANIFEST_URL) is ContentUpdateCheck.Invalid)
    }

    @Test
    fun validatorRejectsCourseWithoutLessonDetails() {
        val payload = ContentPayloadDto.from(
            version = 1,
            updatedAt = "2026-09-10",
            stages = bundledContent().stages,
            lessons = emptyMap(),
            projects = bundledContent().projects,
        )
        val errors = CourseContentValidator.validate(payload.toDomain())

        assertTrue(errors.any { it.contains("缺少详情") || it.contains("不能为空") })
    }

    private fun manager(
        directory: File,
        bundled: com.pythonlearn.app.data.content.CourseContent,
        downloader: ContentDownloader,
    ): ContentUpdateManager {
        return ContentUpdateManager(
            installedFile = File(directory, "content/course_content.json"),
            bundledContent = { bundled },
            downloader = downloader,
            appVersionCode = 1,
            gson = gson,
        )
    }

    private fun bundledContent(): com.pythonlearn.app.data.content.CourseContent {
        val json = File("src/main/assets/content/course_content.json").readText(Charsets.UTF_8)
        return CourseContentJsonCodec.decode(json, gson)
    }

    private fun contentJson(version: Int): String {
        val content = bundledContent()
        return gson.toJson(
            ContentPayloadDto.from(
                version = version,
                updatedAt = "2026-09-11",
                stages = content.stages,
                lessons = content.lessons,
                projects = content.projects,
            ),
        )
    }

    private fun manifestJson(
        version: Int,
        contentUrl: String,
        sha256: String,
        minAppVersion: Int,
    ): String {
        return gson.toJson(
            ContentManifestDto(
                version = version,
                updatedAt = "2026-09-11",
                contentUrl = contentUrl,
                sha256 = sha256,
                minAppVersion = minAppVersion,
            ),
        )
    }

    private fun String.sha256(): String {
        return MessageDigest.getInstance("SHA-256")
            .digest(toByteArray(Charsets.UTF_8))
            .joinToString("") { byte -> "%02x".format(byte) }
    }

    private companion object {
        const val MANIFEST_URL = "https://example.com/content/manifest.json"
        const val CONTENT_URL = "https://example.com/content/course_content.json"
    }
}
