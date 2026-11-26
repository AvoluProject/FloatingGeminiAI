package com.example.floatinggeminiai

import android.animation.ValueAnimator
import android.content.Context
import android.graphics.BlurMaskFilter
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Matrix
import android.graphics.Paint
import android.graphics.RectF
import android.graphics.SweepGradient
import android.util.AttributeSet
import android.view.View
import android.view.animation.LinearInterpolator

class SiriEdgeGlowView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val gradientColors = intArrayOf(
        Color.parseColor("#38BDF8"),
        Color.parseColor("#818CF8"),
        Color.parseColor("#E879F9"),
        Color.parseColor("#F472B6"),
        Color.parseColor("#22D3EE"),
        Color.parseColor("#38BDF8")
    )

    private val glowPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 28f * resources.displayMetrics.density
        maskFilter = BlurMaskFilter(24f * resources.displayMetrics.density, BlurMaskFilter.Blur.NORMAL)
    }

    private val coreRimPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 4.5f * resources.displayMetrics.density
    }

    private var sweepGradient: SweepGradient? = null
    private val shaderMatrix = Matrix()
    private val screenRect = RectF()
    private var currentAngle = 0f
    private var pulseScale = 1f
    private var rotationAnimator: ValueAnimator? = null

    init {
        setLayerType(LAYER_TYPE_SOFTWARE, null)
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        if (w > 0 && h > 0) {
            sweepGradient = SweepGradient(w / 2f, h / 2f, gradientColors, null)
            glowPaint.shader = sweepGradient
            coreRimPaint.shader = sweepGradient
            val inset = 4f * resources.displayMetrics.density
            screenRect.set(inset, inset, w - inset, h - inset)
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val gradient = sweepGradient ?: return
        shaderMatrix.setRotate(currentAngle, width / 2f, height / 2f)
        gradient.setLocalMatrix(shaderMatrix)

        val baseStroke = 24f * resources.displayMetrics.density
        glowPaint.strokeWidth = baseStroke * pulseScale

        val cornerRadius = 38f * resources.displayMetrics.density
        canvas.drawRoundRect(screenRect, cornerRadius, cornerRadius, glowPaint)
        canvas.drawRoundRect(screenRect, cornerRadius, cornerRadius, coreRimPaint)
    }

    fun startSiriAnimation() {
        if (rotationAnimator?.isRunning == true) return
        rotationAnimator = ValueAnimator.ofFloat(0f, 360f).apply {
            duration = 2800L
            repeatCount = ValueAnimator.INFINITE
            interpolator = LinearInterpolator()
            addUpdateListener { anim ->
                currentAngle = anim.animatedValue as Float
                val rad = Math.toRadians(currentAngle.toDouble() * 2.0)
                pulseScale = 0.88f + (0.24f * ((Math.sin(rad).toFloat() + 1f) / 2f))
                invalidate()
            }
            start()
        }
    }

    fun stopAndFreezeAnimation() {
        rotationAnimator?.cancel()
        rotationAnimator = null
    }

    override fun onDetachedFromWindow() {
        stopAndFreezeAnimation()
        super.onDetachedFromWindow()
    }
}
