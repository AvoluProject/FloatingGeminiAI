package com.example.floatinggeminiai

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.textfield.TextInputEditText

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        val etApiKey = findViewById<TextInputEditText>(R.id.etApiKey)
        val btnSaveToken = findViewById<Button>(R.id.btnSaveToken)
        val btnStartOverlay = findViewById<Button>(R.id.btnStartOverlay)
        val btnStopOverlay = findViewById<Button>(R.id.btnStopOverlay)

        // Muat token yang sudah tersimpan sebelumnya
        etApiKey.setText(prefs.getString("api_key", ""))

        btnSaveToken.setOnClickListener {
            val token = etApiKey.text.toString().trim()
            if (token.isEmpty()) {
                Toast.makeText(this, "Token tidak boleh kosong!", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            prefs.edit().putString("api_key", token).apply()
            Toast.makeText(this, "Token Gemini berhasil disimpan!", Toast.LENGTH_SHORT).show()
        }

        btnStartOverlay.setOnClickListener {
            if (!Settings.canDrawOverlays(this)) {
                Toast.makeText(this, "Izinkan aplikasi tampil di atas layar terlebih dahulu", Toast.LENGTH_LONG).show()
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
            Toast.makeText(this, "Bubble AI aktif! Silakan keluar dari aplikasi ini.", Toast.LENGTH_SHORT).show()
        }

        btnStopOverlay.setOnClickListener {
            stopService(Intent(this, FloatingAssistantService::class.java))
            Toast.makeText(this, "Bubble AI dimatikan.", Toast.LENGTH_SHORT).show()
        }
    }
}
