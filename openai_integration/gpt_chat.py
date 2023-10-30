import openai

from . import settings


class GPTChat:
    def __init__(self) -> None:
        self.intro_prompt = settings.GPT_CHAT_INTRO_PROMPT
        self.model = settings.GPT_CHAT_MODEL
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

        return response
