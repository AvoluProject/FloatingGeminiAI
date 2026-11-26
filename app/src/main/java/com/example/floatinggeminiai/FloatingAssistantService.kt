package com.example.floatinggeminiai

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
import android.view.animation.OvershootInterpolator
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
        private const val KEY_SESSION_HISTORY = "session_history_json"
    }

    private lateinit var windowManager: WindowManager
    private lateinit var floatingView: View
    private lateinit var params: WindowManager.LayoutParams
    private val serviceJob = Job()
    private val serviceScope = CoroutineScope(Dispatchers.Main + serviceJob)

    // Komponen UI Utama
    private lateinit var dynamicIslandView: LinearLayout
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

    // State Posisi & Mode Overlay
    private val edgeHandler = Handler(Looper.getMainLooper())
    private var snappedToRightEdge = false
    private var fullScreenWidth = 1080
    private var fullScreenHeight = 2400

    // Pengaturan Dinamis
    private var prefOverlayStyle = "dynamic_island"
    private var prefTapOutsideClose = true
    private var prefLiquidBlur = true
    private var prefHapticFeedback = true
    private var prefIslandWidthPx = 450
    private var prefIslandPosYPx = 32
    private var prefIslandOffsetXPx = 0
    private var prefPopupAlpha = 0.86f
    private var prefBubbleSizePx = 148
    private var prefPersona = "asik"
    private var prefModel = "gemini-3-flash-preview"

    // Data Model Pesan Sesi
    data class SessionMessage(val role: String, val text: String, val timestamp: String)
    private val chatHistory = mutableListOf<SessionMessage>()
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
        .readTimeout(35, TimeUnit.SECONDS)
        .build()

    private val transformToXiaomiEdgeRunnable = Runnable {
        if (prefOverlayStyle == "xiaomi_edge" && bubbleView.visibility == View.VISIBLE) {
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
                if (popupChatView.visibility != View.VISIBLE) {
                    showCollapsedTriggerState()
                }
            }
            ACTION_RESET_SESSION -> {
                if (::chatContainer.isInitialized && ::scrollChat.isInitialized) {
                    resetConversationSession()
                }
            }
        }
        return START_STICKY
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
        prefTapOutsideClose = prefs.getBoolean("tap_outside_close", true)
        prefLiquidBlur = prefs.getBoolean("liquid_blur", true)
        prefHapticFeedback = prefs.getBoolean("haptic_feedback", true)
        prefIslandWidthPx = (prefs.getInt("island_width_dp", 168) * density).toInt()
        prefIslandPosYPx = (prefs.getInt("island_pos_y_dp", 12) * density).toInt()
        prefIslandOffsetXPx = (prefs.getInt("island_offset_x_dp", 0) * density).toInt()
        prefPopupAlpha = (prefs.getInt("popup_opacity", 82) / 100f).coerceIn(0.45f, 1.0f)
        prefBubbleSizePx = (54 * density).toInt()
        prefPersona = prefs.getString("ai_persona", "asik") ?: "asik"
        prefModel = prefs.getString("ai_model", "gemini-3-flash-preview") ?: "gemini-3-flash-preview"
    }

    private fun applyVisualPreferences() {
        if (::dynamicIslandView.isInitialized) {
            val lp = dynamicIslandView.layoutParams
            lp.width = prefIslandWidthPx
            dynamicIslandView.layoutParams = lp
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
    // MEMORI SESI PERMANEN (ANTI-LUPA KONTEKS OBROLAN)
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
            val greeting = "Hai! Floamini sudah siap di Dynamic Island kamu. Sesi obrolan ini terus berjalan dan aku bakal ingat semua yang kita bahas!"
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
        val resetMsg = "Sesi obrolan Floamini sudah di-reset bersih. Yuk mulai bahasan baru!"
        lastBotReply = resetMsg
        addChatMessage(resetMsg, currentTimeLabel(), isUser = false)
    }

    private fun startForegroundNotification(withMediaProjection: Boolean) {
        val channelId = "floamini_dynamic_island_channel"
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
            .setContentText(if (withMediaProjection) "Live Screen Vision aktif" else "Dynamic Island AI siap digunakan")
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

        dynamicIslandView = floatingView.findViewById(R.id.dynamicIslandView)
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

        // ----------------------------------------------------------------------
        // TAP DI LUAR JENDELA UNTUK MENUTUP KEMBALI KE DYNAMIC ISLAND / BUBBLE
        // ----------------------------------------------------------------------
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
        // 1. INTERAKSI DYNAMIC ISLAND (TAP UNTUK EXPAND + GESER HALUS)
        // ----------------------------------------------------------------------
        dynamicIslandView.setOnTouchListener(object : View.OnTouchListener {
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
                        dynamicIslandView.animate().scaleX(1.06f).scaleY(1.06f).setDuration(140).start()
                        return true
                    }
                    MotionEvent.ACTION_MOVE -> {
                        val dx = (event.rawX - initialTouchX).toInt()
                        val dy = (event.rawY - initialTouchY).toInt()
                        if (abs(dx) > 12 || abs(dy) > 12) {
                            params.x = (initialX + dx).coerceIn(16, (fullScreenWidth - prefIslandWidthPx - 16).coerceAtLeast(16))
                            params.y = (initialY + dy).coerceIn(0, fullScreenHeight / 2)
                            windowManager.updateViewLayout(floatingView, params)
                        }
                        return true
                    }
                    MotionEvent.ACTION_UP -> {
                        dynamicIslandView.animate().scaleX(1.0f).scaleY(1.0f).setDuration(140).start()
                        val diffX = abs(event.rawX - initialTouchX)
                        val diffY = abs(event.rawY - initialTouchY)
                        if (diffX < 18 && diffY < 18) {
                            triggerHaptic()
                            openPopupChat()
                        }
                        return true
                    }
                }
                return false
            }
        })

        // ----------------------------------------------------------------------
        // 2. INTERAKSI BUBBLE & XIAOMI EDGE PILL (JIKA DIPILIH DI PENGATURAN)
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
                            triggerHaptic()
                            openPopupChat()
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
                            openPopupChat()
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

        // Tombol X untuk Close kembali ke Dynamic Island / Bubble
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
    // FLUID SPRING ANIMATIONS: DYNAMIC ISLAND <-> LIQUID GLASS WINDOW
    // ==========================================================================
    private fun showCollapsedTriggerState() {
        edgeHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
        popupChatView.visibility = View.GONE
        dynamicIslandView.visibility = View.GONE
        bubbleView.visibility = View.GONE
        xiaomiEdgeView.visibility = View.GONE

        params.flags = WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN
        applyWindowBlur(enabled = false)

        when (prefOverlayStyle) {
            "xiaomi_edge" -> {
                bubbleView.visibility = View.VISIBLE
                bubbleView.alpha = 1.0f
                params.x = if (snappedToRightEdge) (fullScreenWidth - prefBubbleSizePx) else 0
                params.y = fullScreenHeight / 3
                windowManager.updateViewLayout(floatingView, params)
                edgeHandler.postDelayed(transformToXiaomiEdgeRunnable, 2500L)
            }
            "classic_bubble" -> {
                bubbleView.visibility = View.VISIBLE
                bubbleView.alpha = 1.0f
                params.x = if (snappedToRightEdge) (fullScreenWidth - prefBubbleSizePx) else 0
                params.y = fullScreenHeight / 3
                windowManager.updateViewLayout(floatingView, params)
            }
            else -> {
                dynamicIslandView.visibility = View.VISIBLE
                dynamicIslandView.scaleX = 0.7f
                dynamicIslandView.scaleY = 0.7f
                dynamicIslandView.alpha = 0f
                params.x = (((fullScreenWidth - prefIslandWidthPx) / 2) + prefIslandOffsetXPx)
                    .coerceIn(12, (fullScreenWidth - prefIslandWidthPx - 12).coerceAtLeast(12))
                params.y = prefIslandPosYPx
                windowManager.updateViewLayout(floatingView, params)

                dynamicIslandView.animate()
                    .scaleX(1.0f)
                    .scaleY(1.0f)
                    .alpha(1.0f)
                    .setDuration(300)
                    .setInterpolator(OvershootInterpolator(1.1f))
                    .start()
            }
        }
    }

    private fun openPopupChat() {
        edgeHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
        dynamicIslandView.visibility = View.GONE
        xiaomiEdgeView.visibility = View.GONE
        bubbleView.visibility = View.GONE

        popupChatView.visibility = View.VISIBLE
        popupChatView.pivotX = popupChatView.layoutParams.width / 2f
        popupChatView.pivotY = 0f
        popupChatView.scaleX = 0.45f
        popupChatView.scaleY = 0.22f
        popupChatView.alpha = 0f

        val popupW = popupChatView.layoutParams.width
        params.x = ((fullScreenWidth - popupW) / 2).coerceIn(16, (fullScreenWidth - popupW - 16).coerceAtLeast(16))
        params.y = (prefIslandPosYPx + (14 * resources.displayMetrics.density).toInt()).coerceIn(24, fullScreenHeight / 4)
        params.flags = WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL or
                WindowManager.LayoutParams.FLAG_WATCH_OUTSIDE_TOUCH or
                WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN

        applyWindowBlur(enabled = prefLiquidBlur)
        windowManager.updateViewLayout(floatingView, params)

        popupChatView.animate()
            .scaleX(1.0f)
            .scaleY(1.0f)
            .alpha(prefPopupAlpha)
            .setDuration(340)
            .setInterpolator(OvershootInterpolator(0.85f))
            .start()
    }

    private fun closePopupChat() {
        popupChatView.animate()
            .scaleX(0.42f)
            .scaleY(0.18f)
            .alpha(0f)
            .setDuration(210)
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
                    params.blurBehindRadius = 26
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
            edgeHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
            edgeHandler.postDelayed(transformToXiaomiEdgeRunnable, 2500L)
        }
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
    }

    private fun exitXiaomiEdgeMode() {
        edgeHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
        xiaomiEdgeView.visibility = View.GONE
        bubbleView.visibility = View.VISIBLE
        bubbleView.alpha = 1.0f
        params.x = if (snappedToRightEdge) (fullScreenWidth - prefBubbleSizePx) else 0
        windowManager.updateViewLayout(floatingView, params)
        edgeHandler.postDelayed(transformToXiaomiEdgeRunnable, 2500L)
    }

    private fun performQuickForceStop() {
        Toast.makeText(this, "Menghentikan paksa Floamini...", Toast.LENGTH_SHORT).show()
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
            maxWidth = (250 * resources.displayMetrics.density).toInt()
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
    // LIVE SCREEN SHARE (MEDIA PROJECTION + ANDROID 14 CALLBACK SAFE)
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
        } catch (e: Exception) {
            null
        }
    }

    // ==========================================================================
    // KONEKSI GEMINI API (MEMORI SESI + GAYA ASIK + TANPA SIMBOL MARKDOWN)
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
