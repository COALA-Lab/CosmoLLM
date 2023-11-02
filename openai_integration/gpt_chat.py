
import openai

import settings


class GPTChat:
    def __init__(self) -> None:
        self.intro_prompt = settings.GPT_CHAT_INTRO_PROMPT
        self.model = "gpt-3.5-turbo"  # settings.GPT_CHAT_MODEL
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


gpt_chat = GPTChat()
user_message = "this is the code of my function def bla(a,b):return a*b write me a code that calls this function for all numbers a=1..20 and b=3..40. also, the code must make a 3d plot of the returned results, with a on x-axis, b on y-axis and result on z axis."
response = gpt_chat.send_message(user_message)
print(response)
