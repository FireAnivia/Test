from utils import Parser


def test_001():
    """Test basic class with main method"""
    source = """class Program { static void main() {} }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_002():
    """Test method with parameters"""
    source = """class Math { int add(int a; int b) { return a + b; } }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_003():
    """Test class with attribute declaration"""
    source = """class Test { int x; static void main() { x := 42; } }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_004():
    """Test class with string attribute"""
    source = """class Test { string name; static void main() { name := "Alice"; } }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_005():
    """Test final attribute declaration"""
    source = """class Constants { final float PI := 3.14159; static void main() {} }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_006():
    """Test if-else statement"""
    source = """class Test { 
        static void main() { 
            if (x > 0) then { 
                io.writeStrLn("positive"); 
            } else { 
                io.writeStrLn("negative"); 
            }
        }
    }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_007():
    """Test for loop with to keyword"""
    source = """class Test { 
        static void main() { 
            int i;
            for i := 1 to 10 do { 
                i := i + 1; 
            }
        }
    }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_008():
    """Test for loop with downto keyword"""
    source = """class Test { 
        static void main() { 
            int i;
            for i := 10 downto 1 do { 
                io.writeInt(i); 
            }
        }
    }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_009():
    """Test array declaration and access"""
    source = """class Test { 
        static void main() { 
            int[3] arr := {1, 2, 3};
            int first;
            first := arr[0];
            arr[1] := 42;
        }
    }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_010():
    """Test string concatenation and object creation"""
    source = """class Test { 
        static void main() { 
            string result;
            Test obj;
            result := "Hello" ^ " " ^ "World";
            obj := new Test();
        }
    }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_011():
    """Test parser error: missing closing brace in class declaration"""
    source = """class Test { int x := 1; """  # Thiếu dấu }
    expected = "Error on line 1 col 25: <EOF>"
    assert Parser(source).parse() == expected
