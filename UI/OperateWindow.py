import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
import time
from tkinter import filedialog
from Controller.DataBaseController import DataBaseController
from Utils.ExcelOperater import export_to_excel

db_controller = DataBaseController()
# ==================================================================
# 全局配色
# ==================================================================
COLORS = {
    "sidebar_bg": "#1e1f23",      # 深蓝灰侧边栏
    "Level1fg": "#cbd5e1",        # 一级文字灰
    "Level2fg": "#a1a1aa",        # 二级文字灰
    "sidebar_active": "#334155",  # 鼠标悬停/选中背景
    "accent": "#715533",         # 亮蓝强调色
    "selected_fg": "#ffffff",      # 选中行文字颜色s
    "content_bg": "#0d0d0d",      # 内容区背景
    "card_bg": "#ffffff",         # 卡片纯白
    "text_primary": "#0f172a",    # 深色主文字
    "border": "#2c2c3a",          # 分割线颜色

    # ---- 底部按钮区统一配色（主/次/图标三层只靠底色深浅区分）----
    "btn_bg":       "#1e1f23",    # 次按钮与图标按钮底色（比 content_bg 亮一档，暗背景上能看出形状）
    "btn_hover":    "#2b303b",    # 上面的悬停色，比 btn_bg 再亮一档
    "btn_fg":       "#cbd5e1",    # 按钮文字
    "btn_border":   "#2c2c3a",    # 次按钮描边
    "accent_hover": "#8a6740",    # 主按钮悬停（accent 提亮一档）
    "on_accent_fg": "#ffffff",    # 主按钮文字
    "warn_fg":      "#e07a5f",    # 校验提示文字（暖红）
}


# ==================================================================
# 查询配置：学生 / 考试 / 成绩
# ==================================================================
SEARCH_CONFIG = {
    # ------------------------- 学生 -------------------------
    "学生": {
        "content":"学生",
        "row": 7,
        "title": "查询结果",
        "subtitle": "以下是符合筛选条件的全部数据",
        "input_fields": ["id", "name", "class", "grade",
                         "telephonenum", "email", "createtime", "changetime"],
        "query_func": "query_student",
        "columns": ("id", "name", "class_name", "grade",
                    "telephonenum", "email", "createtime", "changetime"),
        "headers": {
            "id":            ("编号",     90),
            "name":          ("姓名",     100),
            "class_name":    ("班级",     110),
            "grade":         ("年级",     90),
            "telephonenum":  ("电话",     140),
            "email":         ("邮箱",     200),
            "createtime":    ("创建时间", 160),
            "changetime":    ("修改时间", 160),
        },
        # 配色引用（对应 COLORS 的键或直接色值）
        "card_bg":        "card_bg",
        "row_bg":         "card_bg",
        "row_alt":        "content_bg",
        "heading_bg":     "sidebar_bg",
        "heading_fg":     "Level2fg",
        "heading_act_bg": "sidebar_active",
        "heading_act_fg": "Level1fg",
        "selected_bg":    "accent",
        "selected_fg":    "selected_fg",
        "h_scroll":       False,
    },

    # ------------------------- 考试 -------------------------
    "考试": {
        "content":"考试",
        "row": 6,
        "title": "考试查询结果",
        "subtitle": "以下是符合筛选条件的全部考试数据",
        "input_fields": ["exam_id", "exam_name", "exam_time",
                         "createtime", "changetime"],
        "query_func": "query_exam",
        "columns": ("exam_id", "exam_name", "exam_time",
                    "createtime", "changetime"),
        "headers": {
            "exam_id":     ("考试编号", 130),
            "exam_name":   ("考试名称", 220),
            "exam_time":   ("考试时间", 180),
            "createtime":  ("创建时间", 180),
            "changetime":  ("修改时间", 180),
        },
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
        "content":"成绩",
        "row": 8,
        "title": "成绩查询结果",
        "subtitle": "以下是符合筛选条件的全部成绩数据",
        "input_fields": ["student_id", "exam_id", "subject",
                         "initialscore", "score", "rank", "headcount",
                         "createtime", "changetime"],
        "query_func": "query_score",
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
    #接受基本操作对象
    def __init__(self, root: tk.Tk, content_frame: tk.Frame):
        self.root = root
        self.content_frame = content_frame

    
    #把Label改为Button，并绑定点击事件
    def create_Button(self, button : tk.Label, reaction):
        button.bind("<Button-1>", lambda event: reaction())
        button.bind("<Enter>", lambda event: button.config(bg=COLORS["sidebar_active"]))
        button.bind("<Leave>", lambda event: button.config(bg=COLORS["sidebar_bg"]))

    # 创建查询数据界面
    def build_operate_page(self):
        # 清空内容区
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
        # 创建查询数据界面
        operate_label = tk.Label(self.content_frame, text="查询数据", bg=COLORS["content_bg"], fg=COLORS["Level1fg"], font=("PingFang SC", 20))
        operate_label.grid(row=0,column=0,padx=10,pady=10)
    
        tk.Label(self.content_frame,text="查询类型：", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=1,column=0,padx=5,pady=5)
        # state="readonly"  ：禁止直接在“查询类型”框里输入文字（否则 get() 返回的是输入的文字）
        # command=...      ：tkinter 在主线程同步回调，选完立即生效，取代原来的线程+队列+100ms 轮询
        self.C_target = ctk.CTkComboBox(
            self.content_frame,
            values=list(SEARCH_CONFIG.keys()),
            border_width=0,
            state="readonly",
            command=self._on_target_change,
        )
        self.C_target.grid(row=1,column=1)

        # CTkComboBox 刚创建时输入框是空的（get() 返回 ""），这里给一个明确的默认类型，
        # 否则进页面时不会有默认输入表单
        self.C_target.set("学生")
        # 进入页面时先挂上默认类型的输入表单
        self._switch_form(self.C_target.get())

    # ------------------------------------------------------------------
    # 查询类型切换：直接在主线程重建表单
    # ------------------------------------------------------------------
    def _on_target_change(self, target):
        """下拉框选择变化时由 tkinter 在主线程回调。"""
        self._switch_form(target)

    def _switch_form(self, target):
        """清掉旧的输入表单和结果区，挂上当前类型的输入表单。"""
        # 结果区若存在一并清掉（它的 grid row 同样 >= 2）
        if hasattr(self, "_result_container"):
            if self._result_container.winfo_exists():
                self._result_container.destroy()
            del self._result_container

        # 清空内容区中 row >= 2 的控件（也就是输入表单）
        for child in list(self.content_frame.winfo_children()):
            grid_info = child.grid_info()
            if grid_info and grid_info.get("row", 0) >= 2:
                child.destroy()

        if target in SEARCH_CONFIG:
            self.pack_button(target)

    def search(self, target):
        """
        统一查询入口。
        target: "学生" / "考试" / "成绩"
        """
        config = SEARCH_CONFIG[target]

        # ---- 1. 读输入 ----
        values = []
        for field in config["input_fields"]:
            entry = getattr(self, f"E_{field}")
            values.append(entry.get())

        print(f"查询条件 ({target}): " + ", ".join(
            f"{k}={v}" for k, v in zip(config["input_fields"], values)
        ))

        # ---- 2. 调数据库 ----
        query_func = getattr(db_controller, config["query_func"])
        results = query_func(*values)
        print(f"查询结果: {len(results)} 条")

        # ---- 3. 渲染 ----
        self._render_result(results, config)

    # ------------------------------------------------------------------
    # 函数二：通用结果表格渲染
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # 画面模版：表格样式 + “卡片 + 表格 + 滚动条”结构
    # 查询结果页和“添加/删除”弹窗共用这一套，保证两个界面长得一致
    # ------------------------------------------------------------------
    def _apply_table_style(self, config):
        """表格、表头、滚动条的 ttk 样式（全局样式，配置一次即可复用）"""
        style = ttk.Style()
        # theme_use 是全局操作，会把所有 ttk 控件样式重建一遍，
        # 只在第一次设置，避免每次渲染都全应用重绘/闪烁
        if not getattr(self, "_ttk_theme_ready", False):
            style.theme_use("clam")
            self._ttk_theme_ready = True

        # 表格主体
        style.configure(
            "DS.Treeview",
            background=COLORS[config["row_bg"]],
            foreground=COLORS["Level1fg"],
            fieldbackground=COLORS[config["row_bg"]],
            rowheight=42,
            borderwidth=0,
            relief="flat",
            font=("PingFang SC", 12),
        )

        # 表头
        style.configure(
            "DS.Treeview.Heading",
            background=COLORS[config["heading_bg"]],
            foreground=COLORS[config["heading_fg"]],
            font=("PingFang SC", 11),
            borderwidth=0,
            relief="flat",
            padding=(14, 14),
        )
        style.map(
            "DS.Treeview.Heading",
            background=[("active", COLORS[config["heading_act_bg"]])],
            foreground=[("active", COLORS[config["heading_act_fg"]])],
        )

        # 选中行
        style.map(
            "DS.Treeview",
            background=[("selected", COLORS[config["selected_bg"]])],
            foreground=[("selected", COLORS[config["selected_fg"]])],
        )

        # 去掉 Treeview 外框
        style.layout("DS.Treeview", [
            ("DS.Treeview.treearea", {"sticky": "nswe"})
        ])

        # 滚动条
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

    def _build_table_card(self, parent, config, height=10, h_scroll=None):
        """按模版创建“卡片 + 表格 + 滚动条”，返回 (卡片, 表格)。

        h_scroll 为 None 时取 config["h_scroll"]；列数多的表请传 True。
        """
        if h_scroll is None:
            h_scroll = config.get("h_scroll", False)

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
            tree.column(col, anchor="w", width=w, minwidth=70, stretch=True)

        # 斑马纹 / 空态
        tree.tag_configure("oddrow",  background="#211F1F")
        tree.tag_configure("evenrow", background="#514C4C")
        tree.tag_configure("empty",   foreground=COLORS["Level2fg"])

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

    def _render_result(self, results, config):
        """在原界面内渲染结果表格（不新建窗口、不清空输入框）"""

        # ---- 1. 销毁上一次结果区，输入框保留 ----
        if hasattr(self, "_result_container") and self._result_container.winfo_exists():
            self._result_container.destroy()

        # ---- 2. 创建结果容器 ----
        row = config["row"]
        self._result_container = tk.Frame(self.content_frame, bg=COLORS["content_bg"])
        self._result_container.grid(
            row=row, column=0, columnspan=4,
            sticky="nsew", padx=5, pady=(24, 5),
        )
        self.content_frame.grid_rowconfigure(row, weight=1)
        for c in range(4):
            self.content_frame.grid_columnconfigure(c, weight=1)

        # ---------- 3. ttk 样式（与“添加/删除”弹窗共用同一套模版）----------
        self._apply_table_style(config)

        # ---------- 4. 顶部标题行 ----------
        header = tk.Frame(self._result_container, bg=COLORS["content_bg"])
        header.pack(fill="x", pady=(0, 8))

        tk.Label(
            header, text=config["title"],
            bg=COLORS["content_bg"], fg=COLORS["Level1fg"],
            font=("PingFang SC", 18, "bold"),
        ).pack(side="left")

        count_text = f"共 {len(results)} 条记录" if results else "无匹配记录"
        tk.Label(
            header, text=count_text,
            bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
            font=("PingFang SC", 12),
        ).pack(side="right", pady=(6, 0))

        tk.Label(
            self._result_container, text=config["subtitle"],
            bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
            font=("PingFang SC", 11),
        ).pack(anchor="w", pady=(0, 10))

        # ---------- 5~7. 卡片 + 表格 + 滚动条（统一模版）----------
        card, tree = self._build_table_card(self._result_container, config, height=10)
        card.pack(fill="both", expand=True)

        if results:
            for i, r in enumerate(results):
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                tree.insert("", "end", values=r, tags=(tag,))
        else:
            tree.insert("", "end", values=("—",) * len(config["columns"]),
                        tags=("empty",))

        # ---------- 8. 底部按钮区 ----------
        footer = tk.Frame(self._result_container, bg=COLORS["content_bg"])
        footer.pack(fill="x", pady=(12, 0))

        # 注意：macOS 上 tk.Button 的 bg 会被系统忽略（永远画成原生灰按钮，颜色调了也没用），
        # 所以这里和本文件其它地方一样，用 tk.Label + <Button-1> 绑定来做按钮，颜色才真正生效。
        # 配色分层：主按钮 = accent，次按钮 / 图标按钮 = btn_bg，只有深浅不同。
        def make_btn(parent, text, cmd, *, bg, hover_bg, fg, font, padx, pady, border=None):
            btn = tk.Label(
                parent, text=text, bg=bg, fg=fg, font=font,
                padx=padx, pady=pady, cursor="hand2", bd=0,
                highlightthickness=1 if border else 0,
                highlightbackground=border or bg,
                highlightcolor=border or bg,
            )
            btn.bind("<Button-1>", lambda e: cmd())
            btn.bind("<Enter>", lambda e: btn.configure(bg=hover_bg))
            btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
            return btn

        # 关闭（主按钮，右侧）
        def close_result():
            if hasattr(self, "_result_container") and self._result_container.winfo_exists():
                self._result_container.destroy()
                del self._result_container

        # 导出（次按钮，右侧）
        def export_result():
            filepath = filedialog.asksaveasfilename(
            title="保存文件",
            defaultextension=".xlsx",
            initialfile="未命名.xlsx",
            filetypes=[
                ("Excel 文件", "*.xlsx"),
                ("所有文件", "*.*"),
            ],
        )
            if not filepath:
                print("用户取消了保存")
                return
            print(f"选择的保存路径: {filepath}")
            export_to_excel(
            headers=[text for text, _ in config["headers"].values()],
                rows=results,
                filepath=filepath,
                sheet_name="查询结果",
                title="查询结果导出",
            )

        # 增加/删除：弹窗，套用查询结果页的同一套画面模版
        def add_entry():
            content = config["content"]
            win = tk.Toplevel(self.root)
            win.title(f"添加{content}")
            win.configure(bg=COLORS["content_bg"])
            win.geometry("880x660")
            win.minsize(640, 480)
            win.transient(self.root)

            # 表格 / 滚动条样式与查询结果页完全一致（同一套模版）
            self._apply_table_style(config)

            # ---------- 标题行（与结果页同一排版）----------
            header = tk.Frame(win, bg=COLORS["content_bg"])
            header.pack(fill="x", padx=16, pady=(14, 6))
            tk.Label(
                header, text=f"添加{content}",
                bg=COLORS["content_bg"], fg=COLORS["Level1fg"],
                font=("PingFang SC", 18, "bold"),
            ).pack(side="left")
            count_label = tk.Label(
                header, text="共 0 条待提交",
                bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
                font=("PingFang SC", 12),
            )
            count_label.pack(side="right", pady=(6, 0))

            tk.Label(
                win, text="填好下面各项后点“确认”，数据会先进入待提交列表",
                bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
                font=("PingFang SC", 11),
            ).pack(anchor="w", padx=16)

            # ---------- 表单卡片 ----------
            form_card = tk.Frame(
                win, bg=COLORS["content_bg"],
                highlightbackground=COLORS["border"],
                highlightthickness=1, bd=0,
            )
            form_card.pack(fill="x", padx=16, pady=(10, 0))
            form = tk.Frame(form_card, bg=COLORS["content_bg"])
            form.pack(fill="x", padx=14, pady=12)
            form.grid_columnconfigure(1, weight=1)
            form.grid_columnconfigure(3, weight=1)

            entries = {}

            def add_field(r, c, text, key):
                tk.Label(
                    form, text=text, bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
                    font=("PingFang SC", 13),
                ).grid(row=r, column=c, padx=(0, 6), pady=6, sticky="e")
                entry = tk.Entry(form, font=("PingFang SC", 12))
                entry.grid(row=r, column=c + 1, padx=(0, 20), pady=6, sticky="ew")
                entries[key] = entry
                return entry

            if content == "学生":
                add_field(0, 0, "编号", "id")
                add_field(0, 2, "姓名", "name")
                add_field(1, 0, "班级", "class")
                add_field(1, 2, "年级", "grade")
                add_field(2, 0, "电话", "telephonenum")
                add_field(2, 2, "邮箱", "email")

            # ---------- 待提交列表：卡片 + 表格 + 双向滚动条 ----------
            card, tree_add = self._build_table_card(win, config, height=6, h_scroll=True)
            card.pack(fill="both", expand=True, padx=16, pady=(12, 0))

            # ---------- 底部按钮（与结果页同一套按钮模版）----------
            footer = tk.Frame(win, bg=COLORS["content_bg"])
            footer.pack(fill="x", padx=16, pady=12)

            hint = tk.Label(
                footer, text="编号和姓名不能为空",
                bg=COLORS["content_bg"], fg=COLORS["warn_fg"], font=("PingFang SC", 11),
            )
            hint.pack(side="left")

            add_list = []

            def submit_entry():
                if content == "学生":
                    values = [
                        entries["id"].get().strip(),
                        entries["name"].get().strip(),
                        entries["class"].get().strip(),
                        entries["grade"].get().strip(),
                        entries["telephonenum"].get().strip(),
                        entries["email"].get().strip(),
                    ]
                    if not values[0] or not values[1]:
                        hint.configure(text="编号和姓名不能为空", fg=COLORS["warn_fg"])
                        return
                    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    new_entry = values + [now, now]
                else:
                    return

                add_list.append(new_entry)
                tree_add.insert(
                    "", "end", values=new_entry,
                    tags=("evenrow" if len(add_list) % 2 == 0 else "oddrow",),
                )
                tree_add.see(tree_add.get_children()[-1])   # 表格自动滚到最后一行
                count_label.configure(text=f"共 {len(add_list)} 条待提交")
                hint.configure(text=f"已加入：{new_entry[0]} {new_entry[1]}", fg=COLORS["Level2fg"])
                for entry in entries.values():
                    entry.delete(0, "end")
                if "id" in entries:
                    entries["id"].focus_set()
                print(f"添加 {content}：{new_entry}")

            confirm_btn = make_btn(
                footer, "确认", submit_entry,
                bg=COLORS["accent"], hover_bg=COLORS["accent_hover"], fg=COLORS["on_accent_fg"],
                font=("PingFang SC", 12), padx=28, pady=10,
            )
            confirm_btn.pack(side="right")

            cancel_btn = make_btn(
                footer, "关闭", win.destroy,
                bg=COLORS["btn_bg"], hover_bg=COLORS["btn_hover"], fg=COLORS["btn_fg"],
                font=("PingFang SC", 12), padx=24, pady=9, border=COLORS["btn_border"],
            )
            cancel_btn.pack(side="right", padx=(0, 12))

            if entries:
                next(iter(entries.values())).focus_set()

            win.grab_set()  # 阻止与主窗口的交互

        # ---------- 9. 底部按钮布局 ----------
        close_btn = make_btn(
            footer, "关闭", close_result,
            bg=COLORS["accent"], hover_bg=COLORS["accent_hover"], fg=COLORS["on_accent_fg"],
            font=("PingFang SC", 12), padx=28, pady=10,
        )
        close_btn.pack(side="right")
        
        export_btn = make_btn(
            footer, "导出", export_result,
            bg=COLORS["btn_bg"], hover_bg=COLORS["btn_hover"], fg=COLORS["btn_fg"],
            font=("PingFang SC", 12), padx=24, pady=9, border=COLORS["btn_border"],
        )
        export_btn.pack(side="right", padx=(0, 12))

        # + / − 小按钮（左侧），与次按钮同一底色，只做小一号
        add_btn = make_btn(
            footer, "＋", add_entry,
            bg=COLORS["btn_bg"], hover_bg=COLORS["btn_hover"], fg=COLORS["btn_fg"],
            font=("PingFang SC", 14, "bold"), padx=8, pady=3,
        )
        add_btn.pack(side="left")

        del_btn = make_btn(
            footer, "−", lambda: print(f"删除 {config['title']}"),
            bg=COLORS["btn_bg"], hover_bg=COLORS["btn_hover"], fg=COLORS["btn_fg"],
            font=("PingFang SC", 14, "bold"), padx=8, pady=3,
        )
        del_btn.pack(side="left", padx=(8, 0))

    # ------------------------------------------------------------------
    # 输入区布局（保留原样，仅修改确认按钮的绑定）
    # ------------------------------------------------------------------
                       
    def pack_button(self, target):
        if target == "学生":
                tk.Label(self.content_frame, text="编号", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=2, column=0, padx=5, pady=5)
                self.E_id = tk.Entry(self.content_frame)
                self.E_id.grid(row=2, column=1, padx=5, pady=5)

                tk.Label(self.content_frame, text="姓名", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=2, column=2, padx=5, pady=5)
                self.E_name = tk.Entry(self.content_frame)
                self.E_name.grid(row=2, column=3, padx=5, pady=5)

                tk.Label(self.content_frame, text="班级", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=3, column=0, padx=5, pady=5)
                self.E_class = tk.Entry(self.content_frame)
                self.E_class.grid(row=3, column=1, padx=5, pady=5)

                tk.Label(self.content_frame, text="年级", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=3, column=2, padx=5, pady=5)
                self.E_grade = tk.Entry(self.content_frame)
                self.E_grade.grid(row=3, column=3, padx=5, pady=5)

                tk.Label(self.content_frame, text="电话", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=4, column=0, padx=5, pady=5)
                self.E_telephonenum = tk.Entry(self.content_frame)
                self.E_telephonenum.grid(row=4, column=1, padx=5, pady=5)

                tk.Label(self.content_frame, text="邮箱", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=4, column=2, padx=5, pady=5)
                self.E_email = tk.Entry(self.content_frame)
                self.E_email.grid(row=4, column=3, padx=5, pady=5)

                tk.Label(self.content_frame, text="创建时间", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=5, column=0, padx=5, pady=5)
                self.E_createtime = tk.Entry(self.content_frame)
                self.E_createtime.grid(row=5, column=1, padx=5, pady=5)

                tk.Label(self.content_frame, text="修改时间", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=5, column=2, padx=5, pady=5)
                self.E_changetime = tk.Entry(self.content_frame)
                self.E_changetime.grid(row=5, column=3, padx=5, pady=5)

                B_confirm = tk.Label(self.content_frame, text="确认", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16))
                B_confirm.grid(row=6, column=0, padx=5, pady=5)
                self.create_Button(B_confirm, lambda: self.search("学生"))

        if target == "考试":
                tk.Label(self.content_frame, text="考试编号", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=2, column=0, padx=5, pady=5)
                self.E_exam_id = tk.Entry(self.content_frame)
                self.E_exam_id.grid(row=2, column=1, padx=5, pady=5)

                tk.Label(self.content_frame, text="考试名称", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=2, column=2, padx=5, pady=5)
                self.E_exam_name = tk.Entry(self.content_frame)
                self.E_exam_name.grid(row=2, column=3, padx=5, pady=5)

                tk.Label(self.content_frame, text="考试时间", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=3, column=0, padx=5, pady=5)
                self.E_exam_time = tk.Entry(self.content_frame)
                self.E_exam_time.grid(row=3, column=1, padx=5, pady=5)

                tk.Label(self.content_frame, text="创建时间", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=3, column=2, padx=5, pady=5)
                self.E_createtime = tk.Entry(self.content_frame)
                self.E_createtime.grid(row=3, column=3, padx=5, pady=5)

                tk.Label(self.content_frame, text="修改时间", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=4, column=0, padx=5, pady=5)
                self.E_changetime = tk.Entry(self.content_frame)
                self.E_changetime.grid(row=4, column=1, padx=5, pady=5)

                B_confirm = tk.Label(self.content_frame, text="确认", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16))
                B_confirm.grid(row=5, column=0, padx=5, pady=5)
                self.create_Button(B_confirm, lambda: self.search("考试"))

        if target == "成绩":
                tk.Label(self.content_frame, text="学生编号", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=2, column=0, padx=5, pady=5)
                self.E_student_id = tk.Entry(self.content_frame)
                self.E_student_id.grid(row=2, column=1, padx=5, pady=5)

                tk.Label(self.content_frame, text="考试编号", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=2, column=2, padx=5, pady=5)
                self.E_exam_id = tk.Entry(self.content_frame)
                self.E_exam_id.grid(row=2, column=3, padx=5, pady=5)

                tk.Label(self.content_frame, text="科目", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=3, column=0, padx=5, pady=5)
                self.E_subject = tk.Entry(self.content_frame)
                self.E_subject.grid(row=3, column=1, padx=5, pady=5)

                tk.Label(self.content_frame, text="初始成绩", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=3, column=2, padx=5, pady=5)
                self.E_initialscore = tk.Entry(self.content_frame)
                self.E_initialscore.grid(row=3, column=3, padx=5, pady=5)

                tk.Label(self.content_frame, text="成绩", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=4, column=0, padx=5, pady=5)
                self.E_score = tk.Entry(self.content_frame)
                self.E_score.grid(row=4, column=1, padx=5, pady=5)

                tk.Label(self.content_frame, text="排名", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=4, column=2, padx=5, pady=5)
                self.E_rank = tk.Entry(self.content_frame)
                self.E_rank.grid(row=4, column=3, padx=5, pady=5)

                tk.Label(self.content_frame, text="总人数", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=5, column=0, padx=5, pady=5)
                self.E_headcount = tk.Entry(self.content_frame)
                self.E_headcount.grid(row=5, column=1, padx=5, pady=5)

                tk.Label(self.content_frame, text="创建时间", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=5, column=2, padx=5, pady=5)
                self.E_createtime = tk.Entry(self.content_frame)
                self.E_createtime.grid(row=5, column=3, padx=5, pady=5)

                tk.Label(self.content_frame, text="修改时间", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=6, column=0, padx=5, pady=5)
                self.E_changetime = tk.Entry(self.content_frame)
                self.E_changetime.grid(row=6, column=1, padx=5, pady=5)

                B_confirm = tk.Label(self.content_frame, text="确认", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16))
                B_confirm.grid(row=7, column=0, padx=5, pady=5)
                self.create_Button(B_confirm, lambda: self.search("成绩"))