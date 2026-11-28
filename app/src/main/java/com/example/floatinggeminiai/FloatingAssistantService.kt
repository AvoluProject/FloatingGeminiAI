package com.example.floatinggeminiai

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
