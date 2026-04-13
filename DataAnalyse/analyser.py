class ScoreAnalyser:
    def __init__(self, scores):
        self.scores = scores

    def average_score(self):
        if not self.scores:
            return 0
        return sum(self.scores) / len(self.scores)

    def highest_score(self):
        if not self.scores:
            return 0
        return max(self.scores)

    def lowest_score(self):
        if not self.scores:
            return 0
        return min(self.scores)

    def score_distribution(self):
        distribution = {}
        for score in self.scores:
            distribution[score] = distribution.get(score, 0) + 1
        return distribution