"""
Code Generator for OPLang programming language.
This module implements a code generator that traverses AST nodes and generates
Java bytecode using the Emitter and Frame classes.
"""

from typing import Any, List, Optional
from ..utils.visitor import ASTVisitor
from ..utils.nodes import *
from .emitter import Emitter, is_void_type, is_int_type, is_string_type, is_bool_type
from .frame import Frame
from .error import IllegalOperandException, IllegalRuntimeException
from .io import IO_SYMBOL_LIST
from .utils import *
from functools import *


class CodeGenerator(ASTVisitor):
    """
    Code generator for OPLang.
    Traverses AST and generates JVM bytecode.
    """
    
    def __init__(self):
        self.current_class = None
        self.emit = None  # Will be initialized per class

    # ============================================================================
    # Program and Class Declarations
    # ============================================================================

    def visit_program(self, node: "Program", o: Any = None):
        """
        Visit program node - generate code for all classes.
        """
        # Process all class declarations
        for class_decl in node.class_decls:
            self.visit(class_decl, o)

    def visit_class_decl(self, node: "ClassDecl", o: Any = None):
        """
        Visit class declaration - generate class structure.
        """
        self.current_class = node.name
        class_file = node.name + ".j"
        self.emit = Emitter(class_file)
        
        # Determine superclass
        superclass = node.superclass if node.superclass else "java/lang/Object"
        
        # Emit class prolog
        self.emit.print_out(self.emit.emit_prolog(node.name, superclass))
        
        # Process class members (attributes, methods, constructors, destructors)
        for member in node.members:
            self.visit(member, o)
        
        # Emit class epilog
        self.emit.emit_epilog()

    # ============================================================================
    # Attribute Declarations
    # ============================================================================

    def visit_attribute_decl(self, node: "AttributeDecl", o: Any = None):
        """
        Visit attribute declaration - generate field directives.
        TODO: Implement attribute initialization if needed
        """
        for attr in node.attributes:
            self.visit(attr, node)

    def visit_attribute(self, node: "Attribute", o: Any = None):
        """
        Visit individual attribute - generate field directive.
        """
        attr_decl = o  # AttributeDecl node
        class_name = self.current_class
        field_name = class_name + "/" + node.name
        
        # Emit field directive
        if attr_decl.is_static:
            self.emit.print_out(
                self.emit.emit_attribute(
                    field_name,
                    attr_decl.attr_type,
                    attr_decl.is_final
                )
            )
        else:
            # Instance field
            self.emit.print_out(
                self.emit.jvm.emitINSTANCEFIELD(
                    field_name,
                    self.emit.get_jvm_type(attr_decl.attr_type)
                )
            )
        
        # TODO: Handle initialization if node.init_value is not None

    # ============================================================================
    # Method Declarations
    # ============================================================================

    def visit_method_decl(self, node: "MethodDecl", o: Any = None):
        """
        Visit method declaration - generate method code.
        """
        frame = Frame(node.name, node.return_type)
        self.generate_method(node, frame, node.is_static)

    def visit_constructor_decl(self, node: "ConstructorDecl", o: Any = None):
        """
        Visit constructor declaration - generate constructor code.
        """
        # TODO: Implement constructor generation
        pass

    def visit_destructor_decl(self, node: "DestructorDecl", o: Any = None):
        """
        Visit destructor declaration - generate destructor code.
        """
        # TODO: Implement destructor generation
        pass

    def visit_parameter(self, node: "Parameter", o: Any = None):
        """
        Visit parameter - register parameter in frame.
        """
        # This is handled in generate_method
        pass

    def generate_method(self, node: "MethodDecl", frame: Frame, is_static: bool):
        """
        Generate code for a method.
        
        Args:
            node: Method declaration node
            frame: Frame for this method
            is_static: Whether method is static
        """
        class_name = self.current_class
        method_name = node.name
        
        # Build method signature
        param_types = [p.param_type for p in node.params]
        return_type = node.return_type
        
        # Create function type for method signature
        func_type = FunctionType(param_types, return_type)
        
        # Emit method directive
        self.emit.print_out(
            self.emit.emit_method(
                method_name,
                func_type,
                is_static
            )
        )
        
        frame.enter_scope(True)
        from_label = frame.get_start_label()
        to_label = frame.get_end_label()
        
        # Handle 'this' parameter for instance methods
        if not is_static:
            this_idx = frame.get_new_index()
            self.emit.print_out(
                self.emit.emit_var(
                    this_idx,
                    "this",
                    ClassType(class_name),
                    from_label,
                    to_label
                )
            )
            # Add 'this' to symbol list
            sym_list.append(Symbol("this", ClassType(class_name), Index(this_idx)))
        
        # Generate code for parameters
        sym_list = []
        param_start_idx = 0 if is_static else 1  # Skip 'this' for instance methods
        for i, param in enumerate(node.params):
            idx = frame.get_new_index()
            self.emit.print_out(
                self.emit.emit_var(
                    idx,
                    param.name,
                    param.param_type,
                    from_label,
                    to_label
                )
            )
            sym_list.append(Symbol(param.name, param.param_type, Index(idx)))
        
        # Add IO symbols
        sym_list = IO_SYMBOL_LIST + sym_list
        
        self.emit.print_out(self.emit.emit_label(from_label, frame))
        
        # Generate code for method body
        o = SubBody(frame, sym_list)
        self.visit(node.body, o)
        
        # Emit return if void
        if is_void_type(return_type):
            self.emit.print_out(self.emit.emit_return(return_type, frame))
        
        self.emit.print_out(self.emit.emit_label(to_label, frame))
        self.emit.print_out(self.emit.emit_end_method(frame))
        
        frame.exit_scope()

    # ============================================================================
    # Type System
    # ============================================================================

    def visit_primitive_type(self, node: "PrimitiveType", o: Any = None):
        pass

    def visit_array_type(self, node: "ArrayType", o: Any = None):
        pass

    def visit_class_type(self, node: "ClassType", o: Any = None):
        pass

    def visit_reference_type(self, node: "ReferenceType", o: Any = None):
        pass

    # ============================================================================
    # Statements
    # ============================================================================

    def visit_block_statement(self, node: "BlockStatement", o: SubBody = None):
        """
        Visit block statement - process variable declarations and statements.
        """
        if o is None:
            return
        
        # Process variable declarations
        for var_decl in node.var_decls:
            o = self.visit(var_decl, o)
        
        # Process statements
        for stmt in node.statements:
            self.visit(stmt, o)

    def visit_variable_decl(self, node: "VariableDecl", o: SubBody = None):
        """
        Visit variable declaration - register local variables.
        """
        if o is None:
            return o
        
        frame = o.frame
        from_label = frame.get_start_label()
        to_label = frame.get_end_label()
        
        new_sym = []
        for var in node.variables:
            idx = frame.get_new_index()
            self.emit.print_out(
                self.emit.emit_var(
                    idx,
                    var.name,
                    node.var_type,
                    from_label,
                    to_label
                )
            )
            
            # Add to symbol list
            new_sym.append(Symbol(var.name, node.var_type, Index(idx)))
            
            # Handle initialization if present
            if var.init_value is not None:
                # Generate code for initialization
                code, typ = self.visit(var.init_value, Access(frame, o.sym))
                self.emit.print_out(code)
                self.emit.print_out(
                    self.emit.emit_write_var(var.name, node.var_type, idx, frame)
                )
        
        return SubBody(frame, new_sym + o.sym)

    def visit_variable(self, node: "Variable", o: Any = None):
        pass

    def visit_assignment_statement(self, node: "AssignmentStatement", o: SubBody = None):
        """
        Visit assignment statement - generate assignment code.
        """
        if o is None:
            return
        
        # Generate code for RHS
        code, typ = self.visit(node.rhs, Access(o.frame, o.sym))
        self.emit.print_out(code)
        
        # Generate code for LHS
        lhs_code, lhs_type = self.visit(node.lhs, Access(o.frame, o.sym, is_left=True))
        self.emit.print_out(lhs_code)

    def visit_if_statement(self, node: "IfStatement", o: Any = None):
        """
        Visit if statement.
        TODO: Implement if statement code generation
        """
        pass

    def visit_for_statement(self, node: "ForStatement", o: Any = None):
        """
        Visit for statement.
        TODO: Implement for statement code generation
        """
        pass

    def visit_break_statement(self, node: "BreakStatement", o: Any = None):
        """
        Visit break statement.
        TODO: Implement break statement code generation
        """
        pass

    def visit_continue_statement(self, node: "ContinueStatement", o: Any = None):
        """
        Visit continue statement.
        TODO: Implement continue statement code generation
        """
        pass

    def visit_return_statement(self, node: "ReturnStatement", o: SubBody = None):
        """
        Visit return statement - generate return code.
        """
        if o is None:
            return
        
        # Generate code for return value
        code, typ = self.visit(node.value, Access(o.frame, o.sym))
        self.emit.print_out(code)
        
        # Emit return instruction
        self.emit.print_out(self.emit.emit_return(typ, o.frame))

    def visit_method_invocation_statement(
        self, node: "MethodInvocationStatement", o: Any = None
    ):
        """
        Visit method invocation statement.
        """
        # TODO: Implement method invocation statement
        pass

    # ============================================================================
    # Left-hand Side (LHS)
    # ============================================================================

    def visit_id_lhs(self, node: "IdLHS", o: Access = None):
        """
        Visit identifier LHS - generate code to write to variable.
        """
        if o is None:
            return "", None
        
        # Find symbol
        sym = next(filter(lambda x: x.name == node.name, o.sym), None)
        if sym is None:
            raise IllegalOperandException(f"Undeclared variable: {node.name}")
        
        if type(sym.value) is Index:
            code = self.emit.emit_write_var(
                sym.name, sym.type, sym.value.value, o.frame
            )
            return code, sym.type
        else:
            raise IllegalOperandException(f"Cannot assign to: {node.name}")

    def visit_postfix_lhs(self, node: "PostfixLHS", o: Any = None):
        """
        Visit postfix LHS (for member access, array access).
        TODO: Implement postfix LHS code generation
        """
        pass

    # ============================================================================
    # Expressions
    # ============================================================================

    def visit_binary_op(self, node: "BinaryOp", o: Access = None):
        """
        Visit binary operation.
        TODO: Implement binary operation code generation
        """
        pass

    def visit_unary_op(self, node: "UnaryOp", o: Access = None):
        """
        Visit unary operation.
        TODO: Implement unary operation code generation
        """
        pass

    def visit_postfix_expression(self, node: "PostfixExpression", o: Access = None):
        """
        Visit postfix expression (method calls, member access, array access).
        TODO: Implement postfix expression code generation
        """
        pass

    def visit_method_call(self, node: "MethodCall", o: Access = None):
        """
        Visit method call.
        TODO: Implement method call code generation
        """
        pass

    def visit_member_access(self, node: "MemberAccess", o: Access = None):
        """
        Visit member access.
        TODO: Implement member access code generation
        """
        pass

    def visit_array_access(self, node: "ArrayAccess", o: Access = None):
        """
        Visit array access.
        TODO: Implement array access code generation
        """
        pass

    def visit_object_creation(self, node: "ObjectCreation", o: Access = None):
        """
        Visit object creation.
        TODO: Implement object creation code generation
        """
        pass

    def visit_identifier(self, node: "Identifier", o: Access = None):
        """
        Visit identifier - generate code to read variable.
        """
        if o is None:
            return "", None
        
        # Find symbol
        sym = next(filter(lambda x: x.name == node.name, o.sym), None)
        if sym is None:
            raise IllegalOperandException(f"Undeclared identifier: {node.name}")
        
        if type(sym.value) is Index:
            code = self.emit.emit_read_var(
                sym.name, sym.type, sym.value.value, o.frame
            )
            return code, sym.type
        else:
            raise IllegalOperandException(f"Cannot read: {node.name}")

    def visit_this_expression(self, node: "ThisExpression", o: Access = None):
        """
        Visit this expression - load 'this' reference.
        """
        if o is None:
            return "", None
        
        # Find 'this' in symbol table (should be at index 0 for instance methods)
        this_sym = next(filter(lambda x: x.name == "this", o.sym), None)
        if this_sym is None:
            raise IllegalOperandException("'this' not available in static context")
        
        if type(this_sym.value) is Index:
            code = self.emit.emit_read_var(
                "this", this_sym.type, this_sym.value.value, o.frame
            )
            return code, this_sym.type
        else:
            raise IllegalOperandException("Invalid 'this' reference")

    def visit_parenthesized_expression(
        self, node: "ParenthesizedExpression", o: Access = None
    ):
        """
        Visit parenthesized expression - just visit inner expression.
        """
        return self.visit(node.expr, o)

    # ============================================================================
    # Literals
    # ============================================================================

    def visit_int_literal(self, node: "IntLiteral", o: Access = None):
        """
        Visit integer literal - push integer constant.
        """
        if o is None:
            return "", None
        code = self.emit.emit_push_iconst(node.value, o.frame)
        return code, PrimitiveType("int")

    def visit_float_literal(self, node: "FloatLiteral", o: Access = None):
        """
        Visit float literal - push float constant.
        """
        if o is None:
            return "", None
        code = self.emit.emit_push_fconst(str(node.value), o.frame)
        return code, PrimitiveType("float")

    def visit_bool_literal(self, node: "BoolLiteral", o: Access = None):
        """
        Visit boolean literal - push boolean constant.
        """
        if o is None:
            return "", None
        value_str = "1" if node.value else "0"
        code = self.emit.emit_push_iconst(value_str, o.frame)
        return code, PrimitiveType("boolean")

    def visit_string_literal(self, node: "StringLiteral", o: Access = None):
        """
        Visit string literal - push string constant.
        """
        if o is None:
            return "", None
        code = self.emit.emit_push_const('"' + node.value + '"', PrimitiveType("string"), o.frame)
        return code, PrimitiveType("string")

    def visit_array_literal(self, node: "ArrayLiteral", o: Access = None):
        """
        Visit array literal.
        TODO: Implement array literal code generation
        """
        pass

    def visit_nil_literal(self, node: "NilLiteral", o: Access = None):
        """
        Visit nil literal - push null reference.
        """
        if o is None:
            return "", None
        o.frame.push()
        code = self.emit.jvm.emitPUSHNULL()
        return code, None  # Type will be determined by context

