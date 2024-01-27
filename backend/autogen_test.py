import autogen
import os
from dotenv import load_dotenv

load_dotenv()

class Agents:
    def __init__(self, OPENAI_API_KEY: str):
        self.OPENAI_API_KEY = OPENAI_API_KEY
        
        self.llm_config = {
            "seed": 42, 
            "temperature": 0,
            "config_list": [{"model": "gpt-3.5-turbo", "api_key": self.OPENAI_API_KEY}],
        }

        self.user_proxy = autogen.UserProxyAgent(
           name="Admin",
           system_message="A human admin. Interact with the planner to discuss the strategy. Strategy execution needs to be approved by this admin.",
           code_execution_config=False,
        )

        self.executor = autogen.AssistantAgent(
            name="Executor",
            llm_config=self.llm_config,
            system_message="Executor. You are responsible to create / execute user commands using the tools provided to you. ",
            code_execution_config={"work_dir": "results"}
        )
        
        self.critic = autogen.AssistantAgent(
            name="Critic",
            system_message="Critic. You are responsible for auditing the results of the executor",
            llm_config=self.llm_config,
        )

    def initiate_chat(self, message: str, max_rounds: int):
        self.max_rounds = max_rounds
        
        self.groupchat = autogen.GroupChat(agents=[self.user_proxy, self.executor, self.critic], messages=[], max_round=self.max_rounds)
        self.manager = autogen.GroupChatManager(groupchat=self.groupchat, llm_config=self.llm_config)
        
        self.user_proxy.initiate_chat(
            self.manager,
            message=message,
        )
        messages = self.groupchat.messages
        creator_messages = []
        for message in messages:
            if message['name'] == "Executor":
                creator_messages.append(message['content'])
        return creator_messages[-1];
    

agent = Agents(os.getenv("OPENAI_API_KEY"))
query = input("What is your task?\n")
output = agent.initiate_chat(query, 10)
print(output)