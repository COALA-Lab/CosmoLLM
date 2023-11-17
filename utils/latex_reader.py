from TexSoup import TexSoup
from llm_integrations.openai import ChatGPT


def execute(filename: str):
    tex_doc = load_file_into_string(filename)

    soup = TexSoup(tex_doc)
    equations = soup.find_all('equation') + soup.find_all('equation*') + soup.find_all('displaymath')

    chat = ChatGPT()

    for equation in equations:
        equation_content = ''.join(str(elem).strip() for elem in equation.all)
        chat.handle_function_generation(equation_content)


def load_file_into_string(filepath):
    try:
        with open(filepath, 'r') as file:
            file_contents = file.read()
        return file_contents
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
