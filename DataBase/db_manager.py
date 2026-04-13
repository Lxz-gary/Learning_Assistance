import sqlite3

class DBManager:
    def __init__(self,db_path:str = "data/information.db"):
        #初始化数据库
        self.conn = None                         #创建/打开数据库
        self.cursor = None                       #创建数据库游标
        self.db_path = db_path                   #数据库路径

    #建立与数据库的连接
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    #结束与数据库的连接
    def close(self):
        if self.conn:
            self.conn.close()

    #创建必要的表
    def _create_table(self):
        # 学生表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id TEXT,
                name TEXT NOT NULL,
                class TEXT,
                grade TEXT,
                phone_number TEXT,
                email TEXT
            )
        ''')
        
        # 考试表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS exams (
                id TEXT,
                name TEXT NOT NULL,
                date TEXT
            )
        ''')
        
        # 成绩表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                exam_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                raw_score REAL,
                rank INTEGER,
                total_candidates INTEGER,
                converted_score REAL,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
                UNIQUE(student_id, exam_id, subject)
            )
        ''')
        
        # 赋分规则表（存储省份规则JSON）
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS rule_province (
                province TEXT PRIMARY KEY,
                rule_json TEXT NOT NULL
            )
        ''')
        
        # 专业选科要求表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS major_subject_require (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                major_name TEXT NOT NULL,
                required_subjects TEXT  
            )
        ''')
        
        # 高校录取数据表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS college_admission (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                college_name TEXT NOT NULL,
                year INTEGER,
                province TEXT,
                batch TEXT,
                min_score INTEGER,
                min_rank INTEGER
            )
        ''')
        
        # 创建常用索引加速查询
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_scores_student ON scores(student_id)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_scores_exam ON scores(exam_id)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_scores_subject ON scores(subject)
        ''')
        
        self.conn.commit()

    #清除数据库中的所有表（慎用）
    def clear_database(self):
        self.cursor.execute('DROP TABLE IF EXISTS students')
        self.cursor.execute('DROP TABLE IF EXISTS exams')
        self.cursor.execute('DROP TABLE IF EXISTS scores')
        self.cursor.execute('DROP TABLE IF EXISTS rule_province')
        self.cursor.execute('DROP TABLE IF EXISTS major_subject_require')
        self.cursor.execute('DROP TABLE IF EXISTS college_admission')
        self.conn.commit()
    #--------------------学生模块--------------------
    
    # ····添加学生····   
    def add_student(self,id: int, name: str, class_name: str, grade: str,phone_number: str = None, email: str = None):
        # 确保所有字段都是字符串类型
        id = str(id) if id is not None else ""
        name = str(name) if name is not None else ""
        class_name = str(class_name) if class_name is not None else ""
        grade = str(grade) if grade is not None else ""  # 关键：将grade转换为字符串
        phone_number = str(phone_number) if phone_number is not None else ""  # 关键：将phone_number转换为字符串
        email = str(email) if email is not None else ""
        self.cursor.execute('''
            INSERT INTO students (id ,name, class, grade, phone_number, email) VALUES (?, ?, ?, ?, ?, ?)
        ''', (id, name, class_name, grade, phone_number, email))
        self.conn.commit()

    # ····删除学生····
    def delete_student(self, id: int):
        self.cursor.execute('''
            DELETE FROM students WHERE id = ?
        ''', (id,))
        self.conn.commit()

    # ····更新学生信息····
    def update_student(self, id: int, name: str = None, class_name: str = None, grade: str = None, phone_number: str = None, email: str = None):
        if id:
            self.cursor.execute('''
                SELECT * FROM students WHERE id = ?
            ''', (id,))
            if not self.cursor.fetchone():
                print(f"学生ID {id} 不存在，无法更新。")
                return
        if name:
            self.cursor.execute('''
                UPDATE students SET name = ? WHERE id = ?
            ''', (name, id))
        if class_name:
            self.cursor.execute('''
                UPDATE students SET class = ? WHERE id = ?
            ''', (class_name, id))
        if grade:
            self.cursor.execute('''
                UPDATE students SET grade = ? WHERE id = ?
            ''', (grade, id))
        if phone_number:
            self.cursor.execute('''
                UPDATE students SET phone_number = ? WHERE id = ?
            ''', (phone_number, id))
        if email:
            self.cursor.execute('''
                UPDATE students SET email = ? WHERE id = ?
            ''', (email, id))
        self.conn.commit()

    #····查询学生信息····
    def query_students(self, id: int = None, name: str = None, class_name: str = None, grade: str = None, phone_number: str = None, email: str = None): 
        query = "SELECT * FROM students WHERE 1=1"
        params = []
        if id:
            query += " AND id = ?"
            params.append(id)
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        if class_name:  
            query += " AND class LIKE ?"
            params.append(f"%{class_name}%")
        if grade:
            query += " AND grade LIKE ?"
            params.append(f"%{grade}%")

        if phone_number:
            query += " AND phone_number LIKE ?"
            params.append(f"%{phone_number}%")
        if email:
            query += " AND email LIKE ?"
            params.append(f"%{email}%")
        self.cursor.execute(query, params)
        return self.cursor.fetchall()       

    #--------------------考试模块--------------------

    # ····添加考试····
    def add_exam(self, id: int, name: str, date: str):
        #检测是否为字符串类型，如果不是则转换为字符串
        id = str(id) if id is not None else ""
        name = str(name) if name is not None else ""
        date = str(date) if date is not None else ""
        self.cursor.execute('''
            INSERT INTO exams (id, name, date) VALUES (?, ?, ?)
        ''', (id, name, date))
        self.conn.commit()

    # ····删除考试····
    def delete_exam(self, id: int):
        self.cursor.execute('''
            DELETE FROM exams WHERE id = ?
        ''', (id,))
        self.conn.commit()

    # ····更新考试信息····
    def update_exam(self, id: int, name: str = None, date: str = None):
        if id:
            self.cursor.execute('''
                SELECT * FROM exams WHERE id = ?
            ''', (id,))
            if not self.cursor.fetchone():
                print(f"考试ID {id} 不存在，无法更新。")
                return
        if name:
            self.cursor.execute('''
                UPDATE exams SET name = ? WHERE id = ?
            ''', (name, id))
        if date:
            self.cursor.execute('''
                UPDATE exams SET date = ? WHERE id = ?
            ''', (date, id))
        self.conn.commit()

    #····查询考试信息····
    def query_exams(self, id: int = None, name: str = None, date: str = None):
        query = "SELECT * FROM exams WHERE 1=1"
        params = []
        if id:
            query += " AND id = ?"
            params.append(id)
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        if date:        
            query += " AND date = ?"
            params.append(date)
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    #--------------------成绩模块--------------------

    # ····添加成绩····
    def add_score(self, student_id: int, exam_id: int, subject: str, raw_score: float, rank: int, total_candidates: int, converted_score: float):
        #检测是否为字符串类型，如果不是则转换为字符串
        student_id = str(student_id) if student_id is not None else ""
        exam_id = str(exam_id) if exam_id is not None else ""   
        subject = str(subject) if subject is not None else ""
        raw_score = float(raw_score) if raw_score is not None else 0.0
        rank = int(rank) if rank is not None else 0
        total_candidates = int(total_candidates) if total_candidates is not None else 0
        converted_score = float(converted_score) if converted_score is not None else 0.0

        self.cursor.execute('''
            INSERT INTO scores (student_id, exam_id, subject, raw_score, rank, total_candidates, converted_score) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (student_id, exam_id, subject, raw_score, rank, total_candidates, converted_score))
        self.conn.commit()
    
    # ····删除成绩····
    def delete_score(self, score_id: int):
        self.cursor.execute('''
            DELETE FROM scores WHERE id = ?
        ''', (score_id,))
        self.conn.commit()

    # ····更新成绩信息····  
    def update_score(self, score_id: int, student_id: int = None, exam_id: int = None, subject: str = None, raw_score: float = None, rank: int = None, total_candidates: int = None, converted_score: float = None):
        if score_id:
            self.cursor.execute('''
                SELECT * FROM scores WHERE id = ?
            ''', (score_id,))
            if not self.cursor.fetchone():
                print(f"成绩ID {score_id} 不存在，无法更新。")
                return
        if student_id:
            self.cursor.execute('''
                UPDATE scores SET student_id = ? WHERE id = ?
            ''', (student_id, score_id))
        if exam_id:
            self.cursor.execute('''
                UPDATE scores SET exam_id = ? WHERE id = ?
            ''', (exam_id, score_id))
        if subject:
            self.cursor.execute('''
                UPDATE scores SET subject = ? WHERE id = ?
            ''', (subject, score_id))
        if raw_score is not None:
            self.cursor.execute('''
                UPDATE scores SET raw_score = ? WHERE id = ?
            ''', (raw_score, score_id))
        if rank is not None:
            self.cursor.execute('''
                UPDATE scores SET rank = ? WHERE id = ?
            ''', (rank, score_id))
        if total_candidates is not None:
            self.cursor.execute('''
                UPDATE scores SET total_candidates = ? WHERE id = ?
            ''', (total_candidates, score_id))
        if converted_score is not None:
            self.cursor.execute('''
                UPDATE scores SET converted_score = ? WHERE id = ?
            ''', (converted_score, score_id))
        self.conn.commit()

    #····查询成绩信息····
    def query_scores(self, score_id: int = None, student_id: int = None , exam_id: int = None, subject: str = None):
        query = "SELECT * FROM scores WHERE 1=1"
        params = []
        if score_id:
            query += " AND id = ?"
            params.append(score_id)
        if student_id:
            query += " AND student_id = ?"
            params.append(student_id)
        if exam_id:
            query += " AND exam_id = ?"
            params.append(exam_id)
        if subject:
            query += " AND subject LIKE ?"
            params.append(f"%{subject}%")
        self.cursor.execute(query, params)
        return self.cursor.fetchall()     




d = DBManager()
d.connect()
d._create_table()
d.close()