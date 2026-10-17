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

    # ==================================================================
    # 增 / 删：统一入口（界面只负责收集和展示，业务校验放在这一层）
    # ==================================================================
    CONTENT_TO_TYPE = {"学生": "student", "考试": "exam", "成绩": "score"}

    def add_record(self, content, values):
        """新增一条记录。values 顺序与数据库列一致（不含时间戳）。

        返回 (是否成功, 中文提示)
        """
        kind = self.CONTENT_TO_TYPE.get(content)
        if kind is None:
            return False, f"未知的数据类型：{content}"

        try:
            # ---- 主键重复 / 关联记录是否存在 ----
            if kind == "student":
                if self.db_manager.record_exists("student", [values[0]]):
                    return False, f"编号 {values[0]} 已存在，请换一个编号"
            elif kind == "exam":
                if self.db_manager.record_exists("exam", [values[0]]):
                    return False, f"考试编号 {values[0]} 已存在，请换一个编号"
            else:
                student_id, exam_id, subject = values[0], values[1], values[2]
                if not self.db_manager.record_exists("student", [student_id]):
                    return False, f"学号 {student_id} 不存在，请先到「学生」里添加"
                if not self.db_manager.record_exists("exam", [exam_id]):
                    return False, f"考试编号 {exam_id} 不存在，请先到「考试」里添加"
                if self.db_manager.record_exists("score", [student_id, exam_id, subject]):
                    return False, f"{student_id} 在 {exam_id} 的{subject}成绩已存在，请改用修改"

            error = self.db_manager.insert_data(tuple(values), kind)
            if error:
                return False, f"保存失败：{error}"
            return True, "添加成功"
        except Exception as exc:
            return False, f"添加失败：{exc}"

    def update_record(self, content, values):
        """修改一条记录（主键不可改）。values 顺序与数据库列一致。

        返回 (是否成功, 中文提示)
        """
        kind = self.CONTENT_TO_TYPE.get(content)
        if kind is None:
            return False, f"未知的数据类型：{content}"

        if kind == "score":
            keys = list(values[:3])
        else:
            keys = [values[0]]

        if not self.db_manager.record_exists(kind, keys):
            return False, "这条记录已经不存在了，可能刚被删除"

        try:
            updated = self.db_manager.update_row(tuple(values), kind)
            if not updated:
                return False, "没有更新任何记录"
            return True, "修改已保存"
        except Exception as exc:
            return False, f"修改失败：{exc}"

    def delete_records(self, content, keys_list):
        """按主键批量删除。返回 (删除条数, 中文提示)"""
        kind = self.CONTENT_TO_TYPE.get(content)
        if kind is None:
            return 0, f"未知的数据类型：{content}"

        deleted = 0
        for keys in keys_list:
            try:
                deleted += self.db_manager.delete_row(kind, keys) or 0
            except Exception as exc:
                return deleted, f"删除过程中出错：{exc}"

        if deleted == 0:
            return 0, "没有删除任何记录（可能已经被删除）"
        return deleted, f"已删除 {deleted} 条记录"

    def count_related_scores(self, content, keys):
        """删除前统计会被级联删除的成绩条数（学生、考试会带走成绩）"""
        if content == "学生":
            return self.db_manager.count_scores(student_id=keys[0])
        if content == "考试":
            return self.db_manager.count_scores(exam_id=keys[0])
        return 0

    # ==================================================================
    # 统计 / 搜索 / 批量导入
    # ==================================================================
    def overview_stats(self):
        return self.db_manager.overview_stats()

    def subject_stats(self):
        return self.db_manager.subject_stats()

    def class_ranking(self):
        return self.db_manager.class_ranking()

    def exam_trend(self, limit=5):
        return self.db_manager.exam_trend(limit)

    def quick_search(self, text, limit=20):
        text = (text or "").strip()
        if not text:
            return []
        return self.db_manager.quick_search(text, limit)

    def import_rows(self, content, rows):
        """批量导入。rows 为数据库列顺序的元组列表（不含时间戳）。

        返回 (成功, 重复跳过, 无效跳过)
        """
        kind = self.CONTENT_TO_TYPE.get(content)
        if kind is None:
            return 0, 0, 0

        invalid = 0
        prepared = []

        if kind == "score":
            # 成绩要预检外键，否则 outer join 会整批失败
            student_ids = self.db_manager.all_ids("student")
            exam_ids = self.db_manager.all_ids("exam")
            seen = set()
            for row in rows:
                key = (str(row[0]), str(row[1]), str(row[2]))
                if key in seen or key[0] not in student_ids or key[1] not in exam_ids:
                    invalid += 1
                    continue
                seen.add(key)
                prepared.append(tuple(row))
        else:
            for row in rows:
                prepared.append(tuple(row))

        inserted = self.db_manager.bulk_insert(kind, prepared)
        return inserted, len(prepared) - inserted, invalid