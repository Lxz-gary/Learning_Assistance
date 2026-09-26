import tkinter as tk
import tkinter.ttk as ttk
import queue, threading, time 
import customtkinter as ctk
from Controller.DataBaseController import DataBaseController

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

class QueryWindow:
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
    def build_query_page(self):
        # 清空内容区
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
        # 创建查询数据界面
        query_label = tk.Label(self.content_frame, text="查询数据", bg=COLORS["content_bg"], fg=COLORS["Level1fg"], font=("PingFang SC", 20))
        query_label.grid(row=0,column=0,padx=10,pady=10)
    
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
            self.root.after(100, practice_quene)  # 每100毫秒检查一次队列
                
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
            # —— 背景层 ——
            "sidebar_bg":      "#1a1b1e",   # 侧边栏：暖灰深色
            "content_bg":      "#212226",   # 内容区：比侧边栏稍亮，形成微妙层次
            "card_bg":         "#2a2b30",   # 卡片：柔和深灰（不再是纯白）

            # —— 文字层 ——
            "Level1fg":        "#e5e7eb",   # 一级文字：柔白
            "Level2fg":        "#9ca3af",   # 二级文字：中灰
            "text_primary":    "#f3f4f6",   # 主文字：近白
            "text_secondary":  "#6b7280",   # 弱化文字：暗灰

            # —— 交互层 ——
            "sidebar_active":  "#2f3037",   # 悬停/选中背景：柔和提升
            "accent":          "#5b6ef5",   # 强调色：柔和蓝紫（降饱和）
            "accent_soft":     "#2e3350",   # 强调色浅底（选中行背景）
            "accent_hover":    "#4a5ce0",   # 悬停深一档

            # —— 边框/分隔 ——
            "border":          "#35363c",   # 边框：柔和深灰
            "divider":         "#2d2e33",   # 分隔线：更淡

            # —— 状态色（柔和版） ——
            "success":         "#4ade80",
            "danger":          "#f87171",
            "warning":         "#fbbf24",
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

        # ---------- 结果窗口 ----------
        root_search = tk.Toplevel(self.root)
        root_search.title("查询结果")
        root_search.configure(bg=COLORS["content_bg"])

        W, H = 1000, 580
        root_search.update_idletasks()
        x = (root_search.winfo_screenwidth() - W) // 2
        y = (root_search.winfo_screenheight() - H) // 2
        root_search.geometry(f"{W}x{H}+{x}+{y}")
        root_search.minsize(760, 440)

        # ---------- ttk 样式 ----------
        style = ttk.Style()
        style.theme_use("clam")

        # 表格主体（深灰卡片 + 柔白字）
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

        # 表头（比卡片稍深一档 + 二级灰字）
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

        # 选中行（柔和蓝底 + 浅色字，不用纯蓝填充）
        style.map(
            "DS.Treeview",
            background=[("selected", COLORS["accent_soft"])],
            foreground=[("selected", "#c7d2fe")],
        )

        # 去掉 Treeview 外框
        style.layout("DS.Treeview", [
            ("DS.Treeview.treearea", {"sticky": "nswe"})
        ])

        # 滚动条（细、柔和、无边框）
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

        # ---------- 顶部标题区 ----------
        header = tk.Frame(root_search, bg=COLORS["content_bg"])
        header.pack(fill="x", padx=36, pady=(28, 0))

        tk.Label(
            header, text="查询结果",
            bg=COLORS["content_bg"], fg=COLORS["Level1fg"],
            font=("PingFang SC", 20, "bold"),
        ).pack(side="left")

        count_text = f"共 {len(results)} 条记录" if results else "无匹配记录"
        tk.Label(
            header, text=count_text,
            bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
            font=("PingFang SC", 12),
        ).pack(side="right", pady=(6, 0))

        tk.Label(
            root_search,
            text="以下是符合筛选条件的全部数据",
            bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
            font=("PingFang SC", 12),
        ).pack(anchor="w", padx=36, pady=(6, 18))

        # ---------- 卡片（深灰 + 柔和边框 + 圆润感） ----------
        card = tk.Frame(
            root_search,
            bg=COLORS["card_bg"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            bd=0,
        )
        card.pack(fill="both", expand=True, padx=36, pady=(0, 22))

        table_frame = tk.Frame(card, bg=COLORS["card_bg"])
        table_frame.pack(fill="both", expand=True, padx=1, pady=1)

        columns = ("id", "name", "class_name", "grade",
                "telephonenum", "email", "createtime", "changetime")

        tree = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            style="DS.Treeview",
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

        # 斑马纹：两种极接近的深灰，视觉上几乎无感但能引导视线
        tree.tag_configure("oddrow",  background=COLORS["card_bg"])     # 基础深灰
        tree.tag_configure("evenrow", background="#2f3037")             # 略亮一档
        tree.tag_configure("empty",   foreground=COLORS["Level2fg"])    # 空态

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
        footer = tk.Frame(root_search, bg=COLORS["content_bg"])
        footer.pack(fill="x", padx=36, pady=(0, 26))

        # 主按钮：柔和蓝紫
        close_btn = tk.Button(
            footer, text="关闭",
            command=root_search.destroy,
            bg=COLORS["accent"], fg="#ffffff",
            activebackground=COLORS["accent_hover"], activeforeground="#ffffff",
            font=("PingFang SC", 12),
            relief="flat", borderwidth=0,
            padx=28, pady=10,
            cursor="hand2",
        )
        close_btn.pack(side="right")

        def on_enter(e): close_btn.configure(bg=COLORS["accent_hover"])
        def on_leave(e): close_btn.configure(bg=COLORS["accent"])
        close_btn.bind("<Enter>", on_enter)
        close_btn.bind("<Leave>", on_leave)

        # 次按钮：柔和描边
        def export_placeholder():
            print("TODO: 导出功能")

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

        root_search.mainloop()

    # 查找考试数据
    def search_exams(self):
        COLORS = {
                   # —— 背景层 ——
                   "sidebar_bg":      "#1a1b1e",   # 侧边栏：暖灰深色
                   "content_bg":      "#212226",   # 内容区：比侧边栏稍亮，形成微妙层次
                   "card_bg":         "#2a2b30",   # 卡片：柔和深灰（不再是纯白）
       
                   # —— 文字层 ——
                   "Level1fg":        "#e5e7eb",   # 一级文字：柔白
                   "Level2fg":        "#9ca3af",   # 二级文字：中灰
                   "text_primary":    "#f3f4f6",   # 主文字：近白
                   "text_secondary":  "#6b7280",   # 弱化文字：暗灰
       
                   # —— 交互层 ——
                   "sidebar_active":  "#2f3037",   # 悬停/选中背景：柔和提升
                   "accent":          "#5b6ef5",   # 强调色：柔和蓝紫（降饱和）
                   "accent_soft":     "#2e3350",   # 强调色浅底（选中行背景）
                   "accent_hover":    "#4a5ce0",   # 悬停深一档
       
                   # —— 边框/分隔 ——
                   "border":          "#35363c",   # 边框：柔和深灰
                   "divider":         "#2d2e33",   # 分隔线：更淡
       
                   # —— 状态色（柔和版） ——
                   "success":         "#4ade80",
                   "danger":          "#f87171",
                   "warning":         "#fbbf24",
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

        # ---------- 结果窗口 ----------
        root_search = tk.Toplevel(self.root)
        root_search.title("考试查询结果")
        root_search.configure(bg=COLORS["content_bg"])

        W, H = 1000, 580
        root_search.update_idletasks()
        x = (root_search.winfo_screenwidth() - W) // 2
        y = (root_search.winfo_screenheight() - H) // 2
        root_search.geometry(f"{W}x{H}+{x}+{y}")
        root_search.minsize(760, 440)

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

        # ---------- 顶部标题区 ----------
        header = tk.Frame(root_search, bg=COLORS["content_bg"])
        header.pack(fill="x", padx=36, pady=(28, 0))

        tk.Label(
            header, text="考试查询结果",
            bg=COLORS["content_bg"], fg=COLORS["Level1fg"],
            font=("PingFang SC", 20, "bold"),
        ).pack(side="left")

        count_text = f"共 {len(results)} 条记录" if results else "无匹配记录"
        tk.Label(
            header, text=count_text,
            bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
            font=("PingFang SC", 12),
        ).pack(side="right", pady=(6, 0))

        tk.Label(
            root_search,
            text="以下是符合筛选条件的全部考试数据",
            bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
            font=("PingFang SC", 12),
        ).pack(anchor="w", padx=36, pady=(6, 18))

        # ---------- 卡片容器 ----------
        card = tk.Frame(
            root_search,
            bg=COLORS["sidebar_bg"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            bd=0,
        )
        card.pack(fill="both", expand=True, padx=36, pady=(0, 22))

        table_frame = tk.Frame(card, bg=COLORS["sidebar_bg"])
        table_frame.pack(fill="both", expand=True, padx=1, pady=1)

        # ---------- 表格列 ----------
        columns = ("exam_id", "exam_name", "exam_time", "createtime", "changetime")

        tree = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            style="DS.Treeview",
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
        footer = tk.Frame(root_search, bg=COLORS["content_bg"])
        footer.pack(fill="x", padx=36, pady=(0, 26))

        # 主按钮
        close_btn = tk.Button(
            footer, text="关闭",
            command=root_search.destroy,
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

        # 次按钮
        def export_placeholder():
            print("TODO: 导出考试数据")

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

        root_search.mainloop()

    #查询成绩
    def search_scores(self):
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

        # ---------- 结果窗口 ----------
        root_search = tk.Toplevel(self.root)
        root_search.title("成绩查询结果")
        root_search.configure(bg=COLORS["content_bg"])

        W, H = 1200, 580
        root_search.update_idletasks()
        x = (root_search.winfo_screenwidth() - W) // 2
        y = (root_search.winfo_screenheight() - H) // 2
        root_search.geometry(f"{W}x{H}+{x}+{y}")
        root_search.minsize(900, 440)

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

        # ---------- 顶部标题区 ----------
        header = tk.Frame(root_search, bg=COLORS["content_bg"])
        header.pack(fill="x", padx=36, pady=(28, 0))

        tk.Label(
            header, text="成绩查询结果",
            bg=COLORS["content_bg"], fg=COLORS["Level1fg"],
            font=("PingFang SC", 20, "bold"),
        ).pack(side="left")

        count_text = f"共 {len(results)} 条记录" if results else "无匹配记录"
        tk.Label(
            header, text=count_text,
            bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
            font=("PingFang SC", 12),
        ).pack(side="right", pady=(6, 0))

        tk.Label(
            root_search,
            text="以下是符合筛选条件的全部成绩数据",
            bg=COLORS["content_bg"], fg=COLORS["Level2fg"],
            font=("PingFang SC", 12),
        ).pack(anchor="w", padx=36, pady=(6, 18))

        # ---------- 卡片容器 ----------
        card = tk.Frame(
            root_search,
            bg=COLORS["sidebar_bg"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            bd=0,
        )
        card.pack(fill="both", expand=True, padx=36, pady=(0, 22))

        table_frame = tk.Frame(card, bg=COLORS["sidebar_bg"])
        table_frame.pack(fill="both", expand=True, padx=1, pady=1)

        # ---------- 表格列 ----------
        columns = (
            "student_id", "exam_id", "subject",
            "initialscore", "score", "rank", "headcount",
            "createtime", "changetime",
        )

        tree = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            style="DS.Treeview",
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

        # 滚动条 + 表格布局
        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical",
            command=tree.yview, style="DS.Vertical.TScrollbar",
        )
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 横向滚动条（9 列较宽，加一个备用）
        h_scrollbar = ttk.Scrollbar(
            table_frame, orient="horizontal",
            command=tree.xview, style="DS.Vertical.TScrollbar",
        )
        tree.configure(xscrollcommand=h_scrollbar.set)
        h_scrollbar.pack(side="bottom", fill="x")

        # ---------- 底部按钮区 ----------
        footer = tk.Frame(root_search, bg=COLORS["content_bg"])
        footer.pack(fill="x", padx=36, pady=(0, 26))

        # 主按钮
        close_btn = tk.Button(
            footer, text="关闭",
            command=root_search.destroy,
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

        # 次按钮
        def export_placeholder():
            print("TODO: 导出成绩数据")

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

        root_search.mainloop()
                       
        
    
    def pack_button(self,target):
        if target == "学生":
            tk.Label(self.content_frame,text="编号", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=2,column=0,padx=5,pady=5)
            self.E_id = tk.Entry(self.content_frame)
            self.E_id.grid(row=2,column=1,padx=5,pady=5)

            tk.Label(self.content_frame,text="姓名", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=3,column=0,padx=5,pady=5)
            self.E_name = tk.Entry(self.content_frame)
            self.E_name.grid(row=3,column=1,padx=5,pady=5)

            tk.Label(self.content_frame,text="班级", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=4,column=0,padx=5,pady=5)
            self.E_class = tk.Entry(self.content_frame)
            self.E_class.grid(row=4,column=1,padx=5,pady=5)

            tk.Label(self.content_frame,text="年级", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=5,column=0,padx=5,pady=5)
            self.E_grade = tk.Entry(self.content_frame)
            self.E_grade.grid(row=5,column=1,padx=5,pady=5)

            tk.Label(self.content_frame,text="电话", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=6,column=0,padx=5,pady=5)
            self.E_telephonenum = tk.Entry(self.content_frame)
            self.E_telephonenum.grid(row=6,column=1,padx=5,pady=5)

            tk.Label(self.content_frame,text="邮箱", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=7,column=0,padx=5,pady=5)
            self.E_email = tk.Entry(self.content_frame)
            self.E_email.grid(row=7,column=1,padx=5,pady=5)

            tk.Label(self.content_frame,text="创建时间", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=8,column=0,padx=5,pady=5)
            self.E_createtime = tk.Entry(self.content_frame)
            self.E_createtime.grid(row=8,column=1,padx=5,pady=5)

            tk.Label(self.content_frame,text="修改时间", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=9,column=0,padx=5,pady=5)
            self.E_changetime = tk.Entry(self.content_frame)
            self.E_changetime.grid(row=9,column=1 ,padx=5,pady=5)

            B_confirm = tk.Label(self.content_frame,text="确认", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16))
            B_confirm.grid(row=10,column=0,padx=5,pady=5)
            self.create_Button(B_confirm, lambda: self.search_students())

        if target == "考试":
            tk.Label(self.content_frame,text="考试编号", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=2,column=0,padx=5,pady=5)
            self.E_exam_id = tk.Entry(self.content_frame)
            self.E_exam_id.grid(row=2,column=1,padx=5,pady=5)

            tk.Label(self.content_frame,text="考试名称", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=3,column=0,padx=5,pady=5)
            self.E_exam_name = tk.Entry(self.content_frame)
            self.E_exam_name.grid(row=3,column=1,padx=5,pady=5)

            tk.Label(self.content_frame,text="考试时间", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=4,column=0,padx=5,pady=5)
            self.E_exam_time = tk.Entry(self.content_frame)
            self.E_exam_time.grid(row=4,column=1,padx=5,pady=5)

            tk.Label(self.content_frame,text="创建时间", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=5,column=0,padx=5,pady=5)
            self.E_createtime = tk.Entry(self.content_frame)
            self.E_createtime.grid(row=5,column=1,padx=5,pady=5)

            tk.Label(self.content_frame,text="修改时间", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=6,column=0,padx=5,pady=5)
            self.E_changetime = tk.Entry(self.content_frame)
            self.E_changetime.grid(row=6,column=1 ,padx=5,pady=5)

            B_confirm = tk.Label(self.content_frame,text="确认", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16))
            B_confirm.grid(row=7,column=0,padx=5,pady=5)
            self.create_Button(B_confirm, lambda: print("TODO: 查询考试数据"))

        if target == "成绩":
            tk.Label(self.content_frame,text="学生编号", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=2,column=0,padx=5,pady=5)
            self.E_student_id = tk.Entry(self.content_frame)
            self.E_student_id.grid(row=2,column=1,padx=5,pady=5)

            tk.Label(self.content_frame,text="考试编号", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=3,column=0,padx=5,pady=5)
            self.E_exam_id = tk.Entry(self.content_frame)
            self.E_exam_id.grid(row=3,column=1,padx=5,pady=5)

            tk.Label(self.content_frame,text="科目", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=4,column=0,padx=5,pady=5)
            self.E_subject = tk.Entry(self.content_frame)
            self.E_subject.grid(row=4,column=1,padx=5,pady=5)

            tk.Label(self.content_frame,text="初始成绩", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=5,column=0,padx=5,pady=5)
            self.E_initialscore = tk.Entry(self.content_frame)
            self.E_initialscore.grid(row=5,column=1,padx=5,pady=5)

            tk.Label(self.content_frame,text="成绩", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=6,column=0,padx=5,pady=5)
            self.E_score = tk.Entry(self.content_frame)
            self.E_score.grid(row=6,column=1,padx=5,pady=5)

            tk.Label(self.content_frame,text="排名", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=7,column=0,padx=5,pady=5)
            self.E_rank = tk.Entry(self.content_frame)
            self.E_rank.grid(row=7,column=1,padx=5,pady=5)

            tk.Label(self.content_frame,text="总人数", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=8,column=0,padx=5,pady=5)
            self.E_headcount = tk.Entry(self.content_frame)
            self.E_headcount.grid(row=8,column=1,padx=5,pady=5) 

            tk.Label(self.content_frame,text="创建时间", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=9,column=0,padx=5,pady=5)
            self.E_createtime = tk.Entry(self.content_frame)
            self.E_createtime.grid(row=9,column=1,padx=5,pady=5)

            tk.Label(self.content_frame,text="修改时间", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=10,column=0,padx=5,pady=5)
            self.E_changetime = tk.Entry(self.content_frame)    
            self.E_changetime.grid(row=10,column=1,padx=5,pady=5)

            B_confirm = tk.Label(self.content_frame,text="确认", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16))
            B_confirm.grid(row=11,column=0,padx=5,pady=5)
            self.create_Button(B_confirm, lambda: print("TODO: 查询成绩数据"))