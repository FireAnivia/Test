from ..utils.nodes import *
from .utils import *


LIB_NAME = "io"

IO_SYMBOL_LIST = [
    # Integer I/O
    Symbol("readInt", FunctionType([], PrimitiveType("int")), CName(LIB_NAME)),
    Symbol("writeInt", FunctionType([PrimitiveType("int")], PrimitiveType("void")), CName(LIB_NAME)),
    Symbol("writeIntLn", FunctionType([PrimitiveType("int")], PrimitiveType("void")), CName(LIB_NAME)),
    
    # Float I/O
    Symbol("readFloat", FunctionType([], PrimitiveType("float")), CName(LIB_NAME)),
    Symbol("writeFloat", FunctionType([PrimitiveType("float")], PrimitiveType("void")), CName(LIB_NAME)),
    Symbol("writeFloatLn", FunctionType([PrimitiveType("float")], PrimitiveType("void")), CName(LIB_NAME)),
    
    # Boolean I/O
    Symbol("readBool", FunctionType([], PrimitiveType("boolean")), CName(LIB_NAME)),
    Symbol("writeBool", FunctionType([PrimitiveType("boolean")], PrimitiveType("void")), CName(LIB_NAME)),
    Symbol("writeBoolLn", FunctionType([PrimitiveType("boolean")], PrimitiveType("void")), CName(LIB_NAME)),
    
    # String I/O
    Symbol("readStr", FunctionType([], PrimitiveType("string")), CName(LIB_NAME)),
    Symbol("writeStr", FunctionType([PrimitiveType("string")], PrimitiveType("void")), CName(LIB_NAME)),
    Symbol("writeStrLn", FunctionType([PrimitiveType("string")], PrimitiveType("void")), CName(LIB_NAME)),
]

