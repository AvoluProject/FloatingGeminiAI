package com.example.floatinggeminiai

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import androidx.core.content.ContextCompat

class FilePickerProxyActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val picker = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "*/*"
            putExtra(
                Intent.EXTRA_MIME_TYPES,
                arrayOf("application/pdf", "image/*", "text/*")
            )
        }
        startActivityForResult(picker, 9002)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        val uri = data?.data
        if (requestCode == 9002 && resultCode == RESULT_OK && uri != null) {
            val svc = Intent(this, FloatingAssistantService::class.java).apply {
                action = FloatingAssistantService.ACTION_FILE_PICKED
                putExtra("file_uri", uri.toString())
            }
            ContextCompat.startForegroundService(this, svc)
        }
        finish()
    }
}
