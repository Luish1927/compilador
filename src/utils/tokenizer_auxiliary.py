from typing import Optional

class TokenizerAuxiliary:
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.index = 0

    def peak(self, ahead: int = 1) -> Optional[str]:
        """
        Returns the next character from the input without consuming it.
        If there are no more characters, returns None.
        """
        peek_index = self.index + ahead - 1
        if peek_index >= len(self.source_code):
            return None
        else:
            return self.source_code[peek_index]


    def consume(self) -> str:
        result = self.source_code[self.index]
        self.index += 1
        return result
    
    def create_buffer(self, token: list):
        buffer = ''.join(token)
        token.clear()
        return buffer