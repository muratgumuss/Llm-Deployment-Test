
from urllib import response
from openai import api_key
import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.utilities import ArxivAPIWrapper,WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun,WikipediaQueryRun,DuckDuckGoSearchRun
from langchain.agents import initialize_agent,AgentType
from langchain.callbacks import StreamlitCallbackHandler
import os

# Arxiv and Wikipedia Tools

arxiv_wrapper = ArxivAPIWrapper(top_k_results=1,doc_content_chars_max=200)
arxiv = ArxivQueryRun(api_wrapper=arxiv_wrapper)

wiki_wrapper = WikipediaAPIWrapper(top_k_results=1,doc_content_chars_max=200)
wiki = WikipediaQueryRun(api_wrapper=wiki_wrapper)

arxiv.name = "Arxiv"
wiki.name = "Wikipedia"

search = DuckDuckGoSearchRun(name="Search")

st.title("Langchain chat with search")

# Sidebar for settings
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter your Groq Api Key:",type="password")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role":"assistant",
                                     "content":"Hi,I'm a chatbot who can search the web."
                                     " How can i help you"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])
prompt = st.chat_input("Ask me anything...")

if prompt and api_key:
    st.session_state.messages.append({"role":"user","content":prompt})   
    st.chat_message("user").write(prompt)

    llm = ChatGroq(groq_api_key = api_key, model_name = "llama3-8b-8192",streaming=True)
    tools = [search,arxiv,wiki]

    search_agent = initialize_agent(tools,llm,agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,handle_parsing_errors=True)

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(),expand_new_thoughts=False)
        history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
        response = search_agent.run(history, callbacks=[st_cb])
        
        st.session_state.messages.append({"role":"assistant","content":response})
        st.write(response)