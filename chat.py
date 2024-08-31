import streamlit as st
from thirdai import licensing, neural_db as ndb
from openai import OpenAI
import nltk
import random
import os
import base64

# Download NLTK punkt
nltk.download("punkt")

# Activate ThirdAI licensing
if "THIRDAI_KEY" in os.environ:
    licensing.activate(os.environ["THIRDAI_KEY"])
else:
    licensing.activate("040B5B-584193-865E93-356F4A-5CF05F-V3")  

# Set OpenAI API key
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = "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"

openai_client = OpenAI()

# Define functions
def get_references(query1):
    search_results = db.search(query1, top_k=1)
    references = []
    for result in search_results:
        references.append(result.text)
    return references

def get_answer(query1, references):
    return generate_answers(
        query1=query1,
        references=references,
    )

def generate_answers(query1, references):
    context = "\n\n".join(references[:3])

    prompt = (
        f"Here's some information that might help. Can you answer this question in a simple and friendly way?\n\n"
        f"Question: {query1}\n\n"
        f"Information: {context}"
    )

    messages = [{"role": "user", "content": prompt}]

    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages, temperature=0.7
    )
    return response.choices[0].message.content

def generate_queries_chatgpt(query1):
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates multiple search queries based on a single input query."},
            {"role": "user", "content": f"Generate multiple search queries related to: {query1}"},
            {"role": "user", "content": "OUTPUT (5 queries):"}
        ]
    )

    # Access the content correctly
    generated_queries = response.choices[0].message.content.strip().split("\n")
    return generated_queries

def vector_search(query, pdf_files):
    available_docs = list(pdf_files.keys())
    random.shuffle(available_docs)
    selected_docs = available_docs[:random.randint(2, 6)]
    scores = {doc: round(random.uniform(0.7, 0.9), 2) for doc in selected_docs}
    return {doc: score for doc, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)}

def reciprocal_rank_fusion(search_results_dict, k=60):
    fused_scores = {}
    for query, doc_scores in search_results_dict.items():
        for rank, (doc, score) in enumerate(sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)):
            if doc not in fused_scores:
                fused_scores[doc] = 0
            fused_scores[doc] += 1 / (rank + k)

    return {doc: score for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)}
def generate_output(reranked_results, queries):
    return f"Final output based on {queries} and reranked documents: {list(reranked_results.keys())}"




# PDF files and NeuralDB setup
pdf_files = {
    "doc1": "cash-back-plan-brochuree.pdf",
    "doc2" :"indiafirst-life-saral-bachat-bima-plan-brochure.pdf",
    "doc3" : "indiafirst-life-smart-pay-plan-brochure.pdf"
}
db = ndb.NeuralDB()
insertable_docs = []

for file in pdf_files:
    pdf_doc = ndb.PDF(pdf_files[file])
    insertable_docs.append(pdf_doc)
source_ids = db.insert(insertable_docs, train=True)


def main():
    # Load external CSS
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    def get_image_base64(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')

    image_base64 = get_image_base64('logo.JPG')
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
        </style>
        """, unsafe_allow_html=True)
    st.markdown("<div class='centered-title'>AI-Insurance Chatbot</div>", unsafe_allow_html=True)

    # Initialize session state for storing chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

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

        # Friendly greeting response
        if user_input.lower() in ["hi", "hello", "hii", "hey"]:
            bot_response = "Hello! How can I assist you today?"
        else:
            # Generate response
            generated_queries = generate_queries_chatgpt(user_input)
            all_results = {}
            for query in generated_queries:
                search_results = vector_search(query, pdf_files)
                all_results[query] = search_results
            
            reranked_results = reciprocal_rank_fusion(all_results)
            references = get_references(user_input)
            
            if references:
                answer = get_answer(user_input, references)
                final_output = generate_output(reranked_results, generated_queries)
                bot_response = f"Here's what I found: {answer}"
            else:
                # Generate a relevant response when no references are found
                bot_response = "It looks like I don't have specific references for that question, but I'm here to help! Could you ask it another way, or do you have another question in mind?"

        # Add bot response to chat history and display it immediately
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.markdown(f"<div class='assistant-bubble'>{bot_response}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
