import openai

from llm_integrations.utils import is_valid_python_code, save_py_script

from . import settings


class ChatGPT:
    def __init__(self) -> None:
        self.intro_prompt = settings.OPENAI_CHAT_GPT_INTRO_PROMPT
        self.model = settings.OPENAI_CHAT_GPT_MODEL
        self.history = []

        openai.api_key = settings.OPENAI_API_KEY

    def send_message(self, message: str) -> str:
        self.history.append({"role": "user", "content": message})
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.intro_prompt},
                *self.history
            ]
        )

        response = completion.choices[0].message.content
        self.history.append({"role": "assistant", "content": response})

        if len(self.history) > settings.HISTORY_LENGTH:
            self.history.pop(0)

        return response

    def _generate_code(self, message: str, system_prompt: str) -> str:
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        )
        return completion.choices[0].message.content
    
    def handle_parametrization_generation(self, message: str):
        response = self._generate_code(message, settings.PARAMETRIZATION_GENERATION_SYSTEM_PROMPT)
        if not is_valid_python_code(response):
            return 'Failed to generate code'
        save_py_script(response, 'parametrization')
        return response
    
    def handle_priori_generation(self, message: str):
        response = self._generate_code(message, settings.PRIORI_GENERATION_SYSTEM_PROMPT)
        if not is_valid_python_code(response):
            return 'Failed to generate code'
        save_py_script(response, 'priori')
        return response

    