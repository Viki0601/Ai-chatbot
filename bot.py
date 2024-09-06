import streamlit as st
from thirdai import licensing, neural_db as ndb
from openai import OpenAI
import os
import base64
import config
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnableWithMessageHistory
# Activate ThirdAI licensing
if "THIRDAI_KEY" in os.environ:
    licensing.activate(os.environ["THIRDAI_KEY"])
else:
    licensing.activate(config.THIRDAI_KEY)

# Set OpenAI API key
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY

openai_client = OpenAI()

pdf_files = {
    "doc1": "cash-back-plan-brochuree.pdf"# Add your PDF file paths here
}

db = ndb.NeuralDB()
insertable_docs = [ndb.PDF(pdf_files[file]) for file in pdf_files]
source_ids = db.insert(insertable_docs, train=False)

# Define functions
def get_references(query):
    search_results = db.search(query, top_k=3)
    return [result.text for result in search_results]

def generate_queries_chatgpt(query):
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates multiple search queries based on a single input query."},
            {"role": "user", "content": f"Generate multiple search queries related to: {query}"},
            {"role": "user", "content": "OUTPUT (5 queries):"}
        ]
    )
    return response.choices[0].message["content"].strip().split("\n")

def generate_answers(query, references):
    context = "\n\n".join(references[:3])
    prompt = (
        f"Please carefully read all the documents provided below and answer the user's question with specific details directly from the document. "
        f"Ensure the answer is accurate, complete, and directly references the relevant sections of the policy, including tables and structured data.\n\n"
        f"User Question: {query}\n\n"
        f"Documents:\n{context}\n\n"
        f"Based on the information in the documents, provide a correct and specific answer to the user's question. "
        f"Include the policy name and any relevant details or conditions mentioned in the policy. "
        f"Focus on the data presented in the table, paying close attention to numeric values, labels, and any relevant units. "
        f"Interpret the numeric values accurately and include them in your response. Provide a clear and precise answer to the user’s question based on the table and any other relevant information from the document. "
        f"If multiple tables are relevant, synthesize information from all of them to form a complete answer."
    )
    return prompt

# Initialize ConversationBufferMemory
memory = ConversationBufferMemory()

def create_runnable():
    def runnable_with_history(messages, prompt):
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages + [{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message["content"]
    
    def get_session_history():
        return memory.load_memory_variables({}).get("chat_history", "")
    
    return RunnableWithMessageHistory(
        runnable=runnable_with_history,
        get_session_history=get_session_history
    )

def main():
    # Load external CSS
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    def get_image_base64(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')

    image_base64 = get_image_base64('logo.jpg')
    st.markdown(f'<img src="data:image/png;base64,{image_base64}" class="logo">', unsafe_allow_html=True)
    st.markdown("""
        <style>
        .centered-title {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
        }
        .logo {
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 150px;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 10px;
            padding: 10px;
        }
        .user-bubble {
            background-color: #e1f5fe;
            padding: 10px;
            border-radius: 10px;
            align-self: flex-start;
        }
        .assistant-bubble {
            background-color: #e8f5e9;
            padding: 10px;
            border-radius: 10px;
            align-self: flex-end;
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("<div class='centered-title'>AI-Insurance Chatbot</div>", unsafe_allow_html=True)
    st.markdown("<div class='centered-title1'>Hi there! I'm your friendly assistant</div>", unsafe_allow_html=True)
    st.markdown("<div class='centered-title1'>Whether you need help with something, I'm here to assist.</div>", unsafe_allow_html=True)
    st.markdown("<div class='centered-title1'>If you have a language preference, let me know?</div>", unsafe_allow_html=True)
    st.markdown("<div class='centered-title1'>How Can I Help You Today?</div>", unsafe_allow_html=True)

    # Initialize session state for storing chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Create runnable with message history
    runnable = create_runnable()

    # Display chat history
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"<div class='user-bubble'>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='assistant-bubble'>{message['content']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # User input
    if user_input := st.chat_input("Ask any question", key="user_input"):
        # Add user message to chat history and display it immediately
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.markdown(f"<div class='user-bubble'>{user_input}</div>", unsafe_allow_html=True)

        # Generate response using RunnableWithMessageHistory
        prompt = generate_answers(user_input, get_references(user_input))
        message_history = [{"role": "user", "content": user_input}]
        response = runnable.run(message_history, prompt)
        bot_response = response.strip()

        # Add bot response to chat history and display it immediately
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.markdown(f"<div class='assistant-bubble'>{bot_response}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
