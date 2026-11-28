package com.example.floatinggeminiai

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.floatinggeminiai.ai.AiEngine
import com.example.floatinggeminiai.ai.AiProvider
import com.example.floatinggeminiai.security.SecureVault
import com.example.floatinggeminiai.ui.LiquidGlassFrameLayout
import kotlinx.coroutines.launch

class WelcomeActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_welcome)

        val vault = SecureVault(this)
        val engine = AiEngine(vault)
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)

        findViewById<LiquidGlassFrameLayout>(R.id.glassWelcomeHero).apply {
            cornerRadiusDp = 28f
            dispersionStrength = 0.35f
            startAmbientRefraction()
        }
        findViewById<LiquidGlassFrameLayout>(R.id.glassWelcomeGuide).apply {
            cornerRadiusDp = 26f
            dispersionStrength = 0.28f
            startAmbientRefraction()
        }

        findViewById<Button>(R.id.btnOpenAiStudio).setOnClickListener {
            startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://aistudio.google.com/app/apikey")))
        }

        val etKey = findViewById<EditText>(R.id.etWelcomeGeminiKey)
        val tvStatus = findViewById<TextView>(R.id.tvWelcomeTestStatus)

        findViewById<Button>(R.id.btnWelcomeSaveAndTest).setOnClickListener {
            val raw = etKey.text.toString().trim()
            if (raw.isEmpty()) {
                Toast.makeText(this, "Tempel Gemini API Key terlebih dahulu.", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            vault.saveApiKey(AiProvider.GEMINI.id, raw)
            prefs.edit().putString("active_provider", AiProvider.GEMINI.id).apply()
            tvStatus.visibility = View.VISIBLE
            tvStatus.text = "Menguji token Gemini..."
            lifecycleScope.launch {
                val res = engine.testConnection(AiProvider.GEMINI, AiProvider.GEMINI.models.first())
                res.onSuccess { msg ->
                    tvStatus.text = msg
                }.onFailure { err ->
                    tvStatus.text = "Gagal: ${err.message}"
                }
            }
        }

        findViewById<Button>(R.id.btnWelcomeFinish).setOnClickListener {
            prefs.edit().putBoolean("welcome_completed", true).apply()
            finish()
        }
    }
}
