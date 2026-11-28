package com.example.floatinggeminiai.security

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class SecureVault(context: Context) {

    private val prefs: SharedPreferences = createEncryptedPrefs(context.applicationContext)

    private fun createEncryptedPrefs(ctx: Context): SharedPreferences {
        return try {
            val masterKey = MasterKey.Builder(ctx)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build()
            EncryptedSharedPreferences.create(
                ctx,
                "floamini_secure_vault",
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        } catch (_: Throwable) {
            ctx.getSharedPreferences("floamini_secure_vault_fallback", Context.MODE_PRIVATE)
        }
    }

    fun saveApiKey(providerId: String, apiKey: String) {
        prefs.edit().putString("key_$providerId", apiKey.trim()).apply()
    }

    fun getApiKey(providerId: String): String {
        return prefs.getString("key_$providerId", "")?.trim().orEmpty()
    }

    fun hasApiKey(providerId: String): Boolean {
        return getApiKey(providerId).isNotEmpty()
    }

    fun saveCustomEndpoint(baseUrl: String, modelId: String) {
        prefs.edit()
            .putString("custom_base_url", baseUrl.trim())
            .putString("custom_model_id", modelId.trim())
            .apply()
    }

    fun getCustomBaseUrl(): String {
        return prefs.getString("custom_base_url", "https://api.openai.com/v1")?.trim().orEmpty()
    }

    fun getCustomModelId(): String {
        return prefs.getString("custom_model_id", "gpt-4o-mini")?.trim().orEmpty()
    }

    fun getMaskedKey(providerId: String): String {
        val raw = getApiKey(providerId)
        if (raw.length <= 8) return if (raw.isEmpty()) "Belum diisi" else "••••••••"
        return "${raw.take(4)}••••••${raw.takeLast(4)}"
    }
}
