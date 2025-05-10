"""
Edge cases examples for code-chunker
"""

from code_chunker import CodeChunker

chunker = CodeChunker()

# Python edge cases
python_edge_cases = """
# 1. Nested function definitions
def outer():
    def inner1():
        def inner2():
            pass
        return inner2
    return inner1

# 2. Decorator chains
@decorator1
@decorator2(param=True)
@decorator3
def decorated_function():
    pass

# 3. Complex class inheritance
class Multi(Base1, Base2, metaclass=MetaClass):
    '''Multiple inheritance and metaclass'''
    pass

# 4. Async context managers
class AsyncContextManager:
    async def __aenter__(self):
        pass
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

# 5. Complex type annotations
def complex_typing(
    data: Dict[str, Union[List[int], Tuple[str, ...]]],
    callback: Callable[[int], Awaitable[None]]
) -> Optional[Generator[int, None, None]]:
    pass

# 6. Lambda expressions
complex_lambda = lambda x, y=10: (lambda z: x + y + z)
"""

# JavaScript/TypeScript edge cases
js_edge_cases = """
// 1. Complex arrow functions
const complex = (a, b = 10) => ({ 
    sum: a + b,
    multiply: () => a * b,
    nested: (c) => (d) => a + b + c + d
});

// 2. Classes with static methods
class StaticExample {
    static staticMethod() {
        return this.staticProp;
    }
    static staticProp = 42;
    
    #privateField = 'private';
    
    get privateField() {
        return this.#privateField;
    }
}

// 3. Generator functions
function* generatorFunction() {
    yield 1;
    yield* anotherGenerator();
}

// 4. Dynamic property names
const dynamicProp = 'test';
const obj = {
    [dynamicProp]: 'value',
    [`computed_${dynamicProp}`]: 'computed'
};

// 5. TypeScript generic constraints
interface Complex<T extends BaseType = DefaultType> {
    process<U extends T>(data: U): Promise<U>;
}

// 6. Complex destructuring
const { a: { b: [c, ...rest] }, d = defaultValue } = complex;
"""

# Go edge cases
go_edge_cases = """
// 1. Method sets and interface embedding
type Writer interface {
    Write([]byte) (int, error)
}

type ReadWriter interface {
    Reader
    Writer
}

// 2. Type assertions and type switches
func typeSwitch(i interface{}) {
    switch v := i.(type) {
    case int:
        fmt.Printf("Integer: %v", v)
    case string:
        fmt.Printf("String: %v", v)
    default:
        fmt.Printf("Unknown type")
    }
}

// 3. Anonymous struct fields
type Person struct {
    Name string
    Address struct {
        Street string
        City   string
    }
}

// 4. Generic functions (Go 1.18+)
func Min[T constraints.Ordered](a, b T) T {
    if a < b {
        return a
    }
    return b
}

// 5. Multiple return values and named returns
func divide(a, b float64) (result float64, err error) {
    if b == 0 {
        err = errors.New("division by zero")
        return
    }
    result = a / b
    return
}
"""

# Rust edge cases
rust_edge_cases = """
// 1. Lifetime annotations
impl<'a, T: Clone> MyStruct<'a, T> {
    fn complex_lifetime<'b>(&'a self, other: &'b T) -> &'a T 
    where
        'b: 'a,
    {
        self.value
    }
}

// 2. Macro definitions
macro_rules! create_function {
    ($func_name:ident) => {
        fn $func_name() {
            println!("Called {:?}()", stringify!($func_name));
        }
    };
}

// 3. Pattern matching and destructuring
match some_value {
    Ok(x) if x > 0 => println!("Positive: {}", x),
    Ok(x) => println!("Non-positive: {}", x),
    Err(e) => eprintln!("Error: {}", e),
}

// 4. Associated types
trait Container {
    type Item;
    fn get(&self, index: usize) -> Option<&Self::Item>;
}

// 5. Unsafe code blocks
unsafe fn dangerous() {
    let raw_ptr = &mut COUNTER as *mut i32;
    *raw_ptr += 1;
}

// 6. Closures with move semantics
let closure = move |x: i32| -> i32 {
    captured_value + x
};
"""

def test_edge_cases():
    """Test edge cases for different programming languages"""
    languages = [
        ('python', python_edge_cases),
        ('javascript', js_edge_cases),
        ('go', go_edge_cases),
        ('rust', rust_edge_cases),
    ]
    
    for lang, code in languages:
        print(f"\n{'='*50}")
        print(f"Testing {lang.upper()} edge cases")
        print(f"{'='*50}")
        
        try:
            result = chunker.parse(code, lang)
            
            print(f"Chunks found: {len(result.chunks)}")
            
            # Categorize and count chunks
            chunk_types = {}
            for chunk in result.chunks:
                chunk_type = chunk.type.value
                chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
            
            print("\nChunk types:")
            for chunk_type, count in chunk_types.items():
                print(f"  {chunk_type}: {count}")
            
            # Show complex chunks
            complex_chunks = [
                c for c in result.chunks 
                if len(c.code.split('\n')) > 5 or 
                'lambda' in c.code or 
                'generic' in c.code.lower() or
                (c.name and 'complex' in c.name.lower())
            ]
            
            if complex_chunks:
                print(f"\nComplex chunks ({len(complex_chunks)}):")
                for chunk in complex_chunks[:3]:  # Show only first 3
                    print(f"  - {chunk.type.value}: {chunk.name}")
                    
        except Exception as e:
            print(f"Error parsing {lang}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_edge_cases() 