import os
import json 
import pandas as pd
import traceback
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file,get_table_data
import streamlit as st
from langchain.callbacks import get_openai_callback
from src.mcqgenerator.mcqgenerator import generate_evaluate_chain
from src.mcqgenerator.logger import logging


with open('A:\GEN AI\auto_mcq_genrate_langchain\Response.json','r') as file:
    RESPONSE_JSON = json.load(file)

st.title("MCQ creatir application")


with st.form("user_input"):
    uploaded_file = st.file_uploader("upload a pdf or txt file")
    mcq_count =  st.number_input("No. of MCQs",min_value = 3 , max_value=50)


    subject = st.text_input("insert subject",max_chars=20)

    tone = st.text_input("complexity level of question" ,max_chars=20 , placeholder="Simple")

    button = st.form_submit_button("create MCQs")
    
    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("loading..."):
            try:
                text=read_file(uploaded_file)
                #count token & cost of api call
                with get_openai_callback() as cb: 
                    response = generate_evaluate_chain(
                        {
                            "text": text ,
                            "number": mcq_count,
                            "subject":subject,
                            "tone": tone ,
                            "response_json": json.dumps(RESPONSE_JSON)
                        }  
                    )
                    # st.write(response)
            except Exception as e: 
                traceback.print_exception(type(e),e,e.__traceback__)
                st.error("Error")

            else:
                print(f'total Tokens:{cb.total_tokens}')
                print(f'Prompt Tokens:{cb.prompt_tokens}')
                print(f'Completion Tokens:{cb.completion_tokens}')
                print(f'Total cost:{cb.total_cost}')

                if isinstance(response,dict):
                    #quiz data-> extract ->  response
                    quiz = response.get("quiz", None)
                    if quiz is not None:
                        table_data = get_table_data(quiz)
                        if table_data is not None:
                            df = pd.DataFrame(table_data)
                            df.index = df.index+1
                            st.table(df)
                            #display the review in a text box as well 
                            st.text_area(label="Review",value=response["review"])

                        else:
                            st.error("Error in the table data")
                
                else:
                    st.write(response)
