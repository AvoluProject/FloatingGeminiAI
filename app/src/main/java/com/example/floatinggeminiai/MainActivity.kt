package com.example.floatinggeminiai

import android.Manifest
import android.app.StatusBarManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.drawable.Icon
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.SeekBar
import android.widget.Spinner
import android.widget.Switch
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.example.floatinggeminiai.ai.AiEngine
import com.example.floatinggeminiai.ai.AiProvider
import com.example.floatinggeminiai.data.ChatRepository
import com.example.floatinggeminiai.security.SecureVault
import com.example.floatinggeminiai.ui.LiquidGlassBottomNavBar
import com.example.floatinggeminiai.ui.LiquidGlassFrameLayout
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var vault: SecureVault
    private lateinit var repo: ChatRepository
    private lateinit var aiEngine: AiEngine
    private var selectedProvider = AiProvider.GEMINI

    override fun onCreate(savedInstanceState: Bundle?) {
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        applySavedThemeMode(prefs.getInt("theme_mode", 0))
        super.onCreate(savedInstanceState)

        if (!prefs.getBoolean("welcome_completed", false)) {
            startActivity(Intent(this, WelcomeActivity::class.java))
        }

        setContentView(R.layout.activity_main)

        vault = SecureVault(this)
        repo = ChatRepository(this)
        aiEngine = AiEngine(vault)

        initLiquidGlassSurfaces()
        initFloatingBottomNavbar()
        setupHomeControls(prefs)
        setupAiProviderVault(prefs)
        setupOverlayAndGlassStudio(prefs)
        setupToolsAndData()
        requestRuntimePermissionsIfNeeded()
    }

    override fun onResume() {
        super.onResume()
        refreshDashboardStatus()
    }

    private fun applySavedThemeMode(modeIndex: Int) {
        when (modeIndex) {
            1 -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES)
            2 -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)
            else -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM)
        }
    }

    private fun initLiquidGlassSurfaces() {
        val heroCard = findViewById<LiquidGlassFrameLayout>(R.id.glassCardHero)
        val statsCard = findViewById<LiquidGlassFrameLayout>(R.id.glassCardStats)
        val providerCard = findViewById<LiquidGlassFrameLayout>(R.id.glassCardProvider)
        val overlayCard = findViewById<LiquidGlassFrameLayout>(R.id.glassCardOverlay)
        val toolsCard = findViewById<LiquidGlassFrameLayout>(R.id.glassCardTools)
        val headerBadge = findViewById<LiquidGlassFrameLayout>(R.id.glassHeaderBadge)

        headerBadge.cornerRadiusDp = 16f
        headerBadge.bevelWidthDp = 8f
        headerBadge.dispersionStrength = 0.42f
        headerBadge.startAmbientRefraction()

        listOf(heroCard, statsCard, providerCard, overlayCard, toolsCard).forEach { card ->
            card.cornerRadiusDp = 26f
            card.bevelWidthDp = 15f
            card.dispersionStrength = 0.28f
            card.specularIntensity = 0.65f
            card.startAmbientRefraction()
        }
    }

    private fun initFloatingBottomNavbar() {
        val navBar = findViewById<LiquidGlassBottomNavBar>(R.id.liquidBottomNavBar)
        val pageHome = findViewById<LinearLayout>(R.id.pageHome)
        val pageAi = findViewById<LinearLayout>(R.id.pageAiProviders)
        val pageOverlay = findViewById<LinearLayout>(R.id.pageOverlayGlass)
        val pageTools = findViewById<LinearLayout>(R.id.pageToolsData)
        val pages = listOf(pageHome, pageAi, pageOverlay, pageTools)

        navBar.setTabs(
            listOf(
                LiquidGlassBottomNavBar.NavTab("Beranda", R.drawable.ic_home),
                LiquidGlassBottomNavBar.NavTab("AI & Keys", R.drawable.ic_key),
                LiquidGlassBottomNavBar.NavTab("Liquid UI", R.drawable.ic_layers),
                LiquidGlassBottomNavBar.NavTab("Tools", R.drawable.ic_tools)
            )
        )

        navBar.onTabSelected = { index ->
            pages.forEachIndexed { idx, view ->
                if (idx == index) {
                    view.alpha = 0f
                    view.visibility = View.VISIBLE
                    view.animate().alpha(1f).setDuration(220L).start()
                } else {
                    view.visibility = View.GONE
                }
            }
        }
    }

    private fun setupHomeControls(prefs: android.content.SharedPreferences) {
        findViewById<Button>(R.id.btnOpenWelcome).setOnClickListener {
            startActivity(Intent(this, WelcomeActivity::class.java))
        }

        findViewById<Button>(R.id.btnGrantOverlay).setOnClickListener {
            val intent = Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:$packageName")
            )
            startActivity(intent)
        }

        findViewById<Button>(R.id.btnStartService).setOnClickListener {
            if (!Settings.canDrawOverlays(this)) {
                Toast.makeText(this, "Aktifkan izin Overlay terlebih dahulu!", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val intent = Intent(this, FloatingAssistantService::class.java).apply {
                action = FloatingAssistantService.ACTION_START_OR_UPDATE
            }
            ContextCompat.startForegroundService(this, intent)
            Toast.makeText(this, "Floamini Liquid Overlay aktif!", Toast.LENGTH_SHORT).show()
        }

        findViewById<Button>(R.id.btnSummonSiriNow).setOnClickListener {
            if (!Settings.canDrawOverlays(this)) {
                Toast.makeText(this, "Aktifkan izin Overlay terlebih dahulu!", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val intent = Intent(this, FloatingAssistantService::class.java).apply {
                action = FloatingAssistantService.ACTION_SUMMON_SIRI
            }
            ContextCompat.startForegroundService(this, intent)
        }

        findViewById<Button>(R.id.btnForceStopService).setOnClickListener {
            stopService(Intent(this, FloatingAssistantService::class.java))
            Toast.makeText(this, "Floamini dihentikan sepenuhnya.", Toast.LENGTH_SHORT).show()
        }
    }

    private fun setupAiProviderVault(prefs: android.content.SharedPreferences) {
        val spinnerProvider = findViewById<Spinner>(R.id.spinnerProvider)
        val spinnerModel = findViewById<Spinner>(R.id.spinnerModel)
        val spinnerPersonality = findViewById<Spinner>(R.id.spinnerPersonality)
        val tvKeyStatus = findViewById<TextView>(R.id.tvProviderKeyStatus)
        val etApiKey = findViewById<EditText>(R.id.etProviderApiKey)
        val layoutCustom = findViewById<LinearLayout>(R.id.layoutCustomEndpoint)
        val etCustomUrl = findViewById<EditText>(R.id.etCustomBaseUrl)
        val etCustomModel = findViewById<EditText>(R.id.etCustomModelId)
        val tvTestResult = findViewById<TextView>(R.id.tvTestConnectionResult)
        val etPersona = findViewById<EditText>(R.id.etCustomPersona)

        selectedProvider = AiProvider.fromId(prefs.getString("active_provider", AiProvider.GEMINI.id))
        val providerNames = AiProvider.entries.map { it.displayName }
        spinnerProvider.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, providerNames)
        spinnerProvider.setSelection(AiProvider.entries.indexOf(selectedProvider))

        etCustomUrl.setText(vault.getCustomBaseUrl())
        etCustomModel.setText(vault.getCustomModelId())
        etPersona.setText(prefs.getString("custom_system_prompt", ""))

        fun bindModelSpinner(provider: AiProvider) {
            val models = if (provider == AiProvider.CUSTOM) {
                listOf(vault.getCustomModelId().ifEmpty { "custom-model" })
            } else {
                provider.models
            }
            spinnerModel.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, models)
            val savedModel = prefs.getString("active_model", "")
            val idx = models.indexOf(savedModel)
            if (idx >= 0) spinnerModel.setSelection(idx)
            tvKeyStatus.text = "Status Vault (${provider.displayName}): ${vault.getMaskedKey(provider.id)}"
            layoutCustom.visibility = if (provider == AiProvider.CUSTOM) View.VISIBLE else View.GONE
        }

        bindModelSpinner(selectedProvider)

        spinnerProvider.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                selectedProvider = AiProvider.entries[position]
                prefs.edit().putString("active_provider", selectedProvider.id).apply()
                etApiKey.setText("")
                tvTestResult.visibility = View.GONE
                bindModelSpinner(selectedProvider)
                refreshDashboardStatus()
                notifyServiceConfigChanged()
            }

            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }

        spinnerModel.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                val chosen = spinnerModel.selectedItem?.toString() ?: return
                prefs.edit().putString("active_model", chosen).apply()
                refreshDashboardStatus()
                notifyServiceConfigChanged()
            }

            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }

        val personalities = listOf(
            "Asik & Santai (Natural)",
            "Singkat & Padat (To The Point)",
            "Detail & Terstruktur",
            "Kreatif & Ekspresif",
            "Coding & Teknis Pro"
        )
        spinnerPersonality.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, personalities)
        spinnerPersonality.setSelection(prefs.getInt("personality_index", 0))
        spinnerPersonality.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                prefs.edit().putInt("personality_index", position).apply()
                notifyServiceConfigChanged()
            }

            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }

        findViewById<Button>(R.id.btnSaveProviderKey).setOnClickListener {
            val newKey = etApiKey.text.toString().trim()
            if (newKey.isNotEmpty()) {
                vault.saveApiKey(selectedProvider.id, newKey)
                etApiKey.setText("")
            }
            if (selectedProvider == AiProvider.CUSTOM) {
                vault.saveCustomEndpoint(etCustomUrl.text.toString(), etCustomModel.text.toString())
                bindModelSpinner(selectedProvider)
            }
            prefs.edit().putString("custom_system_prompt", etPersona.text.toString().trim()).apply()
            tvKeyStatus.text = "Status Vault (${selectedProvider.displayName}): ${vault.getMaskedKey(selectedProvider.id)}"
            Toast.makeText(this, "Tersimpan aman di Encrypted Vault!", Toast.LENGTH_SHORT).show()
            notifyServiceConfigChanged()
        }

        findViewById<Button>(R.id.btnTestProviderConnection).setOnClickListener {
            val activeModel = spinnerModel.selectedItem?.toString() ?: selectedProvider.models.first()
            tvTestResult.visibility = View.VISIBLE
            tvTestResult.text = "Menguji koneksi ke ${selectedProvider.displayName}..."
            lifecycleScope.launch {
                val res = aiEngine.testConnection(selectedProvider, activeModel)
                res.onSuccess { msg ->
                    tvTestResult.text = msg
                }.onFailure { err ->
                    tvTestResult.text = "Gagal: ${err.message}"
                }
            }
        }
    }

    private fun setupOverlayAndGlassStudio(prefs: android.content.SharedPreferences) {
        val spinnerStyle = findViewById<Spinner>(R.id.spinnerOverlayStyle)
        val spinnerPill = findViewById<Spinner>(R.id.spinnerPillAppearance)
        val switchAutoHide = findViewById<Switch>(R.id.switchAutoHidePill)
        val switchSmartFreeze = findViewById<Switch>(R.id.switchSmartFreeze)
        val switchBlur = findViewById<Switch>(R.id.switchLiquidBlur)
        val seekWidth = findViewById<SeekBar>(R.id.seekIslandWidth)
        val seekY = findViewById<SeekBar>(R.id.seekIslandY)
        val seekX = findViewById<SeekBar>(R.id.seekIslandX)
        val seekOpacity = findViewById<SeekBar>(R.id.seekPopupOpacity)
        val spinnerTheme = findViewById<Spinner>(R.id.spinnerThemeMode)

        val styles = listOf("Dynamic Island (Atas)", "Mode Siri (Control Center)", "Xiaomi Edge Pill", "Classic Bubble")
        val styleKeys = listOf("dynamic_island", "siri_mode", "xiaomi_edge", "classic_bubble")
        spinnerStyle.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, styles)
        val curStyle = prefs.getString("overlay_style", "dynamic_island")
        spinnerStyle.setSelection(styleKeys.indexOf(curStyle).coerceAtLeast(0))
        spinnerStyle.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(p: AdapterView<*>?, v: View?, pos: Int, id: Long) {
                prefs.edit().putString("overlay_style", styleKeys[pos]).apply()
                notifyServiceConfigChanged()
            }
            override fun onNothingSelected(p: AdapterView<*>?) {}
        }

        val pillModes = listOf("Lengkap (Ikon + Nama + Pulse)", "Polos (Kamera Punch-Hole)", "Ikon Saja")
        val pillKeys = listOf("lengkap", "polos", "minimal")
        spinnerPill.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, pillModes)
        val curPill = prefs.getString("pill_appearance", "lengkap")
        spinnerPill.setSelection(pillKeys.indexOf(curPill).coerceAtLeast(0))
        spinnerPill.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(p: AdapterView<*>?, v: View?, pos: Int, id: Long) {
                prefs.edit().putString("pill_appearance", pillKeys[pos]).apply()
                notifyServiceConfigChanged()
            }
            override fun onNothingSelected(p: AdapterView<*>?) {}
        }

        switchAutoHide.isChecked = prefs.getBoolean("auto_hide_pill", false)
        switchAutoHide.setOnCheckedChangeListener { _, checked ->
            prefs.edit().putBoolean("auto_hide_pill", checked).apply()
            notifyServiceConfigChanged()
        }

        switchSmartFreeze.isChecked = prefs.getBoolean("smart_freeze", true)
        switchSmartFreeze.setOnCheckedChangeListener { _, checked ->
            prefs.edit().putBoolean("smart_freeze", checked).apply()
            notifyServiceConfigChanged()
        }

        switchBlur.isChecked = prefs.getBoolean("liquid_blur", true)
        switchBlur.setOnCheckedChangeListener { _, checked ->
            prefs.edit().putBoolean("liquid_blur", checked).apply()
            notifyServiceConfigChanged()
        }

        val tvW = findViewById<TextView>(R.id.tvIslandWidthLabel)
        val savedW = prefs.getInt("island_width_dp", 164)
        seekWidth.progress = (savedW - 100).coerceIn(0, 180)
        tvW.text = "Lebar Pil Dynamic Island: ${savedW}dp"
        seekWidth.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(sb: SeekBar?, prog: Int, fromUser: Boolean) {
                val w = 100 + prog
                tvW.text = "Lebar Pil Dynamic Island: ${w}dp"
                prefs.edit().putInt("island_width_dp", w).apply()
                if (fromUser) notifyServiceConfigChanged()
            }
            override fun onStartTrackingTouch(sb: SeekBar?) {}
            override fun onStopTrackingTouch(sb: SeekBar?) {}
        })

        val tvY = findViewById<TextView>(R.id.tvIslandYLabel)
        val savedY = prefs.getInt("island_pos_y_dp", 12)
        seekY.progress = savedY.coerceIn(0, 120)
        tvY.text = "Posisi Vertikal Atas (Y): ${savedY}dp"
        seekY.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(sb: SeekBar?, prog: Int, fromUser: Boolean) {
                tvY.text = "Posisi Vertikal Atas (Y): ${prog}dp"
                prefs.edit().putInt("island_pos_y_dp", prog).apply()
                if (fromUser) notifyServiceConfigChanged()
            }
            override fun onStartTrackingTouch(sb: SeekBar?) {}
            override fun onStopTrackingTouch(sb: SeekBar?) {}
        })

        val tvX = findViewById<TextView>(R.id.tvIslandXLabel)
        val savedX = prefs.getInt("island_offset_x_dp", 0)
        seekX.progress = (savedX + 120).coerceIn(0, 240)
        tvX.text = "Geser Horizontal Kamera (X): ${savedX}dp"
        seekX.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(sb: SeekBar?, prog: Int, fromUser: Boolean) {
                val offset = prog - 120
                tvX.text = "Geser Horizontal Kamera (X): ${offset}dp"
                prefs.edit().putInt("island_offset_x_dp", offset).apply()
                if (fromUser) notifyServiceConfigChanged()
            }
            override fun onStartTrackingTouch(sb: SeekBar?) {}
            override fun onStopTrackingTouch(sb: SeekBar?) {}
        })

        val tvOp = findViewById<TextView>(R.id.tvOpacityLabel)
        val savedOp = prefs.getInt("popup_opacity_pct", 92)
        seekOpacity.progress = (savedOp - 55).coerceIn(0, 45)
        tvOp.text = "Transparansi Jendela Glass: $savedOp%"
        seekOpacity.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(sb: SeekBar?, prog: Int, fromUser: Boolean) {
                val pct = 55 + prog
                tvOp.text = "Transparansi Jendela Glass: $pct%"
                prefs.edit().putInt("popup_opacity_pct", pct).apply()
                if (fromUser) notifyServiceConfigChanged()
            }
            override fun onStartTrackingTouch(sb: SeekBar?) {}
            override fun onStopTrackingTouch(sb: SeekBar?) {}
        })

        val themes = listOf("Ikuti Sistem (Adaptif)", "Dark Liquid Glass", "Light Liquid Glass")
        spinnerTheme.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, themes)
        spinnerTheme.setSelection(prefs.getInt("theme_mode", 0))
        spinnerTheme.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(p: AdapterView<*>?, v: View?, pos: Int, id: Long) {
                if (prefs.getInt("theme_mode", 0) != pos) {
                    prefs.edit().putInt("theme_mode", pos).apply()
                    applySavedThemeMode(pos)
                }
            }
            override fun onNothingSelected(p: AdapterView<*>?) {}
        }

        findViewById<Button>(R.id.btnAddControlCenterTile).setOnClickListener {
            requestAddControlCenterTile()
        }
    }

    private fun setupToolsAndData() {
        val etNotes = findViewById<EditText>(R.id.etMainQuickNotes)
        etNotes.setText(repo.getQuickNotes())

        findViewById<Button>(R.id.btnSaveQuickNotes).setOnClickListener {
            repo.saveQuickNotes(etNotes.text.toString())
            Toast.makeText(this, "Catatan cepat tersimpan!", Toast.LENGTH_SHORT).show()
        }

        findViewById<Button>(R.id.btnClearAllHistory).setOnClickListener {
            AlertDialog.Builder(this)
                .setTitle("Hapus Semua Riwayat?")
                .setMessage("Seluruh sesi percakapan Floamini akan dihapus permanen.")
                .setPositiveButton("Hapus") { _, _ ->
                    repo.clearAllHistory()
                    repo.resetUsage()
                    refreshDashboardStatus()
                    Toast.makeText(this, "Riwayat dibersihkan.", Toast.LENGTH_SHORT).show()
                }
                .setNegativeButton("Batal", null)
                .show()
        }
    }

    private fun refreshDashboardStatus() {
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        val prov = AiProvider.fromId(prefs.getString("active_provider", AiProvider.GEMINI.id))
        val model = prefs.getString("active_model", prov.models.first()).orEmpty()
        findViewById<TextView>(R.id.tvActiveEngineSummary).text = "Engine: ${prov.displayName} ($model)"
        findViewById<TextView>(R.id.tvPermissionBadge).text =
            if (Settings.canDrawOverlays(this)) "Overlay: Aktif" else "Overlay: Perlu Izin"
        findViewById<TextView>(R.id.tvUsageStats).text = repo.getUsageSummary()
    }

    private fun notifyServiceConfigChanged() {
        if (Settings.canDrawOverlays(this)) {
            val intent = Intent(this, FloatingAssistantService::class.java).apply {
                action = FloatingAssistantService.ACTION_RELOAD_CONFIG
            }
            try {
                startService(intent)
            } catch (_: Exception) {
            }
        }
    }

    private fun requestAddControlCenterTile() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            val sbm = getSystemService(StatusBarManager::class.java)
            sbm?.requestAddTileService(
                ComponentName(this, FloaminiTileService::class.java),
                "Floamini AI",
                Icon.createWithResource(this, R.drawable.ic_sparkle),
                mainExecutor
            ) { _ ->
                Toast.makeText(this, "Permintaan tile Control Center diproses.", Toast.LENGTH_SHORT).show()
            }
        } else {
            AlertDialog.Builder(this)
                .setTitle("Shortcut Control Center")
                .setMessage("Tarik panel Quick Settings dari atas layar > ketuk ikon Edit (Pensil) > seret ubin 'Floamini AI' ke area aktif.")
                .setPositiveButton("Mengerti", null)
                .show()
        }
    }

    private fun requestRuntimePermissionsIfNeeded() {
        val perms = mutableListOf(Manifest.permission.RECORD_AUDIO)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            perms.add(Manifest.permission.POST_NOTIFICATIONS)
        }
        val missing = perms.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (missing.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, missing.toTypedArray(), 101)
        }
    }
}
