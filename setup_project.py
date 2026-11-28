   
import os

PROJECT_FILES = {
    # --------------------------------------------------------------------------
    # 0. GITIGNORE (MENCEGAH FILE LOKAL TERMUX TERUNGGAH KE GITHUB)
    # --------------------------------------------------------------------------
    ".gitignore": r"""*.iml
.gradle/
/local.properties
/.idea/
/captures/
.externalNativeBuild/
.cxx/
build/
app/build/
build_termux.sh
*.apk
""",

    # --------------------------------------------------------------------------
    # 1. GITHUB ACTIONS WORKFLOW (AUTO BUILD APK DI SERVER GITHUB)
    # --------------------------------------------------------------------------
    ".github/workflows/build_apk.yml": r"""name: Build Floamini OS APK

on:
  push:
    branches: [ "main", "master" ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Clean Termux Local Overrides
        run: |
          rm -f local.properties
          sed -i '/aapt2FromMavenOverride/d' gradle.properties

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Setup Gradle 8.5
        uses: gradle/actions/setup-gradle@v4
        with:
          gradle-version: '8.5'

      - name: Generate Persistent Signing Keystore
        run: |
          if [ ! -f app/floamini.jks ]; then
            keytool -genkeypair -v -keystore app/floamini.jks -alias floamini_key \
              -keyalg RSA -keysize 2048 -validity 10000 \
              -storepass floamini_keystore_pass_2026 -keypass floamini_keystore_pass_2026 \
              -dname "CN=Floamini, OU=Mobile, O=AvoluProject, L=Yogyakarta, ST=DIY, C=ID"
          fi

      - name: Build Update-Ready APK
        run: gradle assembleDebug

      - name: Upload APK Artifact
        uses: actions/upload-artifact@v4
        with:
          name: Floamini-OS-v7.1-LiquidGlass
          path: app/build/outputs/apk/debug/app-debug.apk
""",

    # --------------------------------------------------------------------------
    # 2. GRADLE ROOT & PROPERTIES
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
rootProject.name = "FloaminiOS"
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
val appVersionCode = 30 + ciRunNumber
val appVersionName = "7.1.$ciRunNumber"

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
            isMinifyEnabled = false
        }
        release {
            isMinifyEnabled = false
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

    "app/proguard-rules.pro": r"""-keep class com.example.floatinggeminiai.** { *; }
""",

    # --------------------------------------------------------------------------
    # 4. ANDROID MANIFEST
    # --------------------------------------------------------------------------
    "app/src/main/AndroidManifest.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.VIBRATE" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:roundIcon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:theme="@style/Theme.FloaminiOS">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <activity
            android:name=".WelcomeActivity"
            android:exported="false" />

        <activity
            android:name=".ScreenCapturePermissionActivity"
            android:exported="false"
            android:theme="@style/Theme.FloaminiTransparent" />

        <activity
            android:name=".FilePickerProxyActivity"
            android:exported="false"
            android:theme="@style/Theme.FloaminiTransparent" />

        <activity
            android:name=".ExternalTriggerActivity"
            android:exported="true"
            android:label="Tanya Floamini AI"
            android:theme="@style/Theme.FloaminiTransparent">
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
        </activity>

        <service
            android:name=".FloatingAssistantService"
            android:enabled="true"
            android:exported="false"
            android:foregroundServiceType="specialUse|mediaProjection">
            <property
                android:name="android.app.PROPERTY_SPECIAL_USE_FGS_SUBTYPE"
                android:value="Floating AI overlay assistant window" />
        </service>

        <service
            android:name=".FloaminiTileService"
            android:icon="@drawable/ic_sparkle"
            android:label="Floamini AI"
            android:permission="android.permission.BIND_QUICK_SETTINGS_TILE"
            android:exported="true">
            <intent-filter>
                <action android:name="android.service.quicksettings.action.QS_TILE" />
            </intent-filter>
        </service>

    </application>
</manifest>
""",

    # --------------------------------------------------------------------------
    # 5. RESOURCES: STRINGS & THEMES
    # --------------------------------------------------------------------------
    "app/src/main/res/values/strings.xml": r"""<resources>
    <string name="app_name">Floamini</string>
</resources>
""",

    "app/src/main/res/values/themes.xml": r"""<resources>
    <style name="Theme.FloaminiOS" parent="Theme.MaterialComponents.DayNight.NoActionBar">
        <item name="colorPrimary">#38BDF8</item>
        <item name="colorPrimaryVariant">#0284C7</item>
        <item name="colorOnPrimary">#020617</item>
        <item name="colorSecondary">#A855F7</item>
        <item name="android:statusBarColor">@android:color/transparent</item>
        <item name="android:navigationBarColor">@android:color/transparent</item>
    </style>

    <style name="Theme.FloaminiTransparent" parent="Theme.MaterialComponents.DayNight.NoActionBar">
        <item name="android:windowIsTranslucent">true</item>
        <item name="android:windowBackground">@android:color/transparent</item>
        <item name="android:windowContentOverlay">@null</item>
        <item name="android:windowNoTitle">true</item>
        <item name="android:backgroundDimEnabled">false</item>
    </style>
</resources>
""",

    # --------------------------------------------------------------------------
    # 6. SECURITY MODULE: ENCRYPTED VAULT (AES256-GCM)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/security/SecureVault.kt": r"""package com.example.floatinggeminiai.security

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class SecureVault(context: Context) {

    private val prefs: SharedPreferences = createEncryptedPrefs(context.applicationContext)

    private fun createEncryptedPrefs(ctx: Context): SharedPreferences {
        return try {
            val masterKey = MasterKey.Builder(ctx)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build()
            EncryptedSharedPreferences.create(
                ctx,
                "floamini_secure_vault",
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        } catch (_: Throwable) {
            ctx.getSharedPreferences("floamini_secure_vault_fallback", Context.MODE_PRIVATE)
        }
    }

    fun saveApiKey(providerId: String, apiKey: String) {
        prefs.edit().putString("key_$providerId", apiKey.trim()).apply()
    }

    fun getApiKey(providerId: String): String {
        return prefs.getString("key_$providerId", "")?.trim().orEmpty()
    }

    fun hasApiKey(providerId: String): Boolean {
        return getApiKey(providerId).isNotEmpty()
    }

    fun saveCustomEndpoint(baseUrl: String, modelId: String) {
        prefs.edit()
            .putString("custom_base_url", baseUrl.trim())
            .putString("custom_model_id", modelId.trim())
            .apply()
    }

    fun getCustomBaseUrl(): String {
        return prefs.getString("custom_base_url", "https://api.openai.com/v1")?.trim().orEmpty()
    }

    fun getCustomModelId(): String {
        return prefs.getString("custom_model_id", "gpt-4o-mini")?.trim().orEmpty()
    }

    fun getMaskedKey(providerId: String): String {
        val raw = getApiKey(providerId)
        if (raw.length <= 8) return if (raw.isEmpty()) "Belum diisi" else "••••••••"
        return "${raw.take(4)}••••••${raw.takeLast(4)}"
    }
}
""",

    # --------------------------------------------------------------------------
    # 7. AI MODELS & PROVIDER CONFIGURATION (11 PROVIDERS)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/ai/AiModels.kt": r"""package com.example.floatinggeminiai.ai

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
    val role: String,
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
""",

    # --------------------------------------------------------------------------
    # 8. MULTI-AI PROVIDER ENGINE (SSE STREAMING, RETRY, AUTO-ROUTER)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/ai/AiProviderAdapters.kt": r"""package com.example.floatinggeminiai.ai

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
""",

    # --------------------------------------------------------------------------
    # 9. DATA REPOSITORY: MULTI-THREAD CONVERSATION, SEARCH & USAGE TRACKING
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/data/ChatRepository.kt": r"""package com.example.floatinggeminiai.data

import android.content.Context
import com.example.floatinggeminiai.ai.ChatMessage
import com.example.floatinggeminiai.ai.ChatThread
import org.json.JSONArray
import org.json.JSONObject

class ChatRepository(context: Context) {

    private val prefs = context.applicationContext.getSharedPreferences("floamini_chat_data", Context.MODE_PRIVATE)

    fun loadAllThreads(): MutableList<ChatThread> {
        val raw = prefs.getString("threads_json", null) ?: return mutableListOf()
        return try {
            val arr = JSONArray(raw)
            val result = mutableListOf<ChatThread>()
            for (i in 0 until arr.length()) {
                val obj = arr.getJSONObject(i)
                val msgsArr = obj.optJSONArray("messages") ?: JSONArray()
                val msgs = mutableListOf<ChatMessage>()
                for (j in 0 until msgsArr.length()) {
                    val m = msgsArr.getJSONObject(j)
                    msgs.add(
                        ChatMessage(
                            id = m.optString("id", System.nanoTime().toString()),
                            role = m.optString("role", "user"),
                            content = m.optString("content", ""),
                            providerTag = m.optString("providerTag", ""),
                            timestamp = m.optLong("timestamp", System.currentTimeMillis())
                        )
                    )
                }
                result.add(
                    ChatThread(
                        id = obj.getString("id"),
                        title = obj.optString("title", "Sesi Floamini"),
                        messages = msgs,
                        updatedAt = obj.optLong("updatedAt", System.currentTimeMillis())
                    )
                )
            }
            result
        } catch (_: Exception) {
            mutableListOf()
        }
    }

    fun saveAllThreads(threads: List<ChatThread>) {
        val arr = JSONArray()
        for (t in threads.take(30)) {
            val msgsArr = JSONArray()
            for (m in t.messages.takeLast(80)) {
                msgsArr.put(
                    JSONObject()
                        .put("id", m.id)
                        .put("role", m.role)
                        .put("content", m.content)
                        .put("providerTag", m.providerTag)
                        .put("timestamp", m.timestamp)
                )
            }
            arr.put(
                JSONObject()
                    .put("id", t.id)
                    .put("title", t.title)
                    .put("messages", msgsArr)
                    .put("updatedAt", t.updatedAt)
            )
        }
        prefs.edit().putString("threads_json", arr.toString()).apply()
    }

    fun getOrCreateActiveThread(): ChatThread {
        val all = loadAllThreads()
        val activeId = prefs.getString("active_thread_id", null)
        val found = all.find { it.id == activeId } ?: all.firstOrNull()
        if (found != null) return found

        val created = ChatThread(id = "session_${System.currentTimeMillis()}", title = "Sesi Utama")
        all.add(0, created)
        saveAllThreads(all)
        setActiveThreadId(created.id)
        return created
    }

    fun createNewThread(title: String = "Sesi Baru"): ChatThread {
        val all = loadAllThreads()
        val created = ChatThread(id = "session_${System.currentTimeMillis()}", title = title)
        all.add(0, created)
        saveAllThreads(all)
        setActiveThreadId(created.id)
        return created
    }

    fun saveThread(thread: ChatThread) {
        val all = loadAllThreads()
        val idx = all.indexOfFirst { it.id == thread.id }
        thread.updatedAt = System.currentTimeMillis()
        if (idx >= 0) {
            all[idx] = thread
        } else {
            all.add(0, thread)
        }
        saveAllThreads(all)
    }

    fun setActiveThreadId(id: String) {
        prefs.edit().putString("active_thread_id", id).apply()
    }

    fun searchThreads(query: String): List<ChatThread> {
        val q = query.trim().lowercase()
        val all = loadAllThreads()
        if (q.isEmpty()) return all
        return all.filter { t ->
            t.title.lowercase().contains(q) || t.messages.any { it.content.lowercase().contains(q) }
        }
    }

    fun clearAllHistory() {
        prefs.edit().remove("threads_json").remove("active_thread_id").apply()
    }

    fun recordUsage(providerName: String, charsOut: Int) {
        val totalReq = prefs.getInt("usage_total_req", 0) + 1
        val totalChars = prefs.getLong("usage_total_chars", 0L) + charsOut
        val provCount = prefs.getInt("usage_prov_$providerName", 0) + 1
        prefs.edit()
            .putInt("usage_total_req", totalReq)
            .putLong("usage_total_chars", totalChars)
            .putInt("usage_prov_$providerName", provCount)
            .apply()
    }

    fun getUsageSummary(): String {
        val req = prefs.getInt("usage_total_req", 0)
        val chars = prefs.getLong("usage_total_chars", 0L)
        val estTokens = chars / 4
        return "Total Permintaan: $req kali | Estimasi Token Output: ~$estTokens token"
    }

    fun resetUsage() {
        prefs.edit().putInt("usage_total_req", 0).putLong("usage_total_chars", 0L).apply()
    }

    fun getQuickNotes(): String = prefs.getString("quick_notes", "").orEmpty()
    fun saveQuickNotes(notes: String) = prefs.edit().putString("quick_notes", notes).apply()
}
""",

    # --------------------------------------------------------------------------
    # 10. VOICE SYSTEM MANAGER (STT + TTS + INTERRUPT + AMPLITUDE)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/voice/VoiceSystemManager.kt": r"""package com.example.floatinggeminiai.voice

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import java.util.Locale

class VoiceSystemManager(
    private val context: Context,
    private val onAmplitudeChanged: (Float) -> Unit,
    private val onSpeechResult: (String) -> Unit,
    private val onSpeechStateChanged: (Boolean, String) -> Unit
) {

    private var speechRecognizer: SpeechRecognizer? = null
    private var tts: TextToSpeech? = null
    private var isTtsReady = false
    var isListening = false
        private set

    init {
        tts = TextToSpeech(context.applicationContext) { status ->
            if (status == TextToSpeech.SUCCESS) {
                val res = tts?.setLanguage(Locale("id", "ID"))
                if (res == TextToSpeech.LANG_MISSING_DATA || res == TextToSpeech.LANG_NOT_SUPPORTED) {
                    tts?.language = Locale.US
                }
                isTtsReady = true
            }
        }
    }

    fun startListening() {
        stopSpeaking()
        if (!SpeechRecognizer.isRecognitionAvailable(context)) {
            onSpeechStateChanged(false, "Pengenal suara tidak tersedia di perangkat ini.")
            return
        }
        stopListening()

        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(context.applicationContext).apply {
            setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: Bundle?) {
                    isListening = true
                    onSpeechStateChanged(true, "Mendengarkan...")
                }

                override fun onBeginningOfSpeech() {}

                override fun onRmsChanged(rmsdB: Float) {
                    val norm = ((rmsdB + 2f) / 12f).coerceIn(0.08f, 1.0f)
                    onAmplitudeChanged(norm)
                }

                override fun onBufferReceived(buffer: ByteArray?) {}

                override fun onEndOfSpeech() {
                    isListening = false
                    onSpeechStateChanged(false, "Memproses suara...")
                }

                override fun onError(error: Int) {
                    isListening = false
                    onAmplitudeChanged(0f)
                    onSpeechStateChanged(false, "Suara selesai / tidak terdeteksi.")
                }

                override fun onResults(results: Bundle?) {
                    isListening = false
                    onAmplitudeChanged(0f)
                    val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                    val spoken = matches?.firstOrNull().orEmpty()
                    onSpeechStateChanged(false, "")
                    if (spoken.isNotBlank()) {
                        onSpeechResult(spoken)
                    }
                }

                override fun onPartialResults(partialResults: Bundle?) {
                    val partial = partialResults?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull()
                    if (!partial.isNullOrBlank()) {
                        onSpeechStateChanged(true, partial)
                    }
                }

                override fun onEvent(eventType: Int, params: Bundle?) {}
            })
        }

        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "id-ID")
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
        }
        speechRecognizer?.startListening(intent)
    }

    fun stopListening() {
        isListening = false
        onAmplitudeChanged(0f)
        try {
            speechRecognizer?.stopListening()
            speechRecognizer?.destroy()
        } catch (_: Exception) {
        }
        speechRecognizer = null
    }

    fun speak(text: String) {
        if (!isTtsReady || text.isBlank()) return
        stopSpeaking()
        tts?.speak(text.take(1500), TextToSpeech.QUEUE_FLUSH, null, "floamini_tts")
    }

    fun stopSpeaking() {
        try {
            if (tts?.isSpeaking == true) {
                tts?.stop()
            }
        } catch (_: Exception) {
        }
    }

    fun release() {
        stopListening()
        stopSpeaking()
        try {
            tts?.shutdown()
        } catch (_: Exception) {
        }
    }
}
""",

    # --------------------------------------------------------------------------
    # 11. SMART FLOATING TOOLS (PDF RENDERER, FILE READER, SAFE CALCULATOR)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/tools/SmartToolsHelper.kt": r"""package com.example.floatinggeminiai.tools

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.pdf.PdfRenderer
import android.net.Uri
import android.provider.OpenableColumns
import android.util.Base64
import java.io.ByteArrayOutputStream
import java.io.InputStreamReader

data class ProcessedAttachment(
    val displayName: String,
    val extractedText: String = "",
    val base64Images: List<String> = emptyList()
)

object SmartToolsHelper {

    fun processUri(context: Context, uri: Uri): ProcessedAttachment {
        val name = queryFileName(context, uri)
        val mime = context.contentResolver.getType(uri).orEmpty().lowercase()

        return when {
            mime.contains("pdf") || name.lowercase().endsWith(".pdf") -> {
                extractPdfPagesAsBase64(context, uri, name)
            }
            mime.startsWith("image/") -> {
                val b64 = encodeImageUriToBase64(context, uri)
                ProcessedAttachment(
                    displayName = name,
                    base64Images = if (b64 != null) listOf(b64) else emptyList()
                )
            }
            else -> {
                val text = readTextUri(context, uri)
                ProcessedAttachment(displayName = name, extractedText = text)
            }
        }
    }

    private fun queryFileName(context: Context, uri: Uri): String {
        var result = "Lampiran"
        try {
            context.contentResolver.query(uri, null, null, null, null)?.use { cursor ->
                val idx = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                if (idx >= 0 && cursor.moveToFirst()) {
                    result = cursor.getString(idx) ?: result
                }
            }
        } catch (_: Exception) {
        }
        return result
    }

    private fun readTextUri(context: Context, uri: Uri): String {
        return try {
            context.contentResolver.openInputStream(uri)?.use { stream ->
                InputStreamReader(stream).readText().take(12000)
            }.orEmpty()
        } catch (_: Exception) {
            ""
        }
    }

    private fun encodeImageUriToBase64(context: Context, uri: Uri): String? {
        return try {
            val raw = context.contentResolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it) } ?: return null
            bitmapToBase64(raw, 1024)
        } catch (_: Exception) {
            null
        }
    }

    private fun extractPdfPagesAsBase64(context: Context, uri: Uri, name: String): ProcessedAttachment {
        val images = mutableListOf<String>()
        try {
            context.contentResolver.openFileDescriptor(uri, "r")?.use { pfd ->
                PdfRenderer(pfd).use { renderer ->
                    val maxPages = renderer.pageCount.coerceAtMost(3)
                    for (i in 0 until maxPages) {
                        renderer.openPage(i).use { page ->
                            val bmp = Bitmap.createBitmap(page.width.coerceAtMost(1024), page.height.coerceAtMost(1400), Bitmap.Config.ARGB_8888)
                            val canvas = Canvas(bmp)
                            canvas.drawColor(Color.WHITE)
                            page.render(bmp, null, null, PdfRenderer.Page.RENDER_MODE_FOR_DISPLAY)
                            images.add(bitmapToBase64(bmp, 1024))
                            bmp.recycle()
                        }
                    }
                }
            }
        } catch (_: Exception) {
        }
        return ProcessedAttachment(displayName = "$name (${images.size} hal.)", base64Images = images)
    }

    fun bitmapToBase64(src: Bitmap, maxDim: Int): String {
        val ratio = minOf(maxDim.toFloat() / src.width, maxDim.toFloat() / src.height, 1.0f)
        val scaled = if (ratio < 1.0f) {
            Bitmap.createScaledBitmap(src, (src.width * ratio).toInt().coerceAtLeast(1), (src.height * ratio).toInt().coerceAtLeast(1), true)
        } else {
            src
        }
        val out = ByteArrayOutputStream()
        scaled.compress(Bitmap.CompressFormat.JPEG, 76, out)
        if (scaled !== src) scaled.recycle()
        return Base64.encodeToString(out.toByteArray(), Base64.NO_WRAP)
    }

    fun evaluateMath(expression: String): String {
        val cleaned = expression.replace(" ", "").replace("×", "*").replace("÷", "/")
        if (cleaned.isEmpty()) return "0"
        return try {
            var pos = -1
            var ch = 0
            fun nextChar() {
                pos++
                ch = if (pos < cleaned.length) cleaned[pos].code else -1
            }
            fun eat(charToEat: Int): Boolean {
                while (ch == ' '.code) nextChar()
                if (ch == charToEat) {
                    nextChar()
                    return true
                }
                return false
            }
            fun parseExpression(): Double {
                fun parseTerm(): Double {
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
                            x = cleaned.substring(startPos, pos).toDouble()
                        } else {
                            throw RuntimeException("Unexpected")
                        }
                        return x
                    }
                    var x = parseFactor()
                    while (true) {
                        x = when {
                            eat('*'.code) -> x * parseFactor()
                            eat('/'.code) -> x / parseFactor()
                            else -> return x
                        }
                    }
                }
                var x = parseTerm()
                while (true) {
                    x = when {
                        eat('+'.code) -> x + parseTerm()
                        eat('-'.code) -> x - parseTerm()
                        else -> return x
                    }
                }
            }
            nextChar()
            val v = parseExpression()
            if (v % 1.0 == 0.0) v.toLong().toString() else String.format("%.4f", v).trimEnd('0').trimEnd('.')
        } catch (_: Exception) {
            "Format salah"
        }
    }
}
""",

    # --------------------------------------------------------------------------
    # 12. KYANT0 LIQUID GLASS ENGINE + LIQUID GLASS BOTTOM NAVBAR
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/ui/LiquidGlassView.kt": r"""package com.example.floatinggeminiai.ui

import android.animation.ValueAnimator
import android.content.Context
import android.content.res.Configuration
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.LinearGradient
import android.graphics.Paint
import android.graphics.Path
import android.graphics.RectF
import android.graphics.RuntimeShader
import android.graphics.Shader
import android.graphics.Typeface
import android.os.Build
import android.util.AttributeSet
import android.view.Gravity
import android.view.HapticFeedbackConstants
import android.view.MotionEvent
import android.view.animation.LinearInterpolator
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import androidx.dynamicanimation.animation.FloatValueHolder
import androidx.dynamicanimation.animation.SpringAnimation
import androidx.dynamicanimation.animation.SpringForce

class LiquidGlassFrameLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : FrameLayout(context, attrs, defStyleAttr) {

    enum class GlassMaterialVariant {
        REGULAR,
        CLEAR
    }

    var cornerRadiusDp: Float = 24f
        set(value) {
            field = value
            requestRebuildBounds()
            invalidate()
        }

    var bevelWidthDp: Float = 14f
        set(value) {
            field = value
            invalidate()
        }

    var dispersionStrength: Float = 0.28f
        set(value) {
            field = value
            invalidate()
        }

    var specularIntensity: Float = 0.62f
        set(value) {
            field = value
            invalidate()
        }

    var materialVariant: GlassMaterialVariant = GlassMaterialVariant.REGULAR
        set(value) {
            field = value
            if (width > 0 && height > 0) {
                updateFallbackGradients(width.toFloat(), height.toFloat())
            }
            invalidate()
        }

    var enableGelPress: Boolean = true

    private var touchX: Float = -1f
    private var touchY: Float = -1f
    private var pressProgress: Float = 0f
    private var shimmerPhase: Float = 0f

    private val boundsRect = RectF()
    private val clipPath = Path()
    private val shaderPaint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val fallbackFillPaint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val fallbackRimPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
    }

    private var agslShader: RuntimeShader? = null
    private var ambientAnimator: ValueAnimator? = null
    private var pressSpring: SpringAnimation? = null

    init {
        setWillNotDraw(false)
        initAgslShaderIfSupported()
    }

    private fun initAgslShaderIfSupported() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            val agslCode = listOf(
                "uniform float2 uResolution;",
                "uniform float uCornerRadius;",
                "uniform float uBevelWidth;",
                "uniform float uDispersionStrength;",
                "uniform float uSpecularIntensity;",
                "uniform float2 uTouchPos;",
                "uniform float uPressProgress;",
                "uniform float uTime;",
                "uniform float uIsDark;",
                "uniform float uClearVariant;",
                "float sdRoundedBox(float2 p, float2 b, float r) {",
                "    float2 q = abs(p) - b + float2(r);",
                "    return min(max(q.x, q.y), 0.0) + length(max(q, float2(0.0))) - r;",
                "}",
                "half4 main(float2 fragCoord) {",
                "    float2 center = uResolution * 0.5;",
                "    float maxR = min(center.x, center.y);",
                "    float radius = clamp(uCornerRadius, 1.0, maxR);",
                "    float2 halfSize = center - float2(0.75);",
                "    float2 p = fragCoord - center;",
                "    float d = sdRoundedBox(p, halfSize, radius);",
                "    if (d > 0.0) { return half4(0.0); }",
                "    float2 eps = float2(1.5, 0.0);",
                "    float2 grad = float2(",
                "        sdRoundedBox(p + eps.xy, halfSize, radius) - sdRoundedBox(p - eps.xy, halfSize, radius),",
                "        sdRoundedBox(p + eps.yx, halfSize, radius) - sdRoundedBox(p - eps.yx, halfSize, radius)",
                "    );",
                "    float2 normal = normalize(grad + float2(0.0001));",
                "    float edgeDist = -d;",
                "    float rimFactor = clamp(1.0 - (edgeDist / max(uBevelWidth, 1.0)), 0.0, 1.0);",
                "    float lensCurve = pow(rimFactor, 2.2);",
                "    float touchDist = length(fragCoord - uTouchPos);",
                "    float gelBulge = uPressProgress * exp(-touchDist * 0.011);",
                "    float2 touchOffset = (uTouchPos - center) * 0.0016 * uPressProgress;",
                "    float2 lightDir = normalize(float2(-0.62, -0.78) + touchOffset);",
                "    float topSpec = pow(max(dot(normal, lightDir), 0.0), 2.6) * (0.35 + 0.65 * lensCurve);",
                "    float bottomRim = pow(max(dot(normal, -lightDir), 0.0), 3.4) * lensCurve * 0.52;",
                "    float angle = atan(normal.y, normal.x) + uTime * 0.45;",
                "    float3 dispersion = float3(",
                "        0.5 + 0.5 * sin(angle),",
                "        0.5 + 0.5 * sin(angle + 2.09439),",
                "        0.5 + 0.5 * sin(angle + 4.18879)",
                "    ) * lensCurve * uDispersionStrength;",
                "    float3 baseDark = mix(float3(0.068, 0.102, 0.185), float3(0.015, 0.022, 0.038), uClearVariant);",
                "    float3 baseLight = mix(float3(0.92, 0.95, 0.99), float3(0.96, 0.98, 1.0), uClearVariant);",
                "    float3 baseCol = mix(baseLight, baseDark, uIsDark);",
                "    float grain = (fract(sin(dot(fragCoord, float2(12.9898, 78.233))) * 43758.5453) - 0.5) * 0.015;",
                "    float3 rgb = baseCol + dispersion",
                "        + float3(0.76, 0.90, 1.0) * (topSpec * uSpecularIntensity + gelBulge * 0.25)",
                "        + float3(0.68, 0.54, 1.0) * bottomRim",
                "        + float3(grain);",
                "    float targetAlpha = mix(0.84, 0.76, uClearVariant);",
                "    float alpha = clamp(targetAlpha + lensCurve * 0.15 + topSpec * 0.20, 0.0, 0.97);",
                "    return half4(half3(rgb * alpha), half(alpha));",
                "}"
            ).joinToString("\n")

            try {
                agslShader = RuntimeShader(agslCode)
                shaderPaint.shader = agslShader
            } catch (_: Throwable) {
                agslShader = null
            }
        }
    }

    private fun isSystemDarkTheme(): Boolean {
        val mode = resources.configuration.uiMode and Configuration.UI_MODE_NIGHT_MASK
        return mode == Configuration.UI_MODE_NIGHT_YES
    }

    private fun requestRebuildBounds() {
        val w = width.toFloat()
        val h = height.toFloat()
        if (w > 0f && h > 0f) {
            boundsRect.set(0f, 0f, w, h)
            val rPx = cornerRadiusDp * resources.displayMetrics.density
            clipPath.reset()
            clipPath.addRoundRect(boundsRect, rPx, rPx, Path.Direction.CW)
        }
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        if (w > 0 && h > 0) {
            requestRebuildBounds()
            if (touchX < 0f) {
                touchX = w / 2f
                touchY = h / 2f
            }
            updateFallbackGradients(w.toFloat(), h.toFloat())
        }
    }

    private fun updateFallbackGradients(w: Float, h: Float) {
        val dark = isSystemDarkTheme()
        fallbackFillPaint.shader = LinearGradient(
            0f, 0f, 0f, h,
            if (materialVariant == GlassMaterialVariant.CLEAR) {
                intArrayOf(Color.parseColor("#E6060912"), Color.parseColor("#F2020306"))
            } else if (dark) {
                intArrayOf(Color.parseColor("#D818243E"), Color.parseColor("#E20B111E"))
            } else {
                intArrayOf(Color.parseColor("#EAFFFFFF"), Color.parseColor("#F0E2E8F0"))
            },
            null,
            Shader.TileMode.CLAMP
        )
        fallbackRimPaint.strokeWidth = 1.4f * resources.displayMetrics.density
        fallbackRimPaint.shader = LinearGradient(
            0f, 0f, w, h,
            intArrayOf(
                Color.parseColor("#B8FFFFFF"),
                Color.parseColor("#6638BDF8"),
                Color.parseColor("#66E879F9")
            ),
            null,
            Shader.TileMode.CLAMP
        )
    }

    override fun dispatchDraw(canvas: Canvas) {
        val w = width.toFloat()
        val h = height.toFloat()
        if (w <= 0f || h <= 0f) {
            super.dispatchDraw(canvas)
            return
        }

        val density = resources.displayMetrics.density
        val rPx = cornerRadiusDp * density
        val shader = agslShader

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU && shader != null) {
            try {
                shader.setFloatUniform("uResolution", w, h)
                shader.setFloatUniform("uCornerRadius", rPx)
                shader.setFloatUniform("uBevelWidth", bevelWidthDp * density)
                shader.setFloatUniform("uDispersionStrength", dispersionStrength)
                shader.setFloatUniform("uSpecularIntensity", specularIntensity)
                shader.setFloatUniform("uTouchPos", if (touchX >= 0f) touchX else w / 2f, if (touchY >= 0f) touchY else h / 2f)
                shader.setFloatUniform("uPressProgress", pressProgress)
                shader.setFloatUniform("uTime", shimmerPhase)
                shader.setFloatUniform("uIsDark", if (isSystemDarkTheme()) 1.0f else 0.0f)
                shader.setFloatUniform("uClearVariant", if (materialVariant == GlassMaterialVariant.CLEAR) 1.0f else 0.0f)
                canvas.drawRect(0f, 0f, w, h, shaderPaint)
            } catch (_: Throwable) {
                drawFallbackGlass(canvas, rPx)
            }
        } else {
            drawFallbackGlass(canvas, rPx)
        }

        val saveCount = canvas.save()
        canvas.clipPath(clipPath)
        super.dispatchDraw(canvas)
        canvas.restoreToCount(saveCount)
    }

    private fun drawFallbackGlass(canvas: Canvas, rPx: Float) {
        canvas.drawRoundRect(boundsRect, rPx, rPx, fallbackFillPaint)
        val inset = fallbackRimPaint.strokeWidth * 0.5f
        val rimRect = RectF(inset, inset, width - inset, height - inset)
        canvas.drawRoundRect(rimRect, rPx, rPx, fallbackRimPaint)
    }

    override fun onInterceptTouchEvent(ev: MotionEvent): Boolean {
        if (enableGelPress) {
            handleGelTouch(ev)
        }
        return super.onInterceptTouchEvent(ev)
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        if (enableGelPress) {
            handleGelTouch(event)
        }
        return super.onTouchEvent(event)
    }

    private fun handleGelTouch(event: MotionEvent) {
        touchX = event.x
        touchY = event.y
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> animateGelPress(1.0f)
            MotionEvent.ACTION_MOVE -> invalidate()
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> animateGelPress(0.0f)
        }
    }

    private fun animateGelPress(target: Float) {
        pressSpring?.cancel()
        val holder = FloatValueHolder(pressProgress * 100f)
        pressSpring = SpringAnimation(holder, target * 100f).apply {
            spring = SpringForce(target * 100f).apply {
                dampingRatio = SpringForce.DAMPING_RATIO_MEDIUM_BOUNCY
                stiffness = SpringForce.STIFFNESS_MEDIUM
            }
            addUpdateListener { _, value, _ ->
                pressProgress = (value / 100f).coerceIn(0f, 1.25f)
                invalidate()
            }
            start()
        }
    }

    fun startAmbientRefraction() {
        if (ambientAnimator?.isRunning == true) return
        ambientAnimator = ValueAnimator.ofFloat(0f, 6.28318f).apply {
            duration = 6000L
            repeatCount = ValueAnimator.INFINITE
            interpolator = LinearInterpolator()
            addUpdateListener {
                shimmerPhase = it.animatedValue as Float
                invalidate()
            }
            start()
        }
    }

    fun stopAmbientRefraction() {
        ambientAnimator?.cancel()
        ambientAnimator = null
    }

    override fun onDetachedFromWindow() {
        stopAmbientRefraction()
        pressSpring?.cancel()
        super.onDetachedFromWindow()
    }
}

class LiquidGlassBottomNavBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : FrameLayout(context, attrs, defStyleAttr) {

    data class NavTab(val label: String, val iconRes: Int)

    private val dockContainer = LiquidGlassFrameLayout(context).apply {
        cornerRadiusDp = 32f
        bevelWidthDp = 15f
        dispersionStrength = 0.34f
        specularIntensity = 0.72f
        materialVariant = LiquidGlassFrameLayout.GlassMaterialVariant.REGULAR
    }

    private val dropletPill = LiquidGlassFrameLayout(context).apply {
        cornerRadiusDp = 24f
        bevelWidthDp = 11f
        dispersionStrength = 0.48f
        specularIntensity = 0.92f
        materialVariant = LiquidGlassFrameLayout.GlassMaterialVariant.CLEAR
        enableGelPress = false
    }

    private val itemsRow = LinearLayout(context).apply {
        orientation = LinearLayout.HORIZONTAL
        gravity = Gravity.CENTER_VERTICAL
    }

    private val tabViews = mutableListOf<Pair<ImageView, TextView>>()
    private var selectedIndex = 0
    private var dropletSpringX: SpringAnimation? = null
    private var dropletSpringScale: SpringAnimation? = null
    var onTabSelected: ((Int) -> Unit)? = null

    init {
        val d = resources.displayMetrics.density
        val pad = (6 * d).toInt()
        dockContainer.setPadding(pad, pad, pad, pad)

        val innerFrame = FrameLayout(context)
        innerFrame.addView(dropletPill, LayoutParams(0, LayoutParams.MATCH_PARENT))
        innerFrame.addView(itemsRow, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT))

        dockContainer.addView(innerFrame, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT))
        addView(dockContainer, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT))
    }

    fun setTabs(tabs: List<NavTab>) {
        itemsRow.removeAllViews()
        tabViews.clear()
        val d = resources.displayMetrics.density
        val isDark = (resources.configuration.uiMode and Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES

        tabs.forEachIndexed { index, tab ->
            val tabBox = LinearLayout(context).apply {
                orientation = LinearLayout.VERTICAL
                gravity = Gravity.CENTER
                setPadding(0, (6 * d).toInt(), 0, (6 * d).toInt())
                setOnClickListener {
                    selectTab(index, animate = true, notify = true)
                }
            }

            val iconView = ImageView(context).apply {
                setImageResource(tab.iconRes)
                setColorFilter(
                    if (index == 0) Color.parseColor("#38BDF8")
                    else if (isDark) Color.parseColor("#94A3B8") else Color.parseColor("#475569")
                )
            }

            val labelView = TextView(context).apply {
                text = tab.label
                textSize = 10.5f
                typeface = if (index == 0) Typeface.DEFAULT_BOLD else Typeface.DEFAULT
                setTextColor(
                    if (index == 0) (if (isDark) Color.parseColor("#F8FAFC") else Color.parseColor("#0284C7"))
                    else if (isDark) Color.parseColor("#94A3B8") else Color.parseColor("#475569")
                )
                gravity = Gravity.CENTER
                setPadding(0, (3 * d).toInt(), 0, 0)
            }

            tabBox.addView(iconView, LinearLayout.LayoutParams((20 * d).toInt(), (20 * d).toInt()))
            tabBox.addView(labelView, LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT))

            val lp = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.MATCH_PARENT, 1f)
            itemsRow.addView(tabBox, lp)
            tabViews.add(Pair(iconView, labelView))
        }

        post {
            updateDropletGeometry(selectedIndex, animate = false)
            dockContainer.startAmbientRefraction()
        }
    }

    fun selectTab(index: Int, animate: Boolean = true, notify: Boolean = false) {
        if (index !in tabViews.indices) return
        if (index != selectedIndex) {
            performHapticFeedback(HapticFeedbackConstants.CLOCK_TICK)
        }
        selectedIndex = index
        val isDark = (resources.configuration.uiMode and Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES

        tabViews.forEachIndexed { i, (icon, label) ->
            val active = (i == index)
            icon.setColorFilter(
                if (active) Color.parseColor("#38BDF8")
                else if (isDark) Color.parseColor("#94A3B8") else Color.parseColor("#475569")
            )
            label.setTextColor(
                if (active) (if (isDark) Color.parseColor("#F8FAFC") else Color.parseColor("#0284C7"))
                else if (isDark) Color.parseColor("#94A3B8") else Color.parseColor("#475569")
            )
            label.typeface = if (active) Typeface.DEFAULT_BOLD else Typeface.DEFAULT
            icon.animate()
                .scaleX(if (active) 1.12f else 1.0f)
                .scaleY(if (active) 1.12f else 1.0f)
                .setDuration(180L)
                .start()
        }

        updateDropletGeometry(index, animate)
        if (notify) {
            onTabSelected?.invoke(index)
        }
    }

    private fun updateDropletGeometry(index: Int, animate: Boolean) {
        if (tabViews.isEmpty() || itemsRow.width <= 0) return
        val tabWidth = itemsRow.width.toFloat() / tabViews.size
        val targetX = index * tabWidth
        val lp = dropletPill.layoutParams
        if (lp.width != tabWidth.toInt()) {
            lp.width = tabWidth.toInt()
            dropletPill.layoutParams = lp
        }

        if (!animate) {
            dropletPill.translationX = targetX
            return
        }

        dropletSpringX?.cancel()
        val holderX = FloatValueHolder(dropletPill.translationX)
        dropletSpringX = SpringAnimation(holderX, targetX).apply {
            spring = SpringForce(targetX).apply {
                dampingRatio = SpringForce.DAMPING_RATIO_LOW_BOUNCY
                stiffness = SpringForce.STIFFNESS_LOW
            }
            addUpdateListener { _, value, _ ->
                dropletPill.translationX = value
            }
            start()
        }

        dropletSpringScale?.cancel()
        val holderS = FloatValueHolder(116f)
        dropletSpringScale = SpringAnimation(holderS, 100f).apply {
            spring = SpringForce(100f).apply {
                dampingRatio = SpringForce.DAMPING_RATIO_MEDIUM_BOUNCY
                stiffness = SpringForce.STIFFNESS_MEDIUM
            }
            addUpdateListener { _, value, _ ->
                val s = value / 100f
                dropletPill.scaleX = s
                dropletPill.scaleY = 2.0f - s
            }
            start()
        }
    }

    override fun onDetachedFromWindow() {
        dockContainer.stopAmbientRefraction()
        dropletSpringX?.cancel()
        dropletSpringScale?.cancel()
        super.onDetachedFromWindow()
    }
}
""",

    # --------------------------------------------------------------------------
    # 13. CUSTOM VIEWS: SIRI EDGE GLOW AURA & 60 FPS VOICE WAVEFORM
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/ui/OverlayEffectsViews.kt": r"""package com.example.floatinggeminiai.ui

import android.animation.ValueAnimator
import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Matrix
import android.graphics.Paint
import android.graphics.RectF
import android.graphics.SweepGradient
import android.util.AttributeSet
import android.view.View
import android.view.animation.LinearInterpolator
import kotlin.math.sin

class SiriEdgeGlowView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var rotationAngle = 0f
    private var glowIntensity = 0f
    private var animator: ValueAnimator? = null
    private val shaderMatrix = Matrix()
    private var sweepShader: SweepGradient? = null

    private val outerGlowPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { style = Paint.Style.STROKE }
    private val innerRimPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { style = Paint.Style.STROKE }
    private val outerRect = RectF()
    private val innerRect = RectF()

    private val siriColors = intArrayOf(
        Color.parseColor("#38BDF8"),
        Color.parseColor("#818CF8"),
        Color.parseColor("#E879F9"),
        Color.parseColor("#FB7185"),
        Color.parseColor("#34D399"),
        Color.parseColor("#38BDF8")
    )

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        if (w > 0 && h > 0) {
            sweepShader = SweepGradient(w / 2f, h / 2f, siriColors, null)
            outerGlowPaint.shader = sweepShader
            innerRimPaint.shader = sweepShader
            val d = resources.displayMetrics.density
            outerGlowPaint.strokeWidth = 22f * d
            innerRimPaint.strokeWidth = 5f * d
            outerRect.set(11f * d, 11f * d, w - 11f * d, h - 11f * d)
            innerRect.set(3f * d, 3f * d, w - 3f * d, h - 3f * d)
        }
    }

    fun startSiriAnimation() {
        animate().alpha(1f).setDuration(240L).start()
        if (animator?.isRunning == true) return
        animator = ValueAnimator.ofFloat(0f, 360f).apply {
            duration = 2800L
            repeatCount = ValueAnimator.INFINITE
            interpolator = LinearInterpolator()
            addUpdateListener {
                rotationAngle = it.animatedValue as Float
                glowIntensity = 0.78f + 0.22f * sin(Math.toRadians(rotationAngle * 2.0)).toFloat()
                invalidate()
            }
            start()
        }
    }

    fun stopAndFreezeAnimation() {
        animator?.cancel()
        animator = null
        alpha = 0f
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val shader = sweepShader ?: return
        shaderMatrix.setRotate(rotationAngle, width / 2f, height / 2f)
        shader.setLocalMatrix(shaderMatrix)
        val corner = 38f * resources.displayMetrics.density
        outerGlowPaint.alpha = (95 * glowIntensity).toInt().coerceIn(30, 140)
        innerRimPaint.alpha = (230 * glowIntensity).toInt().coerceIn(120, 255)
        canvas.drawRoundRect(outerRect, corner, corner, outerGlowPaint)
        canvas.drawRoundRect(innerRect, corner, corner, innerRimPaint)
    }
}

class VoiceWaveformView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var amplitude = 0.1f
    private var phase = 0f
    private val barPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#38BDF8")
        strokeCap = Paint.Cap.ROUND
    }
    private val barRect = RectF()

    fun setAmplitude(amp: Float) {
        amplitude = amp.coerceIn(0.08f, 1.0f)
        phase += 0.35f
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        if (width <= 0 || height <= 0) return
        val bars = 18
        val step = width.toFloat() / bars
        val barWidth = step * 0.45f
        val cy = height / 2f

        for (i in 0 until bars) {
            val wave = sin(phase + i * 0.55f).toFloat()
            val dynamicFactor = (0.35f + 0.65f * ((wave + 1f) / 2f)) * amplitude
            val halfH = (height * 0.44f * dynamicFactor).coerceAtLeast(3f * resources.displayMetrics.density)
            val cx = i * step + step / 2f
            barRect.set(cx - barWidth / 2f, cy - halfH, cx + barWidth / 2f, cy + halfH)
            canvas.drawRoundRect(barRect, barWidth / 2f, barWidth / 2f, barPaint)
        }
    }
}
""",

    # --------------------------------------------------------------------------
    # 14. LAYOUTS: MAIN ACTIVITY (KYANT0 LIQUID GLASS UI + FLOATING NAVBAR)
    # --------------------------------------------------------------------------
    "app/src/main/res/layout/activity_main.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/mainRootFrame"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#050811">

    <!-- AMBIENT AURORA BACKDROP FOR LIQUID GLASS REFRACTION -->
    <View
        android:layout_width="290dp"
        android:layout_height="290dp"
        android:layout_gravity="top|start"
        android:layout_marginStart="-70dp"
        android:layout_marginTop="-40dp"
        android:alpha="0.32"
        android:background="@drawable/bg_ambient_orb_cyan" />

    <View
        android:layout_width="320dp"
        android:layout_height="320dp"
        android:layout_gravity="bottom|end"
        android:layout_marginEnd="-80dp"
        android:layout_marginBottom="40dp"
        android:alpha="0.26"
        android:background="@drawable/bg_ambient_orb_purple" />

    <!-- SCROLLABLE CONTENT PAGES -->
    <ScrollView
        android:id="@+id/mainScrollView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:fillViewport="true"
        android:clipToPadding="false"
        android:paddingTop="40dp"
        android:paddingBottom="108dp"
        android:paddingHorizontal="16dp">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical">

            <!-- TOP HEADER BAR -->
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:gravity="center_vertical"
                android:layout_marginBottom="16dp">

                <com.example.floatinggeminiai.ui.LiquidGlassFrameLayout
                    android:id="@+id/glassHeaderBadge"
                    android:layout_width="46dp"
                    android:layout_height="46dp">

                    <ImageView
                        android:layout_width="24dp"
                        android:layout_height="24dp"
                        android:layout_gravity="center"
                        android:src="@drawable/ic_sparkle"
                        app:tint="#38BDF8" />
                </com.example.floatinggeminiai.ui.LiquidGlassFrameLayout>

                <LinearLayout
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:layout_marginStart="12dp"
                    android:orientation="vertical">

                    <TextView
                        android:id="@+id/tvMainTitle"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Floamini OS v7.1"
                        android:textSize="24sp"
                        android:textStyle="bold"
                        android:textColor="#F8FAFC" />

                    <TextView
                        android:id="@+id/tvMainSubtitle"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Kyant0 Liquid Glass • Multi-AI Overlay"
                        android:textSize="12sp"
                        android:textColor="#94A3B8" />
                </LinearLayout>

                <Button
                    android:id="@+id/btnOpenWelcome"
                    android:layout_width="wrap_content"
                    android:layout_height="38dp"
                    android:text="Panduan"
                    android:textAllCaps="false"
                    android:textSize="12sp"
                    android:textColor="#38BDF8"
                    android:background="@drawable/bg_chip_glass" />
            </LinearLayout>

            <!-- ============================================================== -->
            <!-- TAB 0: BERANDA (CONTROL HUB) -->
            <!-- ============================================================== -->
            <LinearLayout
                android:id="@+id/pageHome"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical">

                <!-- LIQUID GLASS STATUS & LAUNCHER CARD -->
                <com.example.floatinggeminiai.ui.LiquidGlassFrameLayout
                    android:id="@+id/glassCardHero"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="14dp">

                    <LinearLayout
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:orientation="vertical"
                        android:padding="18dp">

                        <LinearLayout
                            android:layout_width="match_parent"
                            android:layout_height="wrap_content"
                            android:orientation="horizontal"
                            android:gravity="center_vertical"
                            android:layout_marginBottom="12dp">

                            <TextView
                                android:id="@+id/tvActiveEngineSummary"
                                android:layout_width="0dp"
                                android:layout_height="wrap_content"
                                android:layout_weight="1"
                                android:text="Engine: Google Gemini (gemini-2.5-flash)"
                                android:textSize="13sp"
                                android:textStyle="bold"
                                android:textColor="#E2E8F0" />

                            <TextView
                                android:id="@+id/tvPermissionBadge"
                                android:layout_width="wrap_content"
                                android:layout_height="wrap_content"
                                android:text="Overlay: Cek"
                                android:textSize="11sp"
                                android:textStyle="bold"
                                android:textColor="#38BDF8"
                                android:paddingHorizontal="10dp"
                                android:paddingVertical="4dp"
                                android:background="@drawable/bg_chip_glass" />
                        </LinearLayout>

                        <Button
                            android:id="@+id/btnGrantOverlay"
                            android:layout_width="match_parent"
                            android:layout_height="44dp"
                            android:text="1. Beri Izin Tampil di Atas Aplikasi Lain"
                            android:textAllCaps="false"
                            android:textColor="#F8FAFC"
                            android:backgroundTint="#1E293B"
                            android:layout_marginBottom="8dp" />

                        <Button
                            android:id="@+id/btnStartService"
                            android:layout_width="match_parent"
                            android:layout_height="48dp"
                            android:text="2. Aktifkan Floamini Liquid Overlay"
                            android:textAllCaps="false"
                            android:textStyle="bold"
                            android:textColor="#020617"
                            android:backgroundTint="#38BDF8"
                            android:layout_marginBottom="8dp" />

                        <LinearLayout
                            android:layout_width="match_parent"
                            android:layout_height="wrap_content"
                            android:orientation="horizontal">

                            <Button
                                android:id="@+id/btnSummonSiriNow"
                                android:layout_width="0dp"
                                android:layout_height="42dp"
                                android:layout_weight="1"
                                android:layout_marginEnd="6dp"
                                android:text="Panggil Siri Aura"
                                android:textAllCaps="false"
                                android:textSize="12sp"
                                android:textColor="#E879F9"
                                android:background="@drawable/bg_chip_glass" />

                            <Button
                                android:id="@+id/btnForceStopService"
                                android:layout_width="0dp"
                                android:layout_height="42dp"
                                android:layout_weight="1"
                                android:layout_marginStart="6dp"
                                android:text="Quick Force Stop"
                                android:textAllCaps="false"
                                android:textSize="12sp"
                                android:textColor="#FCA5A5"
                                android:background="@drawable/bg_chip_glass" />
                        </LinearLayout>
                    </LinearLayout>
                </com.example.floatinggeminiai.ui.LiquidGlassFrameLayout>

                <!-- LIQUID GLASS USAGE & TELEMETRY CARD -->
                <com.example.floatinggeminiai.ui.LiquidGlassFrameLayout
                    android:id="@+id/glassCardStats"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="14dp">

                    <LinearLayout
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:orientation="vertical"
                        android:padding="18dp">

                        <TextView
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="STATISTIK PENGGUNAAN &amp; PRIVASI"
                            android:textSize="11sp"
                            android:textStyle="bold"
                            android:textColor="#38BDF8"
                            android:layout_marginBottom="6dp" />

                        <TextView
                            android:id="@+id/tvUsageStats"
                            android:layout_width="match_parent"
                            android:layout_height="wrap_content"
                            android:text="Total Permintaan: 0 kali"
                            android:textSize="13sp"
                            android:textColor="#CBD5E1"
                            android:layout_marginBottom="10dp" />

                        <TextView
                            android:layout_width="match_parent"
                            android:layout_height="wrap_content"
                            android:text="Semua API Key dienkripsi lokal dengan AES256-GCM. Layar &amp; clipboard tidak pernah dibaca tanpa ketukan Anda."
                            android:textSize="11.5sp"
                            android:textColor="#94A3B8" />
                    </LinearLayout>
                </com.example.floatinggeminiai.ui.LiquidGlassFrameLayout>
            </LinearLayout>

            <!-- ============================================================== -->
            <!-- TAB 1: AI & KEYS (MULTI-PROVIDER VAULT) -->
            <!-- ============================================================== -->
            <LinearLayout
                android:id="@+id/pageAiProviders"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:visibility="gone">

                <com.example.floatinggeminiai.ui.LiquidGlassFrameLayout
                    android:id="@+id/glassCardProvider"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="14dp">

                    <LinearLayout
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:orientation="vertical"
                        android:padding="18dp">

                        <TextView
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="MULTI-AI PROVIDER &amp; ENCRYPTED VAULT"
                            android:textSize="11sp"
                            android:textStyle="bold"
                            android:textColor="#38BDF8"
                            android:layout_marginBottom="10dp" />

                        <TextView
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Pilih Provider AI (11 Engine Didukung)"
                            android:textSize="12sp"
                            android:textColor="#94A3B8"
                            android:layout_marginBottom="4dp" />

                        <Spinner
                            android:id="@+id/spinnerProvider"
                            android:layout_width="match_parent"
                            android:layout_height="44dp"
                            android:background="@drawable/bg_input_glass"
                            android:paddingHorizontal="12dp"
                            android:layout_marginBottom="10dp" />

                        <TextView
                            android:id="@+id/tvProviderKeyStatus"
                            android:layout_width="match_parent"
                            android:layout_height="wrap_content"
                            android:text="Status Vault: Belum diisi"
                            android:textSize="12sp"
                            android:textColor="#38BDF8"
                            android:layout_marginBottom="6dp" />

                        <EditText
                            android:id="@+id/etProviderApiKey"
                            android:layout_width="match_parent"
                            android:layout_height="46dp"
                            android:hint="Tempel API Key Provider terpilih..."
                            android:textColor="#F8FAFC"
                            android:textColorHint="#64748B"
                            android:textSize="13sp"
                            android:inputType="textPassword"
                            android:paddingHorizontal="14dp"
                            android:background="@drawable/bg_input_glass"
                            android:layout_marginBottom="8dp" />

                        <LinearLayout
                            android:id="@+id/layoutCustomEndpoint"
                            android:layout_width="match_parent"
                            android:layout_height="wrap_content"
                            android:orientation="vertical"
                            android:visibility="gone"
                            android:layout_marginBottom="8dp">

                            <EditText
                                android:id="@+id/etCustomBaseUrl"
                                android:layout_width="match_parent"
                                android:layout_height="44dp"
                                android:hint="Custom Base URL (mis. https://api.openai.com/v1)"
                                android:textColor="#F8FAFC"
                                android:textColorHint="#64748B"
                                android:textSize="12.5sp"
                                android:paddingHorizontal="12dp"
                                android:background="@drawable/bg_input_glass"
                                android:layout_marginBottom="6dp" />

                            <EditText
                                android:id="@+id/etCustomModelId"
                                android:layout_width="match_parent"
                                android:layout_height="44dp"
                                android:hint="Custom Model ID (mis. gpt-4o-mini)"
                                android:textColor="#F8FAFC"
                                android:textColorHint="#64748B"
                                android:textSize="12.5sp"
                                android:paddingHorizontal="12dp"
                                android:background="@drawable/bg_input_glass" />
                        </LinearLayout>

                        <LinearLayout
                            android:layout_width="match_parent"
                            android:layout_height="wrap_content"
                            android:orientation="horizontal"
                            android:layout_marginBottom="10dp">

                            <Button
                                android:id="@+id/btnSaveProviderKey"
                                android:layout_width="0dp"
                                android:layout_height="42dp"
                                android:layout_weight="1"
                                android:layout_marginEnd="6dp"
                                android:text="Simpan ke Vault"
                                android:textAllCaps="false"
                                android:textSize="12sp"
                                android:textStyle="bold"
                                android:textColor="#020617"
                                android:backgroundTint="#38BDF8" />

                            <Button
                                android:id="@+id/btnTestProviderConnection"
                                android:layout_width="0dp"
                                android:layout_height="42dp"
                                android:layout_weight="1"
                                android:layout_marginStart="6dp"
                                android:text="Tes Koneksi"
                                android:textAllCaps="false"
                                android:textSize="12sp"
                                android:textColor="#F8FAFC"
                                android:background="@drawable/bg_chip_glass" />
                        </LinearLayout>

                        <TextView
                            android:id="@+id/tvTestConnectionResult"
                            android:layout_width="match_parent"
                            android:layout_height="wrap_content"
                            android:text=""
                            android:textSize="12sp"
                            android:textColor="#34D399"
                            android:visibility="gone"
                            android:layout_marginBottom="8dp" />

                        <TextView
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Model Aktif"
                            android:textSize="12sp"
                            android:textColor="#94A3B8"
                            android:layout_marginBottom="4dp" />

                        <Spinner
                            android:id="@+id/spinnerModel"
                            android:layout_width="match_parent"
                            android:layout_height="44dp"
                            android:background="@drawable/bg_input_glass"
                            android:paddingHorizontal="12dp"
                            android:layout_marginBottom="10dp" />

                        <TextView
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Kepribadian &amp; Gaya Bicara AI"
                            android:textSize="12sp"
                            android:textColor="#94A3B8"
                            android:layout_marginBottom="4dp" />

                        <Spinner
                            android:id="@+id/spinnerPersonality"
                            android:layout_width="match_parent"
                            android:layout_height="44dp"
                            android:background="@drawable/bg_input_glass"
                            android:paddingHorizontal="12dp"
                            android:layout_marginBottom="10dp" />

                        <EditText
                            android:id="@+id/etCustomPersona"
                            android:layout_width="match_parent"
                            android:layout_height="68dp"
                            android:hint="Instruksi sistem tambahan (opsional)..."
                            android:textColor="#F8FAFC"
                            android:textColorHint="#64748B"
                            android:textSize="12.5sp"
                            android:gravity="top"
                            android:padding="12dp"
                            android:background="@drawable/bg_input_glass" />
                    </LinearLayout>
                </com.example.floatinggeminiai.ui.LiquidGlassFrameLayout>
            </LinearLayout>

            <!-- ============================================================== -->
            <!-- TAB 2: OVERLAY & LIQUID GLASS STUDIO -->
            <!-- ============================================================== -->
            <LinearLayout
                android:id="@+id/pageOverlayGlass"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:visibility="gone">

                <com.example.floatinggeminiai.ui.LiquidGlassFrameLayout
                    android:id="@+id/glassCardOverlay"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="14dp">

                    <LinearLayout
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:orientation="vertical"
                        android:padding="18dp">

                        <TextView
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="DYNAMIC ISLAND, SIRI &amp; KYANT0 LIQUID GLASS"
                            android:textSize="11sp"
                            android:textStyle="bold"
                            android:textColor="#38BDF8"
                            android:layout_marginBottom="10dp" />

                        <TextView
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Mode Pemicu Overlay"
                            android:textSize="12sp"
                            android:textColor="#94A3B8"
                            android:layout_marginBottom="4dp" />

                        <Spinner
                            android:id="@+id/spinnerOverlayStyle"
                            android:layout_width="match_parent"
                            android:layout_height="44dp"
                            android:background="@drawable/bg_input_glass"
                            android:paddingHorizontal="12dp"
                            android:layout_marginBottom="10dp" />

                        <TextView
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Tampilan Pil Dynamic Island"
                            android:textSize="12sp"
                            android:textColor="#94A3B8"
                            android:layout_marginBottom="4dp" />

                        <Spinner
                            android:id="@+id/spinnerPillAppearance"
                            android:layout_width="match_parent"
                            android:layout_height="44dp"
                            android:background="@drawable/bg_input_glass"
                            android:paddingHorizontal="12dp"
                            android:layout_marginBottom="10dp" />

                        <Switch
                            android:id="@+id/switchAutoHidePill"
                            android:layout_width="match_parent"
                            android:layout_height="42dp"
                            android:text="Auto-Hide Pil Setelah 3 Detik Diam"
                            android:textColor="#E2E8F0"
                            android:textSize="13sp" />

                        <Switch
                            android:id="@+id/switchSmartFreeze"
                            android:layout_width="match_parent"
                            android:layout_height="42dp"
                            android:text="Auto Smart Freeze (Hemat RAM &amp; Baterai)"
                            android:textColor="#E2E8F0"
                            android:textSize="13sp"
                            android:checked="true" />

                        <Switch
                            android:id="@+id/switchLiquidBlur"
                            android:layout_width="match_parent"
                            android:layout_height="42dp"
                            android:text="Real Window Blur &amp; Chromatic Dispersion"
                            android:textColor="#E2E8F0"
                            android:textSize="13sp"
                            android:checked="true" />

                        <TextView
                            android:id="@+id/tvIslandWidthLabel"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Lebar Pil Dynamic Island: 164dp"
                            android:textSize="12sp"
                            android:textColor="#94A3B8"
                            android:layout_marginTop="8dp" />

                        <SeekBar
                            android:id="@+id/seekIslandWidth"
                            android:layout_width="match_parent"
                            android:layout_height="wrap_content"
                            android:max="180"
                            android:progress="64" />

                        <TextView
                            android:id="@+id/tvIslandYLabel"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Posisi Vertikal Atas (Y): 12dp"
                            android:textSize="12sp"
                            android:textColor="#94A3B8"
                            android:layout_marginTop="6dp" />

                        <SeekBar
                            android:id="@+id/seekIslandY"
                            android:layout_width="match_parent"
                            android:layout_height="wrap_content"
                            android:max="120"
                            android:progress="12" />

                        <TextView
                            android:id="@+id/tvIslandXLabel"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Geser Horizontal Kamera (X): 0dp"
                            android:textSize="12sp"
                            android:textColor="#94A3B8"
                            android:layout_marginTop="6dp" />

                        <SeekBar
                            android:id="@+id/seekIslandX"
                            android:layout_width="match_parent"
                            android:layout_height="wrap_content"
                            android:max="240"
                            android:progress="120" />

                        <TextView
                            android:id="@+id/tvOpacityLabel"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Transparansi Jendela Glass: 92%"
                            android:textSize="12sp"
                            android:textColor="#94A3B8"
                            android:layout_marginTop="6dp" />

                        <SeekBar
                            android:id="@+id/seekPopupOpacity"
                            android:layout_width="match_parent"
                            android:layout_height="wrap_content"
                            android:max="45"
                            android:progress="37" />

                        <TextView
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Tema Adaptif UI"
                            android:textSize="12sp"
                            android:textColor="#94A3B8"
                            android:layout_marginTop="8dp"
                            android:layout_marginBottom="4dp" />

                        <Spinner
                            android:id="@+id/spinnerThemeMode"
                            android:layout_width="match_parent"
                            android:layout_height="44dp"
                            android:background="@drawable/bg_input_glass"
                            android:paddingHorizontal="12dp"
                            android:layout_marginBottom="10dp" />

                        <Button
                            android:id="@+id/btnAddControlCenterTile"
                            android:layout_width="match_parent"
                            android:layout_height="44dp"
                            android:text="Tambah Tombol Siri ke Control Center"
                            android:textAllCaps="false"
                            android:textSize="12.5sp"
                            android:textColor="#38BDF8"
                            android:background="@drawable/bg_chip_glass" />
                    </LinearLayout>
                </com.example.floatinggeminiai.ui.LiquidGlassFrameLayout>
            </LinearLayout>

            <!-- ============================================================== -->
            <!-- TAB 3: TOOLS & DATA -->
            <!-- ============================================================== -->
            <LinearLayout
                android:id="@+id/pageToolsData"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:visibility="gone">

                <com.example.floatinggeminiai.ui.LiquidGlassFrameLayout
                    android:id="@+id/glassCardTools"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:layout_marginBottom="14dp">

                    <LinearLayout
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:orientation="vertical"
                        android:padding="18dp">

                        <TextView
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="QUICK NOTES &amp; PROMPT LIBRARY"
                            android:textSize="11sp"
                            android:textStyle="bold"
                            android:textColor="#38BDF8"
                            android:layout_marginBottom="8dp" />

                        <EditText
                            android:id="@+id/etMainQuickNotes"
                            android:layout_width="match_parent"
                            android:layout_height="110dp"
                            android:hint="Tulis catatan cepat yang juga bisa diakses dari jendela melayang..."
                            android:textColor="#F8FAFC"
                            android:textColorHint="#64748B"
                            android:textSize="13sp"
                            android:gravity="top"
                            android:padding="12dp"
                            android:background="@drawable/bg_input_glass"
                            android:layout_marginBottom="10dp" />

                        <Button
                            android:id="@+id/btnSaveQuickNotes"
                            android:layout_width="match_parent"
                            android:layout_height="42dp"
                            android:text="Simpan Catatan Cepat"
                            android:textAllCaps="false"
                            android:textSize="12.5sp"
                            android:textColor="#020617"
                            android:backgroundTint="#38BDF8"
                            android:layout_marginBottom="12dp" />

                        <Button
                            android:id="@+id/btnClearAllHistory"
                            android:layout_width="match_parent"
                            android:layout_height="42dp"
                            android:text="Hapus Semua Riwayat Percakapan"
                            android:textAllCaps="false"
                            android:textSize="12.5sp"
                            android:textColor="#FCA5A5"
                            android:background="@drawable/bg_chip_glass" />
                    </LinearLayout>
                </com.example.floatinggeminiai.ui.LiquidGlassFrameLayout>
            </LinearLayout>

        </LinearLayout>
    </ScrollView>

    <!-- KYANT0 FLOATING LIQUID GLASS BOTTOM NAVBAR -->
    <com.example.floatinggeminiai.ui.LiquidGlassBottomNavBar
        android:id="@+id/liquidBottomNavBar"
        android:layout_width="match_parent"
        android:layout_height="72dp"
        android:layout_gravity="bottom"
        android:layout_marginHorizontal="16dp"
        android:layout_marginBottom="16dp"
        android:elevation="20dp" />

</FrameLayout>
""",

    # --------------------------------------------------------------------------
    # 15. LAYOUTS: WELCOME ACTIVITY (FIRST WELCOME + API GUIDE)
    # --------------------------------------------------------------------------
    "app/src/main/res/layout/activity_welcome.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#050811"
    android:fillViewport="true">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="20dp">

        <com.example.floatinggeminiai.ui.LiquidGlassFrameLayout
            android:id="@+id/glassWelcomeHero"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="24dp"
            android:layout_marginBottom="16dp">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="20dp">

                <ImageView
                    android:layout_width="36dp"
                    android:layout_height="36dp"
                    android:src="@drawable/ic_sparkle"
                    app:tint="#38BDF8"
                    android:layout_marginBottom="10dp" />

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Selamat Datang di Floamini"
                    android:textSize="22sp"
                    android:textStyle="bold"
                    android:textColor="#F8FAFC" />

                <TextView
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:layout_marginTop="6dp"
                    android:text="Asisten AI melayang dengan Kyant0 Liquid Glass, Dynamic Island, Siri Mode, dan 11 AI Provider langsung di atas aplikasi apa pun."
                    android:textSize="13sp"
                    android:textColor="#CBD5E1" />
            </LinearLayout>
        </com.example.floatinggeminiai.ui.LiquidGlassFrameLayout>

        <com.example.floatinggeminiai.ui.LiquidGlassFrameLayout
            android:id="@+id/glassWelcomeGuide"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="16dp">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="20dp">

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="CARA MENDAPATKAN GEMINI API KEY GRATIS"
                    android:textSize="11sp"
                    android:textStyle="bold"
                    android:textColor="#38BDF8"
                    android:layout_marginBottom="8dp" />

                <TextView
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:text="1. Ketuk tombol Buka Google AI Studio di bawah.\n2. Masuk dengan akun Google Anda, lalu pilih Create API key.\n3. Salin kunci (diawali AIzaSy...) dan tempelkan di kolom bawah ini."
                    android:textSize="12.5sp"
                    android:textColor="#E2E8F0"
                    android:layout_marginBottom="12dp" />

                <Button
                    android:id="@+id/btnOpenAiStudio"
                    android:layout_width="match_parent"
                    android:layout_height="42dp"
                    android:text="Buka Google AI Studio (aistudio.google.com)"
                    android:textAllCaps="false"
                    android:textSize="12.5sp"
                    android:textColor="#38BDF8"
                    android:background="@drawable/bg_chip_glass"
                    android:layout_marginBottom="10dp" />

                <EditText
                    android:id="@+id/etWelcomeGeminiKey"
                    android:layout_width="match_parent"
                    android:layout_height="46dp"
                    android:hint="Tempel Gemini API Key (AIzaSy...)..."
                    android:textColor="#F8FAFC"
                    android:textColorHint="#64748B"
                    android:textSize="13sp"
                    android:paddingHorizontal="14dp"
                    android:background="@drawable/bg_input_glass"
                    android:layout_marginBottom="10dp" />

                <Button
                    android:id="@+id/btnWelcomeSaveAndTest"
                    android:layout_width="match_parent"
                    android:layout_height="44dp"
                    android:text="Simpan &amp; Tes Koneksi Token"
                    android:textAllCaps="false"
                    android:textSize="13sp"
                    android:textStyle="bold"
                    android:textColor="#020617"
                    android:backgroundTint="#38BDF8" />

                <TextView
                    android:id="@+id/tvWelcomeTestStatus"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:layout_marginTop="8dp"
                    android:text=""
                    android:textSize="12sp"
                    android:textColor="#34D399"
                    android:visibility="gone" />
            </LinearLayout>
        </com.example.floatinggeminiai.ui.LiquidGlassFrameLayout>

        <Button
            android:id="@+id/btnWelcomeFinish"
            android:layout_width="match_parent"
            android:layout_height="48dp"
            android:text="Mulai Gunakan Floamini"
            android:textAllCaps="false"
            android:textStyle="bold"
            android:textColor="#F8FAFC"
            android:background="@drawable/bg_chip_glass" />

    </LinearLayout>
</ScrollView>
""",

    # --------------------------------------------------------------------------
    # 16. LAYOUTS: FLOATING OVERLAY (DYNAMIC ISLAND + LIQUID GLASS CHAT)
    # --------------------------------------------------------------------------
    "app/src/main/res/layout/layout_floating_assistant.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/floatingRootContainer"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content">

    <!-- 1A. DYNAMIC ISLAND PILL (KYANT0 CLEAR LIQUID GLASS) -->
    <com.example.floatinggeminiai.ui.LiquidGlassFrameLayout
        android:id="@+id/dynamicIslandGlassHost"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:elevation="16dp">

        <LinearLayout
            android:id="@+id/dynamicIslandView"
            android:layout_width="164dp"
            android:layout_height="34dp"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:paddingHorizontal="12dp">

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
    </com.example.floatinggeminiai.ui.LiquidGlassFrameLayout>

    <!-- 1B. CLASSIC FLOATING BUBBLE -->
    <FrameLayout
        android:id="@+id/bubbleView"
        android:layout_width="54dp"
        android:layout_height="54dp"
        android:background="@drawable/bg_bubble_classic"
        android:elevation="14dp"
        android:visibility="gone">

        <ImageView
            android:layout_width="26dp"
            android:layout_height="26dp"
            android:layout_gravity="center"
            android:src="@drawable/ic_sparkle"
            app:tint="#38BDF8" />
    </FrameLayout>

    <!-- 1C. XIAOMI EDGE SIDEBAR PILL -->
    <FrameLayout
        android:id="@+id/xiaomiEdgeView"
        android:layout_width="16dp"
        android:layout_height="54dp"
        android:background="@drawable/bg_xiaomi_edge"
        android:elevation="14dp"
        android:visibility="gone" />

    <!-- 2. JENDELA CHAT GENUINE LIQUID GLASS (KYANT0 AGSL SHADER CONTAINER) -->
    <com.example.floatinggeminiai.ui.LiquidGlassFrameLayout
        android:id="@+id/popupChatView"
        android:layout_width="352dp"
        android:layout_height="500dp"
        android:elevation="22dp"
        android:visibility="gone">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:orientation="vertical">

            <!-- TOP HEADER BAR -->
            <LinearLayout
                android:id="@+id/glassTitleBar"
                android:layout_width="match_parent"
                android:layout_height="44dp"
                android:orientation="horizontal"
                android:gravity="center_vertical"
                android:paddingHorizontal="12dp">

                <ImageView
                    android:layout_width="17dp"
                    android:layout_height="17dp"
                    android:src="@drawable/ic_sparkle"
                    app:tint="#38BDF8" />

                <TextView
                    android:id="@+id/tvActiveProviderHeader"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:layout_marginStart="8dp"
                    android:text="Gemini 2.5 Flash"
                    android:textSize="12.5sp"
                    android:textStyle="bold"
                    android:textColor="#F8FAFC"
                    android:singleLine="true" />

                <ImageView
                    android:id="@+id/btnCompareMode"
                    android:layout_width="28dp"
                    android:layout_height="28dp"
                    android:padding="5dp"
                    android:src="@drawable/ic_compare"
                    app:tint="#94A3B8"
                    android:contentDescription="Compare AI" />

                <ImageView
                    android:id="@+id/btnScreenShare"
                    android:layout_width="28dp"
                    android:layout_height="28dp"
                    android:padding="5dp"
                    android:src="@drawable/ic_screen_share"
                    app:tint="#94A3B8"
                    android:contentDescription="Live Screen Vision" />

                <ImageView
                    android:id="@+id/btnToggleMiniWindow"
                    android:layout_width="28dp"
                    android:layout_height="28dp"
                    android:padding="6dp"
                    android:src="@drawable/ic_expand"
                    app:tint="#94A3B8"
                    android:contentDescription="Mini/Full Window" />

                <ImageView
                    android:id="@+id/btnToggleSmartDrawer"
                    android:layout_width="28dp"
                    android:layout_height="28dp"
                    android:padding="5dp"
                    android:src="@drawable/ic_plus"
                    app:tint="#38BDF8"
                    android:contentDescription="Smart Tools" />

                <ImageView
                    android:id="@+id/btnClosePopup"
                    android:layout_width="28dp"
                    android:layout_height="28dp"
                    android:padding="6dp"
                    android:src="@drawable/ic_close"
                    app:tint="#FCA5A5"
                    android:contentDescription="Tutup" />
            </LinearLayout>

            <!-- STATUS STRIPS -->
            <TextView
                android:id="@+id/tvScreenShareStatus"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="LIVE SCREEN VISION AKTIF • AI DAPAT MELIHAT LAYAR ANDA"
                android:textSize="10sp"
                android:textStyle="bold"
                android:textColor="#38BDF8"
                android:gravity="center"
                android:paddingVertical="3dp"
                android:background="#2238BDF8"
                android:visibility="gone" />

            <TextView
                android:id="@+id/tvAttachmentBadge"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text=""
                android:textSize="11sp"
                android:textColor="#E879F9"
                android:paddingHorizontal="12dp"
                android:paddingVertical="4dp"
                android:background="#22E879F9"
                android:visibility="gone" />

            <!-- SMART TOOLS & SEARCH DRAWER -->
            <LinearLayout
                android:id="@+id/smartToolsDrawer"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:paddingHorizontal="12dp"
                android:paddingVertical="8dp"
                android:background="#33020617"
                android:visibility="gone">

                <HorizontalScrollView
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:scrollbars="none"
                    android:layout_marginBottom="6dp">

                    <LinearLayout
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:orientation="horizontal">

                        <TextView
                            android:id="@+id/chipSwitchProvider"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Ganti AI"
                            android:textSize="11sp"
                            android:textColor="#38BDF8"
                            android:paddingHorizontal="10dp"
                            android:paddingVertical="5dp"
                            android:layout_marginEnd="6dp"
                            android:background="@drawable/bg_chip_glass" />

                        <TextView
                            android:id="@+id/chipAutoRouter"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Auto-Router: OFF"
                            android:textSize="11sp"
                            android:textColor="#E2E8F0"
                            android:paddingHorizontal="10dp"
                            android:paddingVertical="5dp"
                            android:layout_marginEnd="6dp"
                            android:background="@drawable/bg_chip_glass" />

                        <TextView
                            android:id="@+id/chipClipboard"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Baca Clipboard"
                            android:textSize="11sp"
                            android:textColor="#E2E8F0"
                            android:paddingHorizontal="10dp"
                            android:paddingVertical="5dp"
                            android:layout_marginEnd="6dp"
                            android:background="@drawable/bg_chip_glass" />

                        <TextView
                            android:id="@+id/chipCalculator"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Kalkulator"
                            android:textSize="11sp"
                            android:textColor="#E2E8F0"
                            android:paddingHorizontal="10dp"
                            android:paddingVertical="5dp"
                            android:layout_marginEnd="6dp"
                            android:background="@drawable/bg_chip_glass" />

                        <TextView
                            android:id="@+id/chipNewSession"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Sesi Baru"
                            android:textSize="11sp"
                            android:textColor="#34D399"
                            android:paddingHorizontal="10dp"
                            android:paddingVertical="5dp"
                            android:layout_marginEnd="6dp"
                            android:background="@drawable/bg_chip_glass" />

                        <TextView
                            android:id="@+id/chipQuickForceStop"
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="Force Stop"
                            android:textSize="11sp"
                            android:textColor="#FCA5A5"
                            android:paddingHorizontal="10dp"
                            android:paddingVertical="5dp"
                            android:background="@drawable/bg_chip_glass" />
                    </LinearLayout>
                </HorizontalScrollView>

                <EditText
                    android:id="@+id/etSearchHistory"
                    android:layout_width="match_parent"
                    android:layout_height="34dp"
                    android:hint="Cari riwayat sesi..."
                    android:textSize="11.5sp"
                    android:textColor="#F8FAFC"
                    android:textColorHint="#64748B"
                    android:paddingHorizontal="10dp"
                    android:background="@drawable/bg_input_glass" />

                <LinearLayout
                    android:id="@+id/historyResultsContainer"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:orientation="vertical"
                    android:layout_marginTop="4dp" />
            </LinearLayout>

            <!-- CHAT MESSAGES SCROLL AREA -->
            <ScrollView
                android:id="@+id/chatScrollView"
                android:layout_width="match_parent"
                android:layout_height="0dp"
                android:layout_weight="1"
                android:paddingHorizontal="12dp"
                android:paddingVertical="6dp">

                <LinearLayout
                    android:id="@+id/chatMessagesContainer"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:orientation="vertical" />
            </ScrollView>

            <!-- QUICK ACTION PROMPTS -->
            <HorizontalScrollView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:scrollbars="none"
                android:paddingHorizontal="10dp"
                android:paddingVertical="4dp">

                <LinearLayout
                    android:id="@+id/quickPromptsRow"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:orientation="horizontal" />
            </HorizontalScrollView>

            <!-- VOICE WAVEFORM BAR -->
            <LinearLayout
                android:id="@+id/voiceWaveformBar"
                android:layout_width="match_parent"
                android:layout_height="34dp"
                android:orientation="horizontal"
                android:gravity="center_vertical"
                android:paddingHorizontal="12dp"
                android:visibility="gone">

                <com.example.floatinggeminiai.ui.VoiceWaveformView
                    android:id="@+id/voiceWaveformView"
                    android:layout_width="0dp"
                    android:layout_height="24dp"
                    android:layout_weight="1" />

                <TextView
                    android:id="@+id/tvVoiceHint"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginStart="8dp"
                    android:text="Mendengarkan..."
                    android:textSize="11sp"
                    android:textColor="#38BDF8" />
            </LinearLayout>

            <!-- BOTTOM COMPOSER BAR + RESIZE HANDLE -->
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:gravity="center_vertical"
                android:paddingHorizontal="10dp"
                android:paddingVertical="8dp">

                <ImageView
                    android:id="@+id/btnAttachFile"
                    android:layout_width="32dp"
                    android:layout_height="32dp"
                    android:padding="6dp"
                    android:src="@drawable/ic_attach"
                    app:tint="#94A3B8"
                    android:contentDescription="Lampirkan PDF/Gambar" />

                <ImageView
                    android:id="@+id/btnVoiceMic"
                    android:layout_width="32dp"
                    android:layout_height="32dp"
                    android:padding="6dp"
                    android:src="@drawable/ic_mic"
                    app:tint="#94A3B8"
                    android:contentDescription="Voice Input" />

                <EditText
                    android:id="@+id/etPromptInput"
                    android:layout_width="0dp"
                    android:layout_height="38dp"
                    android:layout_weight="1"
                    android:layout_marginHorizontal="4dp"
                    android:hint="Tanya apa saja..."
                    android:textColor="#F8FAFC"
                    android:textColorHint="#64748B"
                    android:textSize="12.5sp"
                    android:inputType="textCapSentences|textMultiLine"
                    android:imeOptions="actionSend"
                    android:maxLines="3"
                    android:paddingHorizontal="12dp"
                    android:background="@drawable/bg_input_glass" />

                <ImageView
                    android:id="@+id/btnSendOrStop"
                    android:layout_width="34dp"
                    android:layout_height="34dp"
                    android:padding="7dp"
                    android:src="@drawable/ic_send"
                    app:tint="#38BDF8"
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
    </com.example.floatinggeminiai.ui.LiquidGlassFrameLayout>
</FrameLayout>
""",

    # --------------------------------------------------------------------------
    # 17. DRAWABLES: AMBIENT ORBS, GLASS SHAPES & CUSTOM SVG VECTORS
    # --------------------------------------------------------------------------
    "app/src/main/res/drawable/bg_ambient_orb_cyan.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <gradient
        android:type="radial"
        android:gradientRadius="145dp"
        android:startColor="#6638BDF8"
        android:endColor="#0038BDF8" />
</shape>
""",

    "app/src/main/res/drawable/bg_ambient_orb_purple.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <gradient
        android:type="radial"
        android:gradientRadius="160dp"
        android:startColor="#66A855F7"
        android:endColor="#00A855F7" />
</shape>
""",

    "app/src/main/res/drawable/bg_dynamic_island_polos.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#FF000000" />
    <corners android:radius="18dp" />
</shape>
""",

    "app/src/main/res/drawable/bg_island_pulse_dot.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <solid android:color="#38BDF8" />
</shape>
""",

    "app/src/main/res/drawable/bg_bubble_classic.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <gradient
        android:angle="135"
        android:startColor="#E60F172A"
        android:endColor="#F21E293B" />
    <stroke android:width="1.5dp" android:color="#6638BDF8" />
</shape>
""",

    "app/src/main/res/drawable/bg_xiaomi_edge.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#CC38BDF8" />
    <corners android:radius="8dp" />
</shape>
""",

    "app/src/main/res/drawable/bg_input_glass.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#26020617" />
    <stroke android:width="1dp" android:color="#3394A3B8" />
    <corners android:radius="14dp" />
</shape>
""",

    "app/src/main/res/drawable/bg_chip_glass.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#281E293B" />
    <stroke android:width="1dp" android:color="#4038BDF8" />
    <corners android:radius="12dp" />
</shape>
""",

    "app/src/main/res/drawable/bg_msg_user.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient
        android:angle="135"
        android:startColor="#CC0284C7"
        android:endColor="#CC2563EB" />
    <stroke android:width="1dp" android:color="#557DD3FC" />
    <corners android:radius="16dp" />
</shape>
""",

    "app/src/main/res/drawable/bg_msg_ai.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#440F172A" />
    <stroke android:width="1dp" android:color="#33CBD5E1" />
    <corners android:radius="16dp" />
</shape>
""",

    "app/src/main/res/drawable/ic_sparkle.xml": r"""<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF" android:pathData="M12,2L14.4,9.6L22,12L14.4,14.4L12,22L9.6,14.4L2,12L9.6,9.6L12,2Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_home.xml": r"""<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF" android:pathData="M12,3L3,10.5V20C3,20.55 3.45,21 4,21H9V15H15V21H20C20.55,21 21,20.55 21,20V10.5L12,3Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_key.xml": r"""<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF" android:pathData="M12.65,10C11.83,7.67 9.61,6 7,6C3.69,6 1,8.69 1,12C1,15.31 3.69,18 7,18C9.61,18 11.83,16.33 12.65,14H17V18H21V14H23V10H12.65ZM7,14C5.9,14 5,13.1 5,12C5,10.9 5.9,10 7,10C8.1,10 9,10.9 9,12C9,13.1 8.1,14 7,14Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_layers.xml": r"""<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF" android:pathData="M11.99,18.54L4.62,12.81L3,14.07L12,21.07L21,14.07L19.37,12.8L11.99,18.54ZM12,16L19.36,10.27L21,9L12,2L3,9L4.63,10.27L12,16Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_tools.xml": r"""<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF" android:pathData="M22.7,19L13.6,9.9C14.5,7.6 14,4.9 12.1,3C10.1,1 7.1,0.6 4.7,1.7L9,6L6,9L1.6,4.7C0.4,7.1 0.9,10.1 2.9,12.1C4.8,14 7.5,14.5 9.8,13.6L18.9,22.7C19.3,23.1 19.9,23.1 20.3,22.7L22.6,20.4C23.1,20 23.1,19.3 22.7,19Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_send.xml": r"""<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF" android:pathData="M2.01,21L23,12L2.01,3L2,10L17,12L2,14L2.01,21Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_stop.xml": r"""<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF" android:pathData="M6,6H18V18H6V6Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_screen_share.xml": r"""<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF" android:pathData="M20,18C21.1,18 21.99,17.1 21.99,16L22,6C22,4.89 21.1,4 20,4H4C2.89,4 2,4.89 2,6V16C2,17.1 2.89,18 4,18H0V20H24V18H20ZM13,14.47V12.28C10.22,12.28 8.39,13.13 7,15C7.56,12.33 9.11,9.67 13,9.13V7L17,10.73L13,14.47Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_mic.xml": r"""<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF" android:pathData="M12,14C13.66,14 14.99,12.66 14.99,11L15,5C15,3.34 13.66,2 12,2C10.34,2 9,3.34 9,5V11C9,12.66 10.34,14 12,14ZM17.3,11C17.3,14 14.76,16.1 12,16.1C9.24,16.1 6.7,14 6.7,11H5C5,14.41 7.72,17.23 11,17.72V21H13V17.72C16.28,17.24 19,14.42 19,11H17.3Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_plus.xml": r"""<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF" android:pathData="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_close.xml": r"""<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF" android:pathData="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_expand.xml": r"""<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF" android:pathData="M15,3L21,3L21,9L19,9L19,6.41L13.41,12L12,10.59L17.59,5L15,5L15,3ZM9,21L3,21L3,15L5,15L5,17.59L10.59,12L12,13.41L6.41,19L9,19L9,21Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_attach.xml": r"""<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF" android:pathData="M16.5,6V17.5C16.5,19.71 14.71,21.5 12.5,21.5C10.29,21.5 8.5,19.71 8.5,17.5V5C8.5,3.62 9.62,2.5 11,2.5C12.38,2.5 13.5,3.62 13.5,5V15.5C13.5,16.05 13.05,16.5 12.5,16.5C11.95,16.5 11.5,16.05 11.5,15.5V6H10V15.5C10,16.88 11.12,18 12.5,18C13.88,18 15,16.88 15,15.5V5C15,2.79 13.21,1 11,1C8.79,1 7,2.79 7,5V17.5C7,20.54 9.46,23 12.5,23C15.54,23 18,20.54 18,17.5V6H16.5Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_compare.xml": r"""<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF" android:pathData="M10,3H5C3.9,3 3,3.9 3,5V19C3,20.1 3.9,21 5,21H10V23H12V1H10V3ZM10,18H5L10,12V18ZM19,3H14V5H19V18L14,12V21H19C20.1,21 21,20.1 21,19V5C21,3.9 20.1,3 19,3Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_resize_handle.xml": r"""<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF" android:pathData="M22,22H20V20H22V22ZM22,18H20V16H22V18ZM18,22H16V20H18V22ZM18,18H16V16H18V18ZM14,22H12V20H14V22ZM22,14H20V12H22V14Z" />
</vector>
""",

    # --------------------------------------------------------------------------
    # 18. ACTIVITIES & SERVICES (MAIN, WELCOME, OVERLAY, TILE, TRIGGERS)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/MainActivity.kt": r"""package com.example.floatinggeminiai

import android.Manifest
import android.app.StatusBarManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.drawable.Icon
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.SeekBar
import android.widget.Spinner
import android.widget.Switch
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.example.floatinggeminiai.ai.AiEngine
import com.example.floatinggeminiai.ai.AiProvider
import com.example.floatinggeminiai.data.ChatRepository
import com.example.floatinggeminiai.security.SecureVault
import com.example.floatinggeminiai.ui.LiquidGlassBottomNavBar
import com.example.floatinggeminiai.ui.LiquidGlassFrameLayout
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var vault: SecureVault
    private lateinit var repo: ChatRepository
    private lateinit var aiEngine: AiEngine
    private var selectedProvider = AiProvider.GEMINI

    override fun onCreate(savedInstanceState: Bundle?) {
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        applySavedThemeMode(prefs.getInt("theme_mode", 0))
        super.onCreate(savedInstanceState)

        if (!prefs.getBoolean("welcome_completed", false)) {
            startActivity(Intent(this, WelcomeActivity::class.java))
        }

        setContentView(R.layout.activity_main)

        vault = SecureVault(this)
        repo = ChatRepository(this)
        aiEngine = AiEngine(vault)

        initLiquidGlassSurfaces()
        initFloatingBottomNavbar()
        setupHomeControls(prefs)
        setupAiProviderVault(prefs)
        setupOverlayAndGlassStudio(prefs)
        setupToolsAndData()
        requestRuntimePermissionsIfNeeded()
    }

    override fun onResume() {
        super.onResume()
        refreshDashboardStatus()
    }

    private fun applySavedThemeMode(modeIndex: Int) {
        when (modeIndex) {
            1 -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES)
            2 -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)
            else -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM)
        }
    }

    private fun initLiquidGlassSurfaces() {
        val heroCard = findViewById<LiquidGlassFrameLayout>(R.id.glassCardHero)
        val statsCard = findViewById<LiquidGlassFrameLayout>(R.id.glassCardStats)
        val providerCard = findViewById<LiquidGlassFrameLayout>(R.id.glassCardProvider)
        val overlayCard = findViewById<LiquidGlassFrameLayout>(R.id.glassCardOverlay)
        val toolsCard = findViewById<LiquidGlassFrameLayout>(R.id.glassCardTools)
        val headerBadge = findViewById<LiquidGlassFrameLayout>(R.id.glassHeaderBadge)

        headerBadge.cornerRadiusDp = 16f
        headerBadge.bevelWidthDp = 8f
        headerBadge.dispersionStrength = 0.42f
        headerBadge.startAmbientRefraction()

        listOf(heroCard, statsCard, providerCard, overlayCard, toolsCard).forEach { card ->
            card.cornerRadiusDp = 26f
            card.bevelWidthDp = 15f
            card.dispersionStrength = 0.28f
            card.specularIntensity = 0.65f
            card.startAmbientRefraction()
        }
    }

    private fun initFloatingBottomNavbar() {
        val navBar = findViewById<LiquidGlassBottomNavBar>(R.id.liquidBottomNavBar)
        val pageHome = findViewById<LinearLayout>(R.id.pageHome)
        val pageAi = findViewById<LinearLayout>(R.id.pageAiProviders)
        val pageOverlay = findViewById<LinearLayout>(R.id.pageOverlayGlass)
        val pageTools = findViewById<LinearLayout>(R.id.pageToolsData)
        val pages = listOf(pageHome, pageAi, pageOverlay, pageTools)

        navBar.setTabs(
            listOf(
                LiquidGlassBottomNavBar.NavTab("Beranda", R.drawable.ic_home),
                LiquidGlassBottomNavBar.NavTab("AI & Keys", R.drawable.ic_key),
                LiquidGlassBottomNavBar.NavTab("Liquid UI", R.drawable.ic_layers),
                LiquidGlassBottomNavBar.NavTab("Tools", R.drawable.ic_tools)
            )
        )

        navBar.onTabSelected = { index ->
            pages.forEachIndexed { idx, view ->
                if (idx == index) {
                    view.alpha = 0f
                    view.visibility = View.VISIBLE
                    view.animate().alpha(1f).setDuration(220L).start()
                } else {
                    view.visibility = View.GONE
                }
            }
        }
    }

    private fun setupHomeControls(prefs: android.content.SharedPreferences) {
        findViewById<Button>(R.id.btnOpenWelcome).setOnClickListener {
            startActivity(Intent(this, WelcomeActivity::class.java))
        }

        findViewById<Button>(R.id.btnGrantOverlay).setOnClickListener {
            val intent = Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:$packageName")
            )
            startActivity(intent)
        }

        findViewById<Button>(R.id.btnStartService).setOnClickListener {
            if (!Settings.canDrawOverlays(this)) {
                Toast.makeText(this, "Aktifkan izin Overlay terlebih dahulu!", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val intent = Intent(this, FloatingAssistantService::class.java).apply {
                action = FloatingAssistantService.ACTION_START_OR_UPDATE
            }
            ContextCompat.startForegroundService(this, intent)
            Toast.makeText(this, "Floamini Liquid Overlay aktif!", Toast.LENGTH_SHORT).show()
        }

        findViewById<Button>(R.id.btnSummonSiriNow).setOnClickListener {
            if (!Settings.canDrawOverlays(this)) {
                Toast.makeText(this, "Aktifkan izin Overlay terlebih dahulu!", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val intent = Intent(this, FloatingAssistantService::class.java).apply {
                action = FloatingAssistantService.ACTION_SUMMON_SIRI
            }
            ContextCompat.startForegroundService(this, intent)
        }

        findViewById<Button>(R.id.btnForceStopService).setOnClickListener {
            stopService(Intent(this, FloatingAssistantService::class.java))
            Toast.makeText(this, "Floamini dihentikan sepenuhnya.", Toast.LENGTH_SHORT).show()
        }
    }

    private fun setupAiProviderVault(prefs: android.content.SharedPreferences) {
        val spinnerProvider = findViewById<Spinner>(R.id.spinnerProvider)
        val spinnerModel = findViewById<Spinner>(R.id.spinnerModel)
        val spinnerPersonality = findViewById<Spinner>(R.id.spinnerPersonality)
        val tvKeyStatus = findViewById<TextView>(R.id.tvProviderKeyStatus)
        val etApiKey = findViewById<EditText>(R.id.etProviderApiKey)
        val layoutCustom = findViewById<LinearLayout>(R.id.layoutCustomEndpoint)
        val etCustomUrl = findViewById<EditText>(R.id.etCustomBaseUrl)
        val etCustomModel = findViewById<EditText>(R.id.etCustomModelId)
        val tvTestResult = findViewById<TextView>(R.id.tvTestConnectionResult)
        val etPersona = findViewById<EditText>(R.id.etCustomPersona)

        selectedProvider = AiProvider.fromId(prefs.getString("active_provider", AiProvider.GEMINI.id))
        val providerNames = AiProvider.entries.map { it.displayName }
        spinnerProvider.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, providerNames)
        spinnerProvider.setSelection(AiProvider.entries.indexOf(selectedProvider))

        etCustomUrl.setText(vault.getCustomBaseUrl())
        etCustomModel.setText(vault.getCustomModelId())
        etPersona.setText(prefs.getString("custom_system_prompt", ""))

        fun bindModelSpinner(provider: AiProvider) {
            val models = if (provider == AiProvider.CUSTOM) {
                listOf(vault.getCustomModelId().ifEmpty { "custom-model" })
            } else {
                provider.models
            }
            spinnerModel.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, models)
            val savedModel = prefs.getString("active_model", "")
            val idx = models.indexOf(savedModel)
            if (idx >= 0) spinnerModel.setSelection(idx)
            tvKeyStatus.text = "Status Vault (${provider.displayName}): ${vault.getMaskedKey(provider.id)}"
            layoutCustom.visibility = if (provider == AiProvider.CUSTOM) View.VISIBLE else View.GONE
        }

        bindModelSpinner(selectedProvider)

        spinnerProvider.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                selectedProvider = AiProvider.entries[position]
                prefs.edit().putString("active_provider", selectedProvider.id).apply()
                etApiKey.setText("")
                tvTestResult.visibility = View.GONE
                bindModelSpinner(selectedProvider)
                refreshDashboardStatus()
                notifyServiceConfigChanged()
            }

            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }

        spinnerModel.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                val chosen = spinnerModel.selectedItem?.toString() ?: return
                prefs.edit().putString("active_model", chosen).apply()
                refreshDashboardStatus()
                notifyServiceConfigChanged()
            }

            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }

        val personalities = listOf(
            "Asik & Santai (Natural)",
            "Singkat & Padat (To The Point)",
            "Detail & Terstruktur",
            "Kreatif & Ekspresif",
            "Coding & Teknis Pro"
        )
        spinnerPersonality.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, personalities)
        spinnerPersonality.setSelection(prefs.getInt("personality_index", 0))
        spinnerPersonality.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                prefs.edit().putInt("personality_index", position).apply()
                notifyServiceConfigChanged()
            }

            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }

        findViewById<Button>(R.id.btnSaveProviderKey).setOnClickListener {
            val newKey = etApiKey.text.toString().trim()
            if (newKey.isNotEmpty()) {
                vault.saveApiKey(selectedProvider.id, newKey)
                etApiKey.setText("")
            }
            if (selectedProvider == AiProvider.CUSTOM) {
                vault.saveCustomEndpoint(etCustomUrl.text.toString(), etCustomModel.text.toString())
                bindModelSpinner(selectedProvider)
            }
            prefs.edit().putString("custom_system_prompt", etPersona.text.toString().trim()).apply()
            tvKeyStatus.text = "Status Vault (${selectedProvider.displayName}): ${vault.getMaskedKey(selectedProvider.id)}"
            Toast.makeText(this, "Tersimpan aman di Encrypted Vault!", Toast.LENGTH_SHORT).show()
            notifyServiceConfigChanged()
        }

        findViewById<Button>(R.id.btnTestProviderConnection).setOnClickListener {
            val activeModel = spinnerModel.selectedItem?.toString() ?: selectedProvider.models.first()
            tvTestResult.visibility = View.VISIBLE
            tvTestResult.text = "Menguji koneksi ke ${selectedProvider.displayName}..."
            lifecycleScope.launch {
                val res = aiEngine.testConnection(selectedProvider, activeModel)
                res.onSuccess { msg ->
                    tvTestResult.text = msg
                }.onFailure { err ->
                    tvTestResult.text = "Gagal: ${err.message}"
                }
            }
        }
    }

    private fun setupOverlayAndGlassStudio(prefs: android.content.SharedPreferences) {
        val spinnerStyle = findViewById<Spinner>(R.id.spinnerOverlayStyle)
        val spinnerPill = findViewById<Spinner>(R.id.spinnerPillAppearance)
        val switchAutoHide = findViewById<Switch>(R.id.switchAutoHidePill)
        val switchSmartFreeze = findViewById<Switch>(R.id.switchSmartFreeze)
        val switchBlur = findViewById<Switch>(R.id.switchLiquidBlur)
        val seekWidth = findViewById<SeekBar>(R.id.seekIslandWidth)
        val seekY = findViewById<SeekBar>(R.id.seekIslandY)
        val seekX = findViewById<SeekBar>(R.id.seekIslandX)
        val seekOpacity = findViewById<SeekBar>(R.id.seekPopupOpacity)
        val spinnerTheme = findViewById<Spinner>(R.id.spinnerThemeMode)

        val styles = listOf("Dynamic Island (Atas)", "Mode Siri (Control Center)", "Xiaomi Edge Pill", "Classic Bubble")
        val styleKeys = listOf("dynamic_island", "siri_mode", "xiaomi_edge", "classic_bubble")
        spinnerStyle.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, styles)
        val curStyle = prefs.getString("overlay_style", "dynamic_island")
        spinnerStyle.setSelection(styleKeys.indexOf(curStyle).coerceAtLeast(0))
        spinnerStyle.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(p: AdapterView<*>?, v: View?, pos: Int, id: Long) {
                prefs.edit().putString("overlay_style", styleKeys[pos]).apply()
                notifyServiceConfigChanged()
            }
            override fun onNothingSelected(p: AdapterView<*>?) {}
        }

        val pillModes = listOf("Lengkap (Ikon + Nama + Pulse)", "Polos (Kamera Punch-Hole)", "Ikon Saja")
        val pillKeys = listOf("lengkap", "polos", "minimal")
        spinnerPill.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, pillModes)
        val curPill = prefs.getString("pill_appearance", "lengkap")
        spinnerPill.setSelection(pillKeys.indexOf(curPill).coerceAtLeast(0))
        spinnerPill.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(p: AdapterView<*>?, v: View?, pos: Int, id: Long) {
                prefs.edit().putString("pill_appearance", pillKeys[pos]).apply()
                notifyServiceConfigChanged()
            }
            override fun onNothingSelected(p: AdapterView<*>?) {}
        }

        switchAutoHide.isChecked = prefs.getBoolean("auto_hide_pill", false)
        switchAutoHide.setOnCheckedChangeListener { _, checked ->
            prefs.edit().putBoolean("auto_hide_pill", checked).apply()
            notifyServiceConfigChanged()
        }

        switchSmartFreeze.isChecked = prefs.getBoolean("smart_freeze", true)
        switchSmartFreeze.setOnCheckedChangeListener { _, checked ->
            prefs.edit().putBoolean("smart_freeze", checked).apply()
            notifyServiceConfigChanged()
        }

        switchBlur.isChecked = prefs.getBoolean("liquid_blur", true)
        switchBlur.setOnCheckedChangeListener { _, checked ->
            prefs.edit().putBoolean("liquid_blur", checked).apply()
            notifyServiceConfigChanged()
        }

        val tvW = findViewById<TextView>(R.id.tvIslandWidthLabel)
        val savedW = prefs.getInt("island_width_dp", 164)
        seekWidth.progress = (savedW - 100).coerceIn(0, 180)
        tvW.text = "Lebar Pil Dynamic Island: ${savedW}dp"
        seekWidth.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(sb: SeekBar?, prog: Int, fromUser: Boolean) {
                val w = 100 + prog
                tvW.text = "Lebar Pil Dynamic Island: ${w}dp"
                prefs.edit().putInt("island_width_dp", w).apply()
                if (fromUser) notifyServiceConfigChanged()
            }
            override fun onStartTrackingTouch(sb: SeekBar?) {}
            override fun onStopTrackingTouch(sb: SeekBar?) {}
        })

        val tvY = findViewById<TextView>(R.id.tvIslandYLabel)
        val savedY = prefs.getInt("island_pos_y_dp", 12)
        seekY.progress = savedY.coerceIn(0, 120)
        tvY.text = "Posisi Vertikal Atas (Y): ${savedY}dp"
        seekY.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(sb: SeekBar?, prog: Int, fromUser: Boolean) {
                tvY.text = "Posisi Vertikal Atas (Y): ${prog}dp"
                prefs.edit().putInt("island_pos_y_dp", prog).apply()
                if (fromUser) notifyServiceConfigChanged()
            }
            override fun onStartTrackingTouch(sb: SeekBar?) {}
            override fun onStopTrackingTouch(sb: SeekBar?) {}
        })

        val tvX = findViewById<TextView>(R.id.tvIslandXLabel)
        val savedX = prefs.getInt("island_offset_x_dp", 0)
        seekX.progress = (savedX + 120).coerceIn(0, 240)
        tvX.text = "Geser Horizontal Kamera (X): ${savedX}dp"
        seekX.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(sb: SeekBar?, prog: Int, fromUser: Boolean) {
                val offset = prog - 120
                tvX.text = "Geser Horizontal Kamera (X): ${offset}dp"
                prefs.edit().putInt("island_offset_x_dp", offset).apply()
                if (fromUser) notifyServiceConfigChanged()
            }
            override fun onStartTrackingTouch(sb: SeekBar?) {}
            override fun onStopTrackingTouch(sb: SeekBar?) {}
        })

        val tvOp = findViewById<TextView>(R.id.tvOpacityLabel)
        val savedOp = prefs.getInt("popup_opacity_pct", 92)
        seekOpacity.progress = (savedOp - 55).coerceIn(0, 45)
        tvOp.text = "Transparansi Jendela Glass: $savedOp%"
        seekOpacity.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(sb: SeekBar?, prog: Int, fromUser: Boolean) {
                val pct = 55 + prog
                tvOp.text = "Transparansi Jendela Glass: $pct%"
                prefs.edit().putInt("popup_opacity_pct", pct).apply()
                if (fromUser) notifyServiceConfigChanged()
            }
            override fun onStartTrackingTouch(sb: SeekBar?) {}
            override fun onStopTrackingTouch(sb: SeekBar?) {}
        })

        val themes = listOf("Ikuti Sistem (Adaptif)", "Dark Liquid Glass", "Light Liquid Glass")
        spinnerTheme.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, themes)
        spinnerTheme.setSelection(prefs.getInt("theme_mode", 0))
        spinnerTheme.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(p: AdapterView<*>?, v: View?, pos: Int, id: Long) {
                if (prefs.getInt("theme_mode", 0) != pos) {
                    prefs.edit().putInt("theme_mode", pos).apply()
                    applySavedThemeMode(pos)
                }
            }
            override fun onNothingSelected(p: AdapterView<*>?) {}
        }

        findViewById<Button>(R.id.btnAddControlCenterTile).setOnClickListener {
            requestAddControlCenterTile()
        }
    }

    private fun setupToolsAndData() {
        val etNotes = findViewById<EditText>(R.id.etMainQuickNotes)
        etNotes.setText(repo.getQuickNotes())

        findViewById<Button>(R.id.btnSaveQuickNotes).setOnClickListener {
            repo.saveQuickNotes(etNotes.text.toString())
            Toast.makeText(this, "Catatan cepat tersimpan!", Toast.LENGTH_SHORT).show()
        }

        findViewById<Button>(R.id.btnClearAllHistory).setOnClickListener {
            AlertDialog.Builder(this)
                .setTitle("Hapus Semua Riwayat?")
                .setMessage("Seluruh sesi percakapan Floamini akan dihapus permanen.")
                .setPositiveButton("Hapus") { _, _ ->
                    repo.clearAllHistory()
                    repo.resetUsage()
                    refreshDashboardStatus()
                    Toast.makeText(this, "Riwayat dibersihkan.", Toast.LENGTH_SHORT).show()
                }
                .setNegativeButton("Batal", null)
                .show()
        }
    }

    private fun refreshDashboardStatus() {
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        val prov = AiProvider.fromId(prefs.getString("active_provider", AiProvider.GEMINI.id))
        val model = prefs.getString("active_model", prov.models.first()).orEmpty()
        findViewById<TextView>(R.id.tvActiveEngineSummary).text = "Engine: ${prov.displayName} ($model)"
        findViewById<TextView>(R.id.tvPermissionBadge).text =
            if (Settings.canDrawOverlays(this)) "Overlay: Aktif" else "Overlay: Perlu Izin"
        findViewById<TextView>(R.id.tvUsageStats).text = repo.getUsageSummary()
    }

    private fun notifyServiceConfigChanged() {
        if (Settings.canDrawOverlays(this)) {
            val intent = Intent(this, FloatingAssistantService::class.java).apply {
                action = FloatingAssistantService.ACTION_RELOAD_CONFIG
            }
            try {
                startService(intent)
            } catch (_: Exception) {
            }
        }
    }

    private fun requestAddControlCenterTile() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            val sbm = getSystemService(StatusBarManager::class.java)
            sbm?.requestAddTileService(
                ComponentName(this, FloaminiTileService::class.java),
                "Floamini AI",
                Icon.createWithResource(this, R.drawable.ic_sparkle),
                mainExecutor
            ) { _ ->
                Toast.makeText(this, "Permintaan tile Control Center diproses.", Toast.LENGTH_SHORT).show()
            }
        } else {
            AlertDialog.Builder(this)
                .setTitle("Shortcut Control Center")
                .setMessage("Tarik panel Quick Settings dari atas layar > ketuk ikon Edit (Pensil) > seret ubin 'Floamini AI' ke area aktif.")
                .setPositiveButton("Mengerti", null)
                .show()
        }
    }

    private fun requestRuntimePermissionsIfNeeded() {
        val perms = mutableListOf(Manifest.permission.RECORD_AUDIO)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            perms.add(Manifest.permission.POST_NOTIFICATIONS)
        }
        val missing = perms.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (missing.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, missing.toTypedArray(), 101)
        }
    }
}
""",

    "app/src/main/java/com/example/floatinggeminiai/WelcomeActivity.kt": r"""package com.example.floatinggeminiai

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.floatinggeminiai.ai.AiEngine
import com.example.floatinggeminiai.ai.AiProvider
import com.example.floatinggeminiai.security.SecureVault
import com.example.floatinggeminiai.ui.LiquidGlassFrameLayout
import kotlinx.coroutines.launch

class WelcomeActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_welcome)

        val vault = SecureVault(this)
        val engine = AiEngine(vault)
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)

        findViewById<LiquidGlassFrameLayout>(R.id.glassWelcomeHero).apply {
            cornerRadiusDp = 28f
            dispersionStrength = 0.35f
            startAmbientRefraction()
        }
        findViewById<LiquidGlassFrameLayout>(R.id.glassWelcomeGuide).apply {
            cornerRadiusDp = 26f
            dispersionStrength = 0.28f
            startAmbientRefraction()
        }

        findViewById<Button>(R.id.btnOpenAiStudio).setOnClickListener {
            startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://aistudio.google.com/app/apikey")))
        }

        val etKey = findViewById<EditText>(R.id.etWelcomeGeminiKey)
        val tvStatus = findViewById<TextView>(R.id.tvWelcomeTestStatus)

        findViewById<Button>(R.id.btnWelcomeSaveAndTest).setOnClickListener {
            val raw = etKey.text.toString().trim()
            if (raw.isEmpty()) {
                Toast.makeText(this, "Tempel Gemini API Key terlebih dahulu.", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            vault.saveApiKey(AiProvider.GEMINI.id, raw)
            prefs.edit().putString("active_provider", AiProvider.GEMINI.id).apply()
            tvStatus.visibility = View.VISIBLE
            tvStatus.text = "Menguji token Gemini..."
            lifecycleScope.launch {
                val res = engine.testConnection(AiProvider.GEMINI, AiProvider.GEMINI.models.first())
                res.onSuccess { msg ->
                    tvStatus.text = msg
                }.onFailure { err ->
                    tvStatus.text = "Gagal: ${err.message}"
                }
            }
        }

        findViewById<Button>(R.id.btnWelcomeFinish).setOnClickListener {
            prefs.edit().putBoolean("welcome_completed", true).apply()
            finish()
        }
    }
}
""",

    "app/src/main/java/com/example/floatinggeminiai/FloaminiTileService.kt": r"""package com.example.floatinggeminiai

import android.content.Intent
import android.os.Build
import android.provider.Settings
import android.service.quicksettings.Tile
import android.service.quicksettings.TileService
import androidx.core.content.ContextCompat

class FloaminiTileService : TileService() {

    override fun onStartListening() {
        super.onStartListening()
        qsTile?.apply {
            state = Tile.STATE_ACTIVE
            label = "Floamini AI"
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                subtitle = "Siri & Overlay"
            }
            updateTile()
        }
    }

    override fun onClick() {
        super.onClick()
        if (!Settings.canDrawOverlays(this)) {
            val openApp = Intent(this, MainActivity::class.java).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            startActivityAndCollapse(openApp)
            return
        }

        val summonIntent = Intent(this, FloatingAssistantService::class.java).apply {
            action = FloatingAssistantService.ACTION_SUMMON_SIRI
        }
        ContextCompat.startForegroundService(this, summonIntent)
    }
}
""",

    "app/src/main/java/com/example/floatinggeminiai/ScreenCapturePermissionActivity.kt": r"""package com.example.floatinggeminiai

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.media.projection.MediaProjectionManager
import android.os.Bundle
import androidx.core.content.ContextCompat

class ScreenCapturePermissionActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val mgr = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        startActivityForResult(mgr.createScreenCaptureIntent(), 9001)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == 9001 && resultCode == RESULT_OK && data != null) {
            val serviceIntent = Intent(this, FloatingAssistantService::class.java).apply {
                action = FloatingAssistantService.ACTION_MEDIA_PROJECTION_READY
                putExtra("resultCode", resultCode)
                putExtra("data", data)
            }
            ContextCompat.startForegroundService(this, serviceIntent)
        }
        finish()
    }
}
""",

    "app/src/main/java/com/example/floatinggeminiai/FilePickerProxyActivity.kt": r"""package com.example.floatinggeminiai

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import androidx.core.content.ContextCompat

class FilePickerProxyActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val picker = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "*/*"
            putExtra(
                Intent.EXTRA_MIME_TYPES,
                arrayOf("application/pdf", "image/*", "text/*")
            )
        }
        startActivityForResult(picker, 9002)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        val uri = data?.data
        if (requestCode == 9002 && resultCode == RESULT_OK && uri != null) {
            val svc = Intent(this, FloatingAssistantService::class.java).apply {
                action = FloatingAssistantService.ACTION_FILE_PICKED
                putExtra("file_uri", uri.toString())
            }
            ContextCompat.startForegroundService(this, svc)
        }
        finish()
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
import androidx.core.content.ContextCompat

class ExternalTriggerActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (!Settings.canDrawOverlays(this)) {
            Toast.makeText(this, "Aktifkan izin Overlay Floamini terlebih dahulu.", Toast.LENGTH_SHORT).show()
            startActivity(Intent(this, MainActivity::class.java))
            finish()
            return
        }

        val selectedText = intent.getCharSequenceExtra(Intent.EXTRA_PROCESS_TEXT)?.toString()
            ?: intent.getStringExtra(Intent.EXTRA_TEXT)
        val sharedImageUri: Uri? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            intent.getParcelableExtra(Intent.EXTRA_STREAM, Uri::class.java)
        } else {
            @Suppress("DEPRECATION")
            intent.getParcelableExtra(Intent.EXTRA_STREAM)
        }

        val svc = Intent(this, FloatingAssistantService::class.java).apply {
            action = FloatingAssistantService.ACTION_EXTERNAL_QUERY
            if (!selectedText.isNullOrBlank()) putExtra("external_text", selectedText)
            if (sharedImageUri != null) putExtra("file_uri", sharedImageUri.toString())
        }
        ContextCompat.startForegroundService(this, svc)
        finish()
    }
}
""",

    "app/src/main/java/com/example/floatinggeminiai/FloatingAssistantService.kt": r"""package com.example.floatinggeminiai

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
import android.text.Editable
import android.text.TextWatcher
import android.view.Gravity
import android.view.HapticFeedbackConstants
import android.view.LayoutInflater
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
import android.view.inputmethod.EditorInfo
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.core.app.NotificationCompat
import androidx.dynamicanimation.animation.DynamicAnimation
import androidx.dynamicanimation.animation.SpringAnimation
import androidx.dynamicanimation.animation.SpringForce
import com.example.floatinggeminiai.ai.AiEngine
import com.example.floatinggeminiai.ai.AiProvider
import com.example.floatinggeminiai.ai.ChatMessage
import com.example.floatinggeminiai.ai.ChatThread
import com.example.floatinggeminiai.data.ChatRepository
import com.example.floatinggeminiai.security.SecureVault
import com.example.floatinggeminiai.tools.ProcessedAttachment
import com.example.floatinggeminiai.tools.SmartToolsHelper
import com.example.floatinggeminiai.ui.LiquidGlassFrameLayout
import com.example.floatinggeminiai.ui.SiriEdgeGlowView
import com.example.floatinggeminiai.ui.VoiceWaveformView
import com.example.floatinggeminiai.voice.VoiceSystemManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlin.math.abs

class FloatingAssistantService : Service() {

    companion object {
        const val ACTION_START_OR_UPDATE = "com.example.floatinggeminiai.START_OR_UPDATE"
        const val ACTION_RELOAD_CONFIG = "com.example.floatinggeminiai.RELOAD_CONFIG"
        const val ACTION_SUMMON_SIRI = "com.example.floatinggeminiai.SUMMON_SIRI"
        const val ACTION_MEDIA_PROJECTION_READY = "com.example.floatinggeminiai.MEDIA_PROJECTION_READY"
        const val ACTION_FILE_PICKED = "com.example.floatinggeminiai.FILE_PICKED"
        const val ACTION_EXTERNAL_QUERY = "com.example.floatinggeminiai.EXTERNAL_QUERY"
        private const val CHANNEL_ID = "floamini_overlay_channel"
        private const val NOTIF_ID = 4077
    }

    private lateinit var windowManager: WindowManager
    private lateinit var floatingView: View
    private lateinit var params: WindowManager.LayoutParams

    private lateinit var vault: SecureVault
    private lateinit var repo: ChatRepository
    private lateinit var aiEngine: AiEngine
    private lateinit var voiceManager: VoiceSystemManager
    private lateinit var currentThread: ChatThread

    private val serviceScope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private val mainHandler = Handler(Looper.getMainLooper())
    private var activeGenerationJob: Job? = null

    private lateinit var dynamicIslandGlassHost: LiquidGlassFrameLayout
    private lateinit var dynamicIslandView: LinearLayout
    private lateinit var ivIslandSparkle: ImageView
    private lateinit var tvIslandLabel: TextView
    private lateinit var viewIslandPulseDot: View
    private lateinit var bubbleView: FrameLayout
    private lateinit var xiaomiEdgeView: FrameLayout
    private lateinit var popupChatView: LiquidGlassFrameLayout

    private lateinit var tvActiveProviderHeader: TextView
    private lateinit var btnScreenShare: ImageView
    private lateinit var tvScreenShareStatus: TextView
    private lateinit var tvAttachmentBadge: TextView
    private lateinit var chatScrollView: ScrollView
    private lateinit var chatMessagesContainer: LinearLayout
    private lateinit var etPromptInput: EditText
    private lateinit var btnSendOrStop: ImageView
    private lateinit var voiceWaveformBar: LinearLayout
    private lateinit var voiceWaveformView: VoiceWaveformView
    private lateinit var tvVoiceHint: TextView

    private var siriGlowView: SiriEdgeGlowView? = null
    private var isSiriAuraAttached = false
    private var isFloatingViewAttached = false
    private var isSmartFrozen = false
    private var isPillAutoHidden = false
    private var isMiniWindowMode = false
    private var isCompareMode = false
    private var isAutoRouterEnabled = false
    private var snappedToRightEdge = true

    private var activeProvider = AiProvider.GEMINI
    private var activeModel = "gemini-2.5-flash"
    private var pendingAttachment: ProcessedAttachment? = null

    private var prefOverlayStyle = "dynamic_island"
    private var prefPillAppearance = "lengkap"
    private var prefAutoHidePill = false
    private var prefSmartFreeze = true
    private var prefLiquidBlur = true
    private var prefIslandWidthPx = 420
    private var prefIslandPosYPx = 30
    private var prefIslandOffsetXPx = 0
    private var prefPopupAlpha = 0.92f
    private var prefBubbleSizePx = 140

    private var fullScreenWidth = 1080
    private var fullScreenHeight = 2400

    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    private var isScreenShareActive = false

    private val screenOffReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (intent?.action == Intent.ACTION_SCREEN_OFF && prefSmartFreeze) {
                enterSmartFreezeState()
            }
        }
    }

    private val autoHidePillRunnable = Runnable {
        if (prefOverlayStyle == "dynamic_island" &&
            prefAutoHidePill &&
            dynamicIslandGlassHost.visibility == View.VISIBLE &&
            popupChatView.visibility != View.VISIBLE
        ) {
            isPillAutoHidden = true
            dynamicIslandGlassHost.animate()
                .alpha(0.03f)
                .scaleX(0.45f)
                .scaleY(0.45f)
                .setDuration(380L)
                .start()
        }
    }

    private val transformToXiaomiEdgeRunnable = Runnable {
        if (prefOverlayStyle == "xiaomi_edge" && popupChatView.visibility != View.VISIBLE) {
            bubbleView.visibility = View.GONE
            xiaomiEdgeView.visibility = View.VISIBLE
            params.x = if (snappedToRightEdge) (fullScreenWidth - xiaomiEdgeView.layoutParams.width) else 0
            if (isFloatingViewAttached) windowManager.updateViewLayout(floatingView, params)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
        val dm = resources.displayMetrics
        fullScreenWidth = dm.widthPixels
        fullScreenHeight = dm.heightPixels
        prefBubbleSizePx = (54 * dm.density).toInt()

        vault = SecureVault(this)
        repo = ChatRepository(this)
        aiEngine = AiEngine(vault)
        currentThread = repo.getOrCreateActiveThread()

        startForegroundNotification(withMediaProjection = false)
        registerReceiver(screenOffReceiver, IntentFilter(Intent.ACTION_SCREEN_OFF))

        loadPreferences()
        initFloatingOverlay()

        voiceManager = VoiceSystemManager(
            context = this,
            onAmplitudeChanged = { amp ->
                if (::voiceWaveformView.isInitialized) voiceWaveformView.setAmplitude(amp)
            },
            onSpeechResult = { spoken ->
                if (::etPromptInput.isInitialized) {
                    etPromptInput.setText(spoken)
                    sendUserPrompt(spoken)
                }
            },
            onSpeechStateChanged = { listening, hint ->
                if (::voiceWaveformBar.isInitialized) {
                    voiceWaveformBar.visibility = if (listening || hint.isNotEmpty()) View.VISIBLE else View.GONE
                    tvVoiceHint.text = hint
                }
            }
        )

        showCollapsedTriggerState()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        loadPreferences()
        applyVisualPreferences()

        when (intent?.action) {
            ACTION_SUMMON_SIRI -> {
                triggerSiriSummon()
            }
            ACTION_MEDIA_PROJECTION_READY -> {
                val code = intent.getIntExtra("resultCode", Activity.RESULT_CANCELED)
                val data: Intent? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                    intent.getParcelableExtra("data", Intent::class.java)
                } else {
                    @Suppress("DEPRECATION")
                    intent.getParcelableExtra("data")
                }
                if (code == Activity.RESULT_OK && data != null) {
                    startMediaProjectionCapture(code, data)
                }
            }
            ACTION_FILE_PICKED -> {
                val uriStr = intent.getStringExtra("file_uri")
                if (!uriStr.isNullOrEmpty()) {
                    handlePickedUri(Uri.parse(uriStr))
                }
            }
            ACTION_EXTERNAL_QUERY -> {
                openPopupChat(fromSiri = false)
                val extText = intent.getStringExtra("external_text")
                val uriStr = intent.getStringExtra("file_uri")
                if (!uriStr.isNullOrEmpty()) {
                    handlePickedUri(Uri.parse(uriStr))
                }
                if (!extText.isNullOrBlank()) {
                    etPromptInput.setText("Bantu jelaskan/proses teks ini:\n$extText")
                }
            }
            ACTION_RELOAD_CONFIG -> {
                if (popupChatView.visibility != View.VISIBLE) {
                    showCollapsedTriggerState()
                }
            }
            else -> {
                if (popupChatView.visibility != View.VISIBLE) {
                    showCollapsedTriggerState()
                }
            }
        }
        return START_STICKY
    }

    private fun startForegroundNotification(withMediaProjection: Boolean) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Floamini Liquid Glass Overlay",
                NotificationManager.IMPORTANCE_LOW
            )
            val nm = getSystemService(NotificationManager::class.java)
            nm.createNotificationChannel(channel)
        }

        val notif: Notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Floamini OS Aktif")
            .setContentText("Ketuk Dynamic Island / Control Center untuk memanggil AI")
            .setSmallIcon(R.drawable.ic_sparkle)
            .setOngoing(true)
            .build()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            val fgsType = if (withMediaProjection) {
                ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE or ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION
            } else {
                ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE
            }
            startForeground(NOTIF_ID, notif, fgsType)
        } else {
            startForeground(NOTIF_ID, notif)
        }
    }

    private fun loadPreferences() {
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        val d = resources.displayMetrics.density

        activeProvider = AiProvider.fromId(prefs.getString("active_provider", AiProvider.GEMINI.id))
        activeModel = prefs.getString("active_model", activeProvider.models.first()).orEmpty()
            .ifEmpty { activeProvider.models.first() }

        prefOverlayStyle = prefs.getString("overlay_style", "dynamic_island").orEmpty()
        prefPillAppearance = prefs.getString("pill_appearance", "lengkap").orEmpty()
        prefAutoHidePill = prefs.getBoolean("auto_hide_pill", false)
        prefSmartFreeze = prefs.getBoolean("smart_freeze", true)
        prefLiquidBlur = prefs.getBoolean("liquid_blur", true)
        prefIslandWidthPx = (prefs.getInt("island_width_dp", 164) * d).toInt()
        prefIslandPosYPx = (prefs.getInt("island_pos_y_dp", 12) * d).toInt()
        prefIslandOffsetXPx = (prefs.getInt("island_offset_x_dp", 0) * d).toInt()
        prefPopupAlpha = (prefs.getInt("popup_opacity_pct", 92) / 100f).coerceIn(0.55f, 1.0f)
    }

    private fun initFloatingOverlay() {
        floatingView = LayoutInflater.from(this).inflate(R.layout.layout_floating_assistant, null)
        val overlayType = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        } else {
            @Suppress("DEPRECATION")
            WindowManager.LayoutParams.TYPE_PHONE
        }

        params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            overlayType,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = (fullScreenWidth - prefIslandWidthPx) / 2
            y = prefIslandPosYPx
        }

        windowManager.addView(floatingView, params)
        isFloatingViewAttached = true

        dynamicIslandGlassHost = floatingView.findViewById(R.id.dynamicIslandGlassHost)
        dynamicIslandView = floatingView.findViewById(R.id.dynamicIslandView)
        ivIslandSparkle = floatingView.findViewById(R.id.ivIslandSparkle)
        tvIslandLabel = floatingView.findViewById(R.id.tvIslandLabel)
        viewIslandPulseDot = floatingView.findViewById(R.id.viewIslandPulseDot)
        bubbleView = floatingView.findViewById(R.id.bubbleView)
        xiaomiEdgeView = floatingView.findViewById(R.id.xiaomiEdgeView)
        popupChatView = floatingView.findViewById(R.id.popupChatView)

        tvActiveProviderHeader = floatingView.findViewById(R.id.tvActiveProviderHeader)
        btnScreenShare = floatingView.findViewById(R.id.btnScreenShare)
        tvScreenShareStatus = floatingView.findViewById(R.id.tvScreenShareStatus)
        tvAttachmentBadge = floatingView.findViewById(R.id.tvAttachmentBadge)
        chatScrollView = floatingView.findViewById(R.id.chatScrollView)
        chatMessagesContainer = floatingView.findViewById(R.id.chatMessagesContainer)
        etPromptInput = floatingView.findViewById(R.id.etPromptInput)
        btnSendOrStop = floatingView.findViewById(R.id.btnSendOrStop)
        voiceWaveformBar = floatingView.findViewById(R.id.voiceWaveformBar)
        voiceWaveformView = floatingView.findViewById(R.id.voiceWaveformView)
        tvVoiceHint = floatingView.findViewById(R.id.tvVoiceHint)

        val glassTitleBar = floatingView.findViewById<LinearLayout>(R.id.glassTitleBar)
        val smartToolsDrawer = floatingView.findViewById<LinearLayout>(R.id.smartToolsDrawer)

        etPromptInput.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_SEND) {
                btnSendOrStop.performClick()
                true
            } else {
                false
            }
        }

        floatingView.setOnTouchListener { _, event ->
            if (event.action == MotionEvent.ACTION_OUTSIDE && popupChatView.visibility == View.VISIBLE) {
                showCollapsedTriggerState()
                true
            } else {
                false
            }
        }

        dynamicIslandGlassHost.setOnTouchListener(object : View.OnTouchListener {
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
                        animateSpringScale(dynamicIslandGlassHost, 1.07f)
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
                        animateSpringScale(dynamicIslandGlassHost, 1.0f)
                        if (abs(event.rawX - initialTouchX) < 18 && abs(event.rawY - initialTouchY) < 18) {
                            triggerHaptic()
                            isPillAutoHidden = false
                            dynamicIslandGlassHost.alpha = 1.0f
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
                        animateSpringScale(bubbleView, 1.1f)
                        return true
                    }
                    MotionEvent.ACTION_MOVE -> {
                        params.x = (initialX + (event.rawX - initialTouchX).toInt()).coerceIn(0, fullScreenWidth - prefBubbleSizePx)
                        params.y = (initialY + (event.rawY - initialTouchY).toInt()).coerceIn(40, fullScreenHeight - prefBubbleSizePx - 80)
                        windowManager.updateViewLayout(floatingView, params)
                        return true
                    }
                    MotionEvent.ACTION_UP -> {
                        animateSpringScale(bubbleView, 1.0f)
                        if (abs(event.rawX - initialTouchX) < 18 && abs(event.rawY - initialTouchY) < 18) {
                            triggerHaptic()
                            openPopupChat(fromSiri = false)
                        } else {
                            snappedToRightEdge = (params.x + prefBubbleSizePx / 2) > (fullScreenWidth / 2)
                            params.x = if (snappedToRightEdge) (fullScreenWidth - prefBubbleSizePx) else 0
                            windowManager.updateViewLayout(floatingView, params)
                            if (prefOverlayStyle == "xiaomi_edge") {
                                mainHandler.postDelayed(transformToXiaomiEdgeRunnable, 2500L)
                            }
                        }
                        return true
                    }
                }
                return false
            }
        })

        xiaomiEdgeView.setOnClickListener {
            triggerHaptic()
            openPopupChat(fromSiri = false)
        }

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
                        params.x = (initialX + (event.rawX - initialTouchX).toInt())
                            .coerceIn(0, (fullScreenWidth - popupChatView.width).coerceAtLeast(0))
                        params.y = (initialY + (event.rawY - initialTouchY).toInt())
                            .coerceIn(0, (fullScreenHeight - popupChatView.height).coerceAtLeast(0))
                        windowManager.updateViewLayout(floatingView, params)
                        return true
                    }
                    MotionEvent.ACTION_UP -> {
                        saveLastWindowGeometry()
                        return true
                    }
                }
                return false
            }
        })

        floatingView.findViewById<ImageView>(R.id.btnResizeHandle).setOnTouchListener(object : View.OnTouchListener {
            private var startW = 0
            private var startH = 0
            private var startTouchX = 0f
            private var startTouchY = 0f

            override fun onTouch(v: View, event: MotionEvent): Boolean {
                val d = resources.displayMetrics.density
                when (event.action) {
                    MotionEvent.ACTION_DOWN -> {
                        startW = popupChatView.layoutParams.width
                        startH = popupChatView.layoutParams.height
                        startTouchX = event.rawX
                        startTouchY = event.rawY
                        return true
                    }
                    MotionEvent.ACTION_MOVE -> {
                        val lp = popupChatView.layoutParams
                        lp.width = (startW + (event.rawX - startTouchX).toInt())
                            .coerceIn((260 * d).toInt(), (fullScreenWidth - 24).coerceAtLeast(300))
                        lp.height = (startH + (event.rawY - startTouchY).toInt())
                            .coerceIn((260 * d).toInt(), (fullScreenHeight - 100).coerceAtLeast(350))
                        popupChatView.layoutParams = lp
                        return true
                    }
                    MotionEvent.ACTION_UP -> {
                        saveLastWindowGeometry()
                        return true
                    }
                }
                return false
            }
        })

        floatingView.findViewById<ImageView>(R.id.btnClosePopup).setOnClickListener {
            triggerHaptic()
            showCollapsedTriggerState()
        }

        floatingView.findViewById<ImageView>(R.id.btnToggleMiniWindow).setOnClickListener {
            triggerHaptic()
            isMiniWindowMode = !isMiniWindowMode
            openPopupChat(fromSiri = false)
        }

        floatingView.findViewById<ImageView>(R.id.btnCompareMode).setOnClickListener { view ->
            triggerHaptic()
            isCompareMode = !isCompareMode
            (view as ImageView).setColorFilter(
                if (isCompareMode) Color.parseColor("#E879F9") else Color.parseColor("#94A3B8")
            )
            Toast.makeText(
                this,
                if (isCompareMode) "Mode Compare 2 AI Aktif" else "Mode Single AI",
                Toast.LENGTH_SHORT
            ).show()
        }

        btnScreenShare.setOnClickListener {
            triggerHaptic()
            if (isScreenShareActive) {
                stopMediaProjection()
            } else {
                val permIntent = Intent(this, ScreenCapturePermissionActivity::class.java).apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                }
                startActivity(permIntent)
            }
        }

        floatingView.findViewById<ImageView>(R.id.btnToggleSmartDrawer).setOnClickListener {
            triggerHaptic()
            val show = smartToolsDrawer.visibility != View.VISIBLE
            smartToolsDrawer.visibility = if (show) View.VISIBLE else View.GONE
            if (show) {
                refreshHistoryList(floatingView.findViewById(R.id.historyResultsContainer), "")
            }
        }

        floatingView.findViewById<TextView>(R.id.chipSwitchProvider).setOnClickListener {
            val all = AiProvider.entries
            val nextIdx = (all.indexOf(activeProvider) + 1) % all.size
            activeProvider = all[nextIdx]
            activeModel = if (activeProvider == AiProvider.CUSTOM) {
                vault.getCustomModelId().ifEmpty { "custom-model" }
            } else {
                activeProvider.models.first()
            }
            getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE).edit()
                .putString("active_provider", activeProvider.id)
                .putString("active_model", activeModel)
                .apply()
            applyVisualPreferences()
            Toast.makeText(this, "Beralih ke ${activeProvider.displayName}", Toast.LENGTH_SHORT).show()
        }

        floatingView.findViewById<TextView>(R.id.chipAutoRouter).setOnClickListener { tv ->
            isAutoRouterEnabled = !isAutoRouterEnabled
            (tv as TextView).text = if (isAutoRouterEnabled) "Auto-Router: ON" else "Auto-Router: OFF"
            tv.setTextColor(if (isAutoRouterEnabled) Color.parseColor("#38BDF8") else Color.parseColor("#E2E8F0"))
        }

        floatingView.findViewById<TextView>(R.id.chipClipboard).setOnClickListener {
            val cm = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            val clipText = cm.primaryClip?.getItemAt(0)?.text?.toString().orEmpty()
            if (clipText.isBlank()) {
                Toast.makeText(this, "Clipboard kosong.", Toast.LENGTH_SHORT).show()
            } else {
                etPromptInput.setText("Ringkas / jelaskan isi clipboard ini:\n$clipText")
                smartToolsDrawer.visibility = View.GONE
            }
        }

        floatingView.findViewById<TextView>(R.id.chipCalculator).setOnClickListener {
            val expr = etPromptInput.text.toString().trim()
            if (expr.isEmpty()) {
                etPromptInput.hint = "Ketik hitungan (mis. (25*4)+15) lalu klik Kalkulator"
            } else {
                val res = SmartToolsHelper.evaluateMath(expr)
                appendMessageBubble(ChatMessage(role = "assistant", content = "Hasil Kalkulator ($expr) = $res", providerTag = "Kalkulator"))
                etPromptInput.setText("")
            }
        }

        floatingView.findViewById<TextView>(R.id.chipNewSession).setOnClickListener {
            currentThread = repo.createNewThread("Sesi ${System.currentTimeMillis() % 1000}")
            renderCurrentThreadMessages()
            smartToolsDrawer.visibility = View.GONE
            Toast.makeText(this, "Sesi baru dimulai.", Toast.LENGTH_SHORT).show()
        }

        floatingView.findViewById<TextView>(R.id.chipQuickForceStop).setOnClickListener {
            stopSelf()
        }

        floatingView.findViewById<EditText>(R.id.etSearchHistory).addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                refreshHistoryList(floatingView.findViewById(R.id.historyResultsContainer), s?.toString().orEmpty())
            }
            override fun afterTextChanged(s: Editable?) {}
        })

        setupQuickPromptChips()

        floatingView.findViewById<ImageView>(R.id.btnAttachFile).setOnClickListener {
            val pick = Intent(this, FilePickerProxyActivity::class.java).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            startActivity(pick)
        }

        floatingView.findViewById<ImageView>(R.id.btnVoiceMic).setOnClickListener {
            triggerHaptic()
            if (voiceManager.isListening) {
                voiceManager.stopListening()
            } else {
                voiceManager.startListening()
            }
        }

        btnSendOrStop.setOnClickListener {
            triggerHaptic()
            if (activeGenerationJob?.isActive == true) {
                activeGenerationJob?.cancel()
                btnSendOrStop.setImageResource(R.drawable.ic_send)
            } else {
                val text = etPromptInput.text.toString().trim()
                if (text.isNotEmpty() || pendingAttachment != null || isScreenShareActive) {
                    sendUserPrompt(text.ifEmpty { "Analisis tampilan layar / lampiran ini secara singkat dan jelas." })
                }
            }
        }

        applyVisualPreferences()
        renderCurrentThreadMessages()
    }

    private fun setupQuickPromptChips() {
        val row = floatingView.findViewById<LinearLayout>(R.id.quickPromptsRow)
        row.removeAllViews()
        val d = resources.displayMetrics.density
        val actions = listOf(
            "Baca Layar" to "Jelaskan apa yang tampil di layar ini dan bantu jawab jika ada pertanyaan.",
            "Ringkas" to "Ringkas teks berikut menjadi poin inti yang mudah dipahami:",
            "Terjemahkan" to "Terjemahkan ke Bahasa Indonesia yang natural:",
            "Perbaiki Bahasa" to "Perbaiki tata bahasa dan buat kalimat ini lebih rapi:",
            "Bantu Balas" to "Buatkan 3 opsi balasan yang sopan dan asik untuk pesan ini:"
        )

        for ((label, promptPrefix) in actions) {
            val chip = TextView(this).apply {
                text = label
                textSize = 11f
                setTextColor(Color.parseColor("#CBD5E1"))
                setPadding((10 * d).toInt(), (5 * d).toInt(), (10 * d).toInt(), (5 * d).toInt())
                setBackgroundResource(R.drawable.bg_chip_glass)
                setOnClickListener {
                    val existing = etPromptInput.text.toString().trim()
                    if (label == "Baca Layar") {
                        sendUserPrompt(promptPrefix)
                    } else if (existing.isNotEmpty()) {
                        sendUserPrompt("$promptPrefix\n$existing")
                    } else {
                        etPromptInput.setText("$promptPrefix ")
                        etPromptInput.setSelection(etPromptInput.text.length)
                    }
                }
            }
            val lp = LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT).apply {
                marginEnd = (6 * d).toInt()
            }
            row.addView(chip, lp)
        }
    }

    private fun applyVisualPreferences() {
        if (::dynamicIslandGlassHost.isInitialized && ::dynamicIslandView.isInitialized) {
            dynamicIslandGlassHost.cornerRadiusDp = 17f
            dynamicIslandGlassHost.bevelWidthDp = 9f
            dynamicIslandGlassHost.materialVariant = LiquidGlassFrameLayout.GlassMaterialVariant.CLEAR
            dynamicIslandGlassHost.dispersionStrength = if (prefPillAppearance == "polos") 0f else 0.34f
            dynamicIslandGlassHost.specularIntensity = if (prefPillAppearance == "polos") 0f else 0.72f

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
                    dynamicIslandView.background = null
                    ivIslandSparkle.visibility = View.VISIBLE
                    tvIslandLabel.visibility = View.GONE
                    viewIslandPulseDot.visibility = View.VISIBLE
                }
                else -> {
                    dynamicIslandView.background = null
                    ivIslandSparkle.visibility = View.VISIBLE
                    tvIslandLabel.visibility = View.VISIBLE
                    viewIslandPulseDot.visibility = View.VISIBLE
                }
            }
        }
        if (::popupChatView.isInitialized) {
            popupChatView.cornerRadiusDp = 28f
            popupChatView.bevelWidthDp = 16f
            popupChatView.materialVariant = LiquidGlassFrameLayout.GlassMaterialVariant.REGULAR
            popupChatView.dispersionStrength = 0.28f
            popupChatView.specularIntensity = 0.62f
            popupChatView.alpha = prefPopupAlpha
        }
        if (::tvActiveProviderHeader.isInitialized) {
            tvActiveProviderHeader.text = "${activeProvider.displayName} • $activeModel"
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

    private fun regenerateLastResponse() {
        val lastUserIdx = currentThread.messages.indexOfLast { it.role == "user" }
        if (lastUserIdx < 0) return
        val lastUserPrompt = currentThread.messages[lastUserIdx].content
        while (currentThread.messages.size > lastUserIdx) {
            currentThread.messages.removeAt(currentThread.messages.lastIndex)
        }
        repo.saveThread(currentThread)
        renderCurrentThreadMessages()
        sendUserPrompt(lastUserPrompt)
    }

    private fun sendUserPrompt(rawPrompt: String) {
        etPromptInput.setText("")
        val attachment = pendingAttachment
        pendingAttachment = null
        tvAttachmentBadge.visibility = View.GONE

        val composedPrompt = buildString {
            append(rawPrompt)
            if (attachment != null && attachment.extractedText.isNotEmpty()) {
                append("\n\n[Isi Dokumen ${attachment.displayName}]:\n")
                append(attachment.extractedText)
            }
        }

        val userMsg = ChatMessage(role = "user", content = rawPrompt)
        currentThread.messages.add(userMsg)
        if (currentThread.messages.size == 1) {
            currentThread.title = rawPrompt.take(28)
        }
        repo.saveThread(currentThread)
        appendMessageBubble(userMsg)

        val imagesToSend = mutableListOf<String>()
        if (attachment != null) imagesToSend.addAll(attachment.base64Images)
        if (isScreenShareActive) {
            captureCurrentScreenBase64()?.let { imagesToSend.add(it) }
        }

        val systemInstruction = buildSystemPrompt()
        btnSendOrStop.setImageResource(R.drawable.ic_stop)

        activeGenerationJob = serviceScope.launch {
            if (isCompareMode) {
                val primary = Pair(activeProvider, activeModel)
                val secondaryProv = AiProvider.entries.firstOrNull { it != activeProvider && vault.hasApiKey(it.id) }
                    ?: activeProvider
                val secondary = Pair(secondaryProv, secondaryProv.models.first())

                val leftView = appendStreamingAssistantBubble("${primary.first.displayName}")
                val rightView = appendStreamingAssistantBubble("${secondary.first.displayName}")

                val historyCopy = currentThread.messages.dropLast(1) + ChatMessage(role = "user", content = composedPrompt)

                launch {
                    val sb1 = StringBuilder()
                    val r1 = aiEngine.streamChat(primary.first, primary.second, systemInstruction, historyCopy, imagesToSend) { chunk ->
                        sb1.append(chunk)
                        withContext(Dispatchers.Main) {
                            leftView.text = cleanMarkdownSymbols(sb1.toString()) + " ▍"
                            scrollChatToBottom()
                        }
                    }
                    val final1 = r1.getOrElse { "Error: ${it.message}" }
                    leftView.text = cleanMarkdownSymbols(final1)
                    repo.recordUsage(primary.first.displayName, final1.length)
                }

                val sb2 = StringBuilder()
                val r2 = aiEngine.streamChat(secondary.first, secondary.second, systemInstruction, historyCopy, imagesToSend) { chunk ->
                    sb2.append(chunk)
                    withContext(Dispatchers.Main) {
                        rightView.text = cleanMarkdownSymbols(sb2.toString()) + " ▍"
                        scrollChatToBottom()
                    }
                }
                val final2 = r2.getOrElse { "Error: ${it.message}" }
                rightView.text = cleanMarkdownSymbols(final2)
                repo.recordUsage(secondary.first.displayName, final2.length)
                btnSendOrStop.setImageResource(R.drawable.ic_send)
            } else {
                val (chosenProv, chosenModel) = if (isAutoRouterEnabled) {
                    aiEngine.resolveAutoRouter(composedPrompt, imagesToSend.isNotEmpty())
                } else {
                    Pair(activeProvider, activeModel)
                }

                val aiTextView = appendStreamingAssistantBubble("${chosenProv.displayName} • $chosenModel")
                val historyForApi = currentThread.messages.dropLast(1) + ChatMessage(role = "user", content = composedPrompt)
                val sb = StringBuilder()

                val result = aiEngine.streamChat(
                    provider = chosenProv,
                    model = chosenModel,
                    systemPrompt = systemInstruction,
                    history = historyForApi,
                    imageBase64List = imagesToSend,
                    onChunk = { chunk ->
                        sb.append(chunk)
                        withContext(Dispatchers.Main) {
                            aiTextView.text = cleanMarkdownSymbols(sb.toString()) + " ▍"
                            scrollChatToBottom()
                        }
                    }
                )

                val finalClean = result.fold(
                    onSuccess = { cleanMarkdownSymbols(it).ifEmpty { "Tidak ada respons." } },
                    onFailure = { "Kendala: ${it.message}" }
                )
                aiTextView.text = finalClean
                btnSendOrStop.setImageResource(R.drawable.ic_send)

                val assistantMsg = ChatMessage(
                    role = "assistant",
                    content = finalClean,
                    providerTag = "${chosenProv.displayName} • $chosenModel"
                )
                currentThread.messages.add(assistantMsg)
                repo.saveThread(currentThread)
                repo.recordUsage(chosenProv.displayName, finalClean.length)
                renderCurrentThreadMessages()
            }
        }
    }

    private fun buildSystemPrompt(): String {
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        val pIdx = prefs.getInt("personality_index", 0)
        val customNote = prefs.getString("custom_system_prompt", "").orEmpty()
        val styleRule = when (pIdx) {
            1 -> "Jawab singkat, padat, langsung ke inti pertanyaan."
            2 -> "Jawab terstruktur dan jelas dengan penjelasan menyeluruh."
            3 -> "Jawab kreatif, ekspresif, dan inspiratif."
            4 -> "Jawab sebagai senior software engineer yang akurat."
            else -> "Jawab dengan gaya bahasa Indonesia yang asik, santai, ramah, dan langsung ke inti pertanyaan minimal 1-3 kalimat."
        }
        return "Kamu adalah Floamini, asisten AI pribadi di layar Android. $styleRule Jangan gunakan simbol markdown bintang (* atau **) atau tanda pagar (#). $customNote".trim()
    }

    private fun cleanMarkdownSymbols(text: String): String {
        return text.replace("**", "").replace("*", "").replace("###", "").replace("##", "").trim()
    }

    private fun renderCurrentThreadMessages() {
        chatMessagesContainer.removeAllViews()
        if (currentThread.messages.isEmpty()) {
            appendMessageBubble(
                ChatMessage(
                    role = "assistant",
                    content = "Halo! Aku Floamini Liquid Glass siap bantu. Ketuk ikon layar untuk berbagi tampilan layar atau langsung ketik pertanyaanmu.",
                    providerTag = "Floamini OS"
                )
            )
            return
        }
        currentThread.messages.forEachIndexed { idx, m ->
            appendMessageBubble(m, isLastAssistant = (idx == currentThread.messages.lastIndex && m.role == "assistant"))
        }
        scrollChatToBottom()
    }

    private fun appendMessageBubble(msg: ChatMessage, isLastAssistant: Boolean = false) {
        val d = resources.displayMetrics.density
        val isUser = msg.role == "user"

        val wrapper = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = if (isUser) Gravity.END else Gravity.START
            val lp = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                bottomMargin = (8 * d).toInt()
            }
            layoutParams = lp
            alpha = 0f
            translationY = 12f * d
        }

        if (!isUser && msg.providerTag.isNotEmpty()) {
            val tagTv = TextView(this).apply {
                text = msg.providerTag
                textSize = 9.5f
                setTextColor(Color.parseColor("#38BDF8"))
                setPadding((4 * d).toInt(), 0, 0, (2 * d).toInt())
            }
            wrapper.addView(tagTv)
        }

        val bubbleTv = TextView(this).apply {
            text = msg.content
            textSize = 12.5f
            setTextColor(Color.parseColor("#F8FAFC"))
            setPadding((12 * d).toInt(), (9 * d).toInt(), (12 * d).toInt(), (9 * d).toInt())
            setBackgroundResource(if (isUser) R.drawable.bg_msg_user else R.drawable.bg_msg_ai)
            maxWidth = (268 * d).toInt()
            setOnLongClickListener {
                val cm = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                cm.setPrimaryClip(ClipData.newPlainText("Floamini", msg.content))
                Toast.makeText(this@FloatingAssistantService, "Teks disalin!", Toast.LENGTH_SHORT).show()
                true
            }
        }
        wrapper.addView(bubbleTv)

        if (!isUser) {
            val actionRow = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                setPadding((4 * d).toInt(), (3 * d).toInt(), 0, 0)
            }
            val btnSpeak = TextView(this).apply {
                text = "Dengarkan"
                textSize = 10f
                setTextColor(Color.parseColor("#94A3B8"))
                setPadding(0, 0, (12 * d).toInt(), 0)
                setOnClickListener { voiceManager.speak(msg.content) }
            }
            val btnCopy = TextView(this).apply {
                text = "Salin"
                textSize = 10f
                setTextColor(Color.parseColor("#94A3B8"))
                setPadding(0, 0, (12 * d).toInt(), 0)
                setOnClickListener {
                    val cm = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                    cm.setPrimaryClip(ClipData.newPlainText("Floamini", msg.content))
                    Toast.makeText(this@FloatingAssistantService, "Disalin!", Toast.LENGTH_SHORT).show()
                }
            }
            actionRow.addView(btnSpeak)
            actionRow.addView(btnCopy)
            if (isLastAssistant) {
                val btnRegen = TextView(this).apply {
                    text = "Ulangi"
                    textSize = 10f
                    setTextColor(Color.parseColor("#38BDF8"))
                    setOnClickListener { regenerateLastResponse() }
                }
                actionRow.addView(btnRegen)
            }
            wrapper.addView(actionRow)
        }

        chatMessagesContainer.addView(wrapper)
        wrapper.animate().alpha(1f).translationY(0f).setDuration(200L).start()
        scrollChatToBottom()
    }

    private fun appendStreamingAssistantBubble(providerLabel: String): TextView {
        val d = resources.displayMetrics.density
        val wrapper = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.START
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                bottomMargin = (8 * d).toInt()
            }
        }
        val tagTv = TextView(this).apply {
            text = providerLabel
            textSize = 9.5f
            setTextColor(Color.parseColor("#38BDF8"))
            setPadding((4 * d).toInt(), 0, 0, (2 * d).toInt())
        }
        val bubbleTv = TextView(this).apply {
            text = "Berpikir... ▍"
            textSize = 12.5f
            setTextColor(Color.parseColor("#F8FAFC"))
            setPadding((12 * d).toInt(), (9 * d).toInt(), (12 * d).toInt(), (9 * d).toInt())
            setBackgroundResource(R.drawable.bg_msg_ai)
            maxWidth = (268 * d).toInt()
        }
        wrapper.addView(tagTv)
        wrapper.addView(bubbleTv)
        chatMessagesContainer.addView(wrapper)
        scrollChatToBottom()
        return bubbleTv
    }

    private fun scrollChatToBottom() {
        chatScrollView.post {
            chatScrollView.fullScroll(View.FOCUS_DOWN)
        }
    }

    private fun showCollapsedTriggerState() {
        mainHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
        mainHandler.removeCallbacks(autoHidePillRunnable)
        dismissSiriAura()

        popupChatView.stopAmbientRefraction()
        popupChatView.visibility = View.GONE
        dynamicIslandGlassHost.visibility = View.GONE
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
            }
            "classic_bubble" -> {
                wakeFromSmartFreeze()
                bubbleView.visibility = View.VISIBLE
                bubbleView.alpha = 1.0f
                params.x = if (snappedToRightEdge) (fullScreenWidth - prefBubbleSizePx) else 0
                params.y = fullScreenHeight / 3
                windowManager.updateViewLayout(floatingView, params)
            }
            else -> {
                wakeFromSmartFreeze()
                dynamicIslandGlassHost.visibility = View.VISIBLE
                dynamicIslandGlassHost.scaleX = 0.72f
                dynamicIslandGlassHost.scaleY = 0.72f
                dynamicIslandGlassHost.alpha = 1.0f
                if (prefPillAppearance != "polos") {
                    dynamicIslandGlassHost.startAmbientRefraction()
                }
                params.x = (((fullScreenWidth - prefIslandWidthPx) / 2) + prefIslandOffsetXPx)
                    .coerceIn(12, (fullScreenWidth - prefIslandWidthPx - 12).coerceAtLeast(12))
                params.y = prefIslandPosYPx
                windowManager.updateViewLayout(floatingView, params)
                animateSpringScale(dynamicIslandGlassHost, 1.0f)
                scheduleAutoHideAndFreeze()
            }
        }
    }

    private fun openPopupChat(fromSiri: Boolean) {
        wakeFromSmartFreeze()
        mainHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
        mainHandler.removeCallbacks(autoHidePillRunnable)

        dynamicIslandGlassHost.stopAmbientRefraction()
        dynamicIslandGlassHost.visibility = View.GONE
        xiaomiEdgeView.visibility = View.GONE
        bubbleView.visibility = View.GONE

        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        val density = resources.displayMetrics.density
        val savedW = prefs.getInt("last_win_w", (352 * density).toInt())
        val savedH = prefs.getInt("last_win_h", (500 * density).toInt())
        val lp = popupChatView.layoutParams
        lp.width = if (isMiniWindowMode) (280 * density).toInt() else savedW
        lp.height = if (isMiniWindowMode) (265 * density).toInt() else savedH
        popupChatView.layoutParams = lp

        popupChatView.visibility = View.VISIBLE
        popupChatView.startAmbientRefraction()
        popupChatView.pivotX = lp.width / 2f
        popupChatView.pivotY = if (fromSiri) lp.height.toFloat() else 0f
        popupChatView.scaleX = 0.58f
        popupChatView.scaleY = 0.38f
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
        etPromptInput.requestFocus()

        popupChatView.animate()
            .alpha(prefPopupAlpha)
            .setDuration(220L)
            .start()
        animateSpringScale(popupChatView, 1.0f)
    }

    private fun triggerSiriSummon() {
        wakeFromSmartFreeze()
        triggerHaptic()
        if (!isSiriAuraAttached) {
            val glow = SiriEdgeGlowView(this)
            val overlayType = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
            } else {
                @Suppress("DEPRECATION")
                WindowManager.LayoutParams.TYPE_PHONE
            }
            val glowParams = WindowManager.LayoutParams(
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.MATCH_PARENT,
                overlayType,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                        WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE or
                        WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
                PixelFormat.TRANSLUCENT
            )
            windowManager.addView(glow, glowParams)
            siriGlowView = glow
            isSiriAuraAttached = true
        }
        siriGlowView?.startSiriAnimation()
        openPopupChat(fromSiri = true)
    }

    private fun dismissSiriAura() {
        if (isSiriAuraAttached && siriGlowView != null) {
            siriGlowView?.stopAndFreezeAnimation()
            try {
                windowManager.removeView(siriGlowView)
            } catch (_: Exception) {
            }
            siriGlowView = null
            isSiriAuraAttached = false
        }
    }

    private fun scheduleAutoHideAndFreeze() {
        mainHandler.removeCallbacks(autoHidePillRunnable)
        if (prefAutoHidePill) {
            mainHandler.postDelayed(autoHidePillRunnable, 3000L)
        }
    }

    private fun enterSmartFreezeState() {
        if (isSmartFrozen) return
        isSmartFrozen = true
        mainHandler.removeCallbacks(autoHidePillRunnable)
        mainHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
        dynamicIslandGlassHost.stopAmbientRefraction()
        popupChatView.stopAmbientRefraction()
        siriGlowView?.stopAndFreezeAnimation()

        if (prefOverlayStyle == "siri_mode" && isFloatingViewAttached) {
            try {
                windowManager.removeView(floatingView)
                isFloatingViewAttached = false
            } catch (_: Exception) {
            }
        }
    }

    private fun wakeFromSmartFreeze() {
        isSmartFrozen = false
        if (!isFloatingViewAttached) {
            windowManager.addView(floatingView, params)
            isFloatingViewAttached = true
        }
    }

    private fun applyWindowBlur(enabled: Boolean) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            try {
                if (enabled) {
                    params.flags = params.flags or WindowManager.LayoutParams.FLAG_BLUR_BEHIND
                    params.blurBehindRadius = 42
                } else {
                    params.flags = params.flags and WindowManager.LayoutParams.FLAG_BLUR_BEHIND.inv()
                    params.blurBehindRadius = 0
                }
            } catch (_: Throwable) {
            }
        }
    }

    private fun saveLastWindowGeometry() {
        getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE).edit()
            .putInt("last_win_x", params.x)
            .putInt("last_win_y", params.y)
            .putInt("last_win_w", popupChatView.layoutParams.width)
            .putInt("last_win_h", popupChatView.layoutParams.height)
            .apply()
    }

    private fun animateSpringScale(target: View, endScale: Float) {
        SpringAnimation(target, DynamicAnimation.SCALE_X, endScale).apply {
            spring = SpringForce(endScale).apply {
                dampingRatio = SpringForce.DAMPING_RATIO_MEDIUM_BOUNCY
                stiffness = SpringForce.STIFFNESS_MEDIUM
            }
            start()
        }
        SpringAnimation(target, DynamicAnimation.SCALE_Y, endScale).apply {
            spring = SpringForce(endScale).apply {
                dampingRatio = SpringForce.DAMPING_RATIO_MEDIUM_BOUNCY
                stiffness = SpringForce.STIFFNESS_MEDIUM
            }
            start()
        }
    }

    private fun triggerHaptic() {
        floatingView.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP)
    }

    private fun startMediaProjectionCapture(resultCode: Int, data: Intent) {
        stopMediaProjection()
        startForegroundNotification(withMediaProjection = true)
        val mgr = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        mediaProjection = mgr.getMediaProjection(resultCode, data)

        val capW = (fullScreenWidth / 2).coerceAtLeast(360)
        val capH = (fullScreenHeight / 2).coerceAtLeast(640)
        imageReader = ImageReader.newInstance(capW, capH, PixelFormat.RGBA_8888, 2)
        virtualDisplay = mediaProjection?.createVirtualDisplay(
            "FloaminiScreenVision",
            capW,
            capH,
            resources.displayMetrics.densityDpi,
            DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
            imageReader?.surface,
            null,
            mainHandler
        )

        isScreenShareActive = true
        btnScreenShare.setColorFilter(Color.parseColor("#38BDF8"))
        tvScreenShareStatus.visibility = View.VISIBLE
        tvIslandLabel.text = "Live Vision"
        popupChatView.dispersionStrength = 0.46f
        popupChatView.specularIntensity = 0.88f
        Toast.makeText(this, "Live Screen Vision aktif", Toast.LENGTH_SHORT).show()
    }

    private fun captureCurrentScreenBase64(): String? {
        val image = imageReader?.acquireLatestImage() ?: return null
        return try {
            val plane = image.planes[0]
            val buffer = plane.buffer
            val pixelStride = plane.pixelStride
            val rowStride = plane.rowStride
            val rowPadding = rowStride - pixelStride * image.width
            val bmp = Bitmap.createBitmap(
                image.width + rowPadding / pixelStride,
                image.height,
                Bitmap.Config.ARGB_8888
            )
            bmp.copyPixelsFromBuffer(buffer)
            val cropped = Bitmap.createBitmap(bmp, 0, 0, image.width, image.height)
            bmp.recycle()
            val b64 = SmartToolsHelper.bitmapToBase64(cropped, 960)
            cropped.recycle()
            b64
        } catch (_: Exception) {
            null
        } finally {
            image.close()
        }
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
        if (::popupChatView.isInitialized) {
            popupChatView.dispersionStrength = 0.28f
            popupChatView.specularIntensity = 0.62f
        }
        startForegroundNotification(withMediaProjection = false)
    }

    private fun handlePickedUri(uri: Uri) {
        serviceScope.launch(Dispatchers.IO) {
            val processed = SmartToolsHelper.processUri(this@FloatingAssistantService, uri)
            withContext(Dispatchers.Main) {
                pendingAttachment = processed
                tvAttachmentBadge.text = "Lampiran siap: ${processed.displayName}"
                tvAttachmentBadge.visibility = View.VISIBLE
            }
        }
    }

    override fun onDestroy() {
        mainHandler.removeCallbacksAndMessages(null)
        serviceScope.cancel()
        stopMediaProjection()
        dismissSiriAura()
        if (::voiceManager.isInitialized) voiceManager.release()
        try { unregisterReceiver(screenOffReceiver) } catch (_: Exception) {}
        if (isFloatingViewAttached) {
            try { windowManager.removeView(floatingView) } catch (_: Exception) {}
        }
        super.onDestroy()
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
        print(f"Berhasil membuat: {filepath}")

    for stale_file in ["local.properties", "build_termux.sh"]:
        if os.path.exists(stale_file):
            os.remove(stale_file)
            print(f"Membersihkan file lokal: {stale_file}")

    print("\nProyek Floamini OS v7.1 (GitHub Actions Ready) selesai diperbarui!")


if __name__ == "__main__":
    generate_project()
