plugins {
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
