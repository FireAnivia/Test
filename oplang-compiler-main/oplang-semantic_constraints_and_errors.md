# OPLang Programming Language - Semantic Constraints and Error Types
**Static Semantic Analysis Reference**  
**Version 1.0 - September 2025**

## Overview

This document provides a comprehensive reference for all semantic constraints and error types that must be checked by the OPLang static semantic analyzer. OPLang is an object-oriented programming language with inheritance, static typing, and various semantic rules that must be enforced at compile time.

## Error Types Summary

The OPLang static semantic checker must detect and report the following error types:

1. **Redeclared** - Variables, constants, attributes, classes, methods, or parameters declared multiple times in the same scope
2. **Undeclared** - Use of identifiers, classes, attributes, or methods that have not been declared
3. **CannotAssignToConstant** - Attempts to assign to constant variables or immutable fields
4. **TypeMismatchInStatement** - Type incompatibilities in statements
5. **TypeMismatchInExpression** - Type incompatibilities in expressions
6. **TypeMismatchInConstant** - Type incompatibilities in constant declarations
7. **MustInLoop** - Break/continue statements outside of loop contexts
8. **IllegalConstantExpression** - Invalid expressions in constant initialization
9. **IllegalArrayLiteral** - Inconsistent types in array literals
10. **IllegalMemberAccess** - Improper access to static or instance members

---

## Detailed Error Specifications

### 1. Redeclared Variable/Constant/Attribute/Class/Method/Parameter

**Rule:** All declarations must be unique within their respective scopes as defined in the OPLang specification.

**Exception:** `Redeclared(<kind>, <identifier>)`
- `<kind>`: Type of redeclared entity (`Variable`, `Constant`, `Attribute`, `Class`, `Method`, `Parameter`)
- `<identifier>`: Name of the redeclared identifier

**Scope-specific Rules:**
- **Global scope:** Classes and global constants must have unique names
- **Class scope:** Attributes and methods must have unique names within the same class
- **Method scope:** Parameters and local variables must have unique names
- **Block scope:** Variables within the same block must have unique names
- **Inheritance:** Attributes/methods inherited from parent classes can be overridden (not redeclared)

**Examples:**
```oplang
// Error: Redeclared Class in global scope
class Student {
    int id;
    string name;
}
class Student {  // Redeclared(Class, Student)
    float grade;
}

// Error: Redeclared Method in same class
class Calculator {
    int add(int a, int b) {
        return a + b;
    }
    int add(int x, int y) {  // Redeclared(Method, add)
        return x + y;
    }
}

// Error: Redeclared Attribute in same class
class Person {
    string name;
    int age;
    string name;  // Redeclared(Attribute, name)
}

// Error: Redeclared Variable in method scope
class Example {
    void process() {
        int count := 10;
        int count := 20;  // Redeclared(Variable, count)
    }
}

// Error: Redeclared Parameter
class Math {
    int calculate(int x, float y, int x) {  // Redeclared(Parameter, x)
        return x + y;
    }
}

// Error: Redeclared Constant
final int MAX_SIZE = 100;
final int MAX_SIZE = 200;  // Redeclared(Constant, MAX_SIZE)

// Valid: Method overriding (inheritance)
class Animal {
    void makeSound() {
        io.writeStrLn("Some sound");
    }
}
class Dog extends Animal {
    void makeSound() {  // Valid: overriding, not redeclaring
        io.writeStrLn("Woof!");
    }
}

// Valid: Shadowing in different scopes
class ShadowExample {
    int value = 100;  // Class attribute
    
    void method() {
        int value := 200;  // Valid: shadows class attribute
        {
            int value := 300;  // Valid: shadows method variable
        }
    }
}
```

### 2. Undeclared Identifier/Attribute/Method/Class

**Rules:**
- All identifiers (variables, constants, parameters) must be declared before use
- Classes must be declared before instantiation or inheritance
- Attributes must exist in the class or its inheritance chain
- Methods must exist in the class or its inheritance chain

**Exceptions:**
- `UndeclaredIdentifier(<identifier>)`: For undeclared variables, constants, or parameters
- `UndeclaredClass(<class-name>)`: For undeclared classes
- `UndeclaredAttribute(<attribute-name>)`: For undeclared attributes
- `UndeclaredMethod(<method-name>)`: For undeclared methods

**Inheritance Rules:**
- Members of parent classes are accessible in subclasses
- Members are accessible based on scope rules

**Examples:**
```oplang
// Error: Undeclared Variable
class Example {
    void method() {
        int result := undeclaredVar + 10;  // UndeclaredIdentifier(undeclaredVar)
    }
}

// Error: Undeclared Class
class Student extends Person {  // UndeclaredClass(Person)
    int studentId;
}

// Error: Undeclared Attribute
class Car {
    string brand;
    int year;
    
    void display() {
        io.writeStrLn(model);  // UndeclaredAttribute(model)
    }
}

// Error: Undeclared Method
class Calculator {
    int add(int a, int b) {
        return a + b;
    }
    
    void test() {
        int result := multiply(5, 3);  // UndeclaredMethod(multiply)
    }
}

// Error: Method called on wrong class
class MathUtils {
    static int factorial(int n) {
        if n <= 1 then return 1; else return n * factorial(n - 1);
    }
}

class Main {
    void run() {
        Calculator calc := new Calculator();
        int fact := calc.factorial(5);  // UndeclaredMethod(factorial) - not in Calculator
    }
}

// Valid: Inherited member access
class Animal {
    string species;
    
    void setSpecies(string s) {
        species := s;
    }
}

class Dog extends Animal {
    void identify() {
        setSpecies("Canine");  // Valid: inherited method
        io.writeStrLn(species);  // Valid: inherited attribute
    }
}

// Error: Out of scope access
class ScopeTest {
    void method1() {
        int localVar := 42;
    }
    
    void method2() {
        int value := localVar + 1;  // UndeclaredIdentifier(localVar)
    }
}
```

### 3. Cannot Assign To Constant

**Rule:** Constants (final variables/attributes) cannot be modified after initialization.

**Exception:** `CannotAssignToConstant(<statement>)`

**Constant Rules:**
- Final variables must be initialized at declaration or in constructor
- Final variables cannot be reassigned after initialization
- Final attributes follow the same rules
- Assignment in for loops is also checked

**Examples:**
```oplang
// Error: Assignment to constant attribute
class Constants {
    final int MAX_COUNT = 100;
    
    void example() {
        MAX_COUNT := 200;  // Error: CannotAssignToConstant at assignment statement
    }
}

// Error: Assignment to constant attribute
class Configuration {
    final string APP_NAME = "MyApp";
    
    void updateConfig() {
        APP_NAME := "NewApp";  // Error: CannotAssignToConstant at assignment statement
    }
}

// Error: Assignment in for loop
class LoopExample {
    final int limit = 10;
    
    void process() {
        for limit := 0 to 20 do {  // Error: CannotAssignToConstant at for statement
            io.writeIntLn(limit);
        }
    }
}

// Error: Multiple assignment attempts
class MultipleAssignment {
    final float PI = 3.14159;
    
    void calculate() {
        PI := PI * 2;  // Error: CannotAssignToConstant at assignment statement
    }
}

// Valid: Proper constant usage
class ValidConstants {
    final int MAX_SIZE = 1000;
    final string VERSION;
    
    ValidConstants(string version) {
        VERSION := version;  // Valid: initialization in constructor
    }
    
    void display() {
        io.writeStrLn("Version: " ^ VERSION);  // Valid: reading constant
        io.writeIntLn(MAX_SIZE);
    }
}
```

### 4. Type Mismatch In Statement

**Rule:** All statements must conform to OPLang's type rules.

**Exception:** `TypeMismatchInStatement(<statement>)`

**Statement Type Rules:**

**Conditional Statements:**
- If statement condition must be boolean type

**For Statements:**
- Scalar variable must be integer type
- Expression 1 and Expression 2 must be integer type

**Assignment Statements:**
- LHS cannot be void type
- RHS must be same type as LHS or coercible to LHS type
- Integer can coerce to float
- Subtype can coerce to supertype
- Array assignments require same size and compatible element types

**Call Statements:**
- Object must be class type
- Method must return void
- Arguments must match parameter types (with coercion rules)

**Return Statements:**
- Return expression must match method return type

**Examples:**
```oplang
// Error: Non-boolean condition in if statement
class ConditionalError {
    void check() {
        int x := 5;
        if x then {  // Error: TypeMismatchInStatement at if statement
            io.writeStrLn("Invalid");
        }
        
        string message := "hello";
        if message then {  // Error: TypeMismatchInStatement at if statement
            io.writeStrLn("Also invalid");
        }
    }
}

// Error: Non-integer in for statement
class ForLoopError {
    void loop() {
        float f := 1.5;
        boolean condition := true;
        
        for f := 0 to 10 do {  // Error: TypeMismatchInStatement at for statement
            io.writeFloatLn(f);
        }
        
        for int i := condition to 10 do {  // Error: TypeMismatchInStatement at variable declaration
            io.writeIntLn(i);
        }
    }
}

// Error: Assignment type mismatch
class AssignmentError {
    void assign() {
        int x := 10;
        string text := "hello";
        boolean flag := true;
        
        x := text;  // Error: TypeMismatchInStatement at assignment
        text := x;  // Error: TypeMismatchInStatement at assignment
        flag := x;  // Error: TypeMismatchInStatement at assignment
    }
}

// Error: Array assignment mismatch
class ArrayError {
    void arrayAssign() {
        int[3] intArray := {1, 2, 3};
        float[3] floatArray := {1.0, 2.0, 3.0};
        int[2] smallArray := {1, 2};
        
        intArray := floatArray;  // Error: TypeMismatchInStatement at assignment
        intArray := smallArray;  // Error: TypeMismatchInStatement at assignment (different size)
    }
}

// Error: Method call with wrong arguments
class CallError {
    void processInt(int value) {
        io.writeIntLn(value);
    }
    
    void test() {
        string text := "123";
        processInt(text);  // Error: TypeMismatchInStatement at method call
    }
}

// Error: Return type mismatch
class ReturnError {
    int getValue() {
        return "invalid";  // Error: TypeMismatchInStatement at return statement
    }
    
    string getText() {
        return 42;  // Error: TypeMismatchInStatement at return statement
    }
}

// Valid: Proper coercion
class ValidCoercion {
    void coerce() {
        int x := 10;
        float y := x;  // Valid: int to float coercion
        
        Shape obj := new Rectangle(5.0, 3.0);  // Valid: subtype to supertype
    }
}
```

### 5. Type Mismatch In Expression

**Rule:** All expressions must conform to OPLang's type rules.

**Exception:** `TypeMismatchInExpression(<expression>)`

**Expression Type Rules:**

**Array Subscripting:**
- E1 must be array type
- E2 must be integer type

**Binary and Unary Expressions:**
- Follow OPLang specification type rules
- Arithmetic operations require numeric types
- Comparison operations return boolean
- Logical operations require boolean operands

**Method Calls:**
- Object must be class type
- Method must have non-void return type
- Arguments must match parameters with coercion rules

**Attribute Access:**
- Object must be class type
- Attribute must exist in class or inheritance chain

**Examples:**
```oplang
// Error: Array subscripting with wrong types
class ArraySubscriptError {
    void access() {
        int[5] numbers := {1, 2, 3, 4, 5};
        string[2] words := {"hello", "world"};
        
        int value1 := numbers["index"];  // Error: TypeMismatchInExpression at array access
        int value2 := numbers[2.5];      // Error: TypeMismatchInExpression at array access
        string word := words[true];      // Error: TypeMismatchInExpression at array access
        
        // Non-array subscripting
        int x := 10;
        int invalid := x[0];  // Error: TypeMismatchInExpression at array access
    }
}

// Error: Binary operation type mismatch
class BinaryOpError {
    void calculate() {
        int x := 5;
        string text := "hello";
        boolean flag := true;
        
        int sum := x + text;     // Error: TypeMismatchInExpression at binary operation
        boolean result := x && flag;  // Error: TypeMismatchInExpression at binary operation
        int comparison := text < x;   // Error: TypeMismatchInExpression at binary operation
    }
}

// Error: Method call in expression context
class MethodCallError {
    void printMessage() {  // void return type
        io.writeStrLn("Hello");
    }
    
    int getValue() {
        return 42;
    }
    
    void test() {
        int result := printMessage();  // Error: TypeMismatchInExpression at method call
        
        string text := "number";
        int value := getValue(text);  // Error: TypeMismatchInExpression at method call
    }
}

// Error: Attribute access on non-object
class AttributeAccessError {
    void access() {
        int x := 10;
        string text := "hello";
        
        int length := text.value;  // Error: TypeMismatchInExpression at member access (if value doesn't exist)
        int invalid := x.length;   // Error: TypeMismatchInExpression at member access (x is not object)
    }
}

// Error: Unary operation type mismatch
class UnaryOpError {
    void operations() {
        string text := "hello";
        boolean flag := true;
        
        int negative := -text;   // Error: TypeMismatchInExpression at unary operation
        boolean not := !text;    // Error: TypeMismatchInExpression at unary operation
        int notFlag := !flag;    // Error: TypeMismatchInExpression at unary operation (if assigned to int)
    }
}

// Valid: Proper expression types
class ValidExpressions {
    void validOps() {
        int[3] numbers := {1, 2, 3};
        int index := 1;
        int value := numbers[index];  // Valid
        
        int x := 10, y := 20;
        boolean result := x < y;      // Valid
        int sum := x + y;             // Valid
        
        Student student := new Student();
        string name := student.getName();  // Valid - assuming getName() returns string
    }
}
```

### 6. Type Mismatch In Constant

**Rule:** The types of left and right hand sides in constant declaration must be compatible.

**Exception:** `TypeMismatchInConstant(<ConstDecl>)`

**Constant Type Rules:**
- RHS type must match LHS type or be coercible to LHS type
- Same coercion rules as assignment statements
- Integer can coerce to float
- Subtype can coerce to supertype

**Examples:**
```oplang
// Error: Type mismatch in constant declaration
class ConstantTypeError {
    final int a = 1.2;        // Error: TypeMismatchInConstant at constant declaration
    final string text = 42;   // Error: TypeMismatchInConstant at constant declaration
    final boolean flag = "true";  // Error: TypeMismatchInConstant at constant declaration
    
    final int count = 3.14;  // Error: TypeMismatchInConstant at constant declaration
}

// Error: Array constant type mismatch
class ArrayConstantError {
    final int[3] numbers = {1.0, 2.0, 3.0};  // Error: TypeMismatchInConstant at constant declaration
    final string[3] words = {1, 2, 3};        // Error: TypeMismatchInConstant at constant declaration
}

// Valid: Proper constant types
class ValidConstants {
    final int MAX_SIZE = 1000;           // Valid
    final float PI = 3.14159;            // Valid
    final string APP_NAME = "MyApp";     // Valid
    final int[4] PRIMES = {2, 3, 5, 7};   // Valid
    
    final float ratio = 10;          // Valid: int to float coercion
}

// Error: Object type mismatch
class ObjectConstantError {
    final Shape shape = new Integer(42);  // TypeMismatchInConstant - if no inheritance relationship
}
```

### 7. Break/Continue Not In Loop

**Rule:** Break and continue statements must be inside a loop (directly or indirectly).

**Exception:** `MustInLoop(<statement>)`

**Loop Context Rules:**
- Break and continue are only valid inside for loops
- Can be nested inside conditionals within loops
- Cannot cross method boundaries
- Must be in the lexical scope of a loop

**Examples:**
```oplang
// Error: Break/continue outside loop
class LoopError {
    void method() {
        break;     // MustInLoop(break)
        continue;  // MustInLoop(continue)
    }
    
    void conditionalError() {
        if true then {
            break;     // MustInLoop(break)
            continue;  // MustInLoop(continue)
        }
    }
}

// Error: Break/continue in method called from loop
class MethodCallError {
    void helperMethod() {
        break;     // MustInLoop(break) - different method scope
        continue;  // MustInLoop(continue)
    }
    
    void loopWithCall() {
        for int i := 0 to 10 do {
            helperMethod();  // Method call doesn't transfer loop context
        }
    }
}

// Valid: Break/continue in loops
class ValidLoops {
    void forLoopWithBreak() {
        for int i := 0 to 10 do {
            if i == 5 then {
                break;     // Valid
            }
            if i % 2 == 0 then {
                continue;  // Valid
            }
            io.writeIntLn(i);
        }
    }
    
    void forLoop() {
        for int i := 0 to 10 do {
            if i == 3 then {
                continue;  // Valid
            }
            if i == 8 then {
                break;     // Valid
            }
            io.writeIntLn(i);
        }
    }
    
    void nestedLoops() {
        for int i := 0 to 5 do {
            for int j := 0 to 5 do {
                if i == j then {
                    continue;  // Valid - affects inner loop
                }
                if j > 3 then {
                    break;     // Valid - breaks inner loop
                }
            }
        }
    }
}
```

### 8. Illegal Constant Expression

**Rule:** Constant initialization expressions must be evaluable at compile time.

**Exception:** `IllegalConstantExpression(<expression>)`

**Constant Expression Rules:**
- Expression must not be None/null
- Must be statically evaluable
- Can only use literals and immutable attributes
- Can only use operators, no method calls
- No references to mutable variables

**Examples:**
```oplang
// Error: None/null initialization
class IllegalConstantError {
    final int x;  // Error: IllegalConstantExpression at constant declaration
    
    final string text = nil;  // Error: IllegalConstantExpression at constant declaration
}

// Error: Using mutable variable in constant expression
class MutableInConstant {
    int mutableVar = 10;
    final int constant1 = mutableVar;  // Error: IllegalConstantExpression at constant declaration
    
    int localVar = 5;
    final int constant2 = 1 + localVar;  // Error: IllegalConstantExpression at constant declaration
}

// Error: Method calls in constant expression
class MethodCallInConstant {
    final int value = getValue();  // Error: IllegalConstantExpression at constant declaration
    
    int getValue() {
        return 42;
    }
}

// Error: Complex expressions with variables
class ComplexIllegalExpression {
    int a = 10;
    
    final int result = (a * 2) + 5;  // Error: IllegalConstantExpression at constant declaration
    final boolean flag = isValid();   // Error: IllegalConstantExpression at constant declaration
    
    boolean isValid() {
        return true;
    }
}

// Valid: Proper constant expressions
class ValidConstantExpressions {
    final int MAX_SIZE = 100;
    final int DOUBLE_SIZE = MAX_SIZE * 2;     // Valid: uses immutable attribute
    final string MESSAGE = "Hello" ^ "World"; // Valid: literal concatenation
    final boolean FLAG = true && false;       // Valid: boolean literals with operators
    final float PI = 3.14159;
    final float CIRCLE_AREA = PI * 10 * 10;   // Valid: uses final attribute
    
    final int SUM = 10 + 20 + 30;         // Valid: literal arithmetic
}

// Error: Array element access in constant
class ArrayAccessInConstant {
    final int[5] NUMBERS = {1, 2, 3, 4, 5};
    final int FIRST = NUMBERS[0];  // Error: IllegalConstantExpression at constant declaration
}
```

### 9. Illegal Array Literal

**Rule:** All elements in an array literal must have the same type.

**Exception:** `IllegalArrayLiteral(<array-literal>)`

**Array Literal Rules:**
- All elements must be exactly the same type
- No type coercion in array literals
- Empty arrays are allowed if type can be inferred

**Examples:**
```oplang
// Error: Mixed types in array literal
class IllegalArrayError {
    void create() {
        int[3] mixed1 := {1, 2.0, 3};      // Error: IllegalArrayLiteral at array literal
        string[2] mixed2 := {"hello", 42}; // Error: IllegalArrayLiteral at array literal
        boolean[2] mixed3 := {true, 1};    // Error: IllegalArrayLiteral at array literal
    }
}

// Error: Mixed object types
class MixedObjectArray {
    void create() {
        Shape[3] mixed := {new Rectangle(1.0, 2.0), new Triangle(1.0, 2.0), "not a shape"};  // Error: IllegalArrayLiteral at array literal
    }
}

// Valid: Consistent array literals
class ValidArrays {
    void create() {
        int[5] numbers := {1, 2, 3, 4, 5};           // Valid
        string[3] words := {"hello", "world", "!"};   // Valid
        boolean[3] flags := {true, false, true};      // Valid
        float[3] decimals := {1.0, 2.5, 3.14};      // Valid
        
        // Valid object arrays with same type
        Rectangle[2] shapes := {new Rectangle(1.0, 2.0), new Rectangle(3.0, 4.0)};
    }
}

// Valid: Empty arrays (if context provides type)
class EmptyArrays {
    void create() {
        int[0] empty1 := {};               // Valid if type can be inferred
    }
}
```

### 10. Illegal Member Access

**Rule:** Static and instance members must be accessed appropriately according to their visibility and context.

**Exception:** `IllegalMemberAccess(<field-access-or-method-invocation>)`

**Member Access Rules:**
- Static members accessed via class name (ClassName.member)
- Instance members accessed via object reference (object.member)
- Members accessible based on scope and inheritance rules

**Access Violation Types:**
1. Accessing instance member via class name
2. Accessing static member via instance
3. Accessing members that don't exist in inheritance chain

**Examples:**
```oplang
// Setup classes for examples
class Student {
    string name;
    int age;
    static int totalStudents := 0;
    string school := "Default School";
    
    static void resetCount() {
        totalStudents := 0;
    }
    
    void setName(string n) {
        name := n;
    }
    
    void secretMethod() {
        io.writeStrLn("Secret");
    }
}

// Error: Accessing instance member via class
class StaticAccessError {
    void test() {
        string school := Student.school;     // Error: IllegalMemberAccess at member access
        Student.setName("John");            // Error: IllegalMemberAccess at method call
    }
}

// Error: Accessing static member via instance
class InstanceAccessError {
    void test() {
        Student s := new Student();
        int count := s.totalStudents;        // Error: IllegalMemberAccess at member access
        s.resetCount();                     // Error: IllegalMemberAccess at method call
    }
}

// Error: Accessing members that don't exist
class UndeclaredMemberError {
    void test() {
        Student s := new Student();
        string name := s.name;               // Valid - if name exists
        s.secretMethod();                   // Valid - if secretMethod exists
        s.nonExistentMethod();              // UndeclaredMethod(nonExistentMethod)
    }
}

// Valid: Proper member access
class ValidAccess {
    void test() {
        // Correct static access
        int count := Student.totalStudents;  // Valid
        Student.resetCount();               // Valid
        
        // Correct instance access
        Student s := new Student();
        s.school := "New School";            // Valid - instance member
        s.setName("Alice");                 // Valid - instance method
    }
}

// Valid: Access from within inheritance hierarchy
class GraduateStudent extends Student {
    void accessProtected() {
        age := 25;                          // Valid - inherited member
        setName("Graduate");               // Valid - inherited method
    }
}

// Error: Complex access violations
class ComplexAccessError {
    void complexTest() {
        Student s1 := new Student();
        Student s2 := new Student();
        
        // Chained access errors
        s1.secretMethod();                   // Valid if method exists
        string result := Student.school;     // Error: IllegalMemberAccess at member access
        
        // Method call on static access
        s1.resetCount();                     // Error: IllegalMemberAccess at method call
    }
}

// Error: Accessing members through wrong reference type
class ReferenceTypeError {
    void wrongReference() {
        Shape obj := new Student();
        // obj.school := "Test";             // IllegalMemberAccess - Shape doesn't have school
        // obj.setName("Test");             // IllegalMemberAccess - Shape doesn't have setName
        
        // Need to cast first
        ((Student)obj).setName("Test");     // Valid after cast
    }
}
```

---

## Implementation Guidelines

### Error Detection Priority
When multiple errors are present, report them in the following order:
1. **Declaration errors** (Redeclared, Undeclared)
2. **Type errors** (TypeMismatch*)
3. **Access control errors** (IllegalMemberAccess)
4. **Control flow errors** (MustInLoop)
5. **Constant errors** (CannotAssignToConstant, IllegalConstantExpression)
6. **Literal errors** (IllegalArrayLiteral)

### Scope Management
- **Global scope:** Classes, global constants
- **Class scope:** Attributes, methods (with inheritance)
- **Method scope:** Parameters, local variables
- **Block scope:** Local variables within `{}`

### Type System Rules
- **Static typing:** All types determined at compile time
- **Type coercion:** Limited to int→float and subtype→supertype
- **Inheritance:** Members inherited from parent classes
- **Access control:** Members accessible based on scope rules

### Object-Oriented Features
- **Inheritance:** Single inheritance supported
- **Polymorphism:** Method overriding allowed
- **Encapsulation:** Access control through scope rules
- **Static members:** Shared across all instances of a class

---

*Document prepared for OPLang Static Semantic Analysis*  
*Last updated: September 2025*
