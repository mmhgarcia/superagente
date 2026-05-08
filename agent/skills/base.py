from typing import Optional

class BaseSkill:
    id: str

    def match(self, message: str) -> bool:
        raise NotImplementedError

    def execute(self, message: str, history: Optional[list] = None) -> str:
        raise NotImplementedError

    def execute_tool(self, args: dict) -> str:
        query = (
            args.get("query")
            or args.get("texto")
            or args.get("expresion")
            or args.get("expr")
            or ""
        )
        if not query and "numeros" in args:
            nums = args["numeros"]
            op = args.get("operacion", "")
            query = f"{nums[0]} {op} {nums[1]}" if len(nums) >= 2 else str(nums[0])
        return self.execute(query, history=None)
