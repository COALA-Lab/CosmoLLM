from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, \
    HumanMessagePromptTemplate

from . import consts, settings


class Chat:
    def __init__(self) -> None:
        self.llm = ChatOpenAI()
        self.memory = ConversationBufferMemory(memory_key=consts.LANGCHAIN_MEMORY_KEY, return_messages=True)
        self.prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(settings.LANGCHAIN_CHAT_INTRO_PROMPT),
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
