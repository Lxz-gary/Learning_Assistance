"""分析页：成绩概览 / 科目对比 / 班级排名。"""

import tkinter as tk

from Controller.DataBaseController import DataBaseController
from .theme import COLORS, font
from .widgets import build_table_card
from .charts import kpi_card, vbar_chart, hbar_chart

db_controller = DataBaseController()

# 表格模版的基础配置（配色与数据页一致）
TABLE_BASE = {
    "card_bg":        "sidebar_bg",
    "row_bg":         "sidebar_bg",
    "row_alt":        "content_bg",
    "heading_bg":     "sidebar_active",
    "heading_fg":     "Level1fg",
    "heading_act_bg": "accent",
    "heading_act_fg": "card_bg",
    "selected_bg":    "accent",
    "selected_fg":    "selected_fg",
    "h_scroll":       False,
}


class AnalysisWindow:
    def __init__(self, root: tk.Tk, content_frame: tk.Frame):
        self.root = root
        self.content_frame = content_frame

    # ------------------------------------------------------------------
    def show(self, mode):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        for r in range(12):
            self.content_frame.grid_rowconfigure(r, weight=0)
        for c in range(6):
            self.content_frame.grid_columnconfigure(c, weight=0)

        if mode == "overview":
            self._overview()
        elif mode == "subject":
            self._subject()
        elif mode == "class":
            self._class_ranking()

    # ------------------------------------------------------------------
    def _header(self, title, subtitle):
        head = tk.Frame(self.content_frame, bg=COLORS["content_bg"])
        head.pack(fill="x", padx=20, pady=(18, 2))
        tk.Label(
            head, text=title, bg=COLORS["content_bg"], fg=COLORS["Level1fg"],
            font=font(20, "bold"), anchor="w",
        ).pack(anchor="w")
        tk.Label(
            head, text=subtitle, bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
            font=font(11), anchor="w",
        ).pack(anchor="w", pady=(2, 0))
        return head

    def _section(self, text, pady=(16, 6)):
        tk.Label(
            self.content_frame, text=text, bg=COLORS["content_bg"],
            fg=COLORS["Level1fg"], font=font(13, "bold"), anchor="w",
        ).pack(fill="x", padx=20, pady=pady)

    # ==================================================================
    # 概览
    # ==================================================================
    def _overview(self):
        self._header("成绩概览", "数据规模、整体水平与最近考试走势")

        stats = db_controller.overview_stats()

        cards = tk.Frame(self.content_frame, bg=COLORS["content_bg"])
        cards.pack(fill="x", padx=20, pady=(14, 0))
        items = [
            ("学生总数", f"{stats['students']:,}", f"{stats['classes']} 个班级", False),
            ("考试场次", f"{stats['exams']:,}", f"{stats['subjects']} 个科目", False),
            ("成绩记录", f"{stats['scores']:,}", "全部科目合计", False),
            ("平均分", f"{stats['avg_score']:.1f}", "全体成绩均值", False),
            ("及格率", f"{stats['pass_rate']:.1f}%", "≥60 分占比", True),
        ]
        for i, (title, value, hint, accent) in enumerate(items):
            card = kpi_card(cards, title, value, hint, accent=accent)
            card.grid(row=0, column=i, sticky="nsew", padx=(0, 10))
            cards.grid_columnconfigure(i, weight=1)

        # 近 5 场考试平均分
        self._section("近 5 场考试 · 平均分")
        trend = db_controller.exam_trend(5)
        trend_items = [(t["exam_id"][-3:], t["avg"]) for t in reversed(trend)]
        chart = vbar_chart(self.content_frame, trend_items, height=180)
        chart.pack(fill="x", padx=20)

        # 科目平均分
        self._section("各科平均分 · 及格率")
        subjects = db_controller.subject_stats()
        hbar = hbar_chart(
            self.content_frame,
            [(s["subject"], s["avg"], f"及格率 {s['pass_rate']}%") for s in subjects],
            max_value=100,
        )
        hbar.pack(fill="x", padx=20)

        tk.Frame(self.content_frame, bg=COLORS["content_bg"], height=10).pack()

    # ==================================================================
    # 科目对比
    # ==================================================================
    def _subject(self):
        self._header("科目对比", "各科目的平均分、极值与及格率")

        subjects = db_controller.subject_stats()
        if not subjects:
            tk.Label(
                self.content_frame, text="暂无成绩数据", bg=COLORS["content_bg"],
                fg=COLORS["Level2fg"], font=font(12),
            ).pack(pady=40)
            return

        best = subjects[0]
        worst = subjects[-1]
        summary = tk.Frame(self.content_frame, bg=COLORS["content_bg"])
        summary.pack(fill="x", padx=20, pady=(12, 0))
        for i, (title, value, hint, accent) in enumerate([
            ("最高平均分", f"{best['avg']:.1f}", best["subject"], True),
            ("最低平均分", f"{worst['avg']:.1f}", worst["subject"], False),
            ("科目数", f"{len(subjects)}", "覆盖全部科目", False),
        ]):
            c = kpi_card(summary, title, value, hint, accent=accent)
            c.grid(row=0, column=i, sticky="nsew", padx=(0, 10))
            summary.grid_columnconfigure(i, weight=1)

        self._section("平均分对比")
        hbar = hbar_chart(
            self.content_frame,
            [(s["subject"], s["avg"], f"及格率 {s['pass_rate']}%") for s in subjects],
            max_value=100,
        )
        hbar.pack(fill="x", padx=20)

        self._section("明细")
        config = dict(TABLE_BASE)
        config.update({
            "columns": ("subject", "count", "avg", "max", "min", "pass_rate"),
            "headers": {
                "subject":   ("科目",   100),
                "count":     ("成绩数", 100),
                "avg":       ("平均分", 100),
                "max":       ("最高分", 100),
                "min":       ("最低分", 100),
                "pass_rate": ("及格率", 100),
            },
        })
        card, tree = build_table_card(self.content_frame, config, height=10)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        for i, s in enumerate(subjects):
            tree.insert("", "end", values=(
                s["subject"], s["count"], s["avg"], s["max"], s["min"],
                f"{s['pass_rate']}%",
            ), tags=("evenrow" if i % 2 == 0 else "oddrow",))

    # ==================================================================
    # 班级排名
    # ==================================================================
    def _class_ranking(self):
        self._header("班级排名", "按平均分排序（只统计有成绩的班级）")

        rows = db_controller.class_ranking()
        if not rows:
            tk.Label(
                self.content_frame, text="暂无成绩数据", bg=COLORS["content_bg"],
                fg=COLORS["Level2fg"], font=font(12),
            ).pack(pady=40)
            return

        top = rows[0]
        cards = tk.Frame(self.content_frame, bg=COLORS["content_bg"])
        cards.pack(fill="x", padx=20, pady=(12, 0))
        for i, (title, value, hint, accent) in enumerate([
            ("第一名", top["class_name"], f"平均 {top['avg']:.1f} 分", True),
            ("班级数", f"{len(rows)}", "参与统计", False),
            ("平均及格率", f"{sum(r['pass_rate'] for r in rows) / len(rows):.1f}%", "各班均值", False),
        ]):
            c = kpi_card(cards, title, value, hint, accent=accent)
            c.grid(row=0, column=i, sticky="nsew", padx=(0, 10))
            cards.grid_columnconfigure(i, weight=1)

        self._section("排名明细")
        config = dict(TABLE_BASE)
        config.update({
            "columns": ("rank", "class_name", "students", "scores", "avg", "pass_rate"),
            "headers": {
                "rank":       ("排名",   60),
                "class_name": ("班级",   110),
                "students":   ("学生数", 90),
                "scores":     ("成绩数", 90),
                "avg":        ("平均分", 90),
                "pass_rate":  ("及格率", 90),
            },
        })
        card, tree = build_table_card(self.content_frame, config, height=10)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        for i, r in enumerate(rows):
            tree.insert("", "end", values=(
                i + 1, r["class_name"], r["students"], r["scores"],
                r["avg"], f"{r['pass_rate']}%",
            ), tags=("evenrow" if i % 2 == 0 else "oddrow",))
