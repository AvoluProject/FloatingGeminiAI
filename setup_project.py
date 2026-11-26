import os

# ==============================================================================
# SKRIP PEMBANGKIT PROYEK ANDROID: FLOAMINI OS EDITION (v6.0)
# - Design System: iOS 26 Liquid Glass + Adaptive Dark/Light Theme + Spring Physics
# - Floating System: Dynamic Island, Siri Control Center Mode, Xiaomi Edge, Mini/Full Window
# - Multi-AI Engine: 11 Modular Provider Adapters + SSE Streaming + Retry + Auto-Router + Compare AI
# - Voice System: Speech-to-Text, Text-to-Speech, Voice Selection, Live Waveform, Interruption
# - Smart Tools: PDF & File QA, Image Vision, Clipboard, Calculator, Notes, Share-to-AI, Process-Text
# - Security: EncryptedSharedPreferences (AES256-GCM) + Explicit User Permissions
# ==============================================================================

PROJECT_FILES = {
    # --------------------------------------------------------------------------
    # 1. GITHUB ACTIONS WORKFLOW (Gradle 8.5 + Permanent Keystore + Auto Version)
    # --------------------------------------------------------------------------
    ".github/workflows/build_apk.yml": r"""name: Build Floamini OS APK

on:
  push:
    branches: [ "main", "master" ]
  pull_request:
    branches: [ "main", "master" ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Restore Permanent Signing Keystore
        uses: actions/cache@v4
        with:
          path: app/floamini.jks
          key: floamini-permanent-keystore-v1

      - name: Ensure Permanent Signing Keystore Exists
        run: |
          if [ ! -f app/floamini.jks ]; then
            keytool -genkeypair -v -keystore app/floamini.jks -alias floamini_key -keyalg RSA -keysize 2048 -validity 10000 -storepass floamini_keystore_pass_2026 -keypass floamini_keystore_pass_2026 -dname "CN=Floamini, OU=Mobile, O=AvoluProject, L=Yogyakarta, ST=DIY, C=ID"
          fi

      - name: Setup Gradle 8.5
        uses: gradle/actions/setup-gradle@v4
        with:
          gradle-version: '8.5'

      - name: Build Update-Ready APK
        run: gradle assembleDebug

      - name: Upload Floamini APK Artifact
        uses: actions/upload-artifact@v4
        with:
          name: Floamini-OS-v6.0-update-ready
          path: app/build/outputs/apk/debug/app-debug.apk
""",

    # --------------------------------------------------------------------------
    # 2. KONFIGURASI GRADLE ROOT
    # --------------------------------------------------------------------------
    "settings.gradle.kts": r"""pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "Floamini"
include(":app")
""",

    "build.gradle.kts": r"""plugins {
    id("com.android.application") version "8.2.2" apply false
    id("org.jetbrains.kotlin.android") version "1.9.22" apply false
}
""",

    "gradle.properties": r"""org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
android.nonTransitiveRClass=true
""",

    # --------------------------------------------------------------------------
    # 3. KONFIGURASI GRADLE MODULE (:app)
    # --------------------------------------------------------------------------
    "app/build.gradle.kts": r"""plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

val ciRunNumber = System.getenv("GITHUB_RUN_NUMBER")?.toIntOrNull() ?: 0
val appVersionCode = 10 + ciRunNumber
val appVersionName = "6.0.$ciRunNumber"

android {
    namespace = "com.example.floatinggeminiai"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.floatinggeminiai"
        minSdk = 26
        targetSdk = 34
        versionCode = appVersionCode
        versionName = appVersionName
    }

    signingConfigs {
        create("floaminiSign") {
            val ksFile = file("floamini.jks")
            if (ksFile.exists()) {
                storeFile = ksFile
                storePassword = "floamini_keystore_pass_2026"
                keyAlias = "floamini_key"
                keyPassword = "floamini_keystore_pass_2026"
            }
        }
    }

    buildTypes {
        debug {
            val ksFile = file("floamini.jks")
            if (ksFile.exists()) {
                signingConfig = signingConfigs.getByName("floaminiSign")
            }
        }
        release {
            isMinifyEnabled = false
            val ksFile = file("floamini.jks")
            if (ksFile.exists()) {
                signingConfig = signingConfigs.getByName("floaminiSign")
            }
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("androidx.dynamicanimation:dynamicanimation:1.0.0")
    implementation("androidx.security:security-crypto:1.1.0-alpha06")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
}
""",

    # --------------------------------------------------------------------------
    # 4. ANDROID MANIFEST (OVERLAY + CONTROL CENTER + VOICE + SHARE/PROCESS_TEXT)
    # --------------------------------------------------------------------------
    "app/src/main/AndroidManifest.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.VIBRATE" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <queries>
        <intent>
            <action android:name="android.intent.action.TTS_SERVICE" />
        </intent>
        <intent>
            <action android:name="android.speech.RecognitionService" />
        </intent>
    </queries>

    <application
        android:allowBackup="true"
        android:label="Floamini"
        android:supportsRtl="true"
        android:theme="@style/Theme.Floamini.Adaptive">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <activity
            android:name=".WelcomeActivity"
            android:exported="false" />

        <activity
            android:name=".SiriTriggerActivity"
            android:exported="false"
            android:excludeFromRecents="true"
            android:theme="@android:style/Theme.Translucent.NoTitleBar" />

        <activity
            android:name=".ScreenCapturePermissionActivity"
            android:exported="false"
            android:excludeFromRecents="true"
            android:theme="@android:style/Theme.Translucent.NoTitleBar" />

        <activity
            android:name=".FilePickerProxyActivity"
            android:exported="false"
            android:excludeFromRecents="true"
            android:theme="@android:style/Theme.Translucent.NoTitleBar" />

        <activity
            android:name=".AudioPermissionProxyActivity"
            android:exported="false"
            android:excludeFromRecents="true"
            android:theme="@android:style/Theme.Translucent.NoTitleBar" />

        <!-- Text Selection Assistant (PROCESS_TEXT) & Share-to-AI (ACTION_SEND) -->
        <activity
            android:name=".ExternalTriggerActivity"
            android:exported="true"
            android:label="Tanya Floamini AI"
            android:excludeFromRecents="true"
            android:theme="@android:style/Theme.Translucent.NoTitleBar">
            <intent-filter>
                <action android:name="android.intent.action.PROCESS_TEXT" />
                <category android:name="android.intent.category.DEFAULT" />
                <data android:mimeType="text/plain" />
            </intent-filter>
            <intent-filter>
                <action android:name="android.intent.action.SEND" />
                <category android:name="android.intent.category.DEFAULT" />
                <data android:mimeType="text/plain" />
            </intent-filter>
            <intent-filter>
                <action android:name="android.intent.action.SEND" />
                <category android:name="android.intent.category.DEFAULT" />
                <data android:mimeType="image/*" />
            </intent-filter>
            <intent-filter>
                <action android:name="android.intent.action.SEND" />
                <category android:name="android.intent.category.DEFAULT" />
                <data android:mimeType="application/pdf" />
            </intent-filter>
        </activity>

        <service
            android:name=".FloaminiTileService"
            android:exported="true"
            android:icon="@drawable/ic_sparkle"
            android:label="Floamini AI"
            android:permission="android.permission.BIND_QUICK_SETTINGS_TILE">
            <intent-filter>
                <action android:name="android.service.quicksettings.action.QS_TILE" />
            </intent-filter>
        </service>

        <service
            android:name=".FloatingAssistantService"
            android:enabled="true"
            android:exported="false"
            android:foregroundServiceType="specialUse|mediaProjection">
            <property
                android:name="android.app.PROPERTY_SPECIAL_USE_FGS_SUBTYPE"
                android:value="Floamini OS Liquid Glass AI Assistant" />
        </service>

    </application>
</manifest>
""",

    # --------------------------------------------------------------------------
    # 5. ADAPTIVE THEME VALUES (DARK & LIGHT LIQUID GLASS PALETTE)
    # --------------------------------------------------------------------------
    "app/src/main/res/values/colors.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="bg_screen">#F2F5FA</color>
    <color name="bg_card">#E6FFFFFF</color>
    <color name="bg_input">#E2E8F0</color>
    <color name="border_glass">#330F172A</color>
    <color name="text_primary">#0F172A</color>
    <color name="text_secondary">#475569</color>
    <color name="accent_primary">#0284C7</color>
    <color name="accent_secondary">#7C3AED</color>
    <color name="divider_subtle">#CBD5E1</color>
</resources>
""",

    "app/src/main/res/values-night/colors.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="bg_screen">#04070F</color>
    <color name="bg_card">#E611192B</color>
    <color name="bg_input">#0B111E</color>
    <color name="border_glass">#40FFFFFF</color>
    <color name="text_primary">#F8FAFC</color>
    <color name="text_secondary">#94A3B8</color>
    <color name="accent_primary">#38BDF8</color>
    <color name="accent_secondary">#C084FC</color>
    <color name="divider_subtle">#1E293B</color>
</resources>
""",

    "app/src/main/res/values/themes.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.Floamini.Adaptive" parent="Theme.Material3.DayNight.NoActionBar">
        <item name="colorPrimary">@color/accent_primary</item>
        <item name="colorSecondary">@color/accent_secondary</item>
        <item name="android:windowBackground">@color/bg_screen</item>
        <item name="android:statusBarColor">@color/bg_screen</item>
    </style>
</resources>
""",

    # --------------------------------------------------------------------------
    # 6. SECURITY MODULE: ENCRYPTED CREDENTIAL VAULT (AES-256 GCM)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/security/SecureVault.kt": r"""package com.example.floatinggeminiai.security

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import com.example.floatinggeminiai.ai.AiProviderType

class SecureVault(context: Context) {

    private val appContext = context.applicationContext

    private val securePrefs: SharedPreferences by lazy {
        try {
            val masterKey = MasterKey.Builder(appContext)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build()
            EncryptedSharedPreferences.create(
                appContext,
                "floamini_encrypted_vault",
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        } catch (_: Exception) {
            appContext.getSharedPreferences("floamini_vault_fallback", Context.MODE_PRIVATE)
        }
    }

    init {
        migrateLegacyGeminiKeyIfNeeded()
    }

    private fun migrateLegacyGeminiKeyIfNeeded() {
        val legacyPrefs = appContext.getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        val legacyKey = legacyPrefs.getString("api_key", "") ?: ""
        if (legacyKey.isNotEmpty() && getApiKey(AiProviderType.GEMINI).isEmpty()) {
            setApiKey(AiProviderType.GEMINI, legacyKey)
            legacyPrefs.edit().remove("api_key").apply()
        }
    }

    fun getApiKey(provider: AiProviderType): String {
        return securePrefs.getString("key_${provider.id}", "")?.trim() ?: ""
    }

    fun setApiKey(provider: AiProviderType, apiKey: String) {
        val clean = apiKey.trim()
        if (clean.isEmpty()) {
            securePrefs.edit().remove("key_${provider.id}").apply()
        } else {
            securePrefs.edit().putString("key_${provider.id}", clean).apply()
        }
    }

    fun hasAnyConfiguredKey(): Boolean {
        return AiProviderType.values().any { getApiKey(it).isNotEmpty() }
    }

    fun getConfiguredProviders(): List<AiProviderType> {
        return AiProviderType.values().filter { getApiKey(it).isNotEmpty() }
    }

    fun getSelectedModel(provider: AiProviderType): String {
        return securePrefs.getString("model_${provider.id}", provider.defaultModel)
            ?.ifBlank { provider.defaultModel } ?: provider.defaultModel
    }

    fun setSelectedModel(provider: AiProviderType, modelId: String) {
        securePrefs.edit().putString("model_${provider.id}", modelId.trim()).apply()
    }

    fun getCustomBaseUrl(): String {
        return securePrefs.getString("custom_base_url", "https://api.openai.com/v1")
            ?.ifBlank { "https://api.openai.com/v1" } ?: "https://api.openai.com/v1"
    }

    fun setCustomBaseUrl(url: String) {
        securePrefs.edit().putString("custom_base_url", url.trim().trimEnd('/')).apply()
    }

    fun clearAllCredentials() {
        securePrefs.edit().clear().apply()
    }
}
""",

    # --------------------------------------------------------------------------
    # 7. AI MODELS & PROVIDER METADATA (ALL 11 PROVIDERS)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/ai/AiModels.kt": r"""package com.example.floatinggeminiai.ai

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
""",

    # --------------------------------------------------------------------------
    # 8. MODULAR MULTI-AI ADAPTER ENGINE (SSE STREAMING + RETRY + AUTO-ROUTER)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/ai/AiProviderAdapters.kt": r"""package com.example.floatinggeminiai.ai

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
""",

    # --------------------------------------------------------------------------
    # 9. DATA REPOSITORY (MULTI-THREAD HISTORY, SEARCH, USAGE TRACKING, NOTES)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/data/ChatRepository.kt": r"""package com.example.floatinggeminiai.data

import android.content.Context
import com.example.floatinggeminiai.ai.AiProviderType
import com.example.floatinggeminiai.ai.ChatMessage
import com.example.floatinggeminiai.ai.ChatThread
import org.json.JSONArray
import org.json.JSONObject
import java.util.UUID

class ChatRepository(context: Context) {

    private val prefs = context.applicationContext.getSharedPreferences("floamini_data_store", Context.MODE_PRIVATE)

    fun loadAllThreads(): MutableList<ChatThread> {
        val raw = prefs.getString("chat_threads_v6", null) ?: return mutableListOf()
        val list = mutableListOf<ChatThread>()
        try {
            val arr = JSONArray(raw)
            for (i in 0 until arr.length()) {
                val obj = arr.getJSONObject(i)
                val msgArr = obj.optJSONArray("messages") ?: JSONArray()
                val messages = mutableListOf<ChatMessage>()
                for (j in 0 until msgArr.length()) {
                    val m = msgArr.getJSONObject(j)
                    messages.add(
                        ChatMessage(
                            id = m.optString("id", UUID.randomUUID().toString()),
                            role = m.optString("role", "user"),
                            text = m.optString("text", ""),
                            timestamp = m.optString("timestamp", ""),
                            providerBadge = m.optString("providerBadge", "Gemini"),
                            modelName = m.optString("modelName", ""),
                            attachmentLabel = m.optString("attachmentLabel", "").ifEmpty { null }
                        )
                    )
                }
                list.add(
                    ChatThread(
                        id = obj.optString("id", UUID.randomUUID().toString()),
                        title = obj.optString("title", "Sesi Baru"),
                        updatedAt = obj.optLong("updatedAt", System.currentTimeMillis()),
                        messages = messages
                    )
                )
            }
        } catch (_: Exception) {}
        return list
    }

    fun saveAllThreads(threads: List<ChatThread>) {
        val arr = JSONArray()
        for (t in threads.take(40)) {
            val msgArr = JSONArray()
            for (m in t.messages.takeLast(120)) {
                msgArr.put(JSONObject().apply {
                    put("id", m.id)
                    put("role", m.role)
                    put("text", m.text)
                    put("timestamp", m.timestamp)
                    put("providerBadge", m.providerBadge)
                    put("modelName", m.modelName)
                    put("attachmentLabel", m.attachmentLabel ?: "")
                })
            }
            arr.put(JSONObject().apply {
                put("id", t.id)
                put("title", t.title)
                put("updatedAt", t.updatedAt)
                put("messages", msgArr)
            })
        }
        prefs.edit().putString("chat_threads_v6", arr.toString()).apply()
    }

    fun getActiveThreadId(): String {
        return prefs.getString("active_thread_id", "") ?: ""
    }

    fun setActiveThreadId(id: String) {
        prefs.edit().putString("active_thread_id", id).apply()
    }

    fun searchThreads(query: String): List<ChatThread> {
        val q = query.trim().lowercase()
        val all = loadAllThreads()
        if (q.isEmpty()) return all
        return all.filter { thread ->
            thread.title.lowercase().contains(q) ||
                    thread.messages.any { it.text.lowercase().contains(q) }
        }
    }

    fun clearAllThreads() {
        prefs.edit().remove("chat_threads_v6").remove("active_thread_id").apply()
    }

    // Usage Statistics per Provider
    fun recordUsage(provider: AiProviderType, estimatedTokens: Int) {
        val reqKey = "usage_req_${provider.id}"
        val tokKey = "usage_tok_${provider.id}"
        val curReq = prefs.getInt(reqKey, 0) + 1
        val curTok = prefs.getLong(tokKey, 0L) + estimatedTokens.coerceAtLeast(1)
        prefs.edit()
            .putInt(reqKey, curReq)
            .putLong(tokKey, curTok)
            .apply()
    }

    fun getUsageSummaryText(): String {
        val sb = StringBuilder()
        var totalReq = 0
        var totalTok = 0L
        for (p in AiProviderType.values()) {
            val req = prefs.getInt("usage_req_${p.id}", 0)
            val tok = prefs.getLong("usage_tok_${p.id}", 0L)
            if (req > 0) {
                totalReq += req
                totalTok += tok
                sb.append("• ${p.displayName}: $req request (~$tok token)\n")
            }
        }
        if (totalReq == 0) {
            return "Belum ada pemakaian API tercatat pada sesi ini."
        }
        return "Total Keseluruhan: $totalReq request (~$totalTok token)\n\n$sb".trim()
    }

    fun resetUsageStats() {
        val ed = prefs.edit()
        for (p in AiProviderType.values()) {
            ed.remove("usage_req_${p.id}").remove("usage_tok_${p.id}")
        }
        ed.apply()
    }

    // Quick Notes Storage
    fun getQuickNotes(): String = prefs.getString("quick_notes_text", "") ?: ""
    fun saveQuickNotes(text: String) {
        prefs.edit().putString("quick_notes_text", text).apply()
    }
}
""",

    # --------------------------------------------------------------------------
    # 10. VOICE SYSTEM MANAGER (STT, TTS, VOICE SELECTION, INTERRUPTION)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/voice/VoiceSystemManager.kt": r"""package com.example.floatinggeminiai.voice

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.speech.tts.Voice
import java.util.Locale

class VoiceSystemManager(
    context: Context,
    private val onRmsChanged: (Float) -> Unit,
    private val onPartialSpeech: (String) -> Unit,
    private val onFinalSpeech: (String) -> Unit,
    private val onListeningStateChanged: (Boolean) -> Unit,
    private val onSpeakingStateChanged: (Boolean) -> Unit,
    private val onVoiceError: (String) -> Unit
) {
    private val appContext = context.applicationContext
    private var speechRecognizer: SpeechRecognizer? = null
    private var tts: TextToSpeech? = null
    private var isTtsReady = false
    var isListening = false
        private set
    var isSpeaking = false
        private set

    init {
        initTts()
    }

    private fun initTts() {
        tts = TextToSpeech(appContext) { status ->
            if (status == TextToSpeech.SUCCESS) {
                val res = tts?.setLanguage(Locale("id", "ID"))
                if (res == TextToSpeech.LANG_MISSING_DATA || res == TextToSpeech.LANG_NOT_SUPPORTED) {
                    tts?.setLanguage(Locale.US)
                }
                tts?.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                    override fun onStart(utteranceId: String?) {
                        isSpeaking = true
                        onSpeakingStateChanged(true)
                    }

                    override fun onDone(utteranceId: String?) {
                        isSpeaking = false
                        onSpeakingStateChanged(false)
                    }

                    @Deprecated("Deprecated in Java")
                    override fun onError(utteranceId: String?) {
                        isSpeaking = false
                        onSpeakingStateChanged(false)
                    }
                })
                isTtsReady = true
            }
        }
    }

    fun startListening() {
        // Interupsi TTS secara otomatis jika AI sedang berbicara
        stopSpeaking()

        if (!SpeechRecognizer.isRecognitionAvailable(appContext)) {
            onVoiceError("Layanan Speech-to-Text tidak tersedia di perangkat ini.")
            return
        }

        try {
            speechRecognizer?.destroy()
            speechRecognizer = SpeechRecognizer.createSpeechRecognizer(appContext).apply {
                setRecognitionListener(object : RecognitionListener {
                    override fun onReadyForSpeech(params: Bundle?) {
                        isListening = true
                        onListeningStateChanged(true)
                    }

                    override fun onBeginningOfSpeech() {}

                    override fun onRmsChanged(rmsdB: Float) {
                        val normalized = ((rmsdB + 2f) / 12f).coerceIn(0.08f, 1.0f)
                        onRmsChanged(normalized)
                    }

                    override fun onBufferReceived(buffer: ByteArray?) {}

                    override fun onEndOfSpeech() {
                        isListening = false
                        onListeningStateChanged(false)
                    }

                    override fun onError(error: Int) {
                        isListening = false
                        onListeningStateChanged(false)
                        if (error != SpeechRecognizer.ERROR_CLIENT && error != SpeechRecognizer.ERROR_NO_MATCH) {
                            onVoiceError("Suara kurang jelas (Kode $error), coba bicara lagi.")
                        }
                    }

                    override fun onResults(results: Bundle?) {
                        isListening = false
                        onListeningStateChanged(false)
                        val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                        val text = matches?.firstOrNull()?.trim() ?: ""
                        if (text.isNotEmpty()) {
                            onFinalSpeech(text)
                        }
                    }

                    override fun onPartialResults(partialResults: Bundle?) {
                        val partial = partialResults?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull() ?: ""
                        if (partial.isNotEmpty()) {
                            onPartialSpeech(partial)
                        }
                    }

                    override fun onEvent(eventType: Int, params: Bundle?) {}
                })
            }

            val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, "id-ID")
                putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
                putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            }
            speechRecognizer?.startListening(intent)
        } catch (e: Exception) {
            isListening = false
            onListeningStateChanged(false)
            onVoiceError("Gagal memulai mikrofon: ${e.localizedMessage}")
        }
    }

    fun stopListening() {
        try {
            speechRecognizer?.stopListening()
        } catch (_: Exception) {}
        isListening = false
        onListeningStateChanged(false)
    }

    fun speak(text: String, speechRate: Float = 1.05f, preferredVoiceName: String = "") {
        if (!isTtsReady || text.isBlank()) return
        stopSpeaking()
        tts?.setSpeechRate(speechRate.coerceIn(0.6f, 1.8f))
        if (preferredVoiceName.isNotEmpty()) {
            val match = tts?.voices?.firstOrNull { it.name == preferredVoiceName }
            if (match != null) {
                tts?.voice = match
            }
        }
        val cleanText = text.take(1500)
        tts?.speak(cleanText, TextToSpeech.QUEUE_FLUSH, null, "floamini_tts_${System.currentTimeMillis()}")
    }

    fun stopSpeaking() {
        try {
            if (tts?.isSpeaking == true) {
                tts?.stop()
            }
        } catch (_: Exception) {}
        isSpeaking = false
        onSpeakingStateChanged(false)
    }

    fun getAvailableVoices(): List<Voice> {
        return try {
            tts?.voices?.filter { !it.isNetworkConnectionRequired }?.sortedBy { it.locale.displayName } ?: emptyList()
        } catch (_: Exception) {
            emptyList()
        }
    }

    fun release() {
        stopListening()
        stopSpeaking()
        try { speechRecognizer?.destroy() } catch (_: Exception) {}
        try { tts?.shutdown() } catch (_: Exception) {}
        speechRecognizer = null
        tts = null
    }
}
""",

    # --------------------------------------------------------------------------
    # 11. SMART TOOLS HELPER (PDF RENDERER, IMAGE B64, MATH PARSER, CODE FORMATTER)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/tools/SmartToolsHelper.kt": r"""package com.example.floatinggeminiai.tools

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.pdf.PdfRenderer
import android.net.Uri
import android.text.Spannable
import android.text.SpannableStringBuilder
import android.text.style.BackgroundColorSpan
import android.text.style.ForegroundColorSpan
import android.text.style.StyleSpan
import android.text.style.TypefaceSpan
import android.util.Base64
import java.io.ByteArrayOutputStream
import java.io.InputStreamReader
import kotlin.math.pow

data class ProcessedAttachment(
    val displayName: String,
    val extractedText: String,
    val imageBase64List: List<String>
)

object SmartToolsHelper {

    fun processUriAttachment(context: Context, uri: Uri): ProcessedAttachment? {
        val resolver = context.contentResolver
        val mime = resolver.getType(uri) ?: ""
        val name = uri.lastPathSegment?.substringAfterLast('/') ?: "Lampiran"

        return when {
            mime == "application/pdf" || name.endsWith(".pdf", ignoreCase = true) -> {
                extractPdfPagesAsImages(context, uri, name)
            }
            mime.startsWith("image/") -> {
                val b64 = encodeImageUriToBase64(context, uri) ?: return null
                ProcessedAttachment(
                    displayName = "Gambar: $name",
                    extractedText = "",
                    imageBase64List = listOf(b64)
                )
            }
            else -> {
                val text = readTextFromUri(context, uri)
                if (text.isBlank()) null
                else ProcessedAttachment(
                    displayName = "Dokumen: $name",
                    extractedText = text.take(12000),
                    imageBase64List = emptyList()
                )
            }
        }
    }

    private fun extractPdfPagesAsImages(context: Context, uri: Uri, name: String): ProcessedAttachment? {
        return try {
            val pfd = context.contentResolver.openFileDescriptor(uri, "r") ?: return null
            val renderer = PdfRenderer(pfd)
            val pageCount = renderer.pageCount.coerceAtMost(3)
            val images = mutableListOf<String>()

            for (i in 0 until pageCount) {
                val page = renderer.openPage(i)
                val targetW = 768
                val targetH = (page.height.toFloat() / page.width.toFloat() * targetW).toInt().coerceAtLeast(256)
                val bmp = Bitmap.createBitmap(targetW, targetH, Bitmap.Config.ARGB_8888)
                bmp.eraseColor(Color.WHITE)
                page.render(bmp, null, null, PdfRenderer.Page.RENDER_MODE_FOR_DISPLAY)
                page.close()

                val out = ByteArrayOutputStream()
                bmp.compress(Bitmap.CompressFormat.JPEG, 72, out)
                bmp.recycle()
                images.add(Base64.encodeToString(out.toByteArray(), Base64.NO_WRAP))
            }
            renderer.close()
            pfd.close()

            ProcessedAttachment(
                displayName = "PDF ($pageCount hal): $name",
                extractedText = "[Lampiran dokumen PDF $name berisi $pageCount halaman visual]",
                imageBase64List = images
            )
        } catch (_: Exception) {
            null
        }
    }

    fun encodeImageUriToBase64(context: Context, uri: Uri): String? {
        return try {
            val input = context.contentResolver.openInputStream(uri) ?: return null
            val original = BitmapFactory.decodeStream(input)
            input.close()
            if (original == null) return null

            val maxDim = 960
            val scale = if (original.width > maxDim || original.height > maxDim) {
                maxDim.toFloat() / maxOf(original.width, original.height)
            } else 1.0f

            val scaled = if (scale < 1.0f) {
                Bitmap.createScaledBitmap(
                    original,
                    (original.width * scale).toInt(),
                    (original.height * scale).toInt(),
                    true
                )
            } else original

            val out = ByteArrayOutputStream()
            scaled.compress(Bitmap.CompressFormat.JPEG, 72, out)
            if (scaled !== original) scaled.recycle()
            original.recycle()

            Base64.encodeToString(out.toByteArray(), Base64.NO_WRAP)
        } catch (_: Exception) {
            null
        }
    }

    private fun readTextFromUri(context: Context, uri: Uri): String {
        return try {
            val input = context.contentResolver.openInputStream(uri) ?: return ""
            InputStreamReader(input, Charsets.UTF_8).use { it.readText() }
        } catch (_: Exception) {
            ""
        }
    }

    /**
     * Rich Markdown & Code Syntax Highlighter untuk gelembung chat
     */
    fun formatRichMarkdown(raw: String): CharSequence {
        val builder = SpannableStringBuilder()
        val segments = raw.split("```")

        for (i in segments.indices) {
            val seg = segments[i]
            if (i % 2 == 1) {
                // Code Block
                val firstNewline = seg.indexOf('\n')
                val codeBody = if (firstNewline != -1) seg.substring(firstNewline + 1).trimEnd() else seg.trim()
                val start = builder.length
                builder.append("\n$codeBody\n")
                val end = builder.length
                builder.setSpan(TypefaceSpan("monospace"), start, end, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
                builder.setSpan(BackgroundColorSpan(Color.parseColor("#CC070B14")), start, end, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
                builder.setSpan(ForegroundColorSpan(Color.parseColor("#7DD3FC")), start, end, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
            } else {
                // Normal text with inline **bold** and `code`
                appendFormattedInline(builder, seg)
            }
        }
        return builder
    }

    private fun appendFormattedInline(builder: SpannableStringBuilder, text: String) {
        var idx = 0
        while (idx < text.length) {
            if (text.startsWith("**", idx)) {
                val endIdx = text.indexOf("**", idx + 2)
                if (endIdx != -1) {
                    val content = text.substring(idx + 2, endIdx)
                    val s = builder.length
                    builder.append(content)
                    builder.setSpan(StyleSpan(Typeface.BOLD), s, builder.length, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
                    idx = endIdx + 2
                    continue
                }
            }
            if (text[idx] == '`') {
                val endIdx = text.indexOf('`', idx + 1)
                if (endIdx != -1) {
                    val content = text.substring(idx + 1, endIdx)
                    val s = builder.length
                    builder.append(" $content ")
                    builder.setSpan(TypefaceSpan("monospace"), s, builder.length, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
                    builder.setSpan(BackgroundColorSpan(Color.parseColor("#3338BDF8")), s, builder.length, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
                    idx = endIdx + 1
                    continue
                }
            }
            builder.append(text[idx])
            idx++
        }
    }

    /**
     * Safe Mathematical Expression Evaluator (Floating Calculator)
     */
    fun evaluateMathExpression(expr: String): String {
        val clean = expr.replace("×", "*").replace("÷", "/").replace(",", ".").replace(" ", "")
        if (clean.isEmpty()) return "0"
        return try {
            val result = object : Any() {
                var pos = -1
                var ch = 0

                fun nextChar() {
                    ch = if (++pos < clean.length) clean[pos].code else -1
                }

                fun eat(charToEat: Int): Boolean {
                    while (ch == ' '.code) nextChar()
                    if (ch == charToEat) {
                        nextChar()
                        return true
                    }
                    return false
                }

                fun parse(): Double {
                    nextChar()
                    val x = parseExpression()
                    if (pos < clean.length) throw RuntimeException("Unexpected")
                    return x
                }

                fun parseExpression(): Double {
                    var x = parseTerm()
                    while (true) {
                        when {
                            eat('+'.code) -> x += parseTerm()
                            eat('-'.code) -> x -= parseTerm()
                            else -> return x
                        }
                    }
                }

                fun parseTerm(): Double {
                    var x = parseFactor()
                    while (true) {
                        when {
                            eat('*'.code) -> x *= parseFactor()
                            eat('/'.code) -> x /= parseFactor()
                            eat('%'.code) -> x %= parseFactor()
                            else -> return x
                        }
                    }
                }

                fun parseFactor(): Double {
                    if (eat('+'.code)) return parseFactor()
                    if (eat('-'.code)) return -parseFactor()
                    var x: Double
                    val startPos = pos
                    if (eat('('.code)) {
                        x = parseExpression()
                        eat(')'.code)
                    } else if ((ch in '0'.code..'9'.code) || ch == '.'.code) {
                        while ((ch in '0'.code..'9'.code) || ch == '.'.code) nextChar()
                        x = clean.substring(startPos, pos).toDouble()
                    } else {
                        throw RuntimeException("Unexpected")
                    }
                    if (eat('^'.code)) x = x.pow(parseFactor())
                    return x
                }
            }.parse()

            if (result.isNaN() || result.isInfinite()) "Error"
            else if (result % 1.0 == 0.0) result.toLong().toString()
            else String.format("%.6f", result).trimEnd('0').trimEnd('.')
        } catch (_: Exception) {
            "Format salah"
        }
    }
}
""",

    # --------------------------------------------------------------------------
    # 12. CUSTOM VIEWS: SIRI EDGE GLOW AURA & 60 FPS VOICE WAVEFORM
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/SiriEdgeGlowView.kt": r"""package com.example.floatinggeminiai

import android.animation.ValueAnimator
import android.content.Context
import android.graphics.BlurMaskFilter
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Matrix
import android.graphics.Paint
import android.graphics.RectF
import android.graphics.SweepGradient
import android.util.AttributeSet
import android.view.View
import android.view.animation.LinearInterpolator

class SiriEdgeGlowView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val gradientColors = intArrayOf(
        Color.parseColor("#38BDF8"),
        Color.parseColor("#818CF8"),
        Color.parseColor("#E879F9"),
        Color.parseColor("#F472B6"),
        Color.parseColor("#22D3EE"),
        Color.parseColor("#38BDF8")
    )

    private val glowPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 28f * resources.displayMetrics.density
        maskFilter = BlurMaskFilter(24f * resources.displayMetrics.density, BlurMaskFilter.Blur.NORMAL)
    }

    private val coreRimPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 4.5f * resources.displayMetrics.density
    }

    private var sweepGradient: SweepGradient? = null
    private val shaderMatrix = Matrix()
    private val screenRect = RectF()
    private var currentAngle = 0f
    private var pulseScale = 1f
    private var rotationAnimator: ValueAnimator? = null

    init {
        setLayerType(LAYER_TYPE_SOFTWARE, null)
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        if (w > 0 && h > 0) {
            sweepGradient = SweepGradient(w / 2f, h / 2f, gradientColors, null)
            glowPaint.shader = sweepGradient
            coreRimPaint.shader = sweepGradient
            val inset = 4f * resources.displayMetrics.density
            screenRect.set(inset, inset, w - inset, h - inset)
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val gradient = sweepGradient ?: return
        shaderMatrix.setRotate(currentAngle, width / 2f, height / 2f)
        gradient.setLocalMatrix(shaderMatrix)

        val baseStroke = 24f * resources.displayMetrics.density
        glowPaint.strokeWidth = baseStroke * pulseScale

        val cornerRadius = 38f * resources.displayMetrics.density
        canvas.drawRoundRect(screenRect, cornerRadius, cornerRadius, glowPaint)
        canvas.drawRoundRect(screenRect, cornerRadius, cornerRadius, coreRimPaint)
    }

    fun startSiriAnimation() {
        if (rotationAnimator?.isRunning == true) return
        rotationAnimator = ValueAnimator.ofFloat(0f, 360f).apply {
            duration = 2800L
            repeatCount = ValueAnimator.INFINITE
            interpolator = LinearInterpolator()
            addUpdateListener { anim ->
                currentAngle = anim.animatedValue as Float
                val rad = Math.toRadians(currentAngle.toDouble() * 2.0)
                pulseScale = 0.88f + (0.24f * ((Math.sin(rad).toFloat() + 1f) / 2f))
                invalidate()
            }
            start()
        }
    }

    fun stopAndFreezeAnimation() {
        rotationAnimator?.cancel()
        rotationAnimator = null
    }

    override fun onDetachedFromWindow() {
        stopAndFreezeAnimation()
        super.onDetachedFromWindow()
    }
}
""",

    "app/src/main/java/com/example/floatinggeminiai/ui/VoiceWaveformView.kt": r"""package com.example.floatinggeminiai.ui

import android.animation.ValueAnimator
import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.LinearGradient
import android.graphics.Paint
import android.graphics.RectF
import android.graphics.Shader
import android.util.AttributeSet
import android.view.View
import android.view.animation.LinearInterpolator
import kotlin.math.sin

class VoiceWaveformView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val barCount = 18
    private val barRect = RectF()
    private val barPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
    }
    private var phase = 0f
    private var targetAmplitude = 0.15f
    private var currentAmplitude = 0.15f
    private var animator: ValueAnimator? = null

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        if (w > 0 && h > 0) {
            barPaint.shader = LinearGradient(
                0f, 0f, w.toFloat(), 0f,
                intArrayOf(
                    Color.parseColor("#38BDF8"),
                    Color.parseColor("#818CF8"),
                    Color.parseColor("#E879F9")
                ),
                null,
                Shader.TileMode.CLAMP
            )
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        if (width <= 0 || height <= 0) return

        currentAmplitude += (targetAmplitude - currentAmplitude) * 0.28f
        val spacing = width.toFloat() / (barCount * 2f)
        val barWidth = spacing.coerceAtLeast(3f * resources.displayMetrics.density)
        val centerY = height / 2f
        val maxHalfH = height * 0.44f
        val minHalfH = 3f * resources.displayMetrics.density

        for (i in 0 until barCount) {
            val normPos = i.toFloat() / (barCount - 1)
            val envelope = sin(normPos * Math.PI).toFloat()
            val wave = (sin((phase + i * 0.65f).toDouble()).toFloat() + 1f) / 2f
            val halfH = minHalfH + (maxHalfH * envelope * currentAmplitude * (0.35f + 0.65f * wave))

            val left = (i * 2f + 0.5f) * spacing
            barRect.set(left, centerY - halfH, left + barWidth, centerY + halfH)
            canvas.drawRoundRect(barRect, barWidth / 2f, barWidth / 2f, barPaint)
        }
    }

    fun setAmplitude(amp: Float) {
        targetAmplitude = amp.coerceIn(0.1f, 1.0f)
    }

    fun startAnimation() {
        if (animator?.isRunning == true) return
        animator = ValueAnimator.ofFloat(0f, (Math.PI * 20).toFloat()).apply {
            duration = 12000L
            repeatCount = ValueAnimator.INFINITE
            interpolator = LinearInterpolator()
            addUpdateListener {
                phase = it.animatedValue as Float
                invalidate()
            }
            start()
        }
    }

    fun stopAnimation() {
        animator?.cancel()
        animator = null
        targetAmplitude = 0.12f
        invalidate()
    }

    override fun onDetachedFromWindow() {
        stopAnimation()
        super.onDetachedFromWindow()
    }
}
""",

    # --------------------------------------------------------------------------
    # 13. PROXY & TRIGGER ACTIVITIES (CONTROL CENTER, FILE PICKER, AUDIO, EXTERNAL)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/FloaminiTileService.kt": r"""package com.example.floatinggeminiai

import android.app.PendingIntent
import android.content.Intent
import android.os.Build
import android.service.quicksettings.Tile
import android.service.quicksettings.TileService

class FloaminiTileService : TileService() {

    override fun onStartListening() {
        super.onStartListening()
        qsTile?.apply {
            state = Tile.STATE_ACTIVE
            label = "Floamini AI"
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                subtitle = "Panggil Siri"
            }
            updateTile()
        }
    }

    override fun onClick() {
        super.onClick()
        val triggerIntent = Intent(this, SiriTriggerActivity::class.java).apply {
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            val pendingIntent = PendingIntent.getActivity(
                this,
                2026,
                triggerIntent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
            startActivityAndCollapse(pendingIntent)
        } else {
            @Suppress("DEPRECATION")
            startActivityAndCollapse(triggerIntent)
        }
    }
}
""",

    "app/src/main/java/com/example/floatinggeminiai/SiriTriggerActivity.kt": r"""package com.example.floatinggeminiai

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Toast

class SiriTriggerActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        if (!Settings.canDrawOverlays(this)) {
            Toast.makeText(this, "Izinkan Floamini tampil di atas layar dulu", Toast.LENGTH_LONG).show()
            startActivity(Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:$packageName")
            ).apply { addFlags(Intent.FLAG_ACTIVITY_NEW_TASK) })
            finish()
            return
        }

        val serviceIntent = Intent(this, FloatingAssistantService::class.java).apply {
            action = FloatingAssistantService.ACTION_TRIGGER_SIRI
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(serviceIntent)
        } else {
            startService(serviceIntent)
        }
        finish()
    }
}
""",

    "app/src/main/java/com/example/floatinggeminiai/ScreenCapturePermissionActivity.kt": r"""package com.example.floatinggeminiai

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.media.projection.MediaProjectionManager
import android.os.Bundle

class ScreenCapturePermissionActivity : Activity() {

    private val REQUEST_CODE_SCREEN_CAPTURE = 1001

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val projectionManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        startActivityForResult(projectionManager.createScreenCaptureIntent(), REQUEST_CODE_SCREEN_CAPTURE)
    }

    @Deprecated("Deprecated in Java")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_CODE_SCREEN_CAPTURE) {
            val serviceIntent = Intent(this, FloatingAssistantService::class.java).apply {
                action = FloatingAssistantService.ACTION_SCREEN_CAPTURE_RESULT
                putExtra("resultCode", resultCode)
                putExtra("data", data)
            }
            startService(serviceIntent)
        }
        finish()
    }
}
""",

    "app/src/main/java/com/example/floatinggeminiai/FilePickerProxyActivity.kt": r"""package com.example.floatinggeminiai

import android.app.Activity
import android.content.Intent
import android.os.Bundle

class FilePickerProxyActivity : Activity() {

    private val REQ_PICK_ATTACHMENT = 3001

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val pickerIntent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "*/*"
            putExtra(
                Intent.EXTRA_MIME_TYPES,
                arrayOf("image/*", "application/pdf", "text/*")
            )
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        startActivityForResult(pickerIntent, REQ_PICK_ATTACHMENT)
    }

    @Deprecated("Deprecated in Java")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQ_PICK_ATTACHMENT && resultCode == Activity.RESULT_OK && data?.data != null) {
            val uri = data.data!!
            try {
                contentResolver.takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION)
            } catch (_: Exception) {}

            val serviceIntent = Intent(this, FloatingAssistantService::class.java).apply {
                action = FloatingAssistantService.ACTION_ATTACH_URI
                putExtra("uri_string", uri.toString())
            }
            startService(serviceIntent)
        }
        finish()
    }
}
""",

    "app/src/main/java/com/example/floatinggeminiai/AudioPermissionProxyActivity.kt": r"""package com.example.floatinggeminiai

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Toast

class AudioPermissionProxyActivity : Activity() {

    private val REQ_RECORD_AUDIO = 4001

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
            notifyServiceReady()
            finish()
        } else {
            requestPermissions(arrayOf(Manifest.permission.RECORD_AUDIO), REQ_RECORD_AUDIO)
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQ_RECORD_AUDIO && grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            notifyServiceReady()
        } else {
            Toast.makeText(this, "Izin mikrofon diperlukan untuk Voice Chat", Toast.LENGTH_SHORT).show()
        }
        finish()
    }

    private fun notifyServiceReady() {
        startService(Intent(this, FloatingAssistantService::class.java).apply {
            action = FloatingAssistantService.ACTION_AUDIO_PERMISSION_GRANTED
        })
    }
}
""",

    "app/src/main/java/com/example/floatinggeminiai/ExternalTriggerActivity.kt": r"""package com.example.floatinggeminiai

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Toast

class ExternalTriggerActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        if (!Settings.canDrawOverlays(this)) {
            Toast.makeText(this, "Aktifkan izin overlay Floamini terlebih dahulu", Toast.LENGTH_LONG).show()
            startActivity(Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:$packageName")
            ).apply { addFlags(Intent.FLAG_ACTIVITY_NEW_TASK) })
            finish()
            return
        }

        val serviceIntent = Intent(this, FloatingAssistantService::class.java).apply {
            action = FloatingAssistantService.ACTION_EXTERNAL_CONTEXT
        }

        when (intent?.action) {
            Intent.ACTION_PROCESS_TEXT -> {
                val selectedText = intent.getCharSequenceExtra(Intent.EXTRA_PROCESS_TEXT)?.toString() ?: ""
                serviceIntent.putExtra("shared_text", selectedText)
                serviceIntent.putExtra("source_mode", "selection")
            }
            Intent.ACTION_SEND -> {
                val sharedText = intent.getStringExtra(Intent.EXTRA_TEXT) ?: ""
                val streamUri: Uri? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                    intent.getParcelableExtra(Intent.EXTRA_STREAM, Uri::class.java)
                } else {
                    @Suppress("DEPRECATION")
                    intent.getParcelableExtra(Intent.EXTRA_STREAM)
                }
                serviceIntent.putExtra("shared_text", sharedText)
                if (streamUri != null) {
                    serviceIntent.putExtra("uri_string", streamUri.toString())
                }
                serviceIntent.putExtra("source_mode", "share")
            }
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(serviceIntent)
        } else {
            startService(serviceIntent)
        }
        finish()
    }
}
""",

    # --------------------------------------------------------------------------
    # 14. LAYOUT FIRST WELCOME SCREEN
    # --------------------------------------------------------------------------
    "app/src/main/res/layout/activity_welcome.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/bg_screen"
    android:fillViewport="true">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="20dp">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:gravity="center"
            android:paddingVertical="16dp">

            <FrameLayout
                android:layout_width="72dp"
                android:layout_height="72dp"
                android:background="@drawable/bg_dynamic_island">

                <ImageView
                    android:layout_width="34dp"
                    android:layout_height="34dp"
                    android:layout_gravity="center"
                    android:src="@drawable/ic_sparkle"
                    app:tint="#38BDF8" />
            </FrameLayout>

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="12dp"
                android:paddingHorizontal="12dp"
                android:paddingVertical="4dp"
                android:background="@drawable/bg_badge_pill"
                android:text="FLOAMINI OS • MULTI-AI &amp; LIQUID GLASS"
                android:textSize="10sp"
                android:textStyle="bold"
                android:textColor="@color/accent_primary" />

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="10dp"
                android:text="Selamat Datang di Floamini"
                android:textSize="24sp"
                android:textStyle="bold"
                android:textColor="@color/text_primary"
                android:gravity="center" />

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="6dp"
                android:text="Asisten AI tingkat sistem operasi dengan 11 AI Provider, Streaming SSE, Voice Chat, PDF Vision, Dynamic Island, dan Siri Mode."
                android:textSize="13sp"
                android:lineHeight="19dp"
                android:textColor="@color/text_secondary"
                android:gravity="center" />
        </LinearLayout>

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_liquid_glass_card"
            android:padding="18dp"
            android:layout_marginBottom="16dp">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Setup Cepat API Key (Encrypted AES-256)"
                android:textSize="16sp"
                android:textStyle="bold"
                android:textColor="#F8FAFC" />

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="8dp"
                android:text="1. Pilih provider utama Anda (Google Gemini gratis di Google AI Studio, atau OpenAI, Claude, DeepSeek, Grok, Groq, OpenRouter, Mistral, Qwen, Perplexity).\n2. Tempel API Key pada kolom di bawah dan tekan Tes Koneksi."
                android:textSize="12.5sp"
                android:lineHeight="18.5dp"
                android:textColor="#CBD5E1" />

            <Spinner
                android:id="@+id/spWelcomeProvider"
                android:layout_width="match_parent"
                android:layout_height="44dp"
                android:layout_marginTop="12dp"
                android:background="@drawable/bg_input_glass"
                android:paddingHorizontal="12dp" />

            <Button
                android:id="@+id/btnOpenAiStudio"
                android:layout_width="match_parent"
                android:layout_height="44dp"
                android:layout_marginTop="10dp"
                android:text="Buka Portal API Key Provider ↗"
                android:textSize="12.5sp"
                android:textStyle="bold"
                android:backgroundTint="#1E293B"
                android:textColor="#38BDF8" />

            <com.google.android.material.textfield.TextInputLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="10dp"
                android:hint="Tempel API Key di sini"
                app:boxBackgroundColor="#0B111E"
                app:boxStrokeColor="#38BDF8"
                app:hintTextColor="#38BDF8"
                app:endIconMode="password_toggle"
                style="@style/Widget.Material3.TextInputLayout.OutlinedBox">

                <com.google.android.material.textfield.TextInputEditText
                    android:id="@+id/etWelcomeApiKey"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:textColor="#F8FAFC"
                    android:textSize="13sp"
                    android:inputType="textPassword" />
            </com.google.android.material.textfield.TextInputLayout>

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:gravity="center_vertical"
                android:layout_marginTop="10dp">

                <Button
                    android:id="@+id/btnTestTokenWelcome"
                    android:layout_width="wrap_content"
                    android:layout_height="40dp"
                    android:text="Tes Koneksi"
                    android:textSize="12sp"
                    android:textStyle="bold"
                    android:backgroundTint="#0284C7"
                    android:textColor="#FFFFFF" />

                <TextView
                    android:id="@+id/tvTokenTestResult"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:layout_marginStart="12dp"
                    android:text="Belum diuji"
                    android:textSize="12sp"
                    android:textColor="#94A3B8" />
            </LinearLayout>
        </LinearLayout>

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_liquid_glass_card"
            android:padding="18dp"
            android:layout_marginBottom="16dp">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Privasi &amp; Kemampuan OS-Level"
                android:textSize="15sp"
                android:textStyle="bold"
                android:textColor="#F8FAFC" />

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="8dp"
                android:text="• Zero Background Spying: Floamini tidak pernah membaca layar atau clipboard secara diam-diam tanpa tindakan Anda.\n• Seleksi Teks &amp; Share: Blok teks di aplikasi mana pun lalu pilih Tanya Floamini AI, atau bagikan PDF/Gambar langsung ke Floamini.\n• Mode Siri Control Center: Panggil aura Siri dari panel Quick Settings HP Anda kapan saja."
                android:textSize="12sp"
                android:lineHeight="18dp"
                android:textColor="#CBD5E1" />
        </LinearLayout>

        <Button
            android:id="@+id/btnContinueToFloamini"
            android:layout_width="match_parent"
            android:layout_height="54dp"
            android:text="Masuk ke Dashboard Floamini"
            android:textStyle="bold"
            android:textSize="15sp"
            android:backgroundTint="#38BDF8"
            android:textColor="#04070F"
            android:layout_marginBottom="24dp" />

    </LinearLayout>
</ScrollView>
""",

    # --------------------------------------------------------------------------
    # 15. LAYOUT SETTINGS DASHBOARD (ALL 10 REQUIRED SETTINGS SECTIONS)
    # --------------------------------------------------------------------------
    "app/src/main/res/layout/activity_main.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/bg_screen"
    android:fillViewport="true">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="18dp">

        <!-- HEADER -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:layout_marginBottom="16dp">

            <FrameLayout
                android:layout_width="46dp"
                android:layout_height="46dp"
                android:background="@drawable/bg_dynamic_island">

                <ImageView
                    android:layout_width="22dp"
                    android:layout_height="22dp"
                    android:layout_gravity="center"
                    android:src="@drawable/ic_sparkle"
                    app:tint="#38BDF8" />
            </FrameLayout>

            <LinearLayout
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:layout_marginStart="12dp"
                android:orientation="vertical">

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Floamini OS"
                    android:textSize="23sp"
                    android:textStyle="bold"
                    android:textColor="@color/text_primary" />

                <TextView
                    android:id="@+id/tvAppVersionInfo"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="11 AI Providers • Liquid Glass • Siri Aura"
                    android:textSize="11.5sp"
                    android:textColor="@color/text_secondary" />
            </LinearLayout>

            <Button
                android:id="@+id/btnOpenWelcomeGuide"
                android:layout_width="wrap_content"
                android:layout_height="38dp"
                android:text="Panduan"
                android:textSize="12sp"
                android:textColor="@color/accent_primary"
                style="@style/Widget.Material3.Button.OutlinedButton" />
        </LinearLayout>

        <!-- 1. FLOATING WINDOW & CONTROL CENTER -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="1. FLOATING WINDOW &amp; CONTROL CENTER"
            android:textSize="11sp"
            android:textStyle="bold"
            android:letterSpacing="0.06"
            android:textColor="@color/text_secondary"
            android:layout_marginStart="6dp"
            android:layout_marginBottom="6dp" />

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_liquid_glass_card"
            android:padding="16dp"
            android:layout_marginBottom="16dp">

            <Button
                android:id="@+id/btnStartOverlay"
                android:layout_width="match_parent"
                android:layout_height="52dp"
                android:text="Aktifkan Floamini Assistant"
                android:textStyle="bold"
                android:textSize="14sp"
                app:icon="@drawable/ic_dynamic_island"
                app:iconGravity="textStart"
                app:iconTint="#04070F"
                android:backgroundTint="#38BDF8"
                android:textColor="#04070F" />

            <Button
                android:id="@+id/btnAddControlCenterTile"
                android:layout_width="match_parent"
                android:layout_height="44dp"
                android:layout_marginTop="10dp"
                android:text="Tambah Tombol ke Control Center (Siri Mode)"
                android:textSize="12sp"
                android:textStyle="bold"
                app:icon="@drawable/ic_siri_orb"
                app:iconSize="17dp"
                app:iconGravity="textStart"
                app:iconTint="#C084FC"
                android:backgroundTint="#1E1B4B"
                android:textColor="#E9D5FF" />

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginTop="10dp">

                <Button
                    android:id="@+id/btnStopOverlay"
                    android:layout_width="0dp"
                    android:layout_height="42dp"
                    android:layout_weight="1"
                    android:text="Hentikan"
                    android:textSize="12sp"
                    android:textColor="#CBD5E1"
                    app:strokeColor="#334155"
                    style="@style/Widget.Material3.Button.OutlinedButton" />

                <Button
                    android:id="@+id/btnQuickForceStopMain"
                    android:layout_width="0dp"
                    android:layout_height="42dp"
                    android:layout_weight="1.15"
                    android:layout_marginStart="10dp"
                    android:text="Quick Force Stop"
                    android:textSize="12sp"
                    android:textStyle="bold"
                    app:icon="@drawable/ic_power_stop"
                    app:iconSize="16dp"
                    app:iconTint="#FCA5A5"
                    android:backgroundTint="#450A0A"
                    android:textColor="#FCA5A5" />
            </LinearLayout>

            <RadioGroup
                android:id="@+id/rgOverlayStyle"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:layout_marginTop="12dp">

                <RadioButton
                    android:id="@+id/rbStyleDynamicIsland"
                    android:layout_width="match_parent"
                    android:layout_height="34dp"
                    android:text="Dynamic Island (Pil Melayang Atas)"
                    android:textSize="12.5sp"
                    android:textColor="#F8FAFC"
                    android:checked="true" />

                <RadioButton
                    android:id="@+id/rbStyleSiriMode"
                    android:layout_width="match_parent"
                    android:layout_height="34dp"
                    android:text="Mode Siri (Tersembunyi, Panggil via Control Center)"
                    android:textSize="12.5sp"
                    android:textColor="#E9D5FF" />

                <RadioButton
                    android:id="@+id/rbStyleXiaomiEdge"
                    android:layout_width="match_parent"
                    android:layout_height="34dp"
                    android:text="Xiaomi Edge Pill (Garis Tipis Tepi Layar)"
                    android:textSize="12.5sp"
                    android:textColor="#F8FAFC" />

                <RadioButton
                    android:id="@+id/rbStyleClassicBubble"
                    android:layout_width="match_parent"
                    android:layout_height="34dp"
                    android:text="Classic Bubble (Gelembung Bebas)"
                    android:textSize="12.5sp"
                    android:textColor="#F8FAFC" />
            </RadioGroup>

            <RadioGroup
                android:id="@+id/rgPillAppearance"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginTop="6dp">

                <RadioButton
                    android:id="@+id/rbPillStandard"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="Pil Lengkap"
                    android:textSize="11.5sp"
                    android:textColor="#E2E8F0"
                    android:checked="true" />

                <RadioButton
                    android:id="@+id/rbPillPolos"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="Polos Hitam"
                    android:textSize="11.5sp"
                    android:textColor="#E2E8F0" />

                <RadioButton
                    android:id="@+id/rbPillMinimal"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="Ikon Saja"
                    android:textSize="11.5sp"
                    android:textColor="#E2E8F0" />
            </RadioGroup>

            <com.google.android.material.switchmaterial.SwitchMaterial
                android:id="@+id/swAutoHidePill"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Auto-Hide Pil (Memudar Setelah 3 Detik Diam)"
                android:textColor="#E2E8F0"
                android:textSize="12sp" />

            <com.google.android.material.switchmaterial.SwitchMaterial
                android:id="@+id/swSmartFreeze"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Auto Smart Freeze (Hemat RAM &amp; Baterai Saat Idle)"
                android:textColor="#34D399"
                android:textSize="12sp"
                android:checked="true" />

            <com.google.android.material.switchmaterial.SwitchMaterial
                android:id="@+id/swTapOutsideClose"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Ketuk di Luar Jendela untuk Menutup"
                android:textColor="#E2E8F0"
                android:textSize="12sp"
                android:checked="true" />

            <TextView
                android:id="@+id/tvIslandWidthLabel"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="6dp"
                android:text="Lebar Pil Dynamic Island: 164dp"
                android:textSize="11.5sp"
                android:textColor="#CBD5E1" />

            <SeekBar
                android:id="@+id/sbIslandWidth"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:max="130"
                android:progress="54" />

            <TextView
                android:id="@+id/tvIslandPosYLabel"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Posisi Vertikal Atas (Y): 12dp"
                android:textSize="11.5sp"
                android:textColor="#CBD5E1" />

            <SeekBar
                android:id="@+id/sbIslandPosY"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:max="70"
                android:progress="12" />

            <TextView
                android:id="@+id/tvIslandOffsetXLabel"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Geser Horizontal Kamera (X): 0dp"
                android:textSize="11.5sp"
                android:textColor="#CBD5E1" />

            <SeekBar
                android:id="@+id/sbIslandOffsetX"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:max="160"
                android:progress="80" />
        </LinearLayout>

        <!-- 2. MULTI-AI PROVIDERS, API KEYS & MODEL MANAGER -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="2. AI PROVIDERS, API KEYS &amp; MODEL MANAGER (11 ENGINES)"
            android:textSize="11sp"
            android:textStyle="bold"
            android:letterSpacing="0.06"
            android:textColor="@color/text_secondary"
            android:layout_marginStart="6dp"
            android:layout_marginBottom="6dp" />

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_liquid_glass_card"
            android:padding="16dp"
            android:layout_marginBottom="16dp">

            <com.google.android.material.switchmaterial.SwitchMaterial
                android:id="@+id/swAutoRouter"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="AI Auto-Router (Pilih Provider Terbaik Otomatis)"
                android:textColor="#38BDF8"
                android:textSize="12.5sp" />

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="8dp"
                android:text="Pilih Provider untuk Dikonfigurasi / Dijadikan Aktif:"
                android:textSize="12sp"
                android:textColor="#94A3B8" />

            <Spinner
                android:id="@+id/spProviderSelector"
                android:layout_width="match_parent"
                android:layout_height="44dp"
                android:layout_marginTop="6dp"
                android:background="@drawable/bg_input_glass"
                android:paddingHorizontal="12dp" />

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:gravity="center_vertical"
                android:layout_marginTop="10dp">

                <TextView
                    android:id="@+id/tvProviderKeyStatus"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="Status Key: Belum diisi"
                    android:textSize="12sp"
                    android:textColor="#FBBF24" />

                <TextView
                    android:id="@+id/tvOpenProviderDocs"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Dapatkan Key ↗"
                    android:textSize="12sp"
                    android:textStyle="bold"
                    android:textColor="#38BDF8" />
            </LinearLayout>

            <com.google.android.material.textfield.TextInputLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="8dp"
                android:hint="API Key Provider (Terenkripsi AES-256)"
                app:boxBackgroundColor="#0B111E"
                app:boxStrokeColor="#38BDF8"
                app:hintTextColor="#38BDF8"
                app:endIconMode="password_toggle"
                style="@style/Widget.Material3.TextInputLayout.OutlinedBox">

                <com.google.android.material.textfield.TextInputEditText
                    android:id="@+id/etProviderApiKey"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:textColor="#F8FAFC"
                    android:textSize="13sp"
                    android:inputType="textPassword" />
            </com.google.android.material.textfield.TextInputLayout>

            <com.google.android.material.textfield.TextInputLayout
                android:id="@+id/tilCustomBaseUrl"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="8dp"
                android:hint="Custom Base URL (Contoh: https://api.openai.com/v1)"
                app:boxBackgroundColor="#0B111E"
                app:boxStrokeColor="#38BDF8"
                app:hintTextColor="#38BDF8"
                android:visibility="gone"
                style="@style/Widget.Material3.TextInputLayout.OutlinedBox">

                <com.google.android.material.textfield.TextInputEditText
                    android:id="@+id/etCustomBaseUrl"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:textColor="#F8FAFC"
                    android:textSize="13sp"
                    android:inputType="textUri" />
            </com.google.android.material.textfield.TextInputLayout>

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="10dp"
                android:text="Model Preset atau Ketik Model ID Kustom:"
                android:textSize="12sp"
                android:textColor="#94A3B8" />

            <Spinner
                android:id="@+id/spModelPresetSelector"
                android:layout_width="match_parent"
                android:layout_height="42dp"
                android:layout_marginTop="4dp"
                android:background="@drawable/bg_input_glass"
                android:paddingHorizontal="12dp" />

            <com.google.android.material.textfield.TextInputLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="8dp"
                android:hint="Model ID Aktif"
                app:boxBackgroundColor="#0B111E"
                app:boxStrokeColor="#38BDF8"
                app:hintTextColor="#38BDF8"
                style="@style/Widget.Material3.TextInputLayout.OutlinedBox">

                <com.google.android.material.textfield.TextInputEditText
                    android:id="@+id/etActiveModelId"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:textColor="#F8FAFC"
                    android:textSize="13sp"
                    android:inputType="text" />
            </com.google.android.material.textfield.TextInputLayout>

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginTop="10dp">

                <Button
                    android:id="@+id/btnSaveProviderConfig"
                    android:layout_width="0dp"
                    android:layout_height="42dp"
                    android:layout_weight="1"
                    android:text="Simpan Provider"
                    android:textSize="12sp"
                    android:textStyle="bold"
                    android:backgroundTint="#0284C7"
                    android:textColor="#FFFFFF" />

                <Button
                    android:id="@+id/btnTestProviderConnection"
                    android:layout_width="0dp"
                    android:layout_height="42dp"
                    android:layout_weight="1"
                    android:layout_marginStart="8dp"
                    android:text="Tes Koneksi"
                    android:textSize="12sp"
                    android:textColor="#38BDF8"
                    app:strokeColor="#38BDF8"
                    style="@style/Widget.Material3.Button.OutlinedButton" />
            </LinearLayout>

            <TextView
                android:id="@+id/tvProviderTestOutput"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="6dp"
                android:text="Siap menguji koneksi provider"
                android:textSize="11.5sp"
                android:textColor="#94A3B8" />
        </LinearLayout>

        <!-- 3. APPEARANCE, THEME & ANIMATION SETTINGS -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="3. APPEARANCE, LIQUID GLASS &amp; ANIMATION"
            android:textSize="11sp"
            android:textStyle="bold"
            android:letterSpacing="0.06"
            android:textColor="@color/text_secondary"
            android:layout_marginStart="6dp"
            android:layout_marginBottom="6dp" />

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_liquid_glass_card"
            android:padding="16dp"
            android:layout_marginBottom="16dp">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Tema Aplikasi (Adaptive Theme)"
                android:textSize="12.5sp"
                android:textStyle="bold"
                android:textColor="#F8FAFC" />

            <RadioGroup
                android:id="@+id/rgAppTheme"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginTop="4dp">

                <RadioButton
                    android:id="@+id/rbThemeSystem"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="Sistem"
                    android:textSize="12sp"
                    android:textColor="#E2E8F0" />

                <RadioButton
                    android:id="@+id/rbThemeDark"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="Dark Glass"
                    android:textSize="12sp"
                    android:textColor="#E2E8F0"
                    android:checked="true" />

                <RadioButton
                    android:id="@+id/rbThemeLight"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="Light Glass"
                    android:textSize="12sp"
                    android:textColor="#E2E8F0" />
            </RadioGroup>

            <com.google.android.material.switchmaterial.SwitchMaterial
                android:id="@+id/swLiquidBlur"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Dynamic Real-Time Window Blur"
                android:textColor="#E2E8F0"
                android:textSize="12sp"
                android:checked="true" />

            <com.google.android.material.switchmaterial.SwitchMaterial
                android:id="@+id/swHapticFeedback"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Haptic Engine Feedback"
                android:textColor="#E2E8F0"
                android:textSize="12sp"
                android:checked="true" />

            <TextView
                android:id="@+id/tvOpacityLabel"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="6dp"
                android:text="Transparansi Liquid Glass: 84%"
                android:textSize="11.5sp"
                android:textColor="#CBD5E1" />

            <SeekBar
                android:id="@+id/sbOpacity"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:max="55"
                android:progress="39" />

            <TextView
                android:id="@+id/tvAnimSpeedLabel"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Kecepatan Spring Animation: 1.0x"
                android:textSize="11.5sp"
                android:textColor="#CBD5E1" />

            <SeekBar
                android:id="@+id/sbAnimSpeed"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:max="10"
                android:progress="5" />
        </LinearLayout>

        <!-- 4. VOICE SYSTEM, PERSONA & CUSTOM SYSTEM INSTRUCTION -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="4. VOICE SYSTEM &amp; AI PERSONALITY"
            android:textSize="11sp"
            android:textStyle="bold"
            android:letterSpacing="0.06"
            android:textColor="@color/text_secondary"
            android:layout_marginStart="6dp"
            android:layout_marginBottom="6dp" />

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_liquid_glass_card"
            android:padding="16dp"
            android:layout_marginBottom="16dp">

            <com.google.android.material.switchmaterial.SwitchMaterial
                android:id="@+id/swAutoSpeakTts"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Auto-Speak Balasan AI di Mode Voice Chat"
                android:textColor="#E2E8F0"
                android:textSize="12sp"
                android:checked="true" />

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="6dp"
                android:text="Pilih Suara Text-to-Speech (TTS):"
                android:textSize="12sp"
                android:textColor="#94A3B8" />

            <Spinner
                android:id="@+id/spTtsVoiceSelector"
                android:layout_width="match_parent"
                android:layout_height="42dp"
                android:layout_marginTop="4dp"
                android:background="@drawable/bg_input_glass"
                android:paddingHorizontal="12dp" />

            <RadioGroup
                android:id="@+id/rgPersona"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginTop="10dp">

                <RadioButton
                    android:id="@+id/rbAsik"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="Asik"
                    android:textSize="12sp"
                    android:textColor="#E2E8F0"
                    android:checked="true" />

                <RadioButton
                    android:id="@+id/rbRingkas"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="Singkat"
                    android:textSize="12sp"
                    android:textColor="#E2E8F0" />

                <RadioButton
                    android:id="@+id/rbDetail"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="Detail"
                    android:textSize="12sp"
                    android:textColor="#E2E8F0" />

                <RadioButton
                    android:id="@+id/rbTeknis"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="Teknis"
                    android:textSize="12sp"
                    android:textColor="#E2E8F0" />
            </RadioGroup>

            <com.google.android.material.textfield.TextInputLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="8dp"
                android:hint="Custom System Instruction (Opsional)"
                app:boxBackgroundColor="#0B111E"
                app:boxStrokeColor="#38BDF8"
                app:hintTextColor="#38BDF8"
                style="@style/Widget.Material3.TextInputLayout.OutlinedBox">

                <com.google.android.material.textfield.TextInputEditText
                    android:id="@+id/etCustomSystemInstruction"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:textColor="#F8FAFC"
                    android:textSize="12.5sp"
                    android:maxLines="3" />
            </com.google.android.material.textfield.TextInputLayout>
        </LinearLayout>

        <!-- 5. PRIVACY, DATA MANAGEMENT & USAGE STATISTICS -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="5. PRIVACY, DATA MANAGEMENT &amp; USAGE STATISTICS"
            android:textSize="11sp"
            android:textStyle="bold"
            android:letterSpacing="0.06"
            android:textColor="@color/text_secondary"
            android:layout_marginStart="6dp"
            android:layout_marginBottom="6dp" />

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_liquid_glass_card"
            android:padding="16dp"
            android:layout_marginBottom="16dp">

            <TextView
                android:id="@+id/tvUsageStatistics"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Memuat statistik penggunaan..."
                android:textSize="12sp"
                android:lineHeight="18dp"
                android:textColor="#CBD5E1" />

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginTop="12dp">

                <Button
                    android:id="@+id/btnClearAllHistoryMain"
                    android:layout_width="0dp"
                    android:layout_height="40dp"
                    android:layout_weight="1"
                    android:text="Hapus Semua Chat"
                    android:textSize="11.5sp"
                    android:textColor="#FBBF24"
                    app:strokeColor="#475569"
                    style="@style/Widget.Material3.Button.OutlinedButton" />

                <Button
                    android:id="@+id/btnResetUsageStats"
                    android:layout_width="0dp"
                    android:layout_height="40dp"
                    android:layout_weight="1"
                    android:layout_marginStart="8dp"
                    android:text="Reset Statistik"
                    android:textSize="11.5sp"
                    android:textColor="#94A3B8"
                    app:strokeColor="#475569"
                    style="@style/Widget.Material3.Button.OutlinedButton" />
            </LinearLayout>

            <Button
                android:id="@+id/btnWipeVaultKeys"
                android:layout_width="match_parent"
                android:layout_height="40dp"
                android:layout_marginTop="8dp"
                android:text="Hapus Seluruh API Keys dari Vault Terenkripsi"
                android:textSize="11.5sp"
                android:textColor="#FCA5A5"
                app:strokeColor="#7F1D1D"
                style="@style/Widget.Material3.Button.OutlinedButton" />
        </LinearLayout>

        <Button
            android:id="@+id/btnSaveAllSettings"
            android:layout_width="match_parent"
            android:layout_height="52dp"
            android:text="Simpan &amp; Terapkan Semua Pengaturan"
            android:textStyle="bold"
            android:backgroundTint="#2563EB"
            android:textColor="#FFFFFF"
            android:layout_marginBottom="24dp" />

    </LinearLayout>
</ScrollView>
""",

    # --------------------------------------------------------------------------
    # 16. LAYOUT OVERLAY FLOATING ASSISTANT (LIQUID GLASS + MULTI-AI + VOICE + TOOLS)
    # --------------------------------------------------------------------------
    "app/src/main/res/layout/layout_floating_assistant.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content">

    <!-- 1A. DYNAMIC ISLAND PILL -->
    <LinearLayout
        android:id="@+id/dynamicIslandView"
        android:layout_width="164dp"
        android:layout_height="34dp"
        android:orientation="horizontal"
        android:gravity="center_vertical"
        android:paddingHorizontal="12dp"
        android:background="@drawable/bg_dynamic_island"
        android:elevation="16dp">

        <ImageView
            android:id="@+id/ivIslandSparkle"
            android:layout_width="15dp"
            android:layout_height="15dp"
            android:src="@drawable/ic_sparkle"
            app:tint="#38BDF8" />

        <TextView
            android:id="@+id/tvIslandLabel"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:gravity="center"
            android:text="Floamini"
            android:textSize="11.5sp"
            android:textStyle="bold"
            android:textColor="#F8FAFC"
            android:singleLine="true" />

        <View
            android:id="@+id/viewIslandPulseDot"
            android:layout_width="7dp"
            android:layout_height="7dp"
            android:background="@drawable/bg_island_pulse_dot" />
    </LinearLayout>

    <!-- 1B. CLASSIC FLOATING BUBBLE -->
    <FrameLayout
        android:id="@+id/bubbleView"
        android:layout_width="54dp"
        android:layout_height="54dp"
        android:background="@drawable/bg_bubble"
        android:elevation="14dp"
        android:visibility="gone">

        <ImageView
            android:layout_width="25dp"
            android:layout_height="25dp"
            android:layout_gravity="center"
            android:src="@drawable/ic_sparkle"
            app:tint="#38BDF8" />
    </FrameLayout>

    <!-- 1C. XIAOMI EDGE PILL -->
    <FrameLayout
        android:id="@+id/xiaomiEdgeView"
        android:layout_width="18dp"
        android:layout_height="72dp"
        android:background="@drawable/bg_xiaomi_edge_left"
        android:elevation="14dp"
        android:visibility="gone">

        <View
            android:layout_width="3dp"
            android:layout_height="36dp"
            android:layout_gravity="center"
            android:background="@drawable/bg_xiaomi_inner_line" />
    </FrameLayout>

    <!-- 2. JENDELA CHAT GENUINE LIQUID GLASS -->
    <LinearLayout
        android:id="@+id/popupChatView"
        android:layout_width="352dp"
        android:layout_height="500dp"
        android:orientation="vertical"
        android:background="@drawable/bg_liquid_glass_window"
        android:elevation="22dp"
        android:visibility="gone">

        <!-- TOP HEADER BAR -->
        <LinearLayout
            android:id="@+id/glassTitleBar"
            android:layout_width="match_parent"
            android:layout_height="46dp"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:paddingHorizontal="10dp"
            android:background="@drawable/bg_liquid_glass_header">

            <!-- Close X -->
            <ImageView
                android:id="@+id/btnCloseWindowX"
                android:layout_width="26dp"
                android:layout_height="26dp"
                android:padding="5dp"
                android:background="@drawable/bg_close_x_btn"
                android:src="@drawable/ic_close_x"
                app:tint="#F8FAFC"
                android:contentDescription="Tutup" />

            <!-- Mini / Full Window Toggle -->
            <ImageView
                android:id="@+id/btnToggleMiniWindow"
                android:layout_width="26dp"
                android:layout_height="26dp"
                android:layout_marginStart="5dp"
                android:padding="5dp"
                android:background="@drawable/bg_close_x_btn"
                android:src="@drawable/ic_minimize"
                app:tint="#FBBF24"
                android:contentDescription="Mini Window" />

            <!-- Active Provider Switcher Pill -->
            <LinearLayout
                android:id="@+id/btnSwitchProviderPill"
                android:layout_width="0dp"
                android:layout_height="28dp"
                android:layout_weight="1"
                android:layout_marginHorizontal="6dp"
                android:paddingHorizontal="8dp"
                android:gravity="center"
                android:background="@drawable/bg_badge_pill"
                android:orientation="horizontal">

                <ImageView
                    android:layout_width="13dp"
                    android:layout_height="13dp"
                    android:src="@drawable/ic_sparkle"
                    app:tint="#38BDF8" />

                <TextView
                    android:id="@+id/tvActiveProviderHeader"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginStart="5dp"
                    android:text="Gemini • 2.5 Flash"
                    android:textSize="11sp"
                    android:textStyle="bold"
                    android:textColor="#F8FAFC"
                    android:singleLine="true" />
            </LinearLayout>

            <!-- Live Screen Share -->
            <ImageView
                android:id="@+id/btnScreenShare"
                android:layout_width="26dp"
                android:layout_height="26dp"
                android:padding="4dp"
                android:src="@drawable/ic_screen_share"
                app:tint="#94A3B8"
                android:contentDescription="Screen Vision" />

            <!-- Smart Tools & History Drawer Toggle -->
            <ImageView
                android:id="@+id/btnToolsDrawer"
                android:layout_width="26dp"
                android:layout_height="26dp"
                android:layout_marginStart="4dp"
                android:padding="4dp"
                android:src="@drawable/ic_grid_tools"
                app:tint="#C084FC"
                android:contentDescription="Smart Tools" />

            <!-- Plus Menu (+) -->
            <ImageView
                android:id="@+id/btnPlusMenu"
                android:layout_width="26dp"
                android:layout_height="26dp"
                android:layout_marginStart="4dp"
                android:padding="4dp"
                android:background="@drawable/bg_plus_btn"
                android:src="@drawable/ic_plus"
                app:tint="#38BDF8"
                android:contentDescription="Menu Plus" />
        </LinearLayout>

        <!-- STATUS BARS (SCREEN SHARE / ATTACHMENT / COMPARE MODE) -->
        <TextView
            android:id="@+id/tvScreenShareStatus"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:background="#330EA5E9"
            android:paddingVertical="3dp"
            android:paddingHorizontal="10dp"
            android:text="Live Screen Vision Aktif"
            android:textSize="10sp"
            android:textColor="#7DD3FC"
            android:gravity="center"
            android:visibility="gone" />

        <LinearLayout
            android:id="@+id/attachmentPreviewBar"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:background="#337C3AED"
            android:paddingHorizontal="10dp"
            android:paddingVertical="4dp"
            android:visibility="gone">

            <TextView
                android:id="@+id/tvAttachmentName"
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:text="Lampiran siap dikirim"
                android:textSize="10.5sp"
                android:textColor="#E9D5FF"
                android:singleLine="true" />

            <TextView
                android:id="@+id/btnRemoveAttachment"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Hapus"
                android:textSize="10.5sp"
                android:textStyle="bold"
                android:textColor="#FCA5A5" />
        </LinearLayout>

        <!-- DRAWER 1: MENU PLUS (+) & 9 QUICK ACTIONS -->
        <LinearLayout
            android:id="@+id/plusMenuDrawer"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="#F00F172A"
            android:padding="10dp"
            android:visibility="gone">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal">

                <LinearLayout
                    android:id="@+id/actionCompareAi"
                    android:layout_width="0dp"
                    android:layout_height="32dp"
                    android:layout_weight="1"
                    android:gravity="center"
                    android:background="@drawable/bg_chip_action"
                    android:orientation="horizontal">

                    <TextView
                        android:id="@+id/tvCompareBadge"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Compare AI: OFF"
                        android:textSize="10.5sp"
                        android:textStyle="bold"
                        android:textColor="#38BDF8" />
                </LinearLayout>

                <LinearLayout
                    android:id="@+id/actionRegenerate"
                    android:layout_width="0dp"
                    android:layout_height="32dp"
                    android:layout_weight="0.85"
                    android:layout_marginStart="5dp"
                    android:gravity="center"
                    android:background="@drawable/bg_chip_action"
                    android:orientation="horizontal">

                    <TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Regenerate"
                        android:textSize="10.5sp"
                        android:textColor="#F8FAFC" />
                </LinearLayout>

                <LinearLayout
                    android:id="@+id/actionCyclePersona"
                    android:layout_width="0dp"
                    android:layout_height="32dp"
                    android:layout_weight="0.75"
                    android:layout_marginStart="5dp"
                    android:gravity="center"
                    android:background="@drawable/bg_chip_action"
                    android:orientation="horizontal">

                    <TextView
                        android:id="@+id/tvCurrentPersonaBadge"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Asik"
                        android:textSize="10.5sp"
                        android:textColor="#C084FC" />
                </LinearLayout>
            </LinearLayout>

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginTop="5dp">

                <LinearLayout
                    android:id="@+id/actionCopyLast"
                    android:layout_width="0dp"
                    android:layout_height="32dp"
                    android:layout_weight="0.8"
                    android:gravity="center"
                    android:background="@drawable/bg_chip_action"
                    android:orientation="horizontal">

                    <TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Salin"
                        android:textSize="10.5sp"
                        android:textColor="#34D399" />
                </LinearLayout>

                <LinearLayout
                    android:id="@+id/actionNewThread"
                    android:layout_width="0dp"
                    android:layout_height="32dp"
                    android:layout_weight="0.9"
                    android:layout_marginStart="5dp"
                    android:gravity="center"
                    android:background="@drawable/bg_chip_action"
                    android:orientation="horizontal">

                    <TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Sesi Baru"
                        android:textSize="10.5sp"
                        android:textColor="#FBBF24" />
                </LinearLayout>

                <LinearLayout
                    android:id="@+id/actionOpenDashboard"
                    android:layout_width="0dp"
                    android:layout_height="32dp"
                    android:layout_weight="0.9"
                    android:layout_marginStart="5dp"
                    android:gravity="center"
                    android:background="@drawable/bg_chip_action"
                    android:orientation="horizontal">

                    <TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Settings"
                        android:textSize="10.5sp"
                        android:textColor="#CBD5E1" />
                </LinearLayout>

                <LinearLayout
                    android:id="@+id/actionQuickForceStop"
                    android:layout_width="0dp"
                    android:layout_height="32dp"
                    android:layout_weight="0.95"
                    android:layout_marginStart="5dp"
                    android:gravity="center"
                    android:background="@drawable/bg_chip_danger"
                    android:orientation="horizontal">

                    <TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Force Stop"
                        android:textSize="10.5sp"
                        android:textStyle="bold"
                        android:textColor="#FCA5A5" />
                </LinearLayout>
            </LinearLayout>

            <!-- 9 QUICK ACTIONS HORIZONTAL SCROLLER -->
            <HorizontalScrollView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="7dp"
                android:scrollbars="none">

                <LinearLayout
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:orientation="horizontal">

                    <TextView
                        android:id="@+id/qaTranslate"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:paddingHorizontal="9dp"
                        android:paddingVertical="5dp"
                        android:background="@drawable/bg_chip_prompt"
                        android:text="Translate"
                        android:textSize="10sp"
                        android:textColor="#38BDF8" />

                    <TextView
                        android:id="@+id/qaSummarize"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginStart="5dp"
                        android:paddingHorizontal="9dp"
                        android:paddingVertical="5dp"
                        android:background="@drawable/bg_chip_prompt"
                        android:text="Summarize"
                        android:textSize="10sp"
                        android:textColor="#E2E8F0" />

                    <TextView
                        android:id="@+id/qaRewrite"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginStart="5dp"
                        android:paddingHorizontal="9dp"
                        android:paddingVertical="5dp"
                        android:background="@drawable/bg_chip_prompt"
                        android:text="Rewrite"
                        android:textSize="10sp"
                        android:textColor="#E2E8F0" />

                    <TextView
                        android:id="@+id/qaExplain"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginStart="5dp"
                        android:paddingHorizontal="9dp"
                        android:paddingVertical="5dp"
                        android:background="@drawable/bg_chip_prompt"
                        android:text="Explain"
                        android:textSize="10sp"
                        android:textColor="#E2E8F0" />

                    <TextView
                        android:id="@+id/qaBrainstorm"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginStart="5dp"
                        android:paddingHorizontal="9dp"
                        android:paddingVertical="5dp"
                        android:background="@drawable/bg_chip_prompt"
                        android:text="Brainstorm"
                        android:textSize="10sp"
                        android:textColor="#E2E8F0" />

                    <TextView
                        android:id="@+id/qaCoding"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginStart="5dp"
                        android:paddingHorizontal="9dp"
                        android:paddingVertical="5dp"
                        android:background="@drawable/bg_chip_prompt"
                        android:text="Coding"
                        android:textSize="10sp"
                        android:textColor="#34D399" />

                    <TextView
                        android:id="@+id/qaGrammar"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginStart="5dp"
                        android:paddingHorizontal="9dp"
                        android:paddingVertical="5dp"
                        android:background="@drawable/bg_chip_prompt"
                        android:text="Grammar"
                        android:textSize="10sp"
                        android:textColor="#E2E8F0" />

                    <TextView
                        android:id="@+id/qaExtractText"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginStart="5dp"
                        android:paddingHorizontal="9dp"
                        android:paddingVertical="5dp"
                        android:background="@drawable/bg_chip_prompt"
                        android:text="Extract Text"
                        android:textSize="10sp"
                        android:textColor="#E2E8F0" />

                    <TextView
                        android:id="@+id/qaAskSelection"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginStart="5dp"
                        android:paddingHorizontal="9dp"
                        android:paddingVertical="5dp"
                        android:background="@drawable/bg_chip_prompt"
                        android:text="Ask Clipboard"
                        android:textSize="10sp"
                        android:textColor="#FBBF24" />
                </LinearLayout>
            </HorizontalScrollView>
        </LinearLayout>

        <!-- DRAWER 2: SMART FLOATING TOOLS (CLIPBOARD, NOTES, CALCULATOR, HISTORY SEARCH) -->
        <LinearLayout
            android:id="@+id/smartToolsDrawer"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="#F00F172A"
            android:padding="10dp"
            android:visibility="gone">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal">

                <Button
                    android:id="@+id/btnToolClipboard"
                    android:layout_width="0dp"
                    android:layout_height="34dp"
                    android:layout_weight="1"
                    android:text="Clipboard"
                    android:textSize="10.5sp"
                    android:backgroundTint="#1E293B"
                    android:textColor="#38BDF8" />

                <Button
                    android:id="@+id/btnToolCalculator"
                    android:layout_width="0dp"
                    android:layout_height="34dp"
                    android:layout_weight="1"
                    android:layout_marginStart="4dp"
                    android:text="Kalkulator"
                    android:textSize="10.5sp"
                    android:backgroundTint="#1E293B"
                    android:textColor="#34D399" />

                <Button
                    android:id="@+id/btnToolNotes"
                    android:layout_width="0dp"
                    android:layout_height="34dp"
                    android:layout_weight="1"
                    android:layout_marginStart="4dp"
                    android:text="Quick Notes"
                    android:textSize="10.5sp"
                    android:backgroundTint="#1E293B"
                    android:textColor="#FBBF24" />

                <Button
                    android:id="@+id/btnToolHistory"
                    android:layout_width="0dp"
                    android:layout_height="34dp"
                    android:layout_weight="1"
                    android:layout_marginStart="4dp"
                    android:text="Riwayat"
                    android:textSize="10.5sp"
                    android:backgroundTint="#1E293B"
                    android:textColor="#C084FC" />
            </LinearLayout>

            <!-- Mini Floating Calculator Panel -->
            <LinearLayout
                android:id="@+id/panelCalculator"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:gravity="center_vertical"
                android:layout_marginTop="8dp"
                android:background="@drawable/bg_input_glass"
                android:padding="6dp"
                android:visibility="gone">

                <EditText
                    android:id="@+id/etCalcExpression"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:hint="Hitung: (125*4)+50"
                    android:textColorHint="#64748B"
                    android:textColor="#F8FAFC"
                    android:textSize="12sp"
                    android:background="@android:color/transparent"
                    android:padding="4dp" />

                <TextView
                    android:id="@+id/tvCalcResult"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginHorizontal="8dp"
                    android:text="= 0"
                    android:textStyle="bold"
                    android:textColor="#34D399"
                    android:textSize="12.5sp" />

                <Button
                    android:id="@+id/btnEvalCalc"
                    android:layout_width="wrap_content"
                    android:layout_height="32dp"
                    android:text="Hitung"
                    android:textSize="10.5sp"
                    android:backgroundTint="#0284C7"
                    android:textColor="#FFFFFF" />
            </LinearLayout>

            <!-- Mini Quick Notes Panel -->
            <LinearLayout
                android:id="@+id/panelQuickNotes"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:layout_marginTop="8dp"
                android:background="@drawable/bg_input_glass"
                android:padding="8dp"
                android:visibility="gone">

                <EditText
                    android:id="@+id/etQuickNotes"
                    android:layout_width="match_parent"
                    android:layout_height="64dp"
                    android:hint="Catatan cepat Anda..."
                    android:textColorHint="#64748B"
                    android:textColor="#F8FAFC"
                    android:textSize="12sp"
                    android:gravity="top"
                    android:background="@android:color/transparent" />

                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:orientation="horizontal"
                    android:gravity="end">

                    <Button
                        android:id="@+id/btnSendNotesToAi"
                        android:layout_width="wrap_content"
                        android:layout_height="30dp"
                        android:text="Tanya AI soal Catatan"
                        android:textSize="10sp"
                        android:backgroundTint="#7C3AED"
                        android:textColor="#FFFFFF" />
                </LinearLayout>
            </LinearLayout>

            <!-- Chat History & Search Panel -->
            <LinearLayout
                android:id="@+id/panelChatHistory"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:layout_marginTop="8dp"
                android:background="@drawable/bg_input_glass"
                android:padding="8dp"
                android:visibility="gone">

                <EditText
                    android:id="@+id/etSearchChat"
                    android:layout_width="match_parent"
                    android:layout_height="34dp"
                    android:hint="Cari riwayat percakapan..."
                    android:textColorHint="#64748B"
                    android:textColor="#F8FAFC"
                    android:textSize="12sp"
                    android:background="@android:color/transparent" />

                <LinearLayout
                    android:id="@+id/historyThreadsList"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:orientation="vertical"
                    android:layout_marginTop="4dp" />
            </LinearLayout>
        </LinearLayout>

        <!-- AREA PERCAKAPAN (STREAMING + COMPARE AI + RICH CODE) -->
        <ScrollView
            android:id="@+id/scrollChat"
            android:layout_width="match_parent"
            android:layout_height="0dp"
            android:layout_weight="1"
            android:padding="10dp">

            <LinearLayout
                android:id="@+id/chatContainer"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical" />
        </ScrollView>

        <!-- VOICE WAVEFORM BAR (STT & TTS LIVE ANIMATION) -->
        <LinearLayout
            android:id="@+id/voiceWaveformBar"
            android:layout_width="match_parent"
            android:layout_height="44dp"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:paddingHorizontal="12dp"
            android:background="#2638BDF8"
            android:visibility="gone">

            <TextView
                android:id="@+id/tvVoiceStatusLabel"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Mendengarkan..."
                android:textSize="11sp"
                android:textStyle="bold"
                android:textColor="#38BDF8" />

            <com.example.floatinggeminiai.ui.VoiceWaveformView
                android:id="@+id/voiceWaveformView"
                android:layout_width="0dp"
                android:layout_height="28dp"
                android:layout_weight="1"
                android:layout_marginHorizontal="10dp" />

            <TextView
                android:id="@+id/btnStopVoiceAction"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Stop"
                android:textSize="11sp"
                android:textStyle="bold"
                android:textColor="#FCA5A5" />
        </LinearLayout>

        <!-- STREAMING / THINKING & STOP GENERATION BAR -->
        <LinearLayout
            android:id="@+id/typingIndicatorRow"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:paddingHorizontal="14dp"
            android:paddingVertical="4dp"
            android:visibility="gone">

            <ImageView
                android:layout_width="12dp"
                android:layout_height="12dp"
                android:src="@drawable/ic_sparkle"
                app:tint="#38BDF8" />

            <TextView
                android:id="@+id/tvThinkingLabel"
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:layout_marginStart="6dp"
                android:text="Streaming respons..."
                android:textSize="11sp"
                android:textColor="#7DD3FC" />

            <TextView
                android:id="@+id/btnStopGeneration"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:paddingHorizontal="8dp"
                android:paddingVertical="2dp"
                android:background="@drawable/bg_chip_danger"
                android:text="Stop"
                android:textSize="10sp"
                android:textStyle="bold"
                android:textColor="#FCA5A5" />
        </LinearLayout>

        <!-- INPUT BAR: ATTACH (PDF/IMG/FILE), MIC (VOICE), PROMPT, SEND, RESIZE -->
        <LinearLayout
            android:id="@+id/bottomInputContainer"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:paddingStart="8dp"
            android:paddingEnd="5dp"
            android:paddingTop="6dp"
            android:paddingBottom="8dp">

            <ImageButton
                android:id="@+id/btnAttachFile"
                android:layout_width="34dp"
                android:layout_height="34dp"
                android:background="@drawable/bg_close_x_btn"
                android:src="@drawable/ic_attach"
                app:tint="#CBD5E1"
                android:contentDescription="Lampirkan PDF atau Gambar" />

            <ImageButton
                android:id="@+id/btnVoiceMic"
                android:layout_width="34dp"
                android:layout_height="34dp"
                android:layout_marginStart="5dp"
                android:background="@drawable/bg_close_x_btn"
                android:src="@drawable/ic_mic"
                app:tint="#38BDF8"
                android:contentDescription="Voice Chat" />

            <EditText
                android:id="@+id/etPrompt"
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:layout_marginStart="6dp"
                android:hint="Tanya AI..."
                android:textColorHint="#94A3B8"
                android:textColor="#F8FAFC"
                android:textSize="13sp"
                android:maxLines="3"
                android:paddingHorizontal="11dp"
                android:paddingVertical="8dp"
                android:background="@drawable/bg_input_glass" />

            <ImageButton
                android:id="@+id/btnSendPrompt"
                android:layout_width="36dp"
                android:layout_height="36dp"
                android:layout_marginStart="6dp"
                android:background="@drawable/bg_send_btn"
                android:src="@drawable/ic_send"
                app:tint="#FFFFFF"
                android:contentDescription="Kirim" />

            <ImageView
                android:id="@+id/btnResizeHandle"
                android:layout_width="20dp"
                android:layout_height="26dp"
                android:layout_marginStart="3dp"
                android:padding="2dp"
                android:src="@drawable/ic_resize_handle"
                app:tint="#64748B"
                android:contentDescription="Resize" />
        </LinearLayout>

    </LinearLayout>
</FrameLayout>
""",

    # --------------------------------------------------------------------------
    # 17. DRAWABLES: LIQUID GLASS & CUSTOM SVG ICONS
    # --------------------------------------------------------------------------
    "app/src/main/res/drawable/bg_dynamic_island.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item>
        <shape android:shape="rectangle">
            <gradient
                android:angle="135"
                android:startColor="#66FFFFFF"
                android:centerColor="#3338BDF8"
                android:endColor="#26FFFFFF" />
            <corners android:radius="100dp" />
        </shape>
    </item>
    <item android:left="1dp" android:top="1dp" android:right="1dp" android:bottom="1dp">
        <shape android:shape="rectangle">
            <solid android:color="#FA020305" />
            <corners android:radius="100dp" />
        </shape>
    </item>
</layer-list>
""",

    "app/src/main/res/drawable/bg_dynamic_island_polos.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#FF000000" />
    <corners android:radius="100dp" />
</shape>
""",

    "app/src/main/res/drawable/bg_island_pulse_dot.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="oval">
    <solid android:color="#34D399" />
</shape>
""",

    "app/src/main/res/drawable/bg_liquid_glass_card.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item>
        <shape android:shape="rectangle">
            <gradient
                android:angle="135"
                android:startColor="#59FFFFFF"
                android:centerColor="#2638BDF8"
                android:endColor="#26E879F9" />
            <corners android:radius="22dp" />
        </shape>
    </item>
    <item android:left="1dp" android:top="1dp" android:right="1dp" android:bottom="1dp">
        <shape android:shape="rectangle">
            <gradient
                android:angle="270"
                android:startColor="#EB141D30"
                android:endColor="#EB0A0F1C" />
            <corners android:radius="21dp" />
        </shape>
    </item>
</layer-list>
""",

    "app/src/main/res/drawable/bg_liquid_glass_window.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item>
        <shape android:shape="rectangle">
            <gradient
                android:angle="135"
                android:startColor="#A6FFFFFF"
                android:centerColor="#597DD3FC"
                android:endColor="#4DC084FC" />
            <corners android:radius="28dp" />
        </shape>
    </item>
    <item android:left="1.4dp" android:top="1.4dp" android:right="1.4dp" android:bottom="1.4dp">
        <shape android:shape="rectangle">
            <gradient
                android:angle="270"
                android:startColor="#D418233A"
                android:centerColor="#C40E1628"
                android:endColor="#D40A101E" />
            <corners android:radius="26.5dp" />
        </shape>
    </item>
</layer-list>
""",

    "app/src/main/res/drawable/bg_liquid_glass_window_share.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item>
        <shape android:shape="rectangle">
            <gradient
                android:angle="135"
                android:startColor="#E638BDF8"
                android:centerColor="#99818CF8"
                android:endColor="#E6E879F9" />
            <corners android:radius="28dp" />
        </shape>
    </item>
    <item android:left="1.8dp" android:top="1.8dp" android:right="1.8dp" android:bottom="1.8dp">
        <shape android:shape="rectangle">
            <gradient
                android:angle="270"
                android:startColor="#D418233A"
                android:centerColor="#C40E1628"
                android:endColor="#D40A101E" />
            <corners android:radius="26dp" />
        </shape>
    </item>
</layer-list>
""",

    "app/src/main/res/drawable/bg_liquid_glass_header.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <gradient
        android:angle="270"
        android:startColor="#52FFFFFF"
        android:endColor="#14FFFFFF" />
    <corners android:topLeftRadius="26.5dp" android:topRightRadius="26.5dp" />
</shape>
""",

    "app/src/main/res/drawable/bg_close_x_btn.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="oval">
    <solid android:color="#2EFFFFFF" />
    <stroke android:width="0.8dp" android:color="#4DFFFFFF" />
</shape>
""",

    "app/src/main/res/drawable/bg_bubble.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="oval">
    <solid android:color="#EB0B111E" />
    <stroke android:width="1.5dp" android:color="#66FFFFFF" />
</shape>
""",

    "app/src/main/res/drawable/bg_xiaomi_edge_left.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#D90B111E" />
    <corners android:topRightRadius="36dp" android:bottomRightRadius="36dp" />
    <stroke android:width="1.2dp" android:color="#80FFFFFF" />
</shape>
""",

    "app/src/main/res/drawable/bg_xiaomi_edge_right.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#D90B111E" />
    <corners android:topLeftRadius="36dp" android:bottomLeftRadius="36dp" />
    <stroke android:width="1.2dp" android:color="#80FFFFFF" />
</shape>
""",

    "app/src/main/res/drawable/bg_xiaomi_inner_line.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#38BDF8" />
    <corners android:radius="2dp" />
</shape>
""",

    "app/src/main/res/drawable/bg_plus_btn.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="oval">
    <solid android:color="#3338BDF8" />
    <stroke android:width="0.8dp" android:color="#597DD3FC" />
</shape>
""",

    "app/src/main/res/drawable/bg_badge_pill.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#2E38BDF8" />
    <corners android:radius="12dp" />
</shape>
""",

    "app/src/main/res/drawable/bg_chip_action.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#B30B111E" />
    <corners android:radius="10dp" />
    <stroke android:width="1dp" android:color="#33FFFFFF" />
</shape>
""",

    "app/src/main/res/drawable/bg_chip_prompt.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#CC17223B" />
    <corners android:radius="13dp" />
    <stroke android:width="1dp" android:color="#4D38BDF8" />
</shape>
""",

    "app/src/main/res/drawable/bg_chip_danger.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#450A0A" />
    <corners android:radius="10dp" />
    <stroke android:width="1dp" android:color="#991B1B" />
</shape>
""",

    "app/src/main/res/drawable/bg_input_glass.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#8C1E293B" />
    <corners android:radius="15dp" />
    <stroke android:width="1dp" android:color="#4DFFFFFF" />
</shape>
""",

    "app/src/main/res/drawable/bg_send_btn.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="oval">
    <solid android:color="#0284C7" />
    <stroke android:width="0.8dp" android:color="#73FFFFFF" />
</shape>
""",

    "app/src/main/res/drawable/bg_chat_user.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <gradient
        android:angle="135"
        android:startColor="#E60284C7"
        android:endColor="#E62563EB" />
    <corners android:topLeftRadius="16dp" android:topRightRadius="16dp" android:bottomLeftRadius="16dp" android:bottomRightRadius="4dp" />
    <stroke android:width="0.8dp" android:color="#59FFFFFF" />
</shape>
""",

    "app/src/main/res/drawable/bg_chat_bot.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#E01A2438" />
    <corners android:topLeftRadius="16dp" android:topRightRadius="16dp" android:bottomRightRadius="16dp" android:bottomLeftRadius="4dp" />
    <stroke android:width="0.8dp" android:color="#3BFFFFFF" />
</shape>
""",

    "app/src/main/res/drawable/ic_sparkle.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M12,2L14.4,9.6L22,12L14.4,14.4L12,22L9.6,14.4L2,12L9.6,9.6L12,2Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_siri_orb.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M12,2C6.48,2 2,6.48 2,12C2,17.52 6.48,22 12,22C17.52,22 22,17.52 22,12C22,6.48 17.52,2 12,2ZM12,18C8.69,18 6,15.31 6,12C6,8.69 8.69,6 12,6C15.31,6 18,8.69 18,12C18,15.31 15.31,18 12,18ZM12,8.5C10.07,8.5 8.5,10.07 8.5,12C8.5,13.93 10.07,15.5 12,15.5C13.93,15.5 15.5,13.93 15.5,12C15.5,10.07 13.93,8.5 12,8.5Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_close_x.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_minimize.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M6,19H18V17H6V19Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_dynamic_island.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M6,8H18C20.21,8 22,9.79 22,12C22,14.21 20.21,16 18,16H6C3.79,16 2,14.21 2,12C2,9.79 3.79,8 6,8ZM17.5,10.5C16.67,10.5 16,11.17 16,12C16,12.83 16.67,13.5 17.5,13.5C18.33,13.5 19,12.83 19,12C19,11.17 18.33,10.5 17.5,10.5Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_plus.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_grid_tools.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M4,8H8V4H4V8ZM10,20H14V16H10V20ZM4,20H8V16H4V20ZM4,14H8V10H4V14ZM10,14H14V10H10V14ZM16,4V8H20V4H16ZM10,8H14V4H10V8ZM16,14H20V10H16V14ZM16,20H20V16H16V20Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_attach.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M16.5,6V17.5C16.5,19.71 14.71,21.5 12.5,21.5C10.29,21.5 8.5,19.71 8.5,17.5V5C8.5,3.62 9.62,2.5 11,2.5C12.38,2.5 13.5,3.62 13.5,5V15.5C13.5,16.05 13.05,16.5 12.5,16.5C11.95,16.5 11.5,16.05 11.5,15.5V6H10V15.5C10,16.88 11.12,18 12.5,18C13.88,18 15,16.88 15,15.5V5C15,2.79 13.21,1 11,1C8.79,1 7,2.79 7,5V17.5C7,20.54 9.46,23 12.5,23C15.54,23 18,20.54 18,17.5V6H16.5Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_mic.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M12,14C13.66,14 14.99,12.66 14.99,11L15,5C15,3.34 13.66,2 12,2C10.34,2 9,3.34 9,5V11C9,12.66 10.34,14 12,14ZM17.3,11C17.3,14 14.76,16.1 12,16.1C9.24,16.1 6.7,14 6.7,11H5C5,14.41 7.72,17.23 11,17.72V21H13V17.72C16.28,17.23 19,14.41 19,11H17.3Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_send.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="20dp"
    android:height="20dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M2.01,21L23,12L2.01,3L2,10L17,12L2,14L2.01,21Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_screen_share.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M20,18C21.1,18 21.99,17.1 21.99,16L22,6C22,4.89 21.1,4 20,4H4C2.89,4 2,4.89 2,6V16C2,17.1 2.89,18 4,18H0V20H24V18H20ZM13,14.47V12.28C10.22,12.28 8.39,13.13 7,15C7.56,12.33 9.11,9.67 13,9.13V7L17,10.73L13,14.47Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_power_stop.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M13,3H11V13H13V3ZM17.83,5.17L16.41,6.59C17.99,7.86 19,9.81 19,12C19,15.87 15.87,19 12,19C8.13,19 5,15.87 5,12C5,9.81 6.01,7.86 7.58,6.58L6.17,5.17C4.23,6.82 3,9.26 3,12C3,16.97 7.03,21 12,21C16.97,21 21,16.97 21,12C21,9.26 19.77,6.82 17.83,5.17Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_resize_handle.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M22,22H20V20H22V22ZM22,18H20V16H22V18ZM18,22H16V20H18V22ZM18,18H16V16H18V18ZM14,22H12V20H14V22ZM22,14H20V12H22V14Z" />
</vector>
""",

    # --------------------------------------------------------------------------
    # 18. WELCOME ACTIVITY (MULTI-PROVIDER SETUP & ENCRYPTED VAULT TESTER)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/WelcomeActivity.kt": r"""package com.example.floatinggeminiai

import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.floatinggeminiai.ai.AiEngineRegistry
import com.example.floatinggeminiai.ai.AiProviderType
import com.example.floatinggeminiai.security.SecureVault
import com.google.android.material.textfield.TextInputEditText
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class WelcomeActivity : AppCompatActivity() {

    private val activityJob = Job()
    private val uiScope = CoroutineScope(Dispatchers.Main + activityJob)
    private lateinit var vault: SecureVault
    private var selectedProvider = AiProviderType.GEMINI

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_welcome)

        vault = SecureVault(this)
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        val fromSettings = intent.getBooleanExtra("from_settings", false)

        val spWelcomeProvider = findViewById<Spinner>(R.id.spWelcomeProvider)
        val btnOpenAiStudio = findViewById<Button>(R.id.btnOpenAiStudio)
        val etWelcomeApiKey = findViewById<TextInputEditText>(R.id.etWelcomeApiKey)
        val btnTestTokenWelcome = findViewById<Button>(R.id.btnTestTokenWelcome)
        val tvTokenTestResult = findViewById<TextView>(R.id.tvTokenTestResult)
        val btnContinueToFloamini = findViewById<Button>(R.id.btnContinueToFloamini)

        val providers = AiProviderType.values().toList()
        val adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_dropdown_item,
            providers.map { "${it.displayName} (${it.defaultModel})" }
        )
        spWelcomeProvider.adapter = adapter
        spWelcomeProvider.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                selectedProvider = providers[position]
                etWelcomeApiKey.setText(vault.getApiKey(selectedProvider))
            }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }

        if (fromSettings) {
            btnContinueToFloamini.text = "Kembali ke Pengaturan Floamini"
        }

        btnOpenAiStudio.setOnClickListener {
            try {
                startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(selectedProvider.docsUrl)))
            } catch (_: Exception) {
                Toast.makeText(this, "Kunjungi ${selectedProvider.docsUrl}", Toast.LENGTH_LONG).show()
            }
        }

        btnTestTokenWelcome.setOnClickListener {
            val token = etWelcomeApiKey.text.toString().trim()
            if (token.isEmpty()) {
                tvTokenTestResult.text = "Masukkan API Key terlebih dahulu"
                tvTokenTestResult.setTextColor(Color.parseColor("#FBBF24"))
                return@setOnClickListener
            }

            btnTestTokenWelcome.isEnabled = false
            tvTokenTestResult.text = "Menguji ${selectedProvider.shortBadge}..."
            tvTokenTestResult.setTextColor(Color.parseColor("#38BDF8"))

            uiScope.launch {
                val (ok, msg) = withContext(Dispatchers.IO) {
                    AiEngineRegistry.getAdapter(selectedProvider)
                        .testConnection(token, selectedProvider.defaultModel)
                }
                btnTestTokenWelcome.isEnabled = true
                if (ok) {
                    vault.setApiKey(selectedProvider, token)
                    prefs.edit().putString("active_provider_id", selectedProvider.id).apply()
                    tvTokenTestResult.text = "$msg • Tersimpan!"
                    tvTokenTestResult.setTextColor(Color.parseColor("#34D399"))
                } else {
                    tvTokenTestResult.text = msg
                    tvTokenTestResult.setTextColor(Color.parseColor("#FCA5A5"))
                }
            }
        }

        btnContinueToFloamini.setOnClickListener {
            val enteredKey = etWelcomeApiKey.text.toString().trim()
            if (enteredKey.isNotEmpty()) {
                vault.setApiKey(selectedProvider, enteredKey)
                prefs.edit().putString("active_provider_id", selectedProvider.id).apply()
            }
            prefs.edit().putBoolean("has_seen_welcome", true).apply()

            if (!fromSettings) {
                startActivity(Intent(this, MainActivity::class.java))
            }
            finish()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        activityJob.cancel()
    }
}
""",

    # --------------------------------------------------------------------------
    # 19. MAIN ACTIVITY (SETTINGS DASHBOARD WITH ALL 10 REQUIRED SECTIONS)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/MainActivity.kt": r"""package com.example.floatinggeminiai

import android.app.StatusBarManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.graphics.drawable.Icon
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.RadioButton
import android.widget.RadioGroup
import android.widget.SeekBar
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import com.example.floatinggeminiai.ai.AiEngineRegistry
import com.example.floatinggeminiai.ai.AiProviderType
import com.example.floatinggeminiai.data.ChatRepository
import com.example.floatinggeminiai.security.SecureVault
import com.example.floatinggeminiai.voice.VoiceSystemManager
import com.google.android.material.switchmaterial.SwitchMaterial
import com.google.android.material.textfield.TextInputEditText
import com.google.android.material.textfield.TextInputLayout
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlin.system.exitProcess

class MainActivity : AppCompatActivity() {

    private val activityJob = Job()
    private val uiScope = CoroutineScope(Dispatchers.Main + activityJob)
    private lateinit var vault: SecureVault
    private lateinit var repo: ChatRepository
    private var voiceHelper: VoiceSystemManager? = null
    private var editingProvider = AiProviderType.GEMINI

    override fun onCreate(savedInstanceState: Bundle?) {
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        applySavedNightMode(prefs.getString("app_theme", "dark") ?: "dark")

        super.onCreate(savedInstanceState)

        if (!prefs.getBoolean("has_seen_welcome", false)) {
            startActivity(Intent(this, WelcomeActivity::class.java))
            finish()
            return
        }

        setContentView(R.layout.activity_main)

        vault = SecureVault(this)
        repo = ChatRepository(this)

        val tvAppVersionInfo = findViewById<TextView>(R.id.tvAppVersionInfo)
        val btnOpenWelcomeGuide = findViewById<Button>(R.id.btnOpenWelcomeGuide)
        val btnStartOverlay = findViewById<Button>(R.id.btnStartOverlay)
        val btnAddControlCenterTile = findViewById<Button>(R.id.btnAddControlCenterTile)
        val btnStopOverlay = findViewById<Button>(R.id.btnStopOverlay)
        val btnQuickForceStopMain = findViewById<Button>(R.id.btnQuickForceStopMain)

        // 1. Floating Window Controls
        val rgOverlayStyle = findViewById<RadioGroup>(R.id.rgOverlayStyle)
        val rbStyleDynamicIsland = findViewById<RadioButton>(R.id.rbStyleDynamicIsland)
        val rbStyleSiriMode = findViewById<RadioButton>(R.id.rbStyleSiriMode)
        val rbStyleXiaomiEdge = findViewById<RadioButton>(R.id.rbStyleXiaomiEdge)
        val rbStyleClassicBubble = findViewById<RadioButton>(R.id.rbStyleClassicBubble)

        val rgPillAppearance = findViewById<RadioGroup>(R.id.rgPillAppearance)
        val rbPillStandard = findViewById<RadioButton>(R.id.rbPillStandard)
        val rbPillPolos = findViewById<RadioButton>(R.id.rbPillPolos)
        val rbPillMinimal = findViewById<RadioButton>(R.id.rbPillMinimal)

        val swAutoHidePill = findViewById<SwitchMaterial>(R.id.swAutoHidePill)
        val swSmartFreeze = findViewById<SwitchMaterial>(R.id.swSmartFreeze)
        val swTapOutsideClose = findViewById<SwitchMaterial>(R.id.swTapOutsideClose)

        val tvIslandWidthLabel = findViewById<TextView>(R.id.tvIslandWidthLabel)
        val sbIslandWidth = findViewById<SeekBar>(R.id.sbIslandWidth)
        val tvIslandPosYLabel = findViewById<TextView>(R.id.tvIslandPosYLabel)
        val sbIslandPosY = findViewById<SeekBar>(R.id.sbIslandPosY)
        val tvIslandOffsetXLabel = findViewById<TextView>(R.id.tvIslandOffsetXLabel)
        val sbIslandOffsetX = findViewById<SeekBar>(R.id.sbIslandOffsetX)

        // 2. Multi-AI Providers & Model Manager
        val swAutoRouter = findViewById<SwitchMaterial>(R.id.swAutoRouter)
        val spProviderSelector = findViewById<Spinner>(R.id.spProviderSelector)
        val tvProviderKeyStatus = findViewById<TextView>(R.id.tvProviderKeyStatus)
        val tvOpenProviderDocs = findViewById<TextView>(R.id.tvOpenProviderDocs)
        val etProviderApiKey = findViewById<TextInputEditText>(R.id.etProviderApiKey)
        val tilCustomBaseUrl = findViewById<TextInputLayout>(R.id.tilCustomBaseUrl)
        val etCustomBaseUrl = findViewById<TextInputEditText>(R.id.etCustomBaseUrl)
        val spModelPresetSelector = findViewById<Spinner>(R.id.spModelPresetSelector)
        val etActiveModelId = findViewById<TextInputEditText>(R.id.etActiveModelId)
        val btnSaveProviderConfig = findViewById<Button>(R.id.btnSaveProviderConfig)
        val btnTestProviderConnection = findViewById<Button>(R.id.btnTestProviderConnection)
        val tvProviderTestOutput = findViewById<TextView>(R.id.tvProviderTestOutput)

        // 3. Appearance & Animation
        val rgAppTheme = findViewById<RadioGroup>(R.id.rgAppTheme)
        val rbThemeSystem = findViewById<RadioButton>(R.id.rbThemeSystem)
        val rbThemeDark = findViewById<RadioButton>(R.id.rbThemeDark)
        val rbThemeLight = findViewById<RadioButton>(R.id.rbThemeLight)
        val swLiquidBlur = findViewById<SwitchMaterial>(R.id.swLiquidBlur)
        val swHapticFeedback = findViewById<SwitchMaterial>(R.id.swHapticFeedback)
        val tvOpacityLabel = findViewById<TextView>(R.id.tvOpacityLabel)
        val sbOpacity = findViewById<SeekBar>(R.id.sbOpacity)
        val tvAnimSpeedLabel = findViewById<TextView>(R.id.tvAnimSpeedLabel)
        val sbAnimSpeed = findViewById<SeekBar>(R.id.sbAnimSpeed)

        // 4. Voice & Persona
        val swAutoSpeakTts = findViewById<SwitchMaterial>(R.id.swAutoSpeakTts)
        val spTtsVoiceSelector = findViewById<Spinner>(R.id.spTtsVoiceSelector)
        val rgPersona = findViewById<RadioGroup>(R.id.rgPersona)
        val rbAsik = findViewById<RadioButton>(R.id.rbAsik)
        val rbRingkas = findViewById<RadioButton>(R.id.rbRingkas)
        val rbDetail = findViewById<RadioButton>(R.id.rbDetail)
        val rbTeknis = findViewById<RadioButton>(R.id.rbTeknis)
        val etCustomSystemInstruction = findViewById<TextInputEditText>(R.id.etCustomSystemInstruction)

        // 5. Privacy, Data & Usage
        val tvUsageStatistics = findViewById<TextView>(R.id.tvUsageStatistics)
        val btnClearAllHistoryMain = findViewById<Button>(R.id.btnClearAllHistoryMain)
        val btnResetUsageStats = findViewById<Button>(R.id.btnResetUsageStats)
        val btnWipeVaultKeys = findViewById<Button>(R.id.btnWipeVaultKeys)
        val btnSaveAllSettings = findViewById<Button>(R.id.btnSaveAllSettings)

        try {
            val pInfo = packageManager.getPackageInfo(packageName, 0)
            tvAppVersionInfo.text = "v${pInfo.versionName} • 11 AI Engines • Encrypted Vault"
        } catch (_: Exception) {}

        // Load Saved Values
        when (prefs.getString("overlay_style", "dynamic_island")) {
            "siri_mode" -> rbStyleSiriMode.isChecked = true
            "xiaomi_edge" -> rbStyleXiaomiEdge.isChecked = true
            "classic_bubble" -> rbStyleClassicBubble.isChecked = true
            else -> rbStyleDynamicIsland.isChecked = true
        }
        when (prefs.getString("pill_appearance", "standard")) {
            "polos" -> rbPillPolos.isChecked = true
            "minimal" -> rbPillMinimal.isChecked = true
            else -> rbPillStandard.isChecked = true
        }
        swAutoHidePill.isChecked = prefs.getBoolean("auto_hide_pill", false)
        swSmartFreeze.isChecked = prefs.getBoolean("smart_freeze", true)
        swTapOutsideClose.isChecked = prefs.getBoolean("tap_outside_close", true)
        swAutoRouter.isChecked = prefs.getBoolean("auto_router_enabled", false)
        swLiquidBlur.isChecked = prefs.getBoolean("liquid_blur", true)
        swHapticFeedback.isChecked = prefs.getBoolean("haptic_feedback", true)
        swAutoSpeakTts.isChecked = prefs.getBoolean("auto_speak_tts", true)

        when (prefs.getString("app_theme", "dark")) {
            "system" -> rbThemeSystem.isChecked = true
            "light" -> rbThemeLight.isChecked = true
            else -> rbThemeDark.isChecked = true
        }

        val savedIslandW = prefs.getInt("island_width_dp", 164)
        sbIslandWidth.progress = (savedIslandW - 110).coerceIn(0, 130)
        tvIslandWidthLabel.text = "Lebar Pil Dynamic Island: ${savedIslandW}dp"

        val savedIslandY = prefs.getInt("island_pos_y_dp", 12)
        sbIslandPosY.progress = savedIslandY.coerceIn(0, 70)
        tvIslandPosYLabel.text = "Posisi Vertikal Atas (Y): ${savedIslandY}dp"

        val savedIslandX = prefs.getInt("island_offset_x_dp", 0)
        sbIslandOffsetX.progress = (savedIslandX + 80).coerceIn(0, 160)
        tvIslandOffsetXLabel.text = "Geser Horizontal Kamera (X): ${savedIslandX}dp"

        val savedOpacity = prefs.getInt("popup_opacity", 84)
        sbOpacity.progress = (savedOpacity - 45).coerceIn(0, 55)
        tvOpacityLabel.text = "Transparansi Liquid Glass: ${savedOpacity}%"

        val savedAnimProg = prefs.getInt("anim_speed_prog", 5)
        sbAnimSpeed.progress = savedAnimProg.coerceIn(0, 10)
        val speedMult = 0.5f + (savedAnimProg * 0.1f)
        tvAnimSpeedLabel.text = String.format("Kecepatan Spring Animation: %.1fx", speedMult)

        when (prefs.getString("ai_persona", "asik")) {
            "ringkas" -> rbRingkas.isChecked = true
            "detail" -> rbDetail.isChecked = true
            "teknis" -> rbTeknis.isChecked = true
            else -> rbAsik.isChecked = true
        }
        etCustomSystemInstruction.setText(prefs.getString("custom_system_instruction", ""))
        tvUsageStatistics.text = repo.getUsageSummaryText()

        // Setup 11 AI Provider Selector
        val providers = AiProviderType.values().toList()
        editingProvider = AiProviderType.fromId(prefs.getString("active_provider_id", "gemini"))
        spProviderSelector.adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_dropdown_item,
            providers.map { p ->
                val mark = if (vault.getApiKey(p).isNotEmpty()) " [Aktif]" else ""
                "${p.displayName}$mark"
            }
        )
        spProviderSelector.setSelection(providers.indexOf(editingProvider).coerceAtLeast(0))

        fun bindProviderFields(provider: AiProviderType) {
            editingProvider = provider
            val savedKey = vault.getApiKey(provider)
            etProviderApiKey.setText(savedKey)
            if (savedKey.isNotEmpty()) {
                tvProviderKeyStatus.text = "Status Key: Terenkripsi & Siap"
                tvProviderKeyStatus.setTextColor(Color.parseColor("#34D399"))
            } else {
                tvProviderKeyStatus.text = "Status Key: Belum diisi"
                tvProviderKeyStatus.setTextColor(Color.parseColor("#FBBF24"))
            }

            tilCustomBaseUrl.visibility = if (provider == AiProviderType.CUSTOM) View.VISIBLE else View.GONE
            etCustomBaseUrl.setText(vault.getCustomBaseUrl())

            val models = provider.availableModels
            spModelPresetSelector.adapter = ArrayAdapter(
                this,
                android.R.layout.simple_spinner_dropdown_item,
                models
            )
            val currentModel = vault.getSelectedModel(provider)
            etActiveModelId.setText(currentModel)
            val idx = models.indexOf(currentModel)
            if (idx >= 0) spModelPresetSelector.setSelection(idx)
        }

        bindProviderFields(editingProvider)

        spProviderSelector.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                bindProviderFields(providers[position])
            }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }

        spModelPresetSelector.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                val chosen = editingProvider.availableModels[position]
                if (chosen != "custom-model") {
                    etActiveModelId.setText(chosen)
                }
            }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }

        tvOpenProviderDocs.setOnClickListener {
            try {
                startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(editingProvider.docsUrl)))
            } catch (_: Exception) {
                Toast.makeText(this, "Kunjungi ${editingProvider.docsUrl}", Toast.LENGTH_LONG).show()
            }
        }

        btnSaveProviderConfig.setOnClickListener {
            val key = etProviderApiKey.text.toString().trim()
            val modelId = etActiveModelId.text.toString().trim().ifEmpty { editingProvider.defaultModel }
            vault.setApiKey(editingProvider, key)
            vault.setSelectedModel(editingProvider, modelId)
            if (editingProvider == AiProviderType.CUSTOM) {
                vault.setCustomBaseUrl(etCustomBaseUrl.text.toString())
            }
            prefs.edit().putString("active_provider_id", editingProvider.id).apply()
            bindProviderFields(editingProvider)
            Toast.makeText(this, "${editingProvider.displayName} ($modelId) disimpan & dijadikan aktif!", Toast.LENGTH_SHORT).show()
        }

        btnTestProviderConnection.setOnClickListener {
            val key = etProviderApiKey.text.toString().trim()
            val modelId = etActiveModelId.text.toString().trim().ifEmpty { editingProvider.defaultModel }
            val customUrl = etCustomBaseUrl.text.toString().trim()
            if (key.isEmpty()) {
                tvProviderTestOutput.text = "Masukkan API Key terlebih dahulu"
                tvProviderTestOutput.setTextColor(Color.parseColor("#FBBF24"))
                return@setOnClickListener
            }
            btnTestProviderConnection.isEnabled = false
            tvProviderTestOutput.text = "Menguji koneksi ${editingProvider.shortBadge}..."
            tvProviderTestOutput.setTextColor(Color.parseColor("#38BDF8"))

            uiScope.launch {
                val (ok, msg) = withContext(Dispatchers.IO) {
                    AiEngineRegistry.getAdapter(editingProvider).testConnection(key, modelId, customUrl)
                }
                btnTestProviderConnection.isEnabled = true
                tvProviderTestOutput.text = msg
                tvProviderTestOutput.setTextColor(Color.parseColor(if (ok) "#34D399" else "#FCA5A5"))
            }
        }

        // Populate TTS Voice Selector
        voiceHelper = VoiceSystemManager(this, {}, {}, {}, {}, {}, {})
        android.os.Handler(mainLooper).postDelayed({
            val voices = voiceHelper?.getAvailableVoices() ?: emptyList()
            val voiceNames = mutableListOf("Default Sistem (Indonesia)")
            voiceNames.addAll(voices.map { "${it.locale.displayLanguage} - ${it.name}" })
            spTtsVoiceSelector.adapter = ArrayAdapter(
                this,
                android.R.layout.simple_spinner_dropdown_item,
                voiceNames
            )
            val savedVoice = prefs.getString("tts_voice_name", "") ?: ""
            if (savedVoice.isNotEmpty()) {
                val idx = voices.indexOfFirst { it.name == savedVoice }
                if (idx >= 0) spTtsVoiceSelector.setSelection(idx + 1)
            }
            spTtsVoiceSelector.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
                override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                    val chosenVoice = if (position == 0) "" else voices.getOrNull(position - 1)?.name ?: ""
                    prefs.edit().putString("tts_voice_name", chosenVoice).apply()
                }
                override fun onNothingSelected(parent: AdapterView<*>?) {}
            }
        }, 600L)

        // SeekBar Listeners
        sbIslandWidth.setOnSeekBarChangeListener(simpleSeek { p ->
            tvIslandWidthLabel.text = "Lebar Pil Dynamic Island: ${p + 110}dp"
        })
        sbIslandPosY.setOnSeekBarChangeListener(simpleSeek { p ->
            tvIslandPosYLabel.text = "Posisi Vertikal Atas (Y): ${p}dp"
        })
        sbIslandOffsetX.setOnSeekBarChangeListener(simpleSeek { p ->
            tvIslandOffsetXLabel.text = "Geser Horizontal Kamera (X): ${p - 80}dp"
        })
        sbOpacity.setOnSeekBarChangeListener(simpleSeek { p ->
            tvOpacityLabel.text = "Transparansi Liquid Glass: ${p + 45}%"
        })
        sbAnimSpeed.setOnSeekBarChangeListener(simpleSeek { p ->
            tvAnimSpeedLabel.text = String.format("Kecepatan Spring Animation: %.1fx", 0.5f + p * 0.1f)
        })

        fun saveAllPreferences() {
            val style = when (rgOverlayStyle.checkedRadioButtonId) {
                R.id.rbStyleSiriMode -> "siri_mode"
                R.id.rbStyleXiaomiEdge -> "xiaomi_edge"
                R.id.rbStyleClassicBubble -> "classic_bubble"
                else -> "dynamic_island"
            }
            val pillApp = when (rgPillAppearance.checkedRadioButtonId) {
                R.id.rbPillPolos -> "polos"
                R.id.rbPillMinimal -> "minimal"
                else -> "standard"
            }
            val persona = when (rgPersona.checkedRadioButtonId) {
                R.id.rbRingkas -> "ringkas"
                R.id.rbDetail -> "detail"
                R.id.rbTeknis -> "teknis"
                else -> "asik"
            }
            val themeChoice = when (rgAppTheme.checkedRadioButtonId) {
                R.id.rbThemeSystem -> "system"
                R.id.rbThemeLight -> "light"
                else -> "dark"
            }

            val key = etProviderApiKey.text.toString().trim()
            val modelId = etActiveModelId.text.toString().trim().ifEmpty { editingProvider.defaultModel }
            vault.setApiKey(editingProvider, key)
            vault.setSelectedModel(editingProvider, modelId)
            if (editingProvider == AiProviderType.CUSTOM) {
                vault.setCustomBaseUrl(etCustomBaseUrl.text.toString())
            }

            prefs.edit()
                .putString("active_provider_id", editingProvider.id)
                .putBoolean("auto_router_enabled", swAutoRouter.isChecked)
                .putString("overlay_style", style)
                .putString("pill_appearance", pillApp)
                .putBoolean("auto_hide_pill", swAutoHidePill.isChecked)
                .putBoolean("smart_freeze", swSmartFreeze.isChecked)
                .putBoolean("tap_outside_close", swTapOutsideClose.isChecked)
                .putBoolean("liquid_blur", swLiquidBlur.isChecked)
                .putBoolean("haptic_feedback", swHapticFeedback.isChecked)
                .putBoolean("auto_speak_tts", swAutoSpeakTts.isChecked)
                .putString("app_theme", themeChoice)
                .putInt("island_width_dp", sbIslandWidth.progress + 110)
                .putInt("island_pos_y_dp", sbIslandPosY.progress)
                .putInt("island_offset_x_dp", sbIslandOffsetX.progress - 80)
                .putInt("popup_opacity", sbOpacity.progress + 45)
                .putInt("anim_speed_prog", sbAnimSpeed.progress)
                .putString("ai_persona", persona)
                .putString("custom_system_instruction", etCustomSystemInstruction.text.toString().trim())
                .apply()

            applySavedNightMode(themeChoice)

            if (Settings.canDrawOverlays(this)) {
                try {
                    startService(Intent(this, FloatingAssistantService::class.java).apply {
                        action = FloatingAssistantService.ACTION_RELOAD_SETTINGS
                    })
                } catch (_: Exception) {}
            }
        }

        btnAddControlCenterTile.setOnClickListener {
            saveAllPreferences()
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                val sbm = getSystemService(StatusBarManager::class.java)
                sbm.requestAddTileService(
                    ComponentName(this, FloaminiTileService::class.java),
                    "Floamini AI",
                    Icon.createWithResource(this, R.drawable.ic_sparkle),
                    mainExecutor
                ) { code ->
                    runOnUiThread {
                        if (code == StatusBarManager.TILE_ADD_REQUEST_RESULT_TILE_ADDED ||
                            code == StatusBarManager.TILE_ADD_REQUEST_RESULT_TILE_ALREADY_ADDED
                        ) {
                            Toast.makeText(this, "Tombol Floamini AI siap di Control Center!", Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            } else {
                Toast.makeText(this, "Tarik Control Center, tekan Edit, lalu tambahkan tombol Floamini AI!", Toast.LENGTH_LONG).show()
            }
        }

        btnOpenWelcomeGuide.setOnClickListener {
            startActivity(Intent(this, WelcomeActivity::class.java).apply { putExtra("from_settings", true) })
        }

        btnClearAllHistoryMain.setOnClickListener {
            repo.clearAllThreads()
            try {
                startService(Intent(this, FloatingAssistantService::class.java).apply {
                    action = FloatingAssistantService.ACTION_RESET_SESSION
                })
            } catch (_: Exception) {}
            Toast.makeText(this, "Seluruh riwayat chat dihapus", Toast.LENGTH_SHORT).show()
        }

        btnResetUsageStats.setOnClickListener {
            repo.resetUsageStats()
            tvUsageStatistics.text = repo.getUsageSummaryText()
            Toast.makeText(this, "Statistik penggunaan di-reset", Toast.LENGTH_SHORT).show()
        }

        btnWipeVaultKeys.setOnClickListener {
            vault.clearAllCredentials()
            etProviderApiKey.setText("")
            bindProviderFields(editingProvider)
            Toast.makeText(this, "Seluruh API Key terenkripsi dihapus", Toast.LENGTH_SHORT).show()
        }

        btnSaveAllSettings.setOnClickListener {
            saveAllPreferences()
            Toast.makeText(this, "Semua pengaturan Floamini OS disimpan!", Toast.LENGTH_SHORT).show()
        }

        btnStartOverlay.setOnClickListener {
            saveAllPreferences()
            if (!Settings.canDrawOverlays(this)) {
                Toast.makeText(this, "Izinkan Floamini tampil di atas aplikasi lain", Toast.LENGTH_LONG).show()
                startActivity(Intent(
                    Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                    Uri.parse("package:$packageName")
                ))
                return@setOnClickListener
            }

            val serviceIntent = Intent(this, FloatingAssistantService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                startForegroundService(serviceIntent)
            } else {
                startService(serviceIntent)
            }
            Toast.makeText(this, "Floamini OS aktif di layar!", Toast.LENGTH_SHORT).show()
        }

        btnStopOverlay.setOnClickListener {
            stopService(Intent(this, FloatingAssistantService::class.java))
            Toast.makeText(this, "Floamini dihentikan", Toast.LENGTH_SHORT).show()
        }

        btnQuickForceStopMain.setOnClickListener {
            stopService(Intent(this, FloatingAssistantService::class.java))
            startActivity(Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                data = Uri.parse("package:$packageName")
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            })
            finishAffinity()
            exitProcess(0)
        }
    }

    private fun applySavedNightMode(theme: String) {
        val mode = when (theme) {
            "system" -> AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM
            "light" -> AppCompatDelegate.MODE_NIGHT_NO
            else -> AppCompatDelegate.MODE_NIGHT_YES
        }
        AppCompatDelegate.setDefaultNightMode(mode)
    }

    private fun simpleSeek(onChange: (Int) -> Unit) = object : SeekBar.OnSeekBarChangeListener {
        override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) = onChange(progress)
        override fun onStartTrackingTouch(seekBar: SeekBar?) {}
        override fun onStopTrackingTouch(seekBar: SeekBar?) {}
    }

    override fun onResume() {
        super.onResume()
        if (::repo.isInitialized) {
            findViewById<TextView>(R.id.tvUsageStatistics)?.text = repo.getUsageSummaryText()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        voiceHelper?.release()
        activityJob.cancel()
    }
}
""",

    # --------------------------------------------------------------------------
    # 20. FLOATING ASSISTANT SERVICE (OS-LEVEL MULTI-AI, STREAMING, VOICE, TOOLS)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/FloatingAssistantService.kt": r"""package com.example.floatinggeminiai

import android.Manifest
import android.animation.ValueAnimator
import android.app.Activity
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.BroadcastReceiver
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.content.pm.ServiceInfo
import android.graphics.Bitmap
import android.graphics.Color
import android.graphics.PixelFormat
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.media.ImageReader
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.net.Uri
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.provider.Settings
import android.text.Editable
import android.text.TextWatcher
import android.util.Base64
import android.util.DisplayMetrics
import android.view.Gravity
import android.view.LayoutInflater
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
import android.view.animation.DecelerateInterpolator
import android.widget.Button
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.ImageButton
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.core.app.NotificationCompat
import androidx.dynamicanimation.animation.DynamicAnimation
import androidx.dynamicanimation.animation.SpringAnimation
import androidx.dynamicanimation.animation.SpringForce
import com.example.floatinggeminiai.ai.AiEngineRegistry
import com.example.floatinggeminiai.ai.AiProviderType
import com.example.floatinggeminiai.ai.AiRequestPayload
import com.example.floatinggeminiai.ai.ChatMessage
import com.example.floatinggeminiai.ai.ChatThread
import com.example.floatinggeminiai.ai.StreamEvent
import com.example.floatinggeminiai.data.ChatRepository
import com.example.floatinggeminiai.security.SecureVault
import com.example.floatinggeminiai.tools.ProcessedAttachment
import com.example.floatinggeminiai.tools.SmartToolsHelper
import com.example.floatinggeminiai.ui.VoiceWaveformView
import com.example.floatinggeminiai.voice.VoiceSystemManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.launch
import java.io.ByteArrayOutputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.UUID
import kotlin.math.abs
import kotlin.system.exitProcess

class FloatingAssistantService : Service() {

    companion object {
        const val ACTION_SCREEN_CAPTURE_RESULT = "ACTION_SCREEN_CAPTURE_RESULT"
        const val ACTION_RELOAD_SETTINGS = "ACTION_RELOAD_SETTINGS"
        const val ACTION_RESET_SESSION = "ACTION_RESET_SESSION"
        const val ACTION_TRIGGER_SIRI = "ACTION_TRIGGER_SIRI"
        const val ACTION_ATTACH_URI = "ACTION_ATTACH_URI"
        const val ACTION_AUDIO_PERMISSION_GRANTED = "ACTION_AUDIO_PERMISSION_GRANTED"
        const val ACTION_EXTERNAL_CONTEXT = "ACTION_EXTERNAL_CONTEXT"
    }

    private lateinit var windowManager: WindowManager
    private lateinit var floatingView: View
    private lateinit var params: WindowManager.LayoutParams
    private var isFloatingViewAttached = false

    private lateinit var vault: SecureVault
    private lateinit var repo: ChatRepository
    private var voiceManager: VoiceSystemManager? = null

    private var siriGlowView: SiriEdgeGlowView? = null
    private var isSiriAuraActive = false

    private val serviceJob = Job()
    private val serviceScope = CoroutineScope(Dispatchers.Main + serviceJob)
    private var activeGenerationJob: Job? = null

    // UI References
    private lateinit var dynamicIslandView: LinearLayout
    private lateinit var ivIslandSparkle: ImageView
    private lateinit var tvIslandLabel: TextView
    private lateinit var viewIslandPulseDot: View
    private lateinit var bubbleView: FrameLayout
    private lateinit var xiaomiEdgeView: FrameLayout
    private lateinit var popupChatView: LinearLayout

    private lateinit var tvActiveProviderHeader: TextView
    private lateinit var btnScreenShare: ImageView
    private lateinit var tvScreenShareStatus: TextView
    private lateinit var attachmentPreviewBar: LinearLayout
    private lateinit var tvAttachmentName: TextView
    private lateinit var tvCompareBadge: TextView
    private lateinit var tvCurrentPersonaBadge: TextView

    private lateinit var scrollChat: ScrollView
    private lateinit var chatContainer: LinearLayout
    private lateinit var typingIndicatorRow: LinearLayout
    private lateinit var tvThinkingLabel: TextView
    private lateinit var voiceWaveformBar: LinearLayout
    private lateinit var tvVoiceStatusLabel: TextView
    private lateinit var voiceWaveformView: VoiceWaveformView
    private lateinit var etPrompt: EditText
    private lateinit var btnSendPrompt: ImageButton

    // State
    private val mainHandler = Handler(Looper.getMainLooper())
    private var snappedToRightEdge = false
    private var fullScreenWidth = 1080
    private var fullScreenHeight = 2400
    private var isPillAutoHidden = false
    private var isSmartFrozen = false
    private var isMiniWindowMode = false
    private var isCompareMode = false
    private var isVoiceChatLoop = false

    // Preferences
    private var activeProvider = AiProviderType.GEMINI
    private var prefAutoRouter = false
    private var prefOverlayStyle = "dynamic_island"
    private var prefPillAppearance = "standard"
    private var prefAutoHidePill = false
    private var prefSmartFreeze = true
    private var prefTapOutsideClose = true
    private var prefLiquidBlur = true
    private var prefHapticFeedback = true
    private var prefAutoSpeakTts = true
    private var prefTtsVoiceName = ""
    private var prefAnimSpeedMultiplier = 1.0f
    private var prefIslandWidthPx = 440
    private var prefIslandPosYPx = 32
    private var prefIslandOffsetXPx = 0
    private var prefPopupAlpha = 0.84f
    private var prefBubbleSizePx = 148
    private var prefPersona = "asik"
    private var prefCustomSystemInstruction = ""

    // Multi-Thread Session State
    private var allThreads = mutableListOf<ChatThread>()
    private lateinit var currentThread: ChatThread
    private var lastUserPrompt = ""
    private var lastBotReply = ""
    private var pendingAttachment: ProcessedAttachment? = null

    // Screen Capture
    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    private var isScreenShareActive = false
    private var captureWidth = 540
    private var captureHeight = 1200
    private var screenDensity = 320

    private val autoHidePillRunnable = Runnable {
        if (prefOverlayStyle == "dynamic_island" &&
            prefAutoHidePill &&
            dynamicIslandView.visibility == View.VISIBLE &&
            popupChatView.visibility != View.VISIBLE
        ) {
            isPillAutoHidden = true
            dynamicIslandView.animate()
                .alpha(0.02f)
                .scaleX(0.45f)
                .scaleY(0.45f)
                .setDuration((420 / prefAnimSpeedMultiplier).toLong())
                .start()
        }
    }

    private val transformToXiaomiEdgeRunnable = Runnable {
        if (prefOverlayStyle == "xiaomi_edge" && bubbleView.visibility == View.VISIBLE) {
            enterXiaomiEdgeMode()
        }
    }

    private val smartFreezeRunnable = Runnable {
        if (prefSmartFreeze && popupChatView.visibility != View.VISIBLE) {
            enterSmartFreezeState()
        }
    }

    private val screenStateReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            when (intent?.action) {
                Intent.ACTION_SCREEN_OFF -> {
                    if (prefSmartFreeze) {
                        if (popupChatView.visibility == View.VISIBLE) {
                            popupChatView.visibility = View.GONE
                        }
                        dismissSiriAura()
                        voiceManager?.stopListening()
                        voiceManager?.stopSpeaking()
                        enterSmartFreezeState()
                    }
                }
                Intent.ACTION_SCREEN_ON -> {
                    if (isSmartFrozen && prefOverlayStyle != "siri_mode") {
                        wakeFromSmartFreeze()
                    }
                }
            }
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        vault = SecureVault(this)
        repo = ChatRepository(this)
        startForegroundNotification(withMediaProjection = false)
        setupScreenMetrics()
        loadUserPreferences()
        initVoiceSystem()
        setupFloatingOverlay()

        val filter = IntentFilter().apply {
            addAction(Intent.ACTION_SCREEN_OFF)
            addAction(Intent.ACTION_SCREEN_ON)
        }
        registerReceiver(screenStateReceiver, filter)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_SCREEN_CAPTURE_RESULT -> {
                val resultCode = intent.getIntExtra("resultCode", Activity.RESULT_CANCELED)
                val data: Intent? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                    intent.getParcelableExtra("data", Intent::class.java)
                } else {
                    @Suppress("DEPRECATION")
                    intent.getParcelableExtra("data")
                }
                if (resultCode == Activity.RESULT_OK && data != null) {
                    startMediaProjection(resultCode, data)
                } else {
                    Toast.makeText(this, "Izin Screen Vision dibatalkan", Toast.LENGTH_SHORT).show()
                }
            }
            ACTION_RELOAD_SETTINGS -> {
                loadUserPreferences()
                wakeFromSmartFreeze()
                applyVisualPreferences()
                if (popupChatView.visibility != View.VISIBLE) {
                    showCollapsedTriggerState()
                }
            }
            ACTION_RESET_SESSION -> {
                allThreads = repo.loadAllThreads()
                startNewConversationThread()
            }
            ACTION_TRIGGER_SIRI -> {
                triggerHaptic()
                wakeFromSmartFreeze()
                showSiriAura()
                openPopupChat(fromSiri = true)
            }
            ACTION_AUDIO_PERMISSION_GRANTED -> {
                startVoiceChatSession()
            }
            ACTION_ATTACH_URI -> {
                val uriStr = intent.getStringExtra("uri_string") ?: return START_STICKY
                val uri = Uri.parse(uriStr)
                val processed = SmartToolsHelper.processUriAttachment(this, uri)
                if (processed != null) {
                    pendingAttachment = processed
                    tvAttachmentName.text = processed.displayName
                    attachmentPreviewBar.visibility = View.VISIBLE
                    if (popupChatView.visibility != View.VISIBLE) {
                        openPopupChat(fromSiri = false)
                    }
                } else {
                    Toast.makeText(this, "Gagal membaca file lampiran", Toast.LENGTH_SHORT).show()
                }
            }
            ACTION_EXTERNAL_CONTEXT -> {
                val sharedText = intent.getStringExtra("shared_text") ?: ""
                val uriStr = intent.getStringExtra("uri_string")
                val mode = intent.getStringExtra("source_mode") ?: "share"

                wakeFromSmartFreeze()
                openPopupChat(fromSiri = false)

                if (!uriStr.isNullOrEmpty()) {
                    val processed = SmartToolsHelper.processUriAttachment(this, Uri.parse(uriStr))
                    if (processed != null) {
                        pendingAttachment = processed
                        tvAttachmentName.text = processed.displayName
                        attachmentPreviewBar.visibility = View.VISIBLE
                    }
                }

                if (sharedText.isNotBlank()) {
                    val prefix = if (mode == "selection") "Bantu jelaskan atau proses teks pilihan ini:\n\"$sharedText\"" else sharedText
                    etPrompt.setText(prefix)
                    etPrompt.setSelection(etPrompt.text.length)
                }
            }
        }
        return START_STICKY
    }

    // ==========================================================================
    // VOICE SYSTEM (STT + TTS + WAVEFORM + INTERRUPTION)
    // ==========================================================================
    private fun initVoiceSystem() {
        voiceManager = VoiceSystemManager(
            context = this,
            onRmsChanged = { amp ->
                mainHandler.post { voiceWaveformView.setAmplitude(amp) }
            },
            onPartialSpeech = { partial ->
                mainHandler.post {
                    etPrompt.setText(partial)
                    etPrompt.setSelection(partial.length)
                }
            },
            onFinalSpeech = { finalSpoken ->
                mainHandler.post {
                    voiceWaveformView.stopAnimation()
                    voiceWaveformBar.visibility = View.GONE
                    etPrompt.setText(finalSpoken)
                    triggerSendPrompt(finalSpoken, fromVoice = true)
                }
            },
            onListeningStateChanged = { listening ->
                mainHandler.post {
                    if (listening) {
                        voiceWaveformBar.visibility = View.VISIBLE
                        tvVoiceStatusLabel.text = "Mendengarkan..."
                        voiceWaveformView.startAnimation()
                    } else if (voiceManager?.isSpeaking != true) {
                        voiceWaveformView.stopAnimation()
                        voiceWaveformBar.visibility = View.GONE
                    }
                }
            },
            onSpeakingStateChanged = { speaking ->
                mainHandler.post {
                    if (speaking) {
                        voiceWaveformBar.visibility = View.VISIBLE
                        tvVoiceStatusLabel.text = "Floamini Berbicara..."
                        voiceWaveformView.setAmplitude(0.65f)
                        voiceWaveformView.startAnimation()
                    } else {
                        voiceWaveformView.stopAnimation()
                        voiceWaveformBar.visibility = View.GONE
                    }
                }
            },
            onVoiceError = { err ->
                mainHandler.post {
                    voiceWaveformView.stopAnimation()
                    voiceWaveformBar.visibility = View.GONE
                    Toast.makeText(this, err, Toast.LENGTH_SHORT).show()
                }
            }
        )
    }

    private fun startVoiceChatSession() {
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            startActivity(Intent(this, AudioPermissionProxyActivity::class.java).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            })
            return
        }
        isVoiceChatLoop = true
        triggerHaptic()
        voiceManager?.startListening()
    }

    // ==========================================================================
    // AUTO SMART FREEZE ENGINE
    // ==========================================================================
    private fun scheduleSmartFreeze() {
        mainHandler.removeCallbacks(smartFreezeRunnable)
        if (prefSmartFreeze) {
            mainHandler.postDelayed(smartFreezeRunnable, 18_000L)
        }
    }

    private fun enterSmartFreezeState() {
        if (isSmartFrozen) return
        isSmartFrozen = true
        mainHandler.removeCallbacks(autoHidePillRunnable)
        mainHandler.removeCallbacks(transformToXiaomiEdgeRunnable)

        dynamicIslandView.animate().cancel()
        bubbleView.animate().cancel()
        xiaomiEdgeView.animate().cancel()
        siriGlowView?.stopAndFreezeAnimation()

        if (prefOverlayStyle == "siri_mode" && isFloatingViewAttached) {
            try {
                windowManager.removeViewImmediate(floatingView)
                isFloatingViewAttached = false
            } catch (_: Exception) {}
        }
        System.gc()
    }

    private fun wakeFromSmartFreeze() {
        mainHandler.removeCallbacks(smartFreezeRunnable)
        if (!isFloatingViewAttached && ::floatingView.isInitialized) {
            try {
                windowManager.addView(floatingView, params)
                isFloatingViewAttached = true
            } catch (_: Exception) {}
        }
        isSmartFrozen = false
    }

    // ==========================================================================
    // SIRI EDGE GLOW AURA
    // ==========================================================================
    private fun showSiriAura() {
        if (isSiriAuraActive) return
        isSiriAuraActive = true

        val layoutFlag = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        } else {
            @Suppress("DEPRECATION")
            WindowManager.LayoutParams.TYPE_PHONE
        }

        val auraParams = WindowManager.LayoutParams(
            WindowManager.LayoutParams.MATCH_PARENT,
            WindowManager.LayoutParams.MATCH_PARENT,
            layoutFlag,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                    WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE or
                    WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN or
                    WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
            PixelFormat.TRANSLUCENT
        )

        val glowView = SiriEdgeGlowView(this).apply { alpha = 0f }
        siriGlowView = glowView
        try {
            windowManager.addView(glowView, auraParams)
            glowView.startSiriAnimation()
            glowView.animate().alpha(1f).setDuration(340).start()
        } catch (_: Exception) {}
    }

    private fun dismissSiriAura() {
        val glowView = siriGlowView ?: return
        isSiriAuraActive = false
        siriGlowView = null
        glowView.animate()
            .alpha(0f)
            .setDuration(240)
            .withEndAction {
                glowView.stopAndFreezeAnimation()
                try { windowManager.removeViewImmediate(glowView) } catch (_: Exception) {}
            }
            .start()
    }

    private fun triggerHaptic() {
        if (!prefHapticFeedback) return
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                val vm = getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
                vm.defaultVibrator.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_TICK))
            } else {
                @Suppress("DEPRECATION")
                val vibrator = getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    vibrator.vibrate(VibrationEffect.createOneShot(14, VibrationEffect.DEFAULT_AMPLITUDE))
                } else {
                    @Suppress("DEPRECATION")
                    vibrator.vibrate(14)
                }
            }
        } catch (_: Exception) {}
    }

    private fun currentTimeLabel(): String = SimpleDateFormat("HH:mm", Locale.getDefault()).format(Date())

    private fun loadUserPreferences() {
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        val density = resources.displayMetrics.density
        activeProvider = AiProviderType.fromId(prefs.getString("active_provider_id", "gemini"))
        prefAutoRouter = prefs.getBoolean("auto_router_enabled", false)
        prefOverlayStyle = prefs.getString("overlay_style", "dynamic_island") ?: "dynamic_island"
        prefPillAppearance = prefs.getString("pill_appearance", "standard") ?: "standard"
        prefAutoHidePill = prefs.getBoolean("auto_hide_pill", false)
        prefSmartFreeze = prefs.getBoolean("smart_freeze", true)
        prefTapOutsideClose = prefs.getBoolean("tap_outside_close", true)
        prefLiquidBlur = prefs.getBoolean("liquid_blur", true)
        prefHapticFeedback = prefs.getBoolean("haptic_feedback", true)
        prefAutoSpeakTts = prefs.getBoolean("auto_speak_tts", true)
        prefTtsVoiceName = prefs.getString("tts_voice_name", "") ?: ""
        val animProg = prefs.getInt("anim_speed_prog", 5)
        prefAnimSpeedMultiplier = (0.5f + animProg * 0.1f).coerceIn(0.5f, 1.5f)
        prefIslandWidthPx = (prefs.getInt("island_width_dp", 164) * density).toInt()
        prefIslandPosYPx = (prefs.getInt("island_pos_y_dp", 12) * density).toInt()
        prefIslandOffsetXPx = (prefs.getInt("island_offset_x_dp", 0) * density).toInt()
        prefPopupAlpha = (prefs.getInt("popup_opacity", 84) / 100f).coerceIn(0.45f, 1.0f)
        prefBubbleSizePx = (54 * density).toInt()
        prefPersona = prefs.getString("ai_persona", "asik") ?: "asik"
        prefCustomSystemInstruction = prefs.getString("custom_system_instruction", "") ?: ""
    }

    private fun applyVisualPreferences() {
        if (::dynamicIslandView.isInitialized) {
            val lp = dynamicIslandView.layoutParams
            lp.width = prefIslandWidthPx
            dynamicIslandView.layoutParams = lp

            when (prefPillAppearance) {
                "polos" -> {
                    dynamicIslandView.setBackgroundResource(R.drawable.bg_dynamic_island_polos)
                    ivIslandSparkle.visibility = View.GONE
                    tvIslandLabel.visibility = View.GONE
                    viewIslandPulseDot.visibility = View.GONE
                }
                "minimal" -> {
                    dynamicIslandView.setBackgroundResource(R.drawable.bg_dynamic_island)
                    ivIslandSparkle.visibility = View.VISIBLE
                    tvIslandLabel.visibility = View.GONE
                    viewIslandPulseDot.visibility = View.VISIBLE
                }
                else -> {
                    dynamicIslandView.setBackgroundResource(R.drawable.bg_dynamic_island)
                    ivIslandSparkle.visibility = View.VISIBLE
                    tvIslandLabel.visibility = View.VISIBLE
                    viewIslandPulseDot.visibility = View.VISIBLE
                }
            }
        }
        if (::popupChatView.isInitialized) {
            popupChatView.alpha = prefPopupAlpha
        }
        if (::tvActiveProviderHeader.isInitialized) {
            val modelName = vault.getSelectedModel(activeProvider)
            val prefix = if (prefAutoRouter) "Auto • " else ""
            tvActiveProviderHeader.text = "$prefix${activeProvider.shortBadge} • $modelName"
        }
        if (::tvCurrentPersonaBadge.isInitialized) {
            tvCurrentPersonaBadge.text = when (prefPersona) {
                "ringkas" -> "Singkat"
                "detail" -> "Detail"
                "teknis" -> "Teknis"
                else -> "Asik"
            }
        }
    }

    // ==========================================================================
    // MULTI-THREAD CONVERSATION & HISTORY MANAGEMENT
    // ==========================================================================
    private fun initializeThreads() {
        allThreads = repo.loadAllThreads()
        val activeId = repo.getActiveThreadId()
        val existing = allThreads.firstOrNull { it.id == activeId } ?: allThreads.firstOrNull()
        if (existing != null) {
            currentThread = existing
        } else {
            currentThread = ChatThread(
                id = UUID.randomUUID().toString(),
                title = "Obrolan Baru",
                updatedAt = System.currentTimeMillis()
            )
            allThreads.add(0, currentThread)
            repo.setActiveThreadId(currentThread.id)
        }
        renderCurrentThreadMessages()
    }

    private fun startNewConversationThread() {
        currentThread = ChatThread(
            id = UUID.randomUUID().toString(),
            title = "Obrolan Baru",
            updatedAt = System.currentTimeMillis()
        )
        allThreads.add(0, currentThread)
        repo.setActiveThreadId(currentThread.id)
        repo.saveAllThreads(allThreads)
        renderCurrentThreadMessages()
    }

    private fun renderCurrentThreadMessages() {
        chatContainer.removeAllViews()
        if (currentThread.messages.isEmpty()) {
            val greeting = "Halo! Floamini OS siap membantu dengan 11 AI Provider, Streaming SSE, Voice Chat, dan PDF/Screen Vision."
            lastBotReply = greeting
            addChatBubbleView(
                ChatMessage(UUID.randomUUID().toString(), "model", greeting, currentTimeLabel(), activeProvider.shortBadge),
                animateEntrance = false
            )
        } else {
            for (m in currentThread.messages) {
                if (m.role == "model") lastBotReply = m.text
                addChatBubbleView(m, animateEntrance = false)
            }
        }
    }

    private fun persistCurrentThread() {
        currentThread.updatedAt = System.currentTimeMillis()
        if (currentThread.title == "Obrolan Baru") {
            val firstUser = currentThread.messages.firstOrNull { it.role == "user" }
            if (firstUser != null) {
                currentThread.title = firstUser.text.take(34)
            }
        }
        allThreads.removeAll { it.id == currentThread.id }
        allThreads.add(0, currentThread)
        repo.setActiveThreadId(currentThread.id)
        repo.saveAllThreads(allThreads)
    }

    private fun startForegroundNotification(withMediaProjection: Boolean) {
        val channelId = "floamini_os_channel"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(channelId, "Floamini OS Assistant", NotificationManager.IMPORTANCE_LOW)
            getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
        }

        val notification: Notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("Floamini OS")
            .setContentText(if (withMediaProjection) "Live Screen Vision aktif" else "Multi-AI Liquid Glass aktif")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .build()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            val type = if (withMediaProjection) {
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION or ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE
            } else {
                ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE
            }
            startForeground(101, notification, type)
        } else {
            startForeground(101, notification)
        }
    }

    private fun setupScreenMetrics() {
        val metrics = DisplayMetrics()
        val wm = getSystemService(WINDOW_SERVICE) as WindowManager
        @Suppress("DEPRECATION")
        wm.defaultDisplay.getRealMetrics(metrics)
        fullScreenWidth = metrics.widthPixels
        fullScreenHeight = metrics.heightPixels
        captureWidth = fullScreenWidth / 2
        captureHeight = fullScreenHeight / 2
        screenDensity = metrics.densityDpi
    }

    private fun setupFloatingOverlay() {
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        floatingView = LayoutInflater.from(this).inflate(R.layout.layout_floating_assistant, null)

        val layoutFlag = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        } else {
            @Suppress("DEPRECATION")
            WindowManager.LayoutParams.TYPE_PHONE
        }

        params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            layoutFlag,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = ((fullScreenWidth - prefIslandWidthPx) / 2) + prefIslandOffsetXPx
            y = prefIslandPosYPx
        }

        windowManager.addView(floatingView, params)
        isFloatingViewAttached = true

        // Bind Views
        dynamicIslandView = floatingView.findViewById(R.id.dynamicIslandView)
        ivIslandSparkle = floatingView.findViewById(R.id.ivIslandSparkle)
        tvIslandLabel = floatingView.findViewById(R.id.tvIslandLabel)
        viewIslandPulseDot = floatingView.findViewById(R.id.viewIslandPulseDot)
        bubbleView = floatingView.findViewById(R.id.bubbleView)
        xiaomiEdgeView = floatingView.findViewById(R.id.xiaomiEdgeView)
        popupChatView = floatingView.findViewById(R.id.popupChatView)

        val glassTitleBar = floatingView.findViewById<LinearLayout>(R.id.glassTitleBar)
        val btnCloseWindowX = floatingView.findViewById<ImageView>(R.id.btnCloseWindowX)
        val btnToggleMiniWindow = floatingView.findViewById<ImageView>(R.id.btnToggleMiniWindow)
        val btnSwitchProviderPill = floatingView.findViewById<LinearLayout>(R.id.btnSwitchProviderPill)
        tvActiveProviderHeader = floatingView.findViewById(R.id.tvActiveProviderHeader)
        btnScreenShare = floatingView.findViewById(R.id.btnScreenShare)
        val btnToolsDrawer = floatingView.findViewById<ImageView>(R.id.btnToolsDrawer)
        val btnPlusMenu = floatingView.findViewById<ImageView>(R.id.btnPlusMenu)

        tvScreenShareStatus = floatingView.findViewById(R.id.tvScreenShareStatus)
        attachmentPreviewBar = floatingView.findViewById(R.id.attachmentPreviewBar)
        tvAttachmentName = floatingView.findViewById(R.id.tvAttachmentName)
        val btnRemoveAttachment = floatingView.findViewById<TextView>(R.id.btnRemoveAttachment)

        val plusMenuDrawer = floatingView.findViewById<LinearLayout>(R.id.plusMenuDrawer)
        val smartToolsDrawer = floatingView.findViewById<LinearLayout>(R.id.smartToolsDrawer)

        val actionCompareAi = floatingView.findViewById<LinearLayout>(R.id.actionCompareAi)
        tvCompareBadge = floatingView.findViewById(R.id.tvCompareBadge)
        val actionRegenerate = floatingView.findViewById<LinearLayout>(R.id.actionRegenerate)
        val actionCyclePersona = floatingView.findViewById<LinearLayout>(R.id.actionCyclePersona)
        tvCurrentPersonaBadge = floatingView.findViewById(R.id.tvCurrentPersonaBadge)
        val actionCopyLast = floatingView.findViewById<LinearLayout>(R.id.actionCopyLast)
        val actionNewThread = floatingView.findViewById<LinearLayout>(R.id.actionNewThread)
        val actionOpenDashboard = floatingView.findViewById<LinearLayout>(R.id.actionOpenDashboard)
        val actionQuickForceStop = floatingView.findViewById<LinearLayout>(R.id.actionQuickForceStop)

        // 9 Quick Actions
        val qaTranslate = floatingView.findViewById<TextView>(R.id.qaTranslate)
        val qaSummarize = floatingView.findViewById<TextView>(R.id.qaSummarize)
        val qaRewrite = floatingView.findViewById<TextView>(R.id.qaRewrite)
        val qaExplain = floatingView.findViewById<TextView>(R.id.qaExplain)
        val qaBrainstorm = floatingView.findViewById<TextView>(R.id.qaBrainstorm)
        val qaCoding = floatingView.findViewById<TextView>(R.id.qaCoding)
        val qaGrammar = floatingView.findViewById<TextView>(R.id.qaGrammar)
        val qaExtractText = floatingView.findViewById<TextView>(R.id.qaExtractText)
        val qaAskSelection = floatingView.findViewById<TextView>(R.id.qaAskSelection)

        // Smart Tools
        val btnToolClipboard = floatingView.findViewById<Button>(R.id.btnToolClipboard)
        val btnToolCalculator = floatingView.findViewById<Button>(R.id.btnToolCalculator)
        val btnToolNotes = floatingView.findViewById<Button>(R.id.btnToolNotes)
        val btnToolHistory = floatingView.findViewById<Button>(R.id.btnToolHistory)
        val panelCalculator = floatingView.findViewById<LinearLayout>(R.id.panelCalculator)
        val etCalcExpression = floatingView.findViewById<EditText>(R.id.etCalcExpression)
        val tvCalcResult = floatingView.findViewById<TextView>(R.id.tvCalcResult)
        val btnEvalCalc = floatingView.findViewById<Button>(R.id.btnEvalCalc)
        val panelQuickNotes = floatingView.findViewById<LinearLayout>(R.id.panelQuickNotes)
        val etQuickNotes = floatingView.findViewById<EditText>(R.id.etQuickNotes)
        val btnSendNotesToAi = floatingView.findViewById<Button>(R.id.btnSendNotesToAi)
        val panelChatHistory = floatingView.findViewById<LinearLayout>(R.id.panelChatHistory)
        val etSearchChat = floatingView.findViewById<EditText>(R.id.etSearchChat)
        val historyThreadsList = floatingView.findViewById<LinearLayout>(R.id.historyThreadsList)

        scrollChat = floatingView.findViewById(R.id.scrollChat)
        chatContainer = floatingView.findViewById(R.id.chatContainer)
        typingIndicatorRow = floatingView.findViewById(R.id.typingIndicatorRow)
        tvThinkingLabel = floatingView.findViewById(R.id.tvThinkingLabel)
        val btnStopGeneration = floatingView.findViewById<TextView>(R.id.btnStopGeneration)

        voiceWaveformBar = floatingView.findViewById(R.id.voiceWaveformBar)
        tvVoiceStatusLabel = floatingView.findViewById(R.id.tvVoiceStatusLabel)
        voiceWaveformView = floatingView.findViewById(R.id.voiceWaveformView)
        val btnStopVoiceAction = floatingView.findViewById<TextView>(R.id.btnStopVoiceAction)

        val btnAttachFile = floatingView.findViewById<ImageButton>(R.id.btnAttachFile)
        val btnVoiceMic = floatingView.findViewById<ImageButton>(R.id.btnVoiceMic)
        etPrompt = floatingView.findViewById(R.id.etPrompt)
        btnSendPrompt = floatingView.findViewById(R.id.btnSendPrompt)
        val btnResizeHandle = floatingView.findViewById<ImageView>(R.id.btnResizeHandle)

        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        applyVisualPreferences()
        initializeThreads()
        showCollapsedTriggerState()

        // Tap outside window to close
        floatingView.setOnTouchListener { _, event ->
            if (event.action == MotionEvent.ACTION_OUTSIDE &&
                popupChatView.visibility == View.VISIBLE &&
                prefTapOutsideClose
            ) {
                triggerHaptic()
                closePopupChat()
                true
            } else {
                false
            }
        }

        // Smooth Model Switching directly from Header Pill
        btnSwitchProviderPill.setOnClickListener {
            triggerHaptic()
            val configured = vault.getConfiguredProviders()
            val pool = if (configured.isNotEmpty()) configured else AiProviderType.values().toList()
            val nextIdx = (pool.indexOf(activeProvider) + 1) % pool.size
            activeProvider = pool[nextIdx]
            prefs.edit().putString("active_provider_id", activeProvider.id).apply()

            btnSwitchProviderPill.animate().scaleX(0.92f).scaleY(0.92f).setDuration(90).withEndAction {
                applyVisualPreferences()
                btnSwitchProviderPill.animate().scaleX(1f).scaleY(1f).setDuration(120).start()
            }.start()
            Toast.makeText(this, "Beralih ke ${activeProvider.displayName}", Toast.LENGTH_SHORT).show()
        }

        // Toggle Mini Window vs Full Floating Window
        btnToggleMiniWindow.setOnClickListener {
            triggerHaptic()
            isMiniWindowMode = !isMiniWindowMode
            val density = resources.displayMetrics.density
            val lp = popupChatView.layoutParams
            if (isMiniWindowMode) {
                lp.width = (280 * density).toInt()
                lp.height = (255 * density).toInt()
                Toast.makeText(this, "Mini Window Mode", Toast.LENGTH_SHORT).show()
            } else {
                lp.width = prefs.getInt("last_win_w", (352 * density).toInt())
                lp.height = prefs.getInt("last_win_h", (500 * density).toInt())
                Toast.makeText(this, "Full Floating Window", Toast.LENGTH_SHORT).show()
            }
            popupChatView.layoutParams = lp
            windowManager.updateViewLayout(floatingView, params)
        }

        // Dynamic Island Touch & Drag
        dynamicIslandView.setOnTouchListener(object : View.OnTouchListener {
            private var initialX = 0
            private var initialY = 0
            private var initialTouchX = 0f
            private var initialTouchY = 0f

            override fun onTouch(v: View, event: MotionEvent): Boolean {
                when (event.action) {
                    MotionEvent.ACTION_DOWN -> {
                        wakeFromSmartFreeze()
                        mainHandler.removeCallbacks(autoHidePillRunnable)
                        initialX = params.x
                        initialY = params.y
                        initialTouchX = event.rawX
                        initialTouchY = event.rawY
                        animateSpringScale(dynamicIslandView, 1.07f)
                        return true
                    }
                    MotionEvent.ACTION_MOVE -> {
                        val dx = (event.rawX - initialTouchX).toInt()
                        val dy = (event.rawY - initialTouchY).toInt()
                        if (abs(dx) > 12 || abs(dy) > 12) {
                            params.x = (initialX + dx).coerceIn(12, (fullScreenWidth - prefIslandWidthPx - 12).coerceAtLeast(12))
                            params.y = (initialY + dy).coerceIn(0, fullScreenHeight / 2)
                            windowManager.updateViewLayout(floatingView, params)
                        }
                        return true
                    }
                    MotionEvent.ACTION_UP -> {
                        animateSpringScale(dynamicIslandView, 1.0f)
                        if (abs(event.rawX - initialTouchX) < 18 && abs(event.rawY - initialTouchY) < 18) {
                            triggerHaptic()
                            isPillAutoHidden = false
                            dynamicIslandView.alpha = 1.0f
                            openPopupChat(fromSiri = false)
                        } else {
                            scheduleAutoHideAndFreeze()
                        }
                        return true
                    }
                }
                return false
            }
        })

        // Bubble Touch & Snap
        bubbleView.setOnTouchListener(object : View.OnTouchListener {
            private var initialX = 0
            private var initialY = 0
            private var initialTouchX = 0f
            private var initialTouchY = 0f

            override fun onTouch(v: View, event: MotionEvent): Boolean {
                when (event.action) {
                    MotionEvent.ACTION_DOWN -> {
                        wakeFromSmartFreeze()
                        mainHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
                        initialX = params.x
                        initialY = params.y
                        initialTouchX = event.rawX
                        initialTouchY = event.rawY
                        return true
                    }
                    MotionEvent.ACTION_MOVE -> {
                        params.x = (initialX + (event.rawX - initialTouchX).toInt()).coerceIn(0, fullScreenWidth - prefBubbleSizePx)
                        params.y = (initialY + (event.rawY - initialTouchY).toInt()).coerceIn(0, fullScreenHeight - prefBubbleSizePx)
                        windowManager.updateViewLayout(floatingView, params)
                        return true
                    }
                    MotionEvent.ACTION_UP -> {
                        if (abs(event.rawX - initialTouchX) < 15 && abs(event.rawY - initialTouchY) < 15) {
                            triggerHaptic()
                            openPopupChat(fromSiri = false)
                        } else {
                            snapBubbleToNearestEdge()
                        }
                        return true
                    }
                }
                return false
            }
        })

        // Xiaomi Edge Pill
        xiaomiEdgeView.setOnTouchListener(object : View.OnTouchListener {
            private var initialY = 0
            private var initialTouchX = 0f
            private var initialTouchY = 0f

            override fun onTouch(v: View, event: MotionEvent): Boolean {
                when (event.action) {
                    MotionEvent.ACTION_DOWN -> {
                        wakeFromSmartFreeze()
                        initialY = params.y
                        initialTouchX = event.rawX
                        initialTouchY = event.rawY
                        return true
                    }
                    MotionEvent.ACTION_MOVE -> {
                        params.y = (initialY + (event.rawY - initialTouchY).toInt()).coerceIn(0, fullScreenHeight - 180)
                        windowManager.updateViewLayout(floatingView, params)
                        return true
                    }
                    MotionEvent.ACTION_UP -> {
                        val diffX = event.rawX - initialTouchX
                        val swipedInward = (snappedToRightEdge && diffX < -45) || (!snappedToRightEdge && diffX > 45)
                        triggerHaptic()
                        if (swipedInward) openPopupChat(fromSiri = false) else exitXiaomiEdgeMode()
                        return true
                    }
                }
                return false
            }
        })

        // Drag Window & Remember Position
        glassTitleBar.setOnTouchListener(object : View.OnTouchListener {
            private var initialX = 0
            private var initialY = 0
            private var initialTouchX = 0f
            private var initialTouchY = 0f

            override fun onTouch(v: View, event: MotionEvent): Boolean {
                when (event.action) {
                    MotionEvent.ACTION_DOWN -> {
                        initialX = params.x
                        initialY = params.y
                        initialTouchX = event.rawX
                        initialTouchY = event.rawY
                        return true
                    }
                    MotionEvent.ACTION_MOVE -> {
                        val maxW = (fullScreenWidth - popupChatView.width).coerceAtLeast(0)
                        val maxH = (fullScreenHeight - popupChatView.height).coerceAtLeast(0)
                        params.x = (initialX + (event.rawX - initialTouchX).toInt()).coerceIn(0, maxW)
                        params.y = (initialY + (event.rawY - initialTouchY).toInt()).coerceIn(0, maxH)
                        windowManager.updateViewLayout(floatingView, params)
                        return true
                    }
                    MotionEvent.ACTION_UP -> {
                        prefs.edit()
                            .putInt("last_win_x", params.x)
                            .putInt("last_win_y", params.y)
                            .apply()
                        return true
                    }
                }
                return false
            }
        })

        // Resize Window & Remember Size
        btnResizeHandle.setOnTouchListener(object : View.OnTouchListener {
            private var initialW = 0
            private var initialH = 0
            private var initialTouchX = 0f
            private var initialTouchY = 0f

            override fun onTouch(v: View, event: MotionEvent): Boolean {
                val density = resources.displayMetrics.density
                val minW = (275 * density).toInt()
                val minH = (250 * density).toInt()
                val maxW = (fullScreenWidth * 0.96f).toInt()
                val maxH = (fullScreenHeight * 0.84f).toInt()

                when (event.action) {
                    MotionEvent.ACTION_DOWN -> {
                        initialW = popupChatView.width
                        initialH = popupChatView.height
                        initialTouchX = event.rawX
                        initialTouchY = event.rawY
                        return true
                    }
                    MotionEvent.ACTION_MOVE -> {
                        val newW = (initialW + (event.rawX - initialTouchX).toInt()).coerceIn(minW, maxW)
                        val newH = (initialH + (event.rawY - initialTouchY).toInt()).coerceIn(minH, maxH)
                        val lp = popupChatView.layoutParams
                        lp.width = newW
                        lp.height = newH
                        popupChatView.layoutParams = lp
                        windowManager.updateViewLayout(floatingView, params)
                        return true
                    }
                    MotionEvent.ACTION_UP -> {
                        prefs.edit()
                            .putInt("last_win_w", popupChatView.width)
                            .putInt("last_win_h", popupChatView.height)
                            .apply()
                        return true
                    }
                }
                return false
            }
        })

        btnCloseWindowX.setOnClickListener {
            triggerHaptic()
            closePopupChat()
        }

        btnScreenShare.setOnClickListener {
            triggerHaptic()
            if (!isScreenShareActive) {
                startActivity(Intent(this, ScreenCapturePermissionActivity::class.java).apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                })
            } else {
                stopMediaProjection()
                Toast.makeText(this, "Screen Vision dihentikan", Toast.LENGTH_SHORT).show()
            }
        }

        btnPlusMenu.setOnClickListener {
            triggerHaptic()
            smartToolsDrawer.visibility = View.GONE
            val show = plusMenuDrawer.visibility != View.VISIBLE
            plusMenuDrawer.visibility = if (show) View.VISIBLE else View.GONE
            btnPlusMenu.animate().rotation(if (show) 45f else 0f).setDuration(200).start()
        }

        btnToolsDrawer.setOnClickListener {
            triggerHaptic()
            plusMenuDrawer.visibility = View.GONE
            btnPlusMenu.animate().rotation(0f).setDuration(200).start()
            val show = smartToolsDrawer.visibility != View.VISIBLE
            smartToolsDrawer.visibility = if (show) View.VISIBLE else View.GONE
            if (show) {
                etQuickNotes.setText(repo.getQuickNotes())
                refreshHistoryList(historyThreadsList, "")
            }
        }

        // Plus Menu Actions
        actionCompareAi.setOnClickListener {
            triggerHaptic()
            isCompareMode = !isCompareMode
            tvCompareBadge.text = if (isCompareMode) "Compare AI: ON" else "Compare AI: OFF"
            tvCompareBadge.setTextColor(Color.parseColor(if (isCompareMode) "#34D399" else "#38BDF8"))
            Toast.makeText(
                this,
                if (isCompareMode) "Compare AI aktif: membandingkan 2 provider sekaligus" else "Compare AI dimatikan",
                Toast.LENGTH_SHORT
            ).show()
        }

        actionRegenerate.setOnClickListener {
            if (lastUserPrompt.isNotEmpty()) {
                plusMenuDrawer.visibility = View.GONE
                btnPlusMenu.animate().rotation(0f).setDuration(180).start()
                triggerSendPrompt(lastUserPrompt, fromVoice = false, isRegenerate = true)
            } else {
                Toast.makeText(this, "Belum ada pertanyaan untuk diulang", Toast.LENGTH_SHORT).show()
            }
        }

        actionCyclePersona.setOnClickListener {
            triggerHaptic()
            prefPersona = when (prefPersona) {
                "asik" -> "ringkas"
                "ringkas" -> "detail"
                "detail" -> "teknis"
                else -> "asik"
            }
            prefs.edit().putString("ai_persona", prefPersona).apply()
            applyVisualPreferences()
        }

        actionCopyLast.setOnClickListener {
            if (lastBotReply.isNotEmpty()) {
                val cb = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                cb.setPrimaryClip(ClipData.newPlainText("Floamini Reply", lastBotReply))
                Toast.makeText(this, "Jawaban terakhir disalin", Toast.LENGTH_SHORT).show()
            }
        }

        actionNewThread.setOnClickListener {
            triggerHaptic()
            startNewConversationThread()
            plusMenuDrawer.visibility = View.GONE
            btnPlusMenu.animate().rotation(0f).setDuration(180).start()
            Toast.makeText(this, "Sesi obrolan baru dimulai", Toast.LENGTH_SHORT).show()
        }

        actionOpenDashboard.setOnClickListener {
            closePopupChat()
            startActivity(Intent(this, MainActivity::class.java).apply { addFlags(Intent.FLAG_ACTIVITY_NEW_TASK) })
        }

        actionQuickForceStop.setOnClickListener {
            triggerHaptic()
            performQuickForceStop()
        }

        // 9 Quick Actions
        qaTranslate.setOnClickListener { triggerSendPrompt("Terjemahkan teks atau konten layar ini ke Bahasa Indonesia yang natural.") }
        qaSummarize.setOnClickListener { triggerSendPrompt("Ringkas poin-poin terpenting dari konteks atau layar ini secara padat.") }
        qaRewrite.setOnClickListener { triggerSendPrompt("Tulis ulang teks terakhir agar lebih rapi, jelas, dan enak dibaca.") }
        qaExplain.setOnClickListener { triggerSendPrompt("Jelaskan konsep atau isi layar ini dengan bahasa yang mudah dipahami.") }
        qaBrainstorm.setOnClickListener { triggerSendPrompt("Berikan 5 ide kreatif dan segar terkait topik yang sedang kita bahas.") }
        qaCoding.setOnClickListener { triggerSendPrompt("Bantu analisis, perbaiki bug, atau tulis kode bersih untuk kebutuhan ini.") }
        qaGrammar.setOnClickListener { triggerSendPrompt("Periksa dan perbaiki tata bahasa (grammar & ejaan) pada teks terakhir.") }
        qaExtractText.setOnClickListener { triggerSendPrompt("Ekstrak seluruh teks penting yang terlihat pada gambar atau layar secara rapi.") }
        qaAskSelection.setOnClickListener {
            // Explicit user action: read clipboard only when button is tapped
            val cb = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            val clipText = cb.primaryClip?.getItemAt(0)?.coerceToText(this)?.toString()?.trim() ?: ""
            if (clipText.isNotEmpty()) {
                triggerSendPrompt("Bantu jelaskan atau proses teks dari clipboard ini:\n\"$clipText\"")
            } else {
                Toast.makeText(this, "Clipboard saat ini kosong", Toast.LENGTH_SHORT).show()
            }
        }

        // Smart Tools Drawer Buttons
        btnToolClipboard.setOnClickListener {
            val cb = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            val clipText = cb.primaryClip?.getItemAt(0)?.coerceToText(this)?.toString()?.trim() ?: ""
            if (clipText.isNotEmpty()) {
                etPrompt.setText("Analisis teks clipboard ini:\n$clipText")
                smartToolsDrawer.visibility = View.GONE
            } else {
                Toast.makeText(this, "Clipboard kosong", Toast.LENGTH_SHORT).show()
            }
        }

        btnToolCalculator.setOnClickListener {
            panelCalculator.visibility = if (panelCalculator.visibility == View.VISIBLE) View.GONE else View.VISIBLE
            panelQuickNotes.visibility = View.GONE
            panelChatHistory.visibility = View.GONE
        }

        btnEvalCalc.setOnClickListener {
            val expr = etCalcExpression.text.toString()
            tvCalcResult.text = "= ${SmartToolsHelper.evaluateMathExpression(expr)}"
        }

        btnToolNotes.setOnClickListener {
            panelQuickNotes.visibility = if (panelQuickNotes.visibility == View.VISIBLE) View.GONE else View.VISIBLE
            panelCalculator.visibility = View.GONE
            panelChatHistory.visibility = View.GONE
        }

        etQuickNotes.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                repo.saveQuickNotes(s?.toString() ?: "")
            }
            override fun afterTextChanged(s: Editable?) {}
        })

        btnSendNotesToAi.setOnClickListener {
            val note = etQuickNotes.text.toString().trim()
            if (note.isNotEmpty()) {
                smartToolsDrawer.visibility = View.GONE
                triggerSendPrompt("Bantu rapikan atau kembangkan catatan cepat berikut:\n$note")
            }
        }

        btnToolHistory.setOnClickListener {
            panelChatHistory.visibility = if (panelChatHistory.visibility == View.VISIBLE) View.GONE else View.VISIBLE
            panelCalculator.visibility = View.GONE
            panelQuickNotes.visibility = View.GONE
            refreshHistoryList(historyThreadsList, etSearchChat.text.toString())
        }

        etSearchChat.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                refreshHistoryList(historyThreadsList, s?.toString() ?: "")
            }
            override fun afterTextChanged(s: Editable?) {}
        })

        // Attachments (PDF, Image, File)
        btnAttachFile.setOnClickListener {
            triggerHaptic()
            startActivity(Intent(this, FilePickerProxyActivity::class.java).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            })
        }

        btnRemoveAttachment.setOnClickListener {
            pendingAttachment = null
            attachmentPreviewBar.visibility = View.GONE
        }

        // Voice System Controls
        btnVoiceMic.setOnClickListener {
            if (voiceManager?.isListening == true) {
                voiceManager?.stopListening()
            } else {
                startVoiceChatSession()
            }
        }

        btnStopVoiceAction.setOnClickListener {
            isVoiceChatLoop = false
            voiceManager?.stopListening()
            voiceManager?.stopSpeaking()
            voiceWaveformView.stopAnimation()
            voiceWaveformBar.visibility = View.GONE
        }

        // Stop Generation Button
        btnStopGeneration.setOnClickListener {
            activeGenerationJob?.cancel()
            typingIndicatorRow.visibility = View.GONE
            btnSendPrompt.isEnabled = true
            tvIslandLabel.text = "Floamini"
            Toast.makeText(this, "Generasi dihentikan", Toast.LENGTH_SHORT).show()
        }

        // Send Prompt
        btnSendPrompt.setOnClickListener {
            isVoiceChatLoop = false
            triggerSendPrompt(etPrompt.text.toString(), fromVoice = false)
        }
    }

    private fun refreshHistoryList(container: LinearLayout, query: String) {
        container.removeAllViews()
        val matches = repo.searchThreads(query).take(5)
        if (matches.isEmpty()) {
            val emptyTv = TextView(this).apply {
                text = "Tidak ada riwayat cocok"
                textSize = 11f
                setTextColor(Color.parseColor("#94A3B8"))
                setPadding(6, 6, 6, 6)
            }
            container.addView(emptyTv)
            return
        }

        for (thread in matches) {
            val row = TextView(this).apply {
                text = "• ${thread.title} (${thread.messages.size} pesan)"
                textSize = 11.5f
                setTextColor(Color.parseColor("#E2E8F0"))
                setPadding(8, 8, 8, 8)
                setOnClickListener {
                    currentThread = thread
                    repo.setActiveThreadId(thread.id)
                    renderCurrentThreadMessages()
                    floatingView.findViewById<LinearLayout>(R.id.smartToolsDrawer).visibility = View.GONE
                }
            }
            container.addView(row)
        }
    }

    // ==========================================================================
    // SEND PROMPT, SSE STREAMING, COMPARE AI & AUTO-ROUTER
    // ==========================================================================
    private fun triggerSendPrompt(rawPrompt: String, fromVoice: Boolean = false, isRegenerate: Boolean = false) {
        val prompt = rawPrompt.trim()
        if (prompt.isEmpty()) return

        val attachment = pendingAttachment
        pendingAttachment = null
        attachmentPreviewBar.visibility = View.GONE

        val imagesList = mutableListOf<String>()
        if (isScreenShareActive) {
            captureCurrentScreenBase64()?.let { imagesList.add(it) }
        }
        if (attachment != null) {
            imagesList.addAll(attachment.imageBase64List)
        }

        val combinedPrompt = if (attachment != null && attachment.extractedText.isNotBlank()) {
            "$prompt\n\n--- Isi Lampiran (${attachment.displayName}) ---\n${attachment.extractedText}"
        } else {
            prompt
        }

        val chosenProvider = if (prefAutoRouter) {
            AiEngineRegistry.resolveAutoRoute(vault, activeProvider, combinedPrompt, imagesList.isNotEmpty())
        } else {
            activeProvider
        }

        val apiKey = vault.getApiKey(chosenProvider)
        if (apiKey.isEmpty()) {
            Toast.makeText(this, "API Key ${chosenProvider.displayName} belum diisi! Buka Settings.", Toast.LENGTH_LONG).show()
            return
        }

        floatingView.findViewById<LinearLayout>(R.id.plusMenuDrawer).visibility = View.GONE
        floatingView.findViewById<LinearLayout>(R.id.smartToolsDrawer).visibility = View.GONE
        floatingView.findViewById<ImageView>(R.id.btnPlusMenu).animate().rotation(0f).setDuration(180).start()

        wakeFromSmartFreeze()
        triggerHaptic()
        lastUserPrompt = prompt

        if (!isRegenerate) {
            val userMsg = ChatMessage(
                id = UUID.randomUUID().toString(),
                role = "user",
                text = prompt,
                timestamp = currentTimeLabel(),
                attachmentLabel = attachment?.displayName
            )
            currentThread.messages.add(userMsg)
            addChatBubbleView(userMsg, animateEntrance = true)
        }

        etPrompt.text.clear()
        btnSendPrompt.isEnabled = false
        typingIndicatorRow.visibility = View.VISIBLE
        tvIslandLabel.text = "Streaming..."

        activeGenerationJob?.cancel()
        activeGenerationJob = serviceScope.launch {
            if (isCompareMode) {
                executeDualCompareStream(chosenProvider, combinedPrompt, imagesList)
            } else {
                executeSingleProviderStream(chosenProvider, apiKey, combinedPrompt, imagesList, fromVoice)
            }
        }
    }

    private suspend fun executeSingleProviderStream(
        provider: AiProviderType,
        apiKey: String,
        promptText: String,
        imagesList: List<String>,
        fromVoice: Boolean
    ) {
        val modelId = vault.getSelectedModel(provider)
        tvThinkingLabel.text = "${provider.shortBadge} ($modelId) sedang mengetik..."

        val botTime = currentTimeLabel()
        val streamingTv = addStreamingBotBubble(provider.shortBadge, modelId, botTime)
        val buffer = StringBuilder()

        val payload = AiRequestPayload(
            provider = provider,
            apiKey = apiKey,
            model = modelId,
            customBaseUrl = vault.getCustomBaseUrl(),
            systemInstruction = buildSystemInstructionText(),
            history = currentThread.messages.dropLast(1).takeLast(14),
            userPrompt = promptText,
            imageBase64List = imagesList
        )

        AiEngineRegistry.getAdapter(provider).streamChat(payload).collect { event ->
            when (event) {
                is StreamEvent.Delta -> {
                    buffer.append(event.chunk)
                    streamingTv.text = "${buffer} ▍"
                    scrollChat.post { scrollChat.fullScroll(View.FOCUS_DOWN) }
                }
                is StreamEvent.Completed -> {
                    val finalReply = event.fullText.ifBlank { "Respons kosong dari ${provider.shortBadge}." }
                    streamingTv.text = SmartToolsHelper.formatRichMarkdown(finalReply)
                    lastBotReply = finalReply

                    val botMsg = ChatMessage(
                        id = UUID.randomUUID().toString(),
                        role = "model",
                        text = finalReply,
                        timestamp = botTime,
                        providerBadge = provider.shortBadge,
                        modelName = modelId
                    )
                    currentThread.messages.add(botMsg)
                    persistCurrentThread()
                    repo.recordUsage(provider, event.estimatedTokens)

                    typingIndicatorRow.visibility = View.GONE
                    btnSendPrompt.isEnabled = true
                    tvIslandLabel.text = if (isScreenShareActive) "Live Vision" else "Floamini"
                    triggerHaptic()

                    if ((fromVoice || isVoiceChatLoop) && prefAutoSpeakTts) {
                        val plainForSpeech = finalReply.replace("```", " ").replace("**", "").replace("`", "")
                        voiceManager?.speak(plainForSpeech, 1.05f, prefTtsVoiceName)
                    }
                }
                is StreamEvent.Error -> {
                    streamingTv.text = event.message
                    streamingTv.setTextColor(Color.parseColor("#FCA5A5"))
                    typingIndicatorRow.visibility = View.GONE
                    btnSendPrompt.isEnabled = true
                    tvIslandLabel.text = "Floamini"
                }
            }
        }
    }

    private suspend fun executeDualCompareStream(
        primary: AiProviderType,
        promptText: String,
        imagesList: List<String>
    ) {
        val configured = vault.getConfiguredProviders()
        val secondary = configured.firstOrNull { it != primary } ?: primary
        tvThinkingLabel.text = "Membandingkan ${primary.shortBadge} vs ${secondary.shortBadge}..."

        val (tvLeft, tvRight) = addSideBySideCompareCards(primary.shortBadge, secondary.shortBadge)
        val bufLeft = StringBuilder()
        val bufRight = StringBuilder()

        val job1 = serviceScope.async {
            val payload1 = AiRequestPayload(
                provider = primary,
                apiKey = vault.getApiKey(primary),
                model = vault.getSelectedModel(primary),
                customBaseUrl = vault.getCustomBaseUrl(),
                systemInstruction = buildSystemInstructionText(),
                history = currentThread.messages.dropLast(1).takeLast(10),
                userPrompt = promptText,
                imageBase64List = imagesList
            )
            AiEngineRegistry.getAdapter(primary).streamChat(payload1).collect { ev ->
                when (ev) {
                    is StreamEvent.Delta -> {
                        bufLeft.append(ev.chunk)
                        tvLeft.text = "${bufLeft} ▍"
                    }
                    is StreamEvent.Completed -> {
                        tvLeft.text = SmartToolsHelper.formatRichMarkdown(ev.fullText)
                        repo.recordUsage(primary, ev.estimatedTokens)
                    }
                    is StreamEvent.Error -> tvLeft.text = ev.message
                }
            }
        }

        val job2 = serviceScope.async {
            val payload2 = AiRequestPayload(
                provider = secondary,
                apiKey = vault.getApiKey(secondary),
                model = vault.getSelectedModel(secondary),
                customBaseUrl = vault.getCustomBaseUrl(),
                systemInstruction = buildSystemInstructionText(),
                history = currentThread.messages.dropLast(1).takeLast(10),
                userPrompt = promptText,
                imageBase64List = imagesList
            )
            AiEngineRegistry.getAdapter(secondary).streamChat(payload2).collect { ev ->
                when (ev) {
                    is StreamEvent.Delta -> {
                        bufRight.append(ev.chunk)
                        tvRight.text = "${bufRight} ▍"
                        scrollChat.post { scrollChat.fullScroll(View.FOCUS_DOWN) }
                    }
                    is StreamEvent.Completed -> {
                        tvRight.text = SmartToolsHelper.formatRichMarkdown(ev.fullText)
                        repo.recordUsage(secondary, ev.estimatedTokens)
                    }
                    is StreamEvent.Error -> tvRight.text = ev.message
                }
            }
        }

        awaitAll(job1, job2)
        val mergedSummary = "[${primary.shortBadge}]: $bufLeft\n\n[${secondary.shortBadge}]: $bufRight"
        lastBotReply = mergedSummary
        currentThread.messages.add(
            ChatMessage(UUID.randomUUID().toString(), "model", mergedSummary, currentTimeLabel(), "Compare")
        )
        persistCurrentThread()
        typingIndicatorRow.visibility = View.GONE
        btnSendPrompt.isEnabled = true
        tvIslandLabel.text = "Floamini"
        triggerHaptic()
    }

    // ==========================================================================
    // CHAT BUBBLES & STAGGERED ENTRANCE ANIMATION
    // ==========================================================================
    private fun addChatBubbleView(msg: ChatMessage, animateEntrance: Boolean) {
        val isUser = (msg.role == "user")
        val wrapper = LinearLayout(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 6, 0, 6) }
            orientation = LinearLayout.VERTICAL
            gravity = if (isUser) Gravity.END else Gravity.START
        }

        val tvMessage = TextView(this).apply {
            text = if (isUser) msg.text else SmartToolsHelper.formatRichMarkdown(msg.text)
            textSize = 13f
            lineHeight = (19 * resources.displayMetrics.density).toInt()
            setTextColor(Color.parseColor("#F8FAFC"))
            setPadding(26, 16, 26, 16)
            maxWidth = (264 * resources.displayMetrics.density).toInt()
            setBackgroundResource(if (isUser) R.drawable.bg_chat_user else R.drawable.bg_chat_bot)
            setOnClickListener {
                val cb = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                cb.setPrimaryClip(ClipData.newPlainText("Floamini Message", msg.text))
                Toast.makeText(this@FloatingAssistantService, "Pesan disalin", Toast.LENGTH_SHORT).show()
            }
        }

        val metaText = if (isUser) {
            val att = if (!msg.attachmentLabel.isNullOrEmpty()) " • ${msg.attachmentLabel}" else ""
            "Kamu • ${msg.timestamp}$att"
        } else {
            "${msg.providerBadge} • ${msg.timestamp}"
        }

        val tvTime = TextView(this).apply {
            text = metaText
            textSize = 9.5f
            setTextColor(Color.parseColor("#64748B"))
            setPadding(8, 3, 8, 0)
        }

        wrapper.addView(tvMessage)
        wrapper.addView(tvTime)
        chatContainer.addView(wrapper)

        if (animateEntrance) {
            wrapper.alpha = 0f
            wrapper.translationY = 18f
            wrapper.animate()
                .alpha(1f)
                .translationY(0f)
                .setDuration((210 / prefAnimSpeedMultiplier).toLong())
                .setInterpolator(DecelerateInterpolator())
                .start()
        }
        scrollChat.post { scrollChat.fullScroll(View.FOCUS_DOWN) }
    }

    private fun addStreamingBotBubble(providerBadge: String, modelName: String, timeLabel: String): TextView {
        val wrapper = LinearLayout(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 6, 0, 6) }
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.START
        }

        val tvMessage = TextView(this).apply {
            text = "▍"
            textSize = 13f
            lineHeight = (19 * resources.displayMetrics.density).toInt()
            setTextColor(Color.parseColor("#F8FAFC"))
            setPadding(26, 16, 26, 16)
            maxWidth = (264 * resources.displayMetrics.density).toInt()
            setBackgroundResource(R.drawable.bg_chat_bot)
        }

        val tvTime = TextView(this).apply {
            text = "$providerBadge ($modelName) • $timeLabel"
            textSize = 9.5f
            setTextColor(Color.parseColor("#38BDF8"))
            setPadding(8, 3, 8, 0)
        }

        wrapper.addView(tvMessage)
        wrapper.addView(tvTime)
        chatContainer.addView(wrapper)
        scrollChat.post { scrollChat.fullScroll(View.FOCUS_DOWN) }
        return tvMessage
    }

    private fun addSideBySideCompareCards(leftTitle: String, rightTitle: String): Pair<TextView, TextView> {
        val row = LinearLayout(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 6, 0, 6) }
            orientation = LinearLayout.HORIZONTAL
        }

        fun createCol(title: String): Pair<LinearLayout, TextView> {
            val col = LinearLayout(this).apply {
                layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f).apply {
                    setMargins(3, 0, 3, 0)
                }
                orientation = LinearLayout.VERTICAL
                setBackgroundResource(R.drawable.bg_chat_bot)
                setPadding(16, 12, 16, 12)
            }
            val header = TextView(this).apply {
                text = title
                textSize = 10.5f
                setTextColor(Color.parseColor("#38BDF8"))
            }
            val body = TextView(this).apply {
                text = "▍"
                textSize = 12f
                setTextColor(Color.parseColor("#F8FAFC"))
            }
            col.addView(header)
            col.addView(body)
            return col to body
        }

        val (col1, tv1) = createCol(leftTitle)
        val (col2, tv2) = createCol(rightTitle)
        row.addView(col1)
        row.addView(col2)
        chatContainer.addView(row)
        return tv1 to tv2
    }

    // ==========================================================================
    // SPRING ANIMATIONS & WINDOW TRANSITIONS
    // ==========================================================================
    private fun animateSpringScale(target: View, finalScale: Float) {
        val stiff = SpringForce.STIFFNESS_MEDIUM * prefAnimSpeedMultiplier
        SpringAnimation(target, DynamicAnimation.SCALE_X, finalScale).apply {
            spring.dampingRatio = SpringForce.DAMPING_RATIO_LOW_BOUNCY
            spring.stiffness = stiff
            start()
        }
        SpringAnimation(target, DynamicAnimation.SCALE_Y, finalScale).apply {
            spring.dampingRatio = SpringForce.DAMPING_RATIO_LOW_BOUNCY
            spring.stiffness = stiff
            start()
        }
    }

    private fun scheduleAutoHideAndFreeze() {
        mainHandler.removeCallbacks(autoHidePillRunnable)
        if (prefAutoHidePill && prefOverlayStyle == "dynamic_island") {
            mainHandler.postDelayed(autoHidePillRunnable, 3000L)
        }
        scheduleSmartFreeze()
    }

    private fun showCollapsedTriggerState() {
        mainHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
        mainHandler.removeCallbacks(autoHidePillRunnable)
        dismissSiriAura()

        popupChatView.visibility = View.GONE
        dynamicIslandView.visibility = View.GONE
        bubbleView.visibility = View.GONE
        xiaomiEdgeView.visibility = View.GONE
        isPillAutoHidden = false

        params.flags = WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN
        applyWindowBlur(enabled = false)

        when (prefOverlayStyle) {
            "siri_mode" -> {
                if (isFloatingViewAttached) windowManager.updateViewLayout(floatingView, params)
                if (prefSmartFreeze) enterSmartFreezeState()
            }
            "xiaomi_edge" -> {
                wakeFromSmartFreeze()
                bubbleView.visibility = View.VISIBLE
                bubbleView.alpha = 1.0f
                params.x = if (snappedToRightEdge) (fullScreenWidth - prefBubbleSizePx) else 0
                params.y = fullScreenHeight / 3
                windowManager.updateViewLayout(floatingView, params)
                mainHandler.postDelayed(transformToXiaomiEdgeRunnable, 2500L)
                scheduleSmartFreeze()
            }
            "classic_bubble" -> {
                wakeFromSmartFreeze()
                bubbleView.visibility = View.VISIBLE
                bubbleView.alpha = 1.0f
                params.x = if (snappedToRightEdge) (fullScreenWidth - prefBubbleSizePx) else 0
                params.y = fullScreenHeight / 3
                windowManager.updateViewLayout(floatingView, params)
                scheduleSmartFreeze()
            }
            else -> {
                wakeFromSmartFreeze()
                dynamicIslandView.visibility = View.VISIBLE
                dynamicIslandView.scaleX = 0.72f
                dynamicIslandView.scaleY = 0.72f
                dynamicIslandView.alpha = 1.0f
                params.x = (((fullScreenWidth - prefIslandWidthPx) / 2) + prefIslandOffsetXPx)
                    .coerceIn(12, (fullScreenWidth - prefIslandWidthPx - 12).coerceAtLeast(12))
                params.y = prefIslandPosYPx
                windowManager.updateViewLayout(floatingView, params)
                animateSpringScale(dynamicIslandView, 1.0f)
                scheduleAutoHideAndFreeze()
            }
        }
    }

    private fun openPopupChat(fromSiri: Boolean) {
        wakeFromSmartFreeze()
        mainHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
        mainHandler.removeCallbacks(autoHidePillRunnable)

        dynamicIslandView.visibility = View.GONE
        xiaomiEdgeView.visibility = View.GONE
        bubbleView.visibility = View.GONE

        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        val density = resources.displayMetrics.density
        val savedW = prefs.getInt("last_win_w", (352 * density).toInt())
        val savedH = prefs.getInt("last_win_h", (500 * density).toInt())
        val lp = popupChatView.layoutParams
        lp.width = if (isMiniWindowMode) (280 * density).toInt() else savedW
        lp.height = if (isMiniWindowMode) (255 * density).toInt() else savedH
        popupChatView.layoutParams = lp

        popupChatView.visibility = View.VISIBLE
        popupChatView.pivotX = lp.width / 2f
        popupChatView.pivotY = if (fromSiri) lp.height.toFloat() else 0f
        popupChatView.scaleX = 0.55f
        popupChatView.scaleY = 0.35f
        popupChatView.alpha = 0f

        val defaultX = ((fullScreenWidth - lp.width) / 2).coerceIn(16, (fullScreenWidth - lp.width - 16).coerceAtLeast(16))
        val defaultY = if (fromSiri) ((fullScreenHeight - lp.height) / 2).coerceIn(32, fullScreenHeight / 3)
        else (prefIslandPosYPx + (14 * density).toInt()).coerceIn(24, fullScreenHeight / 4)

        params.x = prefs.getInt("last_win_x", defaultX).coerceIn(0, (fullScreenWidth - lp.width).coerceAtLeast(0))
        params.y = prefs.getInt("last_win_y", defaultY).coerceIn(0, (fullScreenHeight - lp.height).coerceAtLeast(0))
        params.flags = WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL or
                WindowManager.LayoutParams.FLAG_WATCH_OUTSIDE_TOUCH or
                WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN

        applyWindowBlur(enabled = prefLiquidBlur)
        windowManager.updateViewLayout(floatingView, params)

        popupChatView.animate()
            .alpha(prefPopupAlpha)
            .setDuration((240 / prefAnimSpeedMultiplier).toLong())
            .start()
        animateSpringScale(popupChatView, 1.0f)
    }

    private fun closePopupChat() {
        voiceManager?.stopListening()
        voiceManager?.stopSpeaking()
        popupChatView.animate()
            .scaleX(0.45f)
            .scaleY(0.22f)
            .alpha(0f)
            .setDuration((190 / prefAnimSpeedMultiplier).toLong())
            .setInterpolator(DecelerateInterpolator())
            .withEndAction { showCollapsedTriggerState() }
            .start()
    }

    private fun applyWindowBlur(enabled: Boolean) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            try {
                if (enabled) {
                    params.flags = params.flags or WindowManager.LayoutParams.FLAG_BLUR_BEHIND
                    params.blurBehindRadius = 38
                } else {
                    params.flags = params.flags and WindowManager.LayoutParams.FLAG_BLUR_BEHIND.inv()
                    params.blurBehindRadius = 0
                }
            } catch (_: Exception) {}
        }
    }

    private fun snapBubbleToNearestEdge() {
        snappedToRightEdge = (params.x + prefBubbleSizePx / 2) >= (fullScreenWidth / 2)
        val targetX = if (snappedToRightEdge) (fullScreenWidth - prefBubbleSizePx) else 0
        ValueAnimator.ofInt(params.x, targetX).apply {
            duration = 230
            interpolator = DecelerateInterpolator()
            addUpdateListener { anim ->
                params.x = anim.animatedValue as Int
                try { windowManager.updateViewLayout(floatingView, params) } catch (_: Exception) {}
            }
            start()
        }
        if (prefOverlayStyle == "xiaomi_edge") {
            mainHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
            mainHandler.postDelayed(transformToXiaomiEdgeRunnable, 2500L)
        }
        scheduleSmartFreeze()
    }

    private fun enterXiaomiEdgeMode() {
        snappedToRightEdge = (params.x + prefBubbleSizePx / 2) >= (fullScreenWidth / 2)
        xiaomiEdgeView.setBackgroundResource(
            if (snappedToRightEdge) R.drawable.bg_xiaomi_edge_right else R.drawable.bg_xiaomi_edge_left
        )
        bubbleView.visibility = View.GONE
        xiaomiEdgeView.visibility = View.VISIBLE
        xiaomiEdgeView.alpha = 0.85f
        val pillW = (18 * resources.displayMetrics.density).toInt()
        params.x = if (snappedToRightEdge) (fullScreenWidth - pillW) else 0
        windowManager.updateViewLayout(floatingView, params)
        xiaomiEdgeView.animate().alpha(0.45f).setDuration(380).start()
        scheduleSmartFreeze()
    }

    private fun exitXiaomiEdgeMode() {
        mainHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
        xiaomiEdgeView.visibility = View.GONE
        bubbleView.visibility = View.VISIBLE
        bubbleView.alpha = 1.0f
        params.x = if (snappedToRightEdge) (fullScreenWidth - prefBubbleSizePx) else 0
        windowManager.updateViewLayout(floatingView, params)
        mainHandler.postDelayed(transformToXiaomiEdgeRunnable, 2500L)
        scheduleSmartFreeze()
    }

    private fun performQuickForceStop() {
        Toast.makeText(this, "Menghentikan paksa Floamini...", Toast.LENGTH_SHORT).show()
        dismissSiriAura()
        stopMediaProjection()
        startActivity(Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
            data = Uri.parse("package:$packageName")
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        })
        stopSelf()
        exitProcess(0)
    }

    // ==========================================================================
    // LIVE SCREEN VISION (MEDIAPROJECTION)
    // ==========================================================================
    private fun startMediaProjection(resultCode: Int, data: Intent) {
        startForegroundNotification(withMediaProjection = true)
        val projectionManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        mediaProjection = projectionManager.getMediaProjection(resultCode, data)

        mediaProjection?.registerCallback(object : MediaProjection.Callback() {
            override fun onStop() {
                mainHandler.post { stopMediaProjection() }
            }
        }, mainHandler)

        imageReader = ImageReader.newInstance(captureWidth, captureHeight, PixelFormat.RGBA_8888, 2)
        virtualDisplay = mediaProjection?.createVirtualDisplay(
            "FloaminiScreenShare",
            captureWidth,
            captureHeight,
            screenDensity,
            DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
            imageReader?.surface,
            null,
            null
        )

        isScreenShareActive = true
        btnScreenShare.setColorFilter(Color.parseColor("#38BDF8"))
        tvScreenShareStatus.visibility = View.VISIBLE
        tvIslandLabel.text = "Live Vision"
        popupChatView.setBackgroundResource(R.drawable.bg_liquid_glass_window_share)
        Toast.makeText(this, "Live Screen Vision aktif", Toast.LENGTH_SHORT).show()
    }

    private fun stopMediaProjection() {
        isScreenShareActive = false
        try { virtualDisplay?.release() } catch (_: Exception) {}
        try { imageReader?.close() } catch (_: Exception) {}
        try { mediaProjection?.stop() } catch (_: Exception) {}
        virtualDisplay = null
        imageReader = null
        mediaProjection = null
        if (::btnScreenShare.isInitialized) btnScreenShare.setColorFilter(Color.parseColor("#94A3B8"))
        if (::tvScreenShareStatus.isInitialized) tvScreenShareStatus.visibility = View.GONE
        if (::tvIslandLabel.isInitialized) tvIslandLabel.text = "Floamini"
        if (::popupChatView.isInitialized) popupChatView.setBackgroundResource(R.drawable.bg_liquid_glass_window)
        startForegroundNotification(withMediaProjection = false)
    }

    private fun captureCurrentScreenBase64(): String? {
        return try {
            val image = imageReader?.acquireLatestImage() ?: return null
            val planes = image.planes
            val buffer = planes[0].buffer
            val pixelStride = planes[0].pixelStride
            val rowStride = planes[0].rowStride
            val rowPadding = rowStride - pixelStride * captureWidth

            val bitmap = Bitmap.createBitmap(
                captureWidth + rowPadding / pixelStride,
                captureHeight,
                Bitmap.Config.ARGB_8888
            )
            bitmap.copyPixelsFromBuffer(buffer)
            image.close()

            val cropped = Bitmap.createBitmap(bitmap, 0, 0, captureWidth, captureHeight)
            val out = ByteArrayOutputStream()
            cropped.compress(Bitmap.CompressFormat.JPEG, 68, out)
            bitmap.recycle()
            cropped.recycle()
            Base64.encodeToString(out.toByteArray(), Base64.NO_WRAP)
        } catch (_: Exception) {
            null
        }
    }

    private fun buildSystemInstructionText(): String {
        val basePersona = when (prefPersona) {
            "ringkas" -> "Kamu adalah Floamini, asisten AI yang sigap dan padat. Jawab langsung ke inti dalam 1-2 kalimat."
            "detail" -> "Kamu adalah Floamini, asisten AI yang ramah dan informatif. Jelaskan jawaban secara runtut dan jelas."
            "teknis" -> "Kamu adalah Floamini, asisten teknis dan software architect cerdas. Berikan solusi terstruktur."
            else -> "Kamu adalah Floamini, asisten AI yang asik, santai, cerdas, dan terasa menyatu dengan sistem operasi Android."
        }
        val custom = if (prefCustomSystemInstruction.isNotBlank()) "\nInstruksi Tambahan Pengguna: $prefCustomSystemInstruction" else ""
        return "$basePersona Selalu ingat konteks percakapan sebelumnya dalam sesi ini.$custom"
    }

    override fun onDestroy() {
        super.onDestroy()
        try { unregisterReceiver(screenStateReceiver) } catch (_: Exception) {}
        mainHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
        mainHandler.removeCallbacks(autoHidePillRunnable)
        mainHandler.removeCallbacks(smartFreezeRunnable)
        voiceManager?.release()
        dismissSiriAura()
        stopMediaProjection()
        activeGenerationJob?.cancel()
        serviceJob.cancel()
        if (isFloatingViewAttached && ::floatingView.isInitialized) {
            try { windowManager.removeView(floatingView) } catch (_: Exception) {}
        }
    }
}
"""
}

def generate_project():
    for filepath, content in PROJECT_FILES.items():
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        print(f"Berhasil membuat/memperbarui: {filepath}")
    print("\nProyek Floamini OS Edition (v6.0) siap di-generate dan di-build di GitHub Actions!")

if __name__ == "__main__":
    generate_project()
