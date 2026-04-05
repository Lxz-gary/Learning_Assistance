import sqlite3

class db_manager:
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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                class TEXT,
                grade TEXT
            )
        ''')
        
        # 考试表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS exams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date TEXT
            )
        ''')
        
        # 成绩表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                exam_id INTEGER NOT NULL,
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

    #--------------------学生模块--------------------
    
    # ····添加学生····   
    def add_student(self,id: int, name: str, class_name: str, grade: str):
        self.cursor.execute('''
            INSERT INTO students (id ,name, class, grade) VALUES (?, ?, ?, ?)
        ''', (id, name, class_name, grade))
        self.conn.commit()

    # ····删除学生····
    def delete_student(self, id: int):
        self.cursor.execute('''
            DELETE FROM students WHERE id = ?
        ''', (id,))
        self.conn.commit()

    # ····更新学生信息····
    def update_student(self, id: int, name: str = None, class_name: str = None, grade: str = None):
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
        self.conn.commit()

    #--------------------考试模块--------------------

    # ····添加考试····
    def add_exam(self, id: int, name: str, date: str):
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

    #--------------------成绩模块--------------------

    # ····添加成绩····
    def add_score(self, student_id: int, exam_id: int, subject: str, raw_score: float, rank: int, total_candidates: int, converted_score: float):
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

            




d = db_manager()
d.connect()
d._create_table()
d.close()