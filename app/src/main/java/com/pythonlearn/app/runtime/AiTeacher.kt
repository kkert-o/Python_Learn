package com.pythonlearn.app.runtime

import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL

data class AiConfig(
    val endpoint: String = DEFAULT_ENDPOINT,
    val apiKey: String = "",
    val model: String = DEFAULT_MODEL,
) {
    companion object {
        const val DEFAULT_ENDPOINT = "https://api.deepseek.com/chat/completions"
        const val DEFAULT_MODEL = "deepseek-chat"
    }
}

object AiTeacherClient {
    fun ask(
        config: AiConfig,
        systemPrompt: String,
        history: List<Pair<String, String>>,
        userText: String,
    ): String {
        if (config.apiKey.isBlank()) {
            throw IllegalStateException("请先配置 API Key")
        }
        val connection = URL(config.endpoint.trim().ifEmpty { AiConfig.DEFAULT_ENDPOINT })
            .openConnection() as HttpURLConnection
        try {
            connection.requestMethod = "POST"
            connection.connectTimeout = 12_000
            connection.readTimeout = 25_000
            connection.doOutput = true
            connection.setRequestProperty("Content-Type", "application/json")
            connection.setRequestProperty("Authorization", "Bearer ${config.apiKey.trim()}")

            val messages = JSONArray().apply {
                put(JSONObject().put("role", "system").put("content", systemPrompt))
                history.forEach { (role, text) ->
                    put(JSONObject().put("role", role).put("content", text))
                }
                put(JSONObject().put("role", "user").put("content", userText))
            }
            val payload = JSONObject()
                .put("model", config.model.trim().ifEmpty { AiConfig.DEFAULT_MODEL })
                .put("messages", messages)
                .put("temperature", 0.3)

            connection.outputStream.use { output ->
                output.write(payload.toString().toByteArray(Charsets.UTF_8))
            }

            val code = connection.responseCode
            val raw = if (code in 200..299) {
                connection.inputStream.bufferedReader(Charsets.UTF_8).readText()
            } else {
                val errorText = connection.errorStream?.bufferedReader(Charsets.UTF_8)?.readText().orEmpty()
                throw IOException("HTTP $code ${errorText.take(300)}")
            }
            return parseReply(raw)
        } finally {
            connection.disconnect()
        }
    }

    private fun parseReply(raw: String): String {
        val json = JSONObject(raw)
        val content = json.optJSONArray("choices")
            ?.optJSONObject(0)
            ?.optJSONObject("message")
            ?.optString("content")
            ?.trim()
        if (content.isNullOrEmpty()) {
            throw IOException("接口没有返回可用内容")
        }
        return content
    }
}
