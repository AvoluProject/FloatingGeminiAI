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
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.util.concurrent.TimeUnit
import kotlin.system.exitProcess

class MainActivity : AppCompatActivity() {

    private val testHttpClient = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .build()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)

        val tvDashboardSessionStatus = findViewById<TextView>(R.id.tvDashboardSessionStatus)
        val etApiKey = findViewById<TextInputEditText>(R.id.etApiKey)
        val etCustomPersonaNote = findViewById<TextInputEditText>(R.id.etCustomPersonaNote)
        val btnTestToken = findViewById<Button>(R.id.btnTestToken)
        val btnStartOverlay = findViewById<Button>(R.id.btnStartOverlay)
        val btnStopOverlay = findViewById<Button>(R.id.btnStopOverlay)
        val btnQuickForceStopMain = findViewById<Button>(R.id.btnQuickForceStopMain)
        val btnClearSessionMain = findViewById<Button>(R.id.btnClearSessionMain)
        val btnSaveAllSettings = findViewById<Button>(R.id.btnSaveAllSettings)

        val rgPersona = findViewById<RadioGroup>(R.id.rgPersona)
        val rbAsik = findViewById<RadioButton>(R.id.rbAsik)
        val rbRingkas = findViewById<RadioButton>(R.id.rbRingkas)
        val rbDetail = findViewById<RadioButton>(R.id.rbDetail)
        val rbKreatif = findViewById<RadioButton>(R.id.rbKreatif)

        val rgModel = findViewById<RadioGroup>(R.id.rgModel)
        val rbModel3Flash = findViewById<RadioButton>(R.id.rbModel3Flash)
        val rbModel25Flash = findViewById<RadioButton>(R.id.rbModel25Flash)
        val rbModel25Pro = findViewById<RadioButton>(R.id.rbModel25Pro)

        val swMagneticSnap = findViewById<SwitchMaterial>(R.id.swMagneticSnap)
        val swXiaomiEdge = findViewById<SwitchMaterial>(R.id.swXiaomiEdge)
        val tvEdgeDelayLabel = findViewById<TextView>(R.id.tvEdgeDelayLabel)
        val sbEdgeDelay = findViewById<SeekBar>(R.id.sbEdgeDelay)
        val tvOpacityLabel = findViewById<TextView>(R.id.tvOpacityLabel)
        val sbOpacity = findViewById<SeekBar>(R.id.sbOpacity)
        val tvBubbleSizeLabel = findViewById<TextView>(R.id.tvBubbleSizeLabel)
        val sbBubbleSize = findViewById<SeekBar>(R.id.sbBubbleSize)

        fun updateSessionBadge() {
            val raw = prefs.getString("session_history_json", null)
            val count = try {
                if (raw.isNullOrEmpty()) 0 else JSONArray(raw).length()
            } catch (_: Exception) { 0 }
            tvDashboardSessionStatus.text = if (count > 0) {
                "Sesi Memori Aktif • $count pesan tersimpan"
            } else {
                "Sesi Memori Baru • Siap Digunakan"
            }
        }

        updateSessionBadge()
        etApiKey.setText(prefs.getString("api_key", ""))
        etCustomPersonaNote.setText(prefs.getString("custom_persona_note", ""))

        when (prefs.getString("ai_persona", "asik")) {
            "ringkas" -> rbRingkas.isChecked = true
            "detail" -> rbDetail.isChecked = true
            "kreatif" -> rbKreatif.isChecked = true
            else -> rbAsik.isChecked = true
        }

        when (prefs.getString("ai_model", "gemini-3-flash-preview")) {
            "gemini-2.5-flash" -> rbModel25Flash.isChecked = true
            "gemini-2.5-pro" -> rbModel25Pro.isChecked = true
            else -> rbModel3Flash.isChecked = true
        }

        swMagneticSnap.isChecked = prefs.getBoolean("magnetic_snap", true)
        swXiaomiEdge.isChecked = prefs.getBoolean("xiaomi_edge", true)

        val savedDelaySec = prefs.getInt("edge_delay_sec", 3)
        sbEdgeDelay.progress = (savedDelaySec - 1).coerceIn(0, 9)
        tvEdgeDelayLabel.text = "Jeda Berubah ke Garis Xiaomi: ${savedDelaySec} Detik"

        val savedOpacity = prefs.getInt("popup_opacity", 84)
        sbOpacity.progress = (savedOpacity - 45).coerceIn(0, 55)
        tvOpacityLabel.text = "Transparansi Jendela Chat: ${savedOpacity}%"

        val savedBubbleSize = prefs.getInt("bubble_size_dp", 56)
        sbBubbleSize.progress = (savedBubbleSize - 44).coerceIn(0, 28)
        tvBubbleSizeLabel.text = "Ukuran Bubble Utama: ${savedBubbleSize}dp"

        sbEdgeDelay.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                tvEdgeDelayLabel.text = "Jeda Berubah ke Garis Xiaomi: ${progress + 1} Detik"
            }
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })

        sbOpacity.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                tvOpacityLabel.text = "Transparansi Jendela Chat: ${progress + 45}%"
            }
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })

        sbBubbleSize.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                tvBubbleSizeLabel.text = "Ukuran Bubble Utama: ${progress + 44}dp"
            }
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })

        fun saveAllPreferences() {
            val persona = when (rgPersona.checkedRadioButtonId) {
                R.id.rbRingkas -> "ringkas"
                R.id.rbDetail -> "detail"
                R.id.rbKreatif -> "kreatif"
                else -> "asik"
            }
            val model = when (rgModel.checkedRadioButtonId) {
                R.id.rbModel25Flash -> "gemini-2.5-flash"
                R.id.rbModel25Pro -> "gemini-2.5-pro"
                else -> "gemini-3-flash-preview"
            }
            prefs.edit()
                .putString("api_key", etApiKey.text.toString().trim())
                .putString("custom_persona_note", etCustomPersonaNote.text.toString().trim())
                .putString("ai_persona", persona)
                .putString("ai_model", model)
                .putBoolean("magnetic_snap", swMagneticSnap.isChecked)
                .putBoolean("xiaomi_edge", swXiaomiEdge.isChecked)
                .putInt("edge_delay_sec", sbEdgeDelay.progress + 1)
                .putInt("popup_opacity", sbOpacity.progress + 45)
                .putInt("bubble_size_dp", sbBubbleSize.progress + 44)
                .apply()

            try {
                val refreshIntent = Intent(this, FloatingAssistantService::class.java).apply {
                    action = FloatingAssistantService.ACTION_RELOAD_SETTINGS
                }
                startService(refreshIntent)
            } catch (_: Exception) {}
        }

        btnTestToken.setOnClickListener {
            val token = etApiKey.text.toString().trim()
            if (token.isEmpty()) {
                Toast.makeText(this, "Masukkan API Token terlebih dahulu", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            btnTestToken.isEnabled = false
            btnTestToken.text = "Menguji..."
            CoroutineScope(Dispatchers.IO).launch {
                val isValid = try {
                    val url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$token"
                    val body = JSONObject().apply {
                        put("contents", JSONArray().apply {
                            put(JSONObject().apply {
                                put("parts", JSONArray().apply {
                                    put(JSONObject().apply { put("text", "Halo") })
                                })
                            })
                        })
                    }.toString().toRequestBody("application/json; charset=utf-8".toMediaType())
                    val req = Request.Builder().url(url).post(body).build()
                    testHttpClient.newCall(req).execute().use { it.isSuccessful }
                } catch (_: Exception) { false }

                withContext(Dispatchers.Main) {
                    btnTestToken.isEnabled = true
                    btnTestToken.text = "Tes Token"
                    if (isValid) {
                        saveAllPreferences()
                        Toast.makeText(this@MainActivity, "Koneksi Berhasil! Token Gemini Valid", Toast.LENGTH_SHORT).show()
                    } else {
                        Toast.makeText(this@MainActivity, "Token tidak valid atau koneksi gagal", Toast.LENGTH_LONG).show()
                    }
                }
            }
        }

        btnSaveAllSettings.setOnClickListener {
            saveAllPreferences()
            Toast.makeText(this, "Semua pengaturan berhasil disimpan", Toast.LENGTH_SHORT).show()
        }

        btnClearSessionMain.setOnClickListener {
            prefs.edit().remove("session_history_json").apply()
            updateSessionBadge()
            try {
                val resetIntent = Intent(this, FloatingAssistantService::class.java).apply {
                    action = FloatingAssistantService.ACTION_RESET_SESSION
                }
                startService(resetIntent)
            } catch (_: Exception) {}
            Toast.makeText(this, "Memori sesi obrolan dibersihkan", Toast.LENGTH_SHORT).show()
        }

        btnStartOverlay.setOnClickListener {
            saveAllPreferences()
            if (!Settings.canDrawOverlays(this)) {
                Toast.makeText(this, "Izinkan tampil di atas aplikasi lain terlebih dahulu", Toast.LENGTH_LONG).show()
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
            Toast.makeText(this, "Floating Assistant aktif di layar", Toast.LENGTH_SHORT).show()
        }

        btnStopOverlay.setOnClickListener {
            stopService(Intent(this, FloatingAssistantService::class.java))
            Toast.makeText(this, "Floating Assistant dihentikan", Toast.LENGTH_SHORT).show()
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
}
