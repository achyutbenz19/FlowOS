from pathlib import Path
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools.ddg_search import DuckDuckGoSearchRun
from langchain.tools.shell import ShellTool
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.storage import LocalFileStore
from langchain_core.prompts import SystemMessagePromptTemplate, PromptTemplate, ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from dotenv import load_dotenv

load_dotenv()

class Agent:
    def __init__(self) -> None:
        self.chat_memory = ConversationBufferWindowMemory(
            k=5,
            return_messages=True
        )
        self.prompt: ChatPromptTemplate = hub.pull("hwchase17/openai-tools-agent")
        self.prompt.messages = [
            SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=[], template='You are a helpful assistant that helps the user with their tasks.')), 
            MessagesPlaceholder(variable_name='chat_history', optional=True), 
            HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template='{input}')), 
            MessagesPlaceholder(variable_name='agent_scratchpad')
        ]
        self.llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

        search_tool = DuckDuckGoSearchRun()
        shell_tool = ShellTool()
        self.tools = [
            search_tool, 
            shell_tool
        ]

        root_path = Path.cwd() / "db"
        self.db = LocalFileStore(root_path)

        agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def get_chat_history(self):
        return self.chat_memory.load_memory_variables({})['history']

    def chat(self, query: str):
        chat_history = self.get_chat_history()

        input_dict = {'input': query}

        if chat_history:
            input_dict['chat_history'] = chat_history
        
        output = self.agent_executor.invoke(input_dict)
        self.chat_memory.save_context({'input': query}, {'output': output['output']})
        return output


if __name__ == "__main__":
    agent = Agent()
    while True:
        query = input(">> ")
        print(agent.chat(query))