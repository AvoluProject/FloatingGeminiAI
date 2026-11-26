package com.example.floatinggeminiai.ai

enum class AiProviderType(
    val id: String,
    val displayName: String,
    val shortBadge: String,
    val defaultBaseUrl: String,
    val defaultModel: String,
    val availableModels: List<String>,
    val docsUrl: String,
    val keyHint: String,
    val supportsVision: Boolean
) {
    GEMINI(
        id = "gemini",
        displayName = "Google Gemini",
        shortBadge = "Gemini",
        defaultBaseUrl = "https://generativelanguage.googleapis.com/v1beta",
        defaultModel = "gemini-2.5-flash",
        availableModels = listOf("gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-flash-preview", "gemini-2.0-flash"),
        docsUrl = "https://aistudio.google.com/apikey",
        keyHint = "AIzaSy...",
        supportsVision = true
    ),
    OPENAI(
        id = "openai",
        displayName = "OpenAI",
        shortBadge = "OpenAI",
        defaultBaseUrl = "https://api.openai.com/v1",
        defaultModel = "gpt-4o-mini",
        availableModels = listOf("gpt-4o-mini", "gpt-4o", "o3-mini", "gpt-4.1-mini"),
        docsUrl = "https://platform.openai.com/api-keys",
        keyHint = "sk-proj-...",
        supportsVision = true
    ),
    CLAUDE(
        id = "claude",
        displayName = "Anthropic Claude",
        shortBadge = "Claude",
        defaultBaseUrl = "https://api.anthropic.com/v1",
        defaultModel = "claude-3-5-sonnet-latest",
        availableModels = listOf("claude-3-5-sonnet-latest", "claude-3-5-haiku-latest", "claude-3-7-sonnet-latest"),
        docsUrl = "https://console.anthropic.com/settings/keys",
        keyHint = "sk-ant-...",
        supportsVision = true
    ),
    DEEPSEEK(
        id = "deepseek",
        displayName = "DeepSeek",
        shortBadge = "DeepSeek",
        defaultBaseUrl = "https://api.deepseek.com",
        defaultModel = "deepseek-chat",
        availableModels = listOf("deepseek-chat", "deepseek-reasoner"),
        docsUrl = "https://platform.deepseek.com/api_keys",
        keyHint = "sk-...",
        supportsVision = false
    ),
    GROK(
        id = "grok",
        displayName = "xAI Grok",
        shortBadge = "Grok",
        defaultBaseUrl = "https://api.x.ai/v1",
        defaultModel = "grok-2-latest",
        availableModels = listOf("grok-2-latest", "grok-2-vision-1212", "grok-beta"),
        docsUrl = "https://console.x.ai/",
        keyHint = "xai-...",
        supportsVision = true
    ),
    GROQ(
        id = "groq",
        displayName = "Groq (Ultra-Fast)",
        shortBadge = "Groq",
        defaultBaseUrl = "https://api.groq.com/openai/v1",
        defaultModel = "llama-3.3-70b-versatile",
        availableModels = listOf("llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"),
        docsUrl = "https://console.groq.com/keys",
        keyHint = "gsk_...",
        supportsVision = false
    ),
    OPENROUTER(
        id = "openrouter",
        displayName = "OpenRouter",
        shortBadge = "OpenRouter",
        defaultBaseUrl = "https://openrouter.ai/api/v1",
        defaultModel = "google/gemini-2.5-flash",
        availableModels = listOf("google/gemini-2.5-flash", "anthropic/claude-3.5-sonnet", "openai/gpt-4o-mini", "deepseek/deepseek-chat"),
        docsUrl = "https://openrouter.ai/keys",
        keyHint = "sk-or-v1-...",
        supportsVision = true
    ),
    MISTRAL(
        id = "mistral",
        displayName = "Mistral AI",
        shortBadge = "Mistral",
        defaultBaseUrl = "https://api.mistral.ai/v1",
        defaultModel = "mistral-small-latest",
        availableModels = listOf("mistral-small-latest", "mistral-large-latest", "codestral-latest", "pixtral-12b-2409"),
        docsUrl = "https://console.mistral.ai/api-keys/",
        keyHint = "Mistral API Key...",
        supportsVision = true
    ),
    QWEN(
        id = "qwen",
        displayName = "Alibaba Qwen",
        shortBadge = "Qwen",
        defaultBaseUrl = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        defaultModel = "qwen-plus",
        availableModels = listOf("qwen-plus", "qwen-max", "qwen-turbo", "qwen2.5-coder-32b-instruct"),
        docsUrl = "https://www.alibabacloud.com/help/en/model-studio/",
        keyHint = "sk-...",
        supportsVision = false
    ),
    PERPLEXITY(
        id = "perplexity",
        displayName = "Perplexity (Web Search)",
        shortBadge = "Perplexity",
        defaultBaseUrl = "https://api.perplexity.ai",
        defaultModel = "sonar",
        availableModels = listOf("sonar", "sonar-pro", "sonar-reasoning"),
        docsUrl = "https://www.perplexity.ai/settings/api",
        keyHint = "pplx-...",
        supportsVision = false
    ),
    CUSTOM(
        id = "custom",
        displayName = "Custom OpenAI-Compatible",
        shortBadge = "Custom",
        defaultBaseUrl = "https://api.openai.com/v1",
        defaultModel = "gpt-4o-mini",
        availableModels = listOf("custom-model"),
        docsUrl = "https://developers.openai.com/api/docs",
        keyHint = "Custom API Key...",
        supportsVision = true
    );

    companion object {
        fun fromId(id: String?): AiProviderType {
            return values().find { it.id == id } ?: GEMINI
        }
    }
}

data class ChatMessage(
    val id: String,
    val role: String, // "user" or "model"
    val text: String,
    val timestamp: String,
    val providerBadge: String = "Gemini",
    val modelName: String = "",
    val attachmentLabel: String? = null
)

data class ChatThread(
    val id: String,
    var title: String,
    var updatedAt: Long,
    val messages: MutableList<ChatMessage> = mutableListOf()
)

data class AiRequestPayload(
    val provider: AiProviderType,
    val apiKey: String,
    val model: String,
    val customBaseUrl: String = "",
    val systemInstruction: String,
    val history: List<ChatMessage>,
    val userPrompt: String,
    val imageBase64List: List<String> = emptyList(),
    val timeoutSeconds: Long = 35L
)

sealed class StreamEvent {
    data class Delta(val chunk: String) : StreamEvent()
    data class Completed(val fullText: String, val estimatedTokens: Int) : StreamEvent()
    data class Error(val message: String) : StreamEvent()
}
