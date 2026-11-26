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
