def fizzbuzz(num: int):
    """
    Return 'Fizz' if `num` is divisible by 3, 'Buzz' if `num` is divisible by 5, 'FizzBuzz' if `num` is divisible both by 3 and 5.
    If `num` isn't divisible neither by 3 nor by 5, return `num`.
    Example:
        fizzbuzz(3) # Fizz
        fizzbuzz(5) # Buzz
        fizzbuzz(15) # FizzBuzz
        fizzbuzz(8) # 8
    """
    ret = ""
    if num % 3 == 0:
        ret += "Fizz"
    if num % 5 == 0:
        ret += "Buzz"
    if ret == "":
        ret = num
    return ret


def fibonacci(n: int):
    """
    Return the `n`-th Fibonacci number (counting from 0).
    Example:
        fibonacci(0) == 0
        fibonacci(1) == 1
        fibonacci(2) == 1
        fibonacci(3) == 2
        fibonacci(4) == 3
    """
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)


def dot_product(a, b):
    """
    Calculate the dot product of `a` and `b`.
    Assume that `a` and `b` have same length.
    Hint:
        lookup `zip` function
    Example:
        dot_product([1, 2, 3], [0, 3, 4]) == 1*0 + 2*3 + 3*4 == 18
    """
    joined = zip(a, b)
    return sum([x * y for x, y in joined])


def redact(data: str, chars: str):
    """
    Return `data` with all characters from `chars` replaced by the character 'x'.
    Characters are case sensitive.
    Example:
        redact("Hello world!", "lo")        # Hexxx wxrxd!
        redact("Secret message", "mse")     # Sxcrxt xxxxagx
    """
    letters = list(chars)
    for letter in letters:
        data = data.replace(letter, "x")
    return data


def count_words(data: str):
    """
    Return a dictionary that maps word -> number of occurences in `data`.
    Words are separated by spaces (' ').
    Characters are case sensitive.

    Hint:
        "hi there".split(" ") -> ["hi", "there"]

    Example:
        count_words('this car is my favourite what car is this')
        {
            'this': 2,
            'car': 2,
            'is': 2,
            'my': 1,
            'favourite': 1,
            'what': 1
        }
    """
    if data == "":
        return {}
    
    split = data.split(" ")
    ret = {}
    for word in split:
        if word in ret:
            ret[word] += 1
        else:
            ret[word] = 1
    return ret


def bonus_fizzbuzz(num: int):
    """
    Implement the `fizzbuzz` function.
    `if`, match-case and cycles are not allowed.
    """
    ret = ""
    try:
        ret += ["Fizz"][num % 3]
    except IndexError:
        pass
    
    try:
        ret += ["Buzz"][num % 5]
    except IndexError:
        pass
    
    try:
        return [num][len(ret)]
    except IndexError:
        return ret


def bonus_utf8(cp: int):
    """
    Encode `cp` (a Unicode code point) into 1-4 UTF-8 bytes - you should know this from `Základy číslicových systémů (ZDS)`.
    Example:
        bonus_utf8(0x01) == [0x01]
        bonus_utf8(0x1F601) == [0xF0, 0x9F, 0x98, 0x81]
    
    
    https://courses.grainger.illinois.edu/cs340/fa2024/text/utf8.html
    """
    length = cp.bit_length()
    if length <= 7:
        return [cp]
    elif length <= 11:
        return [0b11000000 | (cp >> 6), 0b10000000 | (cp & 0b111111)]
    elif length <= 16:
        return [0b11100000 | (cp >> 12), 0b10000000 | ((cp >> 6) & 0b111111), 0b10000000 | (cp & 0b111111)]
    elif length <= 21:
        return [0b11110000 | (cp >> 18), 0b10000000 | ((cp >> 12) & 0b111111), 0b10000000 | ((cp >> 6) & 0b111111), 0b10000000 | (cp & 0b111111)]
    else:
        return []