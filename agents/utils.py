import code
import os
import time


def save_py_script(code: str, module: str) -> None:
    start = code.find("'")+1
    end = code.find("'", start)
    filename = code[start:end] + '_' + str(time.time_ns()) + '.py'
    # os.getcwd() will only work if code is invoked from root
    path = os.path.join(os.getcwd(), module, filename)
    print("path ", path)
    with open(path, 'w') as file:
        file.write(code)
    return path


def is_valid_python_code(code: str) -> bool:
    return compile_python_code(code) is not None


def compile_python_code(code: str, filename: str = "unknown") -> code:
    try:
        return compile(code, filename, "exec")
    except Exception:
        return None
