
import os
from constants import openai_key
from langchain.llms import OpenAI
import streamlit as st
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from langchain.memory import CoversationBufferMemory
# Set environment variable (preferred)
os.environ["OPENAI_API_KEY"] = openai_key

st.title('celebrity search results')
input_text = st.text_input("Search the topic you want")

#prompt templates 
first_input_prompt = PromptTemplate(
    input_variables = ['name'],
    template = "tell me about {name}"
)

llm = OpenAI(temperature=0.8)
chain = LLMChain(llm=llm, prompt = first_input_prompt, verbose = True, output_key ='title', memory = person_memory)

# Initialize LLM without explicit key since env var is set

#2nd prompt templates 
second_input_prompt = PromptTemplate(
    input_variables = ['person'],
    template = "mention five major events happend around that {dob}"
)

chain2 = LLMChain(llm= llm, prompt = second_input_prompt , verbose = True, output_key='dob', memory = 'dob_memory')

third_input_prompt = PromptTemplate(
    input_variables = ['person'],
    template = "when was {person} born"
)
chain3 = LLMChain(llm= llm, prompt = second_input_prompt , verbose = True, output_key='description', memory = descr_memory)

parent_chain = SequentialChain(chains =[chain, chain2],input_variables =['name'],
                               output_variables=['person','dob', 'description']verbose = True)

if input_text:
    #
    
    response = llm(parent_chain({'name': input_text}))
 
    st.write(response)

    with st.expander('Person Name'):
        st.info(person_memory.buffer)
    with st.expander('Major Events'):
        st.info(descr_memory.buffer)
