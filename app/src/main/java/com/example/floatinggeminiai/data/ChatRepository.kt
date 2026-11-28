package com.example.floatinggeminiai.data

import android.content.Context
import com.example.floatinggeminiai.ai.ChatMessage
import com.example.floatinggeminiai.ai.ChatThread
import org.json.JSONArray
import org.json.JSONObject

class ChatRepository(context: Context) {

    private val prefs = context.applicationContext.getSharedPreferences("floamini_chat_data", Context.MODE_PRIVATE)

    fun loadAllThreads(): MutableList<ChatThread> {
        val raw = prefs.getString("threads_json", null) ?: return mutableListOf()
        return try {
            val arr = JSONArray(raw)
            val result = mutableListOf<ChatThread>()
            for (i in 0 until arr.length()) {
                val obj = arr.getJSONObject(i)
                val msgsArr = obj.optJSONArray("messages") ?: JSONArray()
                val msgs = mutableListOf<ChatMessage>()
                for (j in 0 until msgsArr.length()) {
                    val m = msgsArr.getJSONObject(j)
                    msgs.add(
                        ChatMessage(
                            id = m.optString("id", System.nanoTime().toString()),
                            role = m.optString("role", "user"),
                            content = m.optString("content", ""),
                            providerTag = m.optString("providerTag", ""),
                            timestamp = m.optLong("timestamp", System.currentTimeMillis())
                        )
                    )
                }
                result.add(
                    ChatThread(
                        id = obj.getString("id"),
                        title = obj.optString("title", "Sesi Floamini"),
                        messages = msgs,
                        updatedAt = obj.optLong("updatedAt", System.currentTimeMillis())
                    )
                )
            }
            result
        } catch (_: Exception) {
            mutableListOf()
        }
    }

    fun saveAllThreads(threads: List<ChatThread>) {
        val arr = JSONArray()
        for (t in threads.take(30)) {
            val msgsArr = JSONArray()
            for (m in t.messages.takeLast(80)) {
                msgsArr.put(
                    JSONObject()
                        .put("id", m.id)
                        .put("role", m.role)
                        .put("content", m.content)
                        .put("providerTag", m.providerTag)
                        .put("timestamp", m.timestamp)
                )
            }
            arr.put(
                JSONObject()
                    .put("id", t.id)
                    .put("title", t.title)
                    .put("messages", msgsArr)
                    .put("updatedAt", t.updatedAt)
            )
        }
        prefs.edit().putString("threads_json", arr.toString()).apply()
    }

    fun getOrCreateActiveThread(): ChatThread {
        val all = loadAllThreads()
        val activeId = prefs.getString("active_thread_id", null)
        val found = all.find { it.id == activeId } ?: all.firstOrNull()
        if (found != null) return found

        val created = ChatThread(id = "session_${System.currentTimeMillis()}", title = "Sesi Utama")
        all.add(0, created)
        saveAllThreads(all)
        setActiveThreadId(created.id)
        return created
    }

    fun createNewThread(title: String = "Sesi Baru"): ChatThread {
        val all = loadAllThreads()
        val created = ChatThread(id = "session_${System.currentTimeMillis()}", title = title)
        all.add(0, created)
        saveAllThreads(all)
        setActiveThreadId(created.id)
        return created
    }

    fun saveThread(thread: ChatThread) {
        val all = loadAllThreads()
        val idx = all.indexOfFirst { it.id == thread.id }
        thread.updatedAt = System.currentTimeMillis()
        if (idx >= 0) {
            all[idx] = thread
        } else {
            all.add(0, thread)
        }
        saveAllThreads(all)
    }

    fun setActiveThreadId(id: String) {
        prefs.edit().putString("active_thread_id", id).apply()
    }

    fun searchThreads(query: String): List<ChatThread> {
        val q = query.trim().lowercase()
        val all = loadAllThreads()
        if (q.isEmpty()) return all
        return all.filter { t ->
            t.title.lowercase().contains(q) || t.messages.any { it.content.lowercase().contains(q) }
        }
    }

    fun clearAllHistory() {
        prefs.edit().remove("threads_json").remove("active_thread_id").apply()
    }

    fun recordUsage(providerName: String, charsOut: Int) {
        val totalReq = prefs.getInt("usage_total_req", 0) + 1
        val totalChars = prefs.getLong("usage_total_chars", 0L) + charsOut
        val provCount = prefs.getInt("usage_prov_$providerName", 0) + 1
        prefs.edit()
            .putInt("usage_total_req", totalReq)
            .putLong("usage_total_chars", totalChars)
            .putInt("usage_prov_$providerName", provCount)
            .apply()
    }

    fun getUsageSummary(): String {
        val req = prefs.getInt("usage_total_req", 0)
        val chars = prefs.getLong("usage_total_chars", 0L)
        val estTokens = chars / 4
        return "Total Permintaan: $req kali | Estimasi Token Output: ~$estTokens token"
    }

    fun resetUsage() {
        prefs.edit().putInt("usage_total_req", 0).putLong("usage_total_chars", 0L).apply()
    }

    fun getQuickNotes(): String = prefs.getString("quick_notes", "").orEmpty()
    fun saveQuickNotes(notes: String) = prefs.edit().putString("quick_notes", notes).apply()
}
