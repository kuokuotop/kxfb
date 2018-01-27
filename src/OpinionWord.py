class OpinionWord:

    def __init__(self, word, features_modified=set(), sentiments_modified=set(), sentences_from=set(), extracting_rules = set()):
        self.word = str(word)
        self.features_modified = features_modified
        self.sentiments_modified = sentiments_modified
        self.sentences_from = sentences_from
        self.extracting_rules = extracting_rules

    def get_word(self):
        return self.word

    def get_features(self):
        return self.features_modified

    def __str__(self):
        return '(' + self.word + ')'

    def __repr__(self):
        return '(' + self.word + ')'

    def __eq__(self, other):
        if self.word.lower() == other.word.lower():
            return True
        return False

    def __hash__(self):
        return hash(self.word.lower())
