from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, \
    HumanMessagePromptTemplate

from . import consts


class Chat:
    def __init__(self, intro_prompt: str) -> None:
        self.llm = ChatOpenAI()
        self.memory = ConversationBufferMemory(memory_key=consts.LANGCHAIN_MEMORY_KEY, return_messages=True)
        self.prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(intro_prompt),
                MessagesPlaceholder(variable_name=consts.LANGCHAIN_MEMORY_KEY),
                HumanMessagePromptTemplate.from_template(consts.LANGCHAIN_HUMAN_MESSAGE_TEMPLATE)
            ]
        )

    def send_message(self, message: str) -> str:
        conversation = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory,
        )
        response = conversation({consts.LANGCHAIN_HUMAN_MESSAGE_KEY: message})["text"]

        return response
