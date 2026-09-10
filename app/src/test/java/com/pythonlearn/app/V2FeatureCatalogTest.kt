package com.pythonlearn.app

import com.pythonlearn.app.data.AiIndependenceCatalog
import com.pythonlearn.app.data.AiIndependenceEngine
import com.pythonlearn.app.data.EngineeringCatalog
import com.pythonlearn.app.data.ErrorMuseumCatalog
import com.pythonlearn.app.data.GlobalSearchEngine
import com.pythonlearn.app.data.LibraryCatalog
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class V2FeatureCatalogTest {
    @Test
    fun libraryCatalogCoversRequiredEcosystems() {
        val categories = LibraryCatalog.all.map { it.category }.toSet()

        assertEquals(com.pythonlearn.app.data.LibraryCategory.entries.toSet(), categories)
        LibraryCatalog.all.forEach { entry ->
            assertTrue("${entry.id} 缺少安装方式", entry.install.isNotBlank())
            assertTrue("${entry.id} 缺少示例", entry.example.isNotBlank())
        }
        val bundled = LibraryCatalog.all.filter { it.runtimeAvailable }
        assertTrue("APK 内置库数量不足", bundled.size >= 12)
        assertFalse(bundled.any { it.id == "ruff" || it.id == "scikit-learn" })
    }

    @Test
    fun errorMuseumContainsExecutableFixForEveryEntry() {
        ErrorMuseumCatalog.all.forEach { entry ->
            assertTrue("${entry.id} 缺少错误代码", entry.brokenCode.isNotBlank())
            assertTrue("${entry.id} 缺少修复代码", entry.fixedCode.isNotBlank())
            assertFalse("${entry.id} 的修复代码不应与错误代码相同", entry.brokenCode == entry.fixedCode)
        }
    }

    @Test
    fun globalSearchFindsCrossModuleContent() {
        assertTrue(GlobalSearchEngine.search("pandas").any { it.title.contains("pandas") })
        assertTrue(GlobalSearchEngine.search("NameError").any { it.title.contains("变量名") })
        assertTrue(GlobalSearchEngine.search("Git").any { it.title.contains("Git") })
        assertTrue(GlobalSearchEngine.search("FastAPI").any { it.title.contains("FastAPI") })
    }

    @Test
    fun engineeringCatalogCoversGitQualityAndTests() {
        assertEquals(
            setOf(
                com.pythonlearn.app.data.EngineeringCategory.GIT,
                com.pythonlearn.app.data.EngineeringCategory.QUALITY,
                com.pythonlearn.app.data.EngineeringCategory.TESTING,
            ),
            EngineeringCatalog.all.map { it.category }.toSet(),
        )
    }

    @Test
    fun aiIndependenceProfileRewardsPracticeAndReportsDependency() {
        val independent = AiIndependenceEngine.build(
            completedLessons = 20,
            completedProjects = 3,
            completedTraining = 10,
            aiPromptCount = 0,
            aiFreeCompletedIds = setOf("ai-free-debug", "ai-free-function"),
        )
        val dependent = AiIndependenceEngine.build(
            completedLessons = 1,
            completedProjects = 0,
            completedTraining = 0,
            aiPromptCount = 20,
            aiFreeCompletedIds = emptySet(),
        )

        assertTrue(independent.experience > dependent.experience)
        assertEquals(0, independent.dependencyIndex)
        assertTrue(dependent.dependencyIndex > 80)
        assertEquals(AiIndependenceCatalog.challenges.size, independent.aiFreeTotal)
    }
}
