def brackets_depth(input: str) -> list[int]:
    """
    Given a string consisting of matched nested parentheses (<{[]}>), write a Python program to compute
    the depth of each leaf and return it in a list.

    Examples:
        '' = [0]
        '()' = [1]
        '[](()){}' = [1,2,1]
        '[]<(()){}>' = [1,3,2]

    Don't validate input for errors. You will always get a correct input.

    Hint: You can count the sequence of opening (+=1) and closing (-=1) brackets, or you can use a stack.
    """
    climb = ['(', '[', '{', '<']
    fall = [')', ']', '}', '>']
    found: list[int] = []
    start = 0

    while input:
        dist, rest = move(input, climb)
        start += dist
        found.append(start)
        input = rest
        dist, rest = move(input, fall)
        start -= dist
        input = rest
    return found or [0]

def move(input: str, over: list[str]) -> (int, str):
    b = input[0]
    dist = 0
    while b and b in over:
        dist += 1
        try: b = input[dist]
        except IndexError: break
    return dist, input[dist:]


def validate(input: str) -> bool:
    """
    Validate an input consisting of matched nested parentheses and strings (<{["\'\""]}>) containing
    any character and escape sequences. Strings and escape sequences follow python rules, that is
    any double quoted strings can use single quotes without escaping and any single quoted strings
    can use double quotes without escaping.

    Examples:
        ()   = True
        (<>) = True
        (<)> = False # ) does not close <
        ("") = True
        "(") = False # no opening (
        "'" = True
        "\"" = True

    Return True if the input string is in a valid format, otherwise return False.

    Hint: Use a stack.
    """
    def check_string(char: str, quote: str):
        if any(q) and q[-1] == quote and char != quote:
            return True

        if char == quote:
            if len(q) == 0 or q[-1] != quote:
                q.append(quote)
            else:
                q.pop()
            return True
        return False

    opening = ['(', '[', '{', '<']
    closing = [')', ']', '}', '>']
    q: list[str] = []
    for char in input:
        if check_string(char, '"') or check_string(char, '\''):
            continue

        if char in closing:
            if len(q) == 0 or char != q[-1]:
                return False
            else:
                q.pop()
        elif char in opening:
            q.append(closing[opening.index(char)])
        else:
            return False
    return len(q) == 0


