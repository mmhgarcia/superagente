from typing import Optional

class BaseSkill:
    id: str

    def match(self, message: str) -> bool:
        raise NotImplementedError

    def execute(self, message: str, history: Optional[list] = None) -> str:
        raise NotImplementedError
