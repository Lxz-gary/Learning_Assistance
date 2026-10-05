from DataBase.DataOperation import DatabaseManager
from rapidfuzz import fuzz, process

db_manager = DatabaseManager("my_database.db")

class DataBaseController:
    def __init__(self):
        self.db_manager = db_manager

    # 查询学生数据
    def query_student(self, id=None, name=None, class_name=None, grade=None, telephonenum=None, email=None, createtime=None, changetime=None):
        
        initial_check = self.db_manager.query_students(id, name, class_name, grade, telephonenum, email, createtime, changetime)
        results = []
        if initial_check:
            for student in initial_check:
                if id and fuzz.partial_ratio(student[0], id) < 80:
                    continue
                if name and fuzz.partial_ratio(student[1], name) < 80:
                    continue
                if class_name and fuzz.partial_ratio(student[2], class_name) < 80:
                    continue
                if grade and fuzz.partial_ratio(student[3], grade) < 80:
                    continue
                if telephonenum and fuzz.partial_ratio(student[4], telephonenum) < 80:
                    continue
                if email and fuzz.partial_ratio(student[5], email) < 80:
                    continue
                results.append(student)

        return results

    # 查询考试数据
    def query_exam(self, id=None, name=None, date=None, createtime=None, changetime=None):
        initial_check = self.db_manager.query_exams(id, name, date, createtime, changetime)
        results = []
        if initial_check:
            for exam in initial_check:
                if id and fuzz.partial_ratio(exam[0], id) < 80:
                    continue
                if name and fuzz.partial_ratio(exam[1], name) < 80:
                    continue
                if date and fuzz.partial_ratio(exam[3], date) < 80:
                    continue
                results.append(exam)
        return results

    # 查询成绩数据.     TODO: 询问用户是否需要进行分数模糊化
    def query_score(self,student_id = None,exam_id = None,subject = None,initialscore = None,score_use = None,rank = None,headcount = None,createtime = None,changetime = None):
        initial_check = self.db_manager.query_scores(student_id,exam_id,subject,initialscore,score_use,rank,headcount,createtime,changetime)
        results = []
        if initial_check:
            for score in initial_check:
                if student_id and fuzz.partial_ratio(score[0], student_id) < 80:
                    continue
                if exam_id and fuzz.partial_ratio(score[1], exam_id) < 80:
                    continue
                if subject and fuzz.partial_ratio(score[2], subject) < 80:
                    continue
                if initialscore and fuzz.partial_ratio(str(score[3]), str(initialscore)) < 80:
                    continue
                if score_use and fuzz.partial_ratio(str(score[4]), str(score_use)) < 80:
                    continue
                if rank and fuzz.partial_ratio(str(score[5]), str(rank)) < 80:
                    continue
                if headcount and fuzz.partial_ratio(str(score[6]), str(headcount)) < 80:
                    continue
                results.append(score)

        return results