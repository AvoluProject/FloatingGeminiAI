package com.example.floatinggeminiai

import android.Manifest
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
import android.content.pm.PackageManager
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
import android.text.Editable
import android.text.TextWatcher
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
import com.example.floatinggeminiai.ai.AiEngineRegistry
import com.example.floatinggeminiai.ai.AiProviderType
import com.example.floatinggeminiai.ai.AiRequestPayload
import com.example.floatinggeminiai.ai.ChatMessage
import com.example.floatinggeminiai.ai.ChatThread
import com.example.floatinggeminiai.ai.StreamEvent
import com.example.floatinggeminiai.data.ChatRepository
import com.example.floatinggeminiai.security.SecureVault
import com.example.floatinggeminiai.tools.ProcessedAttachment
import com.example.floatinggeminiai.tools.SmartToolsHelper
import com.example.floatinggeminiai.ui.VoiceWaveformView
import com.example.floatinggeminiai.voice.VoiceSystemManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.launch
import java.io.ByteArrayOutputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.UUID
import kotlin.math.abs
import kotlin.system.exitProcess

class FloatingAssistantService : Service() {

    companion object {
        const val ACTION_SCREEN_CAPTURE_RESULT = "ACTION_SCREEN_CAPTURE_RESULT"
        const val ACTION_RELOAD_SETTINGS = "ACTION_RELOAD_SETTINGS"
        const val ACTION_RESET_SESSION = "ACTION_RESET_SESSION"
        const val ACTION_TRIGGER_SIRI = "ACTION_TRIGGER_SIRI"
        const val ACTION_ATTACH_URI = "ACTION_ATTACH_URI"
        const val ACTION_AUDIO_PERMISSION_GRANTED = "ACTION_AUDIO_PERMISSION_GRANTED"
        const val ACTION_EXTERNAL_CONTEXT = "ACTION_EXTERNAL_CONTEXT"
    }

    private lateinit var windowManager: WindowManager
    private lateinit var floatingView: View
    private lateinit var params: WindowManager.LayoutParams
    private var isFloatingViewAttached = false

    private lateinit var vault: SecureVault
    private lateinit var repo: ChatRepository
    private var voiceManager: VoiceSystemManager? = null

    private var siriGlowView: SiriEdgeGlowView? = null
    private var isSiriAuraActive = false

    private val serviceJob = Job()
    private val serviceScope = CoroutineScope(Dispatchers.Main + serviceJob)
    private var activeGenerationJob: Job? = null

    // UI References
    private lateinit var dynamicIslandView: LinearLayout
    private lateinit var ivIslandSparkle: ImageView
    private lateinit var tvIslandLabel: TextView
    private lateinit var viewIslandPulseDot: View
    private lateinit var bubbleView: FrameLayout
    private lateinit var xiaomiEdgeView: FrameLayout
    private lateinit var popupChatView: LinearLayout

    private lateinit var tvActiveProviderHeader: TextView
    private lateinit var btnScreenShare: ImageView
    private lateinit var tvScreenShareStatus: TextView
    private lateinit var attachmentPreviewBar: LinearLayout
    private lateinit var tvAttachmentName: TextView
    private lateinit var tvCompareBadge: TextView
    private lateinit var tvCurrentPersonaBadge: TextView

    private lateinit var scrollChat: ScrollView
    private lateinit var chatContainer: LinearLayout
    private lateinit var typingIndicatorRow: LinearLayout
    private lateinit var tvThinkingLabel: TextView
    private lateinit var voiceWaveformBar: LinearLayout
    private lateinit var tvVoiceStatusLabel: TextView
    private lateinit var voiceWaveformView: VoiceWaveformView
    private lateinit var etPrompt: EditText
    private lateinit var btnSendPrompt: ImageButton

    // State
    private val mainHandler = Handler(Looper.getMainLooper())
    private var snappedToRightEdge = false
    private var fullScreenWidth = 1080
    private var fullScreenHeight = 2400
    private var isPillAutoHidden = false
    private var isSmartFrozen = false
    private var isMiniWindowMode = false
    private var isCompareMode = false
    private var isVoiceChatLoop = false

    // Preferences
    private var activeProvider = AiProviderType.GEMINI
    private var prefAutoRouter = false
    private var prefOverlayStyle = "dynamic_island"
    private var prefPillAppearance = "standard"
    private var prefAutoHidePill = false
    private var prefSmartFreeze = true
    private var prefTapOutsideClose = true
    private var prefLiquidBlur = true
    private var prefHapticFeedback = true
    private var prefAutoSpeakTts = true
    private var prefTtsVoiceName = ""
    private var prefAnimSpeedMultiplier = 1.0f
    private var prefIslandWidthPx = 440
    private var prefIslandPosYPx = 32
    private var prefIslandOffsetXPx = 0
    private var prefPopupAlpha = 0.84f
    private var prefBubbleSizePx = 148
    private var prefPersona = "asik"
    private var prefCustomSystemInstruction = ""

    // Multi-Thread Session State
    private var allThreads = mutableListOf<ChatThread>()
    private lateinit var currentThread: ChatThread
    private var lastUserPrompt = ""
    private var lastBotReply = ""
    private var pendingAttachment: ProcessedAttachment? = null

    // Screen Capture
    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    private var isScreenShareActive = false
    private var captureWidth = 540
    private var captureHeight = 1200
    private var screenDensity = 320

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
                .setDuration((420 / prefAnimSpeedMultiplier).toLong())
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

    private val screenStateReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            when (intent?.action) {
                Intent.ACTION_SCREEN_OFF -> {
                    if (prefSmartFreeze) {
                        if (popupChatView.visibility == View.VISIBLE) {
                            popupChatView.visibility = View.GONE
                        }
                        dismissSiriAura()
                        voiceManager?.stopListening()
                        voiceManager?.stopSpeaking()
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
        vault = SecureVault(this)
        repo = ChatRepository(this)
        startForegroundNotification(withMediaProjection = false)
        setupScreenMetrics()
        loadUserPreferences()
        initVoiceSystem()
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
                    Toast.makeText(this, "Izin Screen Vision dibatalkan", Toast.LENGTH_SHORT).show()
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
                allThreads = repo.loadAllThreads()
                startNewConversationThread()
            }
            ACTION_TRIGGER_SIRI -> {
                triggerHaptic()
                wakeFromSmartFreeze()
                showSiriAura()
                openPopupChat(fromSiri = true)
            }
            ACTION_AUDIO_PERMISSION_GRANTED -> {
                startVoiceChatSession()
            }
            ACTION_ATTACH_URI -> {
                val uriStr = intent.getStringExtra("uri_string") ?: return START_STICKY
                val uri = Uri.parse(uriStr)
                val processed = SmartToolsHelper.processUriAttachment(this, uri)
                if (processed != null) {
                    pendingAttachment = processed
                    tvAttachmentName.text = processed.displayName
                    attachmentPreviewBar.visibility = View.VISIBLE
                    if (popupChatView.visibility != View.VISIBLE) {
                        openPopupChat(fromSiri = false)
                    }
                } else {
                    Toast.makeText(this, "Gagal membaca file lampiran", Toast.LENGTH_SHORT).show()
                }
            }
            ACTION_EXTERNAL_CONTEXT -> {
                val sharedText = intent.getStringExtra("shared_text") ?: ""
                val uriStr = intent.getStringExtra("uri_string")
                val mode = intent.getStringExtra("source_mode") ?: "share"

                wakeFromSmartFreeze()
                openPopupChat(fromSiri = false)

                if (!uriStr.isNullOrEmpty()) {
                    val processed = SmartToolsHelper.processUriAttachment(this, Uri.parse(uriStr))
                    if (processed != null) {
                        pendingAttachment = processed
                        tvAttachmentName.text = processed.displayName
                        attachmentPreviewBar.visibility = View.VISIBLE
                    }
                }

                if (sharedText.isNotBlank()) {
                    val prefix = if (mode == "selection") "Bantu jelaskan atau proses teks pilihan ini:\n\"$sharedText\"" else sharedText
                    etPrompt.setText(prefix)
                    etPrompt.setSelection(etPrompt.text.length)
                }
            }
        }
        return START_STICKY
    }

    // ==========================================================================
    // VOICE SYSTEM (STT + TTS + WAVEFORM + INTERRUPTION)
    // ==========================================================================
    private fun initVoiceSystem() {
        voiceManager = VoiceSystemManager(
            context = this,
            onRmsChanged = { amp ->
                mainHandler.post { voiceWaveformView.setAmplitude(amp) }
            },
            onPartialSpeech = { partial ->
                mainHandler.post {
                    etPrompt.setText(partial)
                    etPrompt.setSelection(partial.length)
                }
            },
            onFinalSpeech = { finalSpoken ->
                mainHandler.post {
                    voiceWaveformView.stopAnimation()
                    voiceWaveformBar.visibility = View.GONE
                    etPrompt.setText(finalSpoken)
                    triggerSendPrompt(finalSpoken, fromVoice = true)
                }
            },
            onListeningStateChanged = { listening ->
                mainHandler.post {
                    if (listening) {
                        voiceWaveformBar.visibility = View.VISIBLE
                        tvVoiceStatusLabel.text = "Mendengarkan..."
                        voiceWaveformView.startAnimation()
                    } else if (voiceManager?.isSpeaking != true) {
                        voiceWaveformView.stopAnimation()
                        voiceWaveformBar.visibility = View.GONE
                    }
                }
            },
            onSpeakingStateChanged = { speaking ->
                mainHandler.post {
                    if (speaking) {
                        voiceWaveformBar.visibility = View.VISIBLE
                        tvVoiceStatusLabel.text = "Floamini Berbicara..."
                        voiceWaveformView.setAmplitude(0.65f)
                        voiceWaveformView.startAnimation()
                    } else {
                        voiceWaveformView.stopAnimation()
                        voiceWaveformBar.visibility = View.GONE
                    }
                }
            },
            onVoiceError = { err ->
                mainHandler.post {
                    voiceWaveformView.stopAnimation()
                    voiceWaveformBar.visibility = View.GONE
                    Toast.makeText(this, err, Toast.LENGTH_SHORT).show()
                }
            }
        )
    }

    private fun startVoiceChatSession() {
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            startActivity(Intent(this, AudioPermissionProxyActivity::class.java).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            })
            return
        }
        isVoiceChatLoop = true
        triggerHaptic()
        voiceManager?.startListening()
    }

    // ==========================================================================
    // AUTO SMART FREEZE ENGINE
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

        if (prefOverlayStyle == "siri_mode" && isFloatingViewAttached) {
            try {
                windowManager.removeViewImmediate(floatingView)
                isFloatingViewAttached = false
            } catch (_: Exception) {}
        }
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
    // SIRI EDGE GLOW AURA
    // ==========================================================================
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

        val glowView = SiriEdgeGlowView(this).apply { alpha = 0f }
        siriGlowView = glowView
        try {
            windowManager.addView(glowView, auraParams)
            glowView.startSiriAnimation()
            glowView.animate().alpha(1f).setDuration(340).start()
        } catch (_: Exception) {}
    }

    private fun dismissSiriAura() {
        val glowView = siriGlowView ?: return
        isSiriAuraActive = false
        siriGlowView = null
        glowView.animate()
            .alpha(0f)
            .setDuration(240)
            .withEndAction {
                glowView.stopAndFreezeAnimation()
                try { windowManager.removeViewImmediate(glowView) } catch (_: Exception) {}
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
                    vibrator.vibrate(VibrationEffect.createOneShot(14, VibrationEffect.DEFAULT_AMPLITUDE))
                } else {
                    @Suppress("DEPRECATION")
                    vibrator.vibrate(14)
                }
            }
        } catch (_: Exception) {}
    }

    private fun currentTimeLabel(): String = SimpleDateFormat("HH:mm", Locale.getDefault()).format(Date())

    private fun loadUserPreferences() {
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        val density = resources.displayMetrics.density
        activeProvider = AiProviderType.fromId(prefs.getString("active_provider_id", "gemini"))
        prefAutoRouter = prefs.getBoolean("auto_router_enabled", false)
        prefOverlayStyle = prefs.getString("overlay_style", "dynamic_island") ?: "dynamic_island"
        prefPillAppearance = prefs.getString("pill_appearance", "standard") ?: "standard"
        prefAutoHidePill = prefs.getBoolean("auto_hide_pill", false)
        prefSmartFreeze = prefs.getBoolean("smart_freeze", true)
        prefTapOutsideClose = prefs.getBoolean("tap_outside_close", true)
        prefLiquidBlur = prefs.getBoolean("liquid_blur", true)
        prefHapticFeedback = prefs.getBoolean("haptic_feedback", true)
        prefAutoSpeakTts = prefs.getBoolean("auto_speak_tts", true)
        prefTtsVoiceName = prefs.getString("tts_voice_name", "") ?: ""
        val animProg = prefs.getInt("anim_speed_prog", 5)
        prefAnimSpeedMultiplier = (0.5f + animProg * 0.1f).coerceIn(0.5f, 1.5f)
        prefIslandWidthPx = (prefs.getInt("island_width_dp", 164) * density).toInt()
        prefIslandPosYPx = (prefs.getInt("island_pos_y_dp", 12) * density).toInt()
        prefIslandOffsetXPx = (prefs.getInt("island_offset_x_dp", 0) * density).toInt()
        prefPopupAlpha = (prefs.getInt("popup_opacity", 84) / 100f).coerceIn(0.45f, 1.0f)
        prefBubbleSizePx = (54 * density).toInt()
        prefPersona = prefs.getString("ai_persona", "asik") ?: "asik"
        prefCustomSystemInstruction = prefs.getString("custom_system_instruction", "") ?: ""
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
        if (::tvActiveProviderHeader.isInitialized) {
            val modelName = vault.getSelectedModel(activeProvider)
            val prefix = if (prefAutoRouter) "Auto • " else ""
            tvActiveProviderHeader.text = "$prefix${activeProvider.shortBadge} • $modelName"
        }
        if (::tvCurrentPersonaBadge.isInitialized) {
            tvCurrentPersonaBadge.text = when (prefPersona) {
                "ringkas" -> "Singkat"
                "detail" -> "Detail"
                "teknis" -> "Teknis"
                else -> "Asik"
            }
        }
    }

    // ==========================================================================
    // MULTI-THREAD CONVERSATION & HISTORY MANAGEMENT
    // ==========================================================================
    private fun initializeThreads() {
        allThreads = repo.loadAllThreads()
        val activeId = repo.getActiveThreadId()
        val existing = allThreads.firstOrNull { it.id == activeId } ?: allThreads.firstOrNull()
        if (existing != null) {
            currentThread = existing
        } else {
            currentThread = ChatThread(
                id = UUID.randomUUID().toString(),
                title = "Obrolan Baru",
                updatedAt = System.currentTimeMillis()
            )
            allThreads.add(0, currentThread)
            repo.setActiveThreadId(currentThread.id)
        }
        renderCurrentThreadMessages()
    }

    private fun startNewConversationThread() {
        currentThread = ChatThread(
            id = UUID.randomUUID().toString(),
            title = "Obrolan Baru",
            updatedAt = System.currentTimeMillis()
        )
        allThreads.add(0, currentThread)
        repo.setActiveThreadId(currentThread.id)
        repo.saveAllThreads(allThreads)
        renderCurrentThreadMessages()
    }

    private fun renderCurrentThreadMessages() {
        chatContainer.removeAllViews()
        if (currentThread.messages.isEmpty()) {
            val greeting = "Halo! Floamini OS siap membantu dengan 11 AI Provider, Streaming SSE, Voice Chat, dan PDF/Screen Vision."
            lastBotReply = greeting
            addChatBubbleView(
                ChatMessage(UUID.randomUUID().toString(), "model", greeting, currentTimeLabel(), activeProvider.shortBadge),
                animateEntrance = false
            )
        } else {
            for (m in currentThread.messages) {
                if (m.role == "model") lastBotReply = m.text
                addChatBubbleView(m, animateEntrance = false)
            }
        }
    }

    private fun persistCurrentThread() {
        currentThread.updatedAt = System.currentTimeMillis()
        if (currentThread.title == "Obrolan Baru") {
            val firstUser = currentThread.messages.firstOrNull { it.role == "user" }
            if (firstUser != null) {
                currentThread.title = firstUser.text.take(34)
            }
        }
        allThreads.removeAll { it.id == currentThread.id }
        allThreads.add(0, currentThread)
        repo.setActiveThreadId(currentThread.id)
        repo.saveAllThreads(allThreads)
    }

    private fun startForegroundNotification(withMediaProjection: Boolean) {
        val channelId = "floamini_os_channel"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(channelId, "Floamini OS Assistant", NotificationManager.IMPORTANCE_LOW)
            getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
        }

        val notification: Notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("Floamini OS")
            .setContentText(if (withMediaProjection) "Live Screen Vision aktif" else "Multi-AI Liquid Glass aktif")
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

        // Bind Views
        dynamicIslandView = floatingView.findViewById(R.id.dynamicIslandView)
        ivIslandSparkle = floatingView.findViewById(R.id.ivIslandSparkle)
        tvIslandLabel = floatingView.findViewById(R.id.tvIslandLabel)
        viewIslandPulseDot = floatingView.findViewById(R.id.viewIslandPulseDot)
        bubbleView = floatingView.findViewById(R.id.bubbleView)
        xiaomiEdgeView = floatingView.findViewById(R.id.xiaomiEdgeView)
        popupChatView = floatingView.findViewById(R.id.popupChatView)

        val glassTitleBar = floatingView.findViewById<LinearLayout>(R.id.glassTitleBar)
        val btnCloseWindowX = floatingView.findViewById<ImageView>(R.id.btnCloseWindowX)
        val btnToggleMiniWindow = floatingView.findViewById<ImageView>(R.id.btnToggleMiniWindow)
        val btnSwitchProviderPill = floatingView.findViewById<LinearLayout>(R.id.btnSwitchProviderPill)
        tvActiveProviderHeader = floatingView.findViewById(R.id.tvActiveProviderHeader)
        btnScreenShare = floatingView.findViewById(R.id.btnScreenShare)
        val btnToolsDrawer = floatingView.findViewById<ImageView>(R.id.btnToolsDrawer)
        val btnPlusMenu = floatingView.findViewById<ImageView>(R.id.btnPlusMenu)

        tvScreenShareStatus = floatingView.findViewById(R.id.tvScreenShareStatus)
        attachmentPreviewBar = floatingView.findViewById(R.id.attachmentPreviewBar)
        tvAttachmentName = floatingView.findViewById(R.id.tvAttachmentName)
        val btnRemoveAttachment = floatingView.findViewById<TextView>(R.id.btnRemoveAttachment)

        val plusMenuDrawer = floatingView.findViewById<LinearLayout>(R.id.plusMenuDrawer)
        val smartToolsDrawer = floatingView.findViewById<LinearLayout>(R.id.smartToolsDrawer)

        val actionCompareAi = floatingView.findViewById<LinearLayout>(R.id.actionCompareAi)
        tvCompareBadge = floatingView.findViewById(R.id.tvCompareBadge)
        val actionRegenerate = floatingView.findViewById<LinearLayout>(R.id.actionRegenerate)
        val actionCyclePersona = floatingView.findViewById<LinearLayout>(R.id.actionCyclePersona)
        tvCurrentPersonaBadge = floatingView.findViewById(R.id.tvCurrentPersonaBadge)
        val actionCopyLast = floatingView.findViewById<LinearLayout>(R.id.actionCopyLast)
        val actionNewThread = floatingView.findViewById<LinearLayout>(R.id.actionNewThread)
        val actionOpenDashboard = floatingView.findViewById<LinearLayout>(R.id.actionOpenDashboard)
        val actionQuickForceStop = floatingView.findViewById<LinearLayout>(R.id.actionQuickForceStop)

        // 9 Quick Actions
        val qaTranslate = floatingView.findViewById<TextView>(R.id.qaTranslate)
        val qaSummarize = floatingView.findViewById<TextView>(R.id.qaSummarize)
        val qaRewrite = floatingView.findViewById<TextView>(R.id.qaRewrite)
        val qaExplain = floatingView.findViewById<TextView>(R.id.qaExplain)
        val qaBrainstorm = floatingView.findViewById<TextView>(R.id.qaBrainstorm)
        val qaCoding = floatingView.findViewById<TextView>(R.id.qaCoding)
        val qaGrammar = floatingView.findViewById<TextView>(R.id.qaGrammar)
        val qaExtractText = floatingView.findViewById<TextView>(R.id.qaExtractText)
        val qaAskSelection = floatingView.findViewById<TextView>(R.id.qaAskSelection)

        // Smart Tools
        val btnToolClipboard = floatingView.findViewById<Button>(R.id.btnToolClipboard)
        val btnToolCalculator = floatingView.findViewById<Button>(R.id.btnToolCalculator)
        val btnToolNotes = floatingView.findViewById<Button>(R.id.btnToolNotes)
        val btnToolHistory = floatingView.findViewById<Button>(R.id.btnToolHistory)
        val panelCalculator = floatingView.findViewById<LinearLayout>(R.id.panelCalculator)
        val etCalcExpression = floatingView.findViewById<EditText>(R.id.etCalcExpression)
        val tvCalcResult = floatingView.findViewById<TextView>(R.id.tvCalcResult)
        val btnEvalCalc = floatingView.findViewById<Button>(R.id.btnEvalCalc)
        val panelQuickNotes = floatingView.findViewById<LinearLayout>(R.id.panelQuickNotes)
        val etQuickNotes = floatingView.findViewById<EditText>(R.id.etQuickNotes)
        val btnSendNotesToAi = floatingView.findViewById<Button>(R.id.btnSendNotesToAi)
        val panelChatHistory = floatingView.findViewById<LinearLayout>(R.id.panelChatHistory)
        val etSearchChat = floatingView.findViewById<EditText>(R.id.etSearchChat)
        val historyThreadsList = floatingView.findViewById<LinearLayout>(R.id.historyThreadsList)

        scrollChat = floatingView.findViewById(R.id.scrollChat)
        chatContainer = floatingView.findViewById(R.id.chatContainer)
        typingIndicatorRow = floatingView.findViewById(R.id.typingIndicatorRow)
        tvThinkingLabel = floatingView.findViewById(R.id.tvThinkingLabel)
        val btnStopGeneration = floatingView.findViewById<TextView>(R.id.btnStopGeneration)

        voiceWaveformBar = floatingView.findViewById(R.id.voiceWaveformBar)
        tvVoiceStatusLabel = floatingView.findViewById(R.id.tvVoiceStatusLabel)
        voiceWaveformView = floatingView.findViewById(R.id.voiceWaveformView)
        val btnStopVoiceAction = floatingView.findViewById<TextView>(R.id.btnStopVoiceAction)

        val btnAttachFile = floatingView.findViewById<ImageButton>(R.id.btnAttachFile)
        val btnVoiceMic = floatingView.findViewById<ImageButton>(R.id.btnVoiceMic)
        etPrompt = floatingView.findViewById(R.id.etPrompt)
        btnSendPrompt = floatingView.findViewById(R.id.btnSendPrompt)
        val btnResizeHandle = floatingView.findViewById<ImageView>(R.id.btnResizeHandle)

        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        applyVisualPreferences()
        initializeThreads()
        showCollapsedTriggerState()

        // Tap outside window to close
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

        // Smooth Model Switching directly from Header Pill
        btnSwitchProviderPill.setOnClickListener {
            triggerHaptic()
            val configured = vault.getConfiguredProviders()
            val pool = if (configured.isNotEmpty()) configured else AiProviderType.values().toList()
            val nextIdx = (pool.indexOf(activeProvider) + 1) % pool.size
            activeProvider = pool[nextIdx]
            prefs.edit().putString("active_provider_id", activeProvider.id).apply()

            btnSwitchProviderPill.animate().scaleX(0.92f).scaleY(0.92f).setDuration(90).withEndAction {
                applyVisualPreferences()
                btnSwitchProviderPill.animate().scaleX(1f).scaleY(1f).setDuration(120).start()
            }.start()
            Toast.makeText(this, "Beralih ke ${activeProvider.displayName}", Toast.LENGTH_SHORT).show()
        }

        // Toggle Mini Window vs Full Floating Window
        btnToggleMiniWindow.setOnClickListener {
            triggerHaptic()
            isMiniWindowMode = !isMiniWindowMode
            val density = resources.displayMetrics.density
            val lp = popupChatView.layoutParams
            if (isMiniWindowMode) {
                lp.width = (280 * density).toInt()
                lp.height = (255 * density).toInt()
                Toast.makeText(this, "Mini Window Mode", Toast.LENGTH_SHORT).show()
            } else {
                lp.width = prefs.getInt("last_win_w", (352 * density).toInt())
                lp.height = prefs.getInt("last_win_h", (500 * density).toInt())
                Toast.makeText(this, "Full Floating Window", Toast.LENGTH_SHORT).show()
            }
            popupChatView.layoutParams = lp
            windowManager.updateViewLayout(floatingView, params)
        }

        // Dynamic Island Touch & Drag
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
                        if (abs(event.rawX - initialTouchX) < 18 && abs(event.rawY - initialTouchY) < 18) {
                            triggerHaptic()
                            isPillAutoHidden = false
                            dynamicIslandView.alpha = 1.0f
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

        // Bubble Touch & Snap
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
                        if (abs(event.rawX - initialTouchX) < 15 && abs(event.rawY - initialTouchY) < 15) {
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

        // Xiaomi Edge Pill
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
                        if (swipedInward) openPopupChat(fromSiri = false) else exitXiaomiEdgeMode()
                        return true
                    }
                }
                return false
            }
        })

        // Drag Window & Remember Position
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
                    MotionEvent.ACTION_UP -> {
                        prefs.edit()
                            .putInt("last_win_x", params.x)
                            .putInt("last_win_y", params.y)
                            .apply()
                        return true
                    }
                }
                return false
            }
        })

        // Resize Window & Remember Size
        btnResizeHandle.setOnTouchListener(object : View.OnTouchListener {
            private var initialW = 0
            private var initialH = 0
            private var initialTouchX = 0f
            private var initialTouchY = 0f

            override fun onTouch(v: View, event: MotionEvent): Boolean {
                val density = resources.displayMetrics.density
                val minW = (275 * density).toInt()
                val minH = (250 * density).toInt()
                val maxW = (fullScreenWidth * 0.96f).toInt()
                val maxH = (fullScreenHeight * 0.84f).toInt()

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
                    MotionEvent.ACTION_UP -> {
                        prefs.edit()
                            .putInt("last_win_w", popupChatView.width)
                            .putInt("last_win_h", popupChatView.height)
                            .apply()
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
                startActivity(Intent(this, ScreenCapturePermissionActivity::class.java).apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                })
            } else {
                stopMediaProjection()
                Toast.makeText(this, "Screen Vision dihentikan", Toast.LENGTH_SHORT).show()
            }
        }

        btnPlusMenu.setOnClickListener {
            triggerHaptic()
            smartToolsDrawer.visibility = View.GONE
            val show = plusMenuDrawer.visibility != View.VISIBLE
            plusMenuDrawer.visibility = if (show) View.VISIBLE else View.GONE
            btnPlusMenu.animate().rotation(if (show) 45f else 0f).setDuration(200).start()
        }

        btnToolsDrawer.setOnClickListener {
            triggerHaptic()
            plusMenuDrawer.visibility = View.GONE
            btnPlusMenu.animate().rotation(0f).setDuration(200).start()
            val show = smartToolsDrawer.visibility != View.VISIBLE
            smartToolsDrawer.visibility = if (show) View.VISIBLE else View.GONE
            if (show) {
                etQuickNotes.setText(repo.getQuickNotes())
                refreshHistoryList(historyThreadsList, "")
            }
        }

        // Plus Menu Actions
        actionCompareAi.setOnClickListener {
            triggerHaptic()
            isCompareMode = !isCompareMode
            tvCompareBadge.text = if (isCompareMode) "Compare AI: ON" else "Compare AI: OFF"
            tvCompareBadge.setTextColor(Color.parseColor(if (isCompareMode) "#34D399" else "#38BDF8"))
            Toast.makeText(
                this,
                if (isCompareMode) "Compare AI aktif: membandingkan 2 provider sekaligus" else "Compare AI dimatikan",
                Toast.LENGTH_SHORT
            ).show()
        }

        actionRegenerate.setOnClickListener {
            if (lastUserPrompt.isNotEmpty()) {
                plusMenuDrawer.visibility = View.GONE
                btnPlusMenu.animate().rotation(0f).setDuration(180).start()
                triggerSendPrompt(lastUserPrompt, fromVoice = false, isRegenerate = true)
            } else {
                Toast.makeText(this, "Belum ada pertanyaan untuk diulang", Toast.LENGTH_SHORT).show()
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
        }

        actionCopyLast.setOnClickListener {
            if (lastBotReply.isNotEmpty()) {
                val cb = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                cb.setPrimaryClip(ClipData.newPlainText("Floamini Reply", lastBotReply))
                Toast.makeText(this, "Jawaban terakhir disalin", Toast.LENGTH_SHORT).show()
            }
        }

        actionNewThread.setOnClickListener {
            triggerHaptic()
            startNewConversationThread()
            plusMenuDrawer.visibility = View.GONE
            btnPlusMenu.animate().rotation(0f).setDuration(180).start()
            Toast.makeText(this, "Sesi obrolan baru dimulai", Toast.LENGTH_SHORT).show()
        }

        actionOpenDashboard.setOnClickListener {
            closePopupChat()
            startActivity(Intent(this, MainActivity::class.java).apply { addFlags(Intent.FLAG_ACTIVITY_NEW_TASK) })
        }

        actionQuickForceStop.setOnClickListener {
            triggerHaptic()
            performQuickForceStop()
        }

        // 9 Quick Actions
        qaTranslate.setOnClickListener { triggerSendPrompt("Terjemahkan teks atau konten layar ini ke Bahasa Indonesia yang natural.") }
        qaSummarize.setOnClickListener { triggerSendPrompt("Ringkas poin-poin terpenting dari konteks atau layar ini secara padat.") }
        qaRewrite.setOnClickListener { triggerSendPrompt("Tulis ulang teks terakhir agar lebih rapi, jelas, dan enak dibaca.") }
        qaExplain.setOnClickListener { triggerSendPrompt("Jelaskan konsep atau isi layar ini dengan bahasa yang mudah dipahami.") }
        qaBrainstorm.setOnClickListener { triggerSendPrompt("Berikan 5 ide kreatif dan segar terkait topik yang sedang kita bahas.") }
        qaCoding.setOnClickListener { triggerSendPrompt("Bantu analisis, perbaiki bug, atau tulis kode bersih untuk kebutuhan ini.") }
        qaGrammar.setOnClickListener { triggerSendPrompt("Periksa dan perbaiki tata bahasa (grammar & ejaan) pada teks terakhir.") }
        qaExtractText.setOnClickListener { triggerSendPrompt("Ekstrak seluruh teks penting yang terlihat pada gambar atau layar secara rapi.") }
        qaAskSelection.setOnClickListener {
            // Explicit user action: read clipboard only when button is tapped
            val cb = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            val clipText = cb.primaryClip?.getItemAt(0)?.coerceToText(this)?.toString()?.trim() ?: ""
            if (clipText.isNotEmpty()) {
                triggerSendPrompt("Bantu jelaskan atau proses teks dari clipboard ini:\n\"$clipText\"")
            } else {
                Toast.makeText(this, "Clipboard saat ini kosong", Toast.LENGTH_SHORT).show()
            }
        }

        // Smart Tools Drawer Buttons
        btnToolClipboard.setOnClickListener {
            val cb = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            val clipText = cb.primaryClip?.getItemAt(0)?.coerceToText(this)?.toString()?.trim() ?: ""
            if (clipText.isNotEmpty()) {
                etPrompt.setText("Analisis teks clipboard ini:\n$clipText")
                smartToolsDrawer.visibility = View.GONE
            } else {
                Toast.makeText(this, "Clipboard kosong", Toast.LENGTH_SHORT).show()
            }
        }

        btnToolCalculator.setOnClickListener {
            panelCalculator.visibility = if (panelCalculator.visibility == View.VISIBLE) View.GONE else View.VISIBLE
            panelQuickNotes.visibility = View.GONE
            panelChatHistory.visibility = View.GONE
        }

        btnEvalCalc.setOnClickListener {
            val expr = etCalcExpression.text.toString()
            tvCalcResult.text = "= ${SmartToolsHelper.evaluateMathExpression(expr)}"
        }

        btnToolNotes.setOnClickListener {
            panelQuickNotes.visibility = if (panelQuickNotes.visibility == View.VISIBLE) View.GONE else View.VISIBLE
            panelCalculator.visibility = View.GONE
            panelChatHistory.visibility = View.GONE
        }

        etQuickNotes.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                repo.saveQuickNotes(s?.toString() ?: "")
            }
            override fun afterTextChanged(s: Editable?) {}
        })

        btnSendNotesToAi.setOnClickListener {
            val note = etQuickNotes.text.toString().trim()
            if (note.isNotEmpty()) {
                smartToolsDrawer.visibility = View.GONE
                triggerSendPrompt("Bantu rapikan atau kembangkan catatan cepat berikut:\n$note")
            }
        }

        btnToolHistory.setOnClickListener {
            panelChatHistory.visibility = if (panelChatHistory.visibility == View.VISIBLE) View.GONE else View.VISIBLE
            panelCalculator.visibility = View.GONE
            panelQuickNotes.visibility = View.GONE
            refreshHistoryList(historyThreadsList, etSearchChat.text.toString())
        }

        etSearchChat.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                refreshHistoryList(historyThreadsList, s?.toString() ?: "")
            }
            override fun afterTextChanged(s: Editable?) {}
        })

        // Attachments (PDF, Image, File)
        btnAttachFile.setOnClickListener {
            triggerHaptic()
            startActivity(Intent(this, FilePickerProxyActivity::class.java).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            })
        }

        btnRemoveAttachment.setOnClickListener {
            pendingAttachment = null
            attachmentPreviewBar.visibility = View.GONE
        }

        // Voice System Controls
        btnVoiceMic.setOnClickListener {
            if (voiceManager?.isListening == true) {
                voiceManager?.stopListening()
            } else {
                startVoiceChatSession()
            }
        }

        btnStopVoiceAction.setOnClickListener {
            isVoiceChatLoop = false
            voiceManager?.stopListening()
            voiceManager?.stopSpeaking()
            voiceWaveformView.stopAnimation()
            voiceWaveformBar.visibility = View.GONE
        }

        // Stop Generation Button
        btnStopGeneration.setOnClickListener {
            activeGenerationJob?.cancel()
            typingIndicatorRow.visibility = View.GONE
            btnSendPrompt.isEnabled = true
            tvIslandLabel.text = "Floamini"
            Toast.makeText(this, "Generasi dihentikan", Toast.LENGTH_SHORT).show()
        }

        // Send Prompt
        btnSendPrompt.setOnClickListener {
            isVoiceChatLoop = false
            triggerSendPrompt(etPrompt.text.toString(), fromVoice = false)
        }
    }

    private fun refreshHistoryList(container: LinearLayout, query: String) {
        container.removeAllViews()
        val matches = repo.searchThreads(query).take(5)
        if (matches.isEmpty()) {
            val emptyTv = TextView(this).apply {
                text = "Tidak ada riwayat cocok"
                textSize = 11sp
                setTextColor(Color.parseColor("#94A3B8"))
                setPadding(6, 6, 6, 6)
            }
            container.addView(emptyTv)
            return
        }

        for (thread in matches) {
            val row = TextView(this).apply {
                text = "• ${thread.title} (${thread.messages.size} pesan)"
                textSize = 11.5sp
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

    // ==========================================================================
    // SEND PROMPT, SSE STREAMING, COMPARE AI & AUTO-ROUTER
    // ==========================================================================
    private fun triggerSendPrompt(rawPrompt: String, fromVoice: Boolean = false, isRegenerate: Boolean = false) {
        val prompt = rawPrompt.trim()
        if (prompt.isEmpty()) return

        val attachment = pendingAttachment
        pendingAttachment = null
        attachmentPreviewBar.visibility = View.GONE

        val imagesList = mutableListOf<String>()
        if (isScreenShareActive) {
            captureCurrentScreenBase64()?.let { imagesList.add(it) }
        }
        if (attachment != null) {
            imagesList.addAll(attachment.imageBase64List)
        }

        val combinedPrompt = if (attachment != null && attachment.extractedText.isNotBlank()) {
            "$prompt\n\n--- Isi Lampiran (${attachment.displayName}) ---\n${attachment.extractedText}"
        } else {
            prompt
        }

        val chosenProvider = if (prefAutoRouter) {
            AiEngineRegistry.resolveAutoRoute(vault, activeProvider, combinedPrompt, imagesList.isNotEmpty())
        } else {
            activeProvider
        }

        val apiKey = vault.getApiKey(chosenProvider)
        if (apiKey.isEmpty()) {
            Toast.makeText(this, "API Key ${chosenProvider.displayName} belum diisi! Buka Settings.", Toast.LENGTH_LONG).show()
            return
        }

        floatingView.findViewById<LinearLayout>(R.id.plusMenuDrawer).visibility = View.GONE
        floatingView.findViewById<LinearLayout>(R.id.smartToolsDrawer).visibility = View.GONE
        floatingView.findViewById<ImageView>(R.id.btnPlusMenu).animate().rotation(0f).setDuration(180).start()

        wakeFromSmartFreeze()
        triggerHaptic()
        lastUserPrompt = prompt

        if (!isRegenerate) {
            val userMsg = ChatMessage(
                id = UUID.randomUUID().toString(),
                role = "user",
                text = prompt,
                timestamp = currentTimeLabel(),
                attachmentLabel = attachment?.displayName
            )
            currentThread.messages.add(userMsg)
            addChatBubbleView(userMsg, animateEntrance = true)
        }

        etPrompt.text.clear()
        btnSendPrompt.isEnabled = false
        typingIndicatorRow.visibility = View.VISIBLE
        tvIslandLabel.text = "Streaming..."

        activeGenerationJob?.cancel()
        activeGenerationJob = serviceScope.launch {
            if (isCompareMode) {
                executeDualCompareStream(chosenProvider, combinedPrompt, imagesList)
            } else {
                executeSingleProviderStream(chosenProvider, apiKey, combinedPrompt, imagesList, fromVoice)
            }
        }
    }

    private suspend fun executeSingleProviderStream(
        provider: AiProviderType,
        apiKey: String,
        promptText: String,
        imagesList: List<String>,
        fromVoice: Boolean
    ) {
        val modelId = vault.getSelectedModel(provider)
        tvThinkingLabel.text = "${provider.shortBadge} ($modelId) sedang mengetik..."

        val botTime = currentTimeLabel()
        val streamingTv = addStreamingBotBubble(provider.shortBadge, modelId, botTime)
        val buffer = StringBuilder()

        val payload = AiRequestPayload(
            provider = provider,
            apiKey = apiKey,
            model = modelId,
            customBaseUrl = vault.getCustomBaseUrl(),
            systemInstruction = buildSystemInstructionText(),
            history = currentThread.messages.dropLast(1).takeLast(14),
            userPrompt = promptText,
            imageBase64List = imagesList
        )

        AiEngineRegistry.getAdapter(provider).streamChat(payload).collect { event ->
            when (event) {
                is StreamEvent.Delta -> {
                    buffer.append(event.chunk)
                    streamingTv.text = "${buffer} ▍"
                    scrollChat.post { scrollChat.fullScroll(View.FOCUS_DOWN) }
                }
                is StreamEvent.Completed -> {
                    val finalReply = event.fullText.ifBlank { "Respons kosong dari ${provider.shortBadge}." }
                    streamingTv.text = SmartToolsHelper.formatRichMarkdown(finalReply)
                    lastBotReply = finalReply

                    val botMsg = ChatMessage(
                        id = UUID.randomUUID().toString(),
                        role = "model",
                        text = finalReply,
                        timestamp = botTime,
                        providerBadge = provider.shortBadge,
                        modelName = modelId
                    )
                    currentThread.messages.add(botMsg)
                    persistCurrentThread()
                    repo.recordUsage(provider, event.estimatedTokens)

                    typingIndicatorRow.visibility = View.GONE
                    btnSendPrompt.isEnabled = true
                    tvIslandLabel.text = if (isScreenShareActive) "Live Vision" else "Floamini"
                    triggerHaptic()

                    if ((fromVoice || isVoiceChatLoop) && prefAutoSpeakTts) {
                        val plainForSpeech = finalReply.replace("```", " ").replace("**", "").replace("`", "")
                        voiceManager?.speak(plainForSpeech, 1.05f, prefTtsVoiceName)
                    }
                }
                is StreamEvent.Error -> {
                    streamingTv.text = event.message
                    streamingTv.setTextColor(Color.parseColor("#FCA5A5"))
                    typingIndicatorRow.visibility = View.GONE
                    btnSendPrompt.isEnabled = true
                    tvIslandLabel.text = "Floamini"
                }
            }
        }
    }

    private suspend fun executeDualCompareStream(
        primary: AiProviderType,
        promptText: String,
        imagesList: List<String>
    ) {
        val configured = vault.getConfiguredProviders()
        val secondary = configured.firstOrNull { it != primary } ?: primary
        tvThinkingLabel.text = "Membandingkan ${primary.shortBadge} vs ${secondary.shortBadge}..."

        val (tvLeft, tvRight) = addSideBySideCompareCards(primary.shortBadge, secondary.shortBadge)
        val bufLeft = StringBuilder()
        val bufRight = StringBuilder()

        val job1 = serviceScope.async {
            val payload1 = AiRequestPayload(
                provider = primary,
                apiKey = vault.getApiKey(primary),
                model = vault.getSelectedModel(primary),
                customBaseUrl = vault.getCustomBaseUrl(),
                systemInstruction = buildSystemInstructionText(),
                history = currentThread.messages.dropLast(1).takeLast(10),
                userPrompt = promptText,
                imageBase64List = imagesList
            )
            AiEngineRegistry.getAdapter(primary).streamChat(payload1).collect { ev ->
                when (ev) {
                    is StreamEvent.Delta -> {
                        bufLeft.append(ev.chunk)
                        tvLeft.text = "${bufLeft} ▍"
                    }
                    is StreamEvent.Completed -> {
                        tvLeft.text = SmartToolsHelper.formatRichMarkdown(ev.fullText)
                        repo.recordUsage(primary, ev.estimatedTokens)
                    }
                    is StreamEvent.Error -> tvLeft.text = ev.message
                }
            }
        }

        val job2 = serviceScope.async {
            val payload2 = AiRequestPayload(
                provider = secondary,
                apiKey = vault.getApiKey(secondary),
                model = vault.getSelectedModel(secondary),
                customBaseUrl = vault.getCustomBaseUrl(),
                systemInstruction = buildSystemInstructionText(),
                history = currentThread.messages.dropLast(1).takeLast(10),
                userPrompt = promptText,
                imageBase64List = imagesList
            )
            AiEngineRegistry.getAdapter(secondary).streamChat(payload2).collect { ev ->
                when (ev) {
                    is StreamEvent.Delta -> {
                        bufRight.append(ev.chunk)
                        tvRight.text = "${bufRight} ▍"
                        scrollChat.post { scrollChat.fullScroll(View.FOCUS_DOWN) }
                    }
                    is StreamEvent.Completed -> {
                        tvRight.text = SmartToolsHelper.formatRichMarkdown(ev.fullText)
                        repo.recordUsage(secondary, ev.estimatedTokens)
                    }
                    is StreamEvent.Error -> tvRight.text = ev.message
                }
            }
        }

        awaitAll(job1, job2)
        val mergedSummary = "[${primary.shortBadge}]: $bufLeft\n\n[${secondary.shortBadge}]: $bufRight"
        lastBotReply = mergedSummary
        currentThread.messages.add(
            ChatMessage(UUID.randomUUID().toString(), "model", mergedSummary, currentTimeLabel(), "Compare")
        )
        persistCurrentThread()
        typingIndicatorRow.visibility = View.GONE
        btnSendPrompt.isEnabled = true
        tvIslandLabel.text = "Floamini"
        triggerHaptic()
    }

    // ==========================================================================
    // CHAT BUBBLES & STAGGERED ENTRANCE ANIMATION
    // ==========================================================================
    private fun addChatBubbleView(msg: ChatMessage, animateEntrance: Boolean) {
        val isUser = (msg.role == "user")
        val wrapper = LinearLayout(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 6, 0, 6) }
            orientation = LinearLayout.VERTICAL
            gravity = if (isUser) Gravity.END else Gravity.START
        }

        val tvMessage = TextView(this).apply {
            text = if (isUser) msg.text else SmartToolsHelper.formatRichMarkdown(msg.text)
            textSize = 13f
            lineHeight = (19 * resources.displayMetrics.density).toInt()
            setTextColor(Color.parseColor("#F8FAFC"))
            setPadding(26, 16, 26, 16)
            maxWidth = (264 * resources.displayMetrics.density).toInt()
            setBackgroundResource(if (isUser) R.drawable.bg_chat_user else R.drawable.bg_chat_bot)
            setOnClickListener {
                val cb = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                cb.setPrimaryClip(ClipData.newPlainText("Floamini Message", msg.text))
                Toast.makeText(this@FloatingAssistantService, "Pesan disalin", Toast.LENGTH_SHORT).show()
            }
        }

        val metaText = if (isUser) {
            val att = if (!msg.attachmentLabel.isNullOrEmpty()) " • ${msg.attachmentLabel}" else ""
            "Kamu • ${msg.timestamp}$att"
        } else {
            "${msg.providerBadge} • ${msg.timestamp}"
        }

        val tvTime = TextView(this).apply {
            text = metaText
            textSize = 9.5f
            setTextColor(Color.parseColor("#64748B"))
            setPadding(8, 3, 8, 0)
        }

        wrapper.addView(tvMessage)
        wrapper.addView(tvTime)
        chatContainer.addView(wrapper)

        if (animateEntrance) {
            wrapper.alpha = 0f
            wrapper.translationY = 18f
            wrapper.animate()
                .alpha(1f)
                .translationY(0f)
                .setDuration((210 / prefAnimSpeedMultiplier).toLong())
                .setInterpolator(DecelerateInterpolator())
                .start()
        }
        scrollChat.post { scrollChat.fullScroll(View.FOCUS_DOWN) }
    }

    private fun addStreamingBotBubble(providerBadge: String, modelName: String, timeLabel: String): TextView {
        val wrapper = LinearLayout(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 6, 0, 6) }
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.START
        }

        val tvMessage = TextView(this).apply {
            text = "▍"
            textSize = 13f
            lineHeight = (19 * resources.displayMetrics.density).toInt()
            setTextColor(Color.parseColor("#F8FAFC"))
            setPadding(26, 16, 26, 16)
            maxWidth = (264 * resources.displayMetrics.density).toInt()
            setBackgroundResource(R.drawable.bg_chat_bot)
        }

        val tvTime = TextView(this).apply {
            text = "$providerBadge ($modelName) • $timeLabel"
            textSize = 9.5f
            setTextColor(Color.parseColor("#38BDF8"))
            setPadding(8, 3, 8, 0)
        }

        wrapper.addView(tvMessage)
        wrapper.addView(tvTime)
        chatContainer.addView(wrapper)
        scrollChat.post { scrollChat.fullScroll(View.FOCUS_DOWN) }
        return tvMessage
    }

    private fun addSideBySideCompareCards(leftTitle: String, rightTitle: String): Pair<TextView, TextView> {
        val row = LinearLayout(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 6, 0, 6) }
            orientation = LinearLayout.HORIZONTAL
        }

        fun createCol(title: String): Pair<LinearLayout, TextView> {
            val col = LinearLayout(this).apply {
                layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f).apply {
                    setMargins(3, 0, 3, 0)
                }
                orientation = LinearLayout.VERTICAL
                setBackgroundResource(R.drawable.bg_chat_bot)
                setPadding(16, 12, 16, 12)
            }
            val header = TextView(this).apply {
                text = title
                textSize = 10.5f
                setTextColor(Color.parseColor("#38BDF8"))
            }
            val body = TextView(this).apply {
                text = "▍"
                textSize = 12f
                setTextColor(Color.parseColor("#F8FAFC"))
            }
            col.addView(header)
            col.addView(body)
            return col to body
        }

        val (col1, tv1) = createCol(leftTitle)
        val (col2, tv2) = createCol(rightTitle)
        row.addView(col1)
        row.addView(col2)
        chatContainer.addView(row)
        return tv1 to tv2
    }

    // ==========================================================================
    // SPRING ANIMATIONS & WINDOW TRANSITIONS
    // ==========================================================================
    private fun animateSpringScale(target: View, finalScale: Float) {
        val stiff = SpringForce.STIFFNESS_MEDIUM * prefAnimSpeedMultiplier
        SpringAnimation(target, DynamicAnimation.SCALE_X, finalScale).apply {
            spring.dampingRatio = SpringForce.DAMPING_RATIO_LOW_BOUNCY
            spring.stiffness = stiff
            start()
        }
        SpringAnimation(target, DynamicAnimation.SCALE_Y, finalScale).apply {
            spring.dampingRatio = SpringForce.DAMPING_RATIO_LOW_BOUNCY
            spring.stiffness = stiff
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

        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        val density = resources.displayMetrics.density
        val savedW = prefs.getInt("last_win_w", (352 * density).toInt())
        val savedH = prefs.getInt("last_win_h", (500 * density).toInt())
        val lp = popupChatView.layoutParams
        lp.width = if (isMiniWindowMode) (280 * density).toInt() else savedW
        lp.height = if (isMiniWindowMode) (255 * density).toInt() else savedH
        popupChatView.layoutParams = lp

        popupChatView.visibility = View.VISIBLE
        popupChatView.pivotX = lp.width / 2f
        popupChatView.pivotY = if (fromSiri) lp.height.toFloat() else 0f
        popupChatView.scaleX = 0.55f
        popupChatView.scaleY = 0.35f
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

        popupChatView.animate()
            .alpha(prefPopupAlpha)
            .setDuration((240 / prefAnimSpeedMultiplier).toLong())
            .start()
        animateSpringScale(popupChatView, 1.0f)
    }

    private fun closePopupChat() {
        voiceManager?.stopListening()
        voiceManager?.stopSpeaking()
        popupChatView.animate()
            .scaleX(0.45f)
            .scaleY(0.22f)
            .alpha(0f)
            .setDuration((190 / prefAnimSpeedMultiplier).toLong())
            .setInterpolator(DecelerateInterpolator())
            .withEndAction { showCollapsedTriggerState() }
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
        snappedToRightEdge = (params.x + prefBubbleSizePx / 2) >= (fullScreenWidth / 2)
        val targetX = if (snappedToRightEdge) (fullScreenWidth - prefBubbleSizePx) else 0
        ValueAnimator.ofInt(params.x, targetX).apply {
            duration = 230
            interpolator = DecelerateInterpolator()
            addUpdateListener { anim ->
                params.x = anim.animatedValue as Int
                try { windowManager.updateViewLayout(floatingView, params) } catch (_: Exception) {}
            }
            start()
        }
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
        val pillW = (18 * resources.displayMetrics.density).toInt()
        params.x = if (snappedToRightEdge) (fullScreenWidth - pillW) else 0
        windowManager.updateViewLayout(floatingView, params)
        xiaomiEdgeView.animate().alpha(0.45f).setDuration(380).start()
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
        startActivity(Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
            data = Uri.parse("package:$packageName")
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        })
        stopSelf()
        exitProcess(0)
    }

    // ==========================================================================
    // LIVE SCREEN VISION (MEDIAPROJECTION)
    // ==========================================================================
    private fun startMediaProjection(resultCode: Int, data: Intent) {
        startForegroundNotification(withMediaProjection = true)
        val projectionManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        mediaProjection = projectionManager.getMediaProjection(resultCode, data)

        mediaProjection?.registerCallback(object : MediaProjection.Callback() {
            override fun onStop() {
                mainHandler.post { stopMediaProjection() }
            }
        }, mainHandler)

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
        if (::btnScreenShare.isInitialized) btnScreenShare.setColorFilter(Color.parseColor("#94A3B8"))
        if (::tvScreenShareStatus.isInitialized) tvScreenShareStatus.visibility = View.GONE
        if (::tvIslandLabel.isInitialized) tvIslandLabel.text = "Floamini"
        if (::popupChatView.isInitialized) popupChatView.setBackgroundResource(R.drawable.bg_liquid_glass_window)
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

            val cropped = Bitmap.createBitmap(bitmap, 0, 0, captureWidth, captureHeight)
            val out = ByteArrayOutputStream()
            cropped.compress(Bitmap.CompressFormat.JPEG, 68, out)
            bitmap.recycle()
            cropped.recycle()
            Base64.encodeToString(out.toByteArray(), Base64.NO_WRAP)
        } catch (_: Exception) {
            null
        }
    }

    private fun buildSystemInstructionText(): String {
        val basePersona = when (prefPersona) {
            "ringkas" -> "Kamu adalah Floamini, asisten AI yang sigap dan padat. Jawab langsung ke inti dalam 1-2 kalimat."
            "detail" -> "Kamu adalah Floamini, asisten AI yang ramah dan informatif. Jelaskan jawaban secara runtut dan jelas."
            "teknis" -> "Kamu adalah Floamini, asisten teknis dan software architect cerdas. Berikan solusi terstruktur."
            else -> "Kamu adalah Floamini, asisten AI yang asik, santai, cerdas, dan terasa menyatu dengan sistem operasi Android."
        }
        val custom = if (prefCustomSystemInstruction.isNotBlank()) "\nInstruksi Tambahan Pengguna: $prefCustomSystemInstruction" else ""
        return "$basePersona Selalu ingat konteks percakapan sebelumnya dalam sesi ini.$custom"
    }

    override fun onDestroy() {
        super.onDestroy()
        try { unregisterReceiver(screenStateReceiver) } catch (_: Exception) {}
        mainHandler.removeCallbacks(transformToXiaomiEdgeRunnable)
        mainHandler.removeCallbacks(autoHidePillRunnable)
        mainHandler.removeCallbacks(smartFreezeRunnable)
        voiceManager?.release()
        dismissSiriAura()
        stopMediaProjection()
        activeGenerationJob?.cancel()
        serviceJob.cancel()
        if (isFloatingViewAttached && ::floatingView.isInitialized) {
            try { windowManager.removeView(floatingView) } catch (_: Exception) {}
        }
    }
}
