import pytest
from tasks import brackets_depth, validate


def test_brackets_depth():
    input = ''
    assert brackets_depth(input) == [0]
    input = '()'
    assert brackets_depth(input) == [1]
    input = '(<>)<>'
    assert brackets_depth(input) == [2, 1]
    input = '(<>)[<>]{{}}'
    assert brackets_depth(input) == [2, 2, 2]
    input = '([]<>{})'
    assert brackets_depth(input) == [2, 2, 2]
    input = '{(<>)[<>]{{}}}'
    assert brackets_depth(input) == [3, 3, 3]
    input = '{(<>)<[<>]>{{}}}<>'
    assert brackets_depth(input) == [3, 4, 3, 1]
    input = '(((((<{[]}>))))){}'
    assert brackets_depth(input) == [8, 1]
    input = '(((((<{[]}>))))){}(((((<{[]}>)))))<[]>(((((<{[]}>)))))'
    assert brackets_depth(input) == [8, 1, 8, 2, 8]


def test_validate_round_brackets():
    input = ''
    assert validate(input) == True
    input = '('
    assert validate(input) == False
    input = '()'
    assert validate(input) == True
    input = '()('
    assert validate(input) == False
    input = '()()'
    assert validate(input) == True
    input = '((())())'
    assert validate(input) == True
    input = '((())())('
    assert validate(input) == False


def test_validate_brackets():
    input = '['
    assert validate(input) == False
    input = '[]'
    assert validate(input) == True
    input = '[]['
    assert validate(input) == False
    input = '[][]'
    assert validate(input) == True
    input = '[[[]][]]'
    assert validate(input) == True
    input = '][[[]][]]['
    assert validate(input) == False

    input = '{'
    assert validate(input) == False
    input = '{}'
    assert validate(input) == True
    input = '{}{'
    assert validate(input) == False
    input = '{}{}'
    assert validate(input) == True
    input = '{{{}}{}}'
    assert validate(input) == True
    input = '}{{{}}{}}{'
    assert validate(input) == False

    input = '<'
    assert validate(input) == False
    input = '<>'
    assert validate(input) == True
    input = '<><'
    assert validate(input) == False
    input = '<><>'
    assert validate(input) == True
    input = '<<<>><>>'
    assert validate(input) == True
    input = '><<<>><>><'
    assert validate(input) == False


def test_validate_quotes():
    input = 'a'
    assert validate(input) == False

    input = '"a"'
    assert validate(input) == True
    input = '"'
    assert validate(input) == False
    input = '{""}'
    assert validate(input) == True
    input = '<">"'
    assert validate(input) == False
    input = '[]<>("asdf")'
    assert validate(input) == True
    input = '"asdf'
    assert validate(input) == False
    input = '"asdf"asdf"'
    assert validate(input) == False


def test_validate_mix_quotes():
    input = "'a'"
    assert validate(input) == True
    input = "'"
    assert validate(input) == False
    input = "{''}"
    assert validate(input) == True
    input = "<'>'"
    assert validate(input) == False
    input = "[]<>('asdf')"
    assert validate(input) == True
    input = "'asdf"
    assert validate(input) == False
    input = "'asdf'asdf'"
    assert validate(input) == False

    input = '"\'"'  # "'"
    assert validate(input) == True
    input = '"\'"\''  # "'"'
    assert validate(input) == False
    input = '"asdf\'"'  # "asdf'"
    assert validate(input) == True
    input = '(<\'>{["asdf"]})'  # (<'>{["asdf"]})
    assert validate(input) == False
    input = '(<\'as"df\'>{["\'"()]})'  # (<'as"df'>{["'"()]})
    assert validate(input) == True
    input = '""()\'\'{}"'  # ""()''{}"
    assert validate(input) == False
    input = '"as\'df"()\'<{[(\'{}'  # "as'df"()'<{[('{}
    assert validate(input) == True
    input = '"as\'df"()\'<{[(\'{asdf}'  # "as'df"()'<{[('{asdf}
    assert validate(input) == False


def test_validate_escape_quotes():
    input = '"\\""'  # "\""
    assert validate(input) == True
    input = '"\\"\\"'  # "\"\"
    assert validate(input) == False
    input = '(<\'asdf\\\'asdf\'>{[""]})'  # (<'asdf\'asdf'>{[""]})
    assert validate(input) == True
    input = '<("\\"")>{[\'asdf\']}'  # <("\"")>{['asdf']}
    assert validate(input) == True
    input = '<(\\")>{[\'asdf\']}'  # <(\")>{['asdf']}
    assert validate(input) == False
    input = '{[\\"\')>{[\'asdf\']}'  # {[\"')>{['asdf']}
    assert validate(input) == False
    input = '{[\')>{[\\\'asdf\']}'  # {[')>{[\'asdf']}
    assert validate(input) == True
    input = '{[\')>{[\\"asdf\']}'  # {[')>{[\"asdf']}
    assert validate(input) == True