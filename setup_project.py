import os

# ==============================================================================
# SKRIP PEMBANGKIT PROYEK ANDROID: FLOAMINI v5.0
# (GENUINE LIQUID GLASS + CUSTOM PILL + SIRI CONTROL CENTER MODE + SMART FREEZE)
# ==============================================================================

PROJECT_FILES = {
    # --------------------------------------------------------------------------
    # 1. GITHUB ACTIONS WORKFLOW (Gradle 8.5 + Permanent Keystore + Auto Version)
    # --------------------------------------------------------------------------
    ".github/workflows/build_apk.yml": r"""name: Build Floamini APK

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
          name: Floamini-v5.0-update-ready
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
    # 3. KONFIGURASI GRADLE MODULE (:app) - SPRING PHYSICS + IN-PLACE UPDATE
    # --------------------------------------------------------------------------
    "app/build.gradle.kts": r"""plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

val ciRunNumber = System.getenv("GITHUB_RUN_NUMBER")?.toIntOrNull() ?: 0
val appVersionCode = 6 + ciRunNumber
val appVersionName = "5.0.$ciRunNumber"

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
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
}
""",

    # --------------------------------------------------------------------------
    # 4. ANDROID MANIFEST (OVERLAY + CONTROL CENTER TILE + SIRI TRIGGER)
    # --------------------------------------------------------------------------
    "app/src/main/AndroidManifest.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.VIBRATE" />
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <application
        android:allowBackup="true"
        android:label="Floamini"
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
            android:theme="@android:style/Theme.Translucent.NoTitleBar" />

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
                android:value="Floamini Liquid Glass AI Assistant" />
        </service>

    </application>
</manifest>
""",

    # --------------------------------------------------------------------------
    # 5. LAYOUT FIRST WELCOME SCREEN
    # --------------------------------------------------------------------------
    "app/src/main/res/layout/activity_welcome.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#04070F"
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
            android:paddingVertical="18dp">

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
                android:layout_marginTop="14dp"
                android:paddingHorizontal="12dp"
                android:paddingVertical="4dp"
                android:background="@drawable/bg_badge_pill"
                android:text="FLOAMINI • LIQUID GLASS &amp; SIRI MODE"
                android:textSize="10sp"
                android:textStyle="bold"
                android:textColor="#38BDF8" />

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="10dp"
                android:text="Selamat Datang di Floamini"
                android:textSize="24sp"
                android:textStyle="bold"
                android:textColor="#F8FAFC"
                android:gravity="center" />

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="6dp"
                android:text="Asisten AI melayang bergaya iOS 26 Liquid Glass dengan kustomisasi Dynamic Island, Mode Siri dari Control Center, serta Auto Smart Freeze hemat baterai."
                android:textSize="13sp"
                android:lineHeight="19dp"
                android:textColor="#94A3B8"
                android:gravity="center" />
        </LinearLayout>

        <!-- KARTU 1: PANDUAN & LINK GEMINI API KEY -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_liquid_glass_card"
            android:padding="18dp"
            android:layout_marginBottom="16dp">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:gravity="center_vertical">

                <FrameLayout
                    android:layout_width="32dp"
                    android:layout_height="32dp"
                    android:background="@drawable/bg_ios_icon_blue">

                    <ImageView
                        android:layout_width="17dp"
                        android:layout_height="17dp"
                        android:layout_gravity="center"
                        android:src="@drawable/ic_key"
                        app:tint="#FFFFFF" />
                </FrameLayout>

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginStart="10dp"
                    android:text="Cara Mendapatkan Gemini API Key"
                    android:textSize="16sp"
                    android:textStyle="bold"
                    android:textColor="#F8FAFC" />
            </LinearLayout>

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="12dp"
                android:text="1. Ketuk tombol Buka Google AI Studio di bawah ini.\n2. Masuk menggunakan akun Google Anda.\n3. Pilih Create API Key lalu salin kode yang diawali AIzaSy...\n4. Tempelkan API Key pada kolom di bawah dan tekan Tes Token."
                android:textSize="12.5sp"
                android:lineHeight="19dp"
                android:textColor="#CBD5E1" />

            <Button
                android:id="@+id/btnOpenAiStudio"
                android:layout_width="match_parent"
                android:layout_height="46dp"
                android:layout_marginTop="14dp"
                android:text="Buka Google AI Studio (aistudio.google.com)"
                android:textSize="12.5sp"
                android:textStyle="bold"
                app:icon="@drawable/ic_external_link"
                app:iconSize="16dp"
                app:iconGravity="textStart"
                app:iconTint="#38BDF8"
                android:backgroundTint="#1E293B"
                android:textColor="#38BDF8" />

            <com.google.android.material.textfield.TextInputLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="12dp"
                android:hint="Tempel Gemini API Key Anda di sini"
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
                    android:text="Tes Token"
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

        <!-- KARTU 2: HINT & FITUR BARU -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_liquid_glass_card"
            android:padding="18dp"
            android:layout_marginBottom="16dp">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:gravity="center_vertical">

                <FrameLayout
                    android:layout_width="32dp"
                    android:layout_height="32dp"
                    android:background="@drawable/bg_ios_icon_purple">

                    <ImageView
                        android:layout_width="17dp"
                        android:layout_height="17dp"
                        android:layout_gravity="center"
                        android:src="@drawable/ic_bolt"
                        app:tint="#FFFFFF" />
                </FrameLayout>

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginStart="10dp"
                    android:text="Hint &amp; Mode Interaksi Floamini"
                    android:textSize="16sp"
                    android:textStyle="bold"
                    android:textColor="#F8FAFC" />
            </LinearLayout>

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="12dp"
                android:text="• Mode Siri (Control Center): Saat dipilih, layar bersih tanpa ikon melayang apa pun. Tarik panel Control Center / Quick Settings HP Anda dan ketuk tombol Floamini AI untuk memunculkan aura cahaya pinggir layar khas Siri iOS!\n\n• Pil Dynamic Island Polos &amp; Auto-Hide: Anda bisa memilih tampilan pil polos hitam pekat yang menyatu dengan kamera depan, serta mengaktifkan Auto-Hide agar pil menghilang otomatis saat diam.\n\n• Auto Smart Freeze: Saat layar mati atau idle, Floamini otomatis membekukan animasi dan membebaskan memori agar baterai tetap irit."
                android:textSize="12.5sp"
                android:lineHeight="18.5dp"
                android:textColor="#CBD5E1" />
        </LinearLayout>

        <Button
            android:id="@+id/btnContinueToFloamini"
            android:layout_width="match_parent"
            android:layout_height="54dp"
            android:text="Mulai Gunakan Floamini"
            android:textStyle="bold"
            android:textSize="15sp"
            android:backgroundTint="#38BDF8"
            android:textColor="#04070F"
            android:layout_marginBottom="24dp" />

    </LinearLayout>
</ScrollView>
""",

    # --------------------------------------------------------------------------
    # 6. LAYOUT HALAMAN UTAMA (iOS 26 SETTINGS + SIRI CONTROL CENTER + FREEZE)
    # --------------------------------------------------------------------------
    "app/src/main/res/layout/activity_main.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#04070F"
    android:fillViewport="true">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="18dp">

        <!-- iOS LARGE TITLE HEADER -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:layout_marginTop="4dp"
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
                    android:text="Floamini"
                    android:textSize="24sp"
                    android:textStyle="bold"
                    android:textColor="#F8FAFC" />

                <TextView
                    android:id="@+id/tvAppVersionInfo"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Liquid Glass • Siri Aura • Smart Freeze"
                    android:textSize="11.5sp"
                    android:textColor="#94A3B8" />
            </LinearLayout>

            <Button
                android:id="@+id/btnOpenWelcomeGuide"
                android:layout_width="wrap_content"
                android:layout_height="38dp"
                android:text="Panduan"
                android:textSize="12sp"
                android:textColor="#38BDF8"
                app:strokeColor="#334155"
                style="@style/Widget.Material3.Button.OutlinedButton" />
        </LinearLayout>

        <!-- SECTION 1: KONTROL LAYANAN & CONTROL CENTER SHORTCUT -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="KONTROL &amp; SHORTCUT CONTROL CENTER"
            android:textSize="11sp"
            android:textStyle="bold"
            android:letterSpacing="0.06"
            android:textColor="#64748B"
            android:layout_marginStart="6dp"
            android:layout_marginBottom="6dp" />

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_liquid_glass_card"
            android:padding="16dp"
            android:layout_marginBottom="18dp">

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

            <!-- Tombol Tambah Shortcut ke Control Center (Quick Settings) -->
            <Button
                android:id="@+id/btnAddControlCenterTile"
                android:layout_width="match_parent"
                android:layout_height="46dp"
                android:layout_marginTop="10dp"
                android:text="Tambah Tombol ke Control Center"
                android:textSize="12.5sp"
                android:textStyle="bold"
                app:icon="@drawable/ic_siri_orb"
                app:iconSize="18dp"
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
                    android:layout_height="44dp"
                    android:layout_weight="1"
                    android:text="Hentikan"
                    android:textSize="12sp"
                    android:textColor="#CBD5E1"
                    app:strokeColor="#334155"
                    style="@style/Widget.Material3.Button.OutlinedButton" />

                <Button
                    android:id="@+id/btnQuickForceStopMain"
                    android:layout_width="0dp"
                    android:layout_height="44dp"
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

            <View
                android:layout_width="match_parent"
                android:layout_height="1dp"
                android:background="#1E293B"
                android:layout_marginVertical="12dp" />

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:gravity="center_vertical">

                <TextView
                    android:id="@+id/tvSessionStatusMain"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="Memori Sesi: 0 pesan tersimpan"
                    android:textSize="12.5sp"
                    android:textColor="#CBD5E1" />

                <Button
                    android:id="@+id/btnResetSessionMain"
                    android:layout_width="wrap_content"
                    android:layout_height="34dp"
                    android:text="Reset Sesi"
                    android:textSize="11sp"
                    android:textColor="#FBBF24"
                    app:strokeColor="#475569"
                    style="@style/Widget.Material3.Button.OutlinedButton" />
            </LinearLayout>
        </LinearLayout>

        <!-- SECTION 2: MODE TAMPILAN & KUSTOMISASI PIL DYNAMIC ISLAND -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="MODE TAMPILAN &amp; KUSTOMISASI PIL"
            android:textSize="11sp"
            android:textStyle="bold"
            android:letterSpacing="0.06"
            android:textColor="#64748B"
            android:layout_marginStart="6dp"
            android:layout_marginBottom="6dp" />

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_liquid_glass_card"
            android:padding="16dp"
            android:layout_marginBottom="18dp">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Pilih Mode Pemicu Layar"
                android:textSize="13.5sp"
                android:textStyle="bold"
                android:textColor="#F8FAFC" />

            <RadioGroup
                android:id="@+id/rgOverlayStyle"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:layout_marginTop="6dp">

                <RadioButton
                    android:id="@+id/rbStyleDynamicIsland"
                    android:layout_width="match_parent"
                    android:layout_height="36dp"
                    android:text="Dynamic Island (Pil Melayang di Atas Layar)"
                    android:textSize="12.5sp"
                    android:textColor="#F8FAFC"
                    android:checked="true" />

                <RadioButton
                    android:id="@+id/rbStyleSiriMode"
                    android:layout_width="match_parent"
                    android:layout_height="36dp"
                    android:text="Mode Siri (Tersembunyi Total, Panggil via Control Center)"
                    android:textSize="12.5sp"
                    android:textColor="#E9D5FF" />

                <RadioButton
                    android:id="@+id/rbStyleXiaomiEdge"
                    android:layout_width="match_parent"
                    android:layout_height="36dp"
                    android:text="Xiaomi Edge Pill (Garis Tipis di Tepi Layar)"
                    android:textSize="12.5sp"
                    android:textColor="#F8FAFC" />

                <RadioButton
                    android:id="@+id/rbStyleClassicBubble"
                    android:layout_width="match_parent"
                    android:layout_height="36dp"
                    android:text="Classic Bubble (Gelembung Melayang Bebas)"
                    android:textSize="12.5sp"
                    android:textColor="#F8FAFC" />
            </RadioGroup>

            <View
                android:layout_width="match_parent"
                android:layout_height="1dp"
                android:background="#1E293B"
                android:layout_marginVertical="10dp" />

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Gaya Visual Pil Dynamic Island"
                android:textSize="13sp"
                android:textStyle="bold"
                android:textColor="#F8FAFC" />

            <RadioGroup
                android:id="@+id/rgPillAppearance"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginTop="4dp">

                <RadioButton
                    android:id="@+id/rbPillStandard"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="Lengkap"
                    android:textSize="12sp"
                    android:textColor="#E2E8F0"
                    android:checked="true" />

                <RadioButton
                    android:id="@+id/rbPillPolos"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="Polos (Hitam)"
                    android:textSize="12sp"
                    android:textColor="#E2E8F0" />

                <RadioButton
                    android:id="@+id/rbPillMinimal"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="Ikon Saja"
                    android:textSize="12sp"
                    android:textColor="#E2E8F0" />
            </RadioGroup>

            <com.google.android.material.switchmaterial.SwitchMaterial
                android:id="@+id/swAutoHidePill"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="6dp"
                android:text="Auto-Hide Pil (Menghilang Halus Setelah 3 Detik Diam)"
                android:textColor="#E2E8F0"
                android:textSize="12.5sp"
                android:checked="false" />

            <com.google.android.material.switchmaterial.SwitchMaterial
                android:id="@+id/swSmartFreeze"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="2dp"
                android:text="Auto Smart Freeze (Hemat RAM &amp; Daya Saat Layar Mati/Idle)"
                android:textColor="#34D399"
                android:textSize="12.5sp"
                android:checked="true" />

            <com.google.android.material.switchmaterial.SwitchMaterial
                android:id="@+id/swTapOutsideClose"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="2dp"
                android:text="Ketuk di Luar Jendela untuk Menutup"
                android:textColor="#E2E8F0"
                android:textSize="12.5sp"
                android:checked="true" />

            <com.google.android.material.switchmaterial.SwitchMaterial
                android:id="@+id/swLiquidBlur"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="2dp"
                android:text="Liquid Glass Real Blur &amp; Specular Refraction"
                android:textColor="#E2E8F0"
                android:textSize="12.5sp"
                android:checked="true" />

            <com.google.android.material.switchmaterial.SwitchMaterial
                android:id="@+id/swHapticFeedback"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="2dp"
                android:text="Getaran Taktil iOS (Haptic Engine)"
                android:textColor="#E2E8F0"
                android:textSize="12.5sp"
                android:checked="true" />

            <View
                android:layout_width="match_parent"
                android:layout_height="1dp"
                android:background="#1E293B"
                android:layout_marginVertical="10dp" />

            <TextView
                android:id="@+id/tvIslandWidthLabel"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Lebar Pil Dynamic Island: 164dp"
                android:textSize="12sp"
                android:textColor="#CBD5E1" />

            <SeekBar
                android:id="@+id/sbIslandWidth"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:max="130"
                android:progress="54"
                android:layout_marginBottom="10dp" />

            <TextView
                android:id="@+id/tvIslandPosYLabel"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Posisi Vertikal Atas (Y): 12dp"
                android:textSize="12sp"
                android:textColor="#CBD5E1" />

            <SeekBar
                android:id="@+id/sbIslandPosY"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:max="70"
                android:progress="12"
                android:layout_marginBottom="10dp" />

            <TextView
                android:id="@+id/tvIslandOffsetXLabel"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Geser Horizontal Kamera (X): 0dp"
                android:textSize="12sp"
                android:textColor="#CBD5E1" />

            <SeekBar
                android:id="@+id/sbIslandOffsetX"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:max="160"
                android:progress="80"
                android:layout_marginBottom="10dp" />

            <TextView
                android:id="@+id/tvOpacityLabel"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Transparansi Liquid Glass: 80%"
                android:textSize="12sp"
                android:textColor="#CBD5E1" />

            <SeekBar
                android:id="@+id/sbOpacity"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:max="55"
                android:progress="35" />
        </LinearLayout>

        <!-- SECTION 3: GEMINI API KEY & KARAKTER AI -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="GEMINI API &amp; KARAKTER AI"
            android:textSize="11sp"
            android:textStyle="bold"
            android:letterSpacing="0.06"
            android:textColor="#64748B"
            android:layout_marginStart="6dp"
            android:layout_marginBottom="6dp" />

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_liquid_glass_card"
            android:padding="16dp"
            android:layout_marginBottom="18dp">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:gravity="center_vertical"
                android:layout_marginBottom="10dp">

                <TextView
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text="Gemini API Token"
                    android:textSize="14sp"
                    android:textStyle="bold"
                    android:textColor="#F8FAFC" />

                <TextView
                    android:id="@+id/tvGetKeyShortcut"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Ambil API Key ↗"
                    android:textSize="12sp"
                    android:textStyle="bold"
                    android:textColor="#38BDF8" />
            </LinearLayout>

            <com.google.android.material.textfield.TextInputLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="Tempel Gemini API Key (AIzaSy...)"
                app:boxBackgroundColor="#0B111E"
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

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="14dp"
                android:text="Gaya Bicara Floamini"
                android:textSize="12sp"
                android:textColor="#94A3B8" />

            <RadioGroup
                android:id="@+id/rgPersona"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginTop="4dp">

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

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="10dp"
                android:text="Model Gemini"
                android:textSize="12sp"
                android:textColor="#94A3B8" />

            <RadioGroup
                android:id="@+id/rgModel"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginTop="4dp">

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

        <Button
            android:id="@+id/btnSaveAllSettings"
            android:layout_width="match_parent"
            android:layout_height="52dp"
            android:text="Simpan &amp; Terapkan ke Floamini"
            android:textStyle="bold"
            android:backgroundTint="#2563EB"
            android:textColor="#FFFFFF"
            android:layout_marginBottom="24dp" />

    </LinearLayout>
</ScrollView>
""",

    # --------------------------------------------------------------------------
    # 7. LAYOUT OVERLAY: DYNAMIC ISLAND (CUSTOM POLOS/LENGKAP) + LIQUID GLASS
    # --------------------------------------------------------------------------
    "app/src/main/res/layout/layout_floating_assistant.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content">

    <!-- 1A. DYNAMIC ISLAND PILL (MENDUKUNG MODE LENGKAP, POLOS, & IKON SAJA) -->
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
        android:layout_width="346dp"
        android:layout_height="478dp"
        android:orientation="vertical"
        android:background="@drawable/bg_liquid_glass_window"
        android:elevation="22dp"
        android:visibility="gone">

        <!-- LIQUID GLASS SPECULAR TOP HEADER BAR -->
        <LinearLayout
            android:id="@+id/glassTitleBar"
            android:layout_width="match_parent"
            android:layout_height="46dp"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:paddingHorizontal="12dp"
            android:background="@drawable/bg_liquid_glass_header">

            <!-- Tombol X untuk Close -->
            <ImageView
                android:id="@+id/btnCloseWindowX"
                android:layout_width="28dp"
                android:layout_height="28dp"
                android:padding="6dp"
                android:background="@drawable/bg_close_x_btn"
                android:src="@drawable/ic_close_x"
                app:tint="#F8FAFC"
                android:contentDescription="Tutup" />

            <LinearLayout
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:gravity="center"
                android:orientation="horizontal">

                <ImageView
                    android:layout_width="14dp"
                    android:layout_height="14dp"
                    android:src="@drawable/ic_sparkle"
                    app:tint="#38BDF8" />

                <TextView
                    android:id="@+id/tvWindowTitle"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginStart="6dp"
                    android:text="Floamini"
                    android:textSize="13.5sp"
                    android:textStyle="bold"
                    android:textColor="#F8FAFC" />

                <TextView
                    android:id="@+id/tvSessionCounterBadge"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginStart="6dp"
                    android:paddingHorizontal="6dp"
                    android:paddingVertical="1dp"
                    android:background="@drawable/bg_badge_pill"
                    android:text="0"
                    android:textSize="9.5sp"
                    android:textColor="#38BDF8" />
            </LinearLayout>

            <!-- Toggle Live Screen Share -->
            <ImageView
                android:id="@+id/btnScreenShare"
                android:layout_width="28dp"
                android:layout_height="28dp"
                android:padding="5dp"
                android:src="@drawable/ic_screen_share"
                app:tint="#94A3B8"
                android:contentDescription="Live Screen Share" />

            <!-- Tombol Plus (+) Ultra Quick Menu -->
            <ImageView
                android:id="@+id/btnPlusMenu"
                android:layout_width="28dp"
                android:layout_height="28dp"
                android:layout_marginStart="6dp"
                android:padding="5dp"
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
            android:text="Live Screen Vision Aktif • Floamini Melihat Layar"
            android:textSize="10sp"
            android:textColor="#7DD3FC"
            android:gravity="center"
            android:visibility="gone" />

        <!-- DRAWER MENU PLUS (+) -->
        <LinearLayout
            android:id="@+id/plusMenuDrawer"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="#EB111827"
            android:padding="10dp"
            android:visibility="gone">

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
                    android:layout_marginStart="5dp"
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
                    android:layout_weight="1.15"
                    android:layout_marginStart="5dp"
                    android:gravity="center"
                    android:background="@drawable/bg_chip_action"
                    android:orientation="horizontal">

                    <ImageView
                        android:layout_width="13dp"
                        android:layout_height="13dp"
                        android:src="@drawable/ic_model_cpu"
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
                    android:layout_weight="0.85"
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
                    android:id="@+id/actionExportChat"
                    android:layout_width="0dp"
                    android:layout_height="34dp"
                    android:layout_weight="0.95"
                    android:layout_marginStart="5dp"
                    android:gravity="center"
                    android:background="@drawable/bg_chip_action"
                    android:orientation="horizontal">

                    <ImageView
                        android:layout_width="13dp"
                        android:layout_height="13dp"
                        android:src="@drawable/ic_bolt"
                        app:tint="#38BDF8" />

                    <TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginStart="4dp"
                        android:text="Export"
                        android:textSize="11sp"
                        android:textColor="#F8FAFC" />
                </LinearLayout>

                <LinearLayout
                    android:id="@+id/actionResetChat"
                    android:layout_width="0dp"
                    android:layout_height="34dp"
                    android:layout_weight="0.9"
                    android:layout_marginStart="5dp"
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
                        android:text="Reset"
                        android:textSize="11sp"
                        android:textColor="#F8FAFC" />
                </LinearLayout>

                <LinearLayout
                    android:id="@+id/actionQuickForceStop"
                    android:layout_width="0dp"
                    android:layout_height="34dp"
                    android:layout_weight="1.15"
                    android:layout_marginStart="5dp"
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
                        android:id="@+id/chipQuickScreenSummary"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:paddingHorizontal="10dp"
                        android:paddingVertical="5dp"
                        android:background="@drawable/bg_chip_prompt"
                        android:text="Ringkas layar ini"
                        android:textSize="10sp"
                        android:textColor="#38BDF8" />

                    <TextView
                        android:id="@+id/chipQuickExplain"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginStart="6dp"
                        android:paddingHorizontal="10dp"
                        android:paddingVertical="5dp"
                        android:background="@drawable/bg_chip_prompt"
                        android:text="Jelasin maksudnya"
                        android:textSize="10sp"
                        android:textColor="#E2E8F0" />

                    <TextView
                        android:id="@+id/chipQuickTranslate"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginStart="6dp"
                        android:paddingHorizontal="10dp"
                        android:paddingVertical="5dp"
                        android:background="@drawable/bg_chip_prompt"
                        android:text="Terjemahin ke Indo"
                        android:textSize="10sp"
                        android:textColor="#E2E8F0" />

                    <TextView
                        android:id="@+id/chipQuickReply"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginStart="6dp"
                        android:paddingHorizontal="10dp"
                        android:paddingVertical="5dp"
                        android:background="@drawable/bg_chip_prompt"
                        android:text="Buatin balasan asik"
                        android:textSize="10sp"
                        android:textColor="#E2E8F0" />
                </LinearLayout>
            </HorizontalScrollView>

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
            android:padding="10dp">

            <LinearLayout
                android:id="@+id/chatContainer"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical" />
        </ScrollView>

        <!-- INDIKATOR MENGETIK -->
        <LinearLayout
            android:id="@+id/typingIndicatorRow"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:paddingHorizontal="14dp"
            android:paddingVertical="3dp"
            android:visibility="gone">

            <ImageView
                android:layout_width="12dp"
                android:layout_height="12dp"
                android:src="@drawable/ic_sparkle"
                app:tint="#38BDF8" />

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginStart="6dp"
                android:text="Floamini lagi mikir..."
                android:textSize="11sp"
                android:textColor="#7DD3FC" />
        </LinearLayout>

        <!-- INPUT PESAN, TOMBOL KIRIM, & RESIZE HANDLE -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:paddingStart="10dp"
            android:paddingEnd="6dp"
            android:paddingTop="6dp"
            android:paddingBottom="8dp">

            <EditText
                android:id="@+id/etPrompt"
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:hint="Tanya atau ngobrol..."
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

            <ImageView
                android:id="@+id/btnResizeHandle"
                android:layout_width="22dp"
                android:layout_height="28dp"
                android:layout_marginStart="4dp"
                android:padding="3dp"
                android:src="@drawable/ic_resize_handle"
                app:tint="#64748B"
                android:contentDescription="Ubah Ukuran Jendela" />
        </LinearLayout>

    </LinearLayout>
</FrameLayout>
""",

    # --------------------------------------------------------------------------
    # 8. DRAWABLES: GENUINE LIQUID GLASS, POLOS PILL, & CUSTOM SVG VECTORS
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
    <item
        android:left="1dp"
        android:top="1dp"
        android:right="1dp"
        android:bottom="1dp">
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
    <item
        android:left="1dp"
        android:top="1dp"
        android:right="1dp"
        android:bottom="1dp">
        <shape android:shape="rectangle">
            <gradient
                android:angle="270"
                android:startColor="#E6141D30"
                android:endColor="#E60A0F1C" />
            <corners android:radius="21dp" />
        </shape>
    </item>
</layer-list>
""",

    "app/src/main/res/drawable/bg_liquid_glass_window.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Lapisan 1: Refraksi Prisma Tepi Liquid Glass -->
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
    <!-- Lapisan 2: Inti Kaca Transparan Bergradasi dengan Pantulan Internal -->
    <item
        android:left="1.4dp"
        android:top="1.4dp"
        android:right="1.4dp"
        android:bottom="1.4dp">
        <shape android:shape="rectangle">
            <gradient
                android:angle="270"
                android:startColor="#CC18233A"
                android:centerColor="#B80E1628"
                android:endColor="#CC0A101E" />
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
    <item
        android:left="1.8dp"
        android:top="1.8dp"
        android:right="1.8dp"
        android:bottom="1.8dp">
        <shape android:shape="rectangle">
            <gradient
                android:angle="270"
                android:startColor="#CC18233A"
                android:centerColor="#B80E1628"
                android:endColor="#CC0A101E" />
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

    "app/src/main/res/drawable/bg_ios_icon_blue.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#0284C7" />
    <corners android:radius="8dp" />
</shape>
""",

    "app/src/main/res/drawable/bg_ios_icon_purple.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#7C3AED" />
    <corners android:radius="8dp" />
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
    <corners
        android:topLeftRadius="0dp"
        android:bottomLeftRadius="0dp"
        android:topRightRadius="36dp"
        android:bottomRightRadius="36dp" />
    <stroke android:width="1.2dp" android:color="#80FFFFFF" />
</shape>
""",

    "app/src/main/res/drawable/bg_xiaomi_edge_right.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#D90B111E" />
    <corners
        android:topLeftRadius="36dp"
        android:bottomLeftRadius="36dp"
        android:topRightRadius="0dp"
        android:bottomRightRadius="0dp" />
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
    <corners android:radius="10dp" />
</shape>
""",

    "app/src/main/res/drawable/bg_chip_action.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#B30B111E" />
    <corners android:radius="11dp" />
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
    <corners android:radius="11dp" />
    <stroke android:width="1dp" android:color="#991B1B" />
</shape>
""",

    "app/src/main/res/drawable/bg_input_glass.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#8C1E293B" />
    <corners android:radius="16dp" />
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
    <solid android:color="#D91A2438" />
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

    "app/src/main/res/drawable/ic_external_link.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M19,19H5V5H12V3H5C3.89,3 3,3.9 3,5V19C3,20.1 3.89,21 5,21H19C20.1,21 21,20.1 21,19V12H19V19ZM14,3V5H17.59L7.76,14.83L9.17,16.24L19,6.41V10H21V3H14Z" />
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

    "app/src/main/res/drawable/ic_model_cpu.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M9,3V5H7C5.9,5 5,5.9 5,7V9H3V11H5V13H3V15H5V17C5,18.1 5.9,19 7,19H9V21H11V19H13V21H15V19H17C18.1,19 19,18.1 19,17V15H21V13H19V11H21V9H19V7C19,5.9 18.1,5 17,5H15V3H13V5H11V3H9ZM7,7H17V17H7V7ZM9,9V15H15V9H9Z" />
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

    "app/src/main/res/drawable/ic_bolt.xml": r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M11,21H10L11,14H6.5C5.92,14 5.93,13.68 6.12,13.34C6.31,13 6.17,13.26 6.19,13.22C7.48,10.94 9.42,7.5 12,3H13L12,10H16.5C16.99,10 17.06,10.33 16.97,10.51L16.9,10.66C12.96,17.55 11,21 11,21Z" />
</vector>
""",

    # --------------------------------------------------------------------------
    # 9. CUSTOM VIEW: APPLE INTELLIGENCE / iOS SIRI EDGE GLOW AURA
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

    # --------------------------------------------------------------------------
    # 10. CONTROL CENTER TILE SERVICE & SIRI TRIGGER ACTIVITY
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
            val permIntent = Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:$packageName")
            ).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            startActivity(permIntent)
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

    # --------------------------------------------------------------------------
    # 11. WELCOME ACTIVITY
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/WelcomeActivity.kt": r"""package com.example.floatinggeminiai

import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.textfield.TextInputEditText
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.util.concurrent.TimeUnit

class WelcomeActivity : AppCompatActivity() {

    private val activityJob = Job()
    private val uiScope = CoroutineScope(Dispatchers.Main + activityJob)

    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .build()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_welcome)

        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        val fromSettings = intent.getBooleanExtra("from_settings", false)

        val btnOpenAiStudio = findViewById<Button>(R.id.btnOpenAiStudio)
        val etWelcomeApiKey = findViewById<TextInputEditText>(R.id.etWelcomeApiKey)
        val btnTestTokenWelcome = findViewById<Button>(R.id.btnTestTokenWelcome)
        val tvTokenTestResult = findViewById<TextView>(R.id.tvTokenTestResult)
        val btnContinueToFloamini = findViewById<Button>(R.id.btnContinueToFloamini)

        etWelcomeApiKey.setText(prefs.getString("api_key", ""))
        if (fromSettings) {
            btnContinueToFloamini.text = "Kembali ke Pengaturan Floamini"
        }

        btnOpenAiStudio.setOnClickListener {
            try {
                startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://aistudio.google.com/apikey")))
            } catch (_: Exception) {
                Toast.makeText(this, "Kunjungi aistudio.google.com/apikey di browser", Toast.LENGTH_LONG).show()
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
            tvTokenTestResult.text = "Menguji koneksi ke Gemini..."
            tvTokenTestResult.setTextColor(Color.parseColor("#38BDF8"))

            uiScope.launch {
                val isValid = verifyGeminiApiKey(token)
                btnTestTokenWelcome.isEnabled = true
                if (isValid) {
                    prefs.edit().putString("api_key", token).apply()
                    tvTokenTestResult.text = "Token Valid & Tersimpan!"
                    tvTokenTestResult.setTextColor(Color.parseColor("#34D399"))
                } else {
                    tvTokenTestResult.text = "Token tidak valid atau jaringan bermasalah"
                    tvTokenTestResult.setTextColor(Color.parseColor("#FCA5A5"))
                }
            }
        }

        btnContinueToFloamini.setOnClickListener {
            val enteredKey = etWelcomeApiKey.text.toString().trim()
            val editor = prefs.edit().putBoolean("has_seen_welcome", true)
            if (enteredKey.isNotEmpty()) {
                editor.putString("api_key", enteredKey)
            }
            editor.apply()

            if (!fromSettings) {
                startActivity(Intent(this, MainActivity::class.java))
            }
            finish()
        }
    }

    private suspend fun verifyGeminiApiKey(apiKey: String): Boolean = withContext(Dispatchers.IO) {
        try {
            val url = "https://generativelanguage.googleapis.com/v1beta/models?key=$apiKey"
            val request = Request.Builder().url(url).get().build()
            httpClient.newCall(request).execute().use { response ->
                response.isSuccessful
            }
        } catch (_: Exception) {
            false
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        activityJob.cancel()
    }
}
""",

    # --------------------------------------------------------------------------
    # 12. MAIN ACTIVITY (iOS 26 SETTINGS + CONTROL CENTER TILE REQUESTER)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/MainActivity.kt": r"""package com.example.floatinggeminiai

import android.app.StatusBarManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.graphics.drawable.Icon
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
import org.json.JSONArray
import kotlin.system.exitProcess

class MainActivity : AppCompatActivity() {

    private lateinit var tvSessionStatusMain: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        if (!prefs.getBoolean("has_seen_welcome", false)) {
            startActivity(Intent(this, WelcomeActivity::class.java))
            finish()
            return
        }

        setContentView(R.layout.activity_main)

        val tvAppVersionInfo = findViewById<TextView>(R.id.tvAppVersionInfo)
        val btnOpenWelcomeGuide = findViewById<Button>(R.id.btnOpenWelcomeGuide)
        val btnStartOverlay = findViewById<Button>(R.id.btnStartOverlay)
        val btnAddControlCenterTile = findViewById<Button>(R.id.btnAddControlCenterTile)
        val btnStopOverlay = findViewById<Button>(R.id.btnStopOverlay)
        val btnQuickForceStopMain = findViewById<Button>(R.id.btnQuickForceStopMain)
        tvSessionStatusMain = findViewById(R.id.tvSessionStatusMain)
        val btnResetSessionMain = findViewById<Button>(R.id.btnResetSessionMain)

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
        val swLiquidBlur = findViewById<SwitchMaterial>(R.id.swLiquidBlur)
        val swHapticFeedback = findViewById<SwitchMaterial>(R.id.swHapticFeedback)

        val tvIslandWidthLabel = findViewById<TextView>(R.id.tvIslandWidthLabel)
        val sbIslandWidth = findViewById<SeekBar>(R.id.sbIslandWidth)
        val tvIslandPosYLabel = findViewById<TextView>(R.id.tvIslandPosYLabel)
        val sbIslandPosY = findViewById<SeekBar>(R.id.sbIslandPosY)
        val tvIslandOffsetXLabel = findViewById<TextView>(R.id.tvIslandOffsetXLabel)
        val sbIslandOffsetX = findViewById<SeekBar>(R.id.sbIslandOffsetX)
        val tvOpacityLabel = findViewById<TextView>(R.id.tvOpacityLabel)
        val sbOpacity = findViewById<SeekBar>(R.id.sbOpacity)

        val tvGetKeyShortcut = findViewById<TextView>(R.id.tvGetKeyShortcut)
        val etApiKey = findViewById<TextInputEditText>(R.id.etApiKey)
        val rgPersona = findViewById<RadioGroup>(R.id.rgPersona)
        val rbAsik = findViewById<RadioButton>(R.id.rbAsik)
        val rbRingkas = findViewById<RadioButton>(R.id.rbRingkas)
        val rbDetail = findViewById<RadioButton>(R.id.rbDetail)
        val rbTeknis = findViewById<RadioButton>(R.id.rbTeknis)

        val rgModel = findViewById<RadioGroup>(R.id.rgModel)
        val rbModel3Flash = findViewById<RadioButton>(R.id.rbModel3Flash)
        val rbModel25Flash = findViewById<RadioButton>(R.id.rbModel25Flash)
        val rbModel25Pro = findViewById<RadioButton>(R.id.rbModel25Pro)
        val btnSaveAllSettings = findViewById<Button>(R.id.btnSaveAllSettings)

        try {
            val pInfo = packageManager.getPackageInfo(packageName, 0)
            tvAppVersionInfo.text = "v${pInfo.versionName} • Liquid Glass & Siri Mode"
        } catch (_: Exception) {}

        etApiKey.setText(prefs.getString("api_key", ""))
        updateSessionStatsLabel()

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
        swLiquidBlur.isChecked = prefs.getBoolean("liquid_blur", true)
        swHapticFeedback.isChecked = prefs.getBoolean("haptic_feedback", true)

        val savedIslandW = prefs.getInt("island_width_dp", 164)
        sbIslandWidth.progress = (savedIslandW - 110).coerceIn(0, 130)
        tvIslandWidthLabel.text = "Lebar Pil Dynamic Island: ${savedIslandW}dp"

        val savedIslandY = prefs.getInt("island_pos_y_dp", 12)
        sbIslandPosY.progress = savedIslandY.coerceIn(0, 70)
        tvIslandPosYLabel.text = "Posisi Vertikal Atas (Y): ${savedIslandY}dp"

        val savedIslandX = prefs.getInt("island_offset_x_dp", 0)
        sbIslandOffsetX.progress = (savedIslandX + 80).coerceIn(0, 160)
        tvIslandOffsetXLabel.text = "Geser Horizontal Kamera (X): ${savedIslandX}dp"

        val savedOpacity = prefs.getInt("popup_opacity", 80)
        sbOpacity.progress = (savedOpacity - 45).coerceIn(0, 55)
        tvOpacityLabel.text = "Transparansi Liquid Glass: ${savedOpacity}%"

        when (prefs.getString("ai_persona", "asik")) {
            "ringkas" -> rbRingkas.isChecked = true
            "detail" -> rbDetail.isChecked = true
            "teknis" -> rbTeknis.isChecked = true
            else -> rbAsik.isChecked = true
        }

        when (prefs.getString("ai_model", "gemini-3-flash-preview")) {
            "gemini-2.5-flash" -> rbModel25Flash.isChecked = true
            "gemini-2.5-pro" -> rbModel25Pro.isChecked = true
            else -> rbModel3Flash.isChecked = true
        }

        sbIslandWidth.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                tvIslandWidthLabel.text = "Lebar Pil Dynamic Island: ${progress + 110}dp"
            }
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })

        sbIslandPosY.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                tvIslandPosYLabel.text = "Posisi Vertikal Atas (Y): ${progress}dp"
            }
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })

        sbIslandOffsetX.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                tvIslandOffsetXLabel.text = "Geser Horizontal Kamera (X): ${progress - 80}dp"
            }
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })

        sbOpacity.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                tvOpacityLabel.text = "Transparansi Liquid Glass: ${progress + 45}%"
            }
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
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
            val model = when (rgModel.checkedRadioButtonId) {
                R.id.rbModel25Flash -> "gemini-2.5-flash"
                R.id.rbModel25Pro -> "gemini-2.5-pro"
                else -> "gemini-3-flash-preview"
            }
            prefs.edit()
                .putString("api_key", etApiKey.text.toString().trim())
                .putString("overlay_style", style)
                .putString("pill_appearance", pillApp)
                .putBoolean("auto_hide_pill", swAutoHidePill.isChecked)
                .putBoolean("smart_freeze", swSmartFreeze.isChecked)
                .putBoolean("tap_outside_close", swTapOutsideClose.isChecked)
                .putBoolean("liquid_blur", swLiquidBlur.isChecked)
                .putBoolean("haptic_feedback", swHapticFeedback.isChecked)
                .putInt("island_width_dp", sbIslandWidth.progress + 110)
                .putInt("island_pos_y_dp", sbIslandPosY.progress)
                .putInt("island_offset_x_dp", sbIslandOffsetX.progress - 80)
                .putInt("popup_opacity", sbOpacity.progress + 45)
                .putString("ai_persona", persona)
                .putString("ai_model", model)
                .apply()

            if (Settings.canDrawOverlays(this)) {
                val refreshIntent = Intent(this, FloatingAssistantService::class.java).apply {
                    action = FloatingAssistantService.ACTION_RELOAD_SETTINGS
                }
                try {
                    startService(refreshIntent)
                } catch (_: Exception) {}
            }
        }

        btnAddControlCenterTile.setOnClickListener {
            saveAllPreferences()
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                val statusBarManager = getSystemService(StatusBarManager::class.java)
                statusBarManager.requestAddTileService(
                    ComponentName(this, FloaminiTileService::class.java),
                    "Floamini AI",
                    Icon.createWithResource(this, R.drawable.ic_sparkle),
                    mainExecutor
                ) { resultCode ->
                    runOnUiThread {
                        if (resultCode == StatusBarManager.TILE_ADD_REQUEST_RESULT_TILE_ADDED ||
                            resultCode == StatusBarManager.TILE_ADD_REQUEST_RESULT_TILE_ALREADY_ADDED
                        ) {
                            Toast.makeText(this, "Tombol Floamini AI siap di Control Center!", Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            } else {
                Toast.makeText(
                    this,
                    "Tarik panel Control Center / Quick Settings dari atas layar, tekan Edit, lalu seret tombol Floamini AI!",
                    Toast.LENGTH_LONG
                ).show()
            }
        }

        btnOpenWelcomeGuide.setOnClickListener {
            startActivity(Intent(this, WelcomeActivity::class.java).apply {
                putExtra("from_settings", true)
            })
        }

        tvGetKeyShortcut.setOnClickListener {
            try {
                startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://aistudio.google.com/apikey")))
            } catch (_: Exception) {
                Toast.makeText(this, "Kunjungi aistudio.google.com/apikey", Toast.LENGTH_LONG).show()
            }
        }

        btnResetSessionMain.setOnClickListener {
            prefs.edit().remove("session_history_json").apply()
            updateSessionStatsLabel()
            val resetIntent = Intent(this, FloatingAssistantService::class.java).apply {
                action = FloatingAssistantService.ACTION_RESET_SESSION
            }
            try {
                startService(resetIntent)
            } catch (_: Exception) {}
            Toast.makeText(this, "Memori sesi Floamini di-reset", Toast.LENGTH_SHORT).show()
        }

        btnSaveAllSettings.setOnClickListener {
            saveAllPreferences()
            Toast.makeText(this, "Pengaturan Floamini diterapkan", Toast.LENGTH_SHORT).show()
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
            val modeText = if (rbStyleSiriMode.isChecked) {
                "Mode Siri aktif! Panggil lewat tombol Floamini AI di Control Center."
            } else {
                "Floamini aktif di layar!"
            }
            Toast.makeText(this, modeText, Toast.LENGTH_SHORT).show()
        }

        btnStopOverlay.setOnClickListener {
            stopService(Intent(this, FloatingAssistantService::class.java))
            Toast.makeText(this, "Floamini dihentikan", Toast.LENGTH_SHORT).show()
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

    override fun onResume() {
        super.onResume()
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        findViewById<TextInputEditText>(R.id.etApiKey)?.setText(prefs.getString("api_key", ""))
        updateSessionStatsLabel()
    }

    private fun updateSessionStatsLabel() {
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        val raw = prefs.getString("session_history_json", null)
        val count = try {
            if (!raw.isNullOrEmpty()) JSONArray(raw).length() else 0
        } catch (_: Exception) { 0 }
        tvSessionStatusMain.text = "Memori Sesi: $count pesan tersimpan"
    }
}
""",

    # --------------------------------------------------------------------------
    # 13. SCREEN CAPTURE PERMISSION ACTIVITY
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
    # 14. FLOATING ASSISTANT SERVICE (LIQUID GLASS + SIRI AURA + SMART FREEZE)
    # --------------------------------------------------------------------------
    "app/src/main/java/com/example/floatinggeminiai/FloatingAssistantService.kt": r"""package com.example.floatinggeminiai

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
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.TimeUnit
import kotlin.math.abs
import kotlin.system.exitProcess

class FloatingAssistantService : Service() {

    companion object {
        const val ACTION_SCREEN_CAPTURE_RESULT = "ACTION_SCREEN_CAPTURE_RESULT"
        const val ACTION_RELOAD_SETTINGS = "ACTION_RELOAD_SETTINGS"
        const val ACTION_RESET_SESSION = "ACTION_RESET_SESSION"
        const val ACTION_TRIGGER_SIRI = "ACTION_TRIGGER_SIRI"
        private const val KEY_SESSION_HISTORY = "session_history_json"
    }

    private lateinit var windowManager: WindowManager
    private lateinit var floatingView: View
    private lateinit var params: WindowManager.LayoutParams
    private var isFloatingViewAttached = false

    // Overlay khusus Siri Edge Glow Aura (Full Screen Non-Touchable Border)
    private var siriGlowView: SiriEdgeGlowView? = null
    private var isSiriAuraActive = false

    private val serviceJob = Job()
    private val serviceScope = CoroutineScope(Dispatchers.Main + serviceJob)

    // Komponen UI
    private lateinit var dynamicIslandView: LinearLayout
    private lateinit var ivIslandSparkle: ImageView
    private lateinit var tvIslandLabel: TextView
    private lateinit var viewIslandPulseDot: View
    private lateinit var bubbleView: FrameLayout
    private lateinit var xiaomiEdgeView: FrameLayout
    private lateinit var popupChatView: LinearLayout
    private lateinit var btnScreenShare: ImageView
    private lateinit var tvScreenShareStatus: TextView
    private lateinit var tvCurrentPersonaBadge: TextView
    private lateinit var tvCurrentModelBadge: TextView
    private lateinit var tvSessionCounterBadge: TextView
    private lateinit var typingIndicatorRow: LinearLayout
    private lateinit var scrollChat: ScrollView
    private lateinit var chatContainer: LinearLayout

    // Handler & Smart Freeze State
    private val mainHandler = Handler(Looper.getMainLooper())
    private var snappedToRightEdge = false
    private var fullScreenWidth = 1080
    private var fullScreenHeight = 2400
    private var isPillAutoHidden = false
    private var isSmartFrozen = false

    // Pengaturan Dinamis
    private var prefOverlayStyle = "dynamic_island"
    private var prefPillAppearance = "standard"
    private var prefAutoHidePill = false
    private var prefSmartFreeze = true
    private var prefTapOutsideClose = true
    private var prefLiquidBlur = true
    private var prefHapticFeedback = true
    private var prefIslandWidthPx = 440
    private var prefIslandPosYPx = 32
    private var prefIslandOffsetXPx = 0
    private var prefPopupAlpha = 0.84f
    private var prefBubbleSizePx = 148
    private var prefPersona = "asik"
    private var prefModel = "gemini-3-flash-preview"

    // Data Sesi
    data class SessionMessage(val role: String, val text: String, val timestamp: String)
    private val chatHistory = mutableListOf<SessionMessage>()
    private var lastBotReply = ""

    // Live Screen Share
    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    private var isScreenShareActive = false
    private var captureWidth = 540
    private var captureHeight = 1200
    private var screenDensity = 320

    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(35, TimeUnit.SECONDS)
        .build()

    // Runnables untuk Auto-Hide, Xiaomi Edge, dan Auto Smart Freeze
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
                .setDuration(420)
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

    // Screen Off / Screen On Receiver untuk Auto Smart Freeze Instan
    private val screenStateReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            when (intent?.action) {
                Intent.ACTION_SCREEN_OFF -> {
                    if (prefSmartFreeze) {
                        if (popupChatView.visibility == View.VISIBLE) {
                            popupChatView.visibility = View.GONE
                        }
                        dismissSiriAura()
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
        startForegroundNotification(withMediaProjection = false)
        setupScreenMetrics()
        loadUserPreferences()
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
                    Toast.makeText(this, "Izin Live Screen Share dibatalkan", Toast.LENGTH_SHORT).show()
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
                if (::chatContainer.isInitialized && ::scrollChat.isInitialized) {
                    resetConversationSession()
                }
            }
            ACTION_TRIGGER_SIRI -> {
                triggerHaptic()
                wakeFromSmartFreeze()
                summonSiriExperience()
            }
        }
        return START_STICKY
    }

    // ==========================================================================
    // AUTO SMART FREEZE ENGINE (HEMAT MEMORI & DAYA SAAT IDLE / LAYAR MATI)
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

        // Jika Mode Siri aktif, lepas view dari WindowManager agar 0% GPU/RAM saat idle
        if (prefOverlayStyle == "siri_mode" && isFloatingViewAttached) {
            try {
                windowManager.removeViewImmediate(floatingView)
                isFloatingViewAttached = false
            } catch (_: Exception) {}
        }

        // Bersihkan buffer memori sementara saat idle
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
    // SIRI EDGE GLOW AURA (DIPANGGIL DARI CONTROL CENTER SHORTCUT)
    // ==========================================================================
    private fun summonSiriExperience() {
        showSiriAura()
        openPopupChat(fromSiri = true)
    }

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

        val glowView = SiriEdgeGlowView(this).apply {
            alpha = 0f
        }
        siriGlowView = glowView
        try {
            windowManager.addView(glowView, auraParams)
            glowView.startSiriAnimation()
            glowView.animate().alpha(1f).setDuration(360).start()
        } catch (_: Exception) {}
    }

    private fun dismissSiriAura() {
        val glowView = siriGlowView ?: return
        isSiriAuraActive = false
        siriGlowView = null
        glowView.animate()
            .alpha(0f)
            .setDuration(260)
            .withEndAction {
                glowView.stopAndFreezeAnimation()
                try {
                    windowManager.removeViewImmediate(glowView)
                } catch (_: Exception) {}
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
                    vibrator.vibrate(VibrationEffect.createOneShot(16, VibrationEffect.DEFAULT_AMPLITUDE))
                } else {
                    @Suppress("DEPRECATION")
                    vibrator.vibrate(16)
                }
            }
        } catch (_: Exception) {}
    }

    private fun currentTimeLabel(): String {
        return SimpleDateFormat("HH:mm", Locale.getDefault()).format(Date())
    }

    private fun loadUserPreferences() {
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        val density = resources.displayMetrics.density
        prefOverlayStyle = prefs.getString("overlay_style", "dynamic_island") ?: "dynamic_island"
        prefPillAppearance = prefs.getString("pill_appearance", "standard") ?: "standard"
        prefAutoHidePill = prefs.getBoolean("auto_hide_pill", false)
        prefSmartFreeze = prefs.getBoolean("smart_freeze", true)
        prefTapOutsideClose = prefs.getBoolean("tap_outside_close", true)
        prefLiquidBlur = prefs.getBoolean("liquid_blur", true)
        prefHapticFeedback = prefs.getBoolean("haptic_feedback", true)
        prefIslandWidthPx = (prefs.getInt("island_width_dp", 164) * density).toInt()
        prefIslandPosYPx = (prefs.getInt("island_pos_y_dp", 12) * density).toInt()
        prefIslandOffsetXPx = (prefs.getInt("island_offset_x_dp", 0) * density).toInt()
        prefPopupAlpha = (prefs.getInt("popup_opacity", 80) / 100f).coerceIn(0.45f, 1.0f)
        prefBubbleSizePx = (54 * density).toInt()
        prefPersona = prefs.getString("ai_persona", "asik") ?: "asik"
        prefModel = prefs.getString("ai_model", "gemini-3-flash-preview") ?: "gemini-3-flash-preview"
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
        if (::tvCurrentPersonaBadge.isInitialized) {
            tvCurrentPersonaBadge.text = when (prefPersona) {
                "ringkas" -> "Singkat"
                "detail" -> "Detail"
                "teknis" -> "Teknis"
                else -> "Asik"
            }
        }
        if (::tvCurrentModelBadge.isInitialized) {
            tvCurrentModelBadge.text = when (prefModel) {
                "gemini-2.5-flash" -> "2.5 Flash"
                "gemini-2.5-pro" -> "2.5 Pro"
                else -> "3 Flash"
            }
        }
        updateSessionCounterBadge()
    }

    private fun updateSessionCounterBadge() {
        if (::tvSessionCounterBadge.isInitialized) {
            tvSessionCounterBadge.text = chatHistory.size.toString()
        }
    }

    // ==========================================================================
    // MEMORI SESI PERMANEN
    // ==========================================================================
    private fun saveSessionHistory() {
        try {
            val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
            val jsonArray = JSONArray()
            for (msg in chatHistory) {
                jsonArray.put(JSONObject().apply {
                    put("role", msg.role)
                    put("text", msg.text)
                    put("timestamp", msg.timestamp)
                })
            }
            prefs.edit().putString(KEY_SESSION_HISTORY, jsonArray.toString()).apply()
            updateSessionCounterBadge()
        } catch (_: Exception) {}
    }

    private fun restoreSessionHistory() {
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
                    val time = obj.optString("timestamp", currentTimeLabel())
                    if (text.isNotEmpty()) {
                        val msg = SessionMessage(role, text, time)
                        chatHistory.add(msg)
                        val isUser = (role == "user")
                        if (!isUser) lastBotReply = text
                        addChatMessage(text, time, isUser = isUser)
                    }
                }
            }
        } catch (_: Exception) {}

        updateSessionCounterBadge()
        if (chatHistory.isEmpty()) {
            val greeting = "Hai! Floamini sudah siap menemani kamu. Obrolan di sesi ini terus tersimpan dan nyambung!"
            lastBotReply = greeting
            addChatMessage(greeting, currentTimeLabel(), isUser = false)
        }
    }

    private fun resetConversationSession() {
        chatHistory.clear()
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        prefs.edit().remove(KEY_SESSION_HISTORY).apply()
        chatContainer.removeAllViews()
        updateSessionCounterBadge()
        val resetMsg = "Sesi obrolan Floamini sudah di-reset bersih. Yuk mulai topik baru!"
        lastBotReply = resetMsg
        addChatMessage(resetMsg, currentTimeLabel(), isUser = false)
    }

    private fun startForegroundNotification(withMediaProjection: Boolean) {
        val channelId = "floamini_liquid_glass_channel"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Floamini AI Assistant",
                NotificationManager.IMPORTANCE_LOW
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }

        val notification: Notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("Floamini")
            .setContentText(if (withMediaProjection) "Live Screen Vision aktif" else "Liquid Glass & Smart Freeze aktif")
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

        dynamicIslandView = floatingView.findViewById(R.id.dynamicIslandView)
        ivIslandSparkle = floatingView.findViewById(R.id.ivIslandSparkle)
        tvIslandLabel = floatingView.findViewById(R.id.tvIslandLabel)
        viewIslandPulseDot = floatingView.findViewById(R.id.viewIslandPulseDot)
        bubbleView = floatingView.findViewById(R.id.bubbleView)
        xiaomiEdgeView = floatingView.findViewById(R.id.xiaomiEdgeView)
        popupChatView = floatingView.findViewById(R.id.popupChatView)

        val glassTitleBar = floatingView.findViewById<LinearLayout>(R.id.glassTitleBar)
        val btnCloseWindowX = floatingView.findViewById<ImageView>(R.id.btnCloseWindowX)
        tvSessionCounterBadge = floatingView.findViewById(R.id.tvSessionCounterBadge)
        btnScreenShare = floatingView.findViewById(R.id.btnScreenShare)
        val btnPlusMenu = floatingView.findViewById<ImageView>(R.id.btnPlusMenu)
        val plusMenuDrawer = floatingView.findViewById<LinearLayout>(R.id.plusMenuDrawer)
        tvScreenShareStatus = floatingView.findViewById(R.id.tvScreenShareStatus)

        val actionToggleToken = floatingView.findViewById<LinearLayout>(R.id.actionToggleToken)
        val actionCyclePersona = floatingView.findViewById<LinearLayout>(R.id.actionCyclePersona)
        val actionCycleModel = floatingView.findViewById<LinearLayout>(R.id.actionCycleModel)
        val actionCopyLast = floatingView.findViewById<LinearLayout>(R.id.actionCopyLast)
        val actionExportChat = floatingView.findViewById<LinearLayout>(R.id.actionExportChat)
        val actionResetChat = floatingView.findViewById<LinearLayout>(R.id.actionResetChat)
        val actionQuickForceStop = floatingView.findViewById<LinearLayout>(R.id.actionQuickForceStop)
        tvCurrentPersonaBadge = floatingView.findViewById(R.id.tvCurrentPersonaBadge)
        tvCurrentModelBadge = floatingView.findViewById(R.id.tvCurrentModelBadge)

        val chipQuickScreenSummary = floatingView.findViewById<TextView>(R.id.chipQuickScreenSummary)
        val chipQuickExplain = floatingView.findViewById<TextView>(R.id.chipQuickExplain)
        val chipQuickTranslate = floatingView.findViewById<TextView>(R.id.chipQuickTranslate)
        val chipQuickReply = floatingView.findViewById<TextView>(R.id.chipQuickReply)

        val tokenInputRow = floatingView.findViewById<LinearLayout>(R.id.tokenInputRow)
        val etPopupToken = floatingView.findViewById<EditText>(R.id.etPopupToken)
        val btnSavePopupToken = floatingView.findViewById<Button>(R.id.btnSavePopupToken)

        scrollChat = floatingView.findViewById(R.id.scrollChat)
        chatContainer = floatingView.findViewById(R.id.chatContainer)
        typingIndicatorRow = floatingView.findViewById(R.id.typingIndicatorRow)
        val etPrompt = floatingView.findViewById<EditText>(R.id.etPrompt)
        val btnSendPrompt = floatingView.findViewById<ImageButton>(R.id.btnSendPrompt)
        val btnResizeHandle = floatingView.findViewById<ImageView>(R.id.btnResizeHandle)

        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        etPopupToken.setText(prefs.getString("api_key", ""))
        applyVisualPreferences()
        restoreSessionHistory()
        showCollapsedTriggerState()

        // Ketuk di luar jendela untuk menutup
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

        fun sendUserPrompt(customPrompt: String) {
            val prompt = customPrompt.trim()
            val apiKey = prefs.getString("api_key", "") ?: ""

            if (prompt.isEmpty()) return
            if (apiKey.isEmpty()) {
                plusMenuDrawer.visibility = View.VISIBLE
                tokenInputRow.visibility = View.VISIBLE
                btnPlusMenu.animate().rotation(45f).setDuration(220).start()
                Toast.makeText(this, "Tempel Gemini API Key dulu ya", Toast.LENGTH_SHORT).show()
                return
            }

            if (plusMenuDrawer.visibility == View.VISIBLE) {
                plusMenuDrawer.visibility = View.GONE
                btnPlusMenu.animate().rotation(0f).setDuration(220).start()
            }

            wakeFromSmartFreeze()
            triggerHaptic()
            val userTime = currentTimeLabel()
            addChatMessage(prompt, userTime, isUser = true)
            etPrompt.text.clear()
            btnSendPrompt.isEnabled = false
            typingIndicatorRow.visibility = View.VISIBLE
            tvIslandLabel.text = "Berpikir..."

            val screenBase64 = if (isScreenShareActive) captureCurrentScreenBase64() else null

            serviceScope.launch {
                val rawReply = callGeminiApi(apiKey, prompt, screenBase64)
                val cleanReply = sanitizeMarkdown(rawReply)
                val botTime = currentTimeLabel()
                lastBotReply = cleanReply

                chatHistory.add(SessionMessage("user", prompt, userTime))
                chatHistory.add(SessionMessage("model", cleanReply, botTime))
                if (chatHistory.size > 200) {
                    chatHistory.removeAt(0)
                    chatHistory.removeAt(0)
                }
                saveSessionHistory()

                typingIndicatorRow.visibility = View.GONE
                tvIslandLabel.text = if (isScreenShareActive) "Live Vision" else "Floamini"
                addChatMessage(cleanReply, botTime, isUser = false)
                btnSendPrompt.isEnabled = true
                triggerHaptic()
            }
        }

        // ----------------------------------------------------------------------
        // 1. INTERAKSI DYNAMIC ISLAND (SPRING PHYSICS + AUTO-HIDE REVEAL)
        // ----------------------------------------------------------------------
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
                        val diffX = abs(event.rawX - initialTouchX)
                        val diffY = abs(event.rawY - initialTouchY)
                        if (diffX < 18 && diffY < 18) {
                            triggerHaptic()
                            if (isPillAutoHidden) {
                                isPillAutoHidden = false
                                dynamicIslandView.alpha = 1.0f
                                openPopupChat(fromSiri = false)
                            } else {
                                openPopupChat(fromSiri = false)
                            }
                        } else {
                            scheduleAutoHideAndFreeze()
                        }
                        return true
                    }
                }
                return false
            }
        })

        // ----------------------------------------------------------------------
        // 2. INTERAKSI BUBBLE & XIAOMI EDGE PILL
        // ----------------------------------------------------------------------
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
                        val diffX = abs(event.rawX - initialTouchX)
                        val diffY = abs(event.rawY - initialTouchY)
                        if (diffX < 15 && diffY < 15) {
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
                        if (swipedInward) {
                            openPopupChat(fromSiri = false)
                        } else {
                            exitXiaomiEdgeMode()
                        }
                        return true
                    }
                }
                return false
            }
        })

        // ----------------------------------------------------------------------
        // 3. GESER & RESIZE JENDELA LIQUID GLASS
        // ----------------------------------------------------------------------
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
                }
                return false
            }
        })

        btnResizeHandle.setOnTouchListener(object : View.OnTouchListener {
            private var initialW = 0
            private var initialH = 0
            private var initialTouchX = 0f
            private var initialTouchY = 0f

            override fun onTouch(v: View, event: MotionEvent): Boolean {
                val density = resources.displayMetrics.density
                val minW = (280 * density).toInt()
                val minH = (320 * density).toInt()
                val maxW = (fullScreenWidth * 0.95f).toInt()
                val maxH = (fullScreenHeight * 0.82f).toInt()

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
                val permIntent = Intent(this, ScreenCapturePermissionActivity::class.java).apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                }
                startActivity(permIntent)
            } else {
                stopMediaProjection()
                Toast.makeText(this, "Live Screen Vision dihentikan", Toast.LENGTH_SHORT).show()
            }
        }

        btnPlusMenu.setOnClickListener {
            triggerHaptic()
            val isVisible = plusMenuDrawer.visibility == View.VISIBLE
            plusMenuDrawer.visibility = if (isVisible) View.GONE else View.VISIBLE
            btnPlusMenu.animate().rotation(if (isVisible) 0f else 45f).setDuration(220).start()
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
            triggerHaptic()
            prefPersona = when (prefPersona) {
                "asik" -> "ringkas"
                "ringkas" -> "detail"
                "detail" -> "teknis"
                else -> "asik"
            }
            prefs.edit().putString("ai_persona", prefPersona).apply()
            applyVisualPreferences()
            Toast.makeText(this, "Gaya: ${tvCurrentPersonaBadge.text}", Toast.LENGTH_SHORT).show()
        }

        actionCycleModel.setOnClickListener {
            triggerHaptic()
            prefModel = when (prefModel) {
                "gemini-3-flash-preview" -> "gemini-2.5-flash"
                "gemini-2.5-flash" -> "gemini-2.5-pro"
                else -> "gemini-3-flash-preview"
            }
            prefs.edit().putString("ai_model", prefModel).apply()
            applyVisualPreferences()
            Toast.makeText(this, "Model: ${tvCurrentModelBadge.text}", Toast.LENGTH_SHORT).show()
        }

        actionCopyLast.setOnClickListener {
            if (lastBotReply.isNotEmpty()) {
                val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                clipboard.setPrimaryClip(ClipData.newPlainText("Floamini Reply", lastBotReply))
                Toast.makeText(this, "Jawaban disalin", Toast.LENGTH_SHORT).show()
            }
        }

        actionExportChat.setOnClickListener {
            if (chatHistory.isEmpty()) {
                Toast.makeText(this, "Belum ada percakapan di sesi ini", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val sb = StringBuilder()
            for (msg in chatHistory) {
                val sender = if (msg.role == "user") "Kamu" else "Floamini"
                sb.append("[$sender - ${msg.timestamp}]\n${msg.text}\n\n")
            }
            val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            clipboard.setPrimaryClip(ClipData.newPlainText("Sesi Floamini", sb.toString().trim()))
            Toast.makeText(this, "Seluruh sesi disalin ke clipboard", Toast.LENGTH_SHORT).show()
        }

        actionResetChat.setOnClickListener {
            triggerHaptic()
            resetConversationSession()
            plusMenuDrawer.visibility = View.GONE
            btnPlusMenu.animate().rotation(0f).setDuration(200).start()
        }

        actionQuickForceStop.setOnClickListener {
            triggerHaptic()
            performQuickForceStop()
        }

        chipQuickScreenSummary.setOnClickListener {
            sendUserPrompt("Tolong ringkas isi layar yang lagi tampil sekarang secara singkat dan jelas.")
        }
        chipQuickExplain.setOnClickListener {
            sendUserPrompt("Jelasin maksud dari apa yang sedang kita bahas atau tampil di layar dengan bahasa gampang.")
        }
        chipQuickTranslate.setOnClickListener {
            sendUserPrompt("Terjemahkan teks utama yang tampil di layar atau yang barusan kita bahas ke bahasa Indonesia yang natural.")
        }
        chipQuickReply.setOnClickListener {
            sendUserPrompt("Buatin ide balasan yang asik, sopan, dan nyambung buat konteks ini.")
        }

        btnSendPrompt.setOnClickListener {
            sendUserPrompt(etPrompt.text.toString())
        }
    }

    // ==========================================================================
    // ANDROIDX REAL SPRING ANIMATION & LIQUID GLASS TRANSITIONS
    // ==========================================================================
    private fun animateSpringScale(target: View, finalScale: Float) {
        SpringAnimation(target, DynamicAnimation.SCALE_X, finalScale).apply {
            spring.dampingRatio = SpringForce.DAMPING_RATIO_LOW_BOUNCY
            spring.stiffness = SpringForce.STIFFNESS_MEDIUM
            start()
        }
        SpringAnimation(target, DynamicAnimation.SCALE_Y, finalScale).apply {
            spring.dampingRatio = SpringForce.DAMPING_RATIO_LOW_BOUNCY
            spring.stiffness = SpringForce.STIFFNESS_MEDIUM
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
                // Mode Siri: layar bersih total saat idle, langsung aktifkan Smart Freeze
                if (isFloatingViewAttached) {
                    windowManager.updateViewLayout(floatingView, params)
                }
                if (prefSmartFreeze) {
                    enterSmartFreezeState()
                }
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

        popupChatView.visibility = View.VISIBLE
        popupChatView.pivotX = popupChatView.layoutParams.width / 2f
        popupChatView.pivotY = if (fromSiri) popupChatView.layoutParams.height.toFloat() else 0f
        popupChatView.scaleX = 0.55f
        popupChatView.scaleY = 0.35f
        popupChatView.alpha = 0f

        val popupW = popupChatView.layoutParams.width
        val popupH = popupChatView.layoutParams.height
        params.x = ((fullScreenWidth - popupW) / 2).coerceIn(16, (fullScreenWidth - popupW - 16).coerceAtLeast(16))
        params.y = if (fromSiri) {
            ((fullScreenHeight - popupH) / 2).coerceIn(32, fullScreenHeight / 3)
        } else {
            (prefIslandPosYPx + (14 * resources.displayMetrics.density).toInt()).coerceIn(24, fullScreenHeight / 4)
        }
        params.flags = WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL or
                WindowManager.LayoutParams.FLAG_WATCH_OUTSIDE_TOUCH or
                WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN

        applyWindowBlur(enabled = prefLiquidBlur)
        windowManager.updateViewLayout(floatingView, params)

        popupChatView.animate()
            .alpha(prefPopupAlpha)
            .setDuration(260)
            .start()
        animateSpringScale(popupChatView, 1.0f)
    }

    private fun closePopupChat() {
        popupChatView.animate()
            .scaleX(0.45f)
            .scaleY(0.22f)
            .alpha(0f)
            .setDuration(200)
            .setInterpolator(DecelerateInterpolator())
            .withEndAction {
                showCollapsedTriggerState()
            }
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

        val pillWidthPx = (18 * resources.displayMetrics.density).toInt()
        params.x = if (snappedToRightEdge) (fullScreenWidth - pillWidthPx) else 0
        windowManager.updateViewLayout(floatingView, params)
        xiaomiEdgeView.animate().alpha(0.45f).setDuration(400).start()
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
        val appInfoIntent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
            data = Uri.parse("package:$packageName")
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        startActivity(appInfoIntent)
        stopSelf()
        exitProcess(0)
    }

    // ==========================================================================
    // GELEMBUNG CHAT KIRI-KANAN + TIMESTAMP + TAP TO COPY
    // ==========================================================================
    private fun addChatMessage(text: String, timeLabel: String, isUser: Boolean) {
        val wrapper = LinearLayout(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                setMargins(0, 6, 0, 6)
            }
            orientation = LinearLayout.VERTICAL
            gravity = if (isUser) Gravity.END else Gravity.START
        }

        val tvMessage = TextView(this).apply {
            this.text = text
            textSize = 13f
            lineHeight = (19 * resources.displayMetrics.density).toInt()
            setTextColor(Color.parseColor("#F8FAFC"))
            setPadding(28, 18, 28, 18)
            maxWidth = (252 * resources.displayMetrics.density).toInt()
            setBackgroundResource(if (isUser) R.drawable.bg_chat_user else R.drawable.bg_chat_bot)

            setOnClickListener {
                val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                clipboard.setPrimaryClip(ClipData.newPlainText("Floamini Message", text))
                Toast.makeText(this@FloatingAssistantService, "Pesan disalin", Toast.LENGTH_SHORT).show()
            }
        }

        val tvTime = TextView(this).apply {
            this.text = if (isUser) "Kamu • $timeLabel" else "Floamini • $timeLabel"
            textSize = 9.5f
            setTextColor(Color.parseColor("#64748B"))
            setPadding(8, 3, 8, 0)
        }

        wrapper.addView(tvMessage)
        wrapper.addView(tvTime)
        chatContainer.addView(wrapper)
        scrollChat.post { scrollChat.fullScroll(View.FOCUS_DOWN) }
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
    // LIVE SCREEN SHARE
    // ==========================================================================
    private fun startMediaProjection(resultCode: Int, data: Intent) {
        startForegroundNotification(withMediaProjection = true)
        val projectionManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        mediaProjection = projectionManager.getMediaProjection(resultCode, data)

        mediaProjection?.registerCallback(object : MediaProjection.Callback() {
            override fun onStop() {
                Handler(Looper.getMainLooper()).post {
                    stopMediaProjection()
                }
            }
        }, Handler(Looper.getMainLooper()))

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
        if (::btnScreenShare.isInitialized) {
            btnScreenShare.setColorFilter(Color.parseColor("#94A3B8"))
        }
        if (::tvScreenShareStatus.isInitialized) {
            tvScreenShareStatus.visibility = View.GONE
        }
        if (::tvIslandLabel.isInitialized) {
            tvIslandLabel.text = "Floamini"
        }
        if (::popupChatView.isInitialized) {
            popupChatView.setBackgroundResource(R.drawable.bg_liquid_glass_window)
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
        } catch (_: Exception) {
            null
        }
    }

    // ==========================================================================
    // KONEKSI GEMINI API
    // ==========================================================================
    private fun buildSystemInstructionText(): String {
        val memoryRule = "Penting: Selalu ingat dan hubungkan seluruh konteks percakapan sebelumnya dalam sesi ini agar obrolan tetap nyambung dan tidak pernah lupa apa yang sedang dibahas."
        val formatRule = "Aturan format wajib: Jangan pernah gunakan simbol markdown seperti tanda bintang (* atau **), tanda pagar (#), atau backtick (`). Tulis dalam teks polos yang bersih dan rapi."
        return when (prefPersona) {
            "ringkas" -> "Kamu adalah Floamini, asisten AI yang sigap dan langsung ke inti masalah. Jawab singkat dan padat dalam 1 sampai 2 kalimat utuh tanpa basa-basi. $memoryRule $formatRule"
            "detail" -> "Kamu adalah Floamini, asisten AI yang ramah dan informatif. Jelaskan jawaban secara runtut dan jelas dalam beberapa kalimat yang mudah dipahami. $memoryRule $formatRule"
            "teknis" -> "Kamu adalah Floamini, asisten teknis dan programmer yang cerdas. Berikan solusi langsung ke intinya dengan penjelasan logis dan ringkas. $memoryRule $formatRule"
            else -> "Kamu adalah Floamini, asisten AI yang asik, santai, ramah, dan tidak kaku seperti teman ngobrol yang pintar. Gunakan bahasa Indonesia yang natural dan enak dibaca. Jawab cukup pendek tapi tetap jelas dan berisi, minimal 1 sampai 3 kalimat utuh yang langsung menjawab inti pertanyaan pengguna tanpa bertele-tele. $memoryRule $formatRule"
        }
    }

    private suspend fun callGeminiApi(apiKey: String, prompt: String, screenBase64: String?): String = withContext(Dispatchers.IO) {
        try {
            val url = "https://generativelanguage.googleapis.com/v1beta/models/$prefModel:generateContent?key=$apiKey"
            val contentsArray = JSONArray()

            for (msg in chatHistory) {
                contentsArray.put(JSONObject().apply {
                    put("role", msg.role)
                    put("parts", JSONArray().apply {
                        put(JSONObject().apply { put("text", msg.text) })
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
        try { unregisterReceiver(screenStateReceiver) } catch (_: Exception) {}
        mainHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
        mainHandler.removeCallbacks(autoHidePillRunnable)
        mainHandler.removeCallbacks(smartFreezeRunnable)
        dismissSiriAura()
        stopMediaProjection()
        serviceJob.cancel()
        if (isFloatingViewAttached && ::floatingView.isInitialized) {
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
    print("\nProyek Floamini v5.0 (Liquid Glass, Siri Mode, Custom Pill & Smart Freeze) siap di-push ke GitHub!")

if __name__ == "__main__":
    generate_project()
