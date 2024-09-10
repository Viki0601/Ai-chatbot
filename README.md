AI-Insurance Chatbot
Project Vision
The AI-Insurance Chatbot is designed to deliver high-performance and cost-effective solutions for the life-insurance industry. Leveraging OpenAI's API and ThirdAI's NeuralDB, this chatbot efficiently answers user queries by referencing life-insurance policy documents. The project aims to enhance user engagement while maintaining low operational costs.

Main Objectives
Low-Cost Operations: By integrating ThirdAI's NeuralDB, the chatbot processes large datasets efficiently, ensuring minimal latency and computational cost.
High Performance: Using OpenAI's GPT-3.5-turbo model, the chatbot delivers accurate and specific answers to user inquiries, based on detailed policy documents.
Seamless User Experience: The chatbot provides a friendly, conversational interface with a focus on clarity and helpfulness, making it easy for users to understand complex insurance plans.
Key Technologies
Streamlit: For building an interactive and user-friendly interface.
ThirdAI NeuralDB: For document search and query optimization.
OpenAI API: For natural language understanding and response generation.
PDF Document Handling: The chatbot references a wide array of policy documents to generate accurate and detailed responses.
How It Works
Document Ingestion: All life insurance policy documents are imported and indexed using ThirdAI's NeuralDB for fast and relevant document search.
Query Processing: When users input queries, the chatbot fetches relevant sections of policy documents and generates detailed answers using GPT-3.5.
Real-time Responses: The chatbot answers user queries on the fly, ensuring that each response references accurate policy information.
Usage
To run the chatbot:

Clone the repository.
Set your OpenAI API key and ThirdAI license key in the environment or config file.
Install the necessary dependencies and launch the Streamlit app.


#Run the code in streamlit
streamlit run app.py
