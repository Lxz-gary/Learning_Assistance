import pandas as pd
import time

class ReadData:
    def __init__(self):
        pass

    #读取学生数据
    def read_studentdata(self,path):
        df = pd.read_excel(path)
        list_of_tuples = [tuple(row) for row in df.values]

        return list_of_tuples

    #读取考试数据
    def read_examdata(self, path):
        df = pd.read_excel(path)
        list_of_tuples = [tuple(row) for row in df.values]
        return list_of_tuples

    #读取成绩数据
    def read_scoredata(self, path):
        df = pd.read_excel(path)
        list_of_tuples = [tuple(row) for row in df.values]
        return list_of_tuples



if __name__ == "__main__":
    r = ReadData()
    t1 = time.time()
    r.read_studentdata("TestData/学生信息表.xlsx")
    t2 = time.time()
    print("读取学生数据耗时：", t2 - t1, "秒")

    t1 = time.time()
    r.read_examdata("TestData/考试信息表.xlsx")
    t2 = time.time()
    print("读取考试数据耗时：", t2 - t1, "秒")

    t1 = time.time()
    r.read_scoredata("TestData/成绩信息表.xlsx")
    t2 = time.time()
    print("读取成绩数据耗时：", t2 - t1, "秒")