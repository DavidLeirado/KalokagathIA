


class TextPredictor():
    def __init__(self, text, model, tokenizer):
        self.text = text
        self.model = model
        self.tokenizer = tokenizer

    def fragment(self):
        # call tokenize
        token_list = []
        return token_list

    def tokenize(self, fragment):
        ...

    def predict(self, token_list):
        # iter
        # pred = model.predict
        ...
        