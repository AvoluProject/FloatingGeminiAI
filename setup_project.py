import os

# ==============================================================================
# GENERATOR PROYEK ANDROID: GEMINI FLOATING PRO (MAJOR UPDATE EDITION)
# ==============================================================================
# Fitur Utama:
# 1. Xiaomi HyperOS Edge Pill + Magnetic Snap + Swipe/Tap Gesture & Vertical Drag
# 2. Jendela Mengambang Gaya macOS Translucent Glass + Corner Resize Handle
# 3. Persistent Multi-Turn Session Memory (Sesi Terus Jalan & Anti-Lupa Konteks)
# 4. Tombol Plus (+) Drawer: Ganti Model AI, Gaya Bicara, Token, Salin Sesi, Reset, & Quick Force Stop
# 5. Live Screen Share Real-Time (MediaProjection + ImageReader) + Quick Prompt Chips
# 6. Dashboard Pengaturan Pro + Tes Koneksi API Token + Custom Instruksi Pribadi
# 7. 100% Custom SVG Vector Icons (Tanpa Emoji) & Zero-Markdown Clean Output
# ==============================================================================

PROJECT_FILES = {
    # --------------------------------------------------------------------------
    # 1. GITHUB ACTIONS WORKFLOW (Gradle 8.5 + JDK 17)
    # --------------------------------------------------------------------------
    ".github/workflows/build_apk.yml": r"""name: Build Android Debug APK

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
rootProject.name = "FloatingGeminiAI"
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

android {
    namespace = "com.example.floatinggeminiai"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.floatinggeminiai"
        minSdk = 26
        targetSdk = 34
        versionCode = 4
        versionName = "3.0-Pro"
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

    # --------------------------------------------------------------------------
    # 4. ANDROID MANIFEST
    # --------------------------------------------------------------------------
    "app/src/main/AndroidManifest.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <application
        android:allowBackup="true"
        android:label="Gemini Floating Pro"
        android:supportsRtl="true"
        android:theme="@style/Theme.Material3.Dark.NoActionBar">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <activity
            android:name=".ScreenCapturePermissionActivity"
            android:exported="false"
            android:theme="@android:style/Theme.Translucent.NoTitleBar" />

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

    # --------------------------------------------------------------------------
    # 5. LAYOUT HALAMAN UTAMA (DASHBOARD PENGATURAN PRO)
    # --------------------------------------------------------------------------
    "app/src/main/res/layout/activity_main.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#060A12"
    android:fillViewport="true">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="20dp">

        <!-- HEADER APLIKASI -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:layout_marginTop="6dp"
            android:layout_marginBottom="18dp">

            <FrameLayout
                android:layout_width="48dp"
                android:layout_height="48dp"
                android:background="@drawable/bg_bubble">

                <ImageView
                    android:layout_width="24dp"
                    android:layout_height="24dp"
                    android:layout_gravity="center"
                    android:src="@drawable/ic_sparkle"
                    app:tint="#38BDF8" />
            </FrameLayout>

            <LinearLayout
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:layout_marginStart="14dp"
                android:orientation="vertical">

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Gemini Floating Pro"
                    android:textSize="21sp"
                    android:textStyle="bold"
                    android:textColor="#F8FAFC" />

                <TextView
                    android:id="@+id/tvDashboardSessionStatus"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Sesi Memori Aktif • Siap Digunakan"
                    android:textSize="12sp"
                    android:textColor="#38BDF8" />
            </LinearLayout>
        </LinearLayout>

        <!-- KARTU KONTROL UTAMA & QUICK FORCE STOP -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_card_dark"
            android:padding="16dp"
            android:layout_marginBottom="16dp">

            <Button
                android:id="@+id/btnStartOverlay"
                android:layout_width="match_parent"
                android:layout_height="54dp"
                android:text="Aktifkan Floating Assistant"
                android:textStyle="bold"
                android:textSize="14sp"
                app:icon="@drawable/ic_sparkle"
                app:iconGravity="textStart"
                app:iconTint="#060A12"
                android:backgroundTint="#38BDF8"
                android:textColor="#060A12" />

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginTop="10dp">

                <Button
                    android:id="@+id/btnStopOverlay"
                    android:layout_width="0dp"
                    android:layout_height="46dp"
                    android:layout_weight="1"
                    android:text="Hentikan"
                    android:textSize="12sp"
                    android:textColor="#CBD5E1"
                    app:strokeColor="#334155"
                    style="@style/Widget.Material3.Button.OutlinedButton" />

                <Button
                    android:id="@+id/btnQuickForceStopMain"
                    android:layout_width="0dp"
                    android:layout_height="46dp"
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

            <Button
                android:id="@+id/btnClearSessionMain"
                android:layout_width="match_parent"
                android:layout_height="40dp"
                android:layout_marginTop="8dp"
                android:text="Reset Memori Sesi Obrolan"
                android:textSize="12sp"
                android:textColor="#94A3B8"
                app:icon="@drawable/ic_trash"
                app:iconSize="15dp"
                app:iconTint="#94A3B8"
                style="@style/Widget.Material3.Button.TextButton" />
        </LinearLayout>

        <!-- KARTU PENGATURAN TOKEN, TES KONEKSI, MODEL, & KEPRIBADIAN AI -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_card_dark"
            android:padding="16dp"
            android:layout_marginBottom="16dp">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:gravity="center_vertical"
                android:layout_marginBottom="12dp">

                <ImageView
                    android:layout_width="18dp"
                    android:layout_height="18dp"
                    android:src="@drawable/ic_key"
                    app:tint="#38BDF8" />

                <TextView
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:layout_marginStart="8dp"
                    android:text="Koneksi &amp; Kepribadian AI"
                    android:textSize="15sp"
                    android:textStyle="bold"
                    android:textColor="#F8FAFC" />

                <Button
                    android:id="@+id/btnTestToken"
                    android:layout_width="wrap_content"
                    android:layout_height="34dp"
                    android:text="Tes Token"
                    android:textSize="11sp"
                    android:textColor="#38BDF8"
                    app:strokeColor="#1E3A8A"
                    style="@style/Widget.Material3.Button.OutlinedButton" />
            </LinearLayout>

            <com.google.android.material.textfield.TextInputLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="Gemini API Token"
                app:boxBackgroundColor="#0F172A"
                app:boxStrokeColor="#38BDF8"
                app:hintTextColor="#38BDF8"
                app:endIconMode="password_toggle"
                style="@style/Widget.Material3.TextInputLayout.OutlinedBox">

                <com.google.android.material.textfield.TextInputEditText
                    android:id="@+id/etApiKey"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:textColor="#F8FAFC"
                    android:textSize="13sp"
                    android:inputType="textPassword" />
            </com.google.android.material.textfield.TextInputLayout>

            <com.google.android.material.textfield.TextInputLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="10dp"
                android:hint="Catatan Pribadi / Panggilan (Opsional)"
                app:boxBackgroundColor="#0F172A"
                app:boxStrokeColor="#334155"
                app:hintTextColor="#94A3B8"
                style="@style/Widget.Material3.TextInputLayout.OutlinedBox">

                <com.google.android.material.textfield.TextInputEditText
                    android:id="@+id/etCustomPersonaNote"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:textColor="#F8FAFC"
                    android:textSize="12sp"
                    android:maxLines="2" />
            </com.google.android.material.textfield.TextInputLayout>

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="14dp"
                android:text="Gaya Bicara Gemini"
                android:textSize="12sp"
                android:textColor="#94A3B8" />

            <RadioGroup
                android:id="@+id/rgPersona"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginTop="6dp">

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
                    android:id="@+id/rbKreatif"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="Kreatif"
                    android:textSize="12sp"
                    android:textColor="#E2E8F0" />
            </RadioGroup>

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="10dp"
                android:text="Model Mesin Gemini"
                android:textSize="12sp"
                android:textColor="#94A3B8" />

            <RadioGroup
                android:id="@+id/rgModel"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginTop="6dp">

                <RadioButton
                    android:id="@+id/rbModel3Flash"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="3 Flash"
                    android:textSize="12sp"
                    android:textColor="#E2E8F0"
                    android:checked="true" />

                <RadioButton
                    android:id="@+id/rbModel25Flash"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="2.5 Flash"
                    android:textSize="12sp"
                    android:textColor="#E2E8F0" />

                <RadioButton
                    android:id="@+id/rbModel25Pro"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="2.5 Pro"
                    android:textSize="12sp"
                    android:textColor="#E2E8F0" />
            </RadioGroup>
        </LinearLayout>

        <!-- KARTU PENGATURAN XIAOMI EDGE PILL & MAC OS GLASS -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_card_dark"
            android:padding="16dp"
            android:layout_marginBottom="16dp">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:gravity="center_vertical"
                android:layout_marginBottom="12dp">

                <ImageView
                    android:layout_width="18dp"
                    android:layout_height="18dp"
                    android:src="@drawable/ic_edge_pill"
                    app:tint="#38BDF8" />

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginStart="8dp"
                    android:text="Xiaomi Edge Pill &amp; Jendela macOS"
                    android:textSize="15sp"
                    android:textStyle="bold"
                    android:textColor="#F8FAFC" />
            </LinearLayout>

            <com.google.android.material.switchmaterial.SwitchMaterial
                android:id="@+id/swMagneticSnap"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Tempel Otomatis ke Pinggir Layar (Magnetic Snap)"
                android:textColor="#E2E8F0"
                android:textSize="13sp"
                android:checked="true" />

            <com.google.android.material.switchmaterial.SwitchMaterial
                android:id="@+id/swXiaomiEdge"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="4dp"
                android:text="Garis Setengah Lingkaran Xiaomi (Edge Pill)"
                android:textColor="#E2E8F0"
                android:textSize="13sp"
                android:checked="true" />

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Saat dilepas ke tepi layar, bubble mengecil menjadi garis setengah lingkaran ala Xiaomi Sidebar. Ketuk atau geser ke dalam untuk membuka."
                android:textSize="11sp"
                android:textColor="#64748B"
                android:layout_marginBottom="12dp" />

            <TextView
                android:id="@+id/tvEdgeDelayLabel"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Jeda Berubah ke Garis Xiaomi: 3 Detik"
                android:textSize="12sp"
                android:textColor="#CBD5E1" />

            <SeekBar
                android:id="@+id/sbEdgeDelay"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:max="9"
                android:progress="2"
                android:layout_marginBottom="12dp" />

            <TextView
                android:id="@+id/tvOpacityLabel"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Transparansi Jendela Chat: 84%"
                android:textSize="12sp"
                android:textColor="#CBD5E1" />

            <SeekBar
                android:id="@+id/sbOpacity"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:max="55"
                android:progress="39"
                android:layout_marginBottom="12dp" />

            <TextView
                android:id="@+id/tvBubbleSizeLabel"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Ukuran Bubble Utama: 56dp"
                android:textSize="12sp"
                android:textColor="#CBD5E1" />

            <SeekBar
                android:id="@+id/sbBubbleSize"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:max="28"
                android:progress="12" />
        </LinearLayout>

        <Button
            android:id="@+id/btnSaveAllSettings"
            android:layout_width="match_parent"
            android:layout_height="52dp"
            android:text="Simpan &amp; Terapkan Pengaturan"
            android:textStyle="bold"
            android:backgroundTint="#2563EB"
            android:textColor="#FFFFFF"
            android:layout_marginBottom="24dp" />

    </LinearLayout>
</ScrollView>
""",

    # --------------------------------------------------------------------------
    # 6. LAYOUT OVERLAY: BUBBLE + XIAOMI EDGE PILL + MAC OS POPUP + PLUS DRAWER
    # --------------------------------------------------------------------------
    "app/src/main/res/layout/layout_floating_assistant.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content">

    <!-- 1A. BUBBLE UTAMA (LINGKARAN PENUH) -->
    <FrameLayout
        android:id="@+id/bubbleView"
        android:layout_width="56dp"
        android:layout_height="56dp"
        android:background="@drawable/bg_bubble"
        android:elevation="12dp">

        <ImageView
            android:layout_width="26dp"
            android:layout_height="26dp"
            android:layout_gravity="center"
            android:src="@drawable/ic_sparkle"
            app:tint="#38BDF8" />
    </FrameLayout>

    <!-- 1B. XIAOMI EDGE PILL (GARIS SETENGAH LINGKARAN DI PINGGIR LAYAR) -->
    <FrameLayout
        android:id="@+id/xiaomiEdgeView"
        android:layout_width="18dp"
        android:layout_height="72dp"
        android:background="@drawable/bg_xiaomi_edge_left"
        android:elevation="12dp"
        android:visibility="gone">

        <View
            android:layout_width="3dp"
            android:layout_height="36dp"
            android:layout_gravity="center"
            android:background="@drawable/bg_xiaomi_inner_line" />
    </FrameLayout>

    <!-- 2. POPUP CHAT GAYA MAC OS WINDOW (TRANSLUCENT GLASS + RESIZABLE) -->
    <LinearLayout
        android:id="@+id/popupChatView"
        android:layout_width="338dp"
        android:layout_height="470dp"
        android:orientation="vertical"
        android:background="@drawable/bg_popup_glass"
        android:elevation="18dp"
        android:visibility="gone">

        <!-- MAC OS TOP ACCESSORY BAR -->
        <LinearLayout
            android:id="@+id/macTitleBar"
            android:layout_width="match_parent"
            android:layout_height="40dp"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:paddingHorizontal="12dp"
            android:background="@drawable/bg_mac_header">

            <!-- Tombol Kontrol Ala macOS: Merah (Tutup), Kuning (Minimize ke Edge), Hijau (Expand) -->
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
                android:id="@+id/btnMacExpand"
                android:layout_width="13dp"
                android:layout_height="13dp"
                android:layout_marginStart="8dp"
                android:background="@drawable/dot_mac_green" />

            <LinearLayout
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:orientation="vertical"
                android:gravity="center">

                <TextView
                    android:id="@+id/tvMacWindowTitle"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Gemini AI"
                    android:textSize="12sp"
                    android:textStyle="bold"
                    android:textColor="#F8FAFC" />

                <TextView
                    android:id="@+id/tvSessionSubtitle"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="3 Flash • Sesi Aktif"
                    android:textSize="9sp"
                    android:textColor="#94A3B8" />
            </LinearLayout>

            <!-- Toggle Live Screen Share Langsung di Header -->
            <ImageView
                android:id="@+id/btnScreenShare"
                android:layout_width="26dp"
                android:layout_height="26dp"
                android:padding="4dp"
                android:src="@drawable/ic_screen_share"
                app:tint="#94A3B8"
                android:contentDescription="Live Screen Share" />

            <!-- TOMBOL PLUS (+) UNTUK MENU AKSI CEPAT & FORCE STOP -->
            <ImageView
                android:id="@+id/btnPlusMenu"
                android:layout_width="26dp"
                android:layout_height="26dp"
                android:layout_marginStart="6dp"
                android:padding="4dp"
                android:background="@drawable/bg_plus_btn"
                android:src="@drawable/ic_plus"
                app:tint="#38BDF8"
                android:contentDescription="Menu Plus" />
        </LinearLayout>

        <!-- Indikator Status Live Screen Share -->
        <TextView
            android:id="@+id/tvScreenShareStatus"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:background="#330EA5E9"
            android:paddingVertical="3dp"
            android:paddingHorizontal="12dp"
            android:text="Live Screen Share Aktif • AI Melihat Layar"
            android:textSize="10sp"
            android:textColor="#38BDF8"
            android:gravity="center"
            android:visibility="gone" />

        <!-- DRAWER MENU PLUS (+): TOKEN, GAYA AI, MODEL, COPY, RESET, & QUICK FORCE STOP -->
        <LinearLayout
            android:id="@+id/plusMenuDrawer"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="#EB1E293B"
            android:padding="10dp"
            android:visibility="gone">

            <!-- Baris 1: Token, Gaya AI, Model AI -->
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:gravity="center_vertical">

                <LinearLayout
                    android:id="@+id/actionToggleToken"
                    android:layout_width="0dp"
                    android:layout_height="34dp"
                    android:layout_weight="1"
                    android:gravity="center"
                    android:background="@drawable/bg_chip_action"
                    android:orientation="horizontal">

                    <ImageView
                        android:layout_width="13dp"
                        android:layout_height="13dp"
                        android:src="@drawable/ic_key"
                        app:tint="#38BDF8" />

                    <TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginStart="4dp"
                        android:text="Token"
                        android:textSize="11sp"
                        android:textColor="#F8FAFC" />
                </LinearLayout>

                <LinearLayout
                    android:id="@+id/actionCyclePersona"
                    android:layout_width="0dp"
                    android:layout_height="34dp"
                    android:layout_weight="1"
                    android:layout_marginStart="6dp"
                    android:gravity="center"
                    android:background="@drawable/bg_chip_action"
                    android:orientation="horizontal">

                    <ImageView
                        android:layout_width="13dp"
                        android:layout_height="13dp"
                        android:src="@drawable/ic_chat_style"
                        app:tint="#A78BFA" />

                    <TextView
                        android:id="@+id/tvCurrentPersonaBadge"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginStart="4dp"
                        android:text="Asik"
                        android:textSize="11sp"
                        android:textColor="#F8FAFC" />
                </LinearLayout>

                <LinearLayout
                    android:id="@+id/actionCycleModel"
                    android:layout_width="0dp"
                    android:layout_height="34dp"
                    android:layout_weight="1.1"
                    android:layout_marginStart="6dp"
                    android:gravity="center"
                    android:background="@drawable/bg_chip_action"
                    android:orientation="horizontal">

                    <ImageView
                        android:layout_width="13dp"
                        android:layout_height="13dp"
                        android:src="@drawable/ic_sparkle"
                        app:tint="#34D399" />

                    <TextView
                        android:id="@+id/tvCurrentModelBadge"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginStart="4dp"
                        android:text="3 Flash"
                        android:textSize="11sp"
                        android:textColor="#F8FAFC" />
                </LinearLayout>
            </LinearLayout>

            <!-- Baris 2: Salin Terakhir, Reset Sesi, Quick Force Stop -->
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginTop="6dp"
                android:gravity="center_vertical">

                <LinearLayout
                    android:id="@+id/actionCopyLast"
                    android:layout_width="0dp"
                    android:layout_height="34dp"
                    android:layout_weight="0.9"
                    android:gravity="center"
                    android:background="@drawable/bg_chip_action"
                    android:orientation="horizontal">

                    <ImageView
                        android:layout_width="13dp"
                        android:layout_height="13dp"
                        android:src="@drawable/ic_copy"
                        app:tint="#34D399" />

                    <TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginStart="4dp"
                        android:text="Salin"
                        android:textSize="11sp"
                        android:textColor="#F8FAFC" />
                </LinearLayout>

                <LinearLayout
                    android:id="@+id/actionResetChat"
                    android:layout_width="0dp"
                    android:layout_height="34dp"
                    android:layout_weight="1"
                    android:layout_marginStart="6dp"
                    android:gravity="center"
                    android:background="@drawable/bg_chip_action"
                    android:orientation="horizontal">

                    <ImageView
                        android:layout_width="13dp"
                        android:layout_height="13dp"
                        android:src="@drawable/ic_trash"
                        app:tint="#FBBF24" />

                    <TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginStart="4dp"
                        android:text="Reset Sesi"
                        android:textSize="11sp"
                        android:textColor="#F8FAFC" />
                </LinearLayout>

                <LinearLayout
                    android:id="@+id/actionQuickForceStop"
                    android:layout_width="0dp"
                    android:layout_height="34dp"
                    android:layout_weight="1.2"
                    android:layout_marginStart="6dp"
                    android:gravity="center"
                    android:background="@drawable/bg_chip_danger"
                    android:orientation="horizontal">

                    <ImageView
                        android:layout_width="13dp"
                        android:layout_height="13dp"
                        android:src="@drawable/ic_power_stop"
                        app:tint="#FCA5A5" />

                    <TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginStart="4dp"
                        android:text="Force Stop"
                        android:textSize="11sp"
                        android:textStyle="bold"
                        android:textColor="#FCA5A5" />
                </LinearLayout>
            </LinearLayout>

            <!-- Input Token Gemini di dalam Drawer -->
            <LinearLayout
                android:id="@+id/tokenInputRow"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginTop="8dp"
                android:background="@drawable/bg_input_glass"
                android:paddingHorizontal="8dp"
                android:paddingVertical="4dp"
                android:gravity="center_vertical"
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
                    android:layout_height="32dp"
                    android:text="Simpan"
                    android:textSize="11sp"
                    android:backgroundTint="#2563EB"
                    android:textColor="#FFFFFF" />
            </LinearLayout>
        </LinearLayout>

        <!-- AREA PERCAKAPAN (BOT DI KIRI, USER DI KANAN) -->
        <ScrollView
            android:id="@+id/scrollChat"
            android:layout_width="match_parent"
            android:layout_height="0dp"
            android:layout_weight="1"
            android:paddingHorizontal="10dp"
            android:paddingTop="8dp">

            <LinearLayout
                android:id="@+id/chatContainer"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical" />
        </ScrollView>

        <!-- QUICK PROMPT CHIPS BAR -->
        <HorizontalScrollView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:scrollbars="none"
            android:paddingHorizontal="10dp"
            android:paddingTop="4dp">

            <LinearLayout
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:orientation="horizontal">

                <TextView
                    android:id="@+id/chipScreenAnalyze"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Baca layar ini"
                    android:textSize="10sp"
                    android:textColor="#38BDF8"
                    android:background="@drawable/bg_quick_chip"
                    android:paddingHorizontal="10dp"
                    android:paddingVertical="5dp" />

                <TextView
                    android:id="@+id/chipSummarize"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginStart="6dp"
                    android:text="Ringkas"
                    android:textSize="10sp"
                    android:textColor="#CBD5E1"
                    android:background="@drawable/bg_quick_chip"
                    android:paddingHorizontal="10dp"
                    android:paddingVertical="5dp" />

                <TextView
                    android:id="@+id/chipTranslate"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginStart="6dp"
                    android:text="Terjemahin"
                    android:textSize="10sp"
                    android:textColor="#CBD5E1"
                    android:background="@drawable/bg_quick_chip"
                    android:paddingHorizontal="10dp"
                    android:paddingVertical="5dp" />

                <TextView
                    android:id="@+id/chipReplyHelp"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginStart="6dp"
                    android:text="Bantu bales chat"
                    android:textSize="10sp"
                    android:textColor="#CBD5E1"
                    android:background="@drawable/bg_quick_chip"
                    android:paddingHorizontal="10dp"
                    android:paddingVertical="5dp" />
            </LinearLayout>
        </HorizontalScrollView>

        <!-- INPUT PESAN, TOMBOL KIRIM, & CORNER RESIZE GRIP -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:paddingStart="10dp"
            android:paddingEnd="4dp"
            android:paddingVertical="8dp">

            <EditText
                android:id="@+id/etPrompt"
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:hint="Lanjut ngobrol atau tanya..."
                android:textColorHint="#94A3B8"
                android:textColor="#F8FAFC"
                android:textSize="13sp"
                android:maxLines="3"
                android:paddingHorizontal="12dp"
                android:paddingVertical="9dp"
                android:background="@drawable/bg_input_glass" />

            <ImageButton
                android:id="@+id/btnSendPrompt"
                android:layout_width="38dp"
                android:layout_height="38dp"
                android:layout_marginStart="8dp"
                android:background="@drawable/bg_send_btn"
                android:src="@drawable/ic_send"
                app:tint="#FFFFFF"
                android:contentDescription="Kirim" />

            <!-- Corner Resize Handle -->
            <ImageView
                android:id="@+id/btnResizeCorner"
                android:layout_width="18dp"
                android:layout_height="18dp"
                android:layout_gravity="bottom"
                android:layout_marginStart="2dp"
                android:src="@drawable/ic_resize_corner"
                app:tint="#64748B"
                android:contentDescription="Ubah Ukuran Jendela" />
        </LinearLayout>

    </LinearLayout>
</FrameLayout>
""",

    # --------------------------------------------------------------------------
    # 7. DRAWABLE RESOURCES (XIAOMI EDGE PILL, MAC OS GLASS, & CUSTOM SVG)
    # --------------------------------------------------------------------------
    "app/src/main/res/drawable/bg_card_dark.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#111827" />
    <corners android:radius="16dp" />
    <stroke android:width="1dp" android:color="#1E293B" />
</shape>
""",

    "app/src/main/res/drawable/bg_bubble.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="oval">
    <solid android:color="#EB0F172A" />
    <stroke android:width="1.5dp" android:color="#38BDF8" />
</shape>
""",

    "app/src/main/res/drawable/bg_xiaomi_edge_left.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#D90F172A" />
    <corners
        android:topLeftRadius="0dp"
        android:bottomLeftRadius="0dp"
        android:topRightRadius="36dp"
        android:bottomRightRadius="36dp" />
    <stroke android:width="1.2dp" android:color="#9938BDF8" />
</shape>
""",

    "app/src/main/res/drawable/bg_xiaomi_edge_right.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#D90F172A" />
    <corners
        android:topLeftRadius="36dp"
        android:bottomLeftRadius="36dp"
        android:topRightRadius="0dp"
        android:bottomRightRadius="0dp" />
    <stroke android:width="1.2dp" android:color="#9938BDF8" />
</shape>
""",

    "app/src/main/res/drawable/bg_xiaomi_inner_line.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#38BDF8" />
    <corners android:radius="2dp" />
</shape>
""",

    "app/src/main/res/drawable/bg_popup_glass.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#D60F172A" />
    <corners android:radius="18dp" />
    <stroke android:width="1dp" android:color="#475569" />
</shape>
""",

    "app/src/main/res/drawable/bg_mac_header.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#F01E293B" />
    <corners android:topLeftRadius="18dp" android:topRightRadius="18dp" />
</shape>
""",

    "app/src/main/res/drawable/dot_mac_red.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <solid android:color="#FF5F56" />
</shape>
""",

    "app/src/main/res/drawable/dot_mac_yellow.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <solid android:color="#FFBD2E" />
</shape>
""",

    "app/src/main/res/drawable/dot_mac_green.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <solid android:color="#27C93F" />
</shape>
""",

    "app/src/main/res/drawable/bg_plus_btn.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="oval">
    <solid android:color="#3338BDF8" />
</shape>
""",

    "app/src/main/res/drawable/bg_chip_action.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#0F172A" />
    <corners android:radius="10dp" />
    <stroke android:width="1dp" android:color="#334155" />
</shape>
""",

    "app/src/main/res/drawable/bg_quick_chip.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#B31E293B" />
    <corners android:radius="12dp" />
    <stroke android:width="1dp" android:color="#334155" />
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
    <solid android:color="#A61E293B" />
    <corners android:radius="14dp" />
    <stroke android:width="1dp" android:color="#334155" />
</shape>
""",

    "app/src/main/res/drawable/bg_send_btn.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="oval">
    <solid android:color="#2563EB" />
</shape>
""",

    "app/src/main/res/drawable/bg_chat_user.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#EB2563EB" />
    <corners android:topLeftRadius="14dp" android:topRightRadius="14dp" android:bottomLeftRadius="14dp" android:bottomRightRadius="4dp" />
</shape>
""",

    "app/src/main/res/drawable/bg_chat_bot.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#E01E293B" />
    <corners android:topLeftRadius="14dp" android:topRightRadius="14dp" android:bottomRightRadius="14dp" android:bottomLeftRadius="4dp" />
    <stroke android:width="1dp" android:color="#334155" />
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

    "app/src/main/res/drawable/ic_key.xml": r"""<?xml version="1.0" encoding="utf-8"?>
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

    "app/src/main/res/drawable/ic_trash.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M6,19C6,20.1 6.9,21 8,21H16C17.1,21 18,20.1 18,19V7H6V19ZM19,4H15.5L14.5,3H9.5L8.5,4H5V6H19V4Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_copy.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M16,1H4C2.9,1 2,1.9 2,3V17H4V3H16V1ZM19,5H8C6.9,5 6,5.9 6,7V21C6,22.1 6.9,23 8,23H19C20.1,23 21,22.1 21,21V7C21,5.9 20.1,5 19,5ZM19,21H8V7H19V21Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_chat_style.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M20,2H4C2.9,2 2,2.9 2,4V22L6,18H20C21.1,18 22,17.1 22,16V4C22,2.9 21.1,2 20,2ZM6,9H18V11H6V9ZM14,14H6V12H14V14ZM18,8H6V6H18V8Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_edge_pill.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M4,4H10C14.42,4 18,7.58 18,12C18,16.42 14.42,20 10,20H4V4ZM8,8V16H10C12.21,16 14,14.21 14,12C14,9.79 12.21,8 10,8H8Z" />
</vector>
""",

    "app/src/main/res/drawable/ic_resize_corner.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="18dp"
    android:height="18dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M22,22H20V20H22V22ZM22,18H20V16H22V18ZM18,22H16V20H18V22ZM18,18H16V16H18V18ZM14,22H12V20H14V22ZM22,14H20V12H22V14Z" />
</vector>
""",

    # --------------------------------------------------------------------------
    # 8. KODE KOTLIN: MAIN ACTIVITY (DASHBOARD PENGATURAN PRO + TES TOKEN)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/MainActivity.kt": r"""package com.example.floatinggeminiai

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.RadioButton
import android.widget.RadioGroup
import android.widget.SeekBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.switchmaterial.SwitchMaterial
import com.google.android.material.textfield.TextInputEditText
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.util.concurrent.TimeUnit
import kotlin.system.exitProcess

class MainActivity : AppCompatActivity() {

    private val testHttpClient = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .build()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)

        val tvDashboardSessionStatus = findViewById<TextView>(R.id.tvDashboardSessionStatus)
        val etApiKey = findViewById<TextInputEditText>(R.id.etApiKey)
        val etCustomPersonaNote = findViewById<TextInputEditText>(R.id.etCustomPersonaNote)
        val btnTestToken = findViewById<Button>(R.id.btnTestToken)
        val btnStartOverlay = findViewById<Button>(R.id.btnStartOverlay)
        val btnStopOverlay = findViewById<Button>(R.id.btnStopOverlay)
        val btnQuickForceStopMain = findViewById<Button>(R.id.btnQuickForceStopMain)
        val btnClearSessionMain = findViewById<Button>(R.id.btnClearSessionMain)
        val btnSaveAllSettings = findViewById<Button>(R.id.btnSaveAllSettings)

        val rgPersona = findViewById<RadioGroup>(R.id.rgPersona)
        val rbAsik = findViewById<RadioButton>(R.id.rbAsik)
        val rbRingkas = findViewById<RadioButton>(R.id.rbRingkas)
        val rbDetail = findViewById<RadioButton>(R.id.rbDetail)
        val rbKreatif = findViewById<RadioButton>(R.id.rbKreatif)

        val rgModel = findViewById<RadioGroup>(R.id.rgModel)
        val rbModel3Flash = findViewById<RadioButton>(R.id.rbModel3Flash)
        val rbModel25Flash = findViewById<RadioButton>(R.id.rbModel25Flash)
        val rbModel25Pro = findViewById<RadioButton>(R.id.rbModel25Pro)

        val swMagneticSnap = findViewById<SwitchMaterial>(R.id.swMagneticSnap)
        val swXiaomiEdge = findViewById<SwitchMaterial>(R.id.swXiaomiEdge)
        val tvEdgeDelayLabel = findViewById<TextView>(R.id.tvEdgeDelayLabel)
        val sbEdgeDelay = findViewById<SeekBar>(R.id.sbEdgeDelay)
        val tvOpacityLabel = findViewById<TextView>(R.id.tvOpacityLabel)
        val sbOpacity = findViewById<SeekBar>(R.id.sbOpacity)
        val tvBubbleSizeLabel = findViewById<TextView>(R.id.tvBubbleSizeLabel)
        val sbBubbleSize = findViewById<SeekBar>(R.id.sbBubbleSize)

        fun updateSessionBadge() {
            val raw = prefs.getString("session_history_json", null)
            val count = try {
                if (raw.isNullOrEmpty()) 0 else JSONArray(raw).length()
            } catch (_: Exception) { 0 }
            tvDashboardSessionStatus.text = if (count > 0) {
                "Sesi Memori Aktif • $count pesan tersimpan"
            } else {
                "Sesi Memori Baru • Siap Digunakan"
            }
        }

        updateSessionBadge()
        etApiKey.setText(prefs.getString("api_key", ""))
        etCustomPersonaNote.setText(prefs.getString("custom_persona_note", ""))

        when (prefs.getString("ai_persona", "asik")) {
            "ringkas" -> rbRingkas.isChecked = true
            "detail" -> rbDetail.isChecked = true
            "kreatif" -> rbKreatif.isChecked = true
            else -> rbAsik.isChecked = true
        }

        when (prefs.getString("ai_model", "gemini-3-flash-preview")) {
            "gemini-2.5-flash" -> rbModel25Flash.isChecked = true
            "gemini-2.5-pro" -> rbModel25Pro.isChecked = true
            else -> rbModel3Flash.isChecked = true
        }

        swMagneticSnap.isChecked = prefs.getBoolean("magnetic_snap", true)
        swXiaomiEdge.isChecked = prefs.getBoolean("xiaomi_edge", true)

        val savedDelaySec = prefs.getInt("edge_delay_sec", 3)
        sbEdgeDelay.progress = (savedDelaySec - 1).coerceIn(0, 9)
        tvEdgeDelayLabel.text = "Jeda Berubah ke Garis Xiaomi: ${savedDelaySec} Detik"

        val savedOpacity = prefs.getInt("popup_opacity", 84)
        sbOpacity.progress = (savedOpacity - 45).coerceIn(0, 55)
        tvOpacityLabel.text = "Transparansi Jendela Chat: ${savedOpacity}%"

        val savedBubbleSize = prefs.getInt("bubble_size_dp", 56)
        sbBubbleSize.progress = (savedBubbleSize - 44).coerceIn(0, 28)
        tvBubbleSizeLabel.text = "Ukuran Bubble Utama: ${savedBubbleSize}dp"

        sbEdgeDelay.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                tvEdgeDelayLabel.text = "Jeda Berubah ke Garis Xiaomi: ${progress + 1} Detik"
            }
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })

        sbOpacity.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                tvOpacityLabel.text = "Transparansi Jendela Chat: ${progress + 45}%"
            }
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })

        sbBubbleSize.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                tvBubbleSizeLabel.text = "Ukuran Bubble Utama: ${progress + 44}dp"
            }
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })

        fun saveAllPreferences() {
            val persona = when (rgPersona.checkedRadioButtonId) {
                R.id.rbRingkas -> "ringkas"
                R.id.rbDetail -> "detail"
                R.id.rbKreatif -> "kreatif"
                else -> "asik"
            }
            val model = when (rgModel.checkedRadioButtonId) {
                R.id.rbModel25Flash -> "gemini-2.5-flash"
                R.id.rbModel25Pro -> "gemini-2.5-pro"
                else -> "gemini-3-flash-preview"
            }
            prefs.edit()
                .putString("api_key", etApiKey.text.toString().trim())
                .putString("custom_persona_note", etCustomPersonaNote.text.toString().trim())
                .putString("ai_persona", persona)
                .putString("ai_model", model)
                .putBoolean("magnetic_snap", swMagneticSnap.isChecked)
                .putBoolean("xiaomi_edge", swXiaomiEdge.isChecked)
                .putInt("edge_delay_sec", sbEdgeDelay.progress + 1)
                .putInt("popup_opacity", sbOpacity.progress + 45)
                .putInt("bubble_size_dp", sbBubbleSize.progress + 44)
                .apply()

            try {
                val refreshIntent = Intent(this, FloatingAssistantService::class.java).apply {
                    action = FloatingAssistantService.ACTION_RELOAD_SETTINGS
                }
                startService(refreshIntent)
            } catch (_: Exception) {}
        }

        btnTestToken.setOnClickListener {
            val token = etApiKey.text.toString().trim()
            if (token.isEmpty()) {
                Toast.makeText(this, "Masukkan API Token terlebih dahulu", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            btnTestToken.isEnabled = false
            btnTestToken.text = "Menguji..."
            CoroutineScope(Dispatchers.IO).launch {
                val isValid = try {
                    val url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$token"
                    val body = JSONObject().apply {
                        put("contents", JSONArray().apply {
                            put(JSONObject().apply {
                                put("parts", JSONArray().apply {
                                    put(JSONObject().apply { put("text", "Halo") })
                                })
                            })
                        })
                    }.toString().toRequestBody("application/json; charset=utf-8".toMediaType())
                    val req = Request.Builder().url(url).post(body).build()
                    testHttpClient.newCall(req).execute().use { it.isSuccessful }
                } catch (_: Exception) { false }

                withContext(Dispatchers.Main) {
                    btnTestToken.isEnabled = true
                    btnTestToken.text = "Tes Token"
                    if (isValid) {
                        saveAllPreferences()
                        Toast.makeText(this@MainActivity, "Koneksi Berhasil! Token Gemini Valid", Toast.LENGTH_SHORT).show()
                    } else {
                        Toast.makeText(this@MainActivity, "Token tidak valid atau koneksi gagal", Toast.LENGTH_LONG).show()
                    }
                }
            }
        }

        btnSaveAllSettings.setOnClickListener {
            saveAllPreferences()
            Toast.makeText(this, "Semua pengaturan berhasil disimpan", Toast.LENGTH_SHORT).show()
        }

        btnClearSessionMain.setOnClickListener {
            prefs.edit().remove("session_history_json").apply()
            updateSessionBadge()
            try {
                val resetIntent = Intent(this, FloatingAssistantService::class.java).apply {
                    action = FloatingAssistantService.ACTION_RESET_SESSION
                }
                startService(resetIntent)
            } catch (_: Exception) {}
            Toast.makeText(this, "Memori sesi obrolan dibersihkan", Toast.LENGTH_SHORT).show()
        }

        btnStartOverlay.setOnClickListener {
            saveAllPreferences()
            if (!Settings.canDrawOverlays(this)) {
                Toast.makeText(this, "Izinkan tampil di atas aplikasi lain terlebih dahulu", Toast.LENGTH_LONG).show()
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
            Toast.makeText(this, "Floating Assistant aktif di layar", Toast.LENGTH_SHORT).show()
        }

        btnStopOverlay.setOnClickListener {
            stopService(Intent(this, FloatingAssistantService::class.java))
            Toast.makeText(this, "Floating Assistant dihentikan", Toast.LENGTH_SHORT).show()
        }

        btnQuickForceStopMain.setOnClickListener {
            stopService(Intent(this, FloatingAssistantService::class.java))
            val appInfoIntent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                data = Uri.parse("package:$packageName")
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            startActivity(appInfoIntent)
            finishAffinity()
            exitProcess(0)
        }
    }
}
""",

    # --------------------------------------------------------------------------
    # 9. ACTIVITY IZIN LIVE SCREEN SHARE (MEDIA PROJECTION)
    # --------------------------------------------------------------------------
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

    # --------------------------------------------------------------------------
    # 10. FLOATING ASSISTANT SERVICE (FULL FEATURE OVERLAY ENGINE)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/FloatingAssistantService.kt": r"""package com.example.floatinggeminiai

import android.animation.ValueAnimator
import android.app.Activity
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.ClipData
import android.content.ClipboardManager
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
import android.net.Uri
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.provider.Settings
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
import kotlin.system.exitProcess

class FloatingAssistantService : Service() {

    companion object {
        const val ACTION_SCREEN_CAPTURE_RESULT = "ACTION_SCREEN_CAPTURE_RESULT"
        const val ACTION_RELOAD_SETTINGS = "ACTION_RELOAD_SETTINGS"
        const val ACTION_RESET_SESSION = "ACTION_RESET_SESSION"
        private const val KEY_SESSION_HISTORY = "session_history_json"
    }

    private lateinit var windowManager: WindowManager
    private lateinit var floatingView: View
    private lateinit var params: WindowManager.LayoutParams
    private val serviceJob = Job()
    private val serviceScope = CoroutineScope(Dispatchers.Main + serviceJob)

    // Komponen UI Utama
    private lateinit var bubbleView: FrameLayout
    private lateinit var xiaomiEdgeView: FrameLayout
    private lateinit var popupChatView: LinearLayout
    private lateinit var btnScreenShare: ImageView
    private lateinit var tvScreenShareStatus: TextView
    private lateinit var tvSessionSubtitle: TextView
    private lateinit var tvCurrentPersonaBadge: TextView
    private lateinit var tvCurrentModelBadge: TextView
    private lateinit var chatContainerRef: LinearLayout
    private lateinit var scrollChatRef: ScrollView

    // State Posisi & Mode Xiaomi Edge
    private val edgeHandler = Handler(Looper.getMainLooper())
    private var isXiaomiEdgeModeActive = false
    private var snappedToRightEdge = false
    private var isWindowExpanded = false
    private var fullScreenWidth = 1080
    private var fullScreenHeight = 2400

    // Pengaturan Dinamis
    private var prefMagneticSnap = true
    private var prefXiaomiEdge = true
    private var prefEdgeDelayMs = 3000L
    private var prefPopupAlpha = 0.85f
    private var prefBubbleSizePx = 150
    private var prefPersona = "asik"
    private var prefModel = "gemini-3-flash-preview"
    private var prefCustomPersonaNote = ""

    // Memori Percakapan Sesi Berkelanjutan (Disimpan Permanen Hingga Reset Sesi)
    private val chatHistory = mutableListOf<Pair<String, String>>()
    private var lastBotReply = ""

    // MediaProjection untuk Live Screen Share
    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    private var isScreenShareActive = false
    private var captureWidth = 540
    private var captureHeight = 1200
    private var screenDensity = 320

    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    private val transformToXiaomiEdgeRunnable = Runnable {
        if (bubbleView.visibility == View.VISIBLE && prefXiaomiEdge) {
            enterXiaomiEdgeMode()
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        startForegroundNotification(withMediaProjection = false)
        setupScreenMetrics()
        loadUserPreferences()
        setupFloatingOverlay()
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
                    Toast.makeText(this, "Izin Live Screen Share dibatalkan", Toast.LENGTH_SHORT).show()
                }
            }
            ACTION_RELOAD_SETTINGS -> {
                loadUserPreferences()
                applyVisualPreferences()
            }
            ACTION_RESET_SESSION -> {
                if (::chatContainerRef.isInitialized && ::scrollChatRef.isInitialized) {
                    resetConversationSession(chatContainerRef, scrollChatRef)
                }
            }
        }
        return START_STICKY
    }

    private fun loadUserPreferences() {
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        prefMagneticSnap = prefs.getBoolean("magnetic_snap", true)
        prefXiaomiEdge = prefs.getBoolean("xiaomi_edge", true)
        prefEdgeDelayMs = (prefs.getInt("edge_delay_sec", 3) * 1000L)
        prefPopupAlpha = (prefs.getInt("popup_opacity", 84) / 100f).coerceIn(0.45f, 1.0f)
        val sizeDp = prefs.getInt("bubble_size_dp", 56)
        prefBubbleSizePx = (sizeDp * resources.displayMetrics.density).toInt()
        prefPersona = prefs.getString("ai_persona", "asik") ?: "asik"
        prefModel = prefs.getString("ai_model", "gemini-3-flash-preview") ?: "gemini-3-flash-preview"
        prefCustomPersonaNote = prefs.getString("custom_persona_note", "") ?: ""
    }

    private fun getShortModelName(): String {
        return when (prefModel) {
            "gemini-2.5-flash" -> "2.5 Flash"
            "gemini-2.5-pro" -> "2.5 Pro"
            else -> "3 Flash"
        }
    }

    private fun applyVisualPreferences() {
        if (::bubbleView.isInitialized) {
            val lp = bubbleView.layoutParams
            lp.width = prefBubbleSizePx
            lp.height = prefBubbleSizePx
            bubbleView.layoutParams = lp
        }
        if (::popupChatView.isInitialized) {
            popupChatView.alpha = prefPopupAlpha
        }
        if (::tvCurrentPersonaBadge.isInitialized) {
            tvCurrentPersonaBadge.text = when (prefPersona) {
                "ringkas" -> "Singkat"
                "detail" -> "Detail"
                "kreatif" -> "Kreatif"
                else -> "Asik"
            }
        }
        if (::tvCurrentModelBadge.isInitialized) {
            tvCurrentModelBadge.text = getShortModelName()
        }
        if (::tvSessionSubtitle.isInitialized) {
            val turns = chatHistory.size
            tvSessionSubtitle.text = "${getShortModelName()} • $turns pesan diingat"
        }
    }

    // ==========================================================================
    // PENYIMPANAN & PEMULIHAN MEMORI SESI BERKELANJUTAN
    // ==========================================================================
    private fun saveSessionHistory() {
        try {
            val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
            val jsonArray = JSONArray()
            for ((role, text) in chatHistory) {
                jsonArray.put(JSONObject().apply {
                    put("role", role)
                    put("text", text)
                })
            }
            prefs.edit().putString(KEY_SESSION_HISTORY, jsonArray.toString()).apply()
            applyVisualPreferences()
        } catch (_: Exception) {}
    }

    private fun restoreSessionHistory(chatContainer: LinearLayout, scrollView: ScrollView) {
        chatHistory.clear()
        chatContainer.removeAllViews()
        try {
            val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
            val rawJson = prefs.getString(KEY_SESSION_HISTORY, null)
            if (!rawJson.isNullOrEmpty()) {
                val jsonArray = JSONArray(rawJson)
                for (i in 0 until jsonArray.length()) {
                    val obj = jsonArray.getJSONObject(i)
                    val role = obj.optString("role", "user")
                    val text = obj.optString("text", "")
                    if (text.isNotEmpty()) {
                        chatHistory.add(Pair(role, text))
                        val isUser = (role == "user")
                        if (!isUser) lastBotReply = text
                        addChatMessage(chatContainer, scrollView, text, isUser = isUser)
                    }
                }
            }
        } catch (_: Exception) {}

        if (chatHistory.isEmpty()) {
            val greeting = "Hai! Sesi obrolan aktif dan aku bakal terus ingat semua topik yang kita bahas. Mau ngobrol atau tanya soal apa nih?"
            lastBotReply = greeting
            addChatMessage(chatContainer, scrollView, greeting, isUser = false)
        }
        applyVisualPreferences()
    }

    private fun resetConversationSession(chatContainer: LinearLayout, scrollView: ScrollView) {
        chatHistory.clear()
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        prefs.edit().remove(KEY_SESSION_HISTORY).apply()
        chatContainer.removeAllViews()
        val resetMsg = "Sesi obrolan sudah di-reset bersih. Yuk mulai bahas topik baru!"
        lastBotReply = resetMsg
        addChatMessage(chatContainer, scrollView, resetMsg, isUser = false)
        applyVisualPreferences()
    }

    private fun startForegroundNotification(withMediaProjection: Boolean) {
        val channelId = "floating_gemini_pro_channel"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Gemini Floating Pro",
                NotificationManager.IMPORTANCE_LOW
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }

        val notification: Notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("Gemini Floating Pro")
            .setContentText(if (withMediaProjection) "Live Screen Share aktif" else "Sesi AI aktif di atas layar")
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
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 0
            y = fullScreenHeight / 3
        }

        windowManager.addView(floatingView, params)

        bubbleView = floatingView.findViewById(R.id.bubbleView)
        xiaomiEdgeView = floatingView.findViewById(R.id.xiaomiEdgeView)
        popupChatView = floatingView.findViewById(R.id.popupChatView)

        val macTitleBar = floatingView.findViewById<LinearLayout>(R.id.macTitleBar)
        val btnMacClose = floatingView.findViewById<View>(R.id.btnMacClose)
        val btnMacMinimize = floatingView.findViewById<View>(R.id.btnMacMinimize)
        val btnMacExpand = floatingView.findViewById<View>(R.id.btnMacExpand)
        tvSessionSubtitle = floatingView.findViewById(R.id.tvSessionSubtitle)
        btnScreenShare = floatingView.findViewById(R.id.btnScreenShare)
        val btnPlusMenu = floatingView.findViewById<ImageView>(R.id.btnPlusMenu)
        val plusMenuDrawer = floatingView.findViewById<LinearLayout>(R.id.plusMenuDrawer)
        tvScreenShareStatus = floatingView.findViewById(R.id.tvScreenShareStatus)

        val actionToggleToken = floatingView.findViewById<LinearLayout>(R.id.actionToggleToken)
        val actionCyclePersona = floatingView.findViewById<LinearLayout>(R.id.actionCyclePersona)
        val actionCycleModel = floatingView.findViewById<LinearLayout>(R.id.actionCycleModel)
        val actionCopyLast = floatingView.findViewById<LinearLayout>(R.id.actionCopyLast)
        val actionResetChat = floatingView.findViewById<LinearLayout>(R.id.actionResetChat)
        val actionQuickForceStop = floatingView.findViewById<LinearLayout>(R.id.actionQuickForceStop)
        tvCurrentPersonaBadge = floatingView.findViewById(R.id.tvCurrentPersonaBadge)
        tvCurrentModelBadge = floatingView.findViewById(R.id.tvCurrentModelBadge)

        val tokenInputRow = floatingView.findViewById<LinearLayout>(R.id.tokenInputRow)
        val etPopupToken = floatingView.findViewById<EditText>(R.id.etPopupToken)
        val btnSavePopupToken = floatingView.findViewById<Button>(R.id.btnSavePopupToken)

        val scrollChat = floatingView.findViewById<ScrollView>(R.id.scrollChat)
        val chatContainer = floatingView.findViewById<LinearLayout>(R.id.chatContainer)
        chatContainerRef = chatContainer
        scrollChatRef = scrollChat

        val chipScreenAnalyze = floatingView.findViewById<TextView>(R.id.chipScreenAnalyze)
        val chipSummarize = floatingView.findViewById<TextView>(R.id.chipSummarize)
        val chipTranslate = floatingView.findViewById<TextView>(R.id.chipTranslate)
        val chipReplyHelp = floatingView.findViewById<TextView>(R.id.chipReplyHelp)

        val etPrompt = floatingView.findViewById<EditText>(R.id.etPrompt)
        val btnSendPrompt = floatingView.findViewById<ImageButton>(R.id.btnSendPrompt)
        val btnResizeCorner = floatingView.findViewById<ImageView>(R.id.btnResizeCorner)

        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        etPopupToken.setText(prefs.getString("api_key", ""))
        applyVisualPreferences()
        restoreSessionHistory(chatContainer, scrollChat)
        scheduleXiaomiEdgeTransform()

        // Fungsi Helper Kirim Pesan
        fun sendPromptMessage(userText: String) {
            val prompt = userText.trim()
            val apiKey = prefs.getString("api_key", "") ?: ""

            if (prompt.isEmpty()) return
            if (apiKey.isEmpty()) {
                plusMenuDrawer.visibility = View.VISIBLE
                tokenInputRow.visibility = View.VISIBLE
                btnPlusMenu.animate().rotation(45f).setDuration(200).start()
                Toast.makeText(this, "Isi Gemini API Token dulu ya", Toast.LENGTH_SHORT).show()
                return
            }

            if (plusMenuDrawer.visibility == View.VISIBLE) {
                plusMenuDrawer.visibility = View.GONE
                btnPlusMenu.animate().rotation(0f).setDuration(200).start()
            }

            addChatMessage(chatContainer, scrollChat, prompt, isUser = true)
            etPrompt.text.clear()
            btnSendPrompt.isEnabled = false

            val screenBase64 = if (isScreenShareActive) captureCurrentScreenBase64() else null
            val typingIndicator = addTypingIndicator(
                chatContainer,
                scrollChat,
                if (screenBase64 != null) "Lagi ngelihat layar & mikir..." else "Gemini lagi ngetik..."
            )

            serviceScope.launch {
                val rawReply = callGeminiApi(apiKey, prompt, screenBase64)
                chatContainer.removeView(typingIndicator)

                val cleanReply = sanitizeMarkdown(rawReply)
                lastBotReply = cleanReply

                chatHistory.add(Pair("user", prompt))
                chatHistory.add(Pair("model", cleanReply))
                if (chatHistory.size > 160) {
                    chatHistory.removeAt(0)
                    chatHistory.removeAt(0)
                }
                saveSessionHistory()

                addChatMessage(chatContainer, scrollChat, cleanReply, isUser = false)
                btnSendPrompt.isEnabled = true
            }
        }

        // ----------------------------------------------------------------------
        // INTERAKSI BUBBLE UTAMA (GESER BEBAS + MAGNETIC SNAP KE PINGGIR LAYAR)
        // ----------------------------------------------------------------------
        bubbleView.setOnTouchListener(object : View.OnTouchListener {
            private var initialX = 0
            private var initialY = 0
            private var initialTouchX = 0f
            private var initialTouchY = 0f

            override fun onTouch(v: View, event: MotionEvent): Boolean {
                when (event.action) {
                    MotionEvent.ACTION_DOWN -> {
                        edgeHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
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
                        val diffX = abs(event.rawX - initialTouchX)
                        val diffY = abs(event.rawY - initialTouchY)
                        if (diffX < 15 && diffY < 15) {
                            openPopupChat()
                        } else {
                            if (prefMagneticSnap) {
                                snapBubbleToNearestEdge()
                            } else {
                                scheduleXiaomiEdgeTransform()
                            }
                        }
                        return true
                    }
                }
                return false
            }
        })

        // ----------------------------------------------------------------------
        // INTERAKSI XIAOMI EDGE PILL (KETUK ATAU GESER KE DALAM UNTUK MEMBUKA)
        // ----------------------------------------------------------------------
        xiaomiEdgeView.setOnTouchListener(object : View.OnTouchListener {
            private var initialY = 0
            private var initialTouchX = 0f
            private var initialTouchY = 0f

            override fun onTouch(v: View, event: MotionEvent): Boolean {
                when (event.action) {
                    MotionEvent.ACTION_DOWN -> {
                        initialY = params.y
                        initialTouchX = event.rawX
                        initialTouchY = event.rawY
                        return true
                    }
                    MotionEvent.ACTION_MOVE -> {
                        params.y = (initialY + (event.rawY - initialTouchY).toInt()).coerceIn(0, fullScreenHeight - 190)
                        windowManager.updateViewLayout(floatingView, params)
                        return true
                    }
                    MotionEvent.ACTION_UP -> {
                        val diffX = event.rawX - initialTouchX
                        val absX = abs(diffX)
                        val absY = abs(event.rawY - initialTouchY)
                        val swipedInward = (!snappedToRightEdge && diffX > 35) || (snappedToRightEdge && diffX < -35)
                        if (swipedInward) {
                            openPopupChat()
                        } else if (absX < 25 && absY < 25) {
                            exitXiaomiEdgeMode()
                        }
                        return true
                    }
                }
                return false
            }
        })

        // ----------------------------------------------------------------------
        // GESER JENDELA POPUP MAC OS KE MANA SAJA DI LAYAR
        // ----------------------------------------------------------------------
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
                        val maxW = (fullScreenWidth - popupChatView.width).coerceAtLeast(0)
                        val maxH = (fullScreenHeight - popupChatView.height).coerceAtLeast(0)
                        params.x = (initialX + (event.rawX - initialTouchX).toInt()).coerceIn(0, maxW)
                        params.y = (initialY + (event.rawY - initialTouchY).toInt()).coerceIn(0, maxH)
                        windowManager.updateViewLayout(floatingView, params)
                        return true
                    }
                }
                return false
            }
        })

        // ----------------------------------------------------------------------
        // CORNER RESIZE HANDLE (UBAH UKURAN JENDELA BEBAS DARI POJOK KANAN BAWAH)
        // ----------------------------------------------------------------------
        btnResizeCorner.setOnTouchListener(object : View.OnTouchListener {
            private var initialW = 0
            private var initialH = 0
            private var initialTouchX = 0f
            private var initialTouchY = 0f

            override fun onTouch(v: View, event: MotionEvent): Boolean {
                val density = resources.displayMetrics.density
                val minW = (270 * density).toInt()
                val minH = (340 * density).toInt()
                val maxW = (fullScreenWidth * 0.95f).toInt()
                val maxH = (fullScreenHeight * 0.80f).toInt()

                when (event.action) {
                    MotionEvent.ACTION_DOWN -> {
                        initialW = popupChatView.width
                        initialH = popupChatView.height
                        initialTouchX = event.rawX
                        initialTouchY = event.rawY
                        return true
                    }
                    MotionEvent.ACTION_MOVE -> {
                        val lp = popupChatView.layoutParams
                        lp.width = (initialW + (event.rawX - initialTouchX).toInt()).coerceIn(minW, maxW)
                        lp.height = (initialH + (event.rawY - initialTouchY).toInt()).coerceIn(minH, maxH)
                        popupChatView.layoutParams = lp
                        windowManager.updateViewLayout(floatingView, params)
                        return true
                    }
                }
                return false
            }
        })

        btnMacClose.setOnClickListener {
            stopSelf()
        }

        btnMacMinimize.setOnClickListener {
            closePopupChat()
        }

        btnMacExpand.setOnClickListener {
            isWindowExpanded = !isWindowExpanded
            val lp = popupChatView.layoutParams
            val density = resources.displayMetrics.density
            if (isWindowExpanded) {
                lp.width = (fullScreenWidth * 0.92f).toInt()
                lp.height = (fullScreenHeight * 0.68f).toInt()
            } else {
                lp.width = (338 * density).toInt()
                lp.height = (470 * density).toInt()
            }
            popupChatView.layoutParams = lp
            windowManager.updateViewLayout(floatingView, params)
        }

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

        btnPlusMenu.setOnClickListener {
            val isVisible = plusMenuDrawer.visibility == View.VISIBLE
            plusMenuDrawer.visibility = if (isVisible) View.GONE else View.VISIBLE
            btnPlusMenu.animate().rotation(if (isVisible) 0f else 45f).setDuration(200).start()
        }

        actionToggleToken.setOnClickListener {
            tokenInputRow.visibility = if (tokenInputRow.visibility == View.VISIBLE) View.GONE else View.VISIBLE
        }

        btnSavePopupToken.setOnClickListener {
            val newToken = etPopupToken.text.toString().trim()
            if (newToken.isNotEmpty()) {
                prefs.edit().putString("api_key", newToken).apply()
                tokenInputRow.visibility = View.GONE
                Toast.makeText(this, "Token Gemini tersimpan", Toast.LENGTH_SHORT).show()
            }
        }

        actionCyclePersona.setOnClickListener {
            prefPersona = when (prefPersona) {
                "asik" -> "ringkas"
                "ringkas" -> "detail"
                "detail" -> "kreatif"
                else -> "asik"
            }
            prefs.edit().putString("ai_persona", prefPersona).apply()
            applyVisualPreferences()
            val label = when (prefPersona) {
                "ringkas" -> "Gaya: Singkat & Padat"
                "detail" -> "Gaya: Penjelasan Lengkap"
                "kreatif" -> "Gaya: Kreatif & Ekspresif"
                else -> "Gaya: Asik & Santai"
            }
            Toast.makeText(this, label, Toast.LENGTH_SHORT).show()
        }

        actionCycleModel.setOnClickListener {
            prefModel = when (prefModel) {
                "gemini-3-flash-preview" -> "gemini-2.5-flash"
                "gemini-2.5-flash" -> "gemini-2.5-pro"
                else -> "gemini-3-flash-preview"
            }
            prefs.edit().putString("ai_model", prefModel).apply()
            applyVisualPreferences()
            Toast.makeText(this, "Model: ${getShortModelName()}", Toast.LENGTH_SHORT).show()
        }

        actionCopyLast.setOnClickListener {
            if (lastBotReply.isNotEmpty()) {
                val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                clipboard.setPrimaryClip(ClipData.newPlainText("Gemini Reply", lastBotReply))
                Toast.makeText(this, "Jawaban AI terakhir disalin", Toast.LENGTH_SHORT).show()
            }
        }

        actionResetChat.setOnClickListener {
            resetConversationSession(chatContainer, scrollChat)
            plusMenuDrawer.visibility = View.GONE
            btnPlusMenu.animate().rotation(0f).setDuration(200).start()
        }

        actionQuickForceStop.setOnClickListener {
            performQuickForceStop()
        }

        // Quick Prompt Chips
        chipScreenAnalyze.setOnClickListener {
            if (!isScreenShareActive) {
                Toast.makeText(this, "Aktifkan ikon Screen Share di pojok kanan atas dulu ya", Toast.LENGTH_SHORT).show()
            } else {
                sendPromptMessage("Coba lihat dan jelasin inti dari apa yang lagi tampil di layar aku sekarang.")
            }
        }

        chipSummarize.setOnClickListener {
            sendPromptMessage("Tolong ringkas inti pembahasan kita barusan jadi lebih gampang dipahami.")
        }

        chipTranslate.setOnClickListener {
            sendPromptMessage("Terjemahin teks atau pembahasan terakhir tadi ke bahasa Indonesia yang santai.")
        }

        chipReplyHelp.setOnClickListener {
            sendPromptMessage("Kasih saran balasan yang asik dan natural buat konteks obrolan atau layar ini.")
        }

        btnSendPrompt.setOnClickListener {
            sendPromptMessage(etPrompt.text.toString())
        }
    }

    // ==========================================================================
    // LOGIKA MAGNETIC EDGE SNAP & XIAOMI HALF-CIRCLE EDGE PILL
    // ==========================================================================
    private fun snapBubbleToNearestEdge() {
        val centerX = params.x + (prefBubbleSizePx / 2)
        snappedToRightEdge = centerX >= (fullScreenWidth / 2)
        val targetX = if (snappedToRightEdge) (fullScreenWidth - prefBubbleSizePx) else 0

        val animator = ValueAnimator.ofInt(params.x, targetX).apply {
            duration = 250
            interpolator = DecelerateInterpolator()
            addUpdateListener { anim ->
                params.x = anim.animatedValue as Int
                try {
                    windowManager.updateViewLayout(floatingView, params)
                } catch (_: Exception) {}
            }
        }
        animator.start()
        scheduleXiaomiEdgeTransform()
    }

    private fun scheduleXiaomiEdgeTransform() {
        edgeHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
        if (prefXiaomiEdge) {
            edgeHandler.postDelayed(transformToXiaomiEdgeRunnable, prefEdgeDelayMs)
        }
    }

    private fun enterXiaomiEdgeMode() {
        isXiaomiEdgeModeActive = true
        snappedToRightEdge = (params.x + prefBubbleSizePx / 2) >= (fullScreenWidth / 2)

        xiaomiEdgeView.setBackgroundResource(
            if (snappedToRightEdge) R.drawable.bg_xiaomi_edge_right else R.drawable.bg_xiaomi_edge_left
        )

        bubbleView.visibility = View.GONE
        xiaomiEdgeView.visibility = View.VISIBLE
        xiaomiEdgeView.alpha = 0.88f

        val pillWidthPx = (18 * resources.displayMetrics.density).toInt()
        params.x = if (snappedToRightEdge) (fullScreenWidth - pillWidthPx) else 0
        windowManager.updateViewLayout(floatingView, params)

        xiaomiEdgeView.animate()
            .alpha(0.48f)
            .setDuration(420)
            .start()
    }

    private fun exitXiaomiEdgeMode() {
        edgeHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
        isXiaomiEdgeModeActive = false
        xiaomiEdgeView.visibility = View.GONE
        bubbleView.visibility = View.VISIBLE
        bubbleView.alpha = 1.0f

        params.x = if (snappedToRightEdge) (fullScreenWidth - prefBubbleSizePx) else 0
        windowManager.updateViewLayout(floatingView, params)
        scheduleXiaomiEdgeTransform()
    }

    private fun openPopupChat() {
        edgeHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
        isXiaomiEdgeModeActive = false
        xiaomiEdgeView.visibility = View.GONE
        bubbleView.visibility = View.GONE
        popupChatView.visibility = View.VISIBLE
        popupChatView.alpha = prefPopupAlpha

        val popupW = (338 * resources.displayMetrics.density).toInt()
        val popupH = (470 * resources.displayMetrics.density).toInt()
        params.x = params.x.coerceIn(16, (fullScreenWidth - popupW - 16).coerceAtLeast(16))
        params.y = params.y.coerceIn(48, (fullScreenHeight - popupH - 48).coerceAtLeast(48))
        params.flags = WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL
        windowManager.updateViewLayout(floatingView, params)
    }

    private fun closePopupChat() {
        popupChatView.visibility = View.GONE
        xiaomiEdgeView.visibility = View.GONE
        bubbleView.visibility = View.VISIBLE
        bubbleView.alpha = 1.0f
        isXiaomiEdgeModeActive = false

        params.flags = WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
        params.x = if (snappedToRightEdge) (fullScreenWidth - prefBubbleSizePx) else 0
        windowManager.updateViewLayout(floatingView, params)

        if (prefMagneticSnap) {
            snapBubbleToNearestEdge()
        } else {
            scheduleXiaomiEdgeTransform()
        }
    }

    private fun performQuickForceStop() {
        Toast.makeText(this, "Menghentikan paksa layanan...", Toast.LENGTH_SHORT).show()
        stopMediaProjection()
        val appInfoIntent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
            data = Uri.parse("package:$packageName")
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        startActivity(appInfoIntent)
        stopSelf()
        exitProcess(0)
    }

    // ==========================================================================
    // TAMPILAN CHAT KIRI-KANAN (TEKAN LAMA UNTUK SALIN) & PEMBERSIH MARKDOWN
    // ==========================================================================
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
            lineHeight = (19 * resources.displayMetrics.density).toInt()
            setTextColor(Color.parseColor("#F8FAFC"))
            setPadding(28, 18, 28, 18)
            maxWidth = (248 * resources.displayMetrics.density).toInt()
            setBackgroundResource(if (isUser) R.drawable.bg_chat_user else R.drawable.bg_chat_bot)

            setOnLongClickListener {
                val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                clipboard.setPrimaryClip(ClipData.newPlainText("Chat Message", text))
                Toast.makeText(this@FloatingAssistantService, "Teks pesan disalin", Toast.LENGTH_SHORT).show()
                true
            }
        }

        wrapper.addView(tvMessage)
        container.addView(wrapper)
        scrollView.post { scrollView.fullScroll(View.FOCUS_DOWN) }
    }

    private fun addTypingIndicator(container: LinearLayout, scrollView: ScrollView, statusText: String): View {
        val wrapper = LinearLayout(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                setMargins(0, 6, 0, 6)
            }
            gravity = Gravity.START
        }

        val tvTyping = TextView(this).apply {
            this.text = statusText
            textSize = 12f
            setTextColor(Color.parseColor("#94A3B8"))
            setPadding(28, 16, 28, 16)
            setBackgroundResource(R.drawable.bg_chat_bot)
        }

        wrapper.addView(tvTyping)
        container.addView(wrapper)
        scrollView.post { scrollView.fullScroll(View.FOCUS_DOWN) }
        return wrapper
    }

    private fun sanitizeMarkdown(text: String): String {
        return text
            .replace("**", "")
            .replace("*", "")
            .replace("###", "")
            .replace("##", "")
            .replace("#", "")
            .replace("`", "")
            .trim()
    }

    // ==========================================================================
    // LIVE SCREEN SHARE (MEDIA PROJECTION + IMAGE READER)
    // ==========================================================================
    private fun startMediaProjection(resultCode: Int, data: Intent) {
        startForegroundNotification(withMediaProjection = true)
        val projectionManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        mediaProjection = projectionManager.getMediaProjection(resultCode, data)

        imageReader = ImageReader.newInstance(captureWidth, captureHeight, PixelFormat.RGBA_8888, 2)
        virtualDisplay = mediaProjection?.createVirtualDisplay(
            "GeminiScreenShare",
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
        if (::btnScreenShare.isInitialized) {
            btnScreenShare.setColorFilter(Color.parseColor("#94A3B8"))
        }
        if (::tvScreenShareStatus.isInitialized) {
            tvScreenShareStatus.visibility = View.GONE
        }
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

            val croppedBitmap = Bitmap.createBitmap(bitmap, 0, 0, captureWidth, captureHeight)
            val outputStream = ByteArrayOutputStream()
            croppedBitmap.compress(Bitmap.CompressFormat.JPEG, 65, outputStream)
            bitmap.recycle()
            croppedBitmap.recycle()

            Base64.encodeToString(outputStream.toByteArray(), Base64.NO_WRAP)
        } catch (e: Exception) {
            null
        }
    }

    // ==========================================================================
    // KONEKSI GEMINI API (INGAT KONTEKS SESI, GAYA ASIK, MINIMAL 1-3 KALIMAT)
    // ==========================================================================
    private fun buildSystemInstructionText(): String {
        val customNote = if (prefCustomPersonaNote.isNotEmpty()) {
            "Catatan tambahan dari pengguna tentang dirinya atau preferensinya: $prefCustomPersonaNote. "
        } else ""

        val memoryRule = "Penting: Selalu ingat dan hubungkan seluruh konteks percakapan sebelumnya dalam sesi ini agar obrolan terus nyambung dan tidak pernah lupa apa yang sedang dibahas."
        val formatRule = "Aturan format wajib: Jangan pernah gunakan simbol markdown seperti tanda bintang (* atau **), tanda pagar (#), atau backtick (`). Tulis dalam teks polos yang bersih dan rapi."

        return when (prefPersona) {
            "ringkas" -> "Kamu adalah asisten AI yang sigap dan langsung ke inti masalah. Jawab singkat dan padat dalam 1 sampai 2 kalimat utuh tanpa basa-basi. $customNote$memoryRule $formatRule"
            "detail" -> "Kamu adalah asisten AI yang ramah dan informatif. Jelaskan jawaban secara runtut dan jelas dalam beberapa kalimat yang mudah dipahami. $customNote$memoryRule $formatRule"
            "kreatif" -> "Kamu adalah asisten AI yang kreatif, ekspresif, dan seru diajak brainstorming. Berikan jawaban yang segar dalam 2 sampai 4 kalimat utuh. $customNote$memoryRule $formatRule"
            else -> "Kamu adalah asisten AI yang asik, santai, ramah, dan tidak kaku seperti teman ngobrol yang pintar. Gunakan bahasa Indonesia yang natural dan enak dibaca. Jawab cukup pendek tapi tetap jelas dan berisi, minimal 1 sampai 3 kalimat utuh yang langsung menjawab inti pertanyaan pengguna tanpa bertele-tele. $customNote$memoryRule $formatRule"
        }
    }

    private suspend fun callGeminiApi(apiKey: String, prompt: String, screenBase64: String?): String = withContext(Dispatchers.IO) {
        try {
            val url = "https://generativelanguage.googleapis.com/v1beta/models/$prefModel:generateContent?key=$apiKey"

            val contentsArray = JSONArray()

            // Kirim seluruh riwayat percakapan sesi aktif agar Gemini tidak pernah lupa konteks
            for ((role, text) in chatHistory) {
                contentsArray.put(JSONObject().apply {
                    put("role", role)
                    put("parts", JSONArray().apply {
                        put(JSONObject().apply { put("text", text) })
                    })
                })
            }

            val currentParts = JSONArray().apply {
                put(JSONObject().apply { put("text", prompt) })
                if (screenBase64 != null) {
                    put(JSONObject().apply {
                        put("inlineData", JSONObject().apply {
                            put("mimeType", "image/jpeg")
                            put("data", screenBase64)
                        })
                    })
                }
            }

            contentsArray.put(JSONObject().apply {
                put("role", "user")
                put("parts", currentParts)
            })

            val jsonBody = JSONObject().apply {
                put("systemInstruction", JSONObject().apply {
                    put("parts", JSONArray().apply {
                        put(JSONObject().apply {
                            put("text", buildSystemInstructionText())
                        })
                    })
                })
                put("contents", contentsArray)
            }

            val requestBody = jsonBody.toString().toRequestBody("application/json; charset=utf-8".toMediaType())
            val request = Request.Builder()
                .url(url)
                .post(requestBody)
                .build()

            httpClient.newCall(request).execute().use { response ->
                val responseString = response.body?.string() ?: ""
                if (!response.isSuccessful) {
                    return@withContext "Waduh, gagal nyambung ke Gemini (Kode ${response.code}). Coba cek lagi API Token kamu di menu Plus ya."
                }
                val jsonResponse = JSONObject(responseString)
                val candidates = jsonResponse.optJSONArray("candidates")
                if (candidates != null && candidates.length() > 0) {
                    val content = candidates.getJSONObject(0).optJSONObject("content")
                    val parts = content?.optJSONArray("parts")
                    if (parts != null && parts.length() > 0) {
                        return@withContext parts.getJSONObject(0).optString("text", "Hmm, aku belum nemu jawabannya nih.")
                    }
                }
                return@withContext "Respons dari Gemini kosong, coba tanyakan sekali lagi ya."
            }
        } catch (e: Exception) {
            return@withContext "Koneksi terganggu nih: ${e.localizedMessage}"
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        edgeHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
        stopMediaProjection()
        serviceJob.cancel()
        if (::floatingView.isInitialized) {
            try {
                windowManager.removeView(floatingView)
            } catch (_: Exception) {}
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
    print("\nSeluruh proyek Android Gemini Floating Pro siap di-push ke GitHub!")

if __name__ == "__main__":
    generate_project()
