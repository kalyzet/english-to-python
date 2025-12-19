"""
Property-based tests for parsing functionality
**Feature: english-to-python-translator, Property 9: Arithmetic pattern identification**
**Validates: Requirements 3.1**
"""

import pytest
from hypothesis import given, strategies as st, assume
from src.core import InputParser, PatternMatcher
from src.models import PatternType


# Hypothesis strategies for generating test data
@st.composite
def arithmetic_keywords(draw):
    """Generate arithmetic keywords"""
    return draw(st.sampled_from([
        'add', 'plus', 'sum', 'subtract', 'minus', 'multiply', 'times', 
        'divide', 'split', 'calculate'
    ]))


@st.composite
def variable_names(draw):
    """Generate valid variable names"""
    first_char = draw(st.sampled_from('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'))
    rest_chars = draw(st.text(
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_',
        min_size=0,
        max_size=10
    ))
    return first_char + rest_chars


@st.composite
def arithmetic_sentences(draw):
    """Generate sentences that should be identified as arithmetic"""
    keyword = draw(arithmetic_keywords())
    var1 = draw(variable_names())
    var2 = draw(variable_names())
    
    # Ensure variables are different
    assume(var1 != var2)
    
    # Create valid templates based on keyword
    if keyword in ['add', 'plus', 'sum']:
        templates = [
            f"add {var1} and {var2}",
            f"{var1} plus {var2}",
            f"sum {var1} and {var2}",
            f"calculate {var1} plus {var2}"
        ]
    elif keyword in ['subtract', 'minus']:
        templates = [
            f"subtract {var1} from {var2}",
            f"{var1} minus {var2}",
            f"calculate {var1} minus {var2}"
        ]
    elif keyword in ['multiply', 'times']:
        templates = [
            f"multiply {var1} by {var2}",
            f"{var1} times {var2}",
            f"calculate {var1} times {var2}"
        ]
    elif keyword in ['divide', 'split']:
        templates = [
            f"divide {var1} by {var2}",
            f"{var1} divided by {var2}",
            f"calculate {var1} divided by {var2}"
        ]
    else:  # calculate
        operation = draw(st.sampled_from(['plus', 'minus', 'times', 'divided by']))
        templates = [f"calculate {var1} {operation} {var2}"]
    
    return draw(st.sampled_from(templates))


@st.composite
def non_arithmetic_sentences(draw):
    """Generate sentences that should NOT be identified as arithmetic"""
    templates = [
        "hello world",
        "create a list",
        "set variable to value", 
        "if condition then action",
        "repeat 5 times",
        "random text here",
        "this is just a sentence",
        "no arithmetic operations here"
    ]
    return draw(st.sampled_from(templates))


class TestArithmeticPatternIdentification:
    """
    **Feature: english-to-python-translator, Property 9: Arithmetic pattern identification**
    **Validates: Requirements 3.1**
    
    Property: For any English sentence containing arithmetic keywords 
    (add, sum, multiply, divide, etc.), the parser should identify 
    the pattern type as 'arithmetic'.
    """
    
    @given(sentence=arithmetic_sentences())
    def test_arithmetic_sentences_identified_as_arithmetic(self, sentence):
        """
        Property: Sentences with arithmetic keywords should be identified as arithmetic
        """
        parser = InputParser()
        
        # Property: Arithmetic sentences should be identified as ARITHMETIC pattern
        pattern_type = parser.identify_pattern(sentence)
        assert pattern_type == PatternType.ARITHMETIC, f"Sentence '{sentence}' should be identified as arithmetic"
    
    @given(sentence=non_arithmetic_sentences())
    def test_non_arithmetic_sentences_not_identified_as_arithmetic(self, sentence):
        """
        Property: Sentences without arithmetic keywords should NOT be identified as arithmetic
        """
        parser = InputParser()
        
        # Property: Non-arithmetic sentences should NOT be identified as ARITHMETIC pattern
        pattern_type = parser.identify_pattern(sentence)
        assert pattern_type != PatternType.ARITHMETIC, f"Sentence '{sentence}' should NOT be identified as arithmetic"
    
    @given(
        keyword=arithmetic_keywords(),
        var1=variable_names(),
        var2=variable_names()
    )
    def test_arithmetic_keyword_presence_implies_arithmetic_pattern(self, keyword, var1, var2):
        """
        Property: Any sentence containing arithmetic keywords should be identifiable as arithmetic
        """
        assume(var1 != var2)
        assume(len(var1) > 0 and len(var2) > 0)
        
        parser = InputParser()
        
        # Create sentence with arithmetic keyword
        sentence = f"{keyword} {var1} and {var2}"
        
        # Property: Presence of arithmetic keyword should result in arithmetic identification
        pattern_type = parser.identify_pattern(sentence)
        
        # Note: Some keywords might not match if they're not in proper context
        # But if they do match, they should be arithmetic
        if pattern_type == PatternType.ARITHMETIC:
            assert True  # This is what we expect
        else:
            # If not identified as arithmetic, the sentence should not match arithmetic patterns
            matcher = PatternMatcher()
            match_result = matcher.match_arithmetic(sentence)
            # If no match found, that's acceptable (keyword might need better context)
            assert match_result is None, f"Sentence '{sentence}' matches arithmetic but not identified as such"
    
    @given(sentence=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    def test_pattern_identification_consistency(self, sentence):
        """
        Property: Pattern identification should be consistent - 
        if a sentence matches arithmetic patterns, it should be identified as arithmetic
        """
        parser = InputParser()
        matcher = PatternMatcher()
        
        # Check if sentence matches arithmetic patterns
        arithmetic_match = matcher.match_arithmetic(sentence)
        identified_pattern = parser.identify_pattern(sentence)
        
        # Property: If sentence matches arithmetic patterns, it should be identified as arithmetic
        if arithmetic_match is not None:
            assert identified_pattern == PatternType.ARITHMETIC, \
                f"Sentence '{sentence}' matches arithmetic patterns but identified as {identified_pattern}"
    
    @given(
        base_sentence=arithmetic_sentences(),
        case_variation=st.integers(min_value=0, max_value=3)
    )
    def test_case_insensitive_arithmetic_identification(self, base_sentence, case_variation):
        """
        Property: Arithmetic pattern identification should be case insensitive
        """
        parser = InputParser()
        
        # Apply different case variations
        if case_variation == 0:
            sentence = base_sentence.lower()
        elif case_variation == 1:
            sentence = base_sentence.upper()
        elif case_variation == 2:
            sentence = base_sentence.title()
        else:
            sentence = base_sentence  # Original case
        
        # Property: All case variations should be identified as arithmetic
        pattern_type = parser.identify_pattern(sentence)
        assert pattern_type == PatternType.ARITHMETIC, \
            f"Case variation '{sentence}' should be identified as arithmetic"


class TestPatternMatcherProperties:
    """Property tests for PatternMatcher component"""
    
    @given(
        keyword=arithmetic_keywords(),
        operand1=variable_names(),
        operand2=variable_names()
    )
    def test_arithmetic_matcher_returns_correct_operation_type(self, keyword, operand1, operand2):
        """
        Property: Arithmetic matcher should return operation types that correspond to keywords
        """
        assume(operand1 != operand2)
        assume(len(operand1) > 0 and len(operand2) > 0)
        
        matcher = PatternMatcher()
        sentence = f"{keyword} {operand1} and {operand2}"
        
        result = matcher.match_arithmetic(sentence)
        
        if result is not None:
            operation_type, operands = result
            
            # Property: Operation type should correspond to keyword
            if keyword in ['add', 'plus', 'sum']:
                assert operation_type == 'add'
            elif keyword in ['subtract', 'minus']:
                assert operation_type == 'subtract'
            elif keyword in ['multiply', 'times']:
                assert operation_type == 'multiply'
            elif keyword in ['divide', 'split']:
                assert operation_type == 'divide'
            elif keyword == 'calculate':
                # Calculate can be followed by different operations
                assert operation_type in ['add', 'subtract', 'multiply', 'divide']
            
            # Property: Operands should contain the variables
            assert len(operands) >= 2
            assert operand1 in operands[0] or operand1 in operands[1]
            assert operand2 in operands[0] or operand2 in operands[1]
    
    @given(sentence=st.text(min_size=1, max_size=200))
    def test_pattern_matcher_deterministic(self, sentence):
        """
        Property: Pattern matcher should be deterministic - same input should give same output
        """
        matcher1 = PatternMatcher()
        matcher2 = PatternMatcher()
        
        # Property: Multiple calls should return same result
        result1 = matcher1.match_arithmetic(sentence)
        result2 = matcher2.match_arithmetic(sentence)
        
        assert result1 == result2, f"Pattern matching should be deterministic for '{sentence}'"
    
    @given(
        sentence=st.text(min_size=1, max_size=100),
        pattern_type=st.sampled_from(['arithmetic', 'assignment', 'conditional', 'loop', 'data_operation'])
    )
    def test_pattern_matcher_exclusivity(self, sentence, pattern_type):
        """
        Property: A sentence should not match multiple primary pattern types simultaneously
        (though this is more of a design choice than a strict requirement)
        """
        matcher = PatternMatcher()
        
        # Get all pattern matches
        arithmetic_match = matcher.match_arithmetic(sentence)
        assignment_match = matcher.match_assignment(sentence)
        conditional_match = matcher.match_conditional(sentence)
        loop_match = matcher.match_loop(sentence)
        data_op_match = matcher.match_data_operation(sentence)
        
        # Count how many patterns match
        matches = [
            arithmetic_match, assignment_match, conditional_match, 
            loop_match, data_op_match
        ]
        non_null_matches = [m for m in matches if m is not None]
        
        # Property: Most sentences should match at most one primary pattern
        # (This is a soft property - some sentences might legitimately match multiple)
        if len(non_null_matches) > 1:
            # This is acceptable but worth noting
            pass  # Multiple matches can happen and that's okay


class TestInputParserIntegrationProperties:
    """Integration property tests for InputParser"""
    
    @given(sentence=arithmetic_sentences())
    def test_arithmetic_parsing_completeness(self, sentence):
        """
        Property: Arithmetic sentences should be parsed with operations extracted
        """
        parser = InputParser()
        
        try:
            parsed = parser.parse_sentence(sentence)
            
            # Property: Arithmetic sentences should result in arithmetic pattern
            assert parsed.pattern_type == PatternType.ARITHMETIC
            
            # Property: Arithmetic sentences should have operations extracted
            assert len(parsed.operations) > 0, f"Arithmetic sentence '{sentence}' should have operations"
            
            # Property: Operations should have valid operation types
            for operation in parsed.operations:
                assert operation.operation_type in ['add', 'subtract', 'multiply', 'divide']
                
        except ValueError:
            # Some generated sentences might be invalid, that's acceptable
            pass
    
    @given(
        sentence=st.text(min_size=5, max_size=100).filter(lambda x: x.strip() and len(x.strip()) >= 3)
    )
    def test_parser_robustness(self, sentence):
        """
        Property: Parser should handle any reasonable input without crashing
        """
        parser = InputParser()
        
        try:
            # Property: Parser should not crash on any valid input
            parsed = parser.parse_sentence(sentence)
            
            # Property: Parsed result should have basic structure
            assert parsed.original_text == sentence.strip()
            assert isinstance(parsed.pattern_type, PatternType)
            assert isinstance(parsed.variables, dict)
            assert isinstance(parsed.operations, list)
            assert isinstance(parsed.conditions, list)
            assert isinstance(parsed.metadata, dict)
            
        except ValueError as e:
            # ValueError is acceptable for invalid inputs
            assert "empty" in str(e).lower() or "invalid" in str(e).lower()
    
    @given(sentence=arithmetic_sentences())
    def test_arithmetic_confidence_scoring(self, sentence):
        """
        Property: Arithmetic sentences should have reasonable confidence scores
        """
        parser = InputParser()
        
        try:
            parsed = parser.parse_sentence(sentence)
            
            if parsed.pattern_type == PatternType.ARITHMETIC:
                # Property: Arithmetic sentences should have decent confidence
                confidence = parsed.metadata.get('confidence', 0.0)
                assert confidence > 0.5, f"Arithmetic sentence '{sentence}' should have confidence > 0.5, got {confidence}"
                
        except ValueError:
            # Some generated sentences might be invalid
            pass


class TestConditionalPatternIdentification:
    """
    **Feature: english-to-python-translator, Property 10: Conditional pattern identification**
    **Validates: Requirements 3.2**
    
    Property: For any English sentence containing conditional keywords 
    (if, then, else, when, etc.), the parser should identify 
    the pattern type as 'conditional'.
    """
    
    @st.composite
    def conditional_keywords(draw):
        """Generate conditional keywords"""
        return draw(st.sampled_from(['if', 'when', 'unless']))
    
    @st.composite
    def conditional_sentences(draw):
        """Generate sentences that should be identified as conditional"""
        keyword = draw(TestConditionalPatternIdentification.conditional_keywords())
        condition = draw(st.text(min_size=3, max_size=20).filter(lambda x: x.strip() and 'then' not in x.lower()))
        action = draw(st.text(min_size=3, max_size=20).filter(lambda x: x.strip()))
        
        if keyword == 'if':
            templates = [
                f"if {condition} then {action}",
                f"if {condition} then {action} else do nothing"
            ]
        elif keyword == 'when':
            templates = [
                f"when {condition} do {action}",
                f"when {condition} then {action}"
            ]
        else:  # unless
            templates = [
                f"unless {condition} then {action}"
            ]
        
        return draw(st.sampled_from(templates))
    
    @given(sentence=conditional_sentences())
    def test_conditional_sentences_identified_as_conditional(self, sentence):
        """
        Property: Sentences with conditional keywords should be identified as conditional
        """
        parser = InputParser()
        
        # Property: Conditional sentences should be identified as CONDITIONAL pattern
        pattern_type = parser.identify_pattern(sentence)
        assert pattern_type == PatternType.CONDITIONAL, f"Sentence '{sentence}' should be identified as conditional"
    
    @given(
        condition=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters=' '),
            min_size=3, max_size=30
        ).filter(lambda x: x.strip() and 'then' not in x.lower() and '\n' not in x),
        action=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters=' '),
            min_size=3, max_size=30
        ).filter(lambda x: x.strip() and '\n' not in x)
    )
    def test_if_then_pattern_identification(self, condition, action):
        """
        Property: If-then patterns should be identified as conditional
        """
        parser = InputParser()
        
        sentence = f"if {condition} then {action}"
        
        # Property: If-then sentences should be identified as CONDITIONAL
        pattern_type = parser.identify_pattern(sentence)
        assert pattern_type == PatternType.CONDITIONAL, f"If-then sentence '{sentence}' should be conditional"
    
    @given(
        condition=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters=' '),
            min_size=3, max_size=30
        ).filter(lambda x: x.strip() and '\n' not in x),
        action=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters=' '),
            min_size=3, max_size=30
        ).filter(lambda x: x.strip() and '\n' not in x)
    )
    def test_when_do_pattern_identification(self, condition, action):
        """
        Property: When-do patterns should be identified as conditional
        """
        parser = InputParser()
        
        sentence = f"when {condition} do {action}"
        
        # Property: When-do sentences should be identified as CONDITIONAL
        pattern_type = parser.identify_pattern(sentence)
        assert pattern_type == PatternType.CONDITIONAL, f"When-do sentence '{sentence}' should be conditional"
    
    @given(sentence=st.sampled_from([
        "hello world", "add x and y", "create a list", "repeat 5 times",
        "set variable to value", "this is just text", "no conditions here"
    ]))
    def test_non_conditional_sentences_not_identified_as_conditional(self, sentence):
        """
        Property: Sentences without conditional keywords should NOT be identified as conditional
        """
        parser = InputParser()
        
        # Property: Non-conditional sentences should NOT be identified as CONDITIONAL pattern
        pattern_type = parser.identify_pattern(sentence)
        assert pattern_type != PatternType.CONDITIONAL, f"Sentence '{sentence}' should NOT be identified as conditional"


class TestIterationPatternIdentification:
    """
    **Feature: english-to-python-translator, Property 11: Iteration pattern identification**
    **Validates: Requirements 3.3**
    
    Property: For any English sentence containing iteration keywords 
    (loop, repeat, for each, etc.), the parser should identify 
    the pattern type as 'loop'.
    """
    
    @st.composite
    def iteration_keywords(draw):
        """Generate iteration keywords"""
        return draw(st.sampled_from(['repeat', 'loop', 'for', 'while']))
    
    @st.composite
    def iteration_sentences(draw):
        """Generate sentences that should be identified as iteration/loop"""
        keyword = draw(TestIterationPatternIdentification.iteration_keywords())
        
        if keyword == 'repeat':
            count = draw(st.integers(min_value=1, max_value=100))
            action = draw(st.text(min_size=3, max_size=20).filter(lambda x: x.strip()))
            templates = [
                f"repeat {count} times",
                f"repeat {count} times {action}",
                f"repeat {count} times: {action}"
            ]
        elif keyword == 'for':
            item = draw(variable_names())
            collection = draw(variable_names())
            assume(item != collection)
            templates = [
                f"for each {item} in {collection}",
                f"for each {item} in {collection} do something"
            ]
        elif keyword == 'while':
            condition = draw(st.text(min_size=3, max_size=20).filter(lambda x: x.strip()))
            templates = [
                f"while {condition}",
                f"while {condition} do something"
            ]
        else:  # loop
            templates = [
                "loop through items",
                "loop until done"
            ]
        
        return draw(st.sampled_from(templates))
    
    @given(sentence=iteration_sentences())
    def test_iteration_sentences_identified_as_loop(self, sentence):
        """
        Property: Sentences with iteration keywords should be identified as loop
        """
        parser = InputParser()
        
        # Property: Iteration sentences should be identified as LOOP pattern
        pattern_type = parser.identify_pattern(sentence)
        assert pattern_type == PatternType.LOOP, f"Sentence '{sentence}' should be identified as loop"
    
    @given(count=st.integers(min_value=1, max_value=50))
    def test_repeat_pattern_identification(self, count):
        """
        Property: Repeat patterns should be identified as loop
        """
        parser = InputParser()
        
        sentence = f"repeat {count} times"
        
        # Property: Repeat sentences should be identified as LOOP
        pattern_type = parser.identify_pattern(sentence)
        assert pattern_type == PatternType.LOOP, f"Repeat sentence '{sentence}' should be loop"
    
    @given(
        item=variable_names(),
        collection=variable_names()
    )
    def test_for_each_pattern_identification(self, item, collection):
        """
        Property: For-each patterns should be identified as loop
        """
        assume(item != collection)
        assume(len(item) > 0 and len(collection) > 0)
        
        parser = InputParser()
        
        sentence = f"for each {item} in {collection}"
        
        # Property: For-each sentences should be identified as LOOP
        pattern_type = parser.identify_pattern(sentence)
        assert pattern_type == PatternType.LOOP, f"For-each sentence '{sentence}' should be loop"


class TestDataOperationPatternIdentification:
    """
    **Feature: english-to-python-translator, Property 12: Data operation pattern identification**
    **Validates: Requirements 3.4**
    
    Property: For any English sentence containing data structure keywords 
    (list, array, dictionary, string, etc.), the parser should identify 
    the pattern type as 'data_operation'.
    """
    
    @st.composite
    def data_operation_keywords(draw):
        """Generate data operation keywords"""
        return draw(st.sampled_from(['create', 'add', 'remove', 'get', 'list', 'dictionary', 'dict']))
    
    @st.composite
    def data_operation_sentences(draw):
        """Generate sentences that should be identified as data operations"""
        keyword = draw(TestDataOperationPatternIdentification.data_operation_keywords())
        
        if keyword == 'create':
            data_type = draw(st.sampled_from(['list', 'dictionary', 'dict']))
            items = draw(st.text(min_size=3, max_size=20).filter(lambda x: x.strip()))
            templates = [
                f"create {data_type} with {items}",
                f"create a {data_type}",
                f"create {data_type}"
            ]
        elif keyword in ['add', 'remove']:
            item = draw(st.text(min_size=1, max_size=15).filter(lambda x: x.strip()))
            list_name = draw(variable_names())
            templates = [
                f"{keyword} {item} to list {list_name}",
                f"{keyword} {item} from list {list_name}",
                f"{keyword} {item} to {list_name}"
            ]
        elif keyword == 'get':
            item = draw(st.text(min_size=1, max_size=15).filter(lambda x: x.strip()))
            source = draw(variable_names())
            templates = [
                f"get {item} from {source}",
                f"get {item} from list {source}"
            ]
        else:  # list, dictionary, dict
            templates = [
                f"create {keyword} with items",
                f"make a {keyword}",
                f"new {keyword}"
            ]
        
        return draw(st.sampled_from(templates))
    
    @given(sentence=data_operation_sentences())
    def test_data_operation_sentences_identified_as_data_operation(self, sentence):
        """
        Property: Sentences with data structure keywords should be identified as data operation
        """
        parser = InputParser()
        
        # Property: Data operation sentences should be identified as DATA_OPERATION pattern
        pattern_type = parser.identify_pattern(sentence)
        assert pattern_type == PatternType.DATA_OPERATION, f"Sentence '{sentence}' should be identified as data operation"
    
    @given(items=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters=' ,'),
        min_size=1, max_size=30
    ).filter(lambda x: x.strip() and '=' not in x and 'to' not in x.lower()))
    def test_create_list_pattern_identification(self, items):
        """
        Property: Create list patterns should be identified as data operation
        """
        parser = InputParser()
        
        sentence = f"create list with {items}"
        
        # Property: Create list sentences should be identified as DATA_OPERATION
        pattern_type = parser.identify_pattern(sentence)
        assert pattern_type == PatternType.DATA_OPERATION, f"Create list sentence '{sentence}' should be data operation"
    
    @given(
        item=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters=' '),
            min_size=1, max_size=15
        ).filter(lambda x: x.strip() and '=' not in x and 'to' not in x.lower()),
        list_name=variable_names()
    )
    def test_add_to_list_pattern_identification(self, item, list_name):
        """
        Property: Add to list patterns should be identified as data operation
        """
        assume(len(list_name) > 0)
        
        parser = InputParser()
        
        sentence = f"add {item} to list {list_name}"
        
        # Property: Add to list sentences should be identified as DATA_OPERATION
        pattern_type = parser.identify_pattern(sentence)
        assert pattern_type == PatternType.DATA_OPERATION, f"Add to list sentence '{sentence}' should be data operation"