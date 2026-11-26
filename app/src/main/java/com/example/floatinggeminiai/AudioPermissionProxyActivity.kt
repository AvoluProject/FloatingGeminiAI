package com.example.floatinggeminiai

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Toast

class AudioPermissionProxyActivity : Activity() {

    private val REQ_RECORD_AUDIO = 4001

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
            notifyServiceReady()
            finish()
        } else {
            requestPermissions(arrayOf(Manifest.permission.RECORD_AUDIO), REQ_RECORD_AUDIO)
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQ_RECORD_AUDIO && grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            notifyServiceReady()
        } else {
            Toast.makeText(this, "Izin mikrofon diperlukan untuk Voice Chat", Toast.LENGTH_SHORT).show()
        }
        finish()
    }

    private fun notifyServiceReady() {
        startService(Intent(this, FloatingAssistantService::class.java).apply {
            action = FloatingAssistantService.ACTION_AUDIO_PERMISSION_GRANTED
        })
    }
}
