"""数据管理页：查询 / 新增 / 修改 / 删除。

界面约定：
- 所有配色、字体来自 UI/theme.py
- 按钮、输入框、确认弹窗、表格卡片来自 UI/widgets.py
- 结果表分页展示（每页 200 条），双击行进入编辑
"""

import math
import time
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog

import customtkinter as ctk

from Controller.DataBaseController import DataBaseController
from Utils.ExcelOperater import export_to_excel
from .theme import COLORS, font
from .widgets import (
    make_btn, make_entry, mark_entry, build_table_card, ask_dialog,
)

db_controller = DataBaseController()


# ======================================================================
# 查询配置：学生 / 考试 / 成绩
# ======================================================================
SEARCH_CONFIG = {
    # ------------------------- 学生 -------------------------
    "学生": {
        "content": "学生",
        "row": 7,
        "title": "学生查询结果",
        "subtitle": "以下是符合筛选条件的学生数据",
        "query_func": "query_student",
        "query_fields": [
            ("id", "编号"), ("name", "姓名"),
            ("class", "班级"), ("grade", "年级"),
            ("telephonenum", "电话"), ("email", "邮箱"),
            ("createtime", "创建时间"), ("changetime", "修改时间"),
        ],
        "query_primary": 2,          # 默认只显示前 2 个条件，其余收进“更多筛选”
        "columns": ("id", "name", "class_name", "grade",
                    "telephonenum", "email", "createtime", "changetime"),
        "headers": {
            "id":            ("编号",     90),
            "name":          ("姓名",     100),
            "class_name":    ("班级",     110),
            "grade":         ("年级",     80),
            "telephonenum":  ("电话",     140),
            "email":         ("邮箱",     200),
            "createtime":    ("创建时间", 160),
            "changetime":    ("修改时间", 160),
        },
        "key_index": [0],            # 主键在 columns 里的下标
        "key_field_count": 1,        # 编辑时前几个字段只读
        "add_fields": [
            {"key": "id",           "label": "编号", "required": True},
            {"key": "name",         "label": "姓名", "required": True},
            {"key": "class",        "label": "班级", "required": True},
            {"key": "grade",        "label": "年级", "required": True},
            {"key": "telephonenum", "label": "电话", "kind": "phone"},
            {"key": "email",        "label": "邮箱", "kind": "email"},
        ],
        "card_bg":        "sidebar_bg",
        "row_bg":         "sidebar_bg",
        "row_alt":        "content_bg",
        "heading_bg":     "sidebar_active",
        "heading_fg":     "Level1fg",
        "heading_act_bg": "accent",
        "heading_act_fg": "card_bg",
        "selected_bg":    "accent",
        "selected_fg":    "selected_fg",
        "h_scroll":       True,
    },

    # ------------------------- 考试 -------------------------
    "考试": {
        "content": "考试",
        "row": 6,
        "title": "考试查询结果",
        "subtitle": "以下是符合筛选条件的考试数据",
        "query_func": "query_exam",
        "query_fields": [
            ("exam_id", "考试编号"), ("exam_name", "考试名称"),
            ("exam_time", "考试时间"), ("createtime", "创建时间"),
            ("changetime", "修改时间"),
        ],
        "query_primary": 2,
        "columns": ("exam_id", "exam_name", "exam_time", "createtime", "changetime"),
        "headers": {
            "exam_id":     ("考试编号", 130),
            "exam_name":   ("考试名称", 220),
            "exam_time":   ("考试时间", 160),
            "createtime":  ("创建时间", 180),
            "changetime":  ("修改时间", 180),
        },
        "key_index": [0],
        "key_field_count": 1,
        "add_fields": [
            {"key": "id",   "label": "考试编号", "required": True},
            {"key": "name", "label": "考试名称", "required": True},
            {"key": "date", "label": "考试日期", "required": True, "kind": "date"},
        ],
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
    },

    # ------------------------- 成绩 -------------------------
    "成绩": {
        "content": "成绩",
        "row": 8,
        "title": "成绩查询结果",
        "subtitle": "以下是符合筛选条件的成绩数据",
        "query_func": "query_score",
        "query_fields": [
            ("student_id", "学号"), ("exam_id", "考试编号"),
            ("subject", "科目"), ("initialscore", "初始成绩"),
            ("score", "成绩"), ("rank", "排名"),
            ("headcount", "总人数"), ("createtime", "创建时间"),
            ("changetime", "修改时间"),
        ],
        "query_primary": 2,
        "columns": ("student_id", "exam_id", "subject",
                    "initialscore", "score", "rank", "headcount",
                    "createtime", "changetime"),
        "headers": {
            "student_id":   ("学号",     100),
            "exam_id":      ("考试编号", 110),
            "subject":      ("科目",     100),
            "initialscore": ("初始分数", 100),
            "score":        ("分数",     90),
            "rank":         ("排名",     80),
            "headcount":    ("总人数",   90),
            "createtime":   ("创建时间", 160),
            "changetime":   ("修改时间", 160),
        },
        "key_index": [0, 1, 2],      # 成绩：(student_id, exam_id, subject) 联合主键
        "key_field_count": 3,
        "add_fields": [
            {"key": "student_id",   "label": "学号",     "required": True},
            {"key": "exam_id",      "label": "考试编号", "required": True},
            {"key": "subject",      "label": "科目",     "required": True},
            {"key": "initialscore", "label": "初始成绩", "required": True, "kind": "int"},
            {"key": "score",        "label": "成绩",     "required": True, "kind": "int"},
            {"key": "rank",         "label": "排名",     "required": True, "kind": "int"},
            {"key": "headcount",    "label": "总人数",   "required": True, "kind": "int"},
        ],
        "card_bg":        "sidebar_bg",
        "row_bg":         "sidebar_bg",
        "row_alt":        "content_bg",
        "heading_bg":     "sidebar_active",
        "heading_fg":     "Level1fg",
        "heading_act_bg": "accent",
        "heading_act_fg": "card_bg",
        "selected_bg":    "accent",
        "selected_fg":    "selected_fg",
        "h_scroll":       True,
    },
}


class OperateWindow:
    PAGE_SIZE = 200

    def __init__(self, root: tk.Tk, content_frame: tk.Frame):
        self.root = root
        self.content_frame = content_frame

        self._result_container = None
        self._all_results = []
        self._current_config = None
        self._current_target = None
        self._current_page = 0
        self._row_keys = {}
        self._page_rows = {}
        self._pending_status = None

        self._query_entries = {}
        self._advanced_widgets = []
        self._advanced_open = False

        self._on_activity = None
        self._on_filter = None

    # ==================================================================
    # 页面骨架
    # ==================================================================
    def build_operate_page(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self._result_container = None

        self.content_frame.grid_columnconfigure(0, weight=0)
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(2, weight=0)
        self.content_frame.grid_columnconfigure(3, weight=1)

        # ---------- 页面标题 ----------
        head = tk.Frame(self.content_frame, bg=COLORS["content_bg"])
        head.grid(row=0, column=0, columnspan=4, sticky="we", padx=16, pady=(18, 2))
        tk.Label(
            head, text="数据管理", bg=COLORS["content_bg"], fg=COLORS["Level1fg"],
            font=font(20, "bold"),
        ).pack(side="left")
        tk.Label(
            head, text="查询 · 新增 · 修改 · 删除", bg=COLORS["content_bg"],
            fg=COLORS["Level2fg"], font=font(11),
        ).pack(side="left", padx=(10, 0), pady=(8, 0))

        # ---------- 查询类型 ----------
        type_row = tk.Frame(self.content_frame, bg=COLORS["content_bg"])
        type_row.grid(row=1, column=0, columnspan=4, sticky="we", padx=16, pady=(6, 4))
        tk.Label(
            type_row, text="查询类型", bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
            font=font(13),
        ).pack(side="left", padx=(0, 10))
        self.C_target = ctk.CTkComboBox(
            type_row, values=list(SEARCH_CONFIG.keys()), width=150, height=30,
            border_width=0, state="readonly", command=self._on_target_change,
            fg_color=COLORS["entry_bg"], text_color=COLORS["Level1fg"],
            button_color=COLORS["btn_bg"], button_hover_color=COLORS["btn_hover"],
            dropdown_fg_color=COLORS["sidebar_bg"],
            dropdown_text_color=COLORS["Level1fg"],
            dropdown_hover_color=COLORS["btn_hover"],
        )
        self.C_target.pack(side="left")
        self.C_target.set("学生")

        self._switch_form("学生")

    def _on_target_change(self, target):
        self._switch_form(target)

    def _switch_form(self, target):
        """清掉旧表单和结果区，挂上当前类型的查询表单。"""
        self._current_target = target
        self._result_container = None

        # 清空 row >= 2 的控件（查询表单、结果区）
        for child in list(self.content_frame.winfo_children()):
            grid_info = child.grid_info()
            if grid_info and grid_info.get("row", 0) >= 2:
                child.destroy()

        # 复位行权重，避免上一个类型留下的空白行
        for r in range(20):
            self.content_frame.grid_rowconfigure(r, weight=0)

        if target in SEARCH_CONFIG:
            self._build_query_form(target)

    # ==================================================================
    # 查询表单
    # ==================================================================
    def _build_query_form(self, target):
        config = SEARCH_CONFIG[target]
        self._current_config = config
        self._advanced_open = False
        self._advanced_widgets = []
        self._query_entries = {}

        fields = config["query_fields"]
        primary = config.get("query_primary", 2)

        for i, (key, label) in enumerate(fields):
            r = 2 + i // 2
            c = (i % 2) * 2

            lbl = tk.Label(
                self.content_frame, text=label, bg=COLORS["content_bg"],
                fg=COLORS["Level2fg"], font=font(13),
            )
            lbl.grid(row=r, column=c, padx=(16, 6), pady=6, sticky="e")

            entry = make_entry(self.content_frame)
            entry.grid(row=r, column=c + 1, padx=(0, 24), pady=6, sticky="we")
            entry.bind("<Return>", lambda e, t=target: self.search(t))

            self._query_entries[key] = entry
            setattr(self, f"E_{key}", entry)

            if i >= primary:
                lbl.grid_remove()
                entry.grid_remove()
                self._advanced_widgets.append((lbl, entry))

        # ---------- 操作行 ----------
        actions = tk.Frame(self.content_frame, bg=COLORS["content_bg"])
        self._form_actions = actions

        if len(fields) > primary:
            self._advanced_btn = make_btn(
                actions, "更多筛选 ▾", self._toggle_advanced,
                kind="ghost", size=11, padx=14, pady=6,
            )
            self._advanced_btn.pack(side="left")

        make_btn(
            actions, "重置", self._reset_query,
            kind="secondary", size=11, padx=16, pady=6,
        ).pack(side="left", padx=(8, 0))

        make_btn(
            actions, "查询", lambda: self.search(target),
            kind="primary", size=12, padx=30, pady=8,
        ).pack(side="right")

        self._layout_form_actions()

    def _layout_form_actions(self):
        """操作行跟着可见字段数量走，收起时不会留一大片空白。"""
        config = self._current_config
        total = len(config["query_fields"])
        primary = config.get("query_primary", 2)
        visible = total if self._advanced_open else primary
        row = 2 + (visible + 1) // 2
        self._form_actions.grid(
            row=row, column=0, columnspan=4, sticky="we", padx=16, pady=(10, 4)
        )

    def _toggle_advanced(self):
        self._advanced_open = not self._advanced_open
        for lbl, entry in self._advanced_widgets:
            if self._advanced_open:
                lbl.grid()
                entry.grid()
            else:
                lbl.grid_remove()
                entry.grid_remove()
        self._advanced_btn.configure(
            text="收起筛选 ▴" if self._advanced_open else "更多筛选 ▾"
        )
        self._layout_form_actions()

    # ------------------------------------------------------------------
    # 对外接口（主窗口用）：回调、状态、跳转
    # ------------------------------------------------------------------
    def set_callbacks(self, on_activity=None, on_filter=None):
        self._on_activity = on_activity
        self._on_filter = on_filter

    def _notify(self, text):
        if self._on_activity:
            self._on_activity(text, self.current_state())

    def current_state(self):
        target = self._current_target
        if target not in SEARCH_CONFIG or not self._query_entries:
            return (target, {})
        return (target, {k: e.get().strip() for k, e in self._query_entries.items()})

    def apply_state(self, state):
        target, filters = state
        if target not in SEARCH_CONFIG:
            return
        if target != self._current_target:
            if hasattr(self, "C_target"):
                self.C_target.set(target)
            self._switch_form(target)
        for key, entry in self._query_entries.items():
            entry.delete(0, "end")
            value = filters.get(key, "")
            if value:
                entry.insert(0, value)
        self.search(target)

    def clear_filters(self):
        if not self._query_entries:
            return
        for entry in self._query_entries.values():
            entry.delete(0, "end")
        self.search(self._current_target)

    def goto(self, kind, keys):
        if kind not in SEARCH_CONFIG:
            return
        mapping = {
            "学生": {"id": keys[0] if keys else ""},
            "考试": {"exam_id": keys[0] if keys else ""},
            "成绩": {
                "student_id": keys[0] if len(keys) > 0 else "",
                "exam_id": keys[1] if len(keys) > 1 else "",
                "subject": keys[2] if len(keys) > 2 else "",
            },
        }
        self.apply_state((kind, mapping.get(kind, {})))
        self.root.after(80, self._focus_first_row)

    def _focus_first_row(self):
        if not self._result_container or not self._result_container.winfo_exists():
            return
        def find(widget):
            for child in widget.winfo_children():
                if isinstance(child, ttk.Treeview):
                    return child
                found = find(child)
                if found is not None:
                    return found
            return None
        tree = find(self._result_container)
        if tree is not None:
            rows = tree.get_children()
            if rows:
                tree.selection_set(rows[0])
                tree.focus(rows[0])
                tree.see(rows[0])

    def _reset_query(self):
        for entry in self._query_entries.values():
            entry.delete(0, "end")
        first = next(iter(self._query_entries.values()), None)
        if first is not None:
            first.focus_set()

    # ==================================================================
    # 查询
    # ==================================================================
    def search(self, target=None, page=0):
        target = target or self._current_target
        if target not in SEARCH_CONFIG:
            return
        config = SEARCH_CONFIG[target]

        values = [self._query_entries[key].get().strip() for key, _ in config["query_fields"]]

        try:
            results = getattr(db_controller, config["query_func"])(*values)
        except Exception as exc:
            results = []
            self._pending_status = (f"查询失败：{exc}", False)

        self._render_result(results, config, page=page)

        active = [
            (label, value)
            for (key, label), value in zip(config["query_fields"], values)
            if value
        ]
        if self._on_filter:
            self._on_filter(target, active)

    # ==================================================================
    # 结果区
    # ==================================================================
    def _render_result(self, results, config, page=0):
        if self._result_container is not None and self._result_container.winfo_exists():
            self._result_container.destroy()

        self._all_results = results
        self._current_config = config

        container = tk.Frame(self.content_frame, bg=COLORS["content_bg"])
        container.grid(row=config["row"], column=0, columnspan=4, sticky="nsew",
                       padx=16, pady=(14, 12))
        self._result_container = container

        for r in range(20):
            self.content_frame.grid_rowconfigure(r, weight=0)
        self.content_frame.grid_rowconfigure(config["row"], weight=1)

        total = len(results)
        pages = max(1, math.ceil(total / self.PAGE_SIZE))
        page = max(0, min(page, pages - 1))
        self._current_page = page

        # ---------- 标题行 ----------
        header = tk.Frame(container, bg=COLORS["content_bg"])
        header.pack(fill="x", pady=(0, 4))
        tk.Label(
            header, text=config["title"], bg=COLORS["content_bg"],
            fg=COLORS["Level1fg"], font=font(17, "bold"),
        ).pack(side="left")
        tk.Label(
            header, text=f"共 {total} 条记录" if total else "无匹配记录",
            bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=font(12),
        ).pack(side="right", pady=(6, 0))

        tk.Label(
            container, text=config["subtitle"] + "　·　双击行可编辑",
            bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=font(11),
        ).pack(anchor="w", pady=(0, 8))

        # ---------- 操作结果提示 ----------
        if self._pending_status:
            text, ok = self._pending_status
            tk.Label(
                container, text=text, bg=COLORS["content_bg"],
                fg=COLORS["ok_fg"] if ok else COLORS["warn_fg"], font=font(11),
            ).pack(anchor="w", pady=(0, 8))
            self._pending_status = None

        # ---------- 表格 ----------
        card, tree = build_table_card(container, config, height=10)
        card.pack(fill="both", expand=True)
        tree.configure(selectmode="extended")

        self._row_keys = {}
        self._page_rows = {}
        start = page * self.PAGE_SIZE
        page_items = results[start:start + self.PAGE_SIZE]

        if page_items:
            for i, row in enumerate(page_items):
                iid = f"row{i}"
                self._row_keys[iid] = [row[j] for j in config["key_index"]]
                self._page_rows[iid] = row
                tree.insert("", "end", iid=iid, values=row,
                            tags=("evenrow" if i % 2 == 0 else "oddrow",))
        else:
            tree.insert("", "end", values=("—",) * len(config["columns"]),
                        tags=("empty",))

        tree.bind("<Double-1>", lambda e: self._edit_selected(tree, config, e))
        tree.bind("<Delete>", lambda e: self._delete_selected(tree, config))
        tree.bind("<BackSpace>", lambda e: self._delete_selected(tree, config))

        # ---------- 分页条 ----------
        if pages > 1:
            pager = tk.Frame(container, bg=COLORS["content_bg"])
            pager.pack(fill="x", pady=(8, 0))

            tk.Label(
                pager, text=f"第 {page + 1} / {pages} 页", bg=COLORS["content_bg"],
                fg=COLORS["Level2fg"], font=font(11),
            ).pack(side="left")

            if page < pages - 1:
                make_btn(
                    pager, "下一页 ›", lambda: self._render_result(results, config, page + 1),
                    kind="ghost", size=11, padx=14, pady=5,
                ).pack(side="right")
            if page > 0:
                make_btn(
                    pager, "‹ 上一页", lambda: self._render_result(results, config, page - 1),
                    kind="ghost", size=11, padx=14, pady=5,
                ).pack(side="right", padx=(0, 8))

        # ---------- 底部按钮 ----------
        footer = tk.Frame(container, bg=COLORS["content_bg"])
        footer.pack(fill="x", pady=(10, 0))

        make_btn(
            footer, "＋ 新增", lambda: self._open_record_dialog(config, "add"),
            kind="primary", size=12, padx=20,
        ).pack(side="left")

        make_btn(
            footer, "− 删除", lambda: self._delete_selected(tree, config),
            kind="danger", size=12, padx=20,
        ).pack(side="left", padx=(8, 0))

        make_btn(
            footer, "关闭", container.destroy, kind="secondary", size=12, padx=22,
        ).pack(side="right")

        make_btn(
            footer, "导出", lambda: self._export(config, results),
            kind="secondary", size=12, padx=22,
        ).pack(side="right", padx=(0, 10))

        sel_label = tk.Label(
            footer, text="", bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
            font=font(11),
        )
        sel_label.pack(side="left", padx=(12, 0))

        def update_selection(event=None):
            n = len(tree.selection())
            sel_label.configure(text=f"已选 {n} 行" if n else "")

        tree.bind("<<TreeviewSelect>>", update_selection)

    # ==================================================================
    # 删除
    # ==================================================================
    def _delete_selected(self, tree, config):
        content = config["content"]

        if not self._row_keys:
            ask_dialog(self.root, "提示", "当前没有可删除的数据。",
                       ok_text="知道了", cancel_text=None)
            return "break"

        selected = [iid for iid in tree.selection() if iid in self._row_keys]
        if not selected:
            ask_dialog(self.root, "提示",
                       "请先在表格里选中要删除的行。\n可以按住 ⌘ 或 Shift 多选。",
                       ok_text="知道了", cancel_text=None)
            return "break"

        keys_list = [self._row_keys[iid] for iid in selected]

        if content == "成绩":
            message = f"将删除 {len(keys_list)} 条成绩记录。"
        else:
            related = sum(
                db_controller.count_related_scores(content, keys) for keys in keys_list
            )
            unit = "名学生" if content == "学生" else "场考试"
            message = f"将删除 {len(keys_list)} {unit}。"
            if related:
                message += f"\n其名下的 {related} 条成绩会一并删除。"
        message += "\n此操作不可恢复，确定继续吗？"

        if not ask_dialog(self.root, "确认删除", message, ok_text="删除", danger=True):
            return "break"

        deleted, msg = db_controller.delete_records(content, keys_list)
        self._pending_status = (msg, deleted > 0)
        if deleted:
            self._notify(f"删除 {deleted} 条{content}")
        self.search(content, page=self._current_page)
        return "break"

    # ==================================================================
    # 新增 / 编辑弹窗
    # ==================================================================
    def _edit_selected(self, tree, config, event=None):
        iid = tree.identify_row(event.y) if event is not None else tree.focus()
        if iid in self._page_rows:
            self._open_record_dialog(config, "edit", self._page_rows[iid])

    def _open_record_dialog(self, config, mode="add", row=None):
        content = config["content"]
        fields = config["add_fields"]
        key_count = config.get("key_field_count", 1)
        is_edit = mode == "edit"

        win = tk.Toplevel(self.root)
        win.title(("编辑" if is_edit else "新增") + content)
        win.configure(bg=COLORS["content_bg"])
        win.geometry("880x560" if is_edit else "880x680")
        win.minsize(660, 320 if is_edit else 460)
        win.transient(self.root)

        # ---------- 标题行 ----------
        header = tk.Frame(win, bg=COLORS["content_bg"])
        header.pack(fill="x", padx=16, pady=(14, 6))
        tk.Label(
            header, text=("编辑" if is_edit else "新增") + content,
            bg=COLORS["content_bg"], fg=COLORS["Level1fg"], font=font(18, "bold"),
        ).pack(side="left")
        badge = tk.Label(
            header, text="" if is_edit else "本次新增 0 条",
            bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=font(12),
        )
        badge.pack(side="right", pady=(6, 0))

        tk.Label(
            win,
            text="主键字段不可修改" if is_edit else "带 * 的是必填项；保存成功后可继续录入下一条",
            bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=font(11),
        ).pack(anchor="w", padx=16)

        # ---------- 表单卡片 ----------
        form_card = tk.Frame(
            win, bg=COLORS["content_bg"],
            highlightbackground=COLORS["border"], highlightthickness=1, bd=0,
        )
        form_card.pack(fill="x", padx=16, pady=(10, 0))
        form = tk.Frame(form_card, bg=COLORS["content_bg"])
        form.pack(fill="x", padx=14, pady=12)
        form.grid_columnconfigure(1, weight=1)
        form.grid_columnconfigure(3, weight=1)

        entries = {}

        for i, field in enumerate(fields):
            r, c = divmod(i, 2)
            tk.Label(
                form, text=field["label"] + (" *" if field.get("required") else ""),
                bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=font(13),
            ).grid(row=r, column=c, padx=(0, 6), pady=6, sticky="e")

            entry = make_entry(form)
            entry.grid(row=r, column=c + 1, padx=(0, 20), pady=6, sticky="ew")
            if is_edit and row is not None:
                # 编辑模式：所有字段回填；主键只读（get() 仍然可用）
                entry.insert(0, "" if row[i] is None else str(row[i]))
                if i < key_count:
                    entry.configure(state="readonly",
                                    readonlybackground=COLORS["entry_bg"],
                                    fg=COLORS["Level2fg"])
            entries[field["key"]] = entry

        # ---------- 本次新增列表（仅新增模式） ----------
        tree_add = None
        if not is_edit:
            card, tree_add = build_table_card(win, config, height=6, h_scroll=True)
            card.pack(fill="both", expand=True, padx=16, pady=(12, 0))

        # ---------- 底部按钮 ----------
        footer = tk.Frame(win, bg=COLORS["content_bg"])
        footer.pack(fill="x", padx=16, pady=12)

        hint = tk.Label(
            footer, text="", bg=COLORS["content_bg"],
            fg=COLORS["warn_fg"], font=font(11),
        )
        hint.pack(side="left")

        added = {"n": 0}

        def field_error(field):
            value = entries[field["key"]].get().strip()
            if field.get("required") and not value:
                return f"{field['label']}不能为空"
            if not value:
                return None
            kind = field.get("kind")
            if kind == "int" and not value.isdigit():
                return f"{field['label']}必须是整数"
            if kind == "phone" and not (value.isdigit() and len(value) == 11):
                return "电话需为 11 位数字"
            if kind == "email" and ("@" not in value or "." not in value.split("@")[-1]):
                return "邮箱格式不正确"
            if kind == "date":
                try:
                    time.strptime(value, "%Y-%m-%d")
                except ValueError:
                    return "考试日期格式应为 YYYY-MM-DD"
            return None

        def check_on_blur(field):
            error = field_error(field)
            mark_entry(entries[field["key"]], bool(error))
            hint.configure(text=f"⚠ {error}" if error else "", fg=COLORS["warn_fg"])

        for i, field in enumerate(fields):
            if is_edit and i < key_count:
                continue
            entries[field["key"]].bind("<FocusOut>", lambda e, f=field: check_on_blur(f))

        def collect():
            values = []
            first_bad = None
            for field in fields:
                error = field_error(field)
                mark_entry(entries[field["key"]], bool(error))
                if error and first_bad is None:
                    first_bad = field
                value = entries[field["key"]].get().strip()
                values.append(int(value) if field.get("kind") == "int" and value else value)
            return values, first_bad

        def submit(event=None):
            values, first_bad = collect()
            if first_bad is not None:
                hint.configure(text=f"⚠ {field_error(first_bad)}", fg=COLORS["warn_fg"])
                entries[first_bad["key"]].focus_set()
                return "break"

            if is_edit:
                ok, message = db_controller.update_record(content, values)
                if not ok:
                    hint.configure(text=f"⚠ {message}", fg=COLORS["warn_fg"])
                    return "break"
                self._pending_status = (message, True)
                self._notify(f"修改{content} {values[0]}")
                self.search(content, page=self._current_page)
                win.destroy()
                return "break"

            ok, message = db_controller.add_record(content, values)
            if not ok:
                hint.configure(text=f"⚠ {message}", fg=COLORS["warn_fg"])
                return "break"

            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            tree_add.insert(
                "", "end", values=list(values) + [now, now],
                tags=("evenrow" if added["n"] % 2 == 0 else "oddrow",),
            )
            tree_add.see(tree_add.get_children()[-1])
            added["n"] += 1
            badge.configure(text=f"本次新增 {added['n']} 条")
            hint.configure(text=f"✓ {message}，可继续录入", fg=COLORS["ok_fg"])

            for entry in entries.values():
                entry.delete(0, "end")
            next(iter(entries.values())).focus_set()
            return "break"

        def finish():
            if added["n"]:
                self._pending_status = (f"已新增 {added['n']} 条{content}记录", True)
                self._notify(f"新增 {added['n']} 条{content}")
                self.search(content, page=10 ** 6)   # 跳到最后一页，能看到新数据
            win.destroy()

        for entry in entries.values():
            entry.bind("<Return>", submit)

        if is_edit:
            make_btn(
                footer, "取消", win.destroy, kind="secondary", size=12, padx=22, pady=8,
            ).pack(side="right", padx=(0, 10))
            make_btn(
                footer, "保存修改", submit, kind="primary", size=12, padx=24, pady=10,
            ).pack(side="right")
        else:
            make_btn(
                footer, "保存并关闭", finish, kind="secondary", size=12, padx=22, pady=9,
            ).pack(side="right")
            make_btn(
                footer, "保存", submit, kind="primary", size=12, padx=26, pady=10,
            ).pack(side="right", padx=(0, 10))

        win.protocol("WM_DELETE_WINDOW", win.destroy if is_edit else finish)

        # 编辑模式下主键只读，焦点放到第一个可编辑字段
        focusables = [
            entries[f["key"]] for i, f in enumerate(fields)
            if not (is_edit and i < key_count)
        ]
        (focusables[0] if focusables else next(iter(entries.values()))).focus_set()

        if is_edit:
            # 编辑弹窗按字段行数算高度，避免一大片空白
            rows = (len(fields) + 1) // 2
            win.geometry(f"880x{180 + rows * 40 + 70}")

        win.grab_set()

    # ==================================================================
    # 导出
    # ==================================================================
    def _export(self, config, results):
        filepath = filedialog.asksaveasfilename(
            title="保存文件",
            defaultextension=".xlsx",
            initialfile=f"{config['content']}数据.xlsx",
            filetypes=[("Excel 文件", "*.xlsx"), ("所有文件", "*.*")],
        )
        if not filepath:
            return
        export_to_excel(
            headers=[text for text, _ in config["headers"].values()],
            rows=results,
            filepath=filepath,
            sheet_name="查询结果",
            title=f"{config['content']}查询结果",
        )
