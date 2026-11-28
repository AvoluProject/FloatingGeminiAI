#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "=== [1/6] Memeriksa Izin Penyimpanan Internal ==="
if [ ! -d "/storage/emulated/0" ]; then
    termux-setup-storage
    sleep 3
fi

echo "=== [2/6] Menginstal JDK 17, Gradle, dan ARM64 AAPT2 ==="
pkg update -y
pkg install -y openjdk-17 gradle aapt2 wget unzip python

if [ -d "$PREFIX/lib/jvm/java-17-openjdk" ]; then
    export JAVA_HOME="$PREFIX/lib/jvm/java-17-openjdk"
elif [ -d "/data/data/com.termux/files/usr/lib/jvm/java-17-openjdk" ]; then
    export JAVA_HOME="/data/data/com.termux/files/usr/lib/jvm/java-17-openjdk"
fi
export PATH="$JAVA_HOME/bin:$PATH"

echo "=== [3/6] Menyiapkan Android SDK 34 ==="
SDK_DIR="$HOME/android-sdk"
mkdir -p "$SDK_DIR/cmdline-tools"

if [ ! -d "$SDK_DIR/cmdline-tools/latest" ]; then
    cd "$SDK_DIR/cmdline-tools"
    rm -f cmdtools.zip
    wget -q --show-progress https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O cmdtools.zip
    unzip -q cmdtools.zip
    mv cmdline-tools latest
    rm -f cmdtools.zip
fi

export ANDROID_HOME="$SDK_DIR"
export ANDROID_SDK_ROOT="$SDK_DIR"
export PATH="$SDK_DIR/cmdline-tools/latest/bin:$SDK_DIR/platform-tools:$PATH"

if [ ! -d "$SDK_DIR/platforms/android-34" ] || [ ! -d "$SDK_DIR/build-tools/34.0.0" ]; then
    yes | sdkmanager --sdk_root="$SDK_DIR" --licenses > /dev/null 2>&1 || true
    sdkmanager --sdk_root="$SDK_DIR" "platforms;android-34" "build-tools;34.0.0"
fi

echo "=== [4/6] Menjalankan Generator Floamini OS v7.0 ==="
cd "$HOME/FloatingGeminiAI"
python setup_project.py

if [ ! -f "app/floamini.jks" ]; then
    keytool -genkeypair -v -keystore app/floamini.jks -alias floamini_key \
        -keyalg RSA -keysize 2048 -validity 10000 \
        -storepass floamini_keystore_pass_2026 -keypass floamini_keystore_pass_2026 \
        -dname "CN=Floamini, OU=Mobile, O=AvoluProject, L=Yogyakarta, ST=DIY, C=ID"
fi

echo "=== [5/6] Compiling APK dengan Gradle ==="
gradle assembleDebug --no-daemon

echo "=== [6/6] Menyalin APK ke /storage/emulated/0/App Build ==="
OUT_DIR="/storage/emulated/0/App Build"
mkdir -p "$OUT_DIR"
cp -f app/build/outputs/apk/debug/app-debug.apk "$OUT_DIR/Floamini-OS-v7.0-LiquidGlass.apk"
echo "SUKSES! Tersimpan di: $OUT_DIR/Floamini-OS-v7.0-LiquidGlass.apk"
