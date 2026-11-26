import os

# ==============================================================================
# SKRIP PEMBANGKIT PROYEK ANDROID: FLOATING GEMINI AI ASSISTANT
# ==============================================================================

PROJECT_FILES = {
    # 1. GITHUB ACTIONS WORKFLOW (Menggunakan Gradle 8.5 agar kompatibel dengan AGP 8.2.2)
    ".github/workflows/build_apk.yml": """name: Build Android Debug APK

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

      - name: Setup Gradle 8.5
        uses: gradle/actions/setup-gradle@v3
        with:
          gradle-version: '8.5'

      - name: Build Debug APK
        run: gradle assembleDebug

      - name: Upload APK Artifact
        uses: actions/upload-artifact@v4
        with:
          name: FloatingGeminiAI-debug
          path: app/build/outputs/apk/debug/app-debug.apk
""",

    # 2. KONFIGURASI GRADLE ROOT
    "settings.gradle.kts": """pluginManagement {
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
rootProject.name = "FloatingGeminiAI"
include(":app")
""",

    "build.gradle.kts": """plugins {
    id("com.android.application") version "8.2.2" apply false
    id("org.jetbrains.kotlin.android") version "1.9.22" apply false
}
""",

    "gradle.properties": """org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
android.nonTransitiveRClass=true
""",

    # 3. KONFIGURASI GRADLE MODULE (:app)
    "app/build.gradle.kts": """plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.floatinggeminiai"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.floatinggeminiai"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
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
    
    // Coroutines untuk pemanggilan API Asynchronous
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    
    // OkHttp untuk koneksi langsung ke REST API Gemini
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
}
""",

    # 4. ANDROID MANIFEST (Izin Overlay, Internet, & Foreground Service)
    "app/src/main/AndroidManifest.xml": """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Izin Internet untuk menghubungi API Gemini -->
    <uses-permission android:name="android.permission.INTERNET" />
    
    <!-- Izin Muncul di Atas Aplikasi Lain (Floating Bubble) -->
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
    
    <!-- Izin Foreground Service agar Bubble tidak dimatikan sistem -->
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <application
        android:allowBackup="true"
        android:label="Gemini Overlay AI"
        android:supportsRtl="true"
        android:theme="@style/Theme.Material3.DayNight.NoActionBar">

        <!-- Halaman Utama Pengaturan Token & Aktivasi Bubble -->
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Service untuk Menampilkan Floating Bubble & Popup Chat -->
        <service
            android:name=".FloatingAssistantService"
            android:enabled="true"
            android:exported="false"
            android:foregroundServiceType="specialUse">
            <property
                android:name="android.app.PROPERTY_SPECIAL_USE_FGS_SUBTYPE"
                android:value="Floating AI Assistant Overlay" />
        </service>

    </application>
</manifest>
""",

    # 5. LAYOUT HALAMAN UTAMA (Input Token Gemini & Tombol Mulai)
    "app/src/main/res/layout/activity_main.xml": """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="24dp"
    android:gravity="center_vertical"
    android:background="#F8FAFC">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="✨ Gemini Floating AI"
        android:textSize="26sp"
        android:textStyle="bold"
        android:textColor="#0F172A" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        android:layout_marginBottom="24dp"
        android:text="Masukkan Gemini API Token Anda untuk mengaktifkan asisten mengambang di atas layar."
        android:textSize="14sp"
        android:textColor="#475569" />

    <com.google.android.material.textfield.TextInputLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Gemini API Key / Token"
        app:endIconMode="password_toggle"
        style="@style/Widget.Material3.TextInputLayout.OutlinedBox">

        <com.google.android.material.textfield.TextInputEditText
            android:id="@+id/etApiKey"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:inputType="textPassword" />
    </com.google.android.material.textfield.TextInputLayout>

    <Button
        android:id="@+id/btnSaveToken"
        android:layout_width="match_parent"
        android:layout_height="52dp"
        android:layout_marginTop="16dp"
        android:text="Simpan Token"
        android:backgroundTint="#2563EB"
        android:textColor="#FFFFFF" />

    <View
        android:layout_width="match_parent"
        android:layout_height="1dp"
        android:layout_marginVertical="24dp"
        android:background="#E2E8F0" />

    <Button
        android:id="@+id/btnStartOverlay"
        android:layout_width="match_parent"
        android:layout_height="56dp"
        android:text="🚀 Munculkan Bubble AI di Layar"
        android:backgroundTint="#0F172A"
        android:textColor="#FFFFFF" />

    <Button
        android:id="@+id/btnStopOverlay"
        android:layout_width="match_parent"
        android:layout_height="48dp"
        android:layout_marginTop="12dp"
        android:text="Matikan Bubble AI"
        style="@style/Widget.Material3.Button.OutlinedButton" />

</LinearLayout>
""",

    # 6. LAYOUT OVERLAY (BUBBLE + POPUP CHAT + PENGATURAN TOKEN CEPAT)
    "app/src/main/res/layout/layout_floating_assistant.xml": """<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content">

    <!-- 1. TAMPILAN BUBBLE MENGAMBANG -->
    <LinearLayout
        android:id="@+id/bubbleView"
        android:layout_width="60dp"
        android:layout_height="60dp"
        android:background="@drawable/bg_bubble"
        android:gravity="center"
        android:elevation="8dp">

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="✨"
            android:textSize="26sp" />
    </LinearLayout>

    <!-- 2. TAMPILAN POPUP CHAT & TOKEN SAAT BUBBLE DIKLIK -->
    <LinearLayout
        android:id="@+id/popupChatView"
        android:layout_width="320dp"
        android:layout_height="430dp"
        android:orientation="vertical"
        android:background="@drawable/bg_popup"
        android:padding="14dp"
        android:elevation="12dp"
        android:visibility="gone">

        <!-- Header Popup -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:paddingBottom="8dp">

            <TextView
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:text="✨ Gemini Assistant"
                android:textStyle="bold"
                android:textSize="16sp"
                android:textColor="#0F172A" />

            <!-- Tombol Toggle Pengaturan Token di Popup -->
            <TextView
                android:id="@+id/btnToggleTokenPanel"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="🔑 Token"
                android:textSize="12sp"
                android:textColor="#2563EB"
                android:padding="6dp"
                android:layout_marginEnd="6dp" />

            <!-- Tombol Perkecil Kembali ke Bubble -->
            <TextView
                android:id="@+id/btnMinimizePopup"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="➖"
                android:textSize="16sp"
                android:padding="6dp" />
        </LinearLayout>

        <!-- Panel Ubah Token Langsung di Popup (Tersembunyi secara default) -->
        <LinearLayout
            android:id="@+id/tokenPanel"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:background="#F1F5F9"
            android:padding="8dp"
            android:layout_marginBottom="8dp"
            android:visibility="gone">

            <EditText
                android:id="@+id/etPopupToken"
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:hint="Tempel Gemini API Key..."
                android:textSize="12sp"
                android:inputType="textPassword"
                android:background="@android:color/transparent"
                android:padding="4dp" />

            <Button
                android:id="@+id/btnSavePopupToken"
                android:layout_width="wrap_content"
                android:layout_height="36dp"
                android:text="Simpan"
                android:textSize="11sp"
                android:backgroundTint="#2563EB"
                android:textColor="#FFFFFF" />
        </LinearLayout>

        <!-- Area Riwayat Percakapan -->
        <ScrollView
            android:id="@+id/scrollChat"
            android:layout_width="match_parent"
            android:layout_height="0dp"
            android:layout_weight="1"
            android:background="#F8FAFC"
            android:padding="10dp">

            <TextView
                android:id="@+id/tvChatHistory"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="AI: Halo! Ada yang bisa saya bantu di layar ini?"
                android:textSize="13sp"
                android:lineSpacingExtra="4dp"
                android:textColor="#1E293B" />
        </ScrollView>

        <!-- Input Pesan & Tombol Kirim -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:layout_marginTop="8dp">

            <EditText
                android:id="@+id/etPrompt"
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:hint="Tanya sesuatu..."
                android:textSize="13sp"
                android:maxLines="3"
                android:padding="10dp"
                android:background="@drawable/bg_input" />

            <Button
                android:id="@+id/btnSendPrompt"
                android:layout_width="wrap_content"
                android:layout_height="42dp"
                android:layout_marginStart="6dp"
                android:text="Kirim"
                android:textSize="12sp"
                android:backgroundTint="#2563EB"
                android:textColor="#FFFFFF" />
        </LinearLayout>

    </LinearLayout>
</FrameLayout>
""",

    # 7. DRAWABLE RESOURCES (Bentuk Bulat Bubble & Sudut Melengkung Popup)
    "app/src/main/res/drawable/bg_bubble.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="oval">
    <solid android:color="#1E293B" />
    <stroke android:width="2dp" android:color="#38BDF8" />
</shape>
""",

    "app/src/main/res/drawable/bg_popup.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#FFFFFF" />
    <corners android:radius="20dp" />
    <stroke android:width="1dp" android:color="#CBD5E1" />
</shape>
""",

    "app/src/main/res/drawable/bg_input.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#F1F5F9" />
    <corners android:radius="12dp" />
</shape>
""",

    # 8. KODE KOTLIN: MAIN ACTIVITY (Manajemen Izin & Token)
    "app/src/main/java/com/example/floatinggeminiai/MainActivity.kt": """package com.example.floatinggeminiai

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.textfield.TextInputEditText

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        val etApiKey = findViewById<TextInputEditText>(R.id.etApiKey)
        val btnSaveToken = findViewById<Button>(R.id.btnSaveToken)
        val btnStartOverlay = findViewById<Button>(R.id.btnStartOverlay)
        val btnStopOverlay = findViewById<Button>(R.id.btnStopOverlay)

        // Muat token yang sudah tersimpan sebelumnya
        etApiKey.setText(prefs.getString("api_key", ""))

        btnSaveToken.setOnClickListener {
            val token = etApiKey.text.toString().trim()
            if (token.isEmpty()) {
                Toast.makeText(this, "Token tidak boleh kosong!", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            prefs.edit().putString("api_key", token).apply()
            Toast.makeText(this, "Token Gemini berhasil disimpan!", Toast.LENGTH_SHORT).show()
        }

        btnStartOverlay.setOnClickListener {
            if (!Settings.canDrawOverlays(this)) {
                Toast.makeText(this, "Izinkan aplikasi tampil di atas layar terlebih dahulu", Toast.LENGTH_LONG).show()
                val intent = Intent(
                    Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                    Uri.parse("package:$packageName")
                )
                startActivity(intent)
                return@setOnClickListener
            }

            val serviceIntent = Intent(this, FloatingAssistantService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                startForegroundService(serviceIntent)
            } else {
                startService(serviceIntent)
            }
            Toast.makeText(this, "Bubble AI aktif! Silakan keluar dari aplikasi ini.", Toast.LENGTH_SHORT).show()
        }

        btnStopOverlay.setOnClickListener {
            stopService(Intent(this, FloatingAssistantService::class.java))
            Toast.makeText(this, "Bubble AI dimatikan.", Toast.LENGTH_SHORT).show()
        }
    }
}
""",

    # 9. KODE KOTLIN: FLOATING SERVICE + INTEGRASI GEMINI API
    "app/src/main/java/com/example/floatinggeminiai/FloatingAssistantService.kt": """package com.example.floatinggeminiai

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.graphics.PixelFormat
import android.os.Build
import android.os.IBinder
import android.view.Gravity
import android.view.LayoutInflater
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.util.concurrent.TimeUnit
import kotlin.math.abs

class FloatingAssistantService : Service() {

    private lateinit var windowManager: WindowManager
    private lateinit var floatingView: View
    private lateinit var params: WindowManager.LayoutParams
    private val serviceJob = Job()
    private val serviceScope = CoroutineScope(Dispatchers.Main + serviceJob)

    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        startForegroundNotification()
        setupFloatingOverlay()
    }

    private fun startForegroundNotification() {
        val channelId = "floating_gemini_channel"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Gemini Floating Assistant",
                NotificationManager.IMPORTANCE_LOW
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }

        val notification: Notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("Gemini AI Assistant Aktif")
            .setContentText("Ketuk bubble mengambang di layar untuk mulai mengobrol.")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .build()

        startForeground(101, notification)
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

        // Awalnya FLAG_NOT_FOCUSABLE agar layar di belakangnya tetap bisa disentuh saat mode bubble
        params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            layoutFlag,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 50
            y = 250
        }

        windowManager.addView(floatingView, params)

        val bubbleView = floatingView.findViewById<LinearLayout>(R.id.bubbleView)
        val popupChatView = floatingView.findViewById<LinearLayout>(R.id.popupChatView)
        val btnMinimizePopup = floatingView.findViewById<TextView>(R.id.btnMinimizePopup)
        val btnToggleTokenPanel = floatingView.findViewById<TextView>(R.id.btnToggleTokenPanel)
        val tokenPanel = floatingView.findViewById<LinearLayout>(R.id.tokenPanel)
        val etPopupToken = floatingView.findViewById<EditText>(R.id.etPopupToken)
        val btnSavePopupToken = floatingView.findViewById<Button>(R.id.btnSavePopupToken)
        val scrollChat = floatingView.findViewById<ScrollView>(R.id.scrollChat)
        val tvChatHistory = floatingView.findViewById<TextView>(R.id.tvChatHistory)
        val etPrompt = floatingView.findViewById<EditText>(R.id.etPrompt)
        val btnSendPrompt = floatingView.findViewById<Button>(R.id.btnSendPrompt)

        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        etPopupToken.setText(prefs.getString("api_key", ""))

        // Logika Geser (Drag) & Klik pada Bubble
        bubbleView.setOnTouchListener(object : View.OnTouchListener {
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
                        params.x = initialX + (event.rawX - initialTouchX).toInt()
                        params.y = initialY + (event.rawY - initialTouchY).toInt()
                        windowManager.updateViewLayout(floatingView, params)
                        return true
                    }
                    MotionEvent.ACTION_UP -> {
                        val diffX = abs(event.rawX - initialTouchX)
                        val diffY = abs(event.rawY - initialTouchY)
                        // Jika pergeseran sangat kecil, anggap sebagai KLIK untuk membuka popup
                        if (diffX < 10 && diffY < 10) {
                            openPopupChat(bubbleView, popupChatView)
                        }
                        return true
                    }
                }
                return false
            }
        })

        // Perkecil kembali ke bentuk Bubble
        btnMinimizePopup.setOnClickListener {
            closePopupChat(bubbleView, popupChatView)
        }

        // Buka/Tutup Panel Ubah Token di dalam Popup
        btnToggleTokenPanel.setOnClickListener {
            tokenPanel.visibility = if (tokenPanel.visibility == View.VISIBLE) View.GONE else View.VISIBLE
        }

        // Simpan Token dari dalam Popup
        btnSavePopupToken.setOnClickListener {
            val newToken = etPopupToken.text.toString().trim()
            if (newToken.isNotEmpty()) {
                prefs.edit().putString("api_key", newToken).apply()
                tokenPanel.visibility = View.GONE
                Toast.makeText(this, "Token diperbarui!", Toast.LENGTH_SHORT).show()
            }
        }

        // Kirim Pertanyaan ke Gemini API
        btnSendPrompt.setOnClickListener {
            val prompt = etPrompt.text.toString().trim()
            val apiKey = prefs.getString("api_key", "") ?: ""

            if (prompt.isEmpty()) return@setOnClickListener
            if (apiKey.isEmpty()) {
                tokenPanel.visibility = View.VISIBLE
                Toast.makeText(this, "Harap isi Gemini API Token terlebih dahulu!", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            // Tampilkan pesan pengguna di layar
            tvChatHistory.append("\\n\\nKamu: $prompt")
            etPrompt.text.clear()
            btnSendPrompt.isEnabled = false
            btnSendPrompt.text = "..."

            scrollChat.post { scrollChat.fullScroll(View.FOCUS_DOWN) }

            serviceScope.launch {
                val reply = callGeminiApi(apiKey, prompt)
                tvChatHistory.append("\\n\\nAI: $reply")
                btnSendPrompt.isEnabled = true
                btnSendPrompt.text = "Kirim"
                scrollChat.post { scrollChat.fullScroll(View.FOCUS_DOWN) }
            }
        }
    }

    private fun openPopupChat(bubbleView: View, popupChatView: View) {
        bubbleView.visibility = View.GONE
        popupChatView.visibility = View.VISIBLE
        // Hapus FLAG_NOT_FOCUSABLE agar keyboard Android bisa muncul saat mengetik di EditText
        params.flags = WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL
        windowManager.updateViewLayout(floatingView, params)
    }

    private fun closePopupChat(bubbleView: View, popupChatView: View) {
        popupChatView.visibility = View.GONE
        bubbleView.visibility = View.VISIBLE
        // Kembalikan FLAG_NOT_FOCUSABLE agar sentuhan di luar bubble diteruskan ke aplikasi di belakangnya
        params.flags = WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
        windowManager.updateViewLayout(floatingView, params)
    }

    private suspend fun callGeminiApi(apiKey: String, prompt: String): String = withContext(Dispatchers.IO) {
        try {
            val url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key=$apiKey"
            
            val jsonBody = JSONObject().apply {
                put("contents", JSONArray().apply {
                    put(JSONObject().apply {
                        put("parts", JSONArray().apply {
                            put(JSONObject().apply {
                                put("text", prompt)
                            })
                        })
                    })
                })
            }

            val requestBody = jsonBody.toString().toRequestBody("application/json; charset=utf-8".toMediaType())
            val request = Request.Builder()
                .url(url)
                .post(requestBody)
                .build()

            httpClient.newCall(request).execute().use { response ->
                val responseString = response.body?.string() ?: ""
                if (!response.isSuccessful) {
                    return@withContext "Error (${response.code}): Periksa kembali API Token Anda."
                }
                val jsonResponse = JSONObject(responseString)
                val candidates = jsonResponse.optJSONArray("candidates")
                if (candidates != null && candidates.length() > 0) {
                    val content = candidates.getJSONObject(0).optJSONObject("content")
                    val parts = content?.optJSONArray("parts")
                    if (parts != null && parts.length() > 0) {
                        return@withContext parts.getJSONObject(0).optString("text", "Tidak ada jawaban.")
                    }
                }
                return@withContext "Respons kosong dari Gemini."
            }
        } catch (e: Exception) {
            return@withContext "Gagal terhubung: ${e.localizedMessage}"
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        serviceJob.cancel()
        if (::floatingView.isInitialized) {
            windowManager.removeView(floatingView)
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
        print(f"✅ Berhasil membuat: {filepath}")
    print("\n🎉 Proyek Android selesai dibuat! Silakan push folder ini ke GitHub untuk otomatis build APK.")

if __name__ == "__main__":
    generate_project()
