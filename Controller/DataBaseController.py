from DataBase.DataOperation import DatabaseManager

db_manager = DatabaseManager("my_database.db")

class DataBaseController:
    def __init__(self):
        self.db_manager = db_manager

    # 查询学生数据
    def query_student(self, id=None, name=None, class_name=None, grade=None, telephonenum=None, email=None, createtime=None, changetime=None):
        return self.db_manager.query_students(id, name, class_name, grade, telephonenum, email, createtime, changetime)

    # 查询考试数据
    def query_exam(self, id=None, name=None, subject=None, date=None, createtime=None, changetime=None):
        return self.db_manager.query_exams(id, name, subject, date, createtime, changetime) 