import ast
import operator
import math
import sys

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

ALLOWED_NAMES = {
    'sqrt': math.sqrt,
}

class SafeEvaluator(ast.NodeVisitor):
    def visit(self, node):
        if isinstance(node, ast.Expression):
            return self.visit(node.body)
        return super().visit(node)

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)
        if op_type in OPERATORS:
            try:
                return OPERATORS[op_type](left, right)
            except ZeroDivisionError:
                raise ZeroDivisionError("División por cero")
        raise ValueError(f"Operador no permitido: {op_type}")

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op_type = type(node.op)
        if op_type in OPERATORS:
            return OPERATORS[op_type](operand)
        raise ValueError(f"Operador unario no permitido: {op_type}")

    def visit_Num(self, node):
        return node.n

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Constante no numérica no permitida")

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Llamada a función inválida")
        func_name = node.func.id
        if func_name not in ALLOWED_NAMES:
            raise ValueError(f"Función no permitida: {func_name}")
        func = ALLOWED_NAMES[func_name]
        if len(node.args) != 1:
            raise ValueError(f"{func_name} requiere 1 argumento")
        arg = self.visit(node.args[0])
        if func_name == 'sqrt' and arg < 0:
            raise ValueError("No se puede calcular la raíz cuadrada de un número negativo")
        return func(arg)

    def visit_Name(self, node):
        if node.id in ALLOWED_NAMES:
            return ALLOWED_NAMES[node.id]
        raise ValueError(f"Nombre no permitido: {node.id}")

    def generic_visit(self, node):
        raise ValueError(f"Expresión no permitida: {node.__class__.__name__}")


def safe_eval(expr: str):
    try:
        parsed = ast.parse(expr, mode='eval')
    except SyntaxError:
        raise ValueError("Sintaxis inválida")
    evaluator = SafeEvaluator()
    return evaluator.visit(parsed)


def main():
    print("Calculadora segura en consola. Escribe 'salir' para terminar.")
    print("Soporta: +, -, *, /, **, sqrt(x)\nEjemplo: 2 ** 3  o  sqrt(9)")
    while True:
        try:
            s = input('> ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nSaliendo...')
            break
        if not s:
            continue
        if s.lower() in ('salir', 'exit', 'quit'):
            print('Saliendo...')
            break
        try:
            result = safe_eval(s)
            print(result)
        except ZeroDivisionError:
            print('Error: División por cero')
        except ValueError as e:
            print(f'Error: {e}')
        except Exception as e:
            print(f'Error inesperado: {e}')


def _self_test():
    tests = {
        '5 + 3': 8,
        '10 - 2 * 3': 4,
        '2 ** 3': 8,
        '9 / 3': 3.0,
        'sqrt(16)': 4.0,
    }
    print('Ejecutando pruebas automáticas...')
    for expr, expected in tests.items():
        try:
            out = safe_eval(expr)
            ok = math.isclose(out, expected, rel_tol=1e-9)
            print(f"{expr} => {out} (esperado: {expected}) {'OK' if ok else 'FALLÓ'}")
        except Exception as e:
            print(f"{expr} => ERROR: {e}")
    # errores esperados
    error_tests = ['10 / 0', 'sqrt(-4)', 'abc + 5']
    for expr in error_tests:
        try:
            out = safe_eval(expr)
            print(f"{expr} => {out} (ERROR: se esperaba excepción)")
        except Exception as e:
            print(f"{expr} => excepción como se esperaba: {e}")


if __name__ == '__main__':
    if '--test' in sys.argv:
        _self_test()
    else:
        main()
