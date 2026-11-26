package com.example.floatinggeminiai

import android.app.StatusBarManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.graphics.drawable.Icon
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.RadioButton
import android.widget.RadioGroup
import android.widget.SeekBar
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import com.example.floatinggeminiai.ai.AiEngineRegistry
import com.example.floatinggeminiai.ai.AiProviderType
import com.example.floatinggeminiai.data.ChatRepository
import com.example.floatinggeminiai.security.SecureVault
import com.example.floatinggeminiai.voice.VoiceSystemManager
import com.google.android.material.switchmaterial.SwitchMaterial
import com.google.android.material.textfield.TextInputEditText
import com.google.android.material.textfield.TextInputLayout
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlin.system.exitProcess

class MainActivity : AppCompatActivity() {

    private val activityJob = Job()
    private val uiScope = CoroutineScope(Dispatchers.Main + activityJob)
    private lateinit var vault: SecureVault
    private lateinit var repo: ChatRepository
    private var voiceHelper: VoiceSystemManager? = null
    private var editingProvider = AiProviderType.GEMINI

    override fun onCreate(savedInstanceState: Bundle?) {
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        applySavedNightMode(prefs.getString("app_theme", "dark") ?: "dark")

        super.onCreate(savedInstanceState)

        if (!prefs.getBoolean("has_seen_welcome", false)) {
            startActivity(Intent(this, WelcomeActivity::class.java))
            finish()
            return
        }

        setContentView(R.layout.activity_main)

        vault = SecureVault(this)
        repo = ChatRepository(this)

        val tvAppVersionInfo = findViewById<TextView>(R.id.tvAppVersionInfo)
        val btnOpenWelcomeGuide = findViewById<Button>(R.id.btnOpenWelcomeGuide)
        val btnStartOverlay = findViewById<Button>(R.id.btnStartOverlay)
        val btnAddControlCenterTile = findViewById<Button>(R.id.btnAddControlCenterTile)
        val btnStopOverlay = findViewById<Button>(R.id.btnStopOverlay)
        val btnQuickForceStopMain = findViewById<Button>(R.id.btnQuickForceStopMain)

        // 1. Floating Window Controls
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

        val tvIslandWidthLabel = findViewById<TextView>(R.id.tvIslandWidthLabel)
        val sbIslandWidth = findViewById<SeekBar>(R.id.sbIslandWidth)
        val tvIslandPosYLabel = findViewById<TextView>(R.id.tvIslandPosYLabel)
        val sbIslandPosY = findViewById<SeekBar>(R.id.sbIslandPosY)
        val tvIslandOffsetXLabel = findViewById<TextView>(R.id.tvIslandOffsetXLabel)
        val sbIslandOffsetX = findViewById<SeekBar>(R.id.sbIslandOffsetX)

        // 2. Multi-AI Providers & Model Manager
        val swAutoRouter = findViewById<SwitchMaterial>(R.id.swAutoRouter)
        val spProviderSelector = findViewById<Spinner>(R.id.spProviderSelector)
        val tvProviderKeyStatus = findViewById<TextView>(R.id.tvProviderKeyStatus)
        val tvOpenProviderDocs = findViewById<TextView>(R.id.tvOpenProviderDocs)
        val etProviderApiKey = findViewById<TextInputEditText>(R.id.etProviderApiKey)
        val tilCustomBaseUrl = findViewById<TextInputLayout>(R.id.tilCustomBaseUrl)
        val etCustomBaseUrl = findViewById<TextInputEditText>(R.id.etCustomBaseUrl)
        val spModelPresetSelector = findViewById<Spinner>(R.id.spModelPresetSelector)
        val etActiveModelId = findViewById<TextInputEditText>(R.id.etActiveModelId)
        val btnSaveProviderConfig = findViewById<Button>(R.id.btnSaveProviderConfig)
        val btnTestProviderConnection = findViewById<Button>(R.id.btnTestProviderConnection)
        val tvProviderTestOutput = findViewById<TextView>(R.id.tvProviderTestOutput)

        // 3. Appearance & Animation
        val rgAppTheme = findViewById<RadioGroup>(R.id.rgAppTheme)
        val rbThemeSystem = findViewById<RadioButton>(R.id.rbThemeSystem)
        val rbThemeDark = findViewById<RadioButton>(R.id.rbThemeDark)
        val rbThemeLight = findViewById<RadioButton>(R.id.rbThemeLight)
        val swLiquidBlur = findViewById<SwitchMaterial>(R.id.swLiquidBlur)
        val swHapticFeedback = findViewById<SwitchMaterial>(R.id.swHapticFeedback)
        val tvOpacityLabel = findViewById<TextView>(R.id.tvOpacityLabel)
        val sbOpacity = findViewById<SeekBar>(R.id.sbOpacity)
        val tvAnimSpeedLabel = findViewById<TextView>(R.id.tvAnimSpeedLabel)
        val sbAnimSpeed = findViewById<SeekBar>(R.id.sbAnimSpeed)

        // 4. Voice & Persona
        val swAutoSpeakTts = findViewById<SwitchMaterial>(R.id.swAutoSpeakTts)
        val spTtsVoiceSelector = findViewById<Spinner>(R.id.spTtsVoiceSelector)
        val rgPersona = findViewById<RadioGroup>(R.id.rgPersona)
        val rbAsik = findViewById<RadioButton>(R.id.rbAsik)
        val rbRingkas = findViewById<RadioButton>(R.id.rbRingkas)
        val rbDetail = findViewById<RadioButton>(R.id.rbDetail)
        val rbTeknis = findViewById<RadioButton>(R.id.rbTeknis)
        val etCustomSystemInstruction = findViewById<TextInputEditText>(R.id.etCustomSystemInstruction)

        // 5. Privacy, Data & Usage
        val tvUsageStatistics = findViewById<TextView>(R.id.tvUsageStatistics)
        val btnClearAllHistoryMain = findViewById<Button>(R.id.btnClearAllHistoryMain)
        val btnResetUsageStats = findViewById<Button>(R.id.btnResetUsageStats)
        val btnWipeVaultKeys = findViewById<Button>(R.id.btnWipeVaultKeys)
        val btnSaveAllSettings = findViewById<Button>(R.id.btnSaveAllSettings)

        try {
            val pInfo = packageManager.getPackageInfo(packageName, 0)
            tvAppVersionInfo.text = "v${pInfo.versionName} • 11 AI Engines • Encrypted Vault"
        } catch (_: Exception) {}

        // Load Saved Values
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
        swAutoRouter.isChecked = prefs.getBoolean("auto_router_enabled", false)
        swLiquidBlur.isChecked = prefs.getBoolean("liquid_blur", true)
        swHapticFeedback.isChecked = prefs.getBoolean("haptic_feedback", true)
        swAutoSpeakTts.isChecked = prefs.getBoolean("auto_speak_tts", true)

        when (prefs.getString("app_theme", "dark")) {
            "system" -> rbThemeSystem.isChecked = true
            "light" -> rbThemeLight.isChecked = true
            else -> rbThemeDark.isChecked = true
        }

        val savedIslandW = prefs.getInt("island_width_dp", 164)
        sbIslandWidth.progress = (savedIslandW - 110).coerceIn(0, 130)
        tvIslandWidthLabel.text = "Lebar Pil Dynamic Island: ${savedIslandW}dp"

        val savedIslandY = prefs.getInt("island_pos_y_dp", 12)
        sbIslandPosY.progress = savedIslandY.coerceIn(0, 70)
        tvIslandPosYLabel.text = "Posisi Vertikal Atas (Y): ${savedIslandY}dp"

        val savedIslandX = prefs.getInt("island_offset_x_dp", 0)
        sbIslandOffsetX.progress = (savedIslandX + 80).coerceIn(0, 160)
        tvIslandOffsetXLabel.text = "Geser Horizontal Kamera (X): ${savedIslandX}dp"

        val savedOpacity = prefs.getInt("popup_opacity", 84)
        sbOpacity.progress = (savedOpacity - 45).coerceIn(0, 55)
        tvOpacityLabel.text = "Transparansi Liquid Glass: ${savedOpacity}%"

        val savedAnimProg = prefs.getInt("anim_speed_prog", 5)
        sbAnimSpeed.progress = savedAnimProg.coerceIn(0, 10)
        val speedMult = 0.5f + (savedAnimProg * 0.1f)
        tvAnimSpeedLabel.text = String.format("Kecepatan Spring Animation: %.1fx", speedMult)

        when (prefs.getString("ai_persona", "asik")) {
            "ringkas" -> rbRingkas.isChecked = true
            "detail" -> rbDetail.isChecked = true
            "teknis" -> rbTeknis.isChecked = true
            else -> rbAsik.isChecked = true
        }
        etCustomSystemInstruction.setText(prefs.getString("custom_system_instruction", ""))
        tvUsageStatistics.text = repo.getUsageSummaryText()

        // Setup 11 AI Provider Selector
        val providers = AiProviderType.values().toList()
        editingProvider = AiProviderType.fromId(prefs.getString("active_provider_id", "gemini"))
        spProviderSelector.adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_dropdown_item,
            providers.map { p ->
                val mark = if (vault.getApiKey(p).isNotEmpty()) " [Aktif]" else ""
                "${p.displayName}$mark"
            }
        )
        spProviderSelector.setSelection(providers.indexOf(editingProvider).coerceAtLeast(0))

        fun bindProviderFields(provider: AiProviderType) {
            editingProvider = provider
            val savedKey = vault.getApiKey(provider)
            etProviderApiKey.setText(savedKey)
            if (savedKey.isNotEmpty()) {
                tvProviderKeyStatus.text = "Status Key: Terenkripsi & Siap"
                tvProviderKeyStatus.setTextColor(Color.parseColor("#34D399"))
            } else {
                tvProviderKeyStatus.text = "Status Key: Belum diisi"
                tvProviderKeyStatus.setTextColor(Color.parseColor("#FBBF24"))
            }

            tilCustomBaseUrl.visibility = if (provider == AiProviderType.CUSTOM) View.VISIBLE else View.GONE
            etCustomBaseUrl.setText(vault.getCustomBaseUrl())

            val models = provider.availableModels
            spModelPresetSelector.adapter = ArrayAdapter(
                this,
                android.R.layout.simple_spinner_dropdown_item,
                models
            )
            val currentModel = vault.getSelectedModel(provider)
            etActiveModelId.setText(currentModel)
            val idx = models.indexOf(currentModel)
            if (idx >= 0) spModelPresetSelector.setSelection(idx)
        }

        bindProviderFields(editingProvider)

        spProviderSelector.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                bindProviderFields(providers[position])
            }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }

        spModelPresetSelector.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                val chosen = editingProvider.availableModels[position]
                if (chosen != "custom-model") {
                    etActiveModelId.setText(chosen)
                }
            }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }

        tvOpenProviderDocs.setOnClickListener {
            try {
                startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(editingProvider.docsUrl)))
            } catch (_: Exception) {
                Toast.makeText(this, "Kunjungi ${editingProvider.docsUrl}", Toast.LENGTH_LONG).show()
            }
        }

        btnSaveProviderConfig.setOnClickListener {
            val key = etProviderApiKey.text.toString().trim()
            val modelId = etActiveModelId.text.toString().trim().ifEmpty { editingProvider.defaultModel }
            vault.setApiKey(editingProvider, key)
            vault.setSelectedModel(editingProvider, modelId)
            if (editingProvider == AiProviderType.CUSTOM) {
                vault.setCustomBaseUrl(etCustomBaseUrl.text.toString())
            }
            prefs.edit().putString("active_provider_id", editingProvider.id).apply()
            bindProviderFields(editingProvider)
            Toast.makeText(this, "${editingProvider.displayName} ($modelId) disimpan & dijadikan aktif!", Toast.LENGTH_SHORT).show()
        }

        btnTestProviderConnection.setOnClickListener {
            val key = etProviderApiKey.text.toString().trim()
            val modelId = etActiveModelId.text.toString().trim().ifEmpty { editingProvider.defaultModel }
            val customUrl = etCustomBaseUrl.text.toString().trim()
            if (key.isEmpty()) {
                tvProviderTestOutput.text = "Masukkan API Key terlebih dahulu"
                tvProviderTestOutput.setTextColor(Color.parseColor("#FBBF24"))
                return@setOnClickListener
            }
            btnTestProviderConnection.isEnabled = false
            tvProviderTestOutput.text = "Menguji koneksi ${editingProvider.shortBadge}..."
            tvProviderTestOutput.setTextColor(Color.parseColor("#38BDF8"))

            uiScope.launch {
                val (ok, msg) = withContext(Dispatchers.IO) {
                    AiEngineRegistry.getAdapter(editingProvider).testConnection(key, modelId, customUrl)
                }
                btnTestProviderConnection.isEnabled = true
                tvProviderTestOutput.text = msg
                tvProviderTestOutput.setTextColor(Color.parseColor(if (ok) "#34D399" else "#FCA5A5"))
            }
        }

        // Populate TTS Voice Selector
        voiceHelper = VoiceSystemManager(this, {}, {}, {}, {}, {}, {})
        android.os.Handler(mainLooper).postDelayed({
            val voices = voiceHelper?.getAvailableVoices() ?: emptyList()
            val voiceNames = mutableListOf("Default Sistem (Indonesia)")
            voiceNames.addAll(voices.map { "${it.locale.displayLanguage} - ${it.name}" })
            spTtsVoiceSelector.adapter = ArrayAdapter(
                this,
                android.R.layout.simple_spinner_dropdown_item,
                voiceNames
            )
            val savedVoice = prefs.getString("tts_voice_name", "") ?: ""
            if (savedVoice.isNotEmpty()) {
                val idx = voices.indexOfFirst { it.name == savedVoice }
                if (idx >= 0) spTtsVoiceSelector.setSelection(idx + 1)
            }
            spTtsVoiceSelector.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
                override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                    val chosenVoice = if (position == 0) "" else voices.getOrNull(position - 1)?.name ?: ""
                    prefs.edit().putString("tts_voice_name", chosenVoice).apply()
                }
                override fun onNothingSelected(parent: AdapterView<*>?) {}
            }
        }, 600L)

        // SeekBar Listeners
        sbIslandWidth.setOnSeekBarChangeListener(simpleSeek { p ->
            tvIslandWidthLabel.text = "Lebar Pil Dynamic Island: ${p + 110}dp"
        })
        sbIslandPosY.setOnSeekBarChangeListener(simpleSeek { p ->
            tvIslandPosYLabel.text = "Posisi Vertikal Atas (Y): ${p}dp"
        })
        sbIslandOffsetX.setOnSeekBarChangeListener(simpleSeek { p ->
            tvIslandOffsetXLabel.text = "Geser Horizontal Kamera (X): ${p - 80}dp"
        })
        sbOpacity.setOnSeekBarChangeListener(simpleSeek { p ->
            tvOpacityLabel.text = "Transparansi Liquid Glass: ${p + 45}%"
        })
        sbAnimSpeed.setOnSeekBarChangeListener(simpleSeek { p ->
            tvAnimSpeedLabel.text = String.format("Kecepatan Spring Animation: %.1fx", 0.5f + p * 0.1f)
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
            val themeChoice = when (rgAppTheme.checkedRadioButtonId) {
                R.id.rbThemeSystem -> "system"
                R.id.rbThemeLight -> "light"
                else -> "dark"
            }

            val key = etProviderApiKey.text.toString().trim()
            val modelId = etActiveModelId.text.toString().trim().ifEmpty { editingProvider.defaultModel }
            vault.setApiKey(editingProvider, key)
            vault.setSelectedModel(editingProvider, modelId)
            if (editingProvider == AiProviderType.CUSTOM) {
                vault.setCustomBaseUrl(etCustomBaseUrl.text.toString())
            }

            prefs.edit()
                .putString("active_provider_id", editingProvider.id)
                .putBoolean("auto_router_enabled", swAutoRouter.isChecked)
                .putString("overlay_style", style)
                .putString("pill_appearance", pillApp)
                .putBoolean("auto_hide_pill", swAutoHidePill.isChecked)
                .putBoolean("smart_freeze", swSmartFreeze.isChecked)
                .putBoolean("tap_outside_close", swTapOutsideClose.isChecked)
                .putBoolean("liquid_blur", swLiquidBlur.isChecked)
                .putBoolean("haptic_feedback", swHapticFeedback.isChecked)
                .putBoolean("auto_speak_tts", swAutoSpeakTts.isChecked)
                .putString("app_theme", themeChoice)
                .putInt("island_width_dp", sbIslandWidth.progress + 110)
                .putInt("island_pos_y_dp", sbIslandPosY.progress)
                .putInt("island_offset_x_dp", sbIslandOffsetX.progress - 80)
                .putInt("popup_opacity", sbOpacity.progress + 45)
                .putInt("anim_speed_prog", sbAnimSpeed.progress)
                .putString("ai_persona", persona)
                .putString("custom_system_instruction", etCustomSystemInstruction.text.toString().trim())
                .apply()

            applySavedNightMode(themeChoice)

            if (Settings.canDrawOverlays(this)) {
                try {
                    startService(Intent(this, FloatingAssistantService::class.java).apply {
                        action = FloatingAssistantService.ACTION_RELOAD_SETTINGS
                    })
                } catch (_: Exception) {}
            }
        }

        btnAddControlCenterTile.setOnClickListener {
            saveAllPreferences()
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                val sbm = getSystemService(StatusBarManager::class.java)
                sbm.requestAddTileService(
                    ComponentName(this, FloaminiTileService::class.java),
                    "Floamini AI",
                    Icon.createWithResource(this, R.drawable.ic_sparkle),
                    mainExecutor
                ) { code ->
                    runOnUiThread {
                        if (code == StatusBarManager.TILE_ADD_REQUEST_RESULT_TILE_ADDED ||
                            code == StatusBarManager.TILE_ADD_REQUEST_RESULT_TILE_ALREADY_ADDED
                        ) {
                            Toast.makeText(this, "Tombol Floamini AI siap di Control Center!", Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            } else {
                Toast.makeText(this, "Tarik Control Center, tekan Edit, lalu tambahkan tombol Floamini AI!", Toast.LENGTH_LONG).show()
            }
        }

        btnOpenWelcomeGuide.setOnClickListener {
            startActivity(Intent(this, WelcomeActivity::class.java).apply { putExtra("from_settings", true) })
        }

        btnClearAllHistoryMain.setOnClickListener {
            repo.clearAllThreads()
            try {
                startService(Intent(this, FloatingAssistantService::class.java).apply {
                    action = FloatingAssistantService.ACTION_RESET_SESSION
                })
            } catch (_: Exception) {}
            Toast.makeText(this, "Seluruh riwayat chat dihapus", Toast.LENGTH_SHORT).show()
        }

        btnResetUsageStats.setOnClickListener {
            repo.resetUsageStats()
            tvUsageStatistics.text = repo.getUsageSummaryText()
            Toast.makeText(this, "Statistik penggunaan di-reset", Toast.LENGTH_SHORT).show()
        }

        btnWipeVaultKeys.setOnClickListener {
            vault.clearAllCredentials()
            etProviderApiKey.setText("")
            bindProviderFields(editingProvider)
            Toast.makeText(this, "Seluruh API Key terenkripsi dihapus", Toast.LENGTH_SHORT).show()
        }

        btnSaveAllSettings.setOnClickListener {
            saveAllPreferences()
            Toast.makeText(this, "Semua pengaturan Floamini OS disimpan!", Toast.LENGTH_SHORT).show()
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
            Toast.makeText(this, "Floamini OS aktif di layar!", Toast.LENGTH_SHORT).show()
        }

        btnStopOverlay.setOnClickListener {
            stopService(Intent(this, FloatingAssistantService::class.java))
            Toast.makeText(this, "Floamini dihentikan", Toast.LENGTH_SHORT).show()
        }

        btnQuickForceStopMain.setOnClickListener {
            stopService(Intent(this, FloatingAssistantService::class.java))
            startActivity(Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                data = Uri.parse("package:$packageName")
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            })
            finishAffinity()
            exitProcess(0)
        }
    }

    private fun applySavedNightMode(theme: String) {
        val mode = when (theme) {
            "system" -> AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM
            "light" -> AppCompatDelegate.MODE_NIGHT_NO
            else -> AppCompatDelegate.MODE_NIGHT_YES
        }
        AppCompatDelegate.setDefaultNightMode(mode)
    }

    private fun simpleSeek(onChange: (Int) -> Unit) = object : SeekBar.OnSeekBarChangeListener {
        override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) = onChange(progress)
        override fun onStartTrackingTouch(seekBar: SeekBar?) {}
        override fun onStopTrackingTouch(seekBar: SeekBar?) {}
    }

    override fun onResume() {
        super.onResume()
        if (::repo.isInitialized) {
            findViewById<TextView>(R.id.tvUsageStatistics)?.text = repo.getUsageSummaryText()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        voiceHelper?.release()
        activityJob.cancel()
    }
}
