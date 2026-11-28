package com.example.floatinggeminiai

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Toast
import androidx.core.content.ContextCompat

class ExternalTriggerActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (!Settings.canDrawOverlays(this)) {
            Toast.makeText(this, "Aktifkan izin Overlay Floamini terlebih dahulu.", Toast.LENGTH_SHORT).show()
            startActivity(Intent(this, MainActivity::class.java))
            finish()
            return
        }

        val selectedText = intent.getCharSequenceExtra(Intent.EXTRA_PROCESS_TEXT)?.toString()
            ?: intent.getStringExtra(Intent.EXTRA_TEXT)
        val sharedImageUri: Uri? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            intent.getParcelableExtra(Intent.EXTRA_STREAM, Uri::class.java)
        } else {
            @Suppress("DEPRECATION")
            intent.getParcelableExtra(Intent.EXTRA_STREAM)
        }

        val svc = Intent(this, FloatingAssistantService::class.java).apply {
            action = FloatingAssistantService.ACTION_EXTERNAL_QUERY
            if (!selectedText.isNullOrBlank()) putExtra("external_text", selectedText)
            if (sharedImageUri != null) putExtra("file_uri", sharedImageUri.toString())
        }
        ContextCompat.startForegroundService(this, svc)
        finish()
    }
}
