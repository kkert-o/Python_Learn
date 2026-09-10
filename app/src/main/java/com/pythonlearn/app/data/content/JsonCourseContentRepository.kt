package com.pythonlearn.app.data.content

import android.content.Context
class JsonCourseContentRepository(
    private val context: Context,
) {
    fun load(): CourseContent {
        val json = context.assets
            .open(ASSET_PATH)
            .bufferedReader(Charsets.UTF_8)
            .use { it.readText() }
        return CourseContentJsonCodec.decode(json)
    }

    companion object {
        const val ASSET_PATH = "content/course_content.json"
    }
}
