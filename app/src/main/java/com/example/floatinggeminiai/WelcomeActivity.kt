package com.example.floatinggeminiai

import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.textfield.TextInputEditText
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.util.concurrent.TimeUnit

class WelcomeActivity : AppCompatActivity() {

    private val activityJob = Job()
    private val uiScope = CoroutineScope(Dispatchers.Main + activityJob)

    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .build()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_welcome)

        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        val fromSettings = intent.getBooleanExtra("from_settings", false)

        val btnOpenAiStudio = findViewById<Button>(R.id.btnOpenAiStudio)
        val etWelcomeApiKey = findViewById<TextInputEditText>(R.id.etWelcomeApiKey)
        val btnTestTokenWelcome = findViewById<Button>(R.id.btnTestTokenWelcome)
        val tvTokenTestResult = findViewById<TextView>(R.id.tvTokenTestResult)
        val btnContinueToFloamini = findViewById<Button>(R.id.btnContinueToFloamini)

        etWelcomeApiKey.setText(prefs.getString("api_key", ""))
        if (fromSettings) {
            btnContinueToFloamini.text = "Kembali ke Pengaturan Floamini"
        }

        btnOpenAiStudio.setOnClickListener {
            try {
                val browserIntent = Intent(Intent.ACTION_VIEW, Uri.parse("https://aistudio.google.com/apikey"))
                startActivity(browserIntent)
            } catch (e: Exception) {
                Toast.makeText(this, "Buka browser dan kunjungi aistudio.google.com/apikey", Toast.LENGTH_LONG).show()
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
            tvTokenTestResult.text = "Menguji koneksi ke Gemini..."
            tvTokenTestResult.setTextColor(Color.parseColor("#38BDF8"))

            uiScope.launch {
                val isValid = verifyGeminiApiKey(token)
                btnTestTokenWelcome.isEnabled = true
                if (isValid) {
                    prefs.edit().putString("api_key", token).apply()
                    tvTokenTestResult.text = "Token Valid & Tersimpan!"
                    tvTokenTestResult.setTextColor(Color.parseColor("#34D399"))
                } else {
                    tvTokenTestResult.text = "Token tidak valid atau jaringan bermasalah"
                    tvTokenTestResult.setTextColor(Color.parseColor("#FCA5A5"))
                }
            }
        }

        btnContinueToFloamini.setOnClickListener {
            val enteredKey = etWelcomeApiKey.text.toString().trim()
            val editor = prefs.edit().putBoolean("has_seen_welcome", true)
            if (enteredKey.isNotEmpty()) {
                editor.putString("api_key", enteredKey)
            }
            editor.apply()

            if (!fromSettings) {
                startActivity(Intent(this, MainActivity::class.java))
            }
            finish()
        }
    }

    private suspend fun verifyGeminiApiKey(apiKey: String): Boolean = withContext(Dispatchers.IO) {
        try {
            val url = "https://generativelanguage.googleapis.com/v1beta/models?key=$apiKey"
            val request = Request.Builder().url(url).get().build()
            httpClient.newCall(request).execute().use { response ->
                response.isSuccessful
            }
        } catch (_: Exception) {
            false
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        activityJob.cancel()
    }
}
