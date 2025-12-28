"""
Utilities module for OPLang programming language.
This module contains shared utilities including AST node definitions,
visitor patterns, and other common functionality.
"""

from .nodes import *
from .visitor import ASTVisitor

__all__ = [
    # Base classes
    "ASTNode",
    # Program structure
    "Program",
    "ClassDecl",
    "ClassMember",
    # Attribute declarations
    "AttributeDecl",
    "Attribute",
    # Method declarations
    "MethodDecl",
    "ConstructorDecl",
    "DestructorDecl",
    "Parameter",
    # Type system
    "Type",
    "PrimitiveType",
    "ArrayType",
    "ClassType",
    "ReferenceType",
    # Statements
    "Statement",
    "BlockStatement",
    "VariableDecl",
    "Variable",
    "AssignmentStatement",
    "IfStatement",
    "ForStatement",
    "BreakStatement",
    "ContinueStatement",
    "ReturnStatement",
    "MethodInvocationStatement",
    # Left-hand side (LHS)
    "LHS",
    "IdLHS",
    "PostfixLHS",
    # Expressions
    "Expr",
    "BinaryOp",
    "UnaryOp",
    "PostfixExpression",
    "PostfixOp",
    "MethodCall",
    "MemberAccess",
    "ArrayAccess",
    "ObjectCreation",
    # "StaticMethodInvocation",
    # "StaticMemberAccess",
    # "MethodInvocation",
    "Identifier",
    "ThisExpression",
    "ParenthesizedExpression",
    # Literals
    "Literal",
    "IntLiteral",
    "FloatLiteral",
    "BoolLiteral",
    "StringLiteral",
    "ArrayLiteral",
    "NilLiteral",
    # Visitor
    "ASTVisitor",
]
