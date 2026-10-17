"""主窗口：侧边栏（导航 + 全局搜索 + 数据卡 + 状态）+ 右侧内容区。"""

import os
import tkinter as tk

from . import theme
from .theme import COLORS, font
from .charts import sparkline
from .widgets import build_card
from .OperateWindow import OperateWindow
from .AnalysisWindow import AnalysisWindow
from .ToolWindow import ToolWindow
from Controller.DataBaseController import DataBaseController

db_controller = DataBaseController()

DB_FILE = "my_database.db"

SIDEBAR_WIDTH = 236
SIDEBAR_COLLAPSED = 68

# (分组标题, [(图标, 文字, key)])
NAV_SECTIONS = [
    ("数据", [
        ("▤", "数据管理", "data"),
    ]),
    ("分析", [
        ("▦", "成绩概览", "overview"),
        ("▥", "科目对比", "subject"),
        ("≡", "班级排名", "class"),
    ]),
    ("工具", [
        ("↧", "导入 Excel", "import"),
        ("↥", "导出数据", "export"),
        ("⧉", "备份数据库", "backup"),
    ]),
]

CHIPS = ["学生", "考试", "成绩"]


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("成绩分析系统")
        self.root.geometry("1220x820")
        self.root.minsize(1000, 700)
        self.root.configure(bg=COLORS["content_bg"])

        self.current_page_key = "data"
        self._collapsed = False
        self._sidebar_width = SIDEBAR_WIDTH
        self._nav_items = {}
        self._active_key = None
        self._recent = []
        self._filter_text = ""

        self._build_ui()

    # ==================================================================
    # 整体布局
    # ==================================================================
    def _build_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=0)
        self.root.grid_columnconfigure(2, weight=1)

        # ---- 侧边栏 ----
        self.sidebar = tk.Frame(
            self.root, bg=COLORS["sidebar_bg"],
            width=SIDEBAR_COLLAPSED if self._collapsed else self._sidebar_width,
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        self.sidebar.pack_propagate(False)

        # ---- 拖拽调宽手柄 ----
        self.resizer = tk.Frame(self.root, bg=COLORS["border"], width=4,
                                cursor="sb_h_double_arrow")
        self.resizer.grid(row=0, column=1, sticky="ns")
        self.resizer.bind("<Button-1>", self._start_resize)
        self.resizer.bind("<B1-Motion>", self._on_resize)

        # ---- 内容区 ----
        self.content = tk.Frame(self.root, bg=COLORS["content_bg"])
        self.content.grid(row=0, column=2, sticky="nsew")

        # ---- 页面对象 ----
        self.operate_window = OperateWindow(self.root, self.content)
        self.operate_window.set_callbacks(
            on_activity=self._on_activity,
            on_filter=self._on_filter,
        )
        self.analysis_window = AnalysisWindow(self.root, self.content)
        self.tool_window = ToolWindow(self.root, self.content)

        self._build_sidebar()
        self._open_page(self.current_page_key)

    # ==================================================================
    # 侧边栏
    # ==================================================================
    def _build_sidebar(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        self._nav_items = {}

        # ---------- 品牌 + 折叠按钮 ----------
        head = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        head.pack(fill="x", padx=14, pady=(16, 6))

        brand = tk.Frame(head, bg=COLORS["sidebar_bg"])
        brand.pack(side="left", fill="x", expand=True)
        if self._collapsed:
            tk.Label(brand, text="成", bg=COLORS["sidebar_bg"], fg=COLORS["Level1fg"],
                     font=font(18, "bold")).pack(anchor="w")
        else:
            tk.Label(brand, text="成绩分析系统", bg=COLORS["sidebar_bg"], fg=COLORS["Level1fg"],
                     font=font(17, "bold"), anchor="w").pack(fill="x")
            tk.Label(brand, text="GRADE ANALYSIS", bg=COLORS["sidebar_bg"], fg=COLORS["Level2fg"],
                     font=font(8), anchor="w").pack(fill="x")

        fold = tk.Label(
            head, text="»" if self._collapsed else "«",
            bg=COLORS["sidebar_bg"], fg=COLORS["Level2fg"],
            font=font(13), padx=6, pady=4, cursor="hand2",
        )
        fold.pack(side="right")
        fold.bind("<Button-1>", lambda e: self._toggle_collapse())

        # ---------- 全局搜索 ----------
        search = tk.Frame(
            self.sidebar, bg=COLORS["entry_bg"],
            highlightbackground=COLORS["border"], highlightthickness=1,
        )
        search.pack(fill="x", padx=14, pady=(6, 2))
        if self._collapsed:
            icon = tk.Label(search, text="⌕", bg=COLORS["entry_bg"], fg=COLORS["Level2fg"],
                            font=font(14), pady=6, cursor="hand2")
            icon.pack(fill="x")
            search.bind("<Button-1>", lambda e: self._open_search())
            icon.bind("<Button-1>", lambda e: self._open_search())
        else:
            tk.Label(search, text="⌕", bg=COLORS["entry_bg"], fg=COLORS["Level2fg"],
                     font=font(12)).pack(side="left", padx=(8, 4))
            tk.Label(search, text="搜索学号 / 姓名", bg=COLORS["entry_bg"],
                     fg=COLORS["Level2fg"], font=font(9)).pack(side="left", pady=6, fill="x", expand=True)
            tk.Label(search, text="⌘K", bg=COLORS["entry_bg"], fg=COLORS["Level2fg"],
                     font=font(8)).pack(side="right", padx=6)
            for w in (search,) + tuple(search.winfo_children()):
                w.bind("<Button-1>", lambda e: self._open_search())

        # ---------- 底部面板（先 pack，保证窄窗口下不被挤掉）----------
        self._build_sidebar_bottom()

        # ---------- 导航 ----------
        nav_area = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        nav_area.pack(fill="both", expand=True, pady=(8, 0))

        for section_title, items in NAV_SECTIONS:
            if not self._collapsed:
                tk.Label(
                    nav_area, text=section_title, bg=COLORS["sidebar_bg"],
                    fg=COLORS["Level2fg"], font=font(9), anchor="w",
                ).pack(fill="x", padx=20, pady=(10, 2))

            for icon, text, key in items:
                self._add_nav_item(nav_area, icon, text, key)

            if section_title == "数据" and not self._collapsed:
                chips = tk.Frame(nav_area, bg=COLORS["sidebar_bg"])
                chips.pack(fill="x", padx=(30, 14), pady=(2, 6))
                for target in CHIPS:
                    chip = tk.Label(
                        chips, text=target, bg=COLORS["btn_bg"], fg=COLORS["Level2fg"],
                        font=font(9), padx=9, pady=2, cursor="hand2",
                    )
                    chip.pack(side="left", padx=(0, 5))
                    chip.bind("<Button-1>", lambda e, t=target: self._goto_type(t))
                    chip.bind("<Enter>", lambda e, w=chip: w.configure(bg=COLORS["btn_hover"]))
                    chip.bind("<Leave>", lambda e, w=chip: w.configure(bg=COLORS["btn_bg"]))

        # 快捷键
        self._bind_shortcuts()

    def _build_sidebar_bottom(self):
        bottom = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        bottom.pack(side="bottom", fill="x")

        # ---- 筛选徽标 ----
        self._filter_holder = tk.Frame(bottom, bg=COLORS["sidebar_bg"])
        if not self._collapsed:
            self._filter_holder.pack(fill="x", padx=14, pady=(0, 6))

        # ---- 最近操作 ----
        self._recent_block = tk.Frame(bottom, bg=COLORS["sidebar_bg"])
        if not self._collapsed:
            self._recent_block.pack(fill="x")

        # ---- 数据卡 ----
        self._stats_labels = {}
        if not self._collapsed:
            card = build_card(bottom, "content_bg")
            card.pack(fill="x", padx=14, pady=(2, 6))
            inner = tk.Frame(card, bg=COLORS["content_bg"])
            inner.pack(fill="x", padx=10, pady=8)

            tk.Label(inner, text="数据概览", bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
                     font=font(9), anchor="w").pack(fill="x")

            grid = tk.Frame(inner, bg=COLORS["content_bg"])
            grid.pack(fill="x", pady=(2, 2))
            for i, (key, label) in enumerate((("students", "学生"), ("exams", "考试"), ("scores", "成绩"))):
                value = tk.Label(grid, text="—", bg=COLORS["content_bg"], fg=COLORS["Level1fg"],
                                 font=font(13, "bold"))
                value.grid(row=0, column=i, sticky="w", padx=(0, 10))
                tk.Label(grid, text=label, bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
                         font=font(8)).grid(row=1, column=i, sticky="w", padx=(0, 10))
                self._stats_labels[key] = value
                grid.grid_columnconfigure(i, weight=1)

            self._stats_hint = tk.Label(inner, text="", bg=COLORS["content_bg"],
                                        fg=COLORS["ok_fg"], font=font(9), anchor="w")
            self._stats_hint.pack(fill="x", pady=(4, 0))

            tk.Label(inner, text="近 5 场考试平均分", bg=COLORS["content_bg"],
                     fg=COLORS["Level2fg"], font=font(8), anchor="w").pack(fill="x", pady=(6, 0))

        # ---- 迷你趋势图 ----
        self._spark_holder = tk.Frame(bottom, bg=COLORS["sidebar_bg"])
        if not self._collapsed:
            self._spark_holder.pack(fill="x", padx=14, pady=(4, 6))

        # ---- 状态条 ----
        tk.Frame(bottom, bg=COLORS["border"], height=1).pack(fill="x", padx=14, pady=(2, 0))
        foot = tk.Frame(bottom, bg=COLORS["sidebar_bg"])
        foot.pack(fill="x", padx=(6 if self._collapsed else 16), pady=(6, 10))

        self._status_label = tk.Label(
            foot, text="● 数据库已连接", bg=COLORS["sidebar_bg"],
            fg=COLORS["ok_fg"], font=font(8), anchor="w",
        )
        self._status_label.pack(fill="x")

        line = tk.Frame(foot, bg=COLORS["sidebar_bg"])
        line.pack(fill="x", pady=(2, 0))

        if not self._collapsed:
            tk.Label(
                line, text="v1.0", bg=COLORS["sidebar_bg"], fg=COLORS["Level2fg"],
                font=font(8), anchor="w",
            ).pack(side="left")

        theme_btn = tk.Label(
            line, text="☀" if theme.mode() == "dark" else "☾",
            bg=COLORS["sidebar_bg"], fg=COLORS["Level2fg"],
            font=font(10), padx=4, cursor="hand2",
        )
        theme_btn.pack(side="right")
        theme_btn.bind("<Button-1>", lambda e: self._toggle_theme())

        self._refresh_stats()
        self._refresh_recent()
        self._refresh_filter_chip()

    def _add_nav_item(self, parent, icon, text, key):
        row = tk.Frame(parent, bg=COLORS["sidebar_bg"])
        row.pack(fill="x", pady=1)

        bar = tk.Frame(row, bg=COLORS["sidebar_bg"], width=3)
        bar.pack(side="left", fill="y")

        icon_lbl = tk.Label(
            row, text=icon, bg=COLORS["sidebar_bg"], fg=COLORS["Level2fg"],
            font=font(12), width=2, padx=8, pady=7,
        )
        if self._collapsed:
            icon_lbl.pack(side="left", fill="x", expand=True)
        else:
            icon_lbl.pack(side="left")

        label = None
        if not self._collapsed:
            label = tk.Label(
                row, text=text, bg=COLORS["sidebar_bg"], fg=COLORS["Level2fg"],
                font=font(12), anchor="w", pady=7,
            )
            label.pack(side="left", fill="x", expand=True)

        item = {"row": row, "bar": bar, "icon": icon_lbl, "label": label,
                "key": key, "text": text}
        self._nav_items[key] = item

        widgets = [row, bar, icon_lbl] + ([label] if label else [])
        for widget in widgets:
            widget.configure(cursor="hand2")
            widget.bind("<Button-1>", lambda e, k=key: self._on_nav_click(k))
            widget.bind("<Enter>", lambda e, it=item: self._hover_nav(it, True))
            widget.bind("<Leave>", lambda e, it=item: self._hover_nav(it, False))
        return item

    def _hover_nav(self, item, entering):
        if item["key"] == self._active_key:
            return
        bg = COLORS["btn_hover"] if entering else COLORS["sidebar_bg"]
        widgets = [item["row"], item["icon"]]
        if item["label"] is not None:
            widgets.append(item["label"])
        for w in widgets:
            w.configure(bg=bg)

    def _mark_active(self):
        for key, item in self._nav_items.items():
            active = key == self._active_key
            bg = COLORS["sidebar_active"] if active else COLORS["sidebar_bg"]
            widgets = [item["row"], item["icon"]]
            if item["label"] is not None:
                widgets.append(item["label"])
            for w in widgets:
                w.configure(bg=bg)
            item["icon"].configure(fg=COLORS["Level1fg"] if active else COLORS["Level2fg"])
            if item["label"] is not None:
                item["label"].configure(
                    fg=COLORS["Level1fg"] if active else COLORS["Level2fg"],
                    font=font(12, "bold") if active else font(12),
                )
            item["bar"].configure(bg=COLORS["accent"] if active else COLORS["sidebar_bg"])

    # ==================================================================
    # 导航 / 路由
    # ==================================================================
    def _on_nav_click(self, key):
        if key == "backup":
            self.tool_window.backup_database()
            return
        self._open_page(key)

    def _open_page(self, key):
        self.current_page_key = key
        self._active_key = key
        self._mark_active()

        if key == "data":
            self.operate_window.build_operate_page()
        elif key in ("overview", "subject", "class"):
            self.analysis_window.show(key)
        elif key == "import":
            self.tool_window.show_import()
        elif key == "export":
            self.tool_window.show_export()

    def _goto_type(self, target):
        self._open_page("data")
        self.operate_window.apply_state((target, {}))

    # ==================================================================
    # 全局搜索
    # ==================================================================
    def _open_search(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("搜索")
        dlg.configure(bg=COLORS["content_bg"])
        dlg.transient(self.root)
        dlg.geometry("520x420")
        dlg.minsize(420, 320)

        head = tk.Frame(dlg, bg=COLORS["content_bg"])
        head.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(head, text="搜索", bg=COLORS["content_bg"], fg=COLORS["Level1fg"],
                 font=font(16, "bold")).pack(side="left")
        tk.Label(head, text="学号 / 姓名 / 考试编号 / 科目", bg=COLORS["content_bg"],
                 fg=COLORS["Level2fg"], font=font(10)).pack(side="right", pady=(6, 0))

        box = tk.Frame(dlg, bg=COLORS["entry_bg"],
                       highlightbackground=COLORS["border"], highlightthickness=1)
        box.pack(fill="x", padx=16)
        entry = tk.Entry(box, bg=COLORS["entry_bg"], fg=COLORS["Level1fg"],
                         insertbackground=COLORS["Level1fg"], relief="flat",
                         font=font(13))
        entry.pack(fill="x", padx=10, pady=8)
        entry.focus_set()

        result_holder = tk.Frame(dlg, bg=COLORS["content_bg"])
        result_holder.pack(fill="both", expand=True, padx=16, pady=(10, 14))

        state = {"items": [], "widgets": []}

        def clear_results():
            for w in result_holder.winfo_children():
                w.destroy()
            state["widgets"] = []

        def choose(index):
            if 0 <= index < len(state["items"]):
                item = state["items"][index]
                dlg.destroy()
                self._goto_record(item["kind"], item["keys"])

        def render():
            clear_results()
            state["items"] = db_controller.quick_search(entry.get())
            if not state["items"]:
                tk.Label(result_holder, text="没有匹配结果", bg=COLORS["content_bg"],
                         fg=COLORS["Level2fg"], font=font(11)).pack(anchor="w", pady=8)
                return
            for i, item in enumerate(state["items"]):
                row = tk.Frame(result_holder, bg=COLORS["content_bg"], cursor="hand2")
                row.pack(fill="x", pady=1)
                tk.Label(row, text=item["kind"], bg=COLORS["btn_bg"],
                         fg=COLORS["Level2fg"], font=font(8), padx=6, pady=1).pack(
                    side="left", padx=(0, 10))
                tk.Label(row, text=item["title"], bg=COLORS["content_bg"],
                         fg=COLORS["Level1fg"], font=font(11), anchor="w").pack(side="left")
                tk.Label(row, text=item["subtitle"], bg=COLORS["content_bg"],
                         fg=COLORS["Level2fg"], font=font(9), anchor="w").pack(
                    side="left", padx=8)
                row.bind("<Button-1>", lambda e, idx=i: choose(idx))
                for child in row.winfo_children():
                    child.bind("<Button-1>", lambda e, idx=i: choose(idx))
                state["widgets"].append(row)

        entry.bind("<KeyRelease>", lambda e: render())
        entry.bind("<Return>", lambda e: choose(0))
        dlg.bind("<Escape>", lambda e: dlg.destroy())
        render()
        dlg.grab_set()

    def _goto_record(self, kind, keys):
        self._open_page("data")
        self.operate_window.goto(kind, keys)

    # ==================================================================
    # 回调：操作记录 / 筛选徽标 / 统计刷新
    # ==================================================================
    def _on_activity(self, text, state=None):
        self._recent.insert(0, (text, state))
        self._recent = self._recent[:3]
        self._refresh_recent()
        self._refresh_stats()

    def _on_filter(self, target, filters):
        if filters:
            parts = [f"{k}={v}" for k, v in filters[:2]]
            more = "…" if len(filters) > 2 else ""
            self._filter_text = f"{target} · " + "、".join(parts) + more
        else:
            self._filter_text = ""
        self._refresh_filter_chip()

    def _refresh_filter_chip(self):
        for w in self._filter_holder.winfo_children():
            w.destroy()
        if not self._filter_text:
            return

        chip = tk.Frame(self._filter_holder, bg=COLORS["btn_bg"])
        chip.pack(fill="x", padx=6, pady=2)
        tk.Label(chip, text="筛选中", bg=COLORS["btn_bg"], fg=COLORS["Level2fg"],
                 font=font(8), padx=6).pack(side="left")
        tk.Label(chip, text=self._filter_text, bg=COLORS["btn_bg"], fg=COLORS["Level1fg"],
                 font=font(8), anchor="w").pack(side="left", fill="x", expand=True)

        close = tk.Label(chip, text="×", bg=COLORS["btn_bg"], fg=COLORS["Level2fg"],
                         font=font(10), padx=6, cursor="hand2")
        close.pack(side="right")
        close.bind("<Button-1>", lambda e: self._clear_filters())
        close.bind("<Enter>", lambda e: close.configure(fg=COLORS["warn_fg"]))
        close.bind("<Leave>", lambda e: close.configure(fg=COLORS["Level2fg"]))

    def _clear_filters(self):
        self.operate_window.clear_filters()

    def _refresh_recent(self):
        for w in self._recent_block.winfo_children():
            w.destroy()
        if self._collapsed:
            return

        tk.Label(
            self._recent_block, text="最近", bg=COLORS["sidebar_bg"],
            fg=COLORS["Level2fg"], font=font(9), anchor="w",
        ).pack(fill="x", padx=20, pady=(4, 0))

        if not self._recent:
            tk.Label(
                self._recent_block, text="暂无操作", bg=COLORS["sidebar_bg"],
                fg=COLORS["Level2fg"], font=font(8), anchor="w",
            ).pack(fill="x", padx=22, pady=(1, 2))
            return

        holder = tk.Frame(self._recent_block, bg=COLORS["sidebar_bg"])
        holder.pack(fill="x", padx=14, pady=(2, 4))
        for text, state in self._recent:
            row = tk.Frame(holder, bg=COLORS["sidebar_bg"], cursor="hand2")
            row.pack(fill="x", pady=1)
            tk.Label(row, text="·", bg=COLORS["sidebar_bg"], fg=COLORS["Level2fg"],
                     font=font(9)).pack(side="left", padx=(2, 4))
            tk.Label(row, text=text, bg=COLORS["sidebar_bg"], fg=COLORS["Level2fg"],
                     font=font(9), anchor="w").pack(side="left", fill="x", expand=True)
            if state is not None:
                for w in (row,) + tuple(row.winfo_children()):
                    w.bind("<Button-1>", lambda e, s=state: self._replay(s))
            else:
                for w in (row,) + tuple(row.winfo_children()):
                    w.configure(cursor="arrow")

    def _replay(self, state):
        self._open_page("data")
        self.operate_window.apply_state(state)

    def _refresh_stats(self):
        try:
            stats = db_controller.overview_stats()
            trend = db_controller.exam_trend(5)
        except Exception:
            self._status_label.configure(text="● 数据库异常", fg=COLORS["danger"])
            return

        if self._stats_labels:
            self._stats_labels["students"].configure(text=f"{stats['students']:,}")
            self._stats_labels["exams"].configure(text=f"{stats['exams']:,}")
            self._stats_labels["scores"].configure(text=f"{stats['scores']:,}")
            self._stats_hint.configure(
                text=f"平均 {stats['avg_score']:.1f} 分 · 及格率 {stats['pass_rate']:.1f}%"
            )

        for w in self._spark_holder.winfo_children():
            w.destroy()
        if trend and not self._collapsed:
            values = [t["avg"] for t in reversed(trend)]
            spark = sparkline(self._spark_holder, values, width=200, height=46)
            spark.pack(anchor="w")

        size = os.path.getsize(DB_FILE) / 1024 / 1024 if os.path.exists(DB_FILE) else 0
        text = f"● {size:.0f}M" if self._collapsed else f"● 数据库已连接 · {size:.1f} MB"
        self._status_label.configure(text=text, fg=COLORS["ok_fg"])

    # ==================================================================
    # 折叠 / 调宽 / 主题
    # ==================================================================
    def _toggle_collapse(self):
        self._collapsed = not self._collapsed
        width = SIDEBAR_COLLAPSED if self._collapsed else self._sidebar_width
        self.sidebar.configure(width=width)
        self._build_sidebar()
        self._mark_active()

    def _start_resize(self, event):
        self._resize_start_x = event.x_root

    def _on_resize(self, event):
        if self._collapsed:
            return
        width = self._sidebar_width + (event.x_root - self._resize_start_x)
        width = max(180, min(360, width))
        if width != self._sidebar_width:
            self._sidebar_width = width
            self.sidebar.configure(width=width)

    def _toggle_theme(self):
        theme.toggle_theme()
        state = self.current_page_key
        self.root.configure(bg=COLORS["content_bg"])
        self._build_ui()
        self._open_page(state)

    # ==================================================================
    # 快捷键
    # ==================================================================
    def _bind_shortcuts(self):
        self.root.bind_all("<Command-k>", lambda e: self._open_search())
        self.root.bind_all("<Control-k>", lambda e: self._open_search())
        self.root.bind_all("<Command-b>", lambda e: self._toggle_collapse())
        self.root.bind_all("<Command-j>", lambda e: self._toggle_theme())
