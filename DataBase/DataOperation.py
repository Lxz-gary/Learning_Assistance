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
            grade-学生年级,str
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
                    PRIMARY KEY (student_id, exam_id, subject),
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
                )''')

            conn.commit()

    #插入数据
    def insert_data(self, data, type):
        try:
            # 主键重复检查：必须用 record_exists 精确匹配，
            # 原来的 query_xxx 是 LIKE 模糊查询（"S1" 会命中 "S100"），而且参数个数还不匹配
            if type == "student":
                if self.record_exists("student", [data[0]]):
                    return f"编号 {data[0]} 已存在"
            elif type == "exam":
                if self.record_exists("exam", [data[0]]):
                    return f"考试编号 {data[0]} 已存在"
            elif type == "score":
                if self.record_exists("score", [data[0], data[1], data[2]]):
                    return f"{data[0]} 在 {data[1]} 的{data[2]}成绩已存在"

            with self.get_db_connection('my_database.db') as conn:
                cursor = conn.cursor()
                data = tuple(data) + (self.get_localtime(), self.get_localtime())

                #学生
                if type == "student":
                    cursor.execute('''
                        INSERT INTO students (id, name, class, grade, telephonenum, email, createtime, changetime)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', data)

                #考试
                elif type == "exam":
                    cursor.execute('''
                        INSERT INTO exams (id, name, date, createtime, changetime)
                    VALUES (?, ?, ?, ?, ?)''', data)

                #成绩
                elif type == "score":
                    cursor.execute('''
                        INSERT INTO scores (student_id, exam_id, subject ,initialscore, score, rank, headcount, createtime, changetime)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)

                conn.commit()
            return None

        except sqlite3.IntegrityError as e:
            return f"数据不合法（外键或唯一约束冲突）：{e}"
        except Exception as e:
            return f"写入失败：{e}"

    #整行更新（主键不改；data 顺序与 insert_data 相同，不含时间戳）
    def update_row(self, data, type):
        data = tuple(data)
        with self.get_db_connection('my_database.db') as conn:
            cursor = conn.cursor()
            now = self.get_localtime()

            if type == "student":
                # (id, name, class, grade, telephonenum, email)
                cursor.execute('''
                    UPDATE students
                    SET name = ?, class = ?, grade = ?, telephonenum = ?, email = ?, changetime = ?
                    WHERE id = ?''', (data[1], data[2], data[3], data[4], data[5], now, data[0]))

            elif type == "exam":
                # (id, name, date)
                cursor.execute('''
                    UPDATE exams
                    SET name = ?, date = ?, changetime = ?
                    WHERE id = ?''', (data[1], data[2], now, data[0]))

            elif type == "score":
                # (student_id, exam_id, subject, initialscore, score, rank, headcount)
                cursor.execute('''
                    UPDATE scores
                    SET initialscore = ?, score = ?, rank = ?, headcount = ?, changetime = ?
                    WHERE student_id = ? AND exam_id = ? AND subject = ?''',
                    (data[3], data[4], data[5], data[6], now, data[0], data[1], data[2]))

            updated = cursor.rowcount
            conn.commit()
            return updated

    #把旧库的 scores 主键从 (student_id, exam_id) 升级为 (student_id, exam_id, subject)
    #幂等：已经是新结构就直接返回 False；迁移前会自动备份成 my_database.db.bak
    def upgrade_scores_schema(self):
        with self.get_db_connection('my_database.db') as conn:
            cursor = conn.cursor()
            info = cursor.execute("PRAGMA table_info(scores)").fetchall()
            if not info:
                return False
            pk = {row[1]: row[5] for row in info}
            if pk.get("subject", 0) > 0:
                return False      # 已经是新结构

            import shutil
            shutil.copyfile('my_database.db', 'my_database.db.bak')

            cursor.execute("PRAGMA foreign_keys = OFF")
            cursor.execute('''
                CREATE TABLE scores_new
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
                    PRIMARY KEY (student_id, exam_id, subject),
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
                )''')
            cursor.execute('''
                INSERT INTO scores_new
                (student_id, exam_id, subject, initialscore, score, rank, headcount, createtime, changetime)
                SELECT student_id, exam_id, subject, initialscore, score, rank, headcount, createtime, changetime
                FROM scores''')
            cursor.execute("DROP TABLE scores")
            cursor.execute("ALTER TABLE scores_new RENAME TO scores")
            cursor.execute("PRAGMA foreign_keys = ON")
            conn.commit()
            return True

    #查询学生数据
    def query_students(self,id,name,Class,grade,telephonenum,email,createtime,changetime):
        #检查是否存在该学生，如果存在则返回该学生信息，否则返回空列表(模糊化处理)
        with self.get_db_connection('my_database.db') as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM students WHERE 1=1"
            params = []
            #检查每个参数是否为None，如果不为None，则加入查询条件
            if id:
                query += " AND id Like ?"
                params.append(f"%{id}%")
            if name:
                query += " AND name Like ?"
                params.append(f"%{name}%")
            if Class:
                query += " AND class Like ?"
                params.append(f"%{Class}%")
            if grade:
                query += " AND grade Like ?"
                params.append(f"%{grade}%")
            if telephonenum:
                query += " AND telephonenum Like ?"
                params.append(f"%{telephonenum}%")
            if email:
                query += " AND email Like ?"
                params.append(f"%{email}%")
            if createtime:
                query += " AND createtime = ?"
                params.append(createtime)
            if changetime:
                query += " AND changetime = ?"
                params.append(changetime)

            cursor.execute(query, params)
            return cursor.fetchall()

    #查询考试数据
    def query_exams(self,id,name,date,createtime,changetime):
        with self.get_db_connection('my_database.db') as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM exams WHERE 1=1"
            params = []
            if id:
                query += " AND id Like ?"
                params.append(f"%{id}%")
            if name:
                query += " AND name Like ?"
                params.append(f"%{name}%")
            if date:
                query += " AND date Like ?"
                params.append(f"%{date}%")
            if createtime:
                query += " AND createtime = ?"
                params.append(createtime)
            if changetime:
                query += " AND changetime = ?"
                params.append(changetime)

            cursor.execute(query, params)
            return cursor.fetchall()

    #查询成绩数据
    def query_scores(self,student_id,exam_id,subject,initialscore,score,rank,headcount,createtime,changetime):
        with self.get_db_connection('my_database.db') as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM scores WHERE 1=1"
            params = []
            if student_id:
                query += " AND student_id Like ?"
                params.append(f"%{student_id}%")
            if exam_id:
                query += " AND exam_id Like ?"
                params.append(f"%{exam_id}%")
            if initialscore is not None:
                query += " AND initialscore Like ?"
                params.append(f"%{initialscore}%")
            if score is not None:
                query += " AND score Like ?"
                params.append(f"%{score}%")
            if rank is not None:
                query += " AND rank Like ?"
                params.append(f"%{rank}%")
            if headcount is not None:
                query += " AND headcount Like ? "
                params.append(f"%{headcount}%")
            if subject:
                query += " AND subject Like ?"
                params.append(f"%{subject}%")
            if createtime:
                query += " AND createtime = ?"
                params.append(createtime)
            if changetime:
                query += " AND changetime = ?"
                params.append(changetime)
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

    #按主键精确判断记录是否存在（注意：不能用 query_xxx，那个是 LIKE 模糊匹配）
    def record_exists(self, type, keys):
        with self.get_db_connection('my_database.db') as conn:
            cursor = conn.cursor()
            if type == "student":
                cursor.execute("SELECT 1 FROM students WHERE id = ?", (keys[0],))
            elif type == "exam":
                cursor.execute("SELECT 1 FROM exams WHERE id = ?", (keys[0],))
            elif type == "score":
                # 传 3 个键 = 按主键精确判断；传 2 个键 = 该生该场考试是否已有任何成绩
                if len(keys) >= 3:
                    cursor.execute("SELECT 1 FROM scores WHERE student_id = ? AND exam_id = ? AND subject = ?",
                                   (keys[0], keys[1], keys[2]))
                else:
                    cursor.execute("SELECT 1 FROM scores WHERE student_id = ? AND exam_id = ?",
                                   (keys[0], keys[1]))
            else:
                return False
            return cursor.fetchone() is not None

    #按主键精确删除一行，返回实际删除的行数
    #（成绩用联合主键 student_id + exam_id，不能用 delete_data，那个会误删该生全部成绩）
    def delete_row(self, type, keys):
        with self.get_db_connection('my_database.db') as conn:
            cursor = conn.cursor()
            if type == "student":
                cursor.execute("DELETE FROM students WHERE id = ?", (keys[0],))
            elif type == "exam":
                cursor.execute("DELETE FROM exams WHERE id = ?", (keys[0],))
            elif type == "score":
                if len(keys) >= 3:
                    cursor.execute("DELETE FROM scores WHERE student_id = ? AND exam_id = ? AND subject = ?",
                                   (keys[0], keys[1], keys[2]))
                else:
                    cursor.execute("DELETE FROM scores WHERE student_id = ? AND exam_id = ?",
                                   (keys[0], keys[1]))
            else:
                return 0
            deleted = cursor.rowcount
            conn.commit()
            return deleted

    #统计某个学生 / 某场考试关联的成绩条数（删除前用于提示级联删除）
    def count_scores(self, student_id=None, exam_id=None):
        with self.get_db_connection('my_database.db') as conn:
            cursor = conn.cursor()
            if student_id is not None:
                cursor.execute("SELECT COUNT(*) FROM scores WHERE student_id = ?", (student_id,))
            elif exam_id is not None:
                cursor.execute("SELECT COUNT(*) FROM scores WHERE exam_id = ?", (exam_id,))
            else:
                cursor.execute("SELECT COUNT(*) FROM scores")
            return cursor.fetchone()[0]

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

    #批量写入（导入 Excel 用）：重复记录自动忽略，返回实际插入条数
    def bulk_insert(self, type, rows):
        if not rows:
            return 0
        now = self.get_localtime()
        with self.get_db_connection('my_database.db') as conn:
            cur = conn.cursor()
            if type == "student":
                sql = ("INSERT OR IGNORE INTO students "
                       "(id, name, class, grade, telephonenum, email, createtime, changetime) "
                       "VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
            elif type == "exam":
                sql = ("INSERT OR IGNORE INTO exams "
                       "(id, name, date, createtime, changetime) VALUES (?, ?, ?, ?, ?)")
            elif type == "score":
                sql = ("INSERT OR IGNORE INTO scores "
                       "(student_id, exam_id, subject, initialscore, score, rank, headcount, createtime, changetime) "
                       "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")
            else:
                return 0

            data = [tuple(row) + (now, now) for row in rows]
            before = conn.total_changes
            cur.executemany(sql, data)
            conn.commit()
            return conn.total_changes - before

    #取某一类的全部主键（批量导入时预检外键用）
    def all_ids(self, type):
        with self.get_db_connection('my_database.db') as conn:
            cur = conn.cursor()
            if type == "student":
                cur.execute("SELECT id FROM students")
            elif type == "exam":
                cur.execute("SELECT id FROM exams")
            elif type == "score":
                cur.execute("SELECT student_id FROM scores")
            else:
                return set()
            return {row[0] for row in cur.fetchall()}

    # ==================================================================
    # 统计分析（侧边栏数据卡 / 分析页）
    # ==================================================================
    def overview_stats(self):
        with self.get_db_connection('my_database.db') as conn:
            cur = conn.cursor()
            students = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
            exams = cur.execute("SELECT COUNT(*) FROM exams").fetchone()[0]
            scores = cur.execute("SELECT COUNT(*) FROM scores").fetchone()[0]
            avg = cur.execute("SELECT AVG(score) FROM scores").fetchone()[0] or 0
            pass_rate = cur.execute(
                "SELECT SUM(CASE WHEN score >= 60 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) FROM scores"
            ).fetchone()[0] or 0
            classes = cur.execute("SELECT COUNT(DISTINCT class) FROM students").fetchone()[0]
            subjects = cur.execute("SELECT COUNT(DISTINCT subject) FROM scores").fetchone()[0]
            return {
                "students": students,
                "exams": exams,
                "scores": scores,
                "classes": classes,
                "subjects": subjects,
                "avg_score": round(avg, 1),
                "pass_rate": round(pass_rate, 1),
            }

    def subject_stats(self):
        with self.get_db_connection('my_database.db') as conn:
            cur = conn.cursor()
            rows = cur.execute('''
                SELECT subject,
                       COUNT(*),
                       ROUND(AVG(score), 1),
                       MAX(score),
                       MIN(score),
                       ROUND(SUM(CASE WHEN score >= 60 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1)
                FROM scores
                GROUP BY subject
                ORDER BY AVG(score) DESC''').fetchall()
            return [
                {"subject": r[0], "count": r[1], "avg": r[2],
                 "max": r[3], "min": r[4], "pass_rate": r[5]}
                for r in rows
            ]

    def class_ranking(self):
        with self.get_db_connection('my_database.db') as conn:
            cur = conn.cursor()
            rows = cur.execute('''
                SELECT s.class,
                       COUNT(DISTINCT s.id),
                       COUNT(c.student_id),
                       ROUND(AVG(c.score), 1),
                       ROUND(SUM(CASE WHEN c.score >= 60 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1)
                FROM students s
                JOIN scores c ON c.student_id = s.id
                GROUP BY s.class
                ORDER BY AVG(c.score) DESC''').fetchall()
            return [
                {"class_name": r[0], "students": r[1], "scores": r[2],
                 "avg": r[3], "pass_rate": r[4]}
                for r in rows
            ]

    def exam_trend(self, limit=5):
        with self.get_db_connection('my_database.db') as conn:
            cur = conn.cursor()
            rows = cur.execute('''
                SELECT c.exam_id, e.name, e.date, ROUND(AVG(c.score), 1)
                FROM scores c
                JOIN exams e ON e.id = c.exam_id
                GROUP BY c.exam_id
                ORDER BY e.date DESC, c.exam_id DESC
                LIMIT ?''', (limit,)).fetchall()
            return [
                {"exam_id": r[0], "name": r[1], "date": r[2], "avg": r[3]}
                for r in rows
            ]

    # ==================================================================
    # 全局快捷搜索（跨三张表）
    # ==================================================================
    def quick_search(self, text, limit=20):
        like = f"%{text}%"
        results = []
        with self.get_db_connection('my_database.db') as conn:
            cur = conn.cursor()
            for row in cur.execute(
                "SELECT id, name, class FROM students WHERE id LIKE ? OR name LIKE ? LIMIT ?",
                (like, like, limit),
            ):
                results.append({
                    "kind": "学生", "keys": [row[0]],
                    "title": row[0], "subtitle": f"{row[1]} · {row[2]}",
                })
            for row in cur.execute(
                "SELECT id, name, date FROM exams WHERE id LIKE ? OR name LIKE ? LIMIT ?",
                (like, like, limit),
            ):
                results.append({
                    "kind": "考试", "keys": [row[0]],
                    "title": row[0], "subtitle": f"{row[1]} · {row[2]}",
                })
            for row in cur.execute(
                """SELECT student_id, exam_id, subject, score FROM scores
                   WHERE student_id LIKE ? OR exam_id LIKE ? OR subject LIKE ?
                   LIMIT ?""",
                (like, like, like, limit),
            ):
                results.append({
                    "kind": "成绩", "keys": [row[0], row[1], row[2]],
                    "title": f"{row[0]} · {row[1]} · {row[2]}",
                    "subtitle": f"成绩 {row[3]}",
                })
        return results[:limit]


if __name__ == "__main__":
    db_manager = DatabaseManager('my_database.db')
    a = db_manager.query_students(None, None, None,"2", None, None, None, None)
    print(a)