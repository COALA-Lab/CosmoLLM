import code
import os
import time
import json


# def save_py_script(code: str, module: str) -> None:
#     start = code.find("'")+1
#     end = code.find("'", start)
#     filename = code[start:end] + '_' + str(time.time_ns()) + '.py'
#     # os.getcwd() will only work if code is invoked from root
#     path = os.path.join(os.getcwd(), module, filename)
#     with open(path, 'w') as file:
#         file.write(code)
#     return filename


def save_py_script(code: str, module: str) -> None:
    start = code.find("'")+1
    end = code.find("'", start)
    filename = code[start:end] + '_' + str(time.time_ns()) + '.py'

    directory = os.path.join(os.getcwd(), module)
    if not os.path.exists(directory):
        os.makedirs(directory)

    path = os.path.join(directory, filename)

    try:
        with open(path, 'w') as file:
            file.write(code)
            file.flush()
            os.fsync(file.fileno())
        return filename
    except Exception as e:
        print(f"error: {e}")
        return None

def save_json_file(data: dict, module: str) -> str:
    filename = f'data_{str(time.time_ns())}.json'
    path = os.path.join(os.getcwd(), module, filename)
    with open(path, 'w') as file:
        json.dump(data, file, indent=2)
    return path


def is_valid_python_code(code: str) -> bool:
    return compile_python_code(code) is not None

def is_valid_json(my_str: str):
    try:
        json.loads(my_str)
        return True
    except json.JSONDecodeError:
        return False


def compile_python_code(code: str, filename: str = "unknown") -> code:
    try:
        return compile(code, filename, "exec")
    except Exception:
        return None
