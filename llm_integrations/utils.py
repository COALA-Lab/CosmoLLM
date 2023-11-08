
from datetime import datetime
import os
import time

def save_parametrization_class(code: str):
    start = code.find("'")+1
    end = code.find("'", start)
    filename = code[start:end] + '_' + str(time.time_ns()) + '.py'
    # os.getcwd() will only work if code is invoked from root
    path = os.path.join(os.getcwd(), 'parametrization', filename)
    with open(path, 'w') as file:
        file.write(code)

def is_valid_python_code(code: str):
    try:
        compile(code, "test", "exec")
        return True
    except:
        return False
