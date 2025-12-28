from utils import Tokenizer


def test_001():
    """Test basic identifier tokenization"""
    source = "abc"
    expected = "abc,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_002():
    """Test keywords recognition"""
    source = "class extends static final if else for do then to downto new this void boolean int float string true false nil break continue return"
    expected = "class,extends,static,final,if,else,for,do,then,to,downto,new,this,void,boolean,int,float,string,true,false,nil,break,continue,return,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_003():
    """Test integer literals"""
    source = "42 0 255 2500"
    expected = "42,0,255,2500,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_004():
    """Test float literals"""
    source = "9.0 12e8 1. 0.33E-3 128e+42"
    expected = "9.0,12e8,1.,0.33E-3,128e+42,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_005():
    """Test boolean literals"""
    source = "true false"
    expected = "true,false,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_006():
    """Test unclosed string literal error"""
    source = '"Hello World'
    expected = "Unclosed String: Hello World"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_007():
    """Test illegal escape sequence error"""
    source = '"Hello \\x World"'
    expected = "Illegal Escape In String: Hello \\x"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_008():
    """Test error character (non-ASCII or invalid character)"""
    source = "int x := 5; @ invalid"
    expected = "int,x,:=,5,;,Error Token @"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_009():
    """Test valid string literals with escape sequences"""
    source = '"This is a string containing tab \\t" "He asked me: \\"Where is John?\\""'
    expected = "This is a string containing tab \\t,He asked me: \\\"Where is John?\\\",EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_009a():
    """Test string literals return content without quotes"""
    source = '"Hello World"'
    expected = "Hello World,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_009b():
    """Test empty string literal"""
    source = '""'
    expected = ",EOF"  # Empty string content
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_010():
    """Test operators and separators"""
    source = "+ - * / \\ % == != < <= > >= && || ! := ^ new . ( ) [ ] { } , ; :"
    expected = "+,-,*,/,\\,%,==,!=,<,<=,>,>=,&&,||,!,:=,^,new,.,(,),[,],{,},,,;,:,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected