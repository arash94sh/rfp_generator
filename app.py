import streamlit as st
from datetime import datetime
import json
import os
import re
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from typing import Annotated
import uuid
import pandas as pd
from typing_extensions import TypedDict



#set llm config
os.environ["MISTRAL_API_KEY"] = "ct0DL5yDroEhR0PicB3wCn60TVkjre8Z"
model = ChatMistralAI(model="mistral-large-latest")


# Set page config
st.set_page_config(
    page_title="RFP Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Add custom CSS to change background color
st.markdown("""
    <style>
        .stApp {
            background-color: #EBEBEB;
        }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("RFP Generator Chatbot")
st.markdown("Chat with me to create your Request for Proposal (RFP). I'll guide you through the process! 💬")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
    
if 'responses' not in st.session_state:
    st.session_state.responses = {}
# dict to string function
def dict_to_context(user_info):
    context = "User Information:\n"
    for key, value in user_info.items():
        context += f"{key.capitalize()}: {value}\n"
    return context
#clean markdown function
def clean_markdown(text):
    # Remove Markdown headings (e.g., ####, ###, ##, #)
    text = re.sub(r'^#+ ', '', text, flags=re.MULTILINE)
    
    # Normalize extra newlines (optional, to clean up spacing)
    text = re.sub(r'\n\s*\n', '\n', text).strip()
    
    # Preserve bold (**text**) and bullet points (* Item or - Item)
    return text

# Define questions
QUESTIONS = [
    {
        'key': 'project_description',
        'question': "Hi! I'm here to help you create your RFP. First, could you tell me about your project? What are you looking to accomplish? 🎯"
    },
    
    {
        'key': 'timeline',
        'question': "Thanks for sharing that! When would you like to start this project? You can say something like 'within 3 months' or 'after 60 days' 📅"
    },
    {
        'key': 'company_name',
        'question': "Great! Now, what's your company name? 🏢"
    },
    {
        'key': 'business_type',
        'question': "Could you tell me a bit about what your business does? 💼"
    },
    {
        'key': 'employee_count',
        'question': "Last question! Approximately how many employees are in your organization? 👥"
    }
]

def generate_rfp():
    return f"""
REQUEST FOR PROPOSAL (RFP)

Date: {datetime.now().strftime('%B %d, %Y')}

COMPANY INFORMATION
Company Name: {st.session_state.responses.get('company_name', '')}
Business Type: {st.session_state.responses.get('business_type', '')}
Number of Employees: {st.session_state.responses.get('employee_count', '')}

PROJECT OVERVIEW
{st.session_state.responses.get('project_description', '')}

TIMELINE
Desired Start: {st.session_state.responses.get('timeline', '')}
    """


def generate_rfp_2(prompt):
    msg = model.invoke(prompt)
    return msg.content

    
# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Display current question if not finished
if st.session_state.current_question < len(QUESTIONS):
    current_q = QUESTIONS[st.session_state.current_question]
    with st.chat_message("assistant"):
        st.write(current_q['question'])
    
    # Get user input
    user_response = st.chat_input("Type your response here...")
    
    if user_response:
        # Display user response
        with st.chat_message("user"):
            st.write(user_response)
            
        # Store the response
        st.session_state.responses[current_q['key']] = user_response
        
        # Add to chat history
        st.session_state.messages.append({"role": "assistant", "content": current_q['question']})
        st.session_state.messages.append({"role": "user", "content": user_response})
        
        # Move to next question
        st.session_state.current_question += 1
        st.rerun()









# Show final RFP when all questions are answered
elif st.session_state.current_question == len(QUESTIONS):
    context = dict_to_context(st.session_state.responses)
    print(context)
    with st.chat_message("assistant"):
        st.write("Great! I've gathered all the information. Here's your generated RFP! 🎉")
    rfp_prompt = f"""You are an expert in creating professional Request for Proposals (RFPs). Based on the following user-provided information, generate a comprehensive, polished, and professional RFP document. Use the provided data as the foundation, but creatively expand and enhance the responses to ensure they are complete, detailed, and suitable for a formal RFP. Fill in any gaps with reasonable assumptions that align with the user's input, maintaining a professional tone and structure. The RFP should include sections such as an introduction, project overview, goals and objectives, scope of work, timeline, company background, and submission requirements. Ensure the RFP is engaging, clear, and tailored to attract qualified vendors.



**Instructions**:
1. **Enhance User Responses**: Use the provided data as a starting point. Expand on the project description and goals to make them specific, actionable, and comprehensive. For example, if the user provides a vague project description, infer reasonable details based on the business type and goals.
2. **Incorporate Company Context**: Use the company name, business type, and employee count to craft a detailed company background section. Highlight the company's mission, industry, and scale to provide context for vendors.
3. **Define Scope of Work**: Based on the project description and goals, outline a clear scope of work, including deliverables, key requirements, and any technical or functional specifications that align with the project.
4. **Timeline and Milestones**: Use the provided timeline to create a detailed project schedule with realistic milestones. If the timeline is vague (e.g., "within 3 months"), propose a reasonable start date and key phases.
5. **Professional Structure**: Organize the RFP with the following sections:
   - **Introduction**: Briefly introduce the company and the purpose of the RFP.
   - **Company Background**: Describe the company based on the provided name, business type, and employee count, adding relevant details about its mission and industry.
   - **Project Overview**: Expand on the project description to provide a clear understanding of the project's purpose and scope.
   - **Goals and Objectives**: List specific, measurable goals based on the user's input, adding clarity and detail as needed.
   - **Scope of Work**: Detail the deliverables, requirements, and expectations for the project.
   - **Timeline**: Provide a detailed schedule with milestones based on the user's timeline input.
   - **Submission Requirements**: Specify how vendors should submit proposals, including format, deadline (assume 30 days from the RFP release unless otherwise specified), and contact information.
   - **Evaluation Criteria**: Outline how proposals will be evaluated (e.g., cost, experience, alignment with goals).
6. **Creative Additions**: Add reasonable details to make the RFP robust, such as industry-specific requirements, stakeholder involvement, or potential challenges, while staying true to the user's input.
7. **Tone and Style**: Use a professional, engaging, and concise tone. Avoid jargon unless appropriate for the business type, and ensure the RFP is accessible to a wide range of potential vendors.
8. **Assumptions**: If any information is missing or vague, make logical assumptions based on the business type and project context. For example, a tech company might require software development, while a retail business might need a marketing solution.
9. **Output Format**: Provide the RFP as a well-structured document with clear headings and concise paragraphs. Use bullet points or numbered lists where appropriate for clarity.


.
Here is the user-provided information:
{context}
"""    
    print(rfp_prompt)
    rfp_content = generate_rfp_2(rfp_prompt)
    st.markdown(rfp_content)
    
    # Add a raw text area for copying if needed
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Download as Text",
            rfp_content,
            file_name="rfp_document.txt",
            mime="text/plain"
        )
    with col2:
        st.download_button(
            "Download as JSON",
            json.dumps(st.session_state.responses, indent=2),
            file_name="rfp_data.json",
            mime="application/json"
        )
        
    if st.button("Start Over 🔄"):
        st.session_state.clear()
        st.rerun() 