package com.example.floatinggeminiai

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
                    put("text", "Jawab dengan sangat singkat, padat, langsung ke inti pertanyaan tanpa basa-basi, dan JANGAN gunakan simbol markdown seperti tanda bintang (* atau **).

Pertanyaan: $prompt")
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
