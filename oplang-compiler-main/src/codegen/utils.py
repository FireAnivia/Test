from ..utils.nodes import Type
from .frame import Frame


class FunctionType(Type):
    """Function type node."""

    def __init__(self, param_types, return_type):
        super().__init__()
        self.param_types = param_types
        self.return_type = return_type

    def accept(self, visitor, o=None):
        return visitor.visit_function_type(self, o)


class ClassType(Type):
    """Class type node."""

    def __init__(self, class_name):
        super().__init__()
        self.class_name = class_name

    def accept(self, visitor, o=None):
        return visitor.visit_class_type(self, o)


class Value:
    pass


class Index(Value):
    def __init__(self, value: int):
        self.value = value


class CName(Value):
    def __init__(self, value: str):
        self.value = value


class Symbol:
    def __init__(self, name: str, _type: Type, value: Value):
        self.name = name
        self.type = _type
        self.value = value


class Access:
    def __init__(
        self,
        frame: Frame,
        sym: list["Symbol"],
        is_left: bool = False,
        is_first: bool = False,
    ):
        self.frame = frame
        self.sym = sym
        self.is_left = is_left
        self.is_first = is_first


class SubBody:
    def __init__(self, frame: Frame, sym: list["Symbol"]):
        self.frame = frame
        self.sym = sym

