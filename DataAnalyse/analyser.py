# 成绩分析器
class ScoreAnalyser:
    def __init__(self, scores):
        self.scores = scores

    #平均分
    def average_score(self):
        if not self.scores:
            return 0
        return sum(self.scores) / len(self.scores)
    
    #最高分
    def highest_score(self):
        if not self.scores:
            return 0
        return max(self.scores)
    
    #最低分
    def lowest_score(self):
        if not self.scores:
            return 0
        return min(self.scores)

    #成绩分布
    def score_distribution(self):
        distribution = {}
        for score in self.scores:
            distribution[score] = distribution.get(score, 0) + 1
        return distribution
    
    #及格率
    def pass_rate(self, passing_score=60):
        if not self.scores:
            return 0
        passed = sum(1 for score in self.scores if score >= passing_score)
        return passed / len(self.scores) * 100
    
    #成绩等级分布
    def grade_distribution(self):
        distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for score in self.scores:
            if score >= 90:
                distribution["A"] += 1
            elif score >= 80:
                distribution["B"] += 1
            elif score >= 70:
                distribution["C"] += 1
            elif score >= 60:
                distribution["D"] += 1
            else:
                distribution["F"] += 1
        return distribution
    
    #综合统计
    def score_statistics(self):
        return {
            "average": self.average_score(),
            "highest": self.highest_score(),
            "lowest": self.lowest_score(),
            "distribution": self.score_distribution(),
            "pass_rate": self.pass_rate(),
            "grade_distribution": self.grade_distribution()
        }
    
# 考试分析器
class ExamAnalyser:
    def __init__(self, scores):
        self.scores = scores

    #考试密度
    def exam_density(self):
        density = {}
        for score in self.scores:
            density[score["exam_id"]] = density.get(score["exam_id"], 0) + 1
        return density
    
#学生分析器
class StudentAnalyser:
    def __init__(self, student_id):
        self.student_id = student_id

    #学生年级分布
    def grade_distribution(self, students):
        distribution = {}
        for student in students:
            if student["id"] == self.student_id:
                grade = student["grade"]
                distribution[grade] = distribution.get(grade, 0) + 1
        return distribution
    
    #学生班级分布
    def class_distribution(self, students):
        distribution = {}
        for student in students:
            if student["id"] == self.student_id:
                class_name = student["class"]
                distribution[class_name] = distribution.get(class_name, 0) + 1
        return distribution
    
    

    