from abc import ABC, abstractmethod
from logger_config import logger
from llama_index.core.node_parser import LangchainNodeParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from llama_index.core.retrievers import VectorIndexRetriever
from utils import load_data, loadllm, loadEmbeddingModel, nodeExtractor, getContextString, extract_json_manually
from vectorstore import VectorStore
import json, os
from termcolor import colored
class Tool(ABC):
    """
    Abstract base class for tools.

    Methods:
    run(input_params):
    Abstract method to run the tool with given input parameters.
    """
    @abstractmethod
    def run(self, input_params):
        pass

class Retrieve(Tool):
    """
    A retriever tool to retrieve relevant documents based on a query.
    Parameters
    top_k : int
    The number of top similar documents to retrieve.

    Methods
    retriever : VectorIndexRetriever
    The retriever object for fetching relevant documents.
    """
    def __init__(self, top_k):
        """
        Initializes the Retriever with the top_k parameter and sets up the retriever.
        Parameters
        top_k : int
        The number of top similar documents to retrieve.
        """
        embed_model = loadEmbeddingModel("huggingface")
        store = VectorStore()
        vector_store_path = "data/vector/default"
        data = load_data('data/corpus.json')
        text_splitter = LangchainNodeParser(RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200))
        nodes = text_splitter.get_nodes_from_documents(data)
        if os.path.exists(vector_store_path):
            index = store.create_index_from_stored(embed_model=embed_model)
        else:
            index = store.create_index(llama_index_nodes=nodes, embed_model=embed_model)
        retriever = VectorIndexRetriever(index=index, similarity_top_k=top_k, embedding_model=embed_model, verbose=True)
        self.retriever = retriever

    def run(self, query):
        """
        Runs the retriever engine with the given query and returns the relevant context string.
        Parameters:
        query : str
        The query string should encompass the essence of the documents that need to be retrieved, enter
        only the content, and only ONE source. DO NOT try to retrieve multiple articles at once.
        Returns:
        context: str
        The context string extracted from the retrieved documents.
        """
        retrieved_nodes = self.retriever.retrieve(query)
        context = getContextString(retrieved_nodes)
        return context


class AskHuman(Tool):
    """
    A tool that prompts a human for assistance in answering a query.

    Methods:
    run(query):
    Prompts the user with a query to obtain human assistance.
    """

    def run(self, query):
        """
        Prompts the human for help and awaits their input. Use this when the retrieved information is
        not useful or whenever you need human assistance for further directions. DO NOT ask the human to analyse
        the information or for the final answer. This tool is onl intended to get directions from the human

        Parameters:
        query : str
        The query string that encapsulates the information or question needing a human response.

        Returns:
        response : str
        The response provided by the human.
        """
        return input(
            colored(f"You have been summoned by the agent to help with the query: {query}\nAnswer it the best you can so it helps the agent: ", 'cyan', attrs=['bold'])) + " Do not irritate me again by asking for help"


class Finish(Tool):
    """
    A tool to return the final answer or result.

    Methods:
    run(final_answer):
    Returns the final answer provided to it.
    """

    def run(self, final_answer):
        """
        Returns the final answer provided to it.

        Parameters:
        final_answer : str
        The final answer or result that needs to be returned.
        Your final answer should always be either yes, no, before, after or a named entity.
        **DO NOT ANSWER IN SENTENCE**

        Returns:
        final_answer : str
        The same final answer or result.
        """
        return final_answer


