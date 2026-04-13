import sys,time
sys.path.append('./DataBase')
sys.path.append('./DataAnalyse')

from DataBase.db_manager import DBManager
from DataBase.data_read import DataReader
from DataAnalyse.analyser import ScoreAnalyser, StudentAnalyser, ExamAnalyser



#测试
if __name__ == "__main__":
    t1 = time.time()
    reader = DataReader("test_data/学生信息表.xlsx")
    students = reader.read_students()
    t2 = time.time()
    print(f"读取学生信息耗时: {t2 - t1:.2f} 秒")

    t1 = time.time()
    reader = DataReader("test_data/考试信息表.xlsx")
    exams = reader.read_exams()
    t2 = time.time()
    print(f"读取考试信息耗时: {t2 - t1:.2f} 秒")

    t1 = time.time()
    reader = DataReader("test_data/成绩信息表.xlsx")
    scores = reader.read_scores()
    t2 = time.time()
    print(f"读取成绩信息耗时: {t2 - t1:.2f} 秒")  

    #写入数据库
    db = DBManager()
    db.connect()
    db.clear_database()  # 清除数据库中的所有表（慎用）
    db._create_table()  # 重新创建表结构
    
    t1 = time.time()
    for student in students:
        db.add_student(student["id"], student["name"], student["class"], str(student["grade"]), str(student["phone_number"]), student["email"])
    t2 = time.time()
    print(f"写入学生信息耗时: {t2 - t1:.2f} 秒")
    
    t1
    for exam in exams:
        db.add_exam(exam["id"], exam["name"], exam["date"])
    t2 = time.time()
    print(f"写入考试信息耗时: {t2 - t1:.2f} 秒")
    
    t1 = time.time()
    for score in scores:
        db.add_score(score["student_id"], score["exam_id"], score["subject"], score["raw_score"], score["rank"], score["total_candidates"], score["converted_score"])
    t2 = time.time()
    print(f"写入成绩信息耗时: {t2 - t1:.2f} 秒")

    db.close()