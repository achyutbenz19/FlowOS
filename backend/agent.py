import platform
from typing import Optional, List
from pathlib import Path
from langchain import hub
from langchain_community.tools.shell.tool import ShellInput
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_community.tools import DuckDuckGoSearchRun, ShellTool, YouTubeSearchTool, tool, Tool
from langchain_community.utilities.stackexchange import StackExchangeAPIWrapper
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.storage import LocalFileStore
from langchain_core.prompts import SystemMessagePromptTemplate, PromptTemplate, ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from pydantic import BaseModel, Field
from tts import speak
from terminal import AsyncShellTool
from dotenv import load_dotenv
load_dotenv()

def stack_exchange_search(query: str):
    """
    A forum search engine. Useful for when you need to answer questions about programming and errors.
    """
    wrapper = StackExchangeAPIWrapper()
    return wrapper.run(query)

def _get_platform() -> str:
    """Get platform."""
    system = platform.system()
    if system == "Darwin":
        return "MacOS"
    return system

async_shell_tool = AsyncShellTool()
def long_running_terminal_command(command: str) -> str:
    return async_shell_tool._run(command)

long_shell_tool = Tool(
    name="long_shell",
    description=f"Run long running shell commands on this {_get_platform()} machine. Use this to run commands that take a long time/infinite to complete so that it can run in the background.",
    func=long_running_terminal_command,
)
search_tool = DuckDuckGoSearchRun()
short_shell_tool = ShellTool()
youtube_tool = YouTubeSearchTool()
stack_exchange_tool = tool(stack_exchange_search)

tool_map = {
    "short_shell": short_shell_tool,
    "long_shell": long_shell_tool,
    "youtube": youtube_tool,
    "search": search_tool,
    "stack_exchange": stack_exchange_tool
}


class AgentConfig(BaseModel):
    system_prompt: str = Field(default=f'''\
You are Flow, a coding assistant that assists the human in developing programs and applications. \
You are powered by multiple different tools that you will use to help the user complete tasks \
Tasks can include things like creating programs, opening up the IDE, searching the web for documentation \
and more. \
Remeber. The user is running on {_get_platform()}. \
Before responding, think thoroughly about what the user is asking and what tool(s) would be best to use. \
When needed, break down the user's request into smaller steps before proceeding. \
Ask the human for more information only if you are unsure of what to do or if the request is ambiguous. \
Always try searching the web for up to date information about documentation on libraries when coding and debugging. \
Make sure your response are as concise as possible. \
''')

    llm_model: str = Field(default="gpt-3.5-turbo-1106")

    llm_temperature: float = Field(default=0.1, ge=0, le=1)

    chat_memory_k: int = Field(default=6)

    tools: List[str] = ["short_shell", "long_shell", "youtube", "search"]

    workflows_db_path: str = "workflows_db"

    verbose: bool = True

    voice: str = "Thomas"

class Agent:
    def __init__(
        self,
        config: Optional[AgentConfig] = None
    ) -> None:
        self.config = config or AgentConfig()
        self.chat_memory = ConversationBufferWindowMemory(
            k=self.config.chat_memory_k,
            return_messages=True
        )
        self.voice = self.config.voice
        self.prompt: ChatPromptTemplate = hub.pull("hwchase17/openai-tools-agent")
        self.prompt.messages = [
            SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=[], template=self.config.system_prompt)), 
            MessagesPlaceholder(variable_name='chat_history', optional=True), 
            HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template='{input}')), 
            MessagesPlaceholder(variable_name='agent_scratchpad')
        ]

        if self.config.llm_model.startswith("gpt-"):
            self.llm = ChatOpenAI(model=self.config.llm_model, temperature=self.config.llm_temperature)
        else:
            raise NotImplementedError("Only GPT models are supported at the moment.")

        self.tools = [
            tool_map[tool] for tool in self.config.tools
        ]

        root_path = Path.cwd() / self.config.workflows_db_path
        print(f"Using {root_path} as db path")
        self.db = LocalFileStore(root_path)

        self.in_workflow: bool = False
        self.workflow_queries: list = []
        agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
        self.workflow_name: Optional[str] = None

    def start_workflow(self, workflow_name: str):
        if self.in_workflow:
            message = f"You're already creating {self.workflow_name}. Complete it before creating another one"
            print(message)
            speak(message, self.voice)
            return message
        
        self.in_workflow = True
        self.workflow_queries = []
        exists = self.db.mget([workflow_name])
        if exists[0]:
            message = f"I am sorry but the workflow {workflow_name} already exists"
            print(message)
            speak(message, self.voice)
            return message

        self.workflow_name = workflow_name
        message = f"Recording {workflow_name}. Ask me anything"
        speak(message, self.voice)
        print(message)
        return message

    def end_workflow(self):
        if not self.in_workflow:
            message = "You are not currently in a workflow. Please start one first."
            print(message)
            return message
        
        self.in_workflow = False
        bytes_queries = "\n".join(self.workflow_queries)
        self.db.mset([(self.workflow_name, bytes_queries.encode("utf-8"))])

        messasge = f"Workflow {self.workflow_name} ended! Saved to db."
        return messasge

    def run_workflow(self, workflow_name: str):
        workflow_queries = self.db.mget([workflow_name])
        if not workflow_queries:
            message = f"Workflow {workflow_name} does not exist!"
            print(message)
            return message
        
        for query in workflow_queries[0].decode().split("\n"):
            print(f"Running query: {query}")
            self.chat(query)

        message = f"Workflow {workflow_name} ran!"
        self.chat_memory.save_context({'input': f"Start {workflow_name}"}, {'output': f"Successfully run {workflow_name}"})
        return message

    def get_chat_history(self):
        return self.chat_memory.load_memory_variables({})['history']

    def chat(
        self, 
        query: str, 
        save_chat_history: bool = True, 
        use_chat_history: bool = True,
        is_voice: bool = True
    ):
        if "start workflow" in query.lower():
            workflow_name = query.split("start workflow")[1].strip()
            return self.start_workflow(workflow_name.replace(" ", "_"))
        elif "end workflow" in query.lower():
            return self.end_workflow()
        elif "run workflow" in query.lower():
            workflow_name = query.split("run workflow")[1].strip().replace(" ", "_")
            return self.run_workflow(workflow_name)
        elif "clear workflow" in query.lower().replace(" ", "_"):
            self.workflow_name = None
            self.workflow_queries = []
            return "Workflow cleared!"
        
        chat_history = self.get_chat_history()

        input_dict = {'input': query}

        if chat_history and use_chat_history:
            input_dict['chat_history'] = chat_history
        
        output = self.agent_executor.invoke(input_dict)

        if self.in_workflow:
            self.workflow_queries.append(query)

        if save_chat_history:
            self.chat_memory.save_context({'input': query}, {'output': output['output']})
        final_response = output['output']
        if is_voice:
            speak(final_response, self.voice)
        return {
            'input': query,
            'output': final_response
        }


if __name__ == "__main__":
    agent = Agent()
    while True:
        query = input("Query: ")
        print(agent.chat(query))