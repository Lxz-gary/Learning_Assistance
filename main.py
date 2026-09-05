import tkinter as tk

# 导入项目中的类
from DataBase.DataOperation import DatabaseManager
from DataHandle.ReadData import ReadData
from Controller.DataBaseController import DataBaseController
from UI.MainWindow import MainWindow


def main():
	"""应用程序入口，演示各个类的基本调用方式。"""
	database_manager = DatabaseManager("my_database.db")
	data_reader = ReadData()
	database_controller = DataBaseController()

	# 这些对象在后续业务中使用；这里保留为入口层的基础调用示例。
	print(f"数据库: {database_manager.db_path}")
	print(f"读取器: {data_reader.__class__.__name__}")
	print(f"查询结果: {database_controller.query_student()}")

	root = tk.Tk()
	MainWindow(root)
	root.mainloop()


if __name__ == "__main__":
	main()



