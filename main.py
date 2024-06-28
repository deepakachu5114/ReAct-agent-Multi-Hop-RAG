from agent import ReAct
from tools import Finish, AskHuman, Retrieve
from logger_config import logger
from utils import loadllm
from termcolor import colored


llm = loadllm("Groq")
retrieve = Retrieve(3)
finish = Finish()
askhuman = AskHuman()
history = []
tools = [retrieve, finish, askhuman]


agent = ReAct(tools, history, llm)

if __name__ == '__main__':
    query = input(colored("Please enter your query: ", 'light_magenta'))
    agent.agentloop(query)