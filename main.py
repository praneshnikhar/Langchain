

import os
from constants import openai_key
from langchain.llms import OpenAI
import streamlit as st


# Set environment variable (preferred)
os.environ["OPENAI_API_KEY"] = openai_key

st.title('Langchain demo with OpenAI API')
input_text = st.text_input("Search the topic you want")

# Initialize LLM without explicit key since env var is set
llm = OpenAI(temperature=0.8)

if input_text:
    response = llm(input_text)
    st.write(response)
