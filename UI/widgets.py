"""通用控件工厂：按钮 / 输入框 / 确认弹窗 / 表格卡片。

严格说 macOS 上 tk.Button 的 bg 会被系统忽略（永远画成原生灰按钮），
所以这里的按钮统一用 tk.Label + <Button-1> 实现，颜色才能真正生效。
"""

import tkinter as tk
import tkinter.ttk as ttk

from .theme import COLORS, font

_theme_ready = False

# kind -> (底色, 悬停色, 文字色, 描边色)
BUTTON_KINDS = {
    "primary":   ("accent", "accent_hover", "on_accent_fg", None),
    "secondary": ("btn_bg", "btn_hover", "btn_fg", "btn_border"),
    "danger":    ("danger", "danger_hover", None, None),
    "ghost":     ("content_bg", "btn_hover", "Level2fg", "btn_border"),
}


def make_btn(parent, text, cmd, kind="secondary", size=12, padx=20, pady=9, fg=None):
    """创建一个带悬停效果的文字按钮（返回 tk.Label，调用方自行 pack/grid）。"""
    bg_key, hover_key, fg_key, border_key = BUTTON_KINDS[kind]
    bg = COLORS[bg_key]
    hover_bg = COLORS[hover_key]
    fg = fg or ("#ffffff" if fg_key is None else COLORS[fg_key])
    border = COLORS[border_key] if border_key else None

    btn = tk.Label(
        parent, text=text, bg=bg, fg=fg, font=font(size),
        padx=padx, pady=pady, cursor="hand2", bd=0,
        highlightthickness=1 if border else 0,
        highlightbackground=border or bg,
        highlightcolor=border or bg,
    )
    btn.bind("<Button-1>", lambda e: cmd())
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
    return btn


def build_card(parent, bg_key="content_bg"):
    """带 1px 边框的卡片容器，背景与内容区一致。"""
    return tk.Frame(
        parent, bg=COLORS[bg_key],
        highlightbackground=COLORS["border"], highlightthickness=1, bd=0,
    )


def make_entry(parent, **kwargs):
    """统一风格的输入框：深底 + 细边框，聚焦时边框变强调色。"""
    entry = tk.Entry(
        parent,
        bg=COLORS["entry_bg"],
        fg=COLORS["Level1fg"],
        insertbackground=COLORS["Level1fg"],
        relief="flat",
        highlightthickness=1,
        highlightbackground=COLORS["entry_border"],
        highlightcolor=COLORS["accent"],
        font=font(12),
        **kwargs,
    )
    return entry


def mark_entry(entry, error=False):
    """校验失败时给输入框套红框，恢复时还原。"""
    if entry is None:
        return
    entry.configure(
        highlightbackground=COLORS["danger"] if error else COLORS["entry_border"],
        highlightcolor=COLORS["danger"] if error else COLORS["accent"],
    )


def apply_table_style(config):
    """表格、表头、滚动条的 ttk 样式（全局样式，配置一次即可复用）。"""
    global _theme_ready

    style = ttk.Style()
    # theme_use 是全局操作，会把所有 ttk 控件样式重建一遍，只设置一次
    if not _theme_ready:
        style.theme_use("clam")
        _theme_ready = True

    style.configure(
        "DS.Treeview",
        background=COLORS[config["row_bg"]],
        foreground=COLORS["Level1fg"],
        fieldbackground=COLORS[config["row_bg"]],
        rowheight=40,
        borderwidth=0,
        relief="flat",
        font=font(12),
    )
    style.configure(
        "DS.Treeview.Heading",
        background=COLORS[config["heading_bg"]],
        foreground=COLORS[config["heading_fg"]],
        font=font(11),
        borderwidth=0,
        relief="flat",
        padding=(12, 12),
    )
    style.map(
        "DS.Treeview.Heading",
        background=[("active", COLORS[config["heading_act_bg"]])],
        foreground=[("active", COLORS[config["heading_act_fg"]])],
    )
    style.map(
        "DS.Treeview",
        background=[("selected", COLORS[config["selected_bg"]])],
        foreground=[("selected", COLORS["selected_fg"])],
    )
    style.layout("DS.Treeview", [("DS.Treeview.treearea", {"sticky": "nswe"})])
    style.configure(
        "DS.Vertical.TScrollbar",
        background=COLORS["border"],
        troughcolor=COLORS["content_bg"],
        bordercolor=COLORS["content_bg"],
        arrowcolor=COLORS["Level2fg"],
        borderwidth=0,
        relief="flat",
        width=8,
    )
    style.map(
        "DS.Vertical.TScrollbar",
        background=[("active", COLORS["Level2fg"])],
    )


def build_table_card(parent, config, height=10, h_scroll=None):
    """按模版创建「卡片 + 表格 + 滚动条」，返回 (卡片, 表格)。"""
    if h_scroll is None:
        h_scroll = config.get("h_scroll", False)

    apply_table_style(config)

    card = tk.Frame(
        parent, bg=COLORS[config["card_bg"]],
        highlightbackground=COLORS["border"],
        highlightthickness=1, bd=0,
    )
    table_frame = tk.Frame(card, bg=COLORS[config["card_bg"]])
    table_frame.pack(fill="both", expand=True, padx=1, pady=1)
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    tree = ttk.Treeview(
        table_frame, columns=config["columns"], show="headings",
        style="DS.Treeview", height=height,
    )
    for col, (text, w) in config["headers"].items():
        tree.heading(col, text=text, anchor="w")
        tree.column(col, anchor="w", width=w, minwidth=60, stretch=True)

    # 斑马纹：直接用配置里的两种行底色，不再写死
    tree.tag_configure("oddrow", background=COLORS[config["row_bg"]])
    tree.tag_configure("evenrow", background=COLORS[config["row_alt"]])
    tree.tag_configure("empty", foreground=COLORS["Level2fg"])

    v_sb = ttk.Scrollbar(
        table_frame, orient="vertical",
        command=tree.yview, style="DS.Vertical.TScrollbar",
    )
    tree.configure(yscrollcommand=v_sb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    v_sb.grid(row=0, column=1, sticky="ns")

    if h_scroll:
        h_sb = ttk.Scrollbar(
            table_frame, orient="horizontal",
            command=tree.xview, style="DS.Vertical.TScrollbar",
        )
        tree.configure(xscrollcommand=h_sb.set)
        h_sb.grid(row=1, column=0, sticky="ew")

    return card, tree


def ask_dialog(root, title, message, ok_text="确定", cancel_text="取消", danger=False):
    """深色主题模态弹窗：confirm 模式带取消，notice 模式传 cancel_text=None。"""
    dlg = tk.Toplevel(root)
    dlg.title(title)
    dlg.configure(bg=COLORS["content_bg"])
    dlg.transient(root)
    dlg.resizable(False, False)

    body = tk.Frame(dlg, bg=COLORS["content_bg"])
    body.pack(fill="both", expand=True, padx=24, pady=(20, 18))

    tk.Label(
        body, text=title, bg=COLORS["content_bg"], fg=COLORS["Level1fg"],
        font=font(15, "bold"),
    ).pack(anchor="w")
    tk.Label(
        body, text=message, bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
        font=font(12), justify="left", wraplength=380,
    ).pack(anchor="w", pady=(10, 18))

    answer = {"ok": False}

    def on_ok():
        answer["ok"] = True
        dlg.destroy()

    buttons = tk.Frame(body, bg=COLORS["content_bg"])
    buttons.pack(fill="x")

    make_btn(
        buttons, ok_text, on_ok,
        kind="danger" if danger else "primary",
        padx=24,
    ).pack(side="right")

    if cancel_text:
        make_btn(buttons, cancel_text, dlg.destroy, kind="secondary", padx=22, pady=8).pack(
            side="right", padx=(0, 10))

    dlg.bind("<Escape>", lambda e: dlg.destroy())
    dlg.bind("<Return>", lambda e: on_ok())

    dlg.update_idletasks()
    x = root.winfo_rootx() + (root.winfo_width() - dlg.winfo_width()) // 2
    y = root.winfo_rooty() + (root.winfo_height() - dlg.winfo_height()) // 3
    dlg.geometry(f"+{max(0, x)}+{max(0, y)}")

    dlg.grab_set()
    dlg.wait_window()
    return answer["ok"]
