"""
Static Error Classes for OPLang Semantic Analysis

This module defines all the exception classes that can be raised during 
static semantic checking of OPLang programs according to the language specification.
"""


class StaticError(Exception):
    """Base class for all static semantic errors in OPLang"""
    pass


class Redeclared(StaticError):
    """
    Raised when an identifier is declared more than once in the same scope.
    
    Args:
        kind (str): The kind of redeclared entity 
                   ('Variable', 'Constant', 'Attribute', 'Class', 'Method', 'Parameter')
        name (str): The name of the redeclared identifier
    """
    def __init__(self, kind, name):
        self.kind = kind
        self.name = name
        super().__init__(f"Redeclared({kind}, {name})")


class UndeclaredIdentifier(StaticError):
    """
    Raised when a variable, constant, or parameter is used but not declared.
    
    Args:
        name (str): The name of the undeclared identifier
    """
    def __init__(self, name):
        self.name = name
        super().__init__(f"UndeclaredIdentifier({name})")


class UndeclaredClass(StaticError):
    """
    Raised when a class is used but not declared.
    
    Args:
        name (str): The name of the undeclared class
    """
    def __init__(self, name):
        self.name = name
        super().__init__(f"UndeclaredClass({name})")


class UndeclaredAttribute(StaticError):
    """
    Raised when an attribute is accessed but not declared in the class or inheritance chain.
    
    Args:
        name (str): The name of the undeclared attribute
    """
    def __init__(self, name):
        self.name = name
        super().__init__(f"UndeclaredAttribute({name})")


class UndeclaredMethod(StaticError):
    """
    Raised when a method is called but not declared in the class or inheritance chain.
    
    Args:
        name (str): The name of the undeclared method
    """
    def __init__(self, name):
        self.name = name
        super().__init__(f"UndeclaredMethod({name})")


class CannotAssignToConstant(StaticError):
    """
    Raised when attempting to assign to a final/constant variable or attribute.
    
    Args:
        stmt: The assignment statement node that attempts to modify a constant
    """
    def __init__(self, stmt):
        self.stmt = stmt
        super().__init__(f"CannotAssignToConstant({stmt})")


class TypeMismatchInStatement(StaticError):
    """
    Raised when there's a type mismatch in a statement context.
    
    Args:
        stmt: The statement node where the type mismatch occurred
    """
    def __init__(self, stmt):
        self.stmt = stmt
        super().__init__(f"TypeMismatchInStatement({stmt})")


class TypeMismatchInExpression(StaticError):
    """
    Raised when there's a type mismatch in an expression context.
    
    Args:
        expr: The expression node where the type mismatch occurred
    """
    def __init__(self, expr):
        self.expr = expr
        super().__init__(f"TypeMismatchInExpression({expr})")


class TypeMismatchInConstant(StaticError):
    """
    Raised when there's a type mismatch between the declared type
    and initialization value in a constant declaration.
    
    Args:
        const_decl: The constant declaration node with the type mismatch
    """
    def __init__(self, const_decl):
        self.const_decl = const_decl
        super().__init__(f"TypeMismatchInConstant({const_decl})")


class MustInLoop(StaticError):
    """
    Raised when break/continue statements appear outside of loop constructs.
    
    Args:
        stmt: The break/continue statement node
    """
    def __init__(self, stmt):
        self.stmt = stmt
        super().__init__(f"MustInLoop({stmt})")


class IllegalConstantExpression(StaticError):
    """
    Raised when a constant is initialized with an expression that
    cannot be evaluated at compile time.
    
    Args:
        expr: The expression that is not a valid constant expression
    """
    def __init__(self, expr):
        self.expr = expr
        super().__init__(f"IllegalConstantExpression({expr})")


class IllegalArrayLiteral(StaticError):
    """
    Raised when an array literal contains elements of different types.
    
    Args:
        array_literal: The array literal with inconsistent element types
    """
    def __init__(self, array_literal):
        self.array_literal = array_literal
        super().__init__(f"IllegalArrayLiteral({array_literal})")


class IllegalMemberAccess(StaticError):
    """
    Raised when attempting to access static/instance members inappropriately:
    - Accessing instance member via class name
    - Accessing static member via instance
    - Accessing members outside their scope
    
    Args:
        access_expr: The member access or method invocation expression
    """
    def __init__(self, access_expr):
        self.access_expr = access_expr
        super().__init__(f"IllegalMemberAccess({access_expr})")


class NoEntryPoint(StaticError):
    """
    Raised when there's no valid main method in the program.
    A valid main method must:
    - Be named 'main'
    - Take no parameters
    - Return void
    - Be static
    """
    def __init__(self):
        super().__init__("No Entry Point")


# Note: Only 3 Illegal* errors are defined in OPLang specification:
# 1. IllegalMemberAccess
# 2. IllegalConstantExpression  
# 3. IllegalArrayLiteral