from enum import Enum
from dataclasses import dataclass
from typing import Optional

from tokenization import Tokenizer

# Leitura e execução
try:
    with open("test.tt", "r") as file:
        content = file.read()
except FileNotFoundError:
    print("Arquivo não encontrado.")
    content = ""

try:
    tokenizer = Tokenizer(content)
    tokens = tokenizer.tokenizer()
    for token in tokens:
        print(token)
except RuntimeError as e:
    print(f"Erro léxico: {e}")
