from __future__ import annotations
from typing import Final, Any, Callable
from pygame_dom.cache.registry import FUNCTION_REGISTRY, STATE_REGISTRY
import ast
import operator

OPS: Final[dict] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod
}

COMPARE_OPS: Final[dict] = {
    ast.Gt: operator.gt,
    ast.Lt: operator.lt,
    ast.GtE: operator.ge,
    ast.LtE: operator.le,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne
}

SAFE_FUNCTIONS: Final[dict] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,

    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,

    "len": len,
    "range": range,
    "enumerate": enumerate,
    "zip": zip,

    "sorted": sorted,
    "reversed": reversed,

    "all": all,
    "any": any,

    "repr": repr,
    "ord": ord,
    "chr": chr,

    "format": format
}

SAFE_METHODS: Final[dict] = {
    dict: {"get", "keys", "values", "items"},
    list: {"append", "count", "index"},
    str: {"lower", "upper", "strip", "split"}
}

def safe_eval_wrapper(expr: str, involved_states: list[str]) -> Any:
    context: dict = {**SAFE_FUNCTIONS}

    for key, value in STATE_REGISTRY.items():
        if key in context:
            continue

        context[key] = value.value

    for key, value in FUNCTION_REGISTRY.items():
        if key in context:
            continue

        context[key] = value
    
    for involved_state in involved_states:
        if involved_state in context:
            continue

        return expr
    
    return safe_eval(expr, context)

def safe_eval(expr: str, context: dict) -> Any:
    tree: ast.AST = ast.parse(expr, mode="eval")
    evaluator: SafeEvaluator = SafeEvaluator(context)

    return evaluator.visit(tree)

class SafeEvaluator(ast.NodeVisitor):
    def __init__(self, context: dict) -> SafeEvaluator:
        self.context = context
    
    def visit_Expression(self, node: Any) -> Any:
        return self.visit(node.body)
    
    def visit_BinOp(self, node: Any) -> Any:
        left: Any = self.visit(node.left)
        right: Any = self.visit(node.right)

        return OPS[type(node.op)](left, right)
    
    def visit_Name(self, node: Any) -> Any:
        return self.context[node.id]
    
    def visit_Constant(self, node: Any) -> Any:
        return node.value
    
    def visit_Subscript(self, node: Any) -> Any:
        value: Any = self.visit(node.value)
        index: Any = self.visit(node.slice)

        return value[index]
    
    def visit_Index(self, node: Any) -> Any:
        return self.visit(node.value)
    
    def visit_Attribute(self, node: Any) -> Any:
        value: Any = self.visit(node.value)
        attr: str = node.attr

        if attr.startswith("__"):
            raise ValueError("Can not access attributes with __")

        return getattr(value, attr)
    
    def visit_Call(self, node: Any) -> Any:
        method: Callable = None

        if isinstance(node.func, ast.Attribute):
            obj: Any = self.visit(node.func.value)
            method_name: str = node.func.attr

            if method_name.startswith("_") or method_name.startswith("__"):
                raise ValueError("Cannot call method with _ or __")

            allowed: list[str] = SAFE_METHODS.get(type(obj), set())

            if method_name not in allowed:
                raise ValueError(f"Method {method_name} not allowed for {type(obj)}")

            method = getattr(obj, method_name)
        else:
            method = self.visit(node.func)

            if method not in self.context.values():
                raise ValueError(f"Function is not supported")

        args: list = [self.visit(arg) for arg in node.args]

        kwargs: dict = {}
        for kw in node.keywords:
            if kw.arg is None:
                raise ValueError("**kwargs unpacking is not allowed")
            
            kwargs[kw.arg] = self.visit(kw.value)

        if not callable(method):
            raise TypeError(f"{method} is not callable")
        
        return method(*args, **kwargs)
    
    def visit_IfExp(self, node: Any) -> Any:
        condition: Any = self.visit(node.test)

        if condition:
            return self.visit(node.body)
        
        return self.visit(node.orelse)
    
    def visit_Compare(self, node: Any) -> Any:
        left: Any = self.visit(node.left)

        for op, comparator in zip(node.ops, node.comparators):
            right: Any = self.visit(comparator)

            if not COMPARE_OPS[type(op)](left, right):
                return False
            
            left = right
        
        return True
    
    def visit_BoolOp(self, node: Any) -> Any:
        if isinstance(node.op, ast.And):
            return all(self.visit(v) for v in node.values)
        elif isinstance(node.op, ast.Or):
            return any(self.visit(v) for v in node.values)

    def visit_UnaryOp(self, node: Any) -> Any:
        if isinstance(node.op, ast.Not):
            return not self.visit(node.operand)

    def generic_visit(self, node: Any) -> Any:
        raise ValueError(f"Unsupported expression: {type(node).__name__}")

def get_variables(expr: str) -> list:
    tree: ast.AST = ast.parse(expr, mode="eval")
    collector: VarCollector = VarCollector()

    collector.visit(tree)

    return list(collector.vars)

class VarCollector(ast.NodeVisitor):
    def __init__(self) -> VarCollector:
        self.vars = set()
    
    def visit_Name(self, node: Any) -> None:
        if not (hasattr(node, "parent") and isinstance(node.parent, ast.Call) and node.parent.func is node):
            if isinstance(node.ctx, ast.Load):
                self.vars.add(node.id)

        self.generic_visit(node)
    
    def visit(self, node: Any) -> None:
        for child in ast.iter_child_nodes(node):
            child.parent = node
        
        super().visit(node)

#print(safe_eval("str('a').upper()", {**SAFE_FUNCTIONS}))
#print(safe_eval("", {**SAFE_FUNCTIONS}))

#print(get_variables("1 + x + len(y) + my_func(w) + lis[0] + clas.attrib"))