from langchain_community.document_loaders import DirectoryLoader
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.vectorstores.utils import filter_complex_metadata

llm = ChatGroq(
	model="llama-3.1-70b-versatile",
	temperature=0.3,
	max_tokens=1024
)

embeddings = HuggingFaceEmbeddings(
	model_name="sentence-transformers/all-MiniLM-L6-v2"
)

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

vectorstore = Chroma.from_documents(
	documents=filter_complex_metadata(splits),
	embedding=embeddings,
	persist_directory="./chroma_db"
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

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
	sys_msg = SystemMessage(content="""You are a helpful assistant with access to the user's documents.
		You MUST use the 'retrieve' tool when the user asks about information that might be in their documents.
		Always call the tool in the correct JSON format - never use <function> tags.
		If the question is general or you don't need documents, answer directly without tools."""
	)
	messages = [sys_msg] + state["messages"]
	response = llm_with_tool.invoke(messages)
	return {"messages": [response]}

workflow = StateGraph(AgentState)

workflow.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "chatbot")
workflow.add_conditional_edges("chatbot", tools_condition)
workflow.add_edge("tools", "chatbot")

memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)
