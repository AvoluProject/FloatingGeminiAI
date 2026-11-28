package com.example.floatinggeminiai.ai

enum class AiProvider(
    val id: String,
    val displayName: String,
    val defaultBaseUrl: String,
    val docsUrl: String,
    val models: List<String>,
    val supportsVision: Boolean
) {
    GEMINI(
        id = "gemini",
        displayName = "Google Gemini",
        defaultBaseUrl = "https://generativelanguage.googleapis.com/v1beta",
        docsUrl = "https://aistudio.google.com/app/apikey",
        models = listOf("gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash", "gemini-3-flash-preview"),
        supportsVision = true
    ),
    OPENAI(
        id = "openai",
        displayName = "OpenAI",
        defaultBaseUrl = "https://api.openai.com/v1",
        docsUrl = "https://platform.openai.com/api-keys",
        models = listOf("gpt-4o-mini", "gpt-4o", "o3-mini", "gpt-4.1-mini"),
        supportsVision = true
    ),
    CLAUDE(
        id = "claude",
        displayName = "Anthropic Claude",
        defaultBaseUrl = "https://api.anthropic.com/v1",
        docsUrl = "https://console.anthropic.com/settings/keys",
        models = listOf("claude-3-5-haiku-latest", "claude-3-7-sonnet-latest", "claude-sonnet-4-20250514"),
        supportsVision = true
    ),
    DEEPSEEK(
        id = "deepseek",
        displayName = "DeepSeek",
        defaultBaseUrl = "https://api.deepseek.com/v1",
        docsUrl = "https://platform.deepseek.com/api_keys",
        models = listOf("deepseek-chat", "deepseek-reasoner"),
        supportsVision = false
    ),
    GROK(
        id = "grok",
        displayName = "xAI Grok",
        defaultBaseUrl = "https://api.x.ai/v1",
        docsUrl = "https://console.x.ai/",
        models = listOf("grok-2-latest", "grok-3-mini", "grok-3"),
        supportsVision = false
    ),
    GROQ(
        id = "groq",
        displayName = "Groq (Ultra Fast)",
        defaultBaseUrl = "https://api.groq.com/openai/v1",
        docsUrl = "https://console.groq.com/keys",
        models = listOf("llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"),
        supportsVision = false
    ),
    OPENROUTER(
        id = "openrouter",
        displayName = "OpenRouter",
        defaultBaseUrl = "https://openrouter.ai/api/v1",
        docsUrl = "https://openrouter.ai/keys",
        models = listOf("google/gemini-2.5-flash", "anthropic/claude-3.5-sonnet", "openai/gpt-4o-mini", "deepseek/deepseek-r1"),
        supportsVision = true
    ),
    MISTRAL(
        id = "mistral",
        displayName = "Mistral AI",
        defaultBaseUrl = "https://api.mistral.ai/v1",
        docsUrl = "https://console.mistral.ai/api-keys/",
        models = listOf("mistral-small-latest", "mistral-large-latest", "codestral-latest"),
        supportsVision = false
    ),
    QWEN(
        id = "qwen",
        displayName = "Alibaba Qwen",
        defaultBaseUrl = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        docsUrl = "https://www.alibabacloud.com/help/en/model-studio/",
        models = listOf("qwen-plus", "qwen-turbo", "qwen-max"),
        supportsVision = false
    ),
    PERPLEXITY(
        id = "perplexity",
        displayName = "Perplexity (Web Search)",
        defaultBaseUrl = "https://api.perplexity.ai",
        docsUrl = "https://www.perplexity.ai/settings/api",
        models = listOf("sonar", "sonar-pro", "sonar-reasoning"),
        supportsVision = false
    ),
    CUSTOM(
        id = "custom",
        displayName = "Custom OpenAI-Compatible",
        defaultBaseUrl = "https://api.openai.com/v1",
        docsUrl = "https://developers.openai.com/api/docs",
        models = listOf("custom-model"),
        supportsVision = false
    );

    companion object {
        fun fromId(id: String?): AiProvider {
            return entries.find { it.id.equals(id, ignoreCase = true) } ?: GEMINI
        }
    }
}

data class ChatMessage(
    val id: String = System.nanoTime().toString(),
    val role: String, // "user" or "assistant"
    val content: String,
    val providerTag: String = "",
    val timestamp: Long = System.currentTimeMillis()
)

data class ChatThread(
    val id: String,
    var title: String,
    val messages: MutableList<ChatMessage> = mutableListOf(),
    var updatedAt: Long = System.currentTimeMillis()
)
