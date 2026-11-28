package com.example.floatinggeminiai.ui

import android.animation.ValueAnimator
import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Matrix
import android.graphics.Paint
import android.graphics.RectF
import android.graphics.SweepGradient
import android.util.AttributeSet
import android.view.View
import android.view.animation.LinearInterpolator
import kotlin.math.sin

class SiriEdgeGlowView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var rotationAngle = 0f
    private var glowIntensity = 0f
    private var animator: ValueAnimator? = null
    private val shaderMatrix = Matrix()
    private var sweepShader: SweepGradient? = null

    private val outerGlowPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { style = Paint.Style.STROKE }
    private val innerRimPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { style = Paint.Style.STROKE }
    private val outerRect = RectF()
    private val innerRect = RectF()

    private val siriColors = intArrayOf(
        Color.parseColor("#38BDF8"),
        Color.parseColor("#818CF8"),
        Color.parseColor("#E879F9"),
        Color.parseColor("#FB7185"),
        Color.parseColor("#34D399"),
        Color.parseColor("#38BDF8")
    )

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        if (w > 0 && h > 0) {
            sweepShader = SweepGradient(w / 2f, h / 2f, siriColors, null)
            outerGlowPaint.shader = sweepShader
            innerRimPaint.shader = sweepShader
            val d = resources.displayMetrics.density
            outerGlowPaint.strokeWidth = 22f * d
            innerRimPaint.strokeWidth = 5f * d
            outerRect.set(11f * d, 11f * d, w - 11f * d, h - 11f * d)
            innerRect.set(3f * d, 3f * d, w - 3f * d, h - 3f * d)
        }
    }

    fun startSiriAnimation() {
        animate().alpha(1f).setDuration(240L).start()
        if (animator?.isRunning == true) return
        animator = ValueAnimator.ofFloat(0f, 360f).apply {
            duration = 2800L
            repeatCount = ValueAnimator.INFINITE
            interpolator = LinearInterpolator()
            addUpdateListener {
                rotationAngle = it.animatedValue as Float
                glowIntensity = 0.78f + 0.22f * sin(Math.toRadians(rotationAngle * 2.0)).toFloat()
                invalidate()
            }
            start()
        }
    }

    fun stopAndFreezeAnimation() {
        animator?.cancel()
        animator = null
        alpha = 0f
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val shader = sweepShader ?: return
        shaderMatrix.setRotate(rotationAngle, width / 2f, height / 2f)
        shader.setLocalMatrix(shaderMatrix)
        val corner = 38f * resources.displayMetrics.density
        outerGlowPaint.alpha = (95 * glowIntensity).toInt().coerceIn(30, 140)
        innerRimPaint.alpha = (230 * glowIntensity).toInt().coerceIn(120, 255)
        canvas.drawRoundRect(outerRect, corner, corner, outerGlowPaint)
        canvas.drawRoundRect(innerRect, corner, corner, innerRimPaint)
    }
}

class VoiceWaveformView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var amplitude = 0.1f
    private var phase = 0f
    private val barPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#38BDF8")
        strokeCap = Paint.Cap.ROUND
    }
    private val barRect = RectF()

    fun setAmplitude(amp: Float) {
        amplitude = amp.coerceIn(0.08f, 1.0f)
        phase += 0.35f
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        if (width <= 0 || height <= 0) return
        val bars = 18
        val step = width.toFloat() / bars
        val barWidth = step * 0.45f
        val cy = height / 2f

        for (i in 0 until bars) {
            val wave = sin(phase + i * 0.55f).toFloat()
            val dynamicFactor = (0.35f + 0.65f * ((wave + 1f) / 2f)) * amplitude
            val halfH = (height * 0.44f * dynamicFactor).coerceAtLeast(3f * resources.displayMetrics.density)
            val cx = i * step + step / 2f
            barRect.set(cx - barWidth / 2f, cy - halfH, cx + barWidth / 2f, cy + halfH)
            canvas.drawRoundRect(barRect, barWidth / 2f, barWidth / 2f, barPaint)
        }
    }
}
