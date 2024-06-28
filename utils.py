import json
import os
import re
from typing import Any, Generator, List, Optional
from llama_index.core.schema import QueryBundle, MetadataMode
from llama_index.core.llms import ChatMessage
from logger_config import logger
from llama_index.core import Settings
from llama_index.core import Document
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.llms.ollama import Ollama
from langchain_community.chat_models import ChatOllama
from llama_index.llms.openai import OpenAI

DEFAULT_MAX_TOKENS = 2048
DEFAULT_TEMP = 0.5

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["OLLAMA_BASE_URL"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def load_data(input_file: str) -> List[Document]:
    """Load data from the input file."""
    documents = []
    with open(input_file, 'r') as file:
        load_data = json.load(file)
    for data in load_data:
        metadata = {"title": data['title'], "published_at": data['published_at'], "source": data['source']}
        documents.append(Document(text=data['body'], metadata=metadata))
    return documents

def loadEmbeddingModel(host, name=None):
    if host == "ollama":
        default_name = "nomic-embed-text"
        logger.info(f"Loading ollama model {default_name} by default. You can change it with the 'name' parameter.")
        try:
            model = OllamaEmbedding(
                model_name=name or default_name,
                base_url=os.environ.get("OLLAMA_BASE_URL"),
            )
            return model
        except Exception as e:
            logger.error(f"Error loading ollama model: {e}")
    elif host == "huggingface":
        default_name = "sentence-transformers/all-mpnet-base-v2"
        logger.info(f"Loading huggingface model {default_name} by default. You can change it with the 'name' parameter.")
        try:
            model = HuggingFaceEmbedding(model_name=name or default_name)
            return model
        except Exception as e:
            logger.error(f"Error loading huggingface model: {e}")
    else:
        raise ValueError(f"Unsupported model type: {host}")

def loadllm(host, name=None, max_tokens=DEFAULT_MAX_TOKENS, temperature=DEFAULT_TEMP):
    if host == "Ollama":
        default_name = "llama3"
        logger.info(f"Loading ollama llm {default_name} by default. You can change it with the 'name' parameter.")
        try:
            Settings.llm = Ollama(
                model=name or default_name,
                base_url=os.environ.get("OLLAMA_BASE_URL"),
                request_timeout=60.0,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return Settings.llm
        except Exception as e:
            logger.error(f"Error loading ollama llm model: {e}")
    elif host == "Groq":
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            logger.error("GROQ_API_KEY environment variable not set. Please set it to your Groq API key.")
            return None
        default_name = "llama3-70b-8192"
        try:
            Settings.llm = Groq(model=default_name, api_key=api_key, temperature=temperature, max_tokens=max_tokens)
            return Settings.llm
        except Exception as e:
            logger.error(f"Error loading groq llm model: {e}")
    elif host == "OpenAI":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set. Please set it to your Open AI API key.")
            return None
        default_name = "gpt-4"
        try:
            model = OpenAI(model=name or default_name, api_key=api_key)
            return model
        except Exception as e:
            logger.error(f"Error loading Open AI llm model: {e}")

def nodeExtractor(context_list):
    context_nodes = []
    for node in context_list:
        context_nodes.append({
            "text": node.text,
            "metadata": node.metadata,
            "score": node.score,
        })
    return context_nodes

def getContextString(nodes):
    contexts = []
    for node in nodes:
        content = node.get_content(metadata_mode=MetadataMode.LLM).replace("\n\n", "\n")
        contexts.append(content)
    context_str = "\n\n".join(contexts)
    return context_str

def extract_json_manually(text):
    try:
        match = re.search(r'\{.*?}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except json.JSONDecodeError:
        pass
    return None
