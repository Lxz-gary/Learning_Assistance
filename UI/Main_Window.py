import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    
    root: tk.Tk

root = tk.Tk()
root.title("成绩分析系统")
root.geometry()

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

class MainWindow:
    root: tk.Tk
    def __init__(self, root: tk.Tk):
        self.root: tk.Tk = root
        root.title("成绩分析系统")
        root.geometry("1000x680")

        # 设置边框拉伸
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=0)  # 侧边栏固定宽度
        root.grid_columnconfigure(1, weight=0)  # 内容区自适应宽度
        root.grid_columnconfigure(2, weight=1)  # 内容区自适应宽度

        # 创建侧边栏
        self.sidebar = tk.Frame(root, bg=COLORS["sidebar_bg"], width=200)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        # 创建内容区
        self.content = tk.Frame(root, bg=COLORS["content_bg"])
        self.content.grid(row=0, column=2, sticky="nsew")

        #创建分割线
        separator = tk.Frame(root, bg=COLORS["border"], width=2)
        separator.grid(row=0, column=1, sticky="ns")

        #创建内容区默认，并使文字整体左右居中，上下居中
        default_label = tk.Label(self.content, text="欢迎使用成绩分析系统", bg=COLORS["content_bg"], fg=COLORS["text_primary"], font=("PingFang SC", 20))
        default_label.pack(pady=20, padx=20, fill="both", expand=True)

        # 创建侧边栏标题
        header = tk.Label(self.sidebar, text="成绩分析系统", bg=COLORS["sidebar_bg"], fg=COLORS["Level1fg"], font=("PingFang SC", 25, "bold"))
        header.pack(pady=20, padx=20, fill="x", anchor="w")

        B_query = tk.Label(self.sidebar, text="查询数据", bg=COLORS["sidebar_bg"], fg=COLORS["Level2fg"], font=("PingFang SC", 16, "bold"))
        self.create_Button(B_query, self.build_query_page)
        B_query.pack(pady=5, padx=20, fill="x")

        root.mainloop()

    #把Label改为Button，并绑定点击事件
    def create_Button(self, button : tk.Label, reaction):
        button.bind("<Button-1>", lambda event: reaction())
        button.bind("<Enter>", lambda event: button.config(bg=COLORS["sidebar_active"]))
        button.bind("<Leave>", lambda event: button.config(bg=COLORS["sidebar_bg"]))        

    #为查询数据搭建页面
    def build_query_page(self):
        # 清空内容区
        for widget in self.content.winfo_children():
            widget.destroy()

        # 创建查询数据界面
        query_label = tk.Label(self.content, text="查询数据", bg=COLORS["content_bg"], fg=COLORS["text_primary"], font=("PingFang SC", 20))
        query_label.pack(pady=20, padx=20, fill="both", expand=True)



root = tk.Tk()
app = MainWindow(root)
