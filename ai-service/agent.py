from langchain_community.document_loaders import DirectoryLoader
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.messages import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import ToolNode, tools_condition

loader = DirectoryLoader(
	path="data/",
	loader_cls=UnstructuredLoader,
	loader_kwargs={
		"strategy": "auto",
		"partition_via_api": False
	},
	glob="**/*.*",
	recursive=True,
	show_progress=True,
	silent_errors=True,
)

documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
	chunk_size=1000,
	chunk_overlap=200
)

splits = text_splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(
	model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = Chroma.from_documents(
	documents=splits,
	embedding=embeddings,
	persist_directory="./chroma_db"
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

llm = ChatGroq(
	model="llama-3.3-70b-versatile",
	temperature=0.3,
	max_tokens=1024
)

@tool
def retrieve(query: str) -> str:
	"""Retrieve relevant information from user's documents."""
	docs = retriever.invoke(query)
	return "\n\n".join([doc.page_content for doc in docs])

tools = [retrieve]

class AgentState(TypedDict):
	messages: Annotated[list, add_messages]

llm_with_tool = llm.bind_tools(tools)

def chatbot(state: AgentState):
	response = llm_with_tool.invoke(state['messages'])
	return { "messages": [response] }

workflow = StateGraph(AgentState)

workflow.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "chatbot")
workflow.add_conditional_edges("chatbot", tools_condition)
workflow.add_edge("tools", "chatbot")

memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)
