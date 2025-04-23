from src.lexer import Lexer
from src.tree_struct import Tree
from src.st_builder import SymbolTable
from typing import Dict, List, Set, Tuple, Any, Optional

UTF8_CharSize = 8  # en bits

# -------------------------------------------------------------------------------------------------

def sizeof(value):
    if isinstance(value, int):
        return value.bit_length() or 1  # Ensure at least 1 bit for zero
    elif isinstance(value, str):
        return len(value.encode('utf-8')) * UTF8_CharSize  # Convert to bytes and count bits
    else:
        raise TypeError("Unsupported type. Only integers and strings are supported.")

# -------------------------------------------------------------------------------------------------

# NOTE: the produced ASM is NASM (Netwide Assembler)
def generate_asm(output_file_path: str, ast: Tree, lexer: Lexer, symbol_tables: List[SymbolTable]) -> None:
    # Opening the output file
    output_file = open(output_file_path, 'w')
    data_section: list[str] = ["section .data\n"]
    text_section: list[str] = ["section .text\n\tglobal _start\n"]
    code_section: list[str] = ["_start:\n"]
    
    # Registers management
    available_registers = ["rax", "rbx", "rcx", "rdx", "rsi", "rdi", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]
    register_mapping = {}  # Maps variable names to registers
    
    # Counters for labels
    label_counter = 0
    string_counter = 0
    
    # To track functions and their local variables
    current_function = None
    function_locals = {}
    function_params = {}
    current_stack_offset = 0
    
    # Ensure we're working with the main symbol table (first one should be global)
    current_table = symbol_tables
    
    # Flag to track if we've added newline buffer
    added_newline_buffer = False
    
    # Buffer for number conversion
    data_section.append("\tnum_buffer times 32 db 0  ; Buffer for number conversion\n")
    
    # Components ----------------------------------------------------------------------------------
    
    def get_new_label():
        nonlocal label_counter
        label = f"label_{label_counter}"
        label_counter += 1
        return label
    
    def get_new_string_label():
        nonlocal string_counter
        label = f"str_{string_counter}"
        string_counter += 1
        return label
    
    def get_variable_location(var_id: int, current_st: SymbolTable) -> str:
        """Get variable location from symbol table - either register or memory location"""
        if var_id in register_mapping:
            return register_mapping[var_id]
        
        # Constants are handled differently (they have negative IDs)
        if var_id < 0:
            return f"[rel cst_{abs(var_id)}]"
        
        # Try to find the variable in the current or ancestor symbol tables
        st = current_st
        while st:
            if var_id in st.symbols:
                symbol_info = st.symbols[var_id]
                
                # Local variable in current function context
                if current_function and st.imbrication_level > 0:
                    if var_id in function_locals.get(current_function, {}):
                        offset = function_locals[current_function][var_id]
                        return f"[rbp{'+' if offset >= 0 else ''}{offset}]"
                    
                    # Check if it's a parameter
                    if var_id in function_params.get(current_function, {}):
                        param_index = function_params[current_function][var_id]
                        # First 6 args in registers, rest on stack
                        arg_registers = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
                        if param_index < len(arg_registers):
                            return arg_registers[param_index]
                        else:
                            # Parameter is on stack at [rbp+16+8*(i-6)]
                            stack_offset = 16 + 8 * (param_index - 6)
                            return f"[rbp+{stack_offset}]"
                
                # Global variable (outside any function)
                return f"[rel var_{var_id}]"
                
            st = st.englobing_table
        
        # If not found anywhere, it's an error
        raise ValueError(f"Variable with ID {var_id} not found in any symbol table")
    
    def allocate_register():
        """Allocate a register for a variable"""
        if not available_registers:
            # If no registers available, we need to spill one to memory
            # For simplicity, we'll just use the stack for now
            return None
        
        return available_registers.pop(0)
    
    def free_register(reg):
        """Free a register"""
        if reg in available_registers:
            return
        available_registers.append(reg)
        # Sort to maintain consistent allocation order
        available_registers.sort()
    
    def get_constant_value(const_id):
        """Get constant value from lexer"""
        if const_id >= 0:
            raise ValueError(f"ID {const_id} is not a constant ID (should be negative)")
        return lexer.constant_lexicon.get(const_id)
    
    def get_identifier_name(id_num):
        """Get identifier name from lexer"""
        if id_num <= 0:
            raise ValueError(f"ID {id_num} is not an identifier ID (should be positive)")
        return lexer.identifier_lexicon.get(id_num)
    
    def generate_code_for_constants():
        """Generate data section for constants"""
        # NOTE: Keys are negative in the constant lexicon
        for key, value in lexer.constant_lexicon.items():
            if isinstance(value, int):
                if sizeof(value) <= 64:  # 64-bit integers
                    data_section.append(f"\tcst_{abs(key)} dq {value}\n")
                else:
                    raise ValueError(f"Invalid constant value: {value} is too large.")
            elif isinstance(value, str):
                # For strings, we escape special characters and convert to bytes
                escaped_value = value.replace('"', '\\"').replace('\n', '\\n')
                data_section.append(f'\tcst_{abs(key)} db "{escaped_value}", 0\n')
                data_section.append(f"\tcst_{abs(key)}_len equ $ - cst_{abs(key)}\n")
            else:
                raise TypeError(f"Unsupported constant type: {type(value)}")
    
    def generate_code_for_variables(st: SymbolTable) -> None:
        """Generate data section entries for variables"""
        for symbol_id, symbol_info in st.symbols.items():
            # Skip function entries and other non-variable types
            if isinstance(symbol_info, dict) and "type" in symbol_info:
                if symbol_info["type"] not in ["function", "if", "else", "for"]:
                    # This is a variable - generate data section entry
                    data_section.append(f"\tvar_{symbol_id} resq 1  ; variable {get_identifier_name(symbol_id)}\n")
        
    def generate_code_for_binary_op(op_node: Tree) -> str:
        """Generate code for binary operations (+, -, *, //, %, etc.)"""
        left_node = op_node.children[0]
        right_node = op_node.children[1]
        
        # Generate code for left and right operands
        left_result = generate_expression(left_node)
        
        # Save left result to a register
        left_reg = allocate_register()
        code_section.append(f"\tmov {left_reg}, {left_result}\n")
        
        # Generate code for right operand
        right_result = generate_expression(right_node)
        
        result_reg = left_reg  # Use the same register for result
        
        # Perform the operation based on operator type
        op_type = op_node.data
        if op_type == 40:  # Addition (+)
            code_section.append(f"\tadd {result_reg}, {right_result}\n")
        elif op_type == 41:  # Subtraction (-)
            code_section.append(f"\tsub {result_reg}, {right_result}\n")
        elif op_type == 42:  # Multiplication (*)
            code_section.append(f"\timul {result_reg}, {right_result}\n")
        elif op_type == 43:  # Integer division (//)
            # Division is special in x86 assembly
            # Need to use rax and rdx for division
            if result_reg != "rax":
                code_section.append(f"\tpush rax\n")
                code_section.append(f"\tpush rdx\n")
                code_section.append(f"\tmov rax, {result_reg}\n")
            code_section.append(f"\txor rdx, rdx\n")  # Clear rdx for division
            
            # Check if right_result is a register
            if right_result in available_registers or right_result in ["rax", "rbx", "rcx", "rdx", "rsi", "rdi", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]:
                code_section.append(f"\tidiv {right_result}\n")
            else:
                # Need to move to a register for division
                temp_reg = allocate_register()
                code_section.append(f"\tmov {temp_reg}, {right_result}\n")
                code_section.append(f"\tidiv {temp_reg}\n")
                free_register(temp_reg)
            
            if result_reg != "rax":
                code_section.append(f"\tmov {result_reg}, rax\n")
                code_section.append(f"\tpop rdx\n")
                code_section.append(f"\tpop rax\n")
            else:
                result_reg = "rax"  # Result is in rax
        elif op_type == 44:  # Modulo (%)
            # Similar to division but take remainder from rdx
            if result_reg != "rax":
                code_section.append(f"\tpush rax\n")
                code_section.append(f"\tpush rdx\n")
                code_section.append(f"\tmov rax, {result_reg}\n")
            code_section.append(f"\txor rdx, rdx\n")
            
            if right_result in available_registers or right_result in ["rax", "rbx", "rcx", "rdx", "rsi", "rdi", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]:
                code_section.append(f"\tidiv {right_result}\n")
            else:
                temp_reg = allocate_register()
                code_section.append(f"\tmov {temp_reg}, {right_result}\n")
                code_section.append(f"\tidiv {temp_reg}\n")
                free_register(temp_reg)
            
            if result_reg != "rdx":
                code_section.append(f"\tmov {result_reg}, rdx\n")  # Remainder is in rdx
                if result_reg != "rax":
                    code_section.append(f"\tpop rdx\n")
                    code_section.append(f"\tpop rax\n")
            else:
                result_reg = "rdx"  # Result is in rdx
        elif op_type in [45, 46, 47, 48, 49, 50]:  # Comparisons
            # For comparison, we use cmp and set the ZF/CF flags
            code_section.append(f"\tcmp {result_reg}, {right_result}\n")
            
            # We need to store the result of comparison (0 or 1)
            code_section.append(f"\tmov {result_reg}, 0\n")  # Initialize result to 0
            
            if op_type == 45:  # <= (less than or equal)
                code_section.append(f"\tsetle {result_reg}b\n")
            elif op_type == 46:  # >= (greater than or equal)
                code_section.append(f"\tsetge {result_reg}b\n")
            elif op_type == 47:  # > (greater than)
                code_section.append(f"\tsetg {result_reg}b\n")
            elif op_type == 48:  # < (less than)
                code_section.append(f"\tsetl {result_reg}b\n")
            elif op_type == 49:  # != (not equal)
                code_section.append(f"\tsetne {result_reg}b\n")
            elif op_type == 50:  # == (equal)
                code_section.append(f"\tsete {result_reg}b\n")
        
        return result_reg
    
    def generate_code_for_unary_op(op_node: Tree) -> str:
        """Generate code for unary operations (-x, not x)"""
        operand_node = op_node.children[0]
        operand_result = generate_expression(operand_node)
        
        result_reg = allocate_register()
        code_section.append(f"\tmov {result_reg}, {operand_result}\n")
        
        op_type = op_node.data
        if op_type == 41:  # Unary minus (-)
            code_section.append(f"\tneg {result_reg}\n")
        elif op_type == 24:  # not
            code_section.append(f"\txor {result_reg}, 1\n")  # Logical NOT (0->1, non-zero->0)
        
        return result_reg
    
    def generate_code_for_logical_op(op_node: Tree) -> str:
        """Generate code for logical operations (and, or)"""
        left_node = op_node.children[0]
        right_node = op_node.children[1]
        
        left_result = generate_expression(left_node)
        
        result_reg = allocate_register()
        code_section.append(f"\tmov {result_reg}, {left_result}\n")
        
        # Short-circuit evaluation
        end_label = get_new_label()
        
        if op_node.data == 22:  # and
            # If left is false (0), skip right evaluation
            code_section.append(f"\ttest {result_reg}, {result_reg}\n")
            code_section.append(f"\tjz {end_label}\n")
            
            # Evaluate right side
            right_result = generate_expression(right_node)
            code_section.append(f"\tmov {result_reg}, {right_result}\n")
            
        elif op_node.data == 23:  # or
            # If left is true (non-zero), skip right evaluation
            code_section.append(f"\ttest {result_reg}, {result_reg}\n")
            code_section.append(f"\tjnz {end_label}\n")
            
            # Evaluate right side
            right_result = generate_expression(right_node)
            code_section.append(f"\tmov {result_reg}, {right_result}\n")
        
        code_section.append(f"{end_label}:\n")
        return result_reg
    
    def generate_expression(expr_node: Tree) -> str:
        """Generate code for expressions and return the register containing the result"""
        if expr_node.is_terminal:
            if expr_node.data == 10:  # IDENTIFIER
                # Get variable value
                var_id = expr_node.value
                return get_variable_location(var_id, current_table)
            elif expr_node.data == 11:  # INTEGER
                # Return the constant value directly
                return str(get_constant_value(expr_node.value))
            elif expr_node.data == 12:  # STRING
                # Return a reference to the string constant
                return f"cst_{abs(expr_node.value)}"
            elif expr_node.data == 25:  # True
                return "1"
            elif expr_node.data == 26:  # False
                return "0"
            elif expr_node.data == 27:  # None
                return "0"
        else:
            # Non-terminal nodes
            if expr_node.data in [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]:  # Binary operations
                return generate_code_for_binary_op(expr_node)
            elif expr_node.data in [24, 41] and len(expr_node.children) == 1:  # Unary operations
                return generate_code_for_unary_op(expr_node)
            elif expr_node.data in [22, 23]:  # Logical operations
                return generate_code_for_logical_op(expr_node)
            elif expr_node.data == "function_call":
                return generate_code_for_function_call(expr_node)
        
        raise ValueError(f"Unsupported expression node: {expr_node.data}")
    
    def generate_code_for_assignment(assign_node: Tree) -> None:
        """Generate code for assignment statements"""
        # Left side (target)
        target_node = assign_node.children[0]
        target_id = target_node.value
        
        # Right side (expression)
        expr_node = assign_node.children[1]
        expr_result = generate_expression(expr_node)
        
        # Assign the result to the target
        if target_id in register_mapping:
            target_reg = register_mapping[target_id]
            code_section.append(f"\tmov {target_reg}, {expr_result}\n")
        else:
            # Allocate a register for this variable if possible
            target_reg = allocate_register()
            if target_reg:
                register_mapping[target_id] = target_reg
                code_section.append(f"\tmov {target_reg}, {expr_result}\n")
            else:
                # If no register available, store in memory
                if current_function:
                    # Local variable in function
                    if target_id not in function_locals.get(current_function, {}):
                        # New local variable, allocate stack space
                        current_stack_offset -= 8  # 8 bytes for 64-bit value
                        function_locals.setdefault(current_function, {})[target_id] = current_stack_offset
                    
                    target_location = f"[rbp{current_stack_offset:+d}]"
                    code_section.append(f"\tmov {target_location}, {expr_result}\n")
                else:
                    # Global variable - ensure it's in the data section
                    var_found = False
                    for line in data_section:
                        if f"var_{target_id}" in line:
                            var_found = True
                            break
                    
                    if not var_found:
                        data_section.append(f"\tvar_{target_id} resq 1  ; variable {get_identifier_name(target_id)}\n")
                    
                    code_section.append(f"\tmov [rel var_{target_id}], {expr_result}\n")
    
    def generate_code_for_if_statement(if_node: Tree) -> None:
        """Generate code for if statements"""
        condition_node = if_node.children[0]
        body_node = if_node.children[1]
        
        # Generate code for the condition
        condition_result = generate_expression(condition_node)
        
        # Create labels for the if structure
        else_label = get_new_label()
        end_label = get_new_label()
        
        # Test the condition
        code_section.append(f"\ttest {condition_result}, {condition_result}\n")
        code_section.append(f"\tjz {else_label}\n")
        
        # If body
        generate_code_for_block(body_node)
        code_section.append(f"\tjmp {end_label}\n")
        
        # Else part (if exists)
        code_section.append(f"{else_label}:\n")
        if len(if_node.children) > 2:  # Has else block
            else_node = if_node.children[2]
            generate_code_for_block(else_node)
        
        code_section.append(f"{end_label}:\n")
    
    def generate_code_for_for_loop(for_node: Tree) -> None:
        """Generate code for for loops"""
        # Python for loop: for var in iterable
        var_node = for_node.children[0]  # Variable (target)
        iterable_node = for_node.children[1]  # Iterable
        body_node = for_node.children[2]  # Body
        
        var_id = var_node.value
        
        # For now, we only support iterating over a range
        if iterable_node.data == "range":
            # Get range parameters
            start = 0
            step = 1
            
            # Range with 1 parameter (end)
            if len(iterable_node.children) == 1:
                end_node = iterable_node.children[0]
                end_result = generate_expression(end_node)
                start_value = "0"
            # Range with 2 parameters (start, end)
            elif len(iterable_node.children) == 2:
                start_node = iterable_node.children[0]
                end_node = iterable_node.children[1]
                start_result = generate_expression(start_node)
                end_result = generate_expression(end_node)
                start_value = start_result
            # Range with 3 parameters (start, end, step)
            elif len(iterable_node.children) == 3:
                start_node = iterable_node.children[0]
                end_node = iterable_node.children[1]
                step_node = iterable_node.children[2]
                start_result = generate_expression(start_node)
                end_result = generate_expression(end_node)
                step_result = generate_expression(step_node)
                start_value = start_result
                step = step_result
            
            # Initialize the loop variable
            loop_var_reg = allocate_register()
            register_mapping[var_id] = loop_var_reg
            code_section.append(f"\tmov {loop_var_reg}, {start_value}\n")
            
            # Create labels for loop structure
            loop_start = get_new_label()
            loop_end = get_new_label()
            
            # Loop header
            code_section.append(f"{loop_start}:\n")
            
            # Check if we've reached the end
            code_section.append(f"\tcmp {loop_var_reg}, {end_result}\n")
            code_section.append(f"\tjge {loop_end}\n")
            
            # Generate code for loop body
            generate_code_for_block(body_node)
            
            # Increment the loop variable
            code_section.append(f"\tadd {loop_var_reg}, {step}\n")
            code_section.append(f"\tjmp {loop_start}\n")
            
            # Loop end
            code_section.append(f"{loop_end}:\n")
            
            # Free the loop variable register
            free_register(loop_var_reg)
            if var_id in register_mapping:
                del register_mapping[var_id]
    
    def generate_code_for_print(print_node: Tree) -> None:
        """Generate code for print statements"""
        # Get the expression to print
        expr_node = print_node.children[0]
        expr_result = generate_expression(expr_node)
        
        # Check if we're printing a string
        if expr_node.is_terminal and expr_node.data == 12:  # STRING
            string_id = expr_node.value
            # Generate code to print the string
            code_section.append(f"\t; Print string\n")
            code_section.append(f"\tmov rax, 1\n")          # sys_write
            code_section.append(f"\tmov rdi, 1\n")          # stdout
            code_section.append(f"\tlea rsi, [rel cst_{abs(string_id)}]\n")  # string buffer
            code_section.append(f"\tmov rdx, cst_{abs(string_id)}_len\n")    # string length
            code_section.append(f"\tsyscall\n")
            
            # Add newline after string
            if not added_newline_buffer:
                data_section.append(f"\tnewline db 10\n")    # Newline character
                added_newline_buffer = True
            
            code_section.append(f"\tmov rax, 1\n")          # sys_write
            code_section.append(f"\tmov rdi, 1\n")          # stdout
            code_section.append(f"\tlea rsi, [rel newline]\n")  # newline character
            code_section.append(f"\tmov rdx, 1\n")          # length 1
            code_section.append(f"\tsyscall\n")
        else:
            # Print a numeric value - convert to string
            code_section.append(f"\t; Print numeric value\n")
            code_section.append(f"\tmov rax, {expr_result}\n")
            
            # Save used registers
            code_section.append(f"\tpush rdi\n")
            code_section.append(f"\tpush rsi\n")
            code_section.append(f"\tpush rdx\n")
            code_section.append(f"\tpush rcx\n")
            code_section.append(f"\tpush r8\n")
            code_section.append(f"\tpush r9\n")
            
            # Integer to string conversion algorithm
            code_section.append(f"\tmov rcx, 0\n")           # Character count
            code_section.append(f"\tmov r9, 10\n")           # Divisor (base 10)
            code_section.append(f"\tlea rdi, [rel num_buffer+31]\n")  # End of buffer
            code_section.append(f"\tmov byte [rdi], 0\n")    # Null terminator
            code_section.append(f"\tdec rdi\n")
            
            # Handle the special case of 0
            code_section.append(f"\tcmp rax, 0\n")
            code_section.append(f"\tjne .convert_loop\n")
            code_section.append(f"\tmov byte [rdi], '0'\n")
            code_section.append(f"\tinc rcx\n")
            code_section.append(f"\tjmp .print_num\n")
            
            # Convert digits
            code_section.append(f".convert_loop:\n")
            code_section.append(f"\tmov rdx, 0\n")           # Clear high bits for division
            code_section.append(f"\tdiv r9\n")               # rax = quotient, rdx = remainder
            code_section.append(f"\tadd dl, '0'\n")          # Convert to ASCII
            code_section.append(f"\tmov [rdi], dl\n")        # Store digit
            code_section.append(f"\tdec rdi\n")              # Move buffer pointer
            code_section.append(f"\tinc rcx\n")              # Increment count
            code_section.append(f"\ttest rax, rax\n")        # Check if quotient is zero
            code_section.append(f"\tjnz .convert_loop\n")    # If not, continue loop
            
            # Print the converted number
            code_section.append(f".print_num:\n")
            code_section.append(f"\tinc rdi\n")              # Point to first digit
            code_section.append(f"\tmov rax, 1\n")           # sys_write
            code_section.append(f"\tmov rsi, rdi\n")         # pointer to string
            code_section.append(f"\tmov rdx, rcx\n")         # length
            code_section.append(f"\tmov rdi, 1\n")           # stdout
            code_section.append(f"\tsyscall\n")
            
            # Add newline after number
            if not added_newline_buffer:
                data_section.append(f"\tnewline db 10\n")    # Newline character
                added_newline_buffer = True
            
            code_section.append(f"\tmov rax, 1\n")          # sys_write
            code_section.append(f"\tmov rdi, 1\n")          # stdout
            code_section.append(f"\tlea rsi, [rel newline]\n")  # newline character
            code_section.append(f"\tmov rdx, 1\n")          # length 1
            code_section.append(f"\tsyscall\n")
            
            # Restore used registers
            code_section.append(f"\tpop r9\n")
            code_section.append(f"\tpop r8\n")
            code_section.append(f"\tpop rcx\n")
            code_section.append(f"\tpop rdx\n")
            code_section.append(f"\tpop rsi\n")
            code_section.append(f"\tpop rdi\n")
    
    def generate_code_for_function_declaration(func_node: Tree) -> None:
        """Generate code for function declarations"""
        nonlocal current_function, current_stack_offset
        
        # Get function name and parameters
        func_name_node = func_node.children[0]
        func_name = get_identifier_name(func_name_node.value)
        func_id = func_name_node.value
        
        # Create a unique function label
        func_label = f"{func_name}_{func_id}"
        
        # Add function to text section
        text_section.append(f"\tglobal {func_label}\n")
        code_section.append(f"{func_label}:\n")
        
        # Function prologue - save old stack frame
        code_section.append(f"\tpush rbp\n")
        code_section.append(f"\tmov rbp, rsp\n")
        
        # Save current function context
        old_function = current_function
        old_stack_offset = current_stack_offset
        
        # Set new function context
        current_function = func_id
        current_stack_offset = 0
        
        # Initialize function local variables storage
        if func_id not in function_locals:
            function_locals[func_id] = {}
        
        # Process parameters if any
        if len(func_node.children) > 2:  # Has parameters
            param_list_node = func_node.children[1]
            body_node = func_node.children[2]
            
            # Process each parameter
            for i, param_node in enumerate(param_list_node.children):
                param_id = param_node.value
                
                # In x64 calling convention, first 6 args are in registers
                # RDI, RSI, RDX, RCX, R8, R9, then stack
                arg_registers = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
                
                if i < len(arg_registers):
                    # Parameter is in a register
                    if param_id not in register_mapping:
                        reg = allocate_register()
                        if reg:
                            register_mapping[param_id] = reg
                            code_section.append(f"\tmov {reg}, {arg_registers[i]}\n")
                        else:
                            # No free register, store on stack
                            current_stack_offset -= 8
                            function_locals[func_id][param_id] = current_stack_offset
                            code_section.append(f"\tmov [rbp{current_stack_offset:+d}], {arg_registers[i]}\n")
                else:
                    # Parameter is on stack: [rbp+16+8*(i-6)]
                    stack_offset = 16 + 8 * (i - 6)
                    current_stack_offset -= 8
                    function_locals[func_id][param_id] = current_stack_offset
                    code_section.append(f"\tmov rax, [rbp+{stack_offset}]\n")
                    code_section.append(f"\tmov [rbp{current_stack_offset:+d}], rax\n")
        else:
            # No parameters
            body_node = func_node.children[1]
        
        # Generate code for function body
        generate_code_for_block(body_node)
        
        # Function epilogue
        code_section.append(f".{func_label}_exit:\n")
        code_section.append(f"\tmov rsp, rbp\n")
        code_section.append(f"\tpop rbp\n")
        code_section.append(f"\tret\n\n")
        
        # Restore previous function context
        current_function = old_function
        current_stack_offset = old_stack_offset
    
    def generate_code_for_function_call(call_node: Tree) -> str:
        """Generate code for function calls"""
        # Get function name
        func_name_node = call_node.children[0]
        func_id = func_name_node.value
        func_name = get_identifier_name(func_id)
        
        # Create function label
        func_label = f"{func_name}_{func_id}"
        
        # Process arguments if any
        if len(call_node.children) > 1:
            arg_list_node = call_node.children[1]
            
            # Save all used registers before function call
            used_registers = list(register_mapping.values())
            for reg in used_registers:
                code_section.append(f"\tpush {reg}\n")
            
            # Push arguments in reverse order (calling convention)
            arg_registers = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
            stack_args = 0
            
            for i, arg_node in enumerate(arg_list_node.children):
                arg_result = generate_expression(arg_node)
                
                if i < len(arg_registers):
                    # Argument goes in register
                    code_section.append(f"\tmov {arg_registers[i]}, {arg_result}\n")
                else:
                    # Argument goes on stack
                    code_section.append(f"\tpush {arg_result}\n")
                    stack_args += 1
            
            # Call the function
            code_section.append(f"\tcall {func_label}\n")
            
            # Clean up stack if needed
            if stack_args > 0:
                code_section.append(f"\tadd rsp, {stack_args * 8}\n")
            
            # Restore used registers
            for reg in reversed(used_registers):
                code_section.append(f"\tpop {reg}\n")
            
            # Return value is in rax
            return "rax"
        else:
            # No arguments
            # Save used registers
            used_registers = list(register_mapping.values())
            for reg in used_registers:
                code_section.append(f"\tpush {reg}\n")
            
            # Call the function
            code_section.append(f"\tcall {func_label}\n")
            
            # Restore used registers
            for reg in reversed(used_registers):
                code_section.append(f"\tpop {reg}\n")
            
            # Return value is in rax
            return "rax"
    
    def generate_code_for_return(return_node: Tree) -> None:
        """Generate code for return statements"""
        if not current_function:
            raise ValueError("Return statement outside of function")
        
        # Process return value if any
        if len(return_node.children) > 0:
            expr_node = return_node.children[0]
            expr_result = generate_expression(expr_node)
            
            # Return value goes in rax
            code_section.append(f"\tmov rax, {expr_result}\n")
        
        # Jump to function exit
        func_name = get_identifier_name(current_function)
        func_label = f"{func_name}_{current_function}"
        code_section.append(f"\tjmp .{func_label}_exit\n")
    
    def generate_code_for_block(block_node: Tree) -> None:
        """Generate code for a block of statements"""
        # Process each statement in the block
        for stmt_node in block_node.children:
            generate_code_for_statement(stmt_node)
    
    def generate_code_for_statement(stmt_node: Tree) -> None:
        """Generate code for a statement"""
        # Determine statement type and call appropriate handler
        if stmt_node.data == 51:  # Assignment (=)
            generate_code_for_assignment(stmt_node)
        elif stmt_node.data == 20:  # if statement
            generate_code_for_if_statement(stmt_node)
        elif stmt_node.data == 31:  # for loop
            generate_code_for_for_loop(stmt_node)
        elif stmt_node.data == 30:  # print statement
            generate_code_for_print(stmt_node)
        elif stmt_node.data == 29:  # return statement
            generate_code_for_return(stmt_node)
        elif stmt_node.data == "function":  # function declaration
            generate_code_for_function_declaration(stmt_node)
        elif stmt_node.data == "function_call":  # function call
            generate_expression(stmt_node)  # This handles the call and ignores the result
        elif stmt_node.data == "block":  # Block of statements
            generate_code_for_block(stmt_node)
    
    def build_components(current_node: Tree) -> None:
        """Process the AST recursively"""
        if current_node.data == "function":
            generate_code_for_function_declaration(current_node)
        elif not current_node.is_terminal:
            # For non-terminal nodes that are not functions, process each child
            for child in current_node.children:
                build_components(child)
    
    def generate_main_code(ast: Tree) -> None:
        """Generate code for the main program (outside of functions)"""
        # Find statements at the global level that are not function declarations
        for child in ast.children:
            if child.data != "function":
                generate_code_for_statement(child)
        
        # Add exit code
        code_section.append("\n\t; Exit program\n")
        code_section.append("\tmov rax, 60\n")          # sys_exit
        code_section.append("\txor rdi, rdi\n")         # exit code 0
        code_section.append("\tsyscall\n")
    
    def write_generated_code() -> None:
        """Write all generated code to the output file"""
        # Write data section if not empty
        if len(data_section) > 1:
            for line in data_section:
                output_file.write(line)
            output_file.write("\n")
        
        # Write text section
        for line in text_section:
            output_file.write(line)
        output_file.write("\n")
        
        # Write code section
        for line in code_section:
            output_file.write(line)
        
        output_file.write("\n; EOF\n")
    
    # Helper function for string manipulation
    def add_string_to_data_section(string_value: str) -> str:
        """Add a string to the data section and return its label"""
        label = get_new_string_label()
        escaped_value = string_value.replace('"', '\\"').replace('\n', '\\n')
        data_section.append(f'\t{label} db "{escaped_value}", 0\n')
        data_section.append(f"\t{label}_len equ $ - {label}\n")
        return label
    
    # Main execution of the generator
    print(f"\nGenerating ASM code in \"{output_file_path}\"...\n")
    
    # Generate data for constants and global variables
    generate_code_for_constants()
    generate_code_for_variables(symbol_tables)
    
    # Add special strings for standard output
    add_string_to_data_section("\\n")  # Newline character
    
    # Process function declarations first
    for child in ast.children:
        if child.data == "function":
            build_components(child)
    
    # Then generate code for the main program
    generate_main_code(ast)
    
    # Write all generated code to the output file
    write_generated_code()
    
    output_file.close()
    print("Generation done!")
    print("NOTE: the produced ASM is NASM (Netwide Assembler). Comments are preceded by a semicolon.\n")