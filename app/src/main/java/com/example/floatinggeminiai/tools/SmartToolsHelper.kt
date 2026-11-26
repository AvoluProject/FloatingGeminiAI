package com.example.floatinggeminiai.tools

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.pdf.PdfRenderer
import android.net.Uri
import android.text.Spannable
import android.text.SpannableStringBuilder
import android.text.style.BackgroundColorSpan
import android.text.style.ForegroundColorSpan
import android.text.style.StyleSpan
import android.text.style.TypefaceSpan
import android.util.Base64
import java.io.ByteArrayOutputStream
import java.io.InputStreamReader
import kotlin.math.pow

data class ProcessedAttachment(
    val displayName: String,
    val extractedText: String,
    val imageBase64List: List<String>
)

object SmartToolsHelper {

    fun processUriAttachment(context: Context, uri: Uri): ProcessedAttachment? {
        val resolver = context.contentResolver
        val mime = resolver.getType(uri) ?: ""
        val name = uri.lastPathSegment?.substringAfterLast('/') ?: "Lampiran"

        return when {
            mime == "application/pdf" || name.endsWith(".pdf", ignoreCase = true) -> {
                extractPdfPagesAsImages(context, uri, name)
            }
            mime.startsWith("image/") -> {
                val b64 = encodeImageUriToBase64(context, uri) ?: return null
                ProcessedAttachment(
                    displayName = "Gambar: $name",
                    extractedText = "",
                    imageBase64List = listOf(b64)
                )
            }
            else -> {
                val text = readTextFromUri(context, uri)
                if (text.isBlank()) null
                else ProcessedAttachment(
                    displayName = "Dokumen: $name",
                    extractedText = text.take(12000),
                    imageBase64List = emptyList()
                )
            }
        }
    }

    private fun extractPdfPagesAsImages(context: Context, uri: Uri, name: String): ProcessedAttachment? {
        return try {
            val pfd = context.contentResolver.openFileDescriptor(uri, "r") ?: return null
            val renderer = PdfRenderer(pfd)
            val pageCount = renderer.pageCount.coerceAtMost(3)
            val images = mutableListOf<String>()

            for (i in 0 until pageCount) {
                val page = renderer.openPage(i)
                val targetW = 768
                val targetH = (page.height.toFloat() / page.width.toFloat() * targetW).toInt().coerceAtLeast(256)
                val bmp = Bitmap.createBitmap(targetW, targetH, Bitmap.Config.ARGB_8888)
                bmp.eraseColor(Color.WHITE)
                page.render(bmp, null, null, PdfRenderer.Page.RENDER_MODE_FOR_DISPLAY)
                page.close()

                val out = ByteArrayOutputStream()
                bmp.compress(Bitmap.CompressFormat.JPEG, 72, out)
                bmp.recycle()
                images.add(Base64.encodeToString(out.toByteArray(), Base64.NO_WRAP))
            }
            renderer.close()
            pfd.close()

            ProcessedAttachment(
                displayName = "PDF ($pageCount hal): $name",
                extractedText = "[Lampiran dokumen PDF $name berisi $pageCount halaman visual]",
                imageBase64List = images
            )
        } catch (_: Exception) {
            null
        }
    }

    fun encodeImageUriToBase64(context: Context, uri: Uri): String? {
        return try {
            val input = context.contentResolver.openInputStream(uri) ?: return null
            val original = BitmapFactory.decodeStream(input)
            input.close()
            if (original == null) return null

            val maxDim = 960
            val scale = if (original.width > maxDim || original.height > maxDim) {
                maxDim.toFloat() / maxOf(original.width, original.height)
            } else 1.0f

            val scaled = if (scale < 1.0f) {
                Bitmap.createScaledBitmap(
                    original,
                    (original.width * scale).toInt(),
                    (original.height * scale).toInt(),
                    true
                )
            } else original

            val out = ByteArrayOutputStream()
            scaled.compress(Bitmap.CompressFormat.JPEG, 72, out)
            if (scaled !== original) scaled.recycle()
            original.recycle()

            Base64.encodeToString(out.toByteArray(), Base64.NO_WRAP)
        } catch (_: Exception) {
            null
        }
    }

    private fun readTextFromUri(context: Context, uri: Uri): String {
        return try {
            val input = context.contentResolver.openInputStream(uri) ?: return ""
            InputStreamReader(input, Charsets.UTF_8).use { it.readText() }
        } catch (_: Exception) {
            ""
        }
    }

    /**
     * Rich Markdown & Code Syntax Highlighter untuk gelembung chat
     */
    fun formatRichMarkdown(raw: String): CharSequence {
        val builder = SpannableStringBuilder()
        val segments = raw.split("```")

        for (i in segments.indices) {
            val seg = segments[i]
            if (i % 2 == 1) {
                // Code Block
                val firstNewline = seg.indexOf('\n')
                val codeBody = if (firstNewline != -1) seg.substring(firstNewline + 1).trimEnd() else seg.trim()
                val start = builder.length
                builder.append("\n$codeBody\n")
                val end = builder.length
                builder.setSpan(TypefaceSpan("monospace"), start, end, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
                builder.setSpan(BackgroundColorSpan(Color.parseColor("#CC070B14")), start, end, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
                builder.setSpan(ForegroundColorSpan(Color.parseColor("#7DD3FC")), start, end, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
            } else {
                // Normal text with inline **bold** and `code`
                appendFormattedInline(builder, seg)
            }
        }
        return builder
    }

    private fun appendFormattedInline(builder: SpannableStringBuilder, text: String) {
        var idx = 0
        while (idx < text.length) {
            if (text.startsWith("**", idx)) {
                val endIdx = text.indexOf("**", idx + 2)
                if (endIdx != -1) {
                    val content = text.substring(idx + 2, endIdx)
                    val s = builder.length
                    builder.append(content)
                    builder.setSpan(StyleSpan(Typeface.BOLD), s, builder.length, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
                    idx = endIdx + 2
                    continue
                }
            }
            if (text[idx] == '`') {
                val endIdx = text.indexOf('`', idx + 1)
                if (endIdx != -1) {
                    val content = text.substring(idx + 1, endIdx)
                    val s = builder.length
                    builder.append(" $content ")
                    builder.setSpan(TypefaceSpan("monospace"), s, builder.length, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
                    builder.setSpan(BackgroundColorSpan(Color.parseColor("#3338BDF8")), s, builder.length, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
                    idx = endIdx + 1
                    continue
                }
            }
            builder.append(text[idx])
            idx++
        }
    }

    /**
     * Safe Mathematical Expression Evaluator (Floating Calculator)
     */
    fun evaluateMathExpression(expr: String): String {
        val clean = expr.replace("×", "*").replace("÷", "/").replace(",", ".").replace(" ", "")
        if (clean.isEmpty()) return "0"
        return try {
            val result = object : Any() {
                var pos = -1
                var ch = 0

                fun nextChar() {
                    ch = if (++pos < clean.length) clean[pos].code else -1
                }

                fun eat(charToEat: Int): Boolean {
                    while (ch == ' '.code) nextChar()
                    if (ch == charToEat) {
                        nextChar()
                        return true
                    }
                    return false
                }

                fun parse(): Double {
                    nextChar()
                    val x = parseExpression()
                    if (pos < clean.length) throw RuntimeException("Unexpected")
                    return x
                }

                fun parseExpression(): Double {
                    var x = parseTerm()
                    while (true) {
                        when {
                            eat('+'.code) -> x += parseTerm()
                            eat('-'.code) -> x -= parseTerm()
                            else -> return x
                        }
                    }
                }

                fun parseTerm(): Double {
                    var x = parseFactor()
                    while (true) {
                        when {
                            eat('*'.code) -> x *= parseFactor()
                            eat('/'.code) -> x /= parseFactor()
                            eat('%'.code) -> x %= parseFactor()
                            else -> return x
                        }
                    }
                }

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
                        x = clean.substring(startPos, pos).toDouble()
                    } else {
                        throw RuntimeException("Unexpected")
                    }
                    if (eat('^'.code)) x = x.pow(parseFactor())
                    return x
                }
            }.parse()

            if (result.isNaN() || result.isInfinite()) "Error"
            else if (result % 1.0 == 0.0) result.toLong().toString()
            else String.format("%.6f", result).trimEnd('0').trimEnd('.')
        } catch (_: Exception) {
            "Format salah"
        }
    }
}
