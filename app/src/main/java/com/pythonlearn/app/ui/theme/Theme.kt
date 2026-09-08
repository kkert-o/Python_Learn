package com.pythonlearn.app.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.sp

enum class ThemePreference(val label: String) {
    SYSTEM("跟随系统"),
    LIGHT("浅色"),
    DARK("深色"),
}

data class AccentOption(
    val name: String,
    val value: Long,
) {
    val color: Color
        get() = Color(value)
}

data class WallpaperOption(
    val id: String,
    val name: String,
    val lightColors: List<Color>,
    val darkColors: List<Color>,
    val isCustom: Boolean = false,
)

val customWallpaperOption = WallpaperOption(
    id = "custom",
    name = "自定义",
    lightColors = listOf(Color(0xFF20262A), Color(0xFF30383D)),
    darkColors = listOf(Color(0xFF10151A), Color(0xFF1D252B)),
    isCustom = true,
)

data class LegalRegion(
    val id: String,
    val label: String,
)

val legalRegionOptions = listOf(
    LegalRegion("CN", "中国大陆"),
    LegalRegion("JP", "日本"),
    LegalRegion("US", "美国"),
    LegalRegion("EU", "欧盟"),
    LegalRegion("OTHER", "其他"),
)

val accentOptions = listOf(
    AccentOption("蓝", 0xFF1677FF),
    AccentOption("青", 0xFF0F9D8F),
    AccentOption("橙", 0xFFD05F3A),
    AccentOption("紫", 0xFF7B61D8),
    AccentOption("绿", 0xFF1F9D6B),
)

val wallpaperOptions = listOf(
    WallpaperOption(
        id = "mist",
        name = "雾蓝",
        lightColors = listOf(Color(0xFFEDF2F1), Color(0xFFDDE8EB), Color(0xFFE6EEE7)),
        darkColors = listOf(Color(0xFF1B252A), Color(0xFF273237), Color(0xFF202A2C)),
    ),
    WallpaperOption(
        id = "mint",
        name = "薄荷",
        lightColors = listOf(Color(0xFFE7F1E9), Color(0xFFD8E8E5), Color(0xFFE4EEE2)),
        darkColors = listOf(Color(0xFF182521), Color(0xFF1E302B), Color(0xFF22332C)),
    ),
    WallpaperOption(
        id = "clay",
        name = "暖砂",
        lightColors = listOf(Color(0xFFF1ECE4), Color(0xFFE7DFD3), Color(0xFFE2E8E6)),
        darkColors = listOf(Color(0xFF29231B), Color(0xFF322A20), Color(0xFF242C2B)),
    ),
    WallpaperOption(
        id = "night",
        name = "夜幕",
        lightColors = listOf(Color(0xFFDCE8EC), Color(0xFFD3E0E4), Color(0xFFCBD7E3)),
        darkColors = listOf(Color(0xFF10161D), Color(0xFF182029), Color(0xFF171F26)),
    ),
    WallpaperOption(
        id = "graphite",
        name = "石墨",
        lightColors = listOf(Color(0xFFE4E8EA), Color(0xFFD7DDE0), Color(0xFFCCD3D7)),
        darkColors = listOf(Color(0xFF171C20), Color(0xFF20262A), Color(0xFF252B2D)),
    ),
)

private val lightColors = lightColorScheme(
    primary = Color(0xFF1677FF),
    onPrimary = Color.White,
    secondary = Color(0xFF1C9D6B),
    surface = Color(0xFFFCFCFD),
    surfaceContainer = Color(0xFFF5F6F7),
    onSurface = Color(0xFF171A1D),
    surfaceVariant = Color(0xFFF0F1F3),
    onSurfaceVariant = Color(0xFF6E747A),
    outline = Color(0xFFE0E2E5),
    background = Color(0xFFF4F5F6),
)

private val darkColors = darkColorScheme(
    primary = Color(0xFF4D9AFF),
    onPrimary = Color.White,
    secondary = Color(0xFF2EB987),
    surface = Color(0xFF171C20),
    surfaceContainer = Color(0xFF1E252A),
    onSurface = Color(0xFFE8EDF1),
    surfaceVariant = Color(0xFF232A2F),
    onSurfaceVariant = Color(0xFF9BA4AB),
    outline = Color(0xFF363F45),
    background = Color(0xFF10151A),
)

private val appTypography = Typography(
    displaySmall = TextStyle(fontSize = 32.sp, lineHeight = 38.sp, fontWeight = FontWeight.Bold, letterSpacing = 0.sp),
    headlineLarge = TextStyle(fontSize = 27.sp, lineHeight = 33.sp, fontWeight = FontWeight.Bold, letterSpacing = 0.sp),
    headlineMedium = TextStyle(fontSize = 23.sp, lineHeight = 29.sp, fontWeight = FontWeight.Bold, letterSpacing = 0.sp),
    headlineSmall = TextStyle(fontSize = 21.sp, lineHeight = 27.sp, fontWeight = FontWeight.SemiBold, letterSpacing = 0.sp),
    titleLarge = TextStyle(fontSize = 18.sp, lineHeight = 24.sp, fontWeight = FontWeight.SemiBold, letterSpacing = 0.sp),
    titleMedium = TextStyle(fontSize = 16.sp, lineHeight = 22.sp, fontWeight = FontWeight.SemiBold, letterSpacing = 0.sp),
    titleSmall = TextStyle(fontSize = 14.sp, lineHeight = 20.sp, fontWeight = FontWeight.SemiBold, letterSpacing = 0.sp),
    bodyLarge = TextStyle(fontSize = 15.sp, lineHeight = 22.sp, letterSpacing = 0.sp),
    bodyMedium = TextStyle(fontSize = 14.sp, lineHeight = 21.sp, letterSpacing = 0.sp),
    bodySmall = TextStyle(fontSize = 12.sp, lineHeight = 18.sp, letterSpacing = 0.sp),
    labelLarge = TextStyle(fontSize = 14.sp, lineHeight = 20.sp, fontWeight = FontWeight.SemiBold, letterSpacing = 0.sp),
    labelMedium = TextStyle(fontSize = 12.sp, lineHeight = 16.sp, fontWeight = FontWeight.Medium, letterSpacing = 0.sp),
    labelSmall = TextStyle(fontSize = 10.sp, lineHeight = 14.sp, fontWeight = FontWeight.Medium, letterSpacing = 0.sp),
)

@Composable
fun PythonLearningTheme(
    preference: ThemePreference,
    accent: AccentOption,
    content: @Composable () -> Unit,
) {
    val darkTheme = when (preference) {
        ThemePreference.SYSTEM -> isSystemInDarkTheme()
        ThemePreference.LIGHT -> false
        ThemePreference.DARK -> true
    }
    val baseScheme = if (darkTheme) darkColors else lightColors
    val colors = baseScheme.copy(
        primary = accent.color,
        secondary = if (darkTheme) Color(0xFF5BD3A6) else Color(0xFF1C9D6B),
        primaryContainer = if (darkTheme) accent.color.copy(alpha = 0.22f) else accent.color.copy(alpha = 0.14f),
    )
    MaterialTheme(
        colorScheme = colors,
        typography = appTypography,
        content = content,
    )
}
