package com.example.floatinggeminiai.ai

import com.example.floatinggeminiai.security.SecureVault
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.util.concurrent.TimeUnit

class AiEngine(private val vault: SecureVault) {

    private val client = OkHttpClient.Builder()
        .connectTimeout(25, TimeUnit.SECONDS)
        .readTimeout(90, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    fun resolveAutoRouter(prompt: String, hasVisualAttachment: Boolean): Pair<AiProvider, String> {
        val configured = AiProvider.entries.filter { vault.hasApiKey(it.id) }
        if (configured.isEmpty()) return Pair(AiProvider.GEMINI, AiProvider.GEMINI.models.first())

        val lower = prompt.lowercase()
        if (hasVisualAttachment) {
            val visionProv = configured.firstOrNull { it.supportsVision } ?: configured.first()
            return Pair(visionProv, visionProv.models.first())
        }
        if (lower.contains("terbaru") || lower.contains("berita") || lower.contains("hari ini") || lower.contains("harga")) {
            configured.find { it == AiProvider.PERPLEXITY }?.let { return Pair(it, it.models.first()) }
        }
        if (lower.contains("kode") || lower.contains("code") || lower.contains("bug") || lower.contains("kotlin") || lower.contains("python")) {
            configured.find { it == AiProvider.DEEPSEEK || it == AiProvider.CLAUDE }?.let {
                return Pair(it, it.models.first())
            }
        }
        configured.find { it == AiProvider.GROQ || it == AiProvider.GEMINI }?.let {
            return Pair(it, it.models.first())
        }
        val chosen = configured.first()
        val model = if (chosen == AiProvider.CUSTOM) vault.getCustomModelId() else chosen.models.first()
        return Pair(chosen, model)
    }

    suspend fun testConnection(provider: AiProvider, model: String): Result<String> = withContext(Dispatchers.IO) {
        val apiKey = vault.getApiKey(provider.id)
        if (apiKey.isEmpty()) {
            return@withContext Result.failure(IllegalStateException("API Key ${provider.displayName} masih kosong."))
        }
        val start = System.currentTimeMillis()
        var responseText = ""
        val result = streamChat(
            provider = provider,
            model = model,
            systemPrompt = "Jawab hanya dengan kata: OK terhubung.",
            history = listOf(ChatMessage(role = "user", content = "Tes koneksi")),
            imageBase64List = emptyList(),
            onChunk = { chunk -> responseText += chunk }
        )
        val latency = System.currentTimeMillis() - start
        result.map { "${provider.displayName} aktif (${latency}ms): ${responseText.trim().take(60)}" }
    }

    suspend fun streamChat(
        provider: AiProvider,
        model: String,
        systemPrompt: String,
        history: List<ChatMessage>,
        imageBase64List: List<String>,
        onChunk: suspend (String) -> Unit
    ): Result<String> = withContext(Dispatchers.IO) {
        val apiKey = vault.getApiKey(provider.id)
        if (apiKey.isEmpty()) {
            return@withContext Result.failure(
                IllegalStateException("API Key untuk ${provider.displayName} belum diisi. Silakan isi di tab AI & Keys.")
            )
        }

        var lastError: Throwable? = null
        for (attempt in 1..2) {
            try {
                val fullText = when (provider) {
                    AiProvider.GEMINI -> executeGeminiStream(apiKey, model, systemPrompt, history, imageBase64List, onChunk)
                    AiProvider.CLAUDE -> executeClaudeStream(apiKey, model, systemPrompt, history, imageBase64List, onChunk)
                    else -> executeOpenAiCompatibleStream(provider, apiKey, model, systemPrompt, history, imageBase64List, onChunk)
                }
                return@withContext Result.success(fullText)
            } catch (ce: CancellationException) {
                throw ce
            } catch (t: Throwable) {
                lastError = t
                if (attempt < 2) delay(700L)
            }
        }
        Result.failure(lastError ?: RuntimeException("Gagal menghubungi ${provider.displayName}"))
    }

    private suspend fun executeGeminiStream(
        apiKey: String,
        model: String,
        systemPrompt: String,
        history: List<ChatMessage>,
        imageBase64List: List<String>,
        onChunk: suspend (String) -> Unit
    ): String {
        val url = "${AiProvider.GEMINI.defaultBaseUrl}/models/$model:streamGenerateContent?alt=sse&key=$apiKey"
        val contentsArray = JSONArray()

        val recentHistory = history.takeLast(24)
        recentHistory.forEachIndexed { idx, msg ->
            val role = if (msg.role == "assistant") "model" else "user"
            val parts = JSONArray()
            parts.put(JSONObject().put("text", msg.content))
            if (idx == recentHistory.lastIndex && role == "user" && imageBase64List.isNotEmpty()) {
                for (b64 in imageBase64List) {
                    parts.put(
                        JSONObject().put(
                            "inlineData",
                            JSONObject()
                                .put("mimeType", "image/jpeg")
                                .put("data", b64)
                        )
                    )
                }
            }
            contentsArray.put(JSONObject().put("role", role).put("parts", parts))
        }

        val bodyJson = JSONObject().apply {
            put("systemInstruction", JSONObject().put("parts", JSONArray().put(JSONObject().put("text", systemPrompt))))
            put("contents", contentsArray)
            put("generationConfig", JSONObject().put("temperature", 0.75))
        }

        val request = Request.Builder()
            .url(url)
            .post(bodyJson.toString().toRequestBody("application/json; charset=utf-8".toMediaType()))
            .build()

        val sb = StringBuilder()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                val errBody = response.body?.string().orEmpty()
                throw RuntimeException("Gemini HTTP ${response.code}: ${extractErrorMessage(errBody)}")
            }
            val stream = response.body?.byteStream() ?: throw RuntimeException("Stream kosong")
            BufferedReader(InputStreamReader(stream)).use { reader ->
                var line: String?
                while (reader.readLine().also { line = it } != null) {
                    val trimmed = line?.trim().orEmpty()
                    if (trimmed.startsWith("data:")) {
                        val payload = trimmed.removePrefix("data:").trim()
                        if (payload == "[DONE]" || payload.isEmpty()) continue
                        try {
                            val json = JSONObject(payload)
                            val candidates = json.optJSONArray("candidates") ?: continue
                            if (candidates.length() > 0) {
                                val parts = candidates.getJSONObject(0)
                                    .optJSONObject("content")
                                    ?.optJSONArray("parts")
                                if (parts != null) {
                                    for (i in 0 until parts.length()) {
                                        val piece = parts.getJSONObject(i).optString("text", "")
                                        if (piece.isNotEmpty()) {
                                            sb.append(piece)
                                            onChunk(piece)
                                        }
                                    }
                                }
                            }
                        } catch (_: Exception) {
                        }
                    }
                }
            }
        }
        return sb.toString()
    }

    private suspend fun executeClaudeStream(
        apiKey: String,
        model: String,
        systemPrompt: String,
        history: List<ChatMessage>,
        imageBase64List: List<String>,
        onChunk: suspend (String) -> Unit
    ): String {
        val url = "${AiProvider.CLAUDE.defaultBaseUrl}/messages"
        val messagesArray = JSONArray()
        val recentHistory = history.takeLast(20)

        recentHistory.forEachIndexed { idx, msg ->
            val role = if (msg.role == "assistant") "assistant" else "user"
            if (idx == recentHistory.lastIndex && role == "user" && imageBase64List.isNotEmpty()) {
                val contentArr = JSONArray()
                for (b64 in imageBase64List) {
                    contentArr.put(
                        JSONObject()
                            .put("type", "image")
                            .put(
                                "source",
                                JSONObject()
                                    .put("type", "base64")
                                    .put("media_type", "image/jpeg")
                                    .put("data", b64)
                            )
                    )
                }
                contentArr.put(JSONObject().put("type", "text").put("text", msg.content))
                messagesArray.put(JSONObject().put("role", role).put("content", contentArr))
            } else {
                messagesArray.put(JSONObject().put("role", role).put("content", msg.content))
            }
        }

        val bodyJson = JSONObject().apply {
            put("model", model)
            put("max_tokens", 2048)
            put("system", systemPrompt)
            put("messages", messagesArray)
            put("stream", true)
        }

        val request = Request.Builder()
            .url(url)
            .addHeader("x-api-key", apiKey)
            .addHeader("anthropic-version", "2023-06-01")
            .post(bodyJson.toString().toRequestBody("application/json; charset=utf-8".toMediaType()))
            .build()

        val sb = StringBuilder()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                val errBody = response.body?.string().orEmpty()
                throw RuntimeException("Claude HTTP ${response.code}: ${extractErrorMessage(errBody)}")
            }
            val stream = response.body?.byteStream() ?: throw RuntimeException("Stream kosong")
            BufferedReader(InputStreamReader(stream)).use { reader ->
                var line: String?
                while (reader.readLine().also { line = it } != null) {
                    val trimmed = line?.trim().orEmpty()
                    if (trimmed.startsWith("data:")) {
                        val payload = trimmed.removePrefix("data:").trim()
                        if (payload.isEmpty() || payload == "[DONE]") continue
                        try {
                            val json = JSONObject(payload)
                            if (json.optString("type") == "content_block_delta") {
                                val text = json.optJSONObject("delta")?.optString("text", "").orEmpty()
                                if (text.isNotEmpty()) {
                                    sb.append(text)
                                    onChunk(text)
                                }
                            }
                        } catch (_: Exception) {
                        }
                    }
                }
            }
        }
        return sb.toString()
    }

    private suspend fun executeOpenAiCompatibleStream(
        provider: AiProvider,
        apiKey: String,
        model: String,
        systemPrompt: String,
        history: List<ChatMessage>,
        imageBase64List: List<String>,
        onChunk: suspend (String) -> Unit
    ): String {
        val baseUrl = if (provider == AiProvider.CUSTOM) {
            vault.getCustomBaseUrl().trimEnd('/')
        } else {
            provider.defaultBaseUrl.trimEnd('/')
        }
        val resolvedModel = if (provider == AiProvider.CUSTOM && model == "custom-model") {
            vault.getCustomModelId().ifEmpty { model }
        } else {
            model
        }

        val messagesArray = JSONArray()
        messagesArray.put(JSONObject().put("role", "system").put("content", systemPrompt))

        val recentHistory = history.takeLast(20)
        recentHistory.forEachIndexed { idx, msg ->
            val role = if (msg.role == "assistant") "assistant" else "user"
            if (idx == recentHistory.lastIndex && role == "user" && imageBase64List.isNotEmpty() && provider.supportsVision) {
                val contentParts = JSONArray()
                contentParts.put(JSONObject().put("type", "text").put("text", msg.content))
                for (b64 in imageBase64List) {
                    contentParts.put(
                        JSONObject()
                            .put("type", "image_url")
                            .put("image_url", JSONObject().put("url", "data:image/jpeg;base64,$b64"))
                    )
                }
                messagesArray.put(JSONObject().put("role", role).put("content", contentParts))
            } else {
                messagesArray.put(JSONObject().put("role", role).put("content", msg.content))
            }
        }

        val bodyJson = JSONObject().apply {
            put("model", resolvedModel)
            put("messages", messagesArray)
            put("stream", true)
        }

        val reqBuilder = Request.Builder()
            .url("$baseUrl/chat/completions")
            .addHeader("Authorization", "Bearer $apiKey")
            .post(bodyJson.toString().toRequestBody("application/json; charset=utf-8".toMediaType()))

        if (provider == AiProvider.OPENROUTER) {
            reqBuilder.addHeader("HTTP-Referer", "https://github.com/AvoluProject/FloatingGeminiAI")
            reqBuilder.addHeader("X-Title", "Floamini OS")
        }

        val sb = StringBuilder()
        client.newCall(reqBuilder.build()).execute().use { response ->
            if (!response.isSuccessful) {
                val errBody = response.body?.string().orEmpty()
                throw RuntimeException("${provider.displayName} HTTP ${response.code}: ${extractErrorMessage(errBody)}")
            }
            val stream = response.body?.byteStream() ?: throw RuntimeException("Stream kosong")
            BufferedReader(InputStreamReader(stream)).use { reader ->
                var line: String?
                while (reader.readLine().also { line = it } != null) {
                    val trimmed = line?.trim().orEmpty()
                    if (trimmed.startsWith("data:")) {
                        val payload = trimmed.removePrefix("data:").trim()
                        if (payload == "[DONE]" || payload.isEmpty()) continue
                        try {
                            val json = JSONObject(payload)
                            val choices = json.optJSONArray("choices") ?: continue
                            if (choices.length() > 0) {
                                val delta = choices.getJSONObject(0).optJSONObject("delta")
                                val content = delta?.optString("content", "").orEmpty()
                                if (content.isNotEmpty()) {
                                    sb.append(content)
                                    onChunk(content)
                                }
                            }
                        } catch (_: Exception) {
                        }
                    }
                }
            }
        }
        return sb.toString()
    }

    private fun extractErrorMessage(raw: String): String {
        return try {
            val obj = JSONObject(raw)
            obj.optJSONObject("error")?.optString("message")
                ?: obj.optString("message")
                ?: raw.take(120)
        } catch (_: Exception) {
            raw.take(120)
        }
    }
}
