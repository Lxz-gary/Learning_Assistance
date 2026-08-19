#导入DataBase/DataOperation.py 和 DataHandle/ReadData.py 中的类
from DataBase.DataOperation import DatabaseManager
from DataHandle.ReadData import ReadData
import time

#将数据库建立在DataBase文件夹下，数据库名为my_database.db
reader = ReadData()
manager = DatabaseManager("DataBase/my_database.db")

'''t1 = time.time()
manager.initialize_database()
student_data = reader.read_studentdata("TestData/学生信息表.xlsx")
for i in student_data:
    manager.insert_data(i,"student")
t2 = time.time()
print("初始化数据库并插入学生数据耗时：", t2 - t1,)

t1 = time.time()
exam_data = reader.read_examdata("TestData/考试信息表.xlsx")
for i in exam_data:
    manager.insert_data(i,"exam")
t2 = time.time()
print("插入考试数据耗时：", t2 - t1,)


t1 = time.time()
score_data = reader.read_scoredata("TestData/成绩信息表.xlsx")
for i in score_data:
    manager.insert_data(i,"score")
t2 = time.time()
print("插入成绩数据耗时：", t2 - t1, "秒")'''

manager.replace_data(('S0001', '学生_1', '高11班', '2', '13875682867', 'student1@school.edu'), "student")
print(manager.query_students('S0001', None, None, None, None, None))

