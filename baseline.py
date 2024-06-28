import os.path
import pprint
from typing import List, Dict
from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import LangchainNodeParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from llama_index.core.retrievers import VectorIndexRetriever
from utils import load_data
from utils import loadllm, loadEmbeddingModel, nodeExtractor, getContextString
from vectorstore import VectorStore
import json
from tqdm import tqdm
from prompts import baseline_prompt


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


with open('data/MultiHopRAG.json', 'r') as file:
    query_data = json.load(file)[:50]

retriever = VectorIndexRetriever(index=index, similarity_top_k=3, embedding_model=embed_model, verbose=True)
llm = loadllm("Groq")
metalist = []

for stuff in tqdm(query_data):
    query = stuff['query']
    retrieved_nodes = retriever.retrieve(query)
    nodes = nodeExtractor(retrieved_nodes)
    context = getContextString(retrieved_nodes)
    response = str(llm.complete(baseline_prompt.DEFAULT_PROMPT.format(query=query, context=context)))
    save = {}
    save['query'] = stuff['query']
    save['answer'] = stuff['answer']
    save['generated_answer'] = response
    save['question_type'] = stuff['question_type']
    save['retrieval_list'] = nodes
    save['gold_list'] = stuff['evidence_list']
    metalist.append(save)


if not os.path.exists("output/"):
    os.makedirs("output/")

save_file = "output/vanilla_rag.json"
with open(save_file, 'w') as json_file:
    json.dump(metalist, json_file)

