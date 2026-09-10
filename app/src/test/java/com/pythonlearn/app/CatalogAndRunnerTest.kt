package com.pythonlearn.app

import com.pythonlearn.app.data.CourseCatalog
import com.pythonlearn.app.data.DemoStats
import com.pythonlearn.app.data.KnowledgeState
import com.pythonlearn.app.data.KnowledgeTreeEngine
import com.pythonlearn.app.data.LessonState
import com.pythonlearn.app.data.ReviewScheduler
import com.pythonlearn.app.data.TrainingCatalog
import com.pythonlearn.app.data.TrainingGrader
import com.pythonlearn.app.data.TrainingType
import com.pythonlearn.app.data.local.LearningEventEntity
import com.pythonlearn.app.data.local.LessonProgressEntity
import com.pythonlearn.app.data.local.ProgressDao
import com.pythonlearn.app.data.local.ProjectProgressEntity
import com.pythonlearn.app.data.local.QuizProgressEntity
import com.pythonlearn.app.data.local.ReviewScheduleEntity
import com.pythonlearn.app.data.local.TrainingProgressEntity
import com.pythonlearn.app.data.repository.ProgressRepository
import com.pythonlearn.app.runtime.PythonErrorExplainer
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
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

    @Test
    fun trainingCatalogCoversEveryV2TrainingMode() {
        TrainingType.entries.forEach { type ->
            assertTrue("缺少 $type 训练题", TrainingCatalog.byType(type).isNotEmpty())
        }
        TrainingCatalog.all.forEach { exercise ->
            assertTrue("训练题 id 不应为空", exercise.id.isNotBlank())
            assertTrue("训练题必须有题目说明", exercise.question.isNotBlank())
            assertTrue("训练题必须有解析", exercise.explanation.isNotBlank())
            if (exercise.isCodeTask) {
                assertNotNull("代码训练必须提供起始代码", exercise.starterCode)
                assertNotNull("代码训练必须提供参考实现", exercise.referenceSolution)
                assertTrue("代码训练必须提供检查规则", exercise.requiredSnippets.isNotEmpty())
            } else {
                assertTrue("选择题必须有选项", exercise.options.size >= 2)
                assertTrue("选择题答案下标越界", exercise.answerIndex in exercise.options.indices)
            }
        }
    }

    @Test
    fun referenceSolutionsPassCodeTraining() {
        TrainingCatalog.all
            .filter { it.isCodeTask }
            .forEach { exercise ->
                val result = TrainingGrader.checkCode(exercise, exercise.referenceSolution!!)
                assertTrue("${exercise.id} 的参考实现没有通过检查：${result.message}", result.correct)
            }
    }

    @Test
    fun debugTrainingRejectsKnownWrongSnippet() {
        val exercise = TrainingCatalog.byId("debug-name")
        assertNotNull(exercise)
        val result = TrainingGrader.checkCode(exercise!!, exercise.starterCode!!)
        assertFalse("未修改的错误代码不应通过", result.correct)
        assertTrue(result.message.contains("错误写法"))
    }

    @Test
    fun trainingProgressMovesFromWrongToCompleted() = runBlocking {
        val dao = FakeProgressDao()
        val repository = ProgressRepository(dao, now = { 100L })

        repository.recordTrainingResult("train-1", correct = false)
        val afterWrong = repository.observeProgress().first()
        assertTrue("train-1" in afterWrong.wrongTrainingIds)
        assertFalse("train-1" in afterWrong.completedTrainingIds)

        repository.recordTrainingResult("train-1", correct = true)
        val afterCorrect = repository.observeProgress().first()
        assertTrue("train-1" in afterCorrect.completedTrainingIds)
        assertFalse("train-1" in afterCorrect.wrongTrainingIds)
    }

    @Test
    fun legacyProgressMigratesIntoRoomSnapshot() = runBlocking {
        val dao = FakeProgressDao()
        val repository = ProgressRepository(dao, now = { 200L })

        repository.migrateLegacyProgress(
            completedLessonIds = setOf("python"),
            completedProjectIds = setOf("calculator"),
            completedTrainingIds = setOf("predict-add"),
            wrongTrainingIds = setOf("debug-name"),
            wrongQuizIds = setOf("旧错题"),
        )

        val snapshot = repository.observeProgress().first()
        assertEquals(setOf("python"), snapshot.completedLessonIds)
        assertEquals(setOf("calculator"), snapshot.completedProjectIds)
        assertEquals(setOf("predict-add"), snapshot.completedTrainingIds)
        assertEquals(setOf("debug-name"), snapshot.wrongTrainingIds)
        assertEquals(setOf("旧错题"), snapshot.wrongQuizIds)
    }

    @Test
    fun reviewScheduleMovesForwardAfterCorrectAnswer() = runBlocking {
        val dao = FakeProgressDao()
        val repository = ProgressRepository(dao, now = { 0L })

        repository.recordTrainingResult("predict-add", correct = false)
        val firstReview = dao.reviewSchedule(ReviewScheduler.trainingKey("predict-add"))
        assertNotNull(firstReview)
        assertEquals(0, firstReview?.reviewStage)

        repository.recordTrainingResult("predict-add", correct = true)
        val secondReview = dao.reviewSchedule(ReviewScheduler.trainingKey("predict-add"))
        assertNotNull(secondReview)
        assertEquals(1, secondReview?.reviewStage)
    }

    @Test
    fun completedLessonWithQuizCanReachMasteredState() {
        val lesson = CourseCatalog.lesson("python")!!
        val nodes = KnowledgeTreeEngine.build(
            completedLessonIds = setOf(lesson.id),
            trainingProgress = emptyList(),
            quizProgress = listOf(
                QuizProgressEntity(
                    question = lesson.quiz.question,
                    resolved = true,
                    correctCount = 1,
                    wrongCount = 0,
                    updatedAt = 10L,
                ),
            ),
            reviewSchedules = emptyList(),
            now = 20L,
        )
        assertEquals(KnowledgeState.MASTERED, nodes.first().state)
        assertTrue(nodes.first().masteryScore >= 80)
    }
}

private class FakeProgressDao : ProgressDao {
    private val lessons = MutableStateFlow<List<LessonProgressEntity>>(emptyList())
    private val projects = MutableStateFlow<List<ProjectProgressEntity>>(emptyList())
    private val training = MutableStateFlow<List<TrainingProgressEntity>>(emptyList())
    private val quizzes = MutableStateFlow<List<QuizProgressEntity>>(emptyList())
    private val reviewSchedules = MutableStateFlow<List<ReviewScheduleEntity>>(emptyList())
    private val learningEvents = MutableStateFlow<List<LearningEventEntity>>(emptyList())

    override fun observeLessons(): Flow<List<LessonProgressEntity>> = lessons

    override fun observeProjects(): Flow<List<ProjectProgressEntity>> = projects

    override fun observeTraining(): Flow<List<TrainingProgressEntity>> = training

    override fun observeQuizzes(): Flow<List<QuizProgressEntity>> = quizzes

    override fun observeReviewSchedules(): Flow<List<ReviewScheduleEntity>> = reviewSchedules

    override fun observeLearningEvents(): Flow<List<LearningEventEntity>> = learningEvents

    override suspend fun lesson(lessonId: String): LessonProgressEntity? {
        return lessons.value.firstOrNull { it.lessonId == lessonId }
    }

    override suspend fun project(projectId: String): ProjectProgressEntity? {
        return projects.value.firstOrNull { it.projectId == projectId }
    }

    override suspend fun training(exerciseId: String): TrainingProgressEntity? {
        return training.value.firstOrNull { it.exerciseId == exerciseId }
    }

    override suspend fun quiz(question: String): QuizProgressEntity? {
        return quizzes.value.firstOrNull { it.question == question }
    }

    override suspend fun reviewSchedule(targetKey: String): ReviewScheduleEntity? {
        return reviewSchedules.value.firstOrNull { it.targetKey == targetKey }
    }

    override suspend fun upsertReviewSchedule(progress: ReviewScheduleEntity) {
        reviewSchedules.value = reviewSchedules.value.filterNot { it.targetKey == progress.targetKey } + progress
    }

    override suspend fun insertLearningEvent(event: LearningEventEntity) {
        learningEvents.value = learningEvents.value + event
    }

    override suspend fun upsertLesson(progress: LessonProgressEntity) {
        lessons.value = lessons.value.filterNot { it.lessonId == progress.lessonId } + progress
    }

    override suspend fun upsertProject(progress: ProjectProgressEntity) {
        projects.value = projects.value.filterNot { it.projectId == progress.projectId } + progress
    }

    override suspend fun upsertTraining(progress: TrainingProgressEntity) {
        training.value = training.value.filterNot { it.exerciseId == progress.exerciseId } + progress
    }

    override suspend fun upsertQuiz(progress: QuizProgressEntity) {
        quizzes.value = quizzes.value.filterNot { it.question == progress.question } + progress
    }
}
