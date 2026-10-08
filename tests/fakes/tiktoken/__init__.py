"""Offline stand-in for tiktoken (the real one downloads its vocabulary). Used by tests only."""
class _Enc:
    def encode(self, text):
        return [hash(w) % 50000 for w in text.replace("-", " - ").split()]
    def decode(self, toks):
        return "".join(chr(97 + (t % 26)) for t in toks)
def get_encoding(name):
    return _Enc()
