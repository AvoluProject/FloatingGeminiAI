package com.example.floatinggeminiai.tools

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.pdf.PdfRenderer
import android.net.Uri
import android.provider.OpenableColumns
import android.util.Base64
import java.io.ByteArrayOutputStream
import java.io.InputStreamReader

data class ProcessedAttachment(
    val displayName: String,
    val extractedText: String = "",
    val base64Images: List<String> = emptyList()
)

object SmartToolsHelper {

    fun processUri(context: Context, uri: Uri): ProcessedAttachment {
        val name = queryFileName(context, uri)
        val mime = context.contentResolver.getType(uri).orEmpty().lowercase()

        return when {
            mime.contains("pdf") || name.lowercase().endsWith(".pdf") -> {
                extractPdfPagesAsBase64(context, uri, name)
            }
            mime.startsWith("image/") -> {
                val b64 = encodeImageUriToBase64(context, uri)
                ProcessedAttachment(
                    displayName = name,
                    base64Images = if (b64 != null) listOf(b64) else emptyList()
                )
            }
            else -> {
                val text = readTextUri(context, uri)
                ProcessedAttachment(displayName = name, extractedText = text)
            }
        }
    }

    private fun queryFileName(context: Context, uri: Uri): String {
        var result = "Lampiran"
        try {
            context.contentResolver.query(uri, null, null, null, null)?.use { cursor ->
                val idx = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                if (idx >= 0 && cursor.moveToFirst()) {
                    result = cursor.getString(idx) ?: result
                }
            }
        } catch (_: Exception) {
        }
        return result
    }

    private fun readTextUri(context: Context, uri: Uri): String {
        return try {
            context.contentResolver.openInputStream(uri)?.use { stream ->
                InputStreamReader(stream).readText().take(12000)
            }.orEmpty()
        } catch (_: Exception) {
            ""
        }
    }

    private fun encodeImageUriToBase64(context: Context, uri: Uri): String? {
        return try {
            val raw = context.contentResolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it) } ?: return null
            bitmapToBase64(raw, 1024)
        } catch (_: Exception) {
            null
        }
    }

    private fun extractPdfPagesAsBase64(context: Context, uri: Uri, name: String): ProcessedAttachment {
        val images = mutableListOf<String>()
        try {
            context.contentResolver.openFileDescriptor(uri, "r")?.use { pfd ->
                PdfRenderer(pfd).use { renderer ->
                    val maxPages = renderer.pageCount.coerceAtMost(3)
                    for (i in 0 until maxPages) {
                        renderer.openPage(i).use { page ->
                            val bmp = Bitmap.createBitmap(page.width.coerceAtMost(1024), page.height.coerceAtMost(1400), Bitmap.Config.ARGB_8888)
                            val canvas = Canvas(bmp)
                            canvas.drawColor(Color.WHITE)
                            page.render(bmp, null, null, PdfRenderer.Page.RENDER_MODE_FOR_DISPLAY)
                            images.add(bitmapToBase64(bmp, 1024))
                            bmp.recycle()
                        }
                    }
                }
            }
        } catch (_: Exception) {
        }
        return ProcessedAttachment(displayName = "$name (${images.size} hal.)", base64Images = images)
    }

    fun bitmapToBase64(src: Bitmap, maxDim: Int): String {
        val ratio = minOf(maxDim.toFloat() / src.width, maxDim.toFloat() / src.height, 1.0f)
        val scaled = if (ratio < 1.0f) {
            Bitmap.createScaledBitmap(src, (src.width * ratio).toInt().coerceAtLeast(1), (src.height * ratio).toInt().coerceAtLeast(1), true)
        } else {
            src
        }
        val out = ByteArrayOutputStream()
        scaled.compress(Bitmap.CompressFormat.JPEG, 76, out)
        if (scaled !== src) scaled.recycle()
        return Base64.encodeToString(out.toByteArray(), Base64.NO_WRAP)
    }

    fun evaluateMath(expression: String): String {
        val cleaned = expression.replace(" ", "").replace("×", "*").replace("÷", "/")
        if (cleaned.isEmpty()) return "0"
        return try {
            var pos = -1
            var ch = 0
            fun nextChar() {
                pos++
                ch = if (pos < cleaned.length) cleaned[pos].code else -1
            }
            fun eat(charToEat: Int): Boolean {
                while (ch == ' '.code) nextChar()
                if (ch == charToEat) {
                    nextChar()
                    return true
                }
                return false
            }
            fun parseExpression(): Double {
                fun parseTerm(): Double {
                    fun parseFactor(): Double {
                        if (eat('+'.code)) return parseFactor()
                        if (eat('-'.code)) return -parseFactor()
                        var x: Double
                        val startPos = pos
                        if (eat('('.code)) {
                            x = parseExpression()
                            eat(')'.code)
                        } else if ((ch in '0'.code..'9'.code) || ch == '.'.code) {
                            while ((ch in '0'.code..'9'.code) || ch == '.'.code) nextChar()
                            x = cleaned.substring(startPos, pos).toDouble()
                        } else {
                            throw RuntimeException("Unexpected")
                        }
                        return x
                    }
                    var x = parseFactor()
                    while (true) {
                        x = when {
                            eat('*'.code) -> x * parseFactor()
                            eat('/'.code) -> x / parseFactor()
                            else -> return x
                        }
                    }
                }
                var x = parseTerm()
                while (true) {
                    x = when {
                        eat('+'.code) -> x + parseTerm()
                        eat('-'.code) -> x - parseTerm()
                        else -> return x
                    }
                }
            }
            nextChar()
            val v = parseExpression()
            if (v % 1.0 == 0.0) v.toLong().toString() else String.format("%.4f", v).trimEnd('0').trimEnd('.')
        } catch (_: Exception) {
            "Format salah"
        }
    }
}
