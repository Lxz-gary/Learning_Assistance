import pandas as pd
import os
import time



#读取指定信息
class DataReader:
    def __init__(self, file_path):
        self.file_path = file_path

    #读取学生信息
    def read_students(self):
        if not os.path.exists(self.file_path):
            print(f"文件 {self.file_path} 不存在。")
            return []
        
        df = pd.read_excel(self.file_path)
        students = []
        for _, row in df.iterrows():
            student = {
                "id": row["学生ID"],
                "name": row["姓名"],
                "class": str(row["班级"]),
                "grade": str(row["年级"]),
                "phone_number": str(row["电话号码"]),
                "email": row["邮箱"]
            }
            students.append(student)
        return students
    
    
    #读取考试信息
    def read_exams(self):        
        if not os.path.exists(self.file_path):
            print(f"文件 {self.file_path} 不存在。")
            return []
        df = pd.read_excel(self.file_path)
        exams = []
        for _, row in df.iterrows():
            exam = {
                "id": row["考试ID"],
                "name": row["考试名称"],
                "date": row["考试日期"]
            }
            exams.append(exam)
        return exams
    
    
    #读取成绩信息
    def read_scores(self):        
        if not os.path.exists(self.file_path):
            print(f"文件 {self.file_path} 不存在。")
            return []
        df = pd.read_excel(self.file_path)
        scores = []
        for _, row in df.iterrows():
            score = {
                "student_id": row["学生ID"],
                "exam_id": row["考试ID"],
                "subject": row["科目"],
                "raw_score": row["成绩"],
                "rank": int(row["排名"]),
                "total_candidates": int(row["总人数"]),
                "converted_score": row["赋分"]

            }
            scores.append(score)
        return scores
    
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
