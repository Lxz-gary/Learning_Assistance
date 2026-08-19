import sqlite3,time
from contextlib import contextmanager


class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path

    #建立数据库连接
    @contextmanager
    def get_db_connection(self, db_path):
        """连接到数据库"""
        conn = sqlite3.connect(db_path)
        try:
            conn.execute('PRAGMA foreign_keys = ON')  # 启用外键约束
            yield conn
        finally:
            conn.close()

    #获取当前本地时间
    def get_localtime(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    #清空数据库中的表
    def clear_database(self):
        with self.get_db_connection('my_database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('DROP TABLE IF EXISTS scores')
            cursor.execute('DROP TABLE IF EXISTS students')
            cursor.execute('DROP TABLE IF EXISTS exams')
            conn.commit()

    #初始化数据库
    def initialize_database(self):

        with self.get_db_connection('my_database.db') as conn:
            cursor = conn.cursor()
            
            self.clear_database()  # 清空数据库中的表
            #学生表
            '''
            id-学生编号,str
            name-学生姓名,str
            class-学生班级,str
            grade-学生成绩,str
            telephonenum-学生电话,str
            email-学生邮箱,str
            createtime-创建时间,str
            changetime-修改时间,str
            '''
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (       
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    class TEXT NOT NULL,
                    grade TEXT NOT NULL,
                    telephonenum TEXT NOT NULL,
                    email TEXT NOT NULL,
                    createtime TEXT NOT NULL,
                    changetime TEXT NOT NULL)''')

            #考试表
            '''
            id-考试编号,str
            name-考试名称,str
            date-考试日期,str
            createtime-创建时间,str
            changetime-修改时间,str
            '''
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exams
                (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    createtime TEXT NOT NULL,
                    changetime TEXT NOT NULL
                )''')

            #成绩表
            '''
            student_id-学生编号,str
            exam_id-考试编号,str
            subject-考试科目,str
            initialscore-初始成绩,int
            score-最终成绩,int
            rank-排名,int
            headcount-总人数,int
            createtime-创建时间,str
            changetime-修改时间,str
            '''
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scores
                (
                    student_id TEXT,
                    exam_id TEXT,
                    subject TEXT NOT NULL,
                    initialscore INTEGER NOT NULL,
                    score INTEGER NOT NULL,
                    rank INTEGER NOT NULL,
                    headcount INTEGER NOT NULL,
                    createtime TEXT NOT NULL,
                    changetime TEXT NOT NULL,
                    PRIMARY KEY (student_id, exam_id),
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
                )''')

            conn.commit()

    #插入数据
    def insert_data(self, data, type):
        try:
            with self.get_db_connection('my_database.db') as conn:
                cursor = conn.cursor()
                #学生
                if type == "student":
                    #检查是否存在
                    if self.query_students(data[0], None, None, None, None, None):
                        return f"Student with id {data[0]} already exists."
                    data = data + (self.get_localtime(), self.get_localtime())
                    cursor.execute('''
                        INSERT INTO students (id, name, class, grade, telephonenum, email, createtime, changetime)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', data)

                #考试
                if type == "exam":
                    #检查是否存在
                    if self.query_exams(data[0], None, None):
                        return f"Exam with id {data[0]} already exists."


                    data = data + (self.get_localtime(), self.get_localtime())#加入时间
                    cursor.execute('''
                        INSERT INTO exams (id, name, date, createtime, changetime)
                    VALUES (?, ?, ?, ?, ?)''', data)

                #成绩
                if type == "score":
                    #检查是否存在
                    if self.query_scores(data[0], data[1], None, None, None, None,None):
                        return f"Score for student_id {data[0]} and exam_id {data[1]} already exists." 

                    data = data + (self.get_localtime(), self.get_localtime())
                    cursor.execute('''
                        INSERT INTO scores (student_id, exam_id, subject ,initialscore, score, rank, headcount, createtime, changetime)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
                conn.commit()

        except sqlite3.IntegrityError as e:
            return "Error inserting {type} data: {e}"

    #替换数据
    def replace_data(self, data, type):
        try:
            with self.get_db_connection('my_database.db') as conn:
                cursor = conn.cursor()
                #学生
                if type == "student":
                    #如果有字段为None，则查询数据库中该学生的对应字段值，并替换为查询结果
                    for i in range(1, len(data)):
                        if data[i] is None:
                            data[i] = self.query_students(data[0], None, None, None, None, None)[0][i]
                    data = data + (self.get_localtime(),)

                    cursor.execute('''
                        UPDATE students
                        SET name = ?, class = ?, grade = ?, telephonenum = ?, email = ?, changetime = ?
                        WHERE id = ?''', (data[1], data[2], data[3], data[4], data[5], self.get_localtime(), data[0]))
                #考试
                if type == "exam":
                    #如果有字段为None，则查询数据库中该考试的对应字段值，并替换为查询结果
                    for i in range(1, len(data)):
                        if data[i] is None:
                            data[i] = self.query_exams(data[0], None, None)[0][i]
                    data = data + (self.get_localtime(),)
                    cursor.execute('''
                        UPDATE exams
                        SET name = ?, date = ?, changetime = ?
                        WHERE id = ?''', (data[1], data[2], self.get_localtime(), data[0]))
                #成绩
                if type == "score":
                    #如果有字段为None，则查询数据库中该成绩的对应字段值，并替换为查询结果(加入subject字段)
                    for i in range(2, len(data)):
                        if data[i] is None:
                            data[i] = self.query_scores(data[0], data[1], None, None, None, None)[0][i]
                    data = data + (self.get_localtime(),)
                    cursor.execute('''
                        UPDATE scores
                        SET subject = ?, initialscore = ?, score = ?, rank = ?, headcount = ?, changetime = ?
                        WHERE student_id = ? AND exam_id = ?''', (data[2], data[3], data[4], data[5], data[6], self.get_localtime(), data[0], data[1]))
                conn.commit()

        except sqlite3.IntegrityError as e:
            return "Error replacing {type} data: {e}"

    #查询学生数据
    def query_students(self,id,name,Class,grade,telephonenum,email):
        #检查是否存在该学生，如果存在则返回该学生信息，否则返回空列表
        with self.get_db_connection('my_database.db') as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM students WHERE 1=1"
            params = []
            if id:
                query += " AND id = ?"
                params.append(id)
            if name:
                query += " AND name = ?"
                params.append(name)
            if Class:
                query += " AND class = ?"
                params.append(Class)
            if grade:
                query += " AND grade = ?"
                params.append(grade)
            if telephonenum:
                query += " AND telephonenum = ?"
                params.append(telephonenum)
            if email:
                query += " AND email = ?"
                params.append(email)

            cursor.execute(query, params)
            return cursor.fetchall()

    #查询考试数据
    def query_exams(self,id,name,date):
        with self.get_db_connection('my_database.db') as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM exams WHERE 1=1"
            params = []
            if id:
                query += " AND id = ?"
                params.append(id)
            if name:
                query += " AND name = ?"
                params.append(name)
            if date:
                query += " AND date = ?"
                params.append(date)

            cursor.execute(query, params)
            return cursor.fetchall()

    #查询成绩数据
    def query_scores(self,student_id,exam_id,subject,initialscore,score,rank,headcount):
        with self.get_db_connection('my_database.db') as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM scores WHERE 1=1"
            params = []
            if student_id:
                query += " AND student_id = ?"
                params.append(student_id)
            if exam_id:
                query += " AND exam_id = ?"
                params.append(exam_id)
            if initialscore is not None:
                query += " AND initialscore = ?"
                params.append(initialscore)
            if score is not None:
                query += " AND score = ?"
                params.append(score)
            if rank is not None:
                query += " AND rank = ?"
                params.append(rank)
            if headcount is not None:
                query += " AND headcount = ?"
                params.append(headcount)
            if subject:
                query += " AND subject = ?"
                params.append(subject)
            cursor.execute(query, params)
            return cursor.fetchall()        
        
    #删除数据
    def delete_data(self, type, id):
        try:
            with self.get_db_connection('my_database.db') as conn:
                cursor = conn.cursor()
                if type == "student":
                    cursor.execute("DELETE FROM students WHERE id = ?", (id,))
                elif type == "exam":
                    cursor.execute("DELETE FROM exams WHERE id = ?", (id,))
                elif type == "score":
                    cursor.execute("DELETE FROM scores WHERE student_id = ? OR exam_id = ?", (id, id))
                conn.commit()
        except sqlite3.Error as e:
            return f"Error deleting {type} data: {e}"

    #查询数据库基本信息
    def get_database_info(self):
        with self.get_db_connection('my_database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM students")
            student_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM exams")
            exam_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM scores")
            score_count = cursor.fetchone()[0]
            return {
                "students": student_count,
                "exams": exam_count,
                "scores": score_count
            }
