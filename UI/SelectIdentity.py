from tkinter import ttk
from tkinter import messagebox
import tkinter as tk
#方便后续的tkraise()应用
class SelectIdentity(tk.Tk):
    def __init__(self, screenName = None, baseName = None, className = "Tk", useTk = True, sync = False, use = None):
        super().__init__(screenName, baseName, className, useTk, sync, use) 
        self.title("选择身份")
        self.geometry("400x300")    
        self.create_widgets()

    def create_widgets(self):
        # 创建标签和下拉菜单
        label = tk.Label(self, text="请选择您的身份:")
        label.pack(pady=10)

        #用照片填充按钮
        student_photo = tk.PhotoImage(file="image/student.png")
        teacher_photo = tk.PhotoImage(file="image/teacher.png")
        self.identity_var = tk.StringVar()
        student_button = tk.Radiobutton(self, text="学生", variable=self.identity_var, value="学生", indicatoron=0, image=student_photo, compound="top")
        teacher_button = tk.Radiobutton(self, text="教师", variable=self.identity_var, value="教师", indicatoron=0, image=teacher_photo, compound="top")
        student_button.pack(pady=10)
        teacher_button.pack(pady=10)
        

    def confirm_identity(self):
        selected_identity = self.identity_var.get()
        if selected_identity:
            messagebox.showinfo("身份选择", f"您选择的身份是: {selected_identity}")
            # 在这里可以根据选择的身份进行相应的操作，例如打开不同的界面
            self.destroy()  # 关闭当前窗口
        else:
            messagebox.showwarning("身份选择", "请先选择一个身份！")

if __name__ == "__main__":
    app = SelectIdentity()
    app.mainloop()