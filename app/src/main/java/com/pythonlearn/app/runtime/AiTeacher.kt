package com.pythonlearn.app.runtime

import com.google.gson.Gson
import com.google.gson.JsonParser
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
    private val gson = Gson()

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

            val messages = buildList {
                add(mapOf("role" to "system", "content" to systemPrompt))
                history.forEach { (role, text) ->
                    add(mapOf("role" to normalizeRole(role), "content" to text))
                }
                add(mapOf("role" to "user", "content" to userText))
            }
            val payload = mapOf(
                "model" to config.model.trim().ifEmpty { AiConfig.DEFAULT_MODEL },
                "messages" to messages,
                "temperature" to 0.3,
            )

            connection.outputStream.use { output ->
                output.write(gson.toJson(payload).toByteArray(Charsets.UTF_8))
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
        val content = JsonParser.parseString(raw)
            .asJsonObject
            .getAsJsonArray("choices")
            .firstOrNull()
            ?.asJsonObject
            ?.getAsJsonObject("message")
            ?.get("content")
            ?.asString
            ?.trim()
        if (content.isNullOrEmpty()) {
            throw IOException("接口没有返回可用内容")
        }
        return content
    }

    internal fun normalizeRole(role: String): String {
        return when (role.trim().lowercase()) {
            "assistant", "bot" -> "assistant"
            "system" -> "system"
            "tool" -> "tool"
            else -> "user"
        }
    }
}
