package com.example.floatinggeminiai

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.graphics.PixelFormat
import android.os.Build
import android.os.IBinder
import android.view.Gravity
import android.view.LayoutInflater
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.util.concurrent.TimeUnit
import kotlin.math.abs

class FloatingAssistantService : Service() {

    private lateinit var windowManager: WindowManager
    private lateinit var floatingView: View
    private lateinit var params: WindowManager.LayoutParams
    private val serviceJob = Job()
    private val serviceScope = CoroutineScope(Dispatchers.Main + serviceJob)

    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        startForegroundNotification()
        setupFloatingOverlay()
    }

    private fun startForegroundNotification() {
        val channelId = "floating_gemini_channel"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Gemini Floating Assistant",
                NotificationManager.IMPORTANCE_LOW
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }

        val notification: Notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("Gemini AI Assistant Aktif")
            .setContentText("Ketuk bubble mengambang di layar untuk mulai mengobrol.")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .build()

        startForeground(101, notification)
    }

    private fun setupFloatingOverlay() {
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        floatingView = LayoutInflater.from(this).inflate(R.layout.layout_floating_assistant, null)

        val layoutFlag = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        } else {
            @Suppress("DEPRECATION")
            WindowManager.LayoutParams.TYPE_PHONE
        }

        // Awalnya FLAG_NOT_FOCUSABLE agar layar di belakangnya tetap bisa disentuh saat mode bubble
        params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            layoutFlag,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 50
            y = 250
        }

        windowManager.addView(floatingView, params)

        val bubbleView = floatingView.findViewById<LinearLayout>(R.id.bubbleView)
        val popupChatView = floatingView.findViewById<LinearLayout>(R.id.popupChatView)
        val btnMinimizePopup = floatingView.findViewById<TextView>(R.id.btnMinimizePopup)
        val btnToggleTokenPanel = floatingView.findViewById<TextView>(R.id.btnToggleTokenPanel)
        val tokenPanel = floatingView.findViewById<LinearLayout>(R.id.tokenPanel)
        val etPopupToken = floatingView.findViewById<EditText>(R.id.etPopupToken)
        val btnSavePopupToken = floatingView.findViewById<Button>(R.id.btnSavePopupToken)
        val scrollChat = floatingView.findViewById<ScrollView>(R.id.scrollChat)
        val tvChatHistory = floatingView.findViewById<TextView>(R.id.tvChatHistory)
        val etPrompt = floatingView.findViewById<EditText>(R.id.etPrompt)
        val btnSendPrompt = floatingView.findViewById<Button>(R.id.btnSendPrompt)

        val prefs = getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        etPopupToken.setText(prefs.getString("api_key", ""))

        // Logika Geser (Drag) & Klik pada Bubble
        bubbleView.setOnTouchListener(object : View.OnTouchListener {
            private var initialX = 0
            private var initialY = 0
            private var initialTouchX = 0f
            private var initialTouchY = 0f

            override fun onTouch(v: View, event: MotionEvent): Boolean {
                when (event.action) {
                    MotionEvent.ACTION_DOWN -> {
                        initialX = params.x
                        initialY = params.y
                        initialTouchX = event.rawX
                        initialTouchY = event.rawY
                        return true
                    }
                    MotionEvent.ACTION_MOVE -> {
                        params.x = initialX + (event.rawX - initialTouchX).toInt()
                        params.y = initialY + (event.rawY - initialTouchY).toInt()
                        windowManager.updateViewLayout(floatingView, params)
                        return true
                    }
                    MotionEvent.ACTION_UP -> {
                        val diffX = abs(event.rawX - initialTouchX)
                        val diffY = abs(event.rawY - initialTouchY)
                        // Jika pergeseran sangat kecil, anggap sebagai KLIK untuk membuka popup
                        if (diffX < 10 && diffY < 10) {
                            openPopupChat(bubbleView, popupChatView)
                        }
                        return true
                    }
                }
                return false
            }
        })

        // Perkecil kembali ke bentuk Bubble
        btnMinimizePopup.setOnClickListener {
            closePopupChat(bubbleView, popupChatView)
        }

        // Buka/Tutup Panel Ubah Token di dalam Popup
        btnToggleTokenPanel.setOnClickListener {
            tokenPanel.visibility = if (tokenPanel.visibility == View.VISIBLE) View.GONE else View.VISIBLE
        }

        // Simpan Token dari dalam Popup
        btnSavePopupToken.setOnClickListener {
            val newToken = etPopupToken.text.toString().trim()
            if (newToken.isNotEmpty()) {
                prefs.edit().putString("api_key", newToken).apply()
                tokenPanel.visibility = View.GONE
                Toast.makeText(this, "Token diperbarui!", Toast.LENGTH_SHORT).show()
            }
        }

        // Kirim Pertanyaan ke Gemini API
        btnSendPrompt.setOnClickListener {
            val prompt = etPrompt.text.toString().trim()
            val apiKey = prefs.getString("api_key", "") ?: ""

            if (prompt.isEmpty()) return@setOnClickListener
            if (apiKey.isEmpty()) {
                tokenPanel.visibility = View.VISIBLE
                Toast.makeText(this, "Harap isi Gemini API Token terlebih dahulu!", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            // Tampilkan pesan pengguna di layar
            tvChatHistory.append("\n\nKamu: $prompt")
            etPrompt.text.clear()
            btnSendPrompt.isEnabled = false
            btnSendPrompt.text = "..."

            scrollChat.post { scrollChat.fullScroll(View.FOCUS_DOWN) }

            serviceScope.launch {
                val reply = callGeminiApi(apiKey, prompt)
                tvChatHistory.append("\n\nAI: $reply")
                btnSendPrompt.isEnabled = true
                btnSendPrompt.text = "Kirim"
                scrollChat.post { scrollChat.fullScroll(View.FOCUS_DOWN) }
            }
        }
    }

    private fun openPopupChat(bubbleView: View, popupChatView: View) {
        bubbleView.visibility = View.GONE
        popupChatView.visibility = View.VISIBLE
        // Hapus FLAG_NOT_FOCUSABLE agar keyboard Android bisa muncul saat mengetik di EditText
        params.flags = WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL
        windowManager.updateViewLayout(floatingView, params)
    }

    private fun closePopupChat(bubbleView: View, popupChatView: View) {
        popupChatView.visibility = View.GONE
        bubbleView.visibility = View.VISIBLE
        // Kembalikan FLAG_NOT_FOCUSABLE agar sentuhan di luar bubble diteruskan ke aplikasi di belakangnya
        params.flags = WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
        windowManager.updateViewLayout(floatingView, params)
    }

    private suspend fun callGeminiApi(apiKey: String, prompt: String): String = withContext(Dispatchers.IO) {
        try {
            val url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key=$apiKey"
            
            val jsonBody = JSONObject().apply {
                put("contents", JSONArray().apply {
                    put(JSONObject().apply {
                        put("parts", JSONArray().apply {
                            put(JSONObject().apply {
                                put("text", prompt)
                            })
                        })
                    })
                })
            }

            val requestBody = jsonBody.toString().toRequestBody("application/json; charset=utf-8".toMediaType())
            val request = Request.Builder()
                .url(url)
                .post(requestBody)
                .build()

            httpClient.newCall(request).execute().use { response ->
                val responseString = response.body?.string() ?: ""
                if (!response.isSuccessful) {
                    return@withContext "Error (${response.code}): Periksa kembali API Token Anda."
                }
                val jsonResponse = JSONObject(responseString)
                val candidates = jsonResponse.optJSONArray("candidates")
                if (candidates != null && candidates.length() > 0) {
                    val content = candidates.getJSONObject(0).optJSONObject("content")
                    val parts = content?.optJSONArray("parts")
                    if (parts != null && parts.length() > 0) {
                        return@withContext parts.getJSONObject(0).optString("text", "Tidak ada jawaban.")
                    }
                }
                return@withContext "Respons kosong dari Gemini."
            }
        } catch (e: Exception) {
            return@withContext "Gagal terhubung: ${e.localizedMessage}"
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        serviceJob.cancel()
        if (::floatingView.isInitialized) {
            windowManager.removeView(floatingView)
        }
    }
}
