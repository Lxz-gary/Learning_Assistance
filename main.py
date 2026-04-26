import sys,time
sys.path.append('./DataBase')
sys.path.append('./DataAnalyse')

from DataBase.db_manager import DBManager
from DataBase.data_read import DataReader
from DataAnalyse.analyser import ScoreAnalyser, StudentAnalyser, ExamAnalyser



#测试
if __name__ == "__main__":

    #写入数据库
    db = DBManager()
    db.connect()
    '''db._create_table()  # 重新创建表结构

    #读取并写入数据
    t1 = time.time()
    reader = DataReader("test_data/学生信息表.xlsx")
    students = reader.read_students()
    for student in students:
        db.add_student(student["id"], student["name"], student["grade"], student["class"])
    t2 = time.time()
    print(f"学生信息写入数据库耗时: {t2 - t1:.2f}秒")

    t1 = time.time()
    reader = DataReader("test_data/考试信息表.xlsx")
    exams = reader.read_exams()
    for exam in exams:
        db.add_exam(exam["id"], exam["name"], exam["date"])
    t2 = time.time()
    print(f"考试信息写入数据库耗时: {t2 - t1:.2f}秒")

    t1 = time.time()
    reader = DataReader("test_data/成绩信息表.xlsx")
    scores = reader.read_scores()
    for score in scores:
        db.add_score(score["student_id"], score["exam_id"], score["subject"], score["raw_score"], score["rank"], score["total_candidates"], score["converted_score"])
    t2 = time.time()
    print(f"成绩信息写入数据库耗时: {t2 - t1:.2f}秒")'''

    #分析具体考试ID的成绩分布
    analyser = ScoreAnalyser(db.query_scores(exam_id="E0982", subject="数学"))
    distribution = analyser.score_distribution()
    print("考试ID E0982 的成绩分布:")
    for grade, count in distribution.items():
        print(f"{grade}: {count} 人")

    #分析具体学生ID的年级分布
    student_analyser = StudentAnalyser("S1234")
    grade_dist = student_analyser.grade_distribution(db.query_students())
    print("学生ID S1234 的年级分布:")
    for grade, count in grade_dist.items():
        print(f"{grade}: {count} 人")   
    
    
    





    db.close()