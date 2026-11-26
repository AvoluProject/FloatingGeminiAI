package com.example.floatinggeminiai.ui

import android.animation.ValueAnimator
import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.LinearGradient
import android.graphics.Paint
import android.graphics.RectF
import android.graphics.Shader
import android.util.AttributeSet
import android.view.View
import android.view.animation.LinearInterpolator
import kotlin.math.sin

class VoiceWaveformView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val barCount = 18
    private val barRect = RectF()
    private val barPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
    }
    private var phase = 0f
    private var targetAmplitude = 0.15f
    private var currentAmplitude = 0.15f
    private var animator: ValueAnimator? = null

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        if (w > 0 && h > 0) {
            barPaint.shader = LinearGradient(
                0f, 0f, w.toFloat(), 0f,
                intArrayOf(
                    Color.parseColor("#38BDF8"),
                    Color.parseColor("#818CF8"),
                    Color.parseColor("#E879F9")
                ),
                null,
                Shader.TileMode.CLAMP
            )
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        if (width <= 0 || height <= 0) return

        currentAmplitude += (targetAmplitude - currentAmplitude) * 0.28f
        val spacing = width.toFloat() / (barCount * 2f)
        val barWidth = spacing.coerceAtLeast(3f * resources.displayMetrics.density)
        val centerY = height / 2f
        val maxHalfH = height * 0.44f
        val minHalfH = 3f * resources.displayMetrics.density

        for (i in 0 until barCount) {
            val normPos = i.toFloat() / (barCount - 1)
            val envelope = sin(normPos * Math.PI).toFloat()
            val wave = (sin((phase + i * 0.65f).toDouble()).toFloat() + 1f) / 2f
            val halfH = minHalfH + (maxHalfH * envelope * currentAmplitude * (0.35f + 0.65f * wave))

            val left = (i * 2f + 0.5f) * spacing
            barRect.set(left, centerY - halfH, left + barWidth, centerY + halfH)
            canvas.drawRoundRect(barRect, barWidth / 2f, barWidth / 2f, barPaint)
        }
    }

    fun setAmplitude(amp: Float) {
        targetAmplitude = amp.coerceIn(0.1f, 1.0f)
    }

    fun startAnimation() {
        if (animator?.isRunning == true) return
        animator = ValueAnimator.ofFloat(0f, (Math.PI * 20).toFloat()).apply {
            duration = 12000L
            repeatCount = ValueAnimator.INFINITE
            interpolator = LinearInterpolator()
            addUpdateListener {
                phase = it.animatedValue as Float
                invalidate()
            }
            start()
        }
    }

    fun stopAnimation() {
        animator?.cancel()
        animator = null
        targetAmplitude = 0.12f
        invalidate()
    }

    override fun onDetachedFromWindow() {
        stopAnimation()
        super.onDetachedFromWindow()
    }
}
