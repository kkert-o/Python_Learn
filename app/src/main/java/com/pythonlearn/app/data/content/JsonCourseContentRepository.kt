package com.pythonlearn.app.data.content

import android.content.Context
import com.google.gson.Gson

class JsonCourseContentRepository(
    private val context: Context,
    private val gson: Gson = Gson(),
) {
    fun load(): CourseContent {
        val json = context.assets
            .open(ASSET_PATH)
            .bufferedReader(Charsets.UTF_8)
            .use { it.readText() }
        return gson.fromJson(json, ContentPayloadDto::class.java).toDomain()
    }

    companion object {
        const val ASSET_PATH = "content/course_content.json"
    }
}
