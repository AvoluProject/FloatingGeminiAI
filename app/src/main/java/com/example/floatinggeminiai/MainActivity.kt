package com.example.floatinggeminiai

import android.content.Context
import android.content.Intent
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
        val btnStopOverlay = findViewById<Button>(R.id.btnStopOverlay)
        val btnQuickForceStopMain = findViewById<Button>(R.id.btnQuickForceStopMain)
        tvSessionStatusMain = findViewById(R.id.tvSessionStatusMain)
        val btnResetSessionMain = findViewById<Button>(R.id.btnResetSessionMain)

        val rgOverlayStyle = findViewById<RadioGroup>(R.id.rgOverlayStyle)
        val rbStyleDynamicIsland = findViewById<RadioButton>(R.id.rbStyleDynamicIsland)
        val rbStyleXiaomiEdge = findViewById<RadioButton>(R.id.rbStyleXiaomiEdge)
        val rbStyleClassicBubble = findViewById<RadioButton>(R.id.rbStyleClassicBubble)

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
            tvAppVersionInfo.text = "v${pInfo.versionName} • iOS 26 Liquid Glass & Dynamic Island"
        } catch (_: Exception) {}

        etApiKey.setText(prefs.getString("api_key", ""))
        updateSessionStatsLabel()

        when (prefs.getString("overlay_style", "dynamic_island")) {
            "xiaomi_edge" -> rbStyleXiaomiEdge.isChecked = true
            "classic_bubble" -> rbStyleClassicBubble.isChecked = true
            else -> rbStyleDynamicIsland.isChecked = true
        }

        swTapOutsideClose.isChecked = prefs.getBoolean("tap_outside_close", true)
        swLiquidBlur.isChecked = prefs.getBoolean("liquid_blur", true)
        swHapticFeedback.isChecked = prefs.getBoolean("haptic_feedback", true)

        val savedIslandW = prefs.getInt("island_width_dp", 168)
        sbIslandWidth.progress = (savedIslandW - 120).coerceIn(0, 120)
        tvIslandWidthLabel.text = "Lebar Pil Dynamic Island: ${savedIslandW}dp"

        val savedIslandY = prefs.getInt("island_pos_y_dp", 12)
        sbIslandPosY.progress = savedIslandY.coerceIn(0, 70)
        tvIslandPosYLabel.text = "Posisi Vertikal Atas (Y): ${savedIslandY}dp"

        val savedIslandX = prefs.getInt("island_offset_x_dp", 0)
        sbIslandOffsetX.progress = (savedIslandX + 80).coerceIn(0, 160)
        tvIslandOffsetXLabel.text = "Geser Horizontal Kamera (X): ${savedIslandX}dp"

        val savedOpacity = prefs.getInt("popup_opacity", 82)
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
                tvIslandWidthLabel.text = "Lebar Pil Dynamic Island: ${progress + 120}dp"
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
                R.id.rbStyleXiaomiEdge -> "xiaomi_edge"
                R.id.rbStyleClassicBubble -> "classic_bubble"
                else -> "dynamic_island"
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
                .putBoolean("tap_outside_close", swTapOutsideClose.isChecked)
                .putBoolean("liquid_blur", swLiquidBlur.isChecked)
                .putBoolean("haptic_feedback", swHapticFeedback.isChecked)
                .putInt("island_width_dp", sbIslandWidth.progress + 120)
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

        btnOpenWelcomeGuide.setOnClickListener {
            val welcomeIntent = Intent(this, WelcomeActivity::class.java).apply {
                putExtra("from_settings", true)
            }
            startActivity(welcomeIntent)
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
                val intent = Intent(
                    Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                    Uri.parse("package:$packageName")
                )
                startActivity(intent)
                return@setOnClickListener
            }

            val serviceIntent = Intent(this, FloatingAssistantService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                startForegroundService(serviceIntent)
            } else {
                startService(serviceIntent)
            }
            Toast.makeText(this, "Floamini aktif di layar", Toast.LENGTH_SHORT).show()
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
