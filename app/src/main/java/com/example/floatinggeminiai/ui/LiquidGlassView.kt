package com.example.floatinggeminiai.ui

import android.animation.ValueAnimator
import android.content.Context
import android.content.res.Configuration
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.LinearGradient
import android.graphics.Paint
import android.graphics.Path
import android.graphics.RectF
import android.graphics.RuntimeShader
import android.graphics.Shader
import android.graphics.Typeface
import android.os.Build
import android.util.AttributeSet
import android.view.Gravity
import android.view.HapticFeedbackConstants
import android.view.MotionEvent
import android.view.animation.LinearInterpolator
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import androidx.dynamicanimation.animation.FloatValueHolder
import androidx.dynamicanimation.animation.SpringAnimation
import androidx.dynamicanimation.animation.SpringForce

/**
 * LiquidGlassFrameLayout — Terinspirasi langsung dari Kyant0/AndroidLiquidGlass:
 * - Signed Distance Field (SDF) Rounded-Box Lens Refraction
 * - Physical RGB Chromatic Dispersion di sepanjang bevel kaca
 * - Interactive Gel-Press Bulge & Angle-Aware Specular Rim Highlight
 * - Mendukung varian REGULAR (readability-first untuk UI/Navbar) dan CLEAR (Dynamic Island)
 */
class LiquidGlassFrameLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : FrameLayout(context, attrs, defStyleAttr) {

    enum class GlassMaterialVariant {
        REGULAR,
        CLEAR
    }

    var cornerRadiusDp: Float = 24f
        set(value) {
            field = value
            requestRebuildBounds()
            invalidate()
        }

    var bevelWidthDp: Float = 14f
        set(value) {
            field = value
            invalidate()
        }

    var dispersionStrength: Float = 0.28f
        set(value) {
            field = value
            invalidate()
        }

    var specularIntensity: Float = 0.62f
        set(value) {
            field = value
            invalidate()
        }

    var materialVariant: GlassMaterialVariant = GlassMaterialVariant.REGULAR
        set(value) {
            field = value
            if (width > 0 && height > 0) {
                updateFallbackGradients(width.toFloat(), height.toFloat())
            }
            invalidate()
        }

    var enableGelPress: Boolean = true

    private var touchX: Float = -1f
    private var touchY: Float = -1f
    private var pressProgress: Float = 0f
    private var shimmerPhase: Float = 0f

    private val boundsRect = RectF()
    private val clipPath = Path()
    private val shaderPaint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val fallbackFillPaint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val fallbackRimPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
    }

    private var agslShader: RuntimeShader? = null
    private var ambientAnimator: ValueAnimator? = null
    private var pressSpring: SpringAnimation? = null

    init {
        setWillNotDraw(false)
        initAgslShaderIfSupported()
    }

    private fun initAgslShaderIfSupported() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            val agslCode = listOf(
                "uniform float2 uResolution;",
                "uniform float uCornerRadius;",
                "uniform float uBevelWidth;",
                "uniform float uDispersionStrength;",
                "uniform float uSpecularIntensity;",
                "uniform float2 uTouchPos;",
                "uniform float uPressProgress;",
                "uniform float uTime;",
                "uniform float uIsDark;",
                "uniform float uClearVariant;",
                "float sdRoundedBox(float2 p, float2 b, float r) {",
                "float2 q = abs(p) - b + float2(r);",
                "return min(max(q.x, q.y), 0.0) + length(max(q, float2(0.0))) - r;",
                "}",
                "half4 main(float2 fragCoord) {",
                "float2 center = uResolution * 0.5;",
                "float maxR = min(center.x, center.y);",
                "float radius = clamp(uCornerRadius, 1.0, maxR);",
                "float2 halfSize = center - float2(0.75);",
                "float2 p = fragCoord - center;",
                "float d = sdRoundedBox(p, halfSize, radius);",
                "if (d > 0.0) {",
                "return half4(0.0);",
                "}",
                "// Surface normal via SDF gradient",
                "float2 eps = float2(1.5, 0.0);",
                "float2 grad = float2(",
                "sdRoundedBox(p + eps.xy, halfSize, radius) - sdRoundedBox(p - eps.xy, halfSize, radius),",
                "sdRoundedBox(p + eps.yx, halfSize, radius) - sdRoundedBox(p - eps.yx, halfSize, radius)",
                ");",
                "float2 normal = normalize(grad + float2(0.0001));",
                "// Convex lens profile along bevel rim",
                "float edgeDist = -d;",
                "float rimFactor = clamp(1.0 - (edgeDist / max(uBevelWidth, 1.0)), 0.0, 1.0);",
                "float lensCurve = pow(rimFactor, 2.2);",
                "// Interactive gel-press bulge around touch",
                "float touchDist = length(fragCoord - uTouchPos);",
                "float gelBulge = uPressProgress * exp(-touchDist * 0.011);",
                "// Directional specular light + dynamic touch shift",
                "float2 touchOffset = (uTouchPos - center) * 0.0016 * uPressProgress;",
                "float2 lightDir = normalize(float2(-0.62, -0.78) + touchOffset);",
                "float topSpec = pow(max(dot(normal, lightDir), 0.0), 2.6) * (0.35 + 0.65 * lensCurve);",
                "float bottomRim = pow(max(dot(normal, -lightDir), 0.0), 3.4) * lensCurve * 0.52;",
                "// Physical RGB chromatic dispersion along bevel normal",
                "float angle = atan(normal.y, normal.x) + uTime * 0.45;",
                "float3 dispersion = float3(",
                "0.5 + 0.5 * sin(angle),",
                "0.5 + 0.5 * sin(angle + 2.09439),",
                "0.5 + 0.5 * sin(angle + 4.18879)",
                ") * lensCurve * uDispersionStrength;",
                "// Adaptive Dark/Light & Regular/Clear base glass material",
                "float3 baseDark = mix(float3(0.068, 0.102, 0.185), float3(0.015, 0.022, 0.038), uClearVariant);",
                "float3 baseLight = mix(float3(0.92, 0.95, 0.99), float3(0.96, 0.98, 1.0), uClearVariant);",
                "float3 baseCol = mix(baseLight, baseDark, uIsDark);",
                "// Micro-grain dithering",
                "float grain = (fract(sin(dot(fragCoord, float2(12.9898, 78.233))) * 43758.5453) - 0.5) * 0.015;",
                "float3 rgb = baseCol",
                "+ dispersion",
                "+ float3(0.76, 0.90, 1.0) * (topSpec * uSpecularIntensity + gelBulge * 0.25)",
                "+ float3(0.68, 0.54, 1.0) * bottomRim",
                "+ float3(grain);",
                "float targetAlpha = mix(0.84, 0.76, uClearVariant);",
                "float alpha = clamp(targetAlpha + lensCurve * 0.15 + topSpec * 0.20, 0.0, 0.97);",
                "return half4(half3(rgb * alpha), half(alpha));",
                "}"
            ).joinToString("\n")

            try {
                agslShader = RuntimeShader(agslCode)
                shaderPaint.shader = agslShader
            } catch (_: Throwable) {
                agslShader = null
            }
        }
    }

    private fun isSystemDarkTheme(): Boolean {
        val mode = resources.configuration.uiMode and Configuration.UI_MODE_NIGHT_MASK
        return mode == Configuration.UI_MODE_NIGHT_YES
    }

    private fun requestRebuildBounds() {
        val w = width.toFloat()
        val h = height.toFloat()
        if (w > 0f && h > 0f) {
            boundsRect.set(0f, 0f, w, h)
            val rPx = cornerRadiusDp * resources.displayMetrics.density
            clipPath.reset()
            clipPath.addRoundRect(boundsRect, rPx, rPx, Path.Direction.CW)
        }
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        if (w > 0 && h > 0) {
            requestRebuildBounds()
            if (touchX < 0f) {
                touchX = w / 2f
                touchY = h / 2f
            }
            updateFallbackGradients(w.toFloat(), h.toFloat())
        }
    }

    private fun updateFallbackGradients(w: Float, h: Float) {
        val dark = isSystemDarkTheme()
        fallbackFillPaint.shader = LinearGradient(
            0f, 0f, 0f, h,
            if (materialVariant == GlassMaterialVariant.CLEAR) {
                intArrayOf(Color.parseColor("#E6060912"), Color.parseColor("#F2020306"))
            } else if (dark) {
                intArrayOf(Color.parseColor("#D818243E"), Color.parseColor("#E20B111E"))
            } else {
                intArrayOf(Color.parseColor("#EAFFFFFF"), Color.parseColor("#F0E2E8F0"))
            },
            null,
            Shader.TileMode.CLAMP
        )
        fallbackRimPaint.strokeWidth = 1.4f * resources.displayMetrics.density
        fallbackRimPaint.shader = LinearGradient(
            0f, 0f, w, h,
            intArrayOf(
                Color.parseColor("#B8FFFFFF"),
                Color.parseColor("#6638BDF8"),
                Color.parseColor("#66E879F9")
            ),
            null,
            Shader.TileMode.CLAMP
        )
    }

    override fun dispatchDraw(canvas: Canvas) {
        val w = width.toFloat()
        val h = height.toFloat()
        if (w <= 0f || h <= 0f) {
            super.dispatchDraw(canvas)
            return
        }

        val density = resources.displayMetrics.density
        val rPx = cornerRadiusDp * density
        val shader = agslShader

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU && shader != null) {
            try {
                shader.setFloatUniform("uResolution", w, h)
                shader.setFloatUniform("uCornerRadius", rPx)
                shader.setFloatUniform("uBevelWidth", bevelWidthDp * density)
                shader.setFloatUniform("uDispersionStrength", dispersionStrength)
                shader.setFloatUniform("uSpecularIntensity", specularIntensity)
                shader.setFloatUniform("uTouchPos", if (touchX >= 0f) touchX else w / 2f, if (touchY >= 0f) touchY else h / 2f)
                shader.setFloatUniform("uPressProgress", pressProgress)
                shader.setFloatUniform("uTime", shimmerPhase)
                shader.setFloatUniform("uIsDark", if (isSystemDarkTheme()) 1.0f else 0.0f)
                shader.setFloatUniform("uClearVariant", if (materialVariant == GlassMaterialVariant.CLEAR) 1.0f else 0.0f)
                canvas.drawRect(0f, 0f, w, h, shaderPaint)
            } catch (_: Throwable) {
                drawFallbackGlass(canvas, rPx)
            }
        } else {
            drawFallbackGlass(canvas, rPx)
        }

        val saveCount = canvas.save()
        canvas.clipPath(clipPath)
        super.dispatchDraw(canvas)
        canvas.restoreToCount(saveCount)
    }

    private fun drawFallbackGlass(canvas: Canvas, rPx: Float) {
        canvas.drawRoundRect(boundsRect, rPx, rPx, fallbackFillPaint)
        val inset = fallbackRimPaint.strokeWidth * 0.5f
        val rimRect = RectF(inset, inset, width - inset, height - inset)
        canvas.drawRoundRect(rimRect, rPx, rPx, fallbackRimPaint)
    }

    override fun onInterceptTouchEvent(ev: MotionEvent): Boolean {
        if (enableGelPress) {
            handleGelTouch(ev)
        }
        return super.onInterceptTouchEvent(ev)
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        if (enableGelPress) {
            handleGelTouch(event)
        }
        return super.onTouchEvent(event)
    }

    private fun handleGelTouch(event: MotionEvent) {
        touchX = event.x
        touchY = event.y
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> animateGelPress(1.0f)
            MotionEvent.ACTION_MOVE -> invalidate()
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> animateGelPress(0.0f)
        }
    }

    private fun animateGelPress(target: Float) {
        pressSpring?.cancel()
        val holder = FloatValueHolder(pressProgress * 100f)
        pressSpring = SpringAnimation(holder, target * 100f).apply {
            spring = SpringForce(target * 100f).apply {
                dampingRatio = SpringForce.DAMPING_RATIO_MEDIUM_BOUNCY
                stiffness = SpringForce.STIFFNESS_MEDIUM
            }
            addUpdateListener { _, value, _ ->
                pressProgress = (value / 100f).coerceIn(0f, 1.25f)
                invalidate()
            }
            start()
        }
    }

    fun startAmbientRefraction() {
        if (ambientAnimator?.isRunning == true) return
        ambientAnimator = ValueAnimator.ofFloat(0f, 6.28318f).apply {
            duration = 6000L
            repeatCount = ValueAnimator.INFINITE
            interpolator = LinearInterpolator()
            addUpdateListener {
                shimmerPhase = it.animatedValue as Float
                invalidate()
            }
            start()
        }
    }

    fun stopAmbientRefraction() {
        ambientAnimator?.cancel()
        ambientAnimator = null
    }

    override fun onDetachedFromWindow() {
        stopAmbientRefraction()
        pressSpring?.cancel()
        super.onDetachedFromWindow()
    }
}

/**
 * LiquidGlassBottomNavBar — Floating Bottom Navigation Bar bergaya iOS 26 / Kyant0 Liquid Glass
 * Dilengkapi kapsul indikator kaca cair (Liquid Droplet) yang meluncur dengan fisika pegas
 * disertai chromatic edge dispersion saat berpindah tab.
 */
class LiquidGlassBottomNavBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : FrameLayout(context, attrs, defStyleAttr) {

    data class NavTab(val label: String, val iconRes: Int)

    private val dockContainer = LiquidGlassFrameLayout(context).apply {
        cornerRadiusDp = 32f
        bevelWidthDp = 15f
        dispersionStrength = 0.34f
        specularIntensity = 0.72f
        materialVariant = LiquidGlassFrameLayout.GlassMaterialVariant.REGULAR
    }

    private val dropletPill = LiquidGlassFrameLayout(context).apply {
        cornerRadiusDp = 24f
        bevelWidthDp = 11f
        dispersionStrength = 0.48f
        specularIntensity = 0.92f
        materialVariant = LiquidGlassFrameLayout.GlassMaterialVariant.CLEAR
        enableGelPress = false
    }

    private val itemsRow = LinearLayout(context).apply {
        orientation = LinearLayout.HORIZONTAL
        gravity = Gravity.CENTER_VERTICAL
    }

    private val tabViews = mutableListOf<Pair<ImageView, TextView>>()
    private var selectedIndex = 0
    private var dropletSpringX: SpringAnimation? = null
    private var dropletSpringScale: SpringAnimation? = null
    var onTabSelected: ((Int) -> Unit)? = null

    init {
        val d = resources.displayMetrics.density
        val pad = (6 * d).toInt()
        dockContainer.setPadding(pad, pad, pad, pad)

        val innerFrame = FrameLayout(context)
        innerFrame.addView(dropletPill, LayoutParams(0, LayoutParams.MATCH_PARENT))
        innerFrame.addView(itemsRow, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT))

        dockContainer.addView(innerFrame, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT))
        addView(dockContainer, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT))
    }

    fun setTabs(tabs: List<NavTab>) {
        itemsRow.removeAllViews()
        tabViews.clear()
        val d = resources.displayMetrics.density

        tabs.forEachIndexed { index, tab ->
            val tabBox = LinearLayout(context).apply {
                orientation = LinearLayout.VERTICAL
                gravity = Gravity.CENTER
                setPadding(0, (6 * d).toInt(), 0, (6 * d).toInt())
                setOnClickListener {
                    selectTab(index, animate = true, notify = true)
                }
            }

            val iconView = ImageView(context).apply {
                setImageResource(tab.iconRes)
                setColorFilter(if (index == 0) Color.parseColor("#38BDF8") else Color.parseColor("#94A3B8"))
            }

            val labelView = TextView(context).apply {
                text = tab.label
                textSize = 10.5f
                typeface = if (index == 0) Typeface.DEFAULT_BOLD else Typeface.DEFAULT
                setTextColor(if (index == 0) Color.parseColor("#F8FAFC") else Color.parseColor("#94A3B8"))
                gravity = Gravity.CENTER
                setPadding(0, (3 * d).toInt(), 0, 0)
            }

            tabBox.addView(iconView, LinearLayout.LayoutParams((20 * d).toInt(), (20 * d).toInt()))
            tabBox.addView(labelView, LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT))

            val lp = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.MATCH_PARENT, 1f)
            itemsRow.addView(tabBox, lp)
            tabViews.add(Pair(iconView, labelView))
        }

        post {
            updateDropletGeometry(selectedIndex, animate = false)
            dockContainer.startAmbientRefraction()
        }
    }

    fun selectTab(index: Int, animate: Boolean = true, notify: Boolean = false) {
        if (index !in tabViews.indices) return
        if (index != selectedIndex) {
            performHapticFeedback(HapticFeedbackConstants.CLOCK_TICK)
        }
        selectedIndex = index
        val isDark = (resources.configuration.uiMode and Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES

        tabViews.forEachIndexed { i, (icon, label) ->
            val active = (i == index)
            icon.setColorFilter(
                if (active) Color.parseColor("#38BDF8")
                else if (isDark) Color.parseColor("#94A3B8") else Color.parseColor("#475569")
            )
            label.setTextColor(
                if (active) Color.parseColor("#F8FAFC")
                else if (isDark) Color.parseColor("#94A3B8") else Color.parseColor("#475569")
            )
            label.typeface = if (active) Typeface.DEFAULT_BOLD else Typeface.DEFAULT
            icon.animate()
                .scaleX(if (active) 1.12f else 1.0f)
                .scaleY(if (active) 1.12f else 1.0f)
                .setDuration(180L)
                .start()
        }

        updateDropletGeometry(index, animate)
        if (notify) {
            onTabSelected?.invoke(index)
        }
    }

    private fun updateDropletGeometry(index: Int, animate: Boolean) {
        if (tabViews.isEmpty() || itemsRow.width <= 0) return
        val tabWidth = itemsRow.width.toFloat() / tabViews.size
        val targetX = index * tabWidth
        val lp = dropletPill.layoutParams
        if (lp.width != tabWidth.toInt()) {
            lp.width = tabWidth.toInt()
            dropletPill.layoutParams = lp
        }

        if (!animate) {
            dropletPill.translationX = targetX
            return
        }

        dropletSpringX?.cancel()
        val holderX = FloatValueHolder(dropletPill.translationX)
        dropletSpringX = SpringAnimation(holderX, targetX).apply {
            spring = SpringForce(targetX).apply {
                dampingRatio = SpringForce.DAMPING_RATIO_LOW_BOUNCY
                stiffness = SpringForce.STIFFNESS_LOW
            }
            addUpdateListener { _, value, _ ->
                dropletPill.translationX = value
            }
            start()
        }

        dropletSpringScale?.cancel()
        val holderS = FloatValueHolder(116f)
        dropletSpringScale = SpringAnimation(holderS, 100f).apply {
            spring = SpringForce(100f).apply {
                dampingRatio = SpringForce.DAMPING_RATIO_MEDIUM_BOUNCY
                stiffness = SpringForce.STIFFNESS_MEDIUM
            }
            addUpdateListener { _, value, _ ->
                val s = value / 100f
                dropletPill.scaleX = s
                dropletPill.scaleY = 2.0f - s
            }
            start()
        }
    }

    override fun onDetachedFromWindow() {
        dockContainer.stopAmbientRefraction()
        dropletSpringX?.cancel()
        dropletSpringScale?.cancel()
        super.onDetachedFromWindow()
    }
}
