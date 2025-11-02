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

## Running the system
0. Add required files to Files/
1. Start ollama server and set generation_llm.model in config.py with model
1. Run "uvicorn api.main:app --reload" to start the server on terminal
2. Open "http://127.0.0.1:8000/docs" on browser
3. Use ingest/ endpoint to ingest files
4. Use query/ endpoint to ask query. Invoke endpoint by sending payload with "query" as key and question (string) as value
5. Ctrl+C for closing the server session