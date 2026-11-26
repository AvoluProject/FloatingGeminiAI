package com.example.floatinggeminiai.data

import android.content.Context
import com.example.floatinggeminiai.ai.AiProviderType
import com.example.floatinggeminiai.ai.ChatMessage
import com.example.floatinggeminiai.ai.ChatThread
import org.json.JSONArray
import org.json.JSONObject
import java.util.UUID

class ChatRepository(context: Context) {

    private val prefs = context.applicationContext.getSharedPreferences("floamini_data_store", Context.MODE_PRIVATE)

    fun loadAllThreads(): MutableList<ChatThread> {
        val raw = prefs.getString("chat_threads_v6", null) ?: return mutableListOf()
        val list = mutableListOf<ChatThread>()
        try {
            val arr = JSONArray(raw)
            for (i in 0 until arr.length()) {
                val obj = arr.getJSONObject(i)
                val msgArr = obj.optJSONArray("messages") ?: JSONArray()
                val messages = mutableListOf<ChatMessage>()
                for (j in 0 until msgArr.length()) {
                    val m = msgArr.getJSONObject(j)
                    messages.add(
                        ChatMessage(
                            id = m.optString("id", UUID.randomUUID().toString()),
                            role = m.optString("role", "user"),
                            text = m.optString("text", ""),
                            timestamp = m.optString("timestamp", ""),
                            providerBadge = m.optString("providerBadge", "Gemini"),
                            modelName = m.optString("modelName", ""),
                            attachmentLabel = m.optString("attachmentLabel", "").ifEmpty { null }
                        )
                    )
                }
                list.add(
                    ChatThread(
                        id = obj.optString("id", UUID.randomUUID().toString()),
                        title = obj.optString("title", "Sesi Baru"),
                        updatedAt = obj.optLong("updatedAt", System.currentTimeMillis()),
                        messages = messages
                    )
                )
            }
        } catch (_: Exception) {}
        return list
    }

    fun saveAllThreads(threads: List<ChatThread>) {
        val arr = JSONArray()
        for (t in threads.take(40)) {
            val msgArr = JSONArray()
            for (m in t.messages.takeLast(120)) {
                msgArr.put(JSONObject().apply {
                    put("id", m.id)
                    put("role", m.role)
                    put("text", m.text)
                    put("timestamp", m.timestamp)
                    put("providerBadge", m.providerBadge)
                    put("modelName", m.modelName)
                    put("attachmentLabel", m.attachmentLabel ?: "")
                })
            }
            arr.put(JSONObject().apply {
                put("id", t.id)
                put("title", t.title)
                put("updatedAt", t.updatedAt)
                put("messages", msgArr)
            })
        }
        prefs.edit().putString("chat_threads_v6", arr.toString()).apply()
    }

    fun getActiveThreadId(): String {
        return prefs.getString("active_thread_id", "") ?: ""
    }

    fun setActiveThreadId(id: String) {
        prefs.edit().putString("active_thread_id", id).apply()
    }

    fun searchThreads(query: String): List<ChatThread> {
        val q = query.trim().lowercase()
        val all = loadAllThreads()
        if (q.isEmpty()) return all
        return all.filter { thread ->
            thread.title.lowercase().contains(q) ||
                    thread.messages.any { it.text.lowercase().contains(q) }
        }
    }

    fun clearAllThreads() {
        prefs.edit().remove("chat_threads_v6").remove("active_thread_id").apply()
    }

    // Usage Statistics per Provider
    fun recordUsage(provider: AiProviderType, estimatedTokens: Int) {
        val reqKey = "usage_req_${provider.id}"
        val tokKey = "usage_tok_${provider.id}"
        val curReq = prefs.getInt(reqKey, 0) + 1
        val curTok = prefs.getLong(tokKey, 0L) + estimatedTokens.coerceAtLeast(1)
        prefs.edit()
            .putInt(reqKey, curReq)
            .putLong(tokKey, curTok)
            .apply()
    }

    fun getUsageSummaryText(): String {
        val sb = StringBuilder()
        var totalReq = 0
        var totalTok = 0L
        for (p in AiProviderType.values()) {
            val req = prefs.getInt("usage_req_${p.id}", 0)
            val tok = prefs.getLong("usage_tok_${p.id}", 0L)
            if (req > 0) {
                totalReq += req
                totalTok += tok
                sb.append("• ${p.displayName}: $req request (~$tok token)\n")
            }
        }
        if (totalReq == 0) {
            return "Belum ada pemakaian API tercatat pada sesi ini."
        }
        return "Total Keseluruhan: $totalReq request (~$totalTok token)\n\n$sb".trim()
    }

    fun resetUsageStats() {
        val ed = prefs.edit()
        for (p in AiProviderType.values()) {
            ed.remove("usage_req_${p.id}").remove("usage_tok_${p.id}")
        }
        ed.apply()
    }

    // Quick Notes Storage
    fun getQuickNotes(): String = prefs.getString("quick_notes_text", "") ?: ""
    fun saveQuickNotes(text: String) {
        prefs.edit().putString("quick_notes_text", text).apply()
    }
}
