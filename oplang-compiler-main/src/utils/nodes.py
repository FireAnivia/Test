"""
AST Node classes for OPLang programming language.
This module defines all the AST node types used to represent
the abstract syntax tree for OPLang programs.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .visitor import ASTVisitor


class ASTNode(ABC):
    """Base class for all AST nodes."""

    def __init__(self):
        self.line = None
        self.column = None

    @abstractmethod
    def accept(self, visitor: "ASTVisitor", o: Any = None):
        """Accept a visitor for the Visitor pattern."""
        pass

    def __str__(self):
        """Default string representation."""
        return f"{self.__class__.__name__}()"


# ============================================================================
# Program and Top-level Declarations
# ============================================================================


class Program(ASTNode):
    """Root node representing the entire OPLang program."""

    def __init__(self, class_decls: List["ClassDecl"]):
        super().__init__()
        self.class_decls = class_decls

    def accept(self, visitor, o=None):
        return visitor.visit_program(self, o)

    def __str__(self):
        classes_str = (
            ", ".join(str(c) for c in self.class_decls) if self.class_decls else ""
        )
        classes_part = f"[{classes_str}]" if classes_str else "[]"
        return f"Program({classes_part})"


class ClassDecl(ASTNode):
    """Class declaration node."""

    def __init__(
        self, name: str, superclass: Optional[str], members: List["ClassMember"]
    ):
        super().__init__()
        self.name = name
        self.superclass = superclass
        self.members = members

    def accept(self, visitor, o=None):
        return visitor.visit_class_decl(self, o)

    def __str__(self):
        super_str = f", extends {self.superclass}" if self.superclass else ""
        members_str = ", ".join(str(m) for m in self.members) if self.members else ""
        members_part = f"[{members_str}]" if members_str else "[]"
        return f"ClassDecl({self.name}{super_str}, {members_part})"


class ClassMember(ASTNode):
    """Base class for class members (attributes, methods, constructors, destructors)."""

    pass


# ============================================================================
# Attribute Declarations
# ============================================================================


class AttributeDecl(ClassMember):
    """Attribute declaration node."""

    def __init__(
        self,
        is_static: bool,
        is_final: bool,
        attr_type: "Type",
        attributes: List["Attribute"],
    ):
        super().__init__()
        self.is_static = is_static
        self.is_final = is_final
        self.attr_type = attr_type
        self.attributes = attributes

    def accept(self, visitor, o=None):
        return visitor.visit_attribute_decl(self, o)

    def __str__(self):
        static_str = "static " if self.is_static else ""
        final_str = "final " if self.is_final else ""
        attrs_str = ", ".join(str(a) for a in self.attributes)
        return f"AttributeDecl({static_str}{final_str}{self.attr_type}, [{attrs_str}])"


class Attribute(ASTNode):
    """Individual attribute node."""

    def __init__(self, name: str, init_value: Optional["Expr"] = None):
        super().__init__()
        self.name = name
        self.init_value = init_value

    def accept(self, visitor, o=None):
        return visitor.visit_attribute(self, o)

    def __str__(self):
        init_str = f" = {self.init_value}" if self.init_value else ""
        return f"Attribute({self.name}{init_str})"


# ============================================================================
# Method Declarations
# ============================================================================


class MethodDecl(ClassMember):
    """Method declaration node."""

    def __init__(
        self,
        is_static: bool,
        return_type: "Type",
        name: str,
        params: List["Parameter"],
        body: "BlockStatement",
    ):
        super().__init__()
        self.is_static = is_static
        self.return_type = return_type
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor, o=None):
        return visitor.visit_method_decl(self, o)

    def __str__(self):
        static_str = "static " if self.is_static else ""
        params_str = ", ".join(str(p) for p in self.params) if self.params else ""
        params_part = f"[{params_str}]" if params_str else "[]"
        return f"MethodDecl({static_str}{self.return_type} {self.name}({params_part}), {self.body})"


class ConstructorDecl(ClassMember):
    """Constructor declaration node."""

    def __init__(self, name: str, params: List["Parameter"], body: "BlockStatement"):
        super().__init__()
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor, o=None):
        return visitor.visit_constructor_decl(self, o)

    def __str__(self):
        params_str = ", ".join(str(p) for p in self.params) if self.params else ""
        params_part = f"[{params_str}]" if params_str else "[]"
        return f"ConstructorDecl({self.name}({params_part}), {self.body})"


class DestructorDecl(ClassMember):
    """Destructor declaration node."""

    def __init__(self, name: str, body: "BlockStatement"):
        super().__init__()
        self.name = name
        self.body = body

    def accept(self, visitor, o=None):
        return visitor.visit_destructor_decl(self, o)

    def __str__(self):
        return f"DestructorDecl(~{self.name}(), {self.body})"


class Parameter(ASTNode):
    """Method/Constructor parameter node."""

    def __init__(self, param_type: "Type", name: str):
        super().__init__()
        self.param_type = param_type
        self.name = name

    def accept(self, visitor, o=None):
        return visitor.visit_parameter(self, o)

    def __str__(self):
        return f"Parameter({self.param_type} {self.name})"


# ============================================================================
# Type System
# ============================================================================


class Type(ASTNode):
    """Base class for type annotations."""

    pass


class PrimitiveType(Type):
    """Primitive type node."""

    def __init__(self, type_name: str):
        super().__init__()
        self.type_name = type_name  # "int", "float", "boolean", "string", "void"

    def accept(self, visitor, o=None):
        return visitor.visit_primitive_type(self, o)

    def __str__(self):
        return f"PrimitiveType({self.type_name})"


class ArrayType(Type):
    """Array type node."""

    def __init__(self, element_type: Type, size: int):
        super().__init__()
        self.element_type = element_type
        self.size = size

    def accept(self, visitor, o=None):
        return visitor.visit_array_type(self, o)

    def __str__(self):
        return f"ArrayType({self.element_type}[{self.size}])"


class ClassType(Type):
    """Class type node."""

    def __init__(self, class_name: str):
        super().__init__()
        self.class_name = class_name

    def accept(self, visitor, o=None):
        return visitor.visit_class_type(self, o)

    def __str__(self):
        return f"ClassType({self.class_name})"


class ReferenceType(Type):
    """Reference type node."""

    def __init__(self, referenced_type: Type):
        super().__init__()
        self.referenced_type = referenced_type

    def accept(self, visitor, o=None):
        return visitor.visit_reference_type(self, o)

    def __str__(self):
        return f"ReferenceType({self.referenced_type} &)"


# ============================================================================
# Statements
# ============================================================================


class Statement(ASTNode):
    """Base class for all statement nodes."""

    pass


class BlockStatement(Statement):
    """Block statement containing variable declarations and statements."""

    def __init__(self, var_decls: List["VariableDecl"], statements: List[Statement]):
        super().__init__()
        self.var_decls = var_decls
        self.statements = statements

    def accept(self, visitor, o=None):
        return visitor.visit_block_statement(self, o)

    def __str__(self):
        vars_str = ", ".join(str(v) for v in self.var_decls) if self.var_decls else ""
        vars_part = f"vars=[{vars_str}], " if vars_str else ""
        stmts_str = (
            ", ".join(str(s) for s in self.statements) if self.statements else ""
        )
        stmts_part = f"stmts=[{stmts_str}]" if stmts_str else "stmts=[]"
        return f"BlockStatement({vars_part}{stmts_part})"


class VariableDecl(ASTNode):
    """Variable declaration node."""

    def __init__(self, is_final: bool, var_type: Type, variables: List["Variable"]):
        super().__init__()
        self.is_final = is_final
        self.var_type = var_type
        self.variables = variables

    def accept(self, visitor, o=None):
        return visitor.visit_variable_decl(self, o)

    def __str__(self):
        final_str = "final " if self.is_final else ""
        vars_str = ", ".join(str(v) for v in self.variables)
        return f"VariableDecl({final_str}{self.var_type}, [{vars_str}])"


class Variable(ASTNode):
    """Individual variable node."""

    def __init__(self, name: str, init_value: Optional["Expr"] = None):
        super().__init__()
        self.name = name
        self.init_value = init_value

    def accept(self, visitor, o=None):
        return visitor.visit_variable(self, o)

    def __str__(self):
        init_str = f" = {self.init_value}" if self.init_value else ""
        return f"Variable({self.name}{init_str})"


class AssignmentStatement(Statement):
    """Assignment statement."""

    def __init__(self, lhs: "LHS", rhs: "Expr"):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs

    def accept(self, visitor, o=None):
        return visitor.visit_assignment_statement(self, o)

    def __str__(self):
        return f"AssignmentStatement({self.lhs} := {self.rhs})"


class IfStatement(Statement):
    """If statement."""

    def __init__(
        self,
        condition: "Expr",
        then_stmt: Statement,
        else_stmt: Optional[Statement] = None,
    ):
        super().__init__()
        self.condition = condition
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

    def accept(self, visitor, o=None):
        return visitor.visit_if_statement(self, o)

    def __str__(self):
        else_str = f", else {self.else_stmt}" if self.else_stmt else ""
        return f"IfStatement(if {self.condition} then {self.then_stmt}{else_str})"


class ForStatement(Statement):
    """For statement."""

    def __init__(
        self,
        variable: str,
        start_expr: "Expr",
        direction: str,
        end_expr: "Expr",
        body: Statement,
    ):
        super().__init__()
        self.variable = variable
        self.start_expr = start_expr
        self.direction = direction  # "to" or "downto"
        self.end_expr = end_expr
        self.body = body

    def accept(self, visitor, o=None):
        return visitor.visit_for_statement(self, o)

    def __str__(self):
        return f"ForStatement(for {self.variable} := {self.start_expr} {self.direction} {self.end_expr} do {self.body})"


class BreakStatement(Statement):
    """Break statement."""

    def __init__(self):
        super().__init__()

    def accept(self, visitor, o=None):
        return visitor.visit_break_statement(self, o)

    def __str__(self):
        return "BreakStatement()"


class ContinueStatement(Statement):
    """Continue statement."""

    def __init__(self):
        super().__init__()

    def accept(self, visitor, o=None):
        return visitor.visit_continue_statement(self, o)

    def __str__(self):
        return "ContinueStatement()"


class ReturnStatement(Statement):
    """Return statement."""

    def __init__(self, value: "Expr"):
        super().__init__()
        self.value = value

    def accept(self, visitor, o=None):
        return visitor.visit_return_statement(self, o)

    def __str__(self):
        return f"ReturnStatement(return {self.value})"


class MethodInvocationStatement(Statement):
    """Method invocation statement."""

    def __init__(self, method_call: "PostfixExpression"):
        super().__init__()
        self.method_call = method_call

    def accept(self, visitor, o=None):
        return visitor.visit_method_invocation_statement(self, o)

    def __str__(self):
        return f"MethodInvocationStatement({self.method_call})"


# ============================================================================
# Left-hand Side (LHS) for Assignment
# ============================================================================


class LHS(ASTNode):
    """Base class for left-hand side expressions in assignment."""

    pass


class IdLHS(LHS):
    """Identifier left-hand side."""

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def accept(self, visitor, o=None):
        return visitor.visit_id_lhs(self, o)

    def __str__(self):
        return f"IdLHS({self.name})"


class PostfixLHS(LHS):
    """Postfix expression left-hand side (for member access, array access)."""

    def __init__(self, postfix_expr: "PostfixExpression"):
        super().__init__()
        self.postfix_expr = postfix_expr

    def accept(self, visitor, o=None):
        return visitor.visit_postfix_lhs(self, o)

    def __str__(self):
        return f"PostfixLHS({self.postfix_expr})"


# ============================================================================
# Expressions
# ============================================================================


class Expr(ASTNode):
    """Base class for all expression nodes."""

    pass


class BinaryOp(Expr):
    """Binary operation expression."""

    def __init__(self, left: Expr, operator: str, right: Expr):
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor, o=None):
        return visitor.visit_binary_op(self, o)

    def __str__(self):
        return f"BinaryOp({self.left}, {self.operator}, {self.right})"


class UnaryOp(Expr):
    """Unary operation expression."""

    def __init__(self, operator: str, operand: Expr):
        super().__init__()
        self.operator = operator  # '+', '-', '!'
        self.operand = operand

    def accept(self, visitor, o=None):
        return visitor.visit_unary_op(self, o)

    def __str__(self):
        return f"UnaryOp({self.operator}, {self.operand})"


class PostfixExpression(Expr):
    """Postfix expression for method calls, member access, array access."""

    def __init__(self, primary: Expr, postfix_ops: List["PostfixOp"]):
        super().__init__()
        self.primary = primary
        self.postfix_ops = postfix_ops

    def accept(self, visitor, o=None):
        return visitor.visit_postfix_expression(self, o)

    def __str__(self):
        ops_str = "".join(str(op) for op in self.postfix_ops)
        return f"PostfixExpression({self.primary}{ops_str})"


class PostfixOp(ASTNode):
    """Base class for postfix operations."""

    pass


class MethodCall(PostfixOp):
    """Method invocation postfix operation."""

    def __init__(self, method_name: str, args: List[Expr]):
        super().__init__()
        self.method_name = method_name
        self.args = args

    def accept(self, visitor, o=None):
        return visitor.visit_method_call(self, o)

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.args) if self.args else ""
        return f".{self.method_name}({args_str})"


class MemberAccess(PostfixOp):
    """Member access postfix operation."""

    def __init__(self, member_name: str):
        super().__init__()
        self.member_name = member_name

    def accept(self, visitor, o=None):
        return visitor.visit_member_access(self, o)

    def __str__(self):
        return f".{self.member_name}"


class ArrayAccess(PostfixOp):
    """Array access postfix operation."""

    def __init__(self, index: Expr):
        super().__init__()
        self.index = index

    def accept(self, visitor, o=None):
        return visitor.visit_array_access(self, o)

    def __str__(self):
        return f"[{self.index}]"


class ObjectCreation(Expr):
    """Object creation expression."""

    def __init__(self, class_name: str, args: List[Expr]):
        super().__init__()
        self.class_name = class_name
        self.args = args

    def accept(self, visitor, o=None):
        return visitor.visit_object_creation(self, o)

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.args) if self.args else ""
        return f"ObjectCreation(new {self.class_name}({args_str}))"


class Identifier(Expr):
    """Identifier expression."""

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def accept(self, visitor, o=None):
        return visitor.visit_identifier(self, o)

    def __str__(self):
        return f"Identifier({self.name})"


class ThisExpression(Expr):
    """This expression."""

    def __init__(self):
        super().__init__()

    def accept(self, visitor, o=None):
        return visitor.visit_this_expression(self, o)

    def __str__(self):
        return "ThisExpression(this)"


class ParenthesizedExpression(Expr):
    """Parenthesized expression."""

    def __init__(self, expr: Expr):
        super().__init__()
        self.expr = expr

    def accept(self, visitor, o=None):
        return visitor.visit_parenthesized_expression(self, o)

    def __str__(self):
        return f"ParenthesizedExpression(({self.expr}))"


# ============================================================================
# Literal Expressions
# ============================================================================


class Literal(Expr):
    """Base class for literal expressions."""

    def __init__(self, value: Any):
        super().__init__()
        self.value = value


class IntLiteral(Literal):
    """Integer literal expression."""

    def __init__(self, value: int):
        super().__init__(value)

    def accept(self, visitor, o=None):
        return visitor.visit_int_literal(self, o)

    def __str__(self):
        return f"IntLiteral({self.value})"


class FloatLiteral(Literal):
    """Float literal expression."""

    def __init__(self, value: float):
        super().__init__(value)

    def accept(self, visitor, o=None):
        return visitor.visit_float_literal(self, o)

    def __str__(self):
        return f"FloatLiteral({self.value})"


class BoolLiteral(Literal):
    """Boolean literal expression."""

    def __init__(self, value: bool):
        super().__init__(value)

    def accept(self, visitor, o=None):
        return visitor.visit_bool_literal(self, o)

    def __str__(self):
        return f"BoolLiteral({self.value})"


class StringLiteral(Literal):
    """String literal expression."""

    def __init__(self, value: str):
        super().__init__(value)

    def accept(self, visitor, o=None):
        return visitor.visit_string_literal(self, o)

    def __str__(self):
        return f"StringLiteral({self.value!r})"


class ArrayLiteral(Literal):
    """Array literal expression."""

    def __init__(self, elements: List[Expr]):
        super().__init__(elements)

    def accept(self, visitor, o=None):
        return visitor.visit_array_literal(self, o)

    def __str__(self):
        elements_str = ", ".join(str(elem) for elem in self.value) if self.value else ""
        return f"ArrayLiteral({{{elements_str}}})"


class NilLiteral(Literal):
    """Nil literal expression."""

    def __init__(self):
        super().__init__(None)

    def accept(self, visitor, o=None):
        return visitor.visit_nil_literal(self, o)

    def __str__(self):
        return "NilLiteral(nil)"
