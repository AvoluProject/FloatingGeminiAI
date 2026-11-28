package com.example.floatinggeminiai

import android.content.Intent
import android.os.Build
import android.provider.Settings
import android.service.quicksettings.Tile
import android.service.quicksettings.TileService
import androidx.core.content.ContextCompat

class FloaminiTileService : TileService() {

    override fun onStartListening() {
        super.onStartListening()
        qsTile?.apply {
            state = Tile.STATE_ACTIVE
            label = "Floamini AI"
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                subtitle = "Siri & Overlay"
            }
            updateTile()
        }
    }

    override fun onClick() {
        super.onClick()
        if (!Settings.canDrawOverlays(this)) {
            val openApp = Intent(this, MainActivity::class.java).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            startActivityAndCollapse(openApp)
            return
        }

        val summonIntent = Intent(this, FloatingAssistantService::class.java).apply {
            action = FloatingAssistantService.ACTION_SUMMON_SIRI
        }
        ContextCompat.startForegroundService(this, summonIntent)
    }
}
