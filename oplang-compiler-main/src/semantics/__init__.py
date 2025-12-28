"""
Semantic Analysis Module for OPLang Programming Language

This module implements static semantic checking for the OPLang object-oriented
programming language including type checking, scope management, and error detection.
"""

from .static_error import *
from .static_checker import StaticChecker

__all__ = [
    'StaticChecker',
    'StaticError',
    'Redeclared',
    'UndeclaredIdentifier', 
    'UndeclaredClass',
    'UndeclaredAttribute',
    'UndeclaredMethod',
    'CannotAssignToConstant',
    'TypeMismatchInStatement',
    'TypeMismatchInExpression', 
    'TypeMismatchInConstant',
    'MustInLoop',
    'IllegalConstantExpression',
    'IllegalArrayLiteral',
    'IllegalMemberAccess',
    'NoEntryPoint'
]