from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.agents import Tool, initialize_agent
from langchain.memory import ConversationBufferMemory

import settings

memory = ConversationBufferMemory(memory_key="chat_history")

llm = OpenAI(
    openai_api_key=settings.OPENAI_API_KEY,
    temperature=0,
    model_name=settings.GPT_CHAT_MODEL
)
template = """This is the function {function}. \n
    Write me a code that calls this function for all numbers a={a} and b={b}. \n
    Also, the code must make a 3d plot of the returned results, \n
    with a on x-axis, b on y-axis and result on z axis."""

prompt = PromptTemplate(
    input_variables=["function", "a", "b"], template=template)

llm_chain = LLMChain(llm=llm, prompt=prompt)

llm_tool = Tool(
    name='Language Model',
    func=llm_chain.run,
    description=settings.GPT_CHAT_INTRO_PROMPT
)

tools = [llm_tool]

conversational_agent = initialize_agent(
    agent='conversational-react-description',
    tools=tools,
    llm=llm,
    verbose=True,
    max_iterations=3,
    memory=memory,
)

conversational_agent(prompt.format(
    function="z=a*b", a="3..40", b="1..20"))
