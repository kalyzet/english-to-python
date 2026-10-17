"""Regression tests for conditional code generation.

Covers the bug where "is" was replaced before compound phrases:
"age is greater than 18" used to become "age == > 18" (invalid Python).
"""

import pytest

from ttc import TranslationEngine
from ttc.engine.generator import CodeGenerator


@pytest.mark.parametrize(
    "condition_text,expected",
    [
        ("age is greater than 18", "age > 18"),
        ("age greater than 18", "age > 18"),
        ("age is less than 18", "age < 18"),
        ("age is 18", "age == 18"),
        ("age is equal to 18", "age == 18"),
        ("count equals 0", "count == 0"),
        ("score is greater than or equal to 90", "score >= 90"),
        ("score is less than or equal to 90", "score <= 90"),
        ("age is not equal to 18", "age != 18"),
        ("x is greater than 5 and y is less than 3", "x > 5 and y < 3"),
    ],
)
def test_format_condition_replaces_phrases(condition_text, expected):
    assert CodeGenerator._format_condition(CodeGenerator, condition_text) == expected


@pytest.mark.parametrize(
    "sentence,expected_code",
    [
        (
            'if age is greater than 18 then print "adult"',
            'if age > 18:\n    print("adult")',
        ),
        (
            "if age greater than 18 then print hi",
            'if age > 18:\n    print("hi")',
        ),
        (
            "if age is less than 18 then print young",
            'if age < 18:\n    print("young")',
        ),
        (
            "if age is 18 then print adult",
            'if age == 18:\n    print("adult")',
        ),
        (
            "when count equals 0 do print empty",
            'if count == 0:\n    print("empty")',
        ),
        (
            "if score is greater than or equal to 90 then print pass",
            'if score >= 90:\n    print("pass")',
        ),
    ],
)
def test_conditionals_translate_to_valid_python(sentence, expected_code):
    result = TranslationEngine().translate(sentence)
    assert result.success, result.error_message
    assert result.python_code == expected_code


@pytest.mark.parametrize(
    "sentence,expected_code",
    [
        (
            "while x greater than 0 do print hi",
            'while x > 0:\n    print("hi")',
        ),
        (
            "while x greater than 0 print hi",
            'while x > 0:\n    print("hi")',
        ),
        (
            "while x greater than 0 decrement x",
            "while x > 0:\n    x -= 1",
        ),
    ],
)
def test_while_loops_translate_to_valid_python(sentence, expected_code):
    result = TranslationEngine().translate(sentence)
    assert result.success, result.error_message
    assert result.python_code == expected_code


@pytest.mark.parametrize(
    "sentence,expected_type",
    [
        # "while"/"loop" as data items must not classify as LOOP
        ("add while to list a", "data_operation"),
        ("add loop to list a", "data_operation"),
        ("repeat 3 times add 1 to list a", "loop"),
        ("loop through my_list print item", "loop"),
        ("for each item in numbers print item", "loop"),
    ],
)
def test_pattern_identification(sentence, expected_type):
    from ttc.engine.parser import InputParser

    pattern_type = InputParser().identify_pattern(sentence)
    assert pattern_type.value == expected_type


@pytest.mark.parametrize(
    "sentence,expected_code",
    [
        ("multiply total by 0.1", "result = total * 0.1"),
        ("add 1.5 and 2", "result = 1.5 + 2"),
        ("divide 10 by 2.5", "result = 10 / 2.5"),
        ("subtract 1 from 5", "result = 5 - 1"),
        ("x = 3.5", "x = 3.5"),
    ],
)
def test_decimal_operands_translate_to_valid_python(sentence, expected_code):
    result = TranslationEngine().translate(sentence)
    assert result.success, result.error_message
    assert result.python_code == expected_code


@pytest.mark.parametrize(
    "sentence,expected_code",
    [
        (
            "if is_member equals true then print member_discount else print no_discount",
            'if is_member == True:\n    print("member_discount")\nelse:\n    print("no_discount")',
        ),
        (
            "if active equals false then print no else print yes",
            'if active == False:\n    print("no")\nelse:\n    print("yes")',
        ),
    ],
)
def test_condition_boolean_literals(sentence, expected_code):
    """Bare true/false must become Python True/False (else runtime NameError)."""
    result = TranslationEngine().translate(sentence)
    assert result.success, result.error_message
    assert result.python_code == expected_code
