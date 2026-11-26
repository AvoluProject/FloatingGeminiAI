package com.example.floatinggeminiai

import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.floatinggeminiai.ai.AiEngineRegistry
import com.example.floatinggeminiai.ai.AiProviderType
import com.example.floatinggeminiai.security.SecureVault
import com.google.android.material.textfield.TextInputEditText
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class WelcomeActivity : AppCompatActivity() {

    private val activityJob = Job()
    private val uiScope = CoroutineScope(Dispatchers.Main + activityJob)
    private lateinit var vault: SecureVault
    private var selectedProvider = AiProviderType.GEMINI

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_welcome)

        vault = SecureVault(this)
        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        val fromSettings = intent.getBooleanExtra("from_settings", false)

        val spWelcomeProvider = findViewById<Spinner>(R.id.spWelcomeProvider)
        val btnOpenAiStudio = findViewById<Button>(R.id.btnOpenAiStudio)
        val etWelcomeApiKey = findViewById<TextInputEditText>(R.id.etWelcomeApiKey)
        val btnTestTokenWelcome = findViewById<Button>(R.id.btnTestTokenWelcome)
        val tvTokenTestResult = findViewById<TextView>(R.id.tvTokenTestResult)
        val btnContinueToFloamini = findViewById<Button>(R.id.btnContinueToFloamini)

        val providers = AiProviderType.values().toList()
        val adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_dropdown_item,
            providers.map { "${it.displayName} (${it.defaultModel})" }
        )
        spWelcomeProvider.adapter = adapter
        spWelcomeProvider.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                selectedProvider = providers[position]
                etWelcomeApiKey.setText(vault.getApiKey(selectedProvider))
            }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }

        if (fromSettings) {
            btnContinueToFloamini.text = "Kembali ke Pengaturan Floamini"
        }

        btnOpenAiStudio.setOnClickListener {
            try {
                startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(selectedProvider.docsUrl)))
            } catch (_: Exception) {
                Toast.makeText(this, "Kunjungi ${selectedProvider.docsUrl}", Toast.LENGTH_LONG).show()
            }
        }

        btnTestTokenWelcome.setOnClickListener {
            val token = etWelcomeApiKey.text.toString().trim()
            if (token.isEmpty()) {
                tvTokenTestResult.text = "Masukkan API Key terlebih dahulu"
                tvTokenTestResult.setTextColor(Color.parseColor("#FBBF24"))
                return@setOnClickListener
            }

            btnTestTokenWelcome.isEnabled = false
            tvTokenTestResult.text = "Menguji ${selectedProvider.shortBadge}..."
            tvTokenTestResult.setTextColor(Color.parseColor("#38BDF8"))

            uiScope.launch {
                val (ok, msg) = withContext(Dispatchers.IO) {
                    AiEngineRegistry.getAdapter(selectedProvider)
                        .testConnection(token, selectedProvider.defaultModel)
                }
                btnTestTokenWelcome.isEnabled = true
                if (ok) {
                    vault.setApiKey(selectedProvider, token)
                    prefs.edit().putString("active_provider_id", selectedProvider.id).apply()
                    tvTokenTestResult.text = "$msg • Tersimpan!"
                    tvTokenTestResult.setTextColor(Color.parseColor("#34D399"))
                } else {
                    tvTokenTestResult.text = msg
                    tvTokenTestResult.setTextColor(Color.parseColor("#FCA5A5"))
                }
            }
        }

        btnContinueToFloamini.setOnClickListener {
            val enteredKey = etWelcomeApiKey.text.toString().trim()
            if (enteredKey.isNotEmpty()) {
                vault.setApiKey(selectedProvider, enteredKey)
                prefs.edit().putString("active_provider_id", selectedProvider.id).apply()
            }
            prefs.edit().putBoolean("has_seen_welcome", true).apply()

            if (!fromSettings) {
                startActivity(Intent(this, MainActivity::class.java))
            }
            finish()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        activityJob.cancel()
    }
}
