import tkinter as tk
import tkinter.ttk as ttk
import queue, threading, time 
import customtkinter as ctk
from tkinter import filedialog
from Controller.DataBaseController import DataBaseController
from Utils.excel_exporter import export_to_excel

# 颜色主题
COLORS = {
    "sidebar_bg": "#1e1f23",      # 深蓝灰侧边栏
    "Level1fg": "#cbd5e1",        # 一级文字灰
    "Level2fg": "#a1a1aa",        # 二级文字灰
    "sidebar_active": "#334155",  # 鼠标悬停/选中背景
    "accent": "#4f6af5",          # 亮蓝强调色
    "content_bg": "#0d0d0d",      # 内容区背景浅灰
    "card_bg": "#ffffff",         # 卡片纯白
    "text_primary": "#0f172a",    # 深色主文字
    "border": "#2c2c3a"           # 分割线颜色
}
db_controller = DataBaseController()

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
        C_target = ctk.CTkComboBox(self.content_frame,values=["学生","考试","成绩"],border_width=0)
        C_target.grid(row=1,column=1)
    
        #读取队列中消息并完成任务
        def practice_quene():
            try:
                data = msg_queue.get_nowait()

                # 清空内容区中 row 大于 2 的控件
                for child in list(self.content_frame.winfo_children()):
                    # 获取该控件的 grid 信息（字典）
                    grid_info = child.grid_info()
                    # 如果控件确实是用 grid 布局的，且 column 值存在且小于阈值
                    if grid_info and 'row' in grid_info:
                        if grid_info['row'] >= 2 :
                            child.destroy()  # 彻底删除控件

                if data == "学生":
                    self.pack_button("学生")
                if data == "考试":
                    self.pack_button("考试")
                if data == "成绩":
                    self.pack_button("成绩")
    
            except queue.Empty:
                pass  # 如果队列为空，则不做任何操作
            self.root.after(100, practice_quene)  # 每10毫秒检查一次队列
                
        #更新队列
        def update_queue():
            target = None
            nonlocal msg_queue, C_target
            while True:
                if target != C_target.get():
                    target = C_target.get()
                    msg_queue.put(target)
                    time.sleep(0.01)
    
        msg_queue = queue.Queue()
        threading.Thread(target=update_queue,daemon = True).start()
            
        practice_quene()

    # 查找学生数据
    def search_students(self):
        COLORS = {
    "sidebar_bg": "#1e1f23",      # 深蓝灰侧边栏
    "Level1fg": "#cbd5e1",        # 一级文字灰
    "Level2fg": "#a1a1aa",        # 二级文字灰
    "sidebar_active": "#334155",  # 鼠标悬停/选中背景
    "accent": "#4f6af5",          # 亮蓝强调色
    "content_bg": "#0d0d0d",      # 内容区背景浅灰
    "card_bg": "#ffffff",         # 卡片纯白
    "text_primary": "#0f172a",    # 深色主文字
    "border": "#2c2c3a"           # 分割线颜色
}
        # ---------- 读取输入 ----------
        id_ = self.E_id.get()
        name = self.E_name.get()
        class_name = self.E_class.get()
        grade = self.E_grade.get()
        telephonenum = self.E_telephonenum.get()
        email = self.E_email.get()
        createtime = self.E_createtime.get()
        changetime = self.E_changetime.get()

        print(f"查询条件: 编号={id_}, 姓名={name}, 班级={class_name}, 年级={grade}, "
            f"电话={telephonenum}, 邮箱={email}, 创建时间={createtime}, 修改时间={changetime}")

        results = db_controller.query_student(
            id_, name, class_name, grade,
            telephonenum, email, createtime, changetime
        )
        print(f"查询结果: {results}")

        # ==================================================================
        # 在原界面内生成结果区（不新建窗口、不清空已有组件）
        # ==================================================================

        # 1) 如果上一次查询已经生成过结果区，只销毁它，输入框保持不动
        if hasattr(self, "_result_container") and self._result_container.winfo_exists():
            self._result_container.destroy()

        # 2) 创建新的结果容器，挂在 content_frame 中
        #    行号 20 是为避开输入框（row 2~10）。如果你有其他组件占用了 row 20，请调整此处行号
        self._result_container = tk.Frame(self.content_frame, bg=COLORS["content_bg"])
        self._result_container.grid(
            row=7, column=0, columnspan=4,
            sticky="nsew", padx=5, pady=(24, 5),
        )

        # 3) 让该行/列可伸缩，表格才能随窗口大小变化
        self.content_frame.grid_rowconfigure(7, weight=1)
        for _c in range(4):
            self.content_frame.grid_columnconfigure(_c, weight=1)

        # ---------- ttk 样式 ----------
        style = ttk.Style()
        style.theme_use("clam")

        # 表格主体
        style.configure(
            "DS.Treeview",
            background=COLORS["card_bg"],
            foreground=COLORS["Level1fg"],
            fieldbackground=COLORS["card_bg"],
            rowheight=42,
            borderwidth=0,
            relief="flat",
            font=("PingFang SC", 12),
        )

        # 表头
        style.configure(
            "DS.Treeview.Heading",
            background=COLORS["sidebar_bg"],
            foreground=COLORS["Level2fg"],
            font=("PingFang SC", 11),
            borderwidth=0,
            relief="flat",
            padding=(14, 14),
        )
        style.map(
            "DS.Treeview.Heading",
            background=[("active", COLORS["sidebar_active"])],
            foreground=[("active", COLORS["Level1fg"])],
        )

        # 选中行
        style.map(
            "DS.Treeview",
            background=[("selected", COLORS["accent"])],
            foreground=[("selected", "#c7d2fe")],
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

        # ---------- 顶部标题行 ----------
        header = tk.Frame(self._result_container, bg=COLORS["content_bg"])
        header.pack(fill="x", pady=(0, 8))

        tk.Label(
            header, text="查询结果",
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
            self._result_container,
            text="以下是符合筛选条件的全部数据",
            bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
            font=("PingFang SC", 11),
        ).pack(anchor="w", pady=(0, 10))

        # ---------- 卡片容器 ----------
        card = tk.Frame(
            self._result_container,
            bg=COLORS["card_bg"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            bd=0,
        )
        card.pack(fill="both", expand=True)

        table_frame = tk.Frame(card, bg=COLORS["card_bg"])
        table_frame.pack(fill="both", expand=True, padx=1, pady=1)

        columns = ("id", "name", "class_name", "grade",
                "telephonenum", "email", "createtime", "changetime")

        tree = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            style="DS.Treeview", height=10,
        )

        headers = {
            "id":            ("编号",     90),
            "name":          ("姓名",     100),
            "class_name":    ("班级",     110),
            "grade":         ("年级",     90),
            "telephonenum":  ("电话",     140),
            "email":         ("邮箱",     200),
            "createtime":    ("创建时间", 160),
            "changetime":    ("修改时间", 160),
        }
        for col, (text, w) in headers.items():
            tree.heading(col, text=text, anchor="w")
            tree.column(col, anchor="w", width=w, minwidth=70, stretch=True)

        tree.tag_configure("oddrow",  background=COLORS["card_bg"])
        tree.tag_configure("evenrow", background="#2f3037")
        tree.tag_configure("empty",   foreground=COLORS["Level2fg"])

        if results:
            for i, row in enumerate(results):
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                tree.insert("", "end", values=row, tags=(tag,))
        else:
            tree.insert("", "end", values=("—",) * len(columns), tags=("empty",))

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical",
            command=tree.yview, style="DS.Vertical.TScrollbar",
        )
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---------- 底部按钮区 ----------
        footer = tk.Frame(self._result_container, bg=COLORS["content_bg"])
        footer.pack(fill="x", pady=(12, 0))

        # 主按钮：关闭结果区（只删除结果，不动输入框）
        def close_result():
            if hasattr(self, "_result_container") and self._result_container.winfo_exists():
                self._result_container.destroy()
                del self._result_container

        close_btn = tk.Button(
            footer, text="关闭",
            command=close_result,
            bg=COLORS["accent"], fg="#ffffff",
            activebackground=COLORS["accent"], activeforeground="#ffffff",
            font=("PingFang SC", 12),
            relief="flat", borderwidth=0,
            padx=28, pady=10,
            cursor="hand2",
        )
        close_btn.pack(side="right")

        def on_enter(e): close_btn.configure(bg=COLORS["accent"])
        def on_leave(e): close_btn.configure(bg=COLORS["accent"])
        close_btn.bind("<Enter>", on_enter)
        close_btn.bind("<Leave>", on_leave)

        # 次按钮：导出
        def export_placeholder():
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
                headers=[text for text, _ in headers.values()],
                rows=results,
                filepath=filepath,
                sheet_name="查询结果",
                title="查询结果导出",
            )

        export_btn = tk.Button(
            footer, text="导出",
            command=export_placeholder,
            bg=COLORS["content_bg"], fg=COLORS["Level1fg"],
            activebackground=COLORS["sidebar_active"], activeforeground=COLORS["Level1fg"],
            font=("PingFang SC", 12),
            relief="flat", borderwidth=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            padx=24, pady=9,
            cursor="hand2",
        )
        export_btn.pack(side="right", padx=(0, 12))

        footer = tk.Frame(self._result_container, bg=COLORS["content_bg"])
        footer.pack(fill="x", pady=(12, 0))

        # ——— 左侧：+ / − 按钮 ———
        def make_small_btn(parent, text, cmd, hover_bg=None):
            """统一风格的小按钮"""
            btn = tk.Button(
                parent, text=text, command=cmd,
                bg=COLORS["sidebar_active"], fg=COLORS["Level1fg"],
                activebackground=COLORS["accent"], activeforeground="#ffffff",
                font=("PingFang SC", 14, "bold"),
                relief="flat", borderwidth=0,
                width=2, height=1,
                cursor="hand2",
            )
            return btn

        add_btn = make_small_btn(footer, "＋", lambda: print("添加成绩"))
        add_btn.pack(side="left")

        del_btn = make_small_btn(footer, "−", lambda: print("删除成绩"))
        del_btn.pack(side="left", padx=(8, 0))

       

    # 查找考试数据
    def search_exams(self):
        COLORS = {
    "sidebar_bg": "#1e1f23",      # 深蓝灰侧边栏
    "Level1fg": "#cbd5e1",        # 一级文字灰
    "Level2fg": "#a1a1aa",        # 二级文字灰
    "sidebar_active": "#334155",  # 鼠标悬停/选中背景
    "accent": "#4f6af5",          # 亮蓝强调色
    "content_bg": "#0d0d0d",      # 内容区背景浅灰
    "card_bg": "#ffffff",         # 卡片纯白
    "text_primary": "#0f172a",    # 深色主文字
    "border": "#2c2c3a"           # 分割线颜色
}
        # ---------- 读取输入 ----------
        exam_id = self.E_exam_id.get()
        exam_name = self.E_exam_name.get()
        exam_time = self.E_exam_time.get()
        createtime = self.E_createtime.get()
        changetime = self.E_changetime.get()

        print(f"查询条件: 考试编号={exam_id}, 考试名称={exam_name}, "
            f"考试时间={exam_time}, 创建时间={createtime}, 修改时间={changetime}")

        results = db_controller.query_exam(
            exam_id, exam_name, exam_time, createtime, changetime
        )

        # ==================================================================
        # 在原界面内生成结果区（不新建窗口、不清空已有组件）
        # ==================================================================

        # 1) 如果上一次查询已经生成过结果区，只销毁它，输入框保持不动
        if hasattr(self, "_result_container") and self._result_container.winfo_exists():
            self._result_container.destroy()

        # 2) 创建新的结果容器，挂在 content_frame 中
        #    行号 20 是为避开输入框（row 2~10）。如果考试输入框占用了不同行，请调整
        self._result_container = tk.Frame(self.content_frame, bg=COLORS["content_bg"])
        self._result_container.grid(
            row=6, column=0, columnspan=4,
            sticky="nsew", padx=5, pady=(24, 5),
        )

        # 3) 让该行/列可伸缩，表格才能随窗口大小变化
        self.content_frame.grid_rowconfigure(6, weight=1)
        for _c in range(4):
            self.content_frame.grid_columnconfigure(_c, weight=1)

        # ---------- ttk 样式 ----------
        style = ttk.Style()
        style.theme_use("clam")

        # 表格主体
        style.configure(
            "DS.Treeview",
            background=COLORS["sidebar_bg"],
            foreground=COLORS["Level1fg"],
            fieldbackground=COLORS["sidebar_bg"],
            rowheight=42,
            borderwidth=0,
            relief="flat",
            font=("PingFang SC", 12),
        )

        # 表头
        style.configure(
            "DS.Treeview.Heading",
            background=COLORS["sidebar_active"],
            foreground=COLORS["Level1fg"],
            font=("PingFang SC", 11),
            borderwidth=0,
            relief="flat",
            padding=(14, 14),
        )
        style.map(
            "DS.Treeview.Heading",
            background=[("active", COLORS["accent"])],
            foreground=[("active", COLORS["card_bg"])],
        )

        # 选中行
        style.map(
            "DS.Treeview",
            background=[("selected", COLORS["accent"])],
            foreground=[("selected", COLORS["card_bg"])],
        )

        # 去掉 Treeview 外框
        style.layout("DS.Treeview", [
            ("DS.Treeview.treearea", {"sticky": "nswe"})
        ])

        # 滚动条
        style.configure(
            "DS.Vertical.TScrollbar",
            background=COLORS["sidebar_active"],
            troughcolor=COLORS["content_bg"],
            bordercolor=COLORS["content_bg"],
            arrowcolor=COLORS["Level2fg"],
            borderwidth=0,
            relief="flat",
            width=8,
        )
        style.map(
            "DS.Vertical.TScrollbar",
            background=[("active", COLORS["accent"])],
        )

        # ---------- 顶部标题行 ----------
        header = tk.Frame(self._result_container, bg=COLORS["content_bg"])
        header.pack(fill="x", pady=(0, 8))

        tk.Label(
            header, text="考试查询结果",
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
            self._result_container,
            text="以下是符合筛选条件的全部考试数据",
            bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
            font=("PingFang SC", 11),
        ).pack(anchor="w", pady=(0, 10))

        # ---------- 卡片容器 ----------
        card = tk.Frame(
            self._result_container,
            bg=COLORS["sidebar_bg"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            bd=0,
        )
        card.pack(fill="both", expand=True)

        table_frame = tk.Frame(card, bg=COLORS["sidebar_bg"])
        table_frame.pack(fill="both", expand=True, padx=1, pady=1)

        # ---------- 表格列 ----------
        columns = ("exam_id", "exam_name", "exam_time", "createtime", "changetime")

        tree = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            style="DS.Treeview", height=10,
        )

        headers = {
            "exam_id":     ("考试编号", 130),
            "exam_name":   ("考试名称", 220),
            "exam_time":   ("考试时间", 180),
            "createtime":  ("创建时间", 180),
            "changetime":  ("修改时间", 180),
        }
        for col, (text, w) in headers.items():
            tree.heading(col, text=text, anchor="w")
            tree.column(col, anchor="w", width=w, minwidth=90, stretch=True)

        # 斑马纹
        tree.tag_configure("oddrow",  background=COLORS["sidebar_bg"])    # 基础深灰
        tree.tag_configure("evenrow", background=COLORS["content_bg"])    # 更暗一档
        tree.tag_configure("empty",   foreground=COLORS["Level2fg"])      # 空态

        if results:
            for i, row in enumerate(results):
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                tree.insert("", "end", values=row, tags=(tag,))
        else:
            tree.insert("", "end", values=("—",) * len(columns), tags=("empty",))

        # 滚动条 + 表格布局
        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical",
            command=tree.yview, style="DS.Vertical.TScrollbar",
        )
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---------- 底部按钮区 ----------
        footer = tk.Frame(self._result_container, bg=COLORS["content_bg"])
        footer.pack(fill="x", pady=(12, 0))

        # 主按钮：关闭结果区（只删除结果，不动输入框）
        def close_result():
            if hasattr(self, "_result_container") and self._result_container.winfo_exists():
                self._result_container.destroy()
                del self._result_container

        close_btn = tk.Button(
            footer, text="关闭",
            command=close_result,
            bg=COLORS["accent"], fg=COLORS["card_bg"],
            activebackground=COLORS["sidebar_active"], activeforeground=COLORS["Level1fg"],
            font=("PingFang SC", 12),
            relief="flat", borderwidth=0,
            padx=28, pady=10,
            cursor="hand2",
        )
        close_btn.pack(side="right")

        def on_enter(e): close_btn.configure(bg=COLORS["sidebar_active"])
        def on_leave(e): close_btn.configure(bg=COLORS["accent"])
        close_btn.bind("<Enter>", on_enter)
        close_btn.bind("<Leave>", on_leave)

        # 次按钮：导出
        def export_placeholder():
            """弹出系统标准的"保存文件"对话框"""
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
                headers=[text for text, _ in headers.values()],
                rows=results,
                filepath=filepath,
                sheet_name="查询结果",
                title="查询结果导出",
            )

        export_btn = tk.Button(
            footer, text="导出",
            command=export_placeholder,
            bg=COLORS["content_bg"], fg=COLORS["Level1fg"],
            activebackground=COLORS["sidebar_active"], activeforeground=COLORS["Level1fg"],
            font=("PingFang SC", 12),
            relief="flat", borderwidth=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            padx=24, pady=9,
            cursor="hand2",
        )
        export_btn.pack(side="right", padx=(0, 12))

    #查询成绩
    def search_scores(self):
        COLORS = {
    "sidebar_bg": "#1e1f23",      # 深蓝灰侧边栏
    "Level1fg": "#cbd5e1",        # 一级文字灰
    "Level2fg": "#a1a1aa",        # 二级文字灰
    "sidebar_active": "#334155",  # 鼠标悬停/选中背景
    "accent": "#4f6af5",          # 亮蓝强调色
    "content_bg": "#0d0d0d",      # 内容区背景浅灰
    "card_bg": "#ffffff",         # 卡片纯白
    "text_primary": "#0f172a",    # 深色主文字
    "border": "#2c2c3a"           # 分割线颜色
}
        # ---------- 读取输入 ----------
        student_id   = self.E_student_id.get()
        exam_id      = self.E_exam_id.get()
        subject      = self.E_subject.get()
        initialscore = self.E_initialscore.get()
        score        = self.E_score.get()
        rank         = self.E_rank.get()
        headcount    = self.E_headcount.get()
        createtime   = self.E_createtime.get()
        changetime   = self.E_changetime.get()

        print(f"查询条件: 学号={student_id}, 考试编号={exam_id}, 科目={subject}, "
            f"初始分={initialscore}, 分数={score}, 排名={rank}, 总人数={headcount}, "
            f"创建时间={createtime}, 修改时间={changetime}")

        results = db_controller.query_score(
            student_id, exam_id, subject, initialscore, score,
            rank, headcount, createtime, changetime
        )

        # ==================================================================
        # 在原界面内生成结果区（不新建窗口、不清空已有组件）
        # ==================================================================

        # 1) 如果上一次查询已经生成过结果区，只销毁它，输入框保持不动
        if hasattr(self, "_result_container") and self._result_container.winfo_exists():
            self._result_container.destroy()

        # 2) 创建新的结果容器，挂在 content_frame 中
        #    行号 20 是为避开输入框（row 2~12）。如果成绩输入框占用了不同行，请调整
        self._result_container = tk.Frame(self.content_frame, bg=COLORS["content_bg"])
        self._result_container.grid(
            row=8, column=0, columnspan=4,
            sticky="nsew", padx=5, pady=(24, 5),
        )

        # 3) 让该行/列可伸缩，表格才能随窗口大小变化
        self.content_frame.grid_rowconfigure(8, weight=1)
        for _c in range(4):
            self.content_frame.grid_columnconfigure(_c, weight=1)

        # ---------- ttk 样式 ----------
        style = ttk.Style()
        style.theme_use("clam")

        # 表格主体
        style.configure(
            "DS.Treeview",
            background=COLORS["sidebar_bg"],
            foreground=COLORS["Level1fg"],
            fieldbackground=COLORS["sidebar_bg"],
            rowheight=42,
            borderwidth=0,
            relief="flat",
            font=("PingFang SC", 12),
        )

        # 表头
        style.configure(
            "DS.Treeview.Heading",
            background=COLORS["sidebar_active"],
            foreground=COLORS["Level1fg"],
            font=("PingFang SC", 11),
            borderwidth=0,
            relief="flat",
            padding=(12, 14),
        )
        style.map(
            "DS.Treeview.Heading",
            background=[("active", COLORS["accent"])],
            foreground=[("active", COLORS["card_bg"])],
        )

        # 选中行
        style.map(
            "DS.Treeview",
            background=[("selected", COLORS["accent"])],
            foreground=[("selected", COLORS["card_bg"])],
        )

        # 去掉 Treeview 外框
        style.layout("DS.Treeview", [
            ("DS.Treeview.treearea", {"sticky": "nswe"})
        ])

        # 滚动条
        style.configure(
            "DS.Vertical.TScrollbar",
            background=COLORS["sidebar_active"],
            troughcolor=COLORS["content_bg"],
            bordercolor=COLORS["content_bg"],
            arrowcolor=COLORS["Level2fg"],
            borderwidth=0,
            relief="flat",
            width=8,
        )
        style.map(
            "DS.Vertical.TScrollbar",
            background=[("active", COLORS["accent"])],
        )

        # ---------- 顶部标题行 ----------
        header = tk.Frame(self._result_container, bg=COLORS["content_bg"])
        header.pack(fill="x", pady=(0, 8))

        tk.Label(
            header, text="成绩查询结果",
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
            self._result_container,
            text="以下是符合筛选条件的全部成绩数据",
            bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
            font=("PingFang SC", 11),
        ).pack(anchor="w", pady=(0, 10))

        # ---------- 卡片容器 ----------
        card = tk.Frame(
            self._result_container,
            bg=COLORS["sidebar_bg"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            bd=0,
        )
        card.pack(fill="both", expand=True)

        table_frame = tk.Frame(card, bg=COLORS["sidebar_bg"])
        table_frame.pack(fill="both", expand=True, padx=1, pady=1)

        # 表格区用 grid 布局：左上表格 / 右上竖滚动条 / 左下横滚动条
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # ---------- 表格列 ----------
        columns = (
            "student_id", "exam_id", "subject",
            "initialscore", "score", "rank", "headcount",
            "createtime", "changetime",
        )

        tree = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            style="DS.Treeview", height=10,
        )

        headers = {
            "student_id":   ("学号",     100),
            "exam_id":      ("考试编号", 110),
            "subject":      ("科目",     100),
            "initialscore": ("初始分数", 100),
            "score":        ("分数",     90),
            "rank":         ("排名",     80),
            "headcount":    ("总人数",   90),
            "createtime":   ("创建时间", 160),
            "changetime":   ("修改时间", 160),
        }
        for col, (text, w) in headers.items():
            tree.heading(col, text=text, anchor="w")
            tree.column(col, anchor="w", width=w, minwidth=70, stretch=True)

        # 斑马纹
        tree.tag_configure("oddrow",  background=COLORS["sidebar_bg"])    # 基础深灰
        tree.tag_configure("evenrow", background=COLORS["content_bg"])    # 更暗一档
        tree.tag_configure("empty",   foreground=COLORS["Level2fg"])      # 空态

        if results:
            for i, row in enumerate(results):
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                tree.insert("", "end", values=row, tags=(tag,))
        else:
            tree.insert("", "end", values=("—",) * len(columns), tags=("empty",))

        # 垂直滚动条 + 横向滚动条
        v_scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical",
            command=tree.yview, style="DS.Vertical.TScrollbar",
        )
        h_scrollbar = ttk.Scrollbar(
            table_frame, orient="horizontal",
            command=tree.xview, style="DS.Vertical.TScrollbar",
        )
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # grid 布局：表格 (0,0)，竖条 (0,1)，横条 (1,0)
        tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        # ---------- 底部按钮区 ----------
        footer = tk.Frame(self._result_container, bg=COLORS["content_bg"])
        footer.pack(fill="x", pady=(12, 0))

        # 主按钮：关闭结果区（只删除结果，不动输入框）
        def close_result():
            if hasattr(self, "_result_container") and self._result_container.winfo_exists():
                self._result_container.destroy()
                del self._result_container

        close_btn = tk.Button(
            footer, text="关闭",
            command=close_result,
            bg=COLORS["accent"], fg=COLORS["card_bg"],
            activebackground=COLORS["sidebar_active"], activeforeground=COLORS["Level1fg"],
            font=("PingFang SC", 12),
            relief="flat", borderwidth=0,
            padx=28, pady=10,
            cursor="hand2",
        )
        close_btn.pack(side="right")

        def on_enter(e): close_btn.configure(bg=COLORS["sidebar_active"])
        def on_leave(e): close_btn.configure(bg=COLORS["accent"])
        close_btn.bind("<Enter>", on_enter)
        close_btn.bind("<Leave>", on_leave)

        # 次按钮：导出
        def export_placeholder():
            """弹出系统标准的"保存文件"对话框"""
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
                headers=[text for text, _ in headers.values()],
                rows=results,
                filepath=filepath,
                sheet_name="查询结果",
                title="查询结果导出",
            )

        export_btn = tk.Button(
            footer, text="导出",
            command=export_placeholder,
            bg=COLORS["content_bg"], fg=COLORS["Level1fg"],
            activebackground=COLORS["sidebar_active"], activeforeground=COLORS["Level1fg"],
            font=("PingFang SC", 12),
            relief="flat", borderwidth=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            padx=24, pady=9,
            cursor="hand2",
        )
        export_btn.pack(side="right", padx=(0, 12))
                       
        
    
    def pack_button(self,target):
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
            self.create_Button(B_confirm, lambda: self.search_students())

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
            self.create_Button(B_confirm, self.search_exams)

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
            self.create_Button(B_confirm, self.search_scores)