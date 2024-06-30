
# ReAct Agent on Multi-Hop RAG QA

The ReAct Agent is a dynamic agent designed to process queries, interact with a set of predefined tools, and generate responses using a language model. This agent maintains a history of interactions to provide context-aware responses and utilizes different tools to perform specific actions based on the input query. The dataset used here is the [Multi-Hop RAG dataset](https://github.com/yixuantt/MultiHop-RAG) 

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
from tools import Retrieve, AskHuman, Finish
from llms import loadllm
from react_agent import ReAct

# Initialize the tool
tools = [Retrieve(3), AskHuman(), Finish()]

# Initialize history
history = []

# Initialize the language model (llama3-70B)
llm = loadllm("Groq")

# Create an instance of the ReAct agent
react_agent = ReAct(tools, history, llm, max_steps=10)

# Run a query
query = "Which company, reported by The Verge and TechCrunch, has been associated with altering the internet's appearance, influencing Android app distribution and in-app payment systems, being the sole valid search engine service option for a major tech competitor, and is accused of harming news publishers' revenues through anticompetitive practices?" # A question from the dataset
react_agent.agentloop(query)
```

## Customization

You can customize the ReAct agent by:

- Adding new tools with specific functionalities.
- Modifying the language model or using a different one.
- Changing the maximum number of steps for processing queries.

### Adding a New Tool

To add a new tool, make sure it inherits the `Tool` class and create a class with a `run` method and add it to the tools list during initialization:

```python
class NewTool(Tool):
    def run(self, input):
        """Your tool's functionality here"""
        return "Tool response"

# Add the new tool to the tools list
tools = [NewTool()]
```


## Logging

The ReAct agent uses the `logger` from `logger_config` to log key events and errors. You can configure the logger to print the alerts on console, typically logs will be stored in `logs/app.log`


## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.

