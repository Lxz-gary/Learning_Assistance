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

    # 查找数据
    def search_students(self):
        id = self.E_id.get()
        name = self.E_name.get()
        class_name = self.E_class.get()
        grade = self.E_grade.get()
        telephonenum = self.E_telephonenum.get()
        email = self.E_email.get()
        createtime = self.E_createtime.get()
        changetime = self.E_changetime.get()
        print(f"查询条件: 编号={id}, 姓名={name}, 班级={class_name}, 年级={grade}, 电话={telephonenum}, 邮箱={email}, 创建时间={createtime}, 修改时间={changetime}")
        results = db_controller.query_student(id, name, class_name, grade, telephonenum, email, createtime, changetime)

        # 创建一个新的窗口来显示查询结果
        root_search = tk.Toplevel(self.root)
        root_search.title("查询结果")
        root_search.geometry("800x400")
        tree = ttk.Treeview(root_search, columns=("id", "name", "class_name", "grade", "telephonenum", "email", "createtime", "changetime"), show="headings")
        tree.heading("id", text="编号")
        tree.heading("name", text="姓名")
        tree.heading("class_name", text="班级")
        tree.heading("grade", text="年级")
        tree.heading("telephonenum", text="电话")
        tree.heading("email", text="邮箱")
        tree.heading("createtime", text="创建时间")
        tree.heading("changetime", text="修改时间")
        for row in results:
            tree.insert("", "end", values=row)
        tree.pack(fill="both", expand=True)

        # 创建滚动条（位于表格右边）
        scrollbar = ttk.Scrollbar(root_search, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # 创建关闭按钮
        close_button = tk.Button(root_search, text="关闭", command=root_search.destroy)
        close_button.pack(pady=10)


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



