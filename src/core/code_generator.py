"""
Code Generator component for English to Python Translator
"""

import ast
from typing import Dict, List, Optional, Any, Tuple

from ..models.parsed_sentence import ParsedSentence, Operation, Condition, PatternType
from ..models.translation_result import TranslationResult


class CodeGenerator:
    """Generates valid Python code from parsed English sentences"""
    
    TEMPLATES = {
        'arithmetic_add': '{result} = {operand1} + {operand2}',
        'arithmetic_subtract': '{result} = {operand1} - {operand2}',
        'arithmetic_multiply': '{result} = {operand1} * {operand2}',
        'arithmetic_divide': '{result} = {operand1} / {operand2}',
        'assignment': '{variable} = {value}',
        'conditional_if': 'if {condition}:\n    {then_block}',
        'conditional_if_else': 'if {condition}:\n    {then_block}\nelse:\n    {else_block}',
        'loop_repeat': 'for _ in range({count}):\n    {body}',
        'loop_for_each': 'for {item} in {collection}:\n    {body}',
        'loop_while': 'while {condition}:\n    {body}',
        'list_create': '{variable} = [{items}]',
        'list_append': '{list_var}.append({item})',
        'dict_create': '{variable} = {{{items}}}',
        'string_create': '{variable} = "{value}"',
    }
    
    def __init__(self):
        self.warnings: List[str] = []
    
    def generate(self, parsed_sentence: ParsedSentence) -> TranslationResult:
        """Main method to generate Python code from parsed sentence"""
        self.warnings = []
        
        try:
            if not parsed_sentence.is_valid():
                return TranslationResult.create_error(
                    "Invalid parsed sentence: no operations, conditions, or variables found",
                    parsed_sentence.original_text
                )
            
            if parsed_sentence.pattern_type == PatternType.ARITHMETIC:
                code = self.generate_arithmetic(parsed_sentence)
            elif parsed_sentence.pattern_type == PatternType.CONDITIONAL:
                code = self.generate_conditional(parsed_sentence)
            elif parsed_sentence.pattern_type == PatternType.LOOP:
                code = self.generate_loop(parsed_sentence)
            elif parsed_sentence.pattern_type == PatternType.DATA_OPERATION:
                code = self.generate_data_operation(parsed_sentence)
            elif parsed_sentence.pattern_type == PatternType.ASSIGNMENT:
                code = self.generate_assignment(parsed_sentence)
            else:
                return TranslationResult.create_error(
                    f"Unsupported pattern type: {parsed_sentence.pattern_type}",
                    parsed_sentence.original_text
                )
            
            formatted_code = self.format_code(code)
            is_valid, error_msg = self.validate_syntax(formatted_code)
            
            if not is_valid:
                return TranslationResult.create_error(
                    f"Generated code has syntax error: {error_msg}",
                    parsed_sentence.original_text
                )
            
            result = TranslationResult.create_success(formatted_code, parsed_sentence.original_text)
            for warning in self.warnings:
                result.add_warning(warning)
            
            return result
            
        except Exception as e:
            return TranslationResult.create_error(
                f"Code generation failed: {str(e)}",
                parsed_sentence.original_text
            )
    
    def generate_arithmetic(self, parsed_sentence: ParsedSentence) -> str:
        """Generate Python code for arithmetic operations"""
        if not parsed_sentence.operations:
            raise ValueError("No operations found for arithmetic pattern")
        
        code_lines = []
        
        for operation in parsed_sentence.operations:
            if not operation.is_arithmetic():
                continue
            
            if len(operation.operands) < 2:
                raise ValueError(f"Arithmetic operation requires at least 2 operands, got {len(operation.operands)}")
            
            operand1 = operation.operands[0]
            operand2 = operation.operands[1]
            result = operation.result_variable or 'result'
            
            template_key = f'arithmetic_{operation.operation_type}'
            if template_key not in self.TEMPLATES:
                raise ValueError(f"Unknown arithmetic operation: {operation.operation_type}")
            
            template = self.TEMPLATES[template_key]
            code = template.format(result=result, operand1=operand1, operand2=operand2)
            code_lines.append(code)
            
            if operation.operation_type == 'divide':
                try:
                    if float(operand2) == 0:
                        self.warnings.append("Warning: Division by zero detected")
                except (ValueError, TypeError):
                    pass
        
        return '\n'.join(code_lines)
    
    def generate_conditional(self, parsed_sentence: ParsedSentence) -> str:
        """Generate Python code for conditional statements"""
        if not parsed_sentence.conditions:
            raise ValueError("No conditions found for conditional pattern")
        
        condition = parsed_sentence.conditions[0]
        then_block = parsed_sentence.metadata.get('then_block', 'pass')
        else_block = parsed_sentence.metadata.get('else_block', None)
        condition_text = self._format_condition(condition.condition_text)
        
        if else_block:
            template = self.TEMPLATES['conditional_if_else']
            code = template.format(condition=condition_text, then_block=then_block, else_block=else_block)
        else:
            template = self.TEMPLATES['conditional_if']
            code = template.format(condition=condition_text, then_block=then_block)
        
        return code
    
    def generate_loop(self, parsed_sentence: ParsedSentence) -> str:
        """Generate Python code for loop statements"""
        loop_type = parsed_sentence.metadata.get('loop_type', 'repeat')
        body = parsed_sentence.metadata.get('body', 'pass')
        
        if loop_type == 'repeat':
            count = parsed_sentence.metadata.get('count', '1')
            template = self.TEMPLATES['loop_repeat']
            code = template.format(count=count, body=body)
        elif loop_type == 'for_each':
            item = parsed_sentence.metadata.get('item', 'item')
            collection = parsed_sentence.metadata.get('collection', '[]')
            template = self.TEMPLATES['loop_for_each']
            code = template.format(item=item, collection=collection, body=body)
        elif loop_type == 'while':
            if not parsed_sentence.conditions:
                raise ValueError("While loop requires a condition")
            condition = self._format_condition(parsed_sentence.conditions[0].condition_text)
            template = self.TEMPLATES['loop_while']
            code = template.format(condition=condition, body=body)
        else:
            raise ValueError(f"Unknown loop type: {loop_type}")
        
        return code
    
    def generate_data_operation(self, parsed_sentence: ParsedSentence) -> str:
        """Generate Python code for data structure operations"""
        if not parsed_sentence.operations:
            raise ValueError("No operations found for data operation pattern")
        
        code_lines = []
        
        for operation in parsed_sentence.operations:
            if operation.operation_type == 'create':
                data_type = parsed_sentence.metadata.get('data_type', 'list')
                
                if data_type == 'list':
                    items = ', '.join(operation.operands)
                    variable = operation.result_variable or 'my_list'
                    template = self.TEMPLATES['list_create']
                    code = template.format(variable=variable, items=items)
                elif data_type == 'dict':
                    items = ', '.join(operation.operands)
                    variable = operation.result_variable or 'my_dict'
                    template = self.TEMPLATES['dict_create']
                    code = template.format(variable=variable, items=items)
                elif data_type == 'string':
                    value = operation.operands[0] if operation.operands else ''
                    variable = operation.result_variable or 'my_string'
                    template = self.TEMPLATES['string_create']
                    code = template.format(variable=variable, value=value)
                else:
                    raise ValueError(f"Unknown data type: {data_type}")
                
                code_lines.append(code)
            
            elif operation.operation_type == 'append':
                if len(operation.operands) < 2:
                    raise ValueError("Append operation requires list variable and item")
                list_var = operation.operands[0]
                item = operation.operands[1]
                template = self.TEMPLATES['list_append']
                code = template.format(list_var=list_var, item=item)
                code_lines.append(code)
            
            else:
                code_lines.append(f"# {operation.operation_type} operation")
        
        return '\n'.join(code_lines)
    
    def generate_assignment(self, parsed_sentence: ParsedSentence) -> str:
        """Generate Python code for assignment operations"""
        code_lines = []
        
        for var_name, var_value in parsed_sentence.variables.items():
            template = self.TEMPLATES['assignment']
            
            if isinstance(var_value, str):
                formatted_value = f'"{var_value}"'
            else:
                formatted_value = str(var_value)
            
            code = template.format(variable=var_name, value=formatted_value)
            code_lines.append(code)
        
        for operation in parsed_sentence.operations:
            if operation.is_assignment():
                if not operation.result_variable or not operation.operands:
                    continue
                
                template = self.TEMPLATES['assignment']
                value = operation.operands[0] if operation.operands else 'None'
                code = template.format(variable=operation.result_variable, value=value)
                code_lines.append(code)
        
        if not code_lines:
            raise ValueError("No assignments found")
        
        return '\n'.join(code_lines)
    
    def format_code(self, code: str) -> str:
        """Format Python code with proper indentation and spacing"""
        if not code.strip():
            return code
        
        lines = code.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.startswith('    ') or line.startswith('\t'):
                formatted_lines.append(line)
            else:
                formatted_line = line.strip()
                if formatted_line:
                    formatted_lines.append(formatted_line)
        
        return '\n'.join(formatted_lines)
    
    def validate_syntax(self, code: str) -> Tuple[bool, str]:
        """Validate Python code syntax using AST parser"""
        if not code.strip():
            return False, "Empty code"
        
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            error_msg = f"Line {e.lineno}: {e.msg}"
            return False, error_msg
        except Exception as e:
            return False, str(e)
    
    def _format_condition(self, condition_text: str) -> str:
        """Format condition text to valid Python boolean expression"""
        condition = condition_text.strip()
        
        replacements = {
            ' equals ': ' == ',
            ' is equal to ': ' == ',
            ' is ': ' == ',
            ' greater than ': ' > ',
            ' less than ': ' < ',
            ' and ': ' and ',
            ' or ': ' or ',
            ' not ': ' not ',
        }
        
        for pattern, replacement in replacements.items():
            condition = condition.replace(pattern, replacement)
        
        return condition
