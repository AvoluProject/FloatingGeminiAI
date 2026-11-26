package com.example.floatinggeminiai.ai

import com.example.floatinggeminiai.security.SecureVault
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.isActive
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

interface AiProviderAdapter {
    fun streamChat(payload: AiRequestPayload): Flow<StreamEvent>
    suspend fun testConnection(apiKey: String, model: String, customBaseUrl: String = ""): Pair<Boolean, String>
}

object AiEngineRegistry {

    private fun buildClient(timeoutSec: Long): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(timeoutSec.coerceAtLeast(15L), TimeUnit.SECONDS)
            .readTimeout(timeoutSec.coerceAtLeast(30L), TimeUnit.SECONDS)
            .writeTimeout(25L, TimeUnit.SECONDS)
            .build()
    }

    fun getAdapter(provider: AiProviderType): AiProviderAdapter {
        return when (provider) {
            AiProviderType.GEMINI -> GeminiAdapter(::buildClient)
            AiProviderType.CLAUDE -> ClaudeAdapter(::buildClient)
            else -> OpenAiCompatibleAdapter(provider, ::buildClient)
        }
    }

    /**
     * AI Auto-Router: Memilih provider terbaik secara otomatis berdasarkan tugas & ketersediaan API Key.
     */
    fun resolveAutoRoute(
        vault: SecureVault,
        fallbackProvider: AiProviderType,
        prompt: String,
        hasImages: Boolean
    ): AiProviderType {
        val configured = vault.getConfiguredProviders()
        if (configured.isEmpty()) return fallbackProvider

        val lower = prompt.lowercase()
        if (hasImages) {
            val visionPriority = listOf(AiProviderType.GEMINI, AiProviderType.OPENAI, AiProviderType.CLAUDE, AiProviderType.GROK, AiProviderType.OPENROUTER)
            visionPriority.firstOrNull { it in configured }?.let { return it }
        }

        val isCoding = listOf("kode", "code", "bug", "error", "kotlin", "python", "java", "script", "gradle", "sql", "html").any { lower.contains(it) }
        if (isCoding) {
            val codePriority = listOf(AiProviderType.DEEPSEEK, AiProviderType.CLAUDE, AiProviderType.QWEN, AiProviderType.OPENAI, AiProviderType.GEMINI)
            codePriority.firstOrNull { it in configured }?.let { return it }
        }

        val isWebSearch = listOf("berita", "terbaru", "hari ini", "harga", "siapa", "kapan", "news", "latest", "2026").any { lower.contains(it) }
        if (isWebSearch && AiProviderType.PERPLEXITY in configured) {
            return AiProviderType.PERPLEXITY
        }

        if (prompt.length < 90 && AiProviderType.GROQ in configured) {
            return AiProviderType.GROQ
        }

        return if (fallbackProvider in configured) fallbackProvider else configured.first()
    }
}

// ==============================================================================
// ADAPTER 1: GOOGLE GEMINI (SSE STREAMING + MULTIMODAL VISION/PDF)
// ==============================================================================
class GeminiAdapter(
    private val clientFactory: (Long) -> OkHttpClient
) : AiProviderAdapter {

    override fun streamChat(payload: AiRequestPayload): Flow<StreamEvent> = flow {
        val url = "${payload.provider.defaultBaseUrl}/models/${payload.model}:streamGenerateContent?alt=sse&key=${payload.apiKey}"
        val contentsArray = JSONArray()

        for (msg in payload.history) {
            contentsArray.put(JSONObject().apply {
                put("role", if (msg.role == "user") "user" else "model")
                put("parts", JSONArray().apply {
                    put(JSONObject().apply { put("text", msg.text) })
                })
            })
        }

        val userParts = JSONArray().apply {
            put(JSONObject().apply { put("text", payload.userPrompt) })
            for (imgB64 in payload.imageBase64List) {
                put(JSONObject().apply {
                    put("inlineData", JSONObject().apply {
                        put("mimeType", "image/jpeg")
                        put("data", imgB64)
                    })
                })
            }
        }
        contentsArray.put(JSONObject().apply {
            put("role", "user")
            put("parts", userParts)
        })

        val bodyJson = JSONObject().apply {
            put("systemInstruction", JSONObject().apply {
                put("parts", JSONArray().apply {
                    put(JSONObject().apply { put("text", payload.systemInstruction) })
                })
            })
            put("contents", contentsArray)
        }

        executeSseWithRetry(
            client = clientFactory(payload.timeoutSeconds),
            requestBuilder = {
                Request.Builder()
                    .url(url)
                    .post(bodyJson.toString().toRequestBody("application/json; charset=utf-8".toMediaType()))
                    .build()
            },
            extractChunk = { jsonLine ->
                val obj = JSONObject(jsonLine)
                val candidates = obj.optJSONArray("candidates")
                val parts = candidates?.optJSONObject(0)?.optJSONObject("content")?.optJSONArray("parts")
                parts?.optJSONObject(0)?.optString("text", "") ?: ""
            },
            onEvent = { emit(it) }
        )
    }.flowOn(Dispatchers.IO)

    override suspend fun testConnection(apiKey: String, model: String, customBaseUrl: String): Pair<Boolean, String> {
        return try {
            val req = Request.Builder()
                .url("https://generativelanguage.googleapis.com/v1beta/models?key=$apiKey")
                .get()
                .build()
            clientFactory(15L).newCall(req).execute().use { res ->
                if (res.isSuccessful) true to "Gemini terhubung ($model)"
                else false to "Gagal HTTP ${res.code}"
            }
        } catch (e: Exception) {
            false to "Koneksi gagal: ${e.localizedMessage}"
        }
    }
}

// ==============================================================================
// ADAPTER 2: ANTHROPIC CLAUDE (/v1/messages SSE STREAMING + VISION)
// ==============================================================================
class ClaudeAdapter(
    private val clientFactory: (Long) -> OkHttpClient
) : AiProviderAdapter {

    override fun streamChat(payload: AiRequestPayload): Flow<StreamEvent> = flow {
        val url = "${payload.provider.defaultBaseUrl}/messages"
        val messagesArray = JSONArray()

        for (msg in payload.history) {
            messagesArray.put(JSONObject().apply {
                put("role", if (msg.role == "user") "user" else "assistant")
                put("content", msg.text)
            })
        }

        if (payload.imageBase64List.isEmpty()) {
            messagesArray.put(JSONObject().apply {
                put("role", "user")
                put("content", payload.userPrompt)
            })
        } else {
            val contentBlocks = JSONArray()
            for (imgB64 in payload.imageBase64List) {
                contentBlocks.put(JSONObject().apply {
                    put("type", "image")
                    put("source", JSONObject().apply {
                        put("type", "base64")
                        put("media_type", "image/jpeg")
                        put("data", imgB64)
                    })
                })
            }
            contentBlocks.put(JSONObject().apply {
                put("type", "text")
                put("text", payload.userPrompt)
            })
            messagesArray.put(JSONObject().apply {
                put("role", "user")
                put("content", contentBlocks)
            })
        }

        val bodyJson = JSONObject().apply {
            put("model", payload.model)
            put("max_tokens", 2048)
            put("stream", true)
            put("system", payload.systemInstruction)
            put("messages", messagesArray)
        }

        executeSseWithRetry(
            client = clientFactory(payload.timeoutSeconds),
            requestBuilder = {
                Request.Builder()
                    .url(url)
                    .addHeader("x-api-key", payload.apiKey)
                    .addHeader("anthropic-version", "2023-06-01")
                    .addHeader("content-type", "application/json")
                    .post(bodyJson.toString().toRequestBody("application/json; charset=utf-8".toMediaType()))
                    .build()
            },
            extractChunk = { jsonLine ->
                val obj = JSONObject(jsonLine)
                if (obj.optString("type") == "content_block_delta") {
                    obj.optJSONObject("delta")?.optString("text", "") ?: ""
                } else {
                    ""
                }
            },
            onEvent = { emit(it) }
        )
    }.flowOn(Dispatchers.IO)

    override suspend fun testConnection(apiKey: String, model: String, customBaseUrl: String): Pair<Boolean, String> {
        return try {
            val body = JSONObject().apply {
                put("model", model)
                put("max_tokens", 8)
                put("messages", JSONArray().apply {
                    put(JSONObject().apply {
                        put("role", "user")
                        put("content", "Hi")
                    })
                })
            }
            val req = Request.Builder()
                .url("https://api.anthropic.com/v1/messages")
                .addHeader("x-api-key", apiKey)
                .addHeader("anthropic-version", "2023-06-01")
                .post(body.toString().toRequestBody("application/json; charset=utf-8".toMediaType()))
                .build()
            clientFactory(15L).newCall(req).execute().use { res ->
                if (res.isSuccessful) true to "Claude terhubung ($model)"
                else false to "Gagal HTTP ${res.code}"
            }
        } catch (e: Exception) {
            false to "Koneksi gagal: ${e.localizedMessage}"
        }
    }
}

// ==============================================================================
// ADAPTER 3: OPENAI & COMPATIBLE PROVIDERS (OPENAI, DEEPSEEK, GROK, GROQ,
// OPENROUTER, MISTRAL, QWEN, PERPLEXITY, CUSTOM)
// ==============================================================================
class OpenAiCompatibleAdapter(
    private val provider: AiProviderType,
    private val clientFactory: (Long) -> OkHttpClient
) : AiProviderAdapter {

    private fun resolveEndpoint(customBaseUrl: String): String {
        val base = if (provider == AiProviderType.CUSTOM && customBaseUrl.isNotBlank()) {
            customBaseUrl.trimEnd('/')
        } else {
            provider.defaultBaseUrl.trimEnd('/')
        }
        return if (base.endsWith("/chat/completions")) base else "$base/chat/completions"
    }

    override fun streamChat(payload: AiRequestPayload): Flow<StreamEvent> = flow {
        val endpoint = resolveEndpoint(payload.customBaseUrl)
        val messagesArray = JSONArray().apply {
            put(JSONObject().apply {
                put("role", "system")
                put("content", payload.systemInstruction)
            })
            for (msg in payload.history) {
                put(JSONObject().apply {
                    put("role", if (msg.role == "user") "user" else "assistant")
                    put("content", msg.text)
                })
            }
        }

        if (payload.imageBase64List.isNotEmpty() && provider.supportsVision) {
            val contentArray = JSONArray().apply {
                put(JSONObject().apply {
                    put("type", "text")
                    put("text", payload.userPrompt)
                })
                for (imgB64 in payload.imageBase64List) {
                    put(JSONObject().apply {
                        put("type", "image_url")
                        put("image_url", JSONObject().apply {
                            put("url", "data:image/jpeg;base64,$imgB64")
                        })
                    })
                }
            }
            messagesArray.put(JSONObject().apply {
                put("role", "user")
                put("content", contentArray)
            })
        } else {
            messagesArray.put(JSONObject().apply {
                put("role", "user")
                put("content", payload.userPrompt)
            })
        }

        val bodyJson = JSONObject().apply {
            put("model", payload.model)
            put("stream", true)
            put("messages", messagesArray)
        }

        executeSseWithRetry(
            client = clientFactory(payload.timeoutSeconds),
            requestBuilder = {
                val builder = Request.Builder()
                    .url(endpoint)
                    .addHeader("Authorization", "Bearer ${payload.apiKey}")
                    .addHeader("Content-Type", "application/json")
                if (provider == AiProviderType.OPENROUTER) {
                    builder.addHeader("HTTP-Referer", "https://github.com/AvoluProject/FloatingGeminiAI")
                    builder.addHeader("X-Title", "Floamini OS Assistant")
                }
                builder.post(bodyJson.toString().toRequestBody("application/json; charset=utf-8".toMediaType())).build()
            },
            extractChunk = { jsonLine ->
                val obj = JSONObject(jsonLine)
                val choices = obj.optJSONArray("choices")
                val delta = choices?.optJSONObject(0)?.optJSONObject("delta")
                delta?.optString("content", "") ?: ""
            },
            onEvent = { emit(it) }
        )
    }.flowOn(Dispatchers.IO)

    override suspend fun testConnection(apiKey: String, model: String, customBaseUrl: String): Pair<Boolean, String> {
        return try {
            val endpoint = resolveEndpoint(customBaseUrl)
            val bodyJson = JSONObject().apply {
                put("model", model)
                put("max_tokens", 8)
                put("messages", JSONArray().apply {
                    put(JSONObject().apply {
                        put("role", "user")
                        put("content", "Hi")
                    })
                })
            }
            val req = Request.Builder()
                .url(endpoint)
                .addHeader("Authorization", "Bearer $apiKey")
                .addHeader("Content-Type", "application/json")
                .post(bodyJson.toString().toRequestBody("application/json; charset=utf-8".toMediaType()))
                .build()

            clientFactory(15L).newCall(req).execute().use { res ->
                if (res.isSuccessful) true to "${provider.shortBadge} terhubung ($model)"
                else false to "${provider.shortBadge} HTTP ${res.code}"
            }
        } catch (e: Exception) {
            false to "Koneksi gagal: ${e.localizedMessage}"
        }
    }
}

// ==============================================================================
// SHARED SSE STREAMING ENGINE WITH EXPONENTIAL BACKOFF RETRY
// ==============================================================================
private suspend fun executeSseWithRetry(
    client: OkHttpClient,
    requestBuilder: () -> Request,
    extractChunk: (String) -> String,
    onEvent: suspend (StreamEvent) -> Unit
) {
    var attempt = 0
    val maxRetries = 2

    while (attempt <= maxRetries) {
        if (!currentCoroutineContext().isActive) return
        try {
            val response = client.newCall(requestBuilder()).execute()
            response.use { res ->
                if (!res.isSuccessful) {
                    val code = res.code
                    if ((code == 429 || code in 500..599) && attempt < maxRetries) {
                        attempt++
                        delay(800L * attempt)
                        return@use
                    }
                    val errText = res.body?.string()?.take(180) ?: ""
                    onEvent(StreamEvent.Error("Server menolak permintaan (HTTP $code). $errText"))
                    return
                }

                val source = res.body?.source()
                if (source == null) {
                    onEvent(StreamEvent.Error("Stream respons kosong dari server."))
                    return
                }

                val fullBuilder = StringBuilder()
                while (currentCoroutineContext().isActive && !source.exhausted()) {
                    val line = source.readUtf8Line() ?: break
                    if (!line.startsWith("data:")) continue
                    val dataStr = line.removePrefix("data:").trim()
                    if (dataStr.isEmpty() || dataStr == "[DONE]") continue

                    try {
                        val piece = extractChunk(dataStr)
                        if (piece.isNotEmpty()) {
                            fullBuilder.append(piece)
                            onEvent(StreamEvent.Delta(piece))
                        }
                    } catch (_: Exception) {}
                }

                val finalStr = fullBuilder.toString()
                val estTokens = (finalStr.length / 4).coerceAtLeast(1)
                onEvent(StreamEvent.Completed(finalStr, estTokens))
                return
            }
        } catch (ioe: IOException) {
            if (attempt < maxRetries && currentCoroutineContext().isActive) {
                attempt++
                delay(750L * attempt)
            } else {
                onEvent(StreamEvent.Error("Gangguan jaringan: ${ioe.localizedMessage}"))
                return
            }
        } catch (e: Exception) {
            onEvent(StreamEvent.Error("Terjadi kesalahan: ${e.localizedMessage}"))
            return
        }
    }
}
