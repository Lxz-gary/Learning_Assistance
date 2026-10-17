"""全局主题：配色与字体统一从这里取，支持暗 / 亮两套。"""

DARK = {
    # ---- 基础 ----
    "sidebar_bg":     "#1e1f23",
    "sidebar_active": "#334155",
    "content_bg":     "#0d0d0d",
    "card_bg":        "#ffffff",
    "border":         "#2c2c3a",
    # ---- 文字 ----
    "Level1fg":       "#cbd5e1",
    "Level2fg":       "#a1a1aa",
    "text_primary":   "#0f172a",
    "selected_fg":    "#ffffff",
    # ---- 强调色 ----
    "accent":         "#715533",
    "accent_hover":   "#8a6740",
    "on_accent_fg":   "#ffffff",
    "danger":         "#a8433a",
    "danger_hover":   "#bf5147",
    "ok_fg":          "#5fbf7f",
    "warn_fg":        "#e07a5f",
    # ---- 控件 ----
    "btn_bg":         "#1e1f23",
    "btn_hover":      "#2b303b",
    "btn_fg":         "#cbd5e1",
    "btn_border":     "#2c2c3a",
    "entry_bg":       "#1a1c20",
    "entry_border":   "#2c2c3a",
    # ---- 图表 ----
    "chart_grid":     "#2a2c33",
    "chart_bar":      "#8a6740",
    "chart_bar_alt":  "#5fbf7f",
}

LIGHT = {
    "sidebar_bg":     "#f1f3f6",
    "sidebar_active": "#dbe4f0",
    "content_bg":     "#ffffff",
    "card_bg":        "#ffffff",
    "border":         "#e3e6eb",
    "Level1fg":       "#1f2937",
    "Level2fg":       "#6b7280",
    "text_primary":   "#0f172a",
    "selected_fg":    "#ffffff",
    "accent":         "#8a6740",
    "accent_hover":   "#a17c52",
    "on_accent_fg":   "#ffffff",
    "danger":         "#c0392b",
    "danger_hover":   "#d1453a",
    "ok_fg":          "#2e8b57",
    "warn_fg":        "#c0653f",
    "btn_bg":         "#eef1f4",
    "btn_hover":      "#e0e5ea",
    "btn_fg":         "#374151",
    "btn_border":     "#d9dde3",
    "entry_bg":       "#ffffff",
    "entry_border":   "#d9dde3",
    "chart_grid":     "#e8ebef",
    "chart_bar":      "#8a6740",
    "chart_bar_alt":  "#2e8b57",
}

COLORS = dict(DARK)
FONT_FAMILY = "PingFang SC"

_state = {"mode": "dark"}


def font(size=12, weight="normal"):
    return (FONT_FAMILY, size, weight)


def mode():
    return _state["mode"]


def set_theme(new_mode):
    """切换主题：只改 COLORS 内容，重建界面时生效。"""
    _state["mode"] = "light" if new_mode == "light" else "dark"
    COLORS.clear()
    COLORS.update(LIGHT if _state["mode"] == "light" else DARK)
    # customtkinter 的下拉框等控件有自己的外观模式，一并同步
    try:
        import customtkinter as ctk
        ctk.set_appearance_mode("light" if _state["mode"] == "light" else "dark")
    except Exception:
        pass
    return _state["mode"]


def toggle_theme():
    return set_theme("light" if _state["mode"] == "dark" else "dark")
