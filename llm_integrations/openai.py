import openai

from llm_integrations.utils import is_valid_python_code, save_parametrization_class

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

    def _generate_parametrization_class(self, message: str) -> str:
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": settings.PARAMETRIZATION_GENERATION_SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ]
        )
        return completion.choices[0].message.content
    
    def handle_parametrization_generation(self, message: str):
        response = self._generate_parametrization_class(message)
        if not is_valid_python_code(response):
            return 'Failed to generate code'
        save_parametrization_class(response)
        return response
