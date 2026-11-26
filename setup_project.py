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
        uses: gradle/actions/setup-gradle@v4
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
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <application
        android:allowBackup="true"
        android:label="Gemini Overlay AI"
        android:supportsRtl="true"
        android:theme="@style/Theme.Material3.Dark.NoActionBar">

        <!-- Halaman Utama Pengaturan Token & Aktivasi Bubble -->
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Activity Transparan untuk Meminta Izin Screen Capture (MediaProjection) -->
        <activity
            android:name=".ScreenCapturePermissionActivity"
            android:exported="false"
            android:theme="@android:style/Theme.Translucent.NoTitleBar" />

        <!-- Service untuk Menampilkan Floating Bubble, Screen Share & Popup Chat -->
        <service
            android:name=".FloatingAssistantService"
            android:enabled="true"
            android:exported="false"
            android:foregroundServiceType="specialUse|mediaProjection">
            <property
                android:name="android.app.PROPERTY_SPECIAL_USE_FGS_SUBTYPE"
                android:value="Floating AI Assistant Overlay" />
        </service>

    </application>
</manifest>
""",

    # 5. LAYOUT HALAMAN UTAMA (Modern Dark Glass UI, Tanpa Emoji)
    "app/src/main/res/layout/activity_main.xml": """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="24dp"
    android:gravity="center_vertical"
    android:background="#090D16">

    <LinearLayout
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:gravity="center_vertical">

        <ImageView
            android:layout_width="32dp"
            android:layout_height="32dp"
            android:src="@drawable/ic_sparkle"
            app:tint="#38BDF8" />

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginStart="12dp"
            android:text="Gemini Floating AI"
            android:textSize="24sp"
            android:textStyle="bold"
            android:textColor="#F8FAFC" />
    </LinearLayout>

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="8dp"
        android:layout_marginBottom="28dp"
        android:text="Asisten AI mengambang dengan dukungan Live Screen Share dan antarmuka macOS."
        android:textSize="14sp"
        android:textColor="#94A3B8" />

    <com.google.android.material.textfield.TextInputLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Gemini API Token"
        app:boxBackgroundColor="#1E293B"
        app:boxStrokeColor="#38BDF8"
        app:hintTextColor="#38BDF8"
        app:endIconMode="password_toggle"
        style="@style/Widget.Material3.TextInputLayout.OutlinedBox">

        <com.google.android.material.textfield.TextInputEditText
            android:id="@+id/etApiKey"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:textColor="#F8FAFC"
            android:inputType="textPassword" />
    </com.google.android.material.textfield.TextInputLayout>

    <Button
        android:id="@+id/btnSaveToken"
        android:layout_width="match_parent"
        android:layout_height="52dp"
        android:layout_marginTop="16dp"
        android:text="Simpan Token"
        android:textStyle="bold"
        android:backgroundTint="#2563EB"
        android:textColor="#FFFFFF" />

    <View
        android:layout_width="match_parent"
        android:layout_height="1dp"
        android:layout_marginVertical="24dp"
        android:background="#1E293B" />

    <Button
        android:id="@+id/btnStartOverlay"
        android:layout_width="match_parent"
        android:layout_height="56dp"
        android:text="Aktifkan Floating Assistant"
        android:textStyle="bold"
        app:icon="@drawable/ic_sparkle"
        app:iconGravity="textStart"
        android:backgroundTint="#0EA5E9"
        android:textColor="#090D16" />

    <Button
        android:id="@+id/btnStopOverlay"
        android:layout_width="match_parent"
        android:layout_height="48dp"
        android:layout_marginTop="12dp"
        android:text="Nonaktifkan Assistant"
        android:textColor="#94A3B8"
        app:strokeColor="#334155"
        style="@style/Widget.Material3.Button.OutlinedButton" />

</LinearLayout>
""",

    # 6. LAYOUT OVERLAY (BUBBLE + MAC OS WINDOW POPUP SEMI-TRANSPARAN + CHAT KIRI-KANAN)
    "app/src/main/res/layout/layout_floating_assistant.xml": """<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content">

    <!-- 1. BUBBLE MENGAMBANG (Akan memudar setelah 3 detik saat minimize) -->
    <FrameLayout
        android:id="@+id/bubbleView"
        android:layout_width="56dp"
        android:layout_height="56dp"
        android:background="@drawable/bg_bubble"
        android:elevation="10dp">

        <ImageView
            android:layout_width="26dp"
            android:layout_height="26dp"
            android:layout_gravity="center"
            android:src="@drawable/ic_sparkle"
            app:tint="#38BDF8" />
    </FrameLayout>

    <!-- 2. POPUP CHAT GAYA MAC OS WINDOW (SEMI-TRANSPARAN) -->
    <LinearLayout
        android:id="@+id/popupChatView"
        android:layout_width="330dp"
        android:layout_height="440dp"
        android:orientation="vertical"
        android:background="@drawable/bg_popup_glass"
        android:elevation="14dp"
        android:visibility="gone">

        <!-- MAC OS TOP ACCESSORY BAR -->
        <LinearLayout
            android:id="@+id/macTitleBar"
            android:layout_width="match_parent"
            android:layout_height="38dp"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:paddingHorizontal="12dp"
            android:background="@drawable/bg_mac_header">

            <!-- Tombol Kontrol Ala macOS (Merah: Tutup Service, Kuning: Minimize) -->
            <View
                android:id="@+id/btnMacClose"
                android:layout_width="13dp"
                android:layout_height="13dp"
                android:background="@drawable/dot_mac_red" />

            <View
                android:id="@+id/btnMacMinimize"
                android:layout_width="13dp"
                android:layout_height="13dp"
                android:layout_marginStart="8dp"
                android:background="@drawable/dot_mac_yellow" />

            <View
                android:layout_width="13dp"
                android:layout_height="13dp"
                android:layout_marginStart="8dp"
                android:background="@drawable/dot_mac_green" />

            <TextView
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:gravity="center"
                android:text="Gemini AI"
                android:textSize="12sp"
                android:textStyle="bold"
                android:textColor="#CBD5E1" />

            <!-- Tombol Toggle Live Screen Share -->
            <ImageView
                android:id="@+id/btnScreenShare"
                android:layout_width="24dp"
                android:layout_height="24dp"
                android:padding="3dp"
                android:src="@drawable/ic_screen_share"
                app:tint="#94A3B8"
                android:contentDescription="Screen Share" />

            <!-- Tombol Toggle Token -->
            <ImageView
                android:id="@+id/btnToggleTokenPanel"
                android:layout_width="24dp"
                android:layout_height="24dp"
                android:layout_marginStart="6dp"
                android:padding="3dp"
                android:src="@drawable/ic_key"
                app:tint="#94A3B8"
                android:contentDescription="Token" />
        </LinearLayout>

        <!-- Indikator Status Live Screen Share -->
        <TextView
            android:id="@+id/tvScreenShareStatus"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:background="#330EA5E9"
            android:paddingVertical="3dp"
            android:paddingHorizontal="12dp"
            android:text="Live Screen Share Aktif (AI melihat layar Anda)"
            android:textSize="10sp"
            android:textColor="#38BDF8"
            android:gravity="center"
            android:visibility="gone" />

        <!-- Panel Ubah Token di dalam Popup -->
        <LinearLayout
            android:id="@+id/tokenPanel"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:background="#CC1E293B"
            android:padding="8dp"
            android:visibility="gone">

            <EditText
                android:id="@+id/etPopupToken"
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:hint="Tempel Gemini API Key..."
                android:textColorHint="#64748B"
                android:textColor="#F8FAFC"
                android:textSize="12sp"
                android:inputType="textPassword"
                android:background="@android:color/transparent"
                android:padding="4dp" />

            <Button
                android:id="@+id/btnSavePopupToken"
                android:layout_width="wrap_content"
                android:layout_height="34dp"
                android:text="Simpan"
                android:textSize="11sp"
                android:backgroundTint="#2563EB"
                android:textColor="#FFFFFF" />
        </LinearLayout>

        <!-- Area Percakapan (Chat Kiri untuk Bot, Chat Kanan untuk User) -->
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

        <!-- Input Pesan & Tombol Kirim SVG -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:padding="10dp">

            <EditText
                android:id="@+id/etPrompt"
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:hint="Tanya inti masalah..."
                android:textColorHint="#94A3B8"
                android:textColor="#F8FAFC"
                android:textSize="13sp"
                android:maxLines="3"
                android:paddingHorizontal="12dp"
                android:paddingVertical="9dp"
                android:background="@drawable/bg_input_glass" />

            <ImageButton
                android:id="@+id/btnSendPrompt"
                android:layout_width="40dp"
                android:layout_height="40dp"
                android:layout_marginStart="8dp"
                android:background="@drawable/bg_send_btn"
                android:src="@drawable/ic_send"
                app:tint="#FFFFFF"
                android:contentDescription="Kirim" />
        </LinearLayout>

    </LinearLayout>
</FrameLayout>
""",

    # 7. DRAWABLE RESOURCES & CUSTOM SVG ICONS
    "app/src/main/res/drawable/bg_bubble.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="oval">
    <solid android:color="#D90F172A" />
    <stroke android:width="1.5dp" android:color="#38BDF8" />
</shape>
""",

    "app/src/main/res/drawable/bg_popup_glass.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#CC0F172A" />
    <corners android:radius="18dp" />
    <stroke android:width="1dp" android:color="#475569" />
</shape>
""",

    "app/src/main/res/drawable/bg_mac_header.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#E61E293B" />
    <corners android:topLeftRadius="18dp" android:topRightRadius="18dp" />
</shape>
""",

    "app/src/main/res/drawable/dot_mac_red.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <solid android:color="#FF5F56" />
</shape>
""",

    "app/src/main/res/drawable/dot_mac_yellow.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <solid android:color="#FFBD2E" />
</shape>
""",

    "app/src/main/res/drawable/dot_mac_green.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <solid android:color="#27C93F" />
</shape>
""",

    "app/src/main/res/drawable/bg_input_glass.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#991E293B" />
    <corners android:radius="14dp" />
    <stroke android:width="1dp" android:color="#334155" />
</shape>
""",

    "app/src/main/res/drawable/bg_send_btn.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="oval">
    <solid android:color="#2563EB" />
</shape>
""",

    "app/src/main/res/drawable/bg_chat_user.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#D92563EB" />
    <corners android:topLeftRadius="14dp" android:topRightRadius="14dp" android:bottomLeftRadius="14dp" android:bottomRightRadius="4dp" />
</shape>
""",

    "app/src/main/res/drawable/bg_chat_bot.xml": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#CC1E293B" />
    <corners android:topLeftRadius="14dp" android:topRightRadius="14dp" android:bottomRightRadius="14dp" android:bottomLeftRadius="4dp" />
    <stroke android:width="1dp" android:color="#334155" />
</shape>
""",

    # CUSTOM SVG VECTOR ICONS
    "app/src/main/res/drawable/ic_sparkle.xml": """<?xml version="1.0" encoding="utf-8"?>
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

    "app/src/main/res/drawable/ic_key.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M12.65,10C11.83,7.67 9.61,6 7,6C3.69,6 1,8.69 1,12C1,15.31 3.69,18 7,18C9.61,18 11.83,16.33 12.65,14H17V18H21V14H23V10H12.65ZM7,14C5.9,14 5,13.1 5,12C5,10.9 5.9,10 7,10C8.1,10 9,10.9 9,12C9,13.1 8.1,14 7,14Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_send.xml": """<?xml version="1.0" encoding="utf-8"?>
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

    "app/src/main/res/drawable/ic_screen_share.xml": """<?xml version="1.0" encoding="utf-8"?>
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

    # 8. KODE KOTLIN: MAIN ACTIVITY
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

        etApiKey.setText(prefs.getString("api_key", ""))

        btnSaveToken.setOnClickListener {
            val token = etApiKey.text.toString().trim()
            if (token.isEmpty()) {
                Toast.makeText(this, "Token tidak boleh kosong", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            prefs.edit().putString("api_key", token).apply()
            Toast.makeText(this, "Token Gemini tersimpan", Toast.LENGTH_SHORT).show()
        }

        btnStartOverlay.setOnClickListener {
            if (!Settings.canDrawOverlays(this)) {
                Toast.makeText(this, "Aktifkan izin tampil di atas aplikasi lain", Toast.LENGTH_LONG).show()
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
            Toast.makeText(this, "Bubble AI aktif di layar", Toast.LENGTH_SHORT).show()
        }

        btnStopOverlay.setOnClickListener {
            stopService(Intent(this, FloatingAssistantService::class.java))
            Toast.makeText(this, "Bubble AI dinonaktifkan", Toast.LENGTH_SHORT).show()
        }
    }
}
""",

    # 9. ACTIVITY IZIN LIVE SCREEN SHARE (MEDIA PROJECTION)
    "app/src/main/java/com/example/floatinggeminiai/ScreenCapturePermissionActivity.kt": """package com.example.floatinggeminiai

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

    # 10. FLOATING SERVICE: MAC OS WINDOW, AUTO-FADE 3 DETIK, CHAT KIRI-KANAN, & LIVE SCREEN SHARE
    "app/src/main/java/com/example/floatinggeminiai/FloatingAssistantService.kt": """package com.example.floatinggeminiai

import android.app.Activity
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.graphics.Bitmap
import android.graphics.Color
import android.graphics.PixelFormat
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.media.ImageReader
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.util.Base64
import android.util.DisplayMetrics
import android.view.Gravity
import android.view.LayoutInflater
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
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
import java.io.ByteArrayOutputStream
import java.util.concurrent.TimeUnit
import kotlin.math.abs

class FloatingAssistantService : Service() {

    companion object {
        const val ACTION_SCREEN_CAPTURE_RESULT = "ACTION_SCREEN_CAPTURE_RESULT"
    }

    private lateinit var windowManager: WindowManager
    private lateinit var floatingView: View
    private lateinit var params: WindowManager.LayoutParams
    private val serviceJob = Job()
    private val serviceScope = CoroutineScope(Dispatchers.Main + serviceJob)

    // Handler untuk auto-fade bubble setelah 3 detik di-minimize
    private val fadeHandler = Handler(Looper.getMainLooper())
    private var isBubbleFaded = false
    private lateinit var bubbleView: FrameLayout
    private lateinit var popupChatView: LinearLayout
    private lateinit var btnScreenShare: ImageView
    private lateinit var tvScreenShareStatus: TextView

    // MediaProjection untuk Live Screen Share
    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    private var isScreenShareActive = false
    private var screenWidth = 720
    private var screenHeight = 1280
    private var screenDensity = 320

    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    private val fadeOutRunnable = Runnable {
        if (bubbleView.visibility == View.VISIBLE) {
            bubbleView.animate()
                .alpha(0.02f) // Memudar hingga nyaris tak terlihat namun tetap bisa diketuk di tempat terakhir
                .setDuration(600)
                .withEndAction { isBubbleFaded = true }
                .start()
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        startForegroundNotification(withMediaProjection = false)
        setupScreenMetrics()
        setupFloatingOverlay()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_SCREEN_CAPTURE_RESULT) {
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
                Toast.makeText(this, "Izin Live Screen Share dibatalkan", Toast.LENGTH_SHORT).show()
            }
        }
        return START_STICKY
    }

    private fun startForegroundNotification(withMediaProjection: Boolean) {
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
            .setContentTitle("Gemini AI Overlay")
            .setContentText(if (withMediaProjection) "Live Screen Share aktif" else "Asisten mengambang aktif")
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
        // Perkecil resolusi tangkapan layar agar hemat memori dan cepat dikirim ke AI
        screenWidth = metrics.widthPixels / 2
        screenHeight = metrics.heightPixels / 2
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
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 40
            y = 240
        }

        windowManager.addView(floatingView, params)

        bubbleView = floatingView.findViewById(R.id.bubbleView)
        popupChatView = floatingView.findViewById(R.id.popupChatView)
        val macTitleBar = floatingView.findViewById<LinearLayout>(R.id.macTitleBar)
        val btnMacClose = floatingView.findViewById<View>(R.id.btnMacClose)
        val btnMacMinimize = floatingView.findViewById<View>(R.id.btnMacMinimize)
        btnScreenShare = floatingView.findViewById(R.id.btnScreenShare)
        tvScreenShareStatus = floatingView.findViewById(R.id.tvScreenShareStatus)
        val btnToggleTokenPanel = floatingView.findViewById<ImageView>(R.id.btnToggleTokenPanel)
        val tokenPanel = floatingView.findViewById<LinearLayout>(R.id.tokenPanel)
        val etPopupToken = floatingView.findViewById<EditText>(R.id.etPopupToken)
        val btnSavePopupToken = floatingView.findViewById<Button>(R.id.btnSavePopupToken)
        val scrollChat = floatingView.findViewById<ScrollView>(R.id.scrollChat)
        val chatContainer = floatingView.findViewById<LinearLayout>(R.id.chatContainer)
        val etPrompt = floatingView.findViewById<EditText>(R.id.etPrompt)
        val btnSendPrompt = floatingView.findViewById<ImageButton>(R.id.btnSendPrompt)

        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        etPopupToken.setText(prefs.getString("api_key", ""))

        // Pesan sambutan awal di sisi kiri (Bot)
        addChatMessage(chatContainer, scrollChat, "Halo, ada yang bisa dibantu?", isUser = false)

        // Mulai hitung mundur 3 detik untuk memudarkan bubble
        scheduleBubbleFadeOut()

        // Interaksi pada Bubble (Geser, Munculkan kembali jika memudar, atau Buka Popup)
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
                        if (!isBubbleFaded) {
                            params.x = initialX + (event.rawX - initialTouchX).toInt()
                            params.y = initialY + (event.rawY - initialTouchY).toInt()
                            windowManager.updateViewLayout(floatingView, params)
                        }
                        return true
                    }
                    MotionEvent.ACTION_UP -> {
                        val diffX = abs(event.rawX - initialTouchX)
                        val diffY = abs(event.rawY - initialTouchY)
                        if (diffX < 15 && diffY < 15) {
                            if (isBubbleFaded) {
                                // Ketuk di tempat terakhir terlihat -> munculkan ikon kembali!
                                revealBubble()
                            } else {
                                // Jika ikon sudah terlihat -> buka popup chat
                                openPopupChat()
                            }
                        }
                        return true
                    }
                }
                return false
            }
        })

        // Fitur Geser Jendela Popup lewat macOS Top Bar
        macTitleBar.setOnTouchListener(object : View.OnTouchListener {
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
                }
                return false
            }
        })

        // Tombol Merah macOS: Tutup Assistant
        btnMacClose.setOnClickListener {
            stopSelf()
        }

        // Tombol Kuning macOS: Minimize ke Bubble (lalu memudar setelah 3 detik)
        btnMacMinimize.setOnClickListener {
            closePopupChat()
        }

        // Tombol Live Screen Share
        btnScreenShare.setOnClickListener {
            if (!isScreenShareActive) {
                val permIntent = Intent(this, ScreenCapturePermissionActivity::class.java).apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                }
                startActivity(permIntent)
            } else {
                stopMediaProjection()
                Toast.makeText(this, "Live Screen Share dihentikan", Toast.LENGTH_SHORT).show()
            }
        }

        // Toggle Panel Token
        btnToggleTokenPanel.setOnClickListener {
            tokenPanel.visibility = if (tokenPanel.visibility == View.VISIBLE) View.GONE else View.VISIBLE
        }

        btnSavePopupToken.setOnClickListener {
            val newToken = etPopupToken.text.toString().trim()
            if (newToken.isNotEmpty()) {
                prefs.edit().putString("api_key", newToken).apply()
                tokenPanel.visibility = View.GONE
                Toast.makeText(this, "Token disimpan", Toast.LENGTH_SHORT).show()
            }
        }

        // Kirim Pertanyaan
        btnSendPrompt.setOnClickListener {
            val prompt = etPrompt.text.toString().trim()
            val apiKey = prefs.getString("api_key", "") ?: ""

            if (prompt.isEmpty()) return@setOnClickListener
            if (apiKey.isEmpty()) {
                tokenPanel.visibility = View.VISIBLE
                Toast.makeText(this, "Masukkan Gemini API Token dulu", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            // Tambahkan bubble chat User di sebelah KANAN
            addChatMessage(chatContainer, scrollChat, prompt, isUser = true)
            etPrompt.text.clear()
            btnSendPrompt.isEnabled = false

            // Ambil tangkapan layar saat ini jika Live Screen Share aktif
            val screenBase64 = if (isScreenShareActive) captureCurrentScreenBase64() else null

            serviceScope.launch {
                val rawReply = callGeminiApi(apiKey, prompt, screenBase64)
                val cleanReply = sanitizeMarkdown(rawReply)
                // Tambahkan bubble chat Bot di sebelah KIRI
                addChatMessage(chatContainer, scrollChat, cleanReply, isUser = false)
                btnSendPrompt.isEnabled = true
            }
        }
    }

    private fun scheduleBubbleFadeOut() {
        fadeHandler.removeCallbacks(fadeOutRunnable)
        fadeHandler.postDelayed(fadeOutRunnable, 3000)
    }

    private fun revealBubble() {
        fadeHandler.removeCallbacks(fadeOutRunnable)
        isBubbleFaded = false
        bubbleView.animate()
            .alpha(1.0f)
            .setDuration(250)
            .withEndAction { scheduleBubbleFadeOut() }
            .start()
    }

    private fun openPopupChat() {
        fadeHandler.removeCallbacks(fadeOutRunnable)
        isBubbleFaded = false
        bubbleView.alpha = 1.0f
        bubbleView.visibility = View.GONE
        popupChatView.visibility = View.VISIBLE
        params.flags = WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL
        windowManager.updateViewLayout(floatingView, params)
    }

    private fun closePopupChat() {
        popupChatView.visibility = View.GONE
        bubbleView.visibility = View.VISIBLE
        bubbleView.alpha = 1.0f
        isBubbleFaded = false
        params.flags = WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
        windowManager.updateViewLayout(floatingView, params)
        // Mulai timer 3 detik untuk memudar dan hilang
        scheduleBubbleFadeOut()
    }

    private fun addChatMessage(container: LinearLayout, scrollView: ScrollView, text: String, isUser: Boolean) {
        val wrapper = LinearLayout(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                setMargins(0, 6, 0, 6)
            }
            gravity = if (isUser) Gravity.END else Gravity.START
        }

        val tvMessage = TextView(this).apply {
            this.text = text
            textSize = 13f
            setTextColor(Color.parseColor("#F8FAFC"))
            setPadding(28, 18, 28, 18)
            maxWidth = (240 * resources.displayMetrics.density).toInt()
            setBackgroundResource(if (isUser) R.drawable.bg_chat_user else R.drawable.bg_chat_bot)
        }

        wrapper.addView(tvMessage)
        container.addView(wrapper)
        scrollView.post { scrollView.fullScroll(View.FOCUS_DOWN) }
    }

    private fun sanitizeMarkdown(text: String): String {
        return text
            .replace("**", "")
            .replace("*", "")
            .replace("###", "")
            .replace("##", "")
            .replace("#", "")
            .trim()
    }

    private fun startMediaProjection(resultCode: Int, data: Intent) {
        startForegroundNotification(withMediaProjection = true)
        val projectionManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        mediaProjection = projectionManager.getMediaProjection(resultCode, data)

        imageReader = ImageReader.newInstance(screenWidth, screenHeight, PixelFormat.RGBA_8888, 2)
        virtualDisplay = mediaProjection?.createVirtualDisplay(
            "GeminiScreenShare",
            screenWidth,
            screenHeight,
            screenDensity,
            DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
            imageReader?.surface,
            null,
            null
        )

        isScreenShareActive = true
        btnScreenShare.setColorFilter(Color.parseColor("#38BDF8"))
        tvScreenShareStatus.visibility = View.VISIBLE
        Toast.makeText(this, "Live Screen Share aktif", Toast.LENGTH_SHORT).show()
    }

    private fun stopMediaProjection() {
        isScreenShareActive = false
        virtualDisplay?.release()
        imageReader?.close()
        mediaProjection?.stop()
        virtualDisplay = null
        imageReader = null
        mediaProjection = null
        btnScreenShare.setColorFilter(Color.parseColor("#94A3B8"))
        tvScreenShareStatus.visibility = View.GONE
        startForegroundNotification(withMediaProjection = false)
    }

    private fun captureCurrentScreenBase64(): String? {
        return try {
            val image = imageReader?.acquireLatestImage() ?: return null
            val planes = image.planes
            val buffer = planes[0].buffer
            val pixelStride = planes[0].pixelStride
            val rowStride = planes[0].rowStride
            val rowPadding = rowStride - pixelStride * screenWidth

            val bitmap = Bitmap.createBitmap(
                screenWidth + rowPadding / pixelStride,
                screenHeight,
                Bitmap.Config.ARGB_8888
            )
            bitmap.copyPixelsFromBuffer(buffer)
            image.close()

            val croppedBitmap = Bitmap.createBitmap(bitmap, 0, 0, screenWidth, screenHeight)
            val outputStream = ByteArrayOutputStream()
            croppedBitmap.compress(Bitmap.CompressFormat.JPEG, 65, outputStream)
            bitmap.recycle()
            croppedBitmap.recycle()

            Base64.encodeToString(outputStream.toByteArray(), Base64.NO_WRAP)
        } catch (e: Exception) {
            null
        }
    }

    private suspend fun callGeminiApi(apiKey: String, prompt: String, screenBase64: String?): String = withContext(Dispatchers.IO) {
        try {
            val url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key=$apiKey"

            val partsArray = JSONArray().apply {
                put(JSONObject().apply {
                    put("text", "Jawab dengan sangat singkat, padat, langsung ke inti pertanyaan tanpa basa-basi, dan JANGAN gunakan simbol markdown seperti tanda bintang (* atau **).\n\nPertanyaan: $prompt")
                })
                if (screenBase64 != null) {
                    put(JSONObject().apply {
                        put("inlineData", JSONObject().apply {
                            put("mimeType", "image/jpeg")
                            put("data", screenBase64)
                        })
                    })
                }
            }

            val jsonBody = JSONObject().apply {
                put("contents", JSONArray().apply {
                    put(JSONObject().apply {
                        put("parts", partsArray)
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
                    return@withContext "Error (${response.code}): Cek kembali API Token Anda."
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
                return@withContext "Respons kosong dari AI."
            }
        } catch (e: Exception) {
            return@withContext "Gagal terhubung: ${e.localizedMessage}"
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        fadeHandler.removeCallbacks(fadeOutRunnable)
        stopMediaProjection()
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
