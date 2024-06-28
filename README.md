
# ReAct Agent on Multi-Hop RAG QA

The ReAct Agent is a dynamic agent designed to process queries, interact with a set of predefined tools, and generate responses using a language model. This agent maintains a history of interactions to provide context-aware responses and utilizes different tools to perform specific actions based on the input query.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/deepakachu5114/ReAct-agent-Multi-Hop-RAG
    cd ReAct-agent-Multi-Hop-RAG
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up the necessary environment variables, any one will do:
    ```bash
    export GROQ_API_KEY="your_groq_api_key"
    export OLLAMA_BASE_URL="your_ollama_base_url"
    export OPENAI_API_KEY="your_openai_api_key"
    ```

## Usage

### Initialization

Create an instance of the `ReAct` agent with the necessary tools, history, language model, and maximum steps:

```python
from tools import YourTool
from utils import loadllm

# Initialize your tools
tools = [YourTool()]

# Initialize history (can be an empty list)
history = []

# Initialize your language model
llm = loadllm("Groq/Ollama/OpenAI")

# Create an instance of the ReAct agent
react_agent = ReAct(tools, history, llm, max_steps=10)
```

### Running a Query

Use the `agentloop` method to process a query:

```python
query = "Your query here"
react_agent.agentloop(query)
```

The agent will process the query, interact with the tools, and provide the final response based on the context and actions performed.

## Example

Here is an example of how to initialize and run the ReAct agent:

```python
from tools import MyTool (Import any tool that you want)
from llms import loadllm
from react_agent import ReAct

# Initialize the tool
tools = [MyTool()]

# Initialize history
history = []

# Initialize the language model
llm = loadllm("Groq/Ollama/OpenAI")

# Create an instance of the ReAct agent
react_agent = ReAct(tools, history, llm, max_steps=10)

# Run a query
query = "Tell me about the history of AI."
react_agent.agentloop(query)
```

## Customization

You can customize the ReAct agent by:

- Adding new tools with specific functionalities.
- Modifying the language model or using a different one.
- Changing the maximum number of steps for processing queries.

### Adding a New Tool

To add a new tool, create a class with a `run` method and add it to the tools list during initialization:

```python
class NewTool:
    def run(self, input):
        """Your tool's functionality here"""
        return "Tool response"

# Add the new tool to the tools list
tools = [NewTool()]
```


## Logging

The ReAct agent uses the `logger` from `logger_config` to log key events and errors. Ensure you have configured the logger properly in `logger_config.py` to capture and store logs as needed.

## Contributing

If you want to contribute to the ReAct agent, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.

