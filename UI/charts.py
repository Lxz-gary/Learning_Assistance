"""轻量图表组件：KPI 卡 / 竖向柱状图 / 横向条形 / 迷你趋势图。

没有引入 matplotlib，全部用 Canvas 画，跟主题色保持一致。
"""

import tkinter as tk

from .theme import COLORS, font


def kpi_card(parent, title, value, hint="", accent=False):
    """KPI 小卡：大数字 + 标题 + 可选说明。"""
    card = tk.Frame(
        parent, bg=COLORS["sidebar_bg"],
        highlightbackground=COLORS["border"], highlightthickness=1, bd=0,
    )
    inner = tk.Frame(card, bg=COLORS["sidebar_bg"])
    inner.pack(fill="both", expand=True, padx=14, pady=12)

    tk.Label(
        inner, text=title, bg=COLORS["sidebar_bg"], fg=COLORS["Level2fg"],
        font=font(10), anchor="w",
    ).pack(fill="x")
    tk.Label(
        inner, text=value, bg=COLORS["sidebar_bg"],
        fg=COLORS["accent"] if accent else COLORS["Level1fg"],
        font=font(22, "bold"), anchor="w",
    ).pack(fill="x", pady=(2, 0))
    if hint:
        tk.Label(
            inner, text=hint, bg=COLORS["sidebar_bg"], fg=COLORS["Level2fg"],
            font=font(9), anchor="w",
        ).pack(fill="x")
    return card


def vbar_chart(parent, items, height=170, unit="", bar_color=None, alt_color=None):
    """竖向柱状图。items = [(标签, 数值), ...]，随控件宽度自动重绘。"""
    bar_color = bar_color or COLORS["chart_bar"]
    alt_color = alt_color or COLORS["chart_bar_alt"]

    canvas = tk.Canvas(
        parent, height=height, bg=COLORS["content_bg"],
        highlightthickness=0, bd=0,
    )
    state = {"items": list(items)}

    def redraw(event=None):
        canvas.delete("all")
        w = canvas.winfo_width() or 600
        h = canvas.winfo_height() or height
        data = state["items"]
        if not data:
            canvas.create_text(w / 2, h / 2, text="暂无数据",
                               fill=COLORS["Level2fg"], font=font(11))
            return

        pad_l, pad_r, pad_t, pad_b = 34, 16, 18, 34
        plot_w = max(40, w - pad_l - pad_r)
        plot_h = max(40, h - pad_t - pad_b)
        vmax = max(v for _, v in data) or 1
        vmax = vmax * 1.15

        # 网格线 + y 轴刻度
        for i in range(4):
            y = pad_t + plot_h * i / 3
            canvas.create_line(pad_l, y, w - pad_r, y,
                               fill=COLORS["chart_grid"], dash=(2, 4))
            canvas.create_text(pad_l - 6, y, text=f"{vmax * (3 - i) / 3:.0f}",
                               fill=COLORS["Level2fg"], font=font(8), anchor="e")

        slot = plot_w / len(data)
        bar_w = min(46, slot * 0.55)
        for i, (label, value) in enumerate(data):
            cx = pad_l + slot * (i + 0.5)
            bh = plot_h * (value / vmax)
            x0, y0 = cx - bar_w / 2, pad_t + plot_h - bh
            color = alt_color if i == max(range(len(data)), key=lambda k: data[k][1]) else bar_color
            canvas.create_rectangle(x0, y0, x0 + bar_w, pad_t + plot_h,
                                    fill=color, outline="")
            canvas.create_text(cx, y0 - 8, text=f"{value:.1f}{unit}",
                               fill=COLORS["Level1fg"], font=font(9))
            canvas.create_text(cx, h - 16, text=label,
                               fill=COLORS["Level2fg"], font=font(9))

    canvas.bind("<Configure>", redraw)
    canvas.after(40, redraw)
    return canvas


def hbar_chart(parent, items, unit="", height_per_row=30, max_value=None):
    """横向条形图。items = [(标签, 数值, 右侧说明), ...]；max_value 用于固定刻度。"""
    data = list(items)
    vmax = max_value or max((v for _, v, _ in data), default=1) or 1
    holder = tk.Frame(parent, bg=COLORS["content_bg"])

    for label, value, extra in data:
        row = tk.Frame(holder, bg=COLORS["content_bg"])
        row.pack(fill="x", pady=3)

        tk.Label(
            row, text=label, bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
            font=font(10), width=8, anchor="w",
        ).pack(side="left")

        track = tk.Frame(row, bg=COLORS["chart_grid"], height=14)
        track.pack(side="left", fill="x", expand=True, padx=(4, 8))
        track.pack_propagate(False)
        ratio = max(0.02, value / vmax)
        fill = tk.Frame(track, bg=COLORS["chart_bar"])
        fill.place(relx=0, rely=0, relwidth=ratio, relheight=1)

        tk.Label(
            row, text=f"{value:.1f}{unit}" + (f"   {extra}" if extra else ""),
            bg=COLORS["content_bg"], fg=COLORS["Level1fg"], font=font(10),
            width=18, anchor="w",
        ).pack(side="left")

    return holder


def sparkline(parent, values, width=200, height=44, color=None):
    """迷你趋势柱图（侧边栏用）。values = [数值, ...]"""
    canvas = tk.Canvas(
        parent, width=width, height=height, bg=COLORS["sidebar_bg"],
        highlightthickness=0, bd=0,
    )
    color = color or COLORS["chart_bar"]

    def redraw():
        canvas.delete("all")
        data = list(values)
        if not data:
            return
        w = width
        h = height
        vmin, vmax = min(data), max(data)
        span = (vmax - vmin) or 1
        slot = w / len(data)
        bar_w = min(22, slot * 0.55)
        for i, v in enumerate(data):
            ratio = (v - vmin) / span
            bh = 8 + ratio * (h - 22)
            cx = slot * (i + 0.5)
            x0 = cx - bar_w / 2
            canvas.create_rectangle(x0, h - 12 - bh, x0 + bar_w, h - 12,
                                    fill=color, outline="")
            canvas.create_text(cx, h - 2, text=f"{v:.0f}",
                               fill=COLORS["Level2fg"], font=font(7), anchor="s")

    canvas.after(40, redraw)
    return canvas
