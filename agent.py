from logger_config import logger
from utils import extract_json_manually
import json
from llama_index.core.llms import ChatMessage
from prompts import react_prompt
from termcolor import colored

class ReAct:
    """
    A class to represent the ReAct agent.

    Attributes:
        tools (list): A list of tools available for the agent.
        history (list): A list to maintain the history of interactions.
        llm (object): The language model used for generating responses.
        max_steps (int): Maximum number of steps the agent will take in a single query.

    Methods:
        __init__(tools, history, llm, max_steps=10): Initializes the ReAct agent with tools, history, LLM, and max steps.
        update_history(episode): Updates the interaction history.
        _run(query, max_retries=3): Runs a single step of the agent's loop with retries for JSON decoding.
        agentloop(query): Main loop for the agent to process the query and produce results.
    """

    def __init__(self, tools, history, llm, max_steps=10):
        """
        Initializes the ReAct agent with tools, history, LLM, and max steps.

        Args:
            tools (list): A list of tools available for the agent.
            history (list): A list to maintain the history of interactions.
            llm (object): The language model used for generating responses.
            max_steps (int, optional): Maximum number of steps the agent will take in a single query. Defaults to 10.
        """
        self.tools = tools
        self.history = history
        self.llm = llm
        self.max_steps = max_steps
        tool_descriptions = "\n".join([f"{tool.__class__.__name__.lower()}: {tool.run.__doc__}" for tool in tools])
        self.tool_descriptions = tool_descriptions
        logger.info("ReAct agent initialized with tools: %s", [tool.__class__.__name__ for tool in tools])

    def update_history(self, episode):
        """
        Updates the interaction history.

        Args:
            episode (str): The latest episode to be added to the history.
        """
        if len(self.history) > 3:
            self.history = self.history[1:]
        self.history.append(episode)
        logger.debug("History updated")

    def _run(self, query, max_retries=3):
        """
        Runs a single step of the agent's loop with retries for JSON decoding.

        Args:
            query (str): The query to be processed.
            max_retries (int, optional): Maximum number of retries for JSON decoding. Defaults to 3.

        Returns:
            tuple: A tuple containing thought, action, and action input.
        """
        for i in range(max_retries):
            history_string = "\n\n".join(self.history)
            prompt = react_prompt.DEFAULT_PROMPT.format(query=query, history=history_string,
                                                        tool_descriptions=self.tool_descriptions)

            response = self.llm.chat([ChatMessage(role="system", content=react_prompt.system_prompt),
                                      ChatMessage(role="user", content=prompt)]
                                     ).message.content

            try:
                result = json.loads(response)
                break
            except json.decoder.JSONDecodeError:
                logger.warning("JSON decode error. Trying manual extraction.")
                result = extract_json_manually(response)
                if result:
                    break
        else:
            logger.error("Failed to decode JSON after %d retries.", max_retries)
            result = {}

        thought = result.get("thought", "Empty")
        action = result.get("action", "Empty")
        action_input = result.get("input", "Empty")

        return thought, action, action_input

    def agentloop(self, query):
        """
        Main loop for the agent to process the query and produce results.

        Args:
            query (str): The query to be processed.
        """
        logger.info("Running query: %s", query)
        print(f"{colored('QUERY', 'cyan', attrs=['bold'])}: {colored(f'{query}', 'green')}")

        iteration = 1
        while iteration <= self.max_steps:
            logger.info("Iteration %d", iteration)
            current_thought, current_action, current_action_input = self._run(query)

            # Print essential information to the terminal
            print(f"\n{colored(f'THOUGHT {iteration}', 'red', attrs=['bold'])} :{current_thought}")
            print(f"{colored(f'ACTION {iteration}', 'red', attrs=['bold'])} :{current_action}")
            print(f"{colored(f'ACTION INPUT {iteration}', 'red', attrs=['bold'])} :{current_action_input}")

            if current_action == "finish":
                logger.info("Finish action received. Exiting loop.")
                self.update_history(current_action_input)
                break
            else:
                current_tool = next((tool for tool in self.tools if current_action == tool.__class__.__name__.lower()),
                                    None)
                if current_tool is None:
                    logger.error("No matching tool found for action: %s", current_action)
                    break
                logger.info("Using tool: %s", current_tool.__class__.__name__)
                observation = current_tool.run(current_action_input)

                # Print observation to the terminal
                print(f"\n{colored(f'OBSERVATION {iteration}', 'red', attrs=['bold'])}: \n{observation}\n")

            episode = "\n".join([
                f"{colored(f'THOUGHT {iteration}', 'red', attrs=['bold'])} :{current_thought}",
                f"{colored(f'ACTION {iteration}', 'red', attrs=['bold'])} :{current_action}",
                f"{colored(f'ACTION INPUT {iteration}', 'red', attrs=['bold'])} :{current_action_input}",
                f"{colored(f'OBSERVATION {iteration}', 'red', attrs=['bold'])} :{observation}"
            ])
            self.update_history(episode)
            iteration += 1

        if self.history:
            print(colored(f"\n\nFINAL ANSWER: {self.history.pop()}", 'light_blue', attrs=['bold']))
        logger.info("Agent loop finished.")
