package com.pythonlearn.app

import com.pythonlearn.app.data.CourseCatalog
import com.pythonlearn.app.data.DemoStats
import com.pythonlearn.app.data.LessonState
import com.pythonlearn.app.runtime.PythonErrorExplainer
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class CatalogAndRunnerTest {

    @Test
    fun freshUserHasNoProgress() {
        CourseCatalog.stages.forEach { stage ->
            assertEquals(0, stage.progress)
            stage.lessons.forEach { lesson ->
                assertFalse("新用户不应有已完成课程", lesson.state == LessonState.DONE)
                assertFalse("新用户不应有进行中课程", lesson.state == LessonState.DOING)
            }
        }
        assertEquals(0, DemoStats.learningDays)
        assertEquals(0, DemoStats.finishedCourses)
        assertEquals(0, DemoStats.finishedPractice)
    }

    @Test
    fun everyPublishedLessonHasDetail() {
        CourseCatalog.stages.forEach { stage ->
            stage.lessons.forEach { lesson ->
                assertTrue("${lesson.id} 缺少课程详情", CourseCatalog.lesson(lesson.id) != null)
            }
        }
        assertEquals(CourseCatalog.stages.sumOf { it.lessons.size }, CourseCatalog.allQuizzes.size)
    }

    @Test
    fun quizCanBeFoundByQuestion() {
        val question = CourseCatalog.lesson("list")?.quiz?.question
        assertTrue(question != null)
        assertEquals(CourseCatalog.lesson("list")?.quiz?.answerIndex, CourseCatalog.quizByQuestion(question!!)?.answerIndex)
    }

    @Test
    fun firstLessonIsAvailableForFreshUser() {
        val python = CourseCatalog.lesson("python")
        assertTrue(python != null)
        assertEquals("python", python?.id)
        assertEquals(LessonState.TODO, CourseCatalog.lessonState("python", emptySet()))
        assertEquals(LessonState.LOCKED, CourseCatalog.lessonState("hello", emptySet()))
    }

    @Test
    fun completingLessonUnlocksNextLesson() {
        val completed = setOf("python")
        assertEquals(LessonState.DONE, CourseCatalog.lessonState("python", completed))
        assertEquals(LessonState.TODO, CourseCatalog.lessonState("hello", completed))
        assertTrue(CourseCatalog.overallProgress(completed) > 0)
    }

    @Test
    fun finishingBasicsUnlocksConditionalLesson() {
        val completed = setOf("python", "hello", "print", "input", "variable", "types")
        assertEquals(LessonState.TODO, CourseCatalog.lessonState("if", completed))
        assertEquals("if", CourseCatalog.nextLessonId(completed))
    }

    @Test
    fun unknownLessonStaysLocked() {
        assertEquals(LessonState.LOCKED, CourseCatalog.lessonState("not-a-course", emptySet()))
    }

    @Test
    fun errorExplainerGivesFriendlyNameHint() {
        val hint = PythonErrorExplainer.explain(
            errorType = "NameError",
            message = "name 'socre' is not defined",
            traceback = "  File \"<user_code>\", line 3, in <module>\nNameError: name 'socre' is not defined",
        )
        assertTrue(hint.contains("socre"))
    }

    @Test
    fun errorExplainerPointsToLine() {
        val hint = PythonErrorExplainer.explain(
            errorType = "IndentationError",
            message = "unexpected indent",
            traceback = "  File \"<user_code>\", line 2, in <module>\nIndentationError: unexpected indent",
        )
        assertTrue(hint.contains("第 2 行"))
    }
}
