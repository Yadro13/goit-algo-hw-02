def check_delimiters(expression):
    stack = []
    # Відповідність відкритих і закритих дужок
    pairs = {')': '(', ']': '[', '}': '{'}

    for char in expression:
        if char in '([{':
            stack.append(char)
        elif char in ')]}':
            if not stack:
                return "Несиметрично (зайва закриваюча дужка)"
            if stack.pop() != pairs[char]:
                return "Несиметрично (невірна пара дужок)"

    if stack:
        return "Несиметрично (є незакриті дужки)"
    return "Симетрично"


# Приклади перевірки
examples = [
    "( ){[ 1 ]( 1 + 3 )( ){ }}",     # Симетрично
    "( 23 ( 2 - 3);",                # Несиметрично
    "( 11 }",                        # Несиметрично
    "((({[]})))",                   # Симетрично
    "{[()()]}",                     # Симетрично
    "([)]",                         # Несиметрично
]

for exp in examples:
    print(f"{exp}: {check_delimiters(exp)}")
