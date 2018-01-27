class SentencePruning:
    def __init__(self, sentenceId, pruningIndex):
        self.sentenceId = sentenceId
        self.pruningIndex = pruningIndex

    def get_sentenceid(self):
        return self.sentenceId

    def get_index(self):
        return self.pruningIndex