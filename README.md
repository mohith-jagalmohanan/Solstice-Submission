# Solstice-Submission

## Optional
1. conda create -n "Solstice"
2. conda activate "Solstice"

## Install dependencies
1. pip install -r requirements.txt

If the above step fails, follow the steps given below:

1. python3 -m ensure pip --upgrade
2. pip3 install --upgrade pymupdf
3. pip3 install --upgrade --quiet  langchain langchain-core langchain-community langchain-text-splitters langchain-milvus milvus-lite langchain-openai langchain-classic langchain-ollama bs4
4. pip3 install --upgrade pip
5. pip3 install torch torchvision torchaudio sentence-transformers
6. pip3 install -U langchain-huggingface

## Setting up the LLM inference server
1. Install ollama using: curl -fsSL https://ollama.com/install.sh | sh
2. (Optional) Run: "ollama serve" to start service
3. Pull the required model using: ollama pull <model-name>. For small model, choose "gemma3:1b"
4. "ollama list" to verify LLM has been downloaded

## Hosting the API (Server start)
0. Add required files to Files/
1. Start ollama server and set generation_llm.model in config.py with model
2. Run "uvicorn api.main:app --reload" to start the server on terminal

## Client code
1. Run: "python client.py" and follow instructions

NOTE: To test the APIs through browser, follow the steps below:
1. Open "http://127.0.0.1:8000/docs" on browser
2. Use ingest/ endpoint to ingest files
3. Use query/ endpoint to ask query. Invoke endpoint by sending payload with "query" as key and question (string) as value
4. Ctrl+C for closing the server session
5. Some queries to try out:
    - When was Gandhiji assassinated
    - Who was Elon Musk's father?
    - Where was Einstein born?

## Improvements to be made

### API-level changes:
1. Have a file upload API for document ingestion. This is more useful from a user experience point of view

### Automated Testing:
Ideally I would want to test out the system in the following manner:
1. Given a set of documents chunked and persisted (ingested), annotate a relevance set (of chunks) for each query. Since I do not want to miss out on unwanted information relevant to the query, I would measure Recall@k and ideally optimize for this
2. For the final generation of response for the given query, I would use a BLEU score/ROUGE score (ideally BLEU to focus on precision of generation)

### Chat feature:
1. Current system does not allow chat functionality as previous context is lost.
2. Storing chat functionality might invoke new challenges like:
    - Having to summarize older context information to save context window
    - Having to rephrase current query with information from previous chats and previous retrieval responses
    - Ideally an agentic RAG system is good to handle such interactions, if enough context length is available

### Using better LLM:
1. Currently I am using one of the smallest opensource LLMs available (Gemma3 1Billion model). This was a conscious choice for this project because:
    - On working with the Gemma3 1 billion model, I realized that this model has very less "knowledge". For example if I ask (without relevant context) about who Elon Musk's father is, it would hallucinate. If my system is giving the right ansswer, it is proof that the correct context has been picked
    - The model inference is very fast even on a laptop

However going forward, it is better to use a bigger model