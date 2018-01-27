class AnnotatedReview:
    def __init__(self, hash_code, sentence, feature_list, opinion_list):
        self.hash_code = hash_code
        self.sentence = sentence
        self.feature_list = feature_list
        self.opinion_list = opinion_list

    def __str__(self):
        return self.sentence

    def __repr__(self):
        return self.sentence

    def __eq__(self, other):
        if self.sentence() == other.sentence():
            return True
        return False

    def __hash__(self):
        return hash(self.sentence)
