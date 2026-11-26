package com.example.floatinggeminiai.security

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import com.example.floatinggeminiai.ai.AiProviderType

class SecureVault(context: Context) {

    private val appContext = context.applicationContext

    private val securePrefs: SharedPreferences by lazy {
        try {
            val masterKey = MasterKey.Builder(appContext)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build()
            EncryptedSharedPreferences.create(
                appContext,
                "floamini_encrypted_vault",
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        } catch (_: Exception) {
            appContext.getSharedPreferences("floamini_vault_fallback", Context.MODE_PRIVATE)
        }
    }

    init {
        migrateLegacyGeminiKeyIfNeeded()
    }

    private fun migrateLegacyGeminiKeyIfNeeded() {
        val legacyPrefs = appContext.getSharedPreferences("gemini_prefs", Context.MODE_PRIVATE)
        val legacyKey = legacyPrefs.getString("api_key", "") ?: ""
        if (legacyKey.isNotEmpty() && getApiKey(AiProviderType.GEMINI).isEmpty()) {
            setApiKey(AiProviderType.GEMINI, legacyKey)
            legacyPrefs.edit().remove("api_key").apply()
        }
    }

    fun getApiKey(provider: AiProviderType): String {
        return securePrefs.getString("key_${provider.id}", "")?.trim() ?: ""
    }

    fun setApiKey(provider: AiProviderType, apiKey: String) {
        val clean = apiKey.trim()
        if (clean.isEmpty()) {
            securePrefs.edit().remove("key_${provider.id}").apply()
        } else {
            securePrefs.edit().putString("key_${provider.id}", clean).apply()
        }
    }

    fun hasAnyConfiguredKey(): Boolean {
        return AiProviderType.values().any { getApiKey(it).isNotEmpty() }
    }

    fun getConfiguredProviders(): List<AiProviderType> {
        return AiProviderType.values().filter { getApiKey(it).isNotEmpty() }
    }

    fun getSelectedModel(provider: AiProviderType): String {
        return securePrefs.getString("model_${provider.id}", provider.defaultModel)
            ?.ifBlank { provider.defaultModel } ?: provider.defaultModel
    }

    fun setSelectedModel(provider: AiProviderType, modelId: String) {
        securePrefs.edit().putString("model_${provider.id}", modelId.trim()).apply()
    }

    fun getCustomBaseUrl(): String {
        return securePrefs.getString("custom_base_url", "https://api.openai.com/v1")
            ?.ifBlank { "https://api.openai.com/v1" } ?: "https://api.openai.com/v1"
    }

    fun setCustomBaseUrl(url: String) {
        securePrefs.edit().putString("custom_base_url", url.trim().trimEnd('/')).apply()
    }

    fun clearAllCredentials() {
        securePrefs.edit().clear().apply()
    }
}
