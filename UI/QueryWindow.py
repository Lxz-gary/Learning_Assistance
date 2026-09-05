import tkinter as tk
import tkinter.ttk as ttk
import queue, threading, time 
import customtkinter as ctk
from ..Controller.DataBaseController import DataBaseController

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
                    print("student")
                    self.pack_button("学生")
                if data == "考试":
                    print("exam")
                if data == "成绩":
                    print("score")
    
            except queue.Empty:
                print("done")
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
        results = db_controller.query_student(id, name, class_name, grade, telephonenum, email, createtime, changetime)

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

            B_confirm = tk.Label(self.content_frame,text="确认", bg=COLORS["content_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16)).grid(row=10,column=0,padx=5,pady=5)
            self.create_Button(B_confirm, lambda: self.search_students(target))



