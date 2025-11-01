import requests
import argparse
import sys
import json

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8000"
INGEST_URL = f"{BASE_URL}/ingest"
QUERY_URL = f"{BASE_URL}/query"
# ---------------------

def styled_print(text, color_code):
    """Prints text in a given ANSI color."""
    print(f"\033[{color_code}m{text}\033[0m")

def trigger_ingest():
    """Sends a POST request to the /ingest endpoint."""
    styled_print("Attempting to trigger document ingestion...", "33") # Yellow
    styled_print(f"Sending request to: {INGEST_URL}", "34") # Blue
    
    try:
        response = requests.post(INGEST_URL, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            styled_print("\n✅ Success!", "32") # Green
            styled_print(f"   Message: {data.get('message')}", "32")
            styled_print(f"   Files to be processed: {data.get('files_processed')}", "32")
        elif response.status_code == 404:
            styled_print(f"\n❌ Error: {response.status_code}", "31") # Red
            styled_print(f"   Detail: {response.json().get('detail')}", "31")
            styled_print("   Hint: Make sure the 'Files' directory exists.", "33")
        else:
            styled_print(f"\n❌ Unexpected Error: {response.status_code}", "31")
            styled_print(f"   Response: {response.text}", "31")
            
    except requests.exceptions.ConnectionError:
        styled_print("\n❌ Connection Error", "31")
        styled_print(f"   Could not connect to {BASE_URL}.", "31")
        styled_print("   Hint: Is the Uvicorn server running?", "33")
    except Exception as e:
        styled_print(f"\n❌ An unknown error occurred: {e}", "31")

def perform_query(query_text: str):
    """Sends a POST request to the /query endpoint with the user's question."""
    styled_print(f"Querying API with: '{query_text}'", "34") # Blue
    
    payload = {"query": query_text}
    
    try:
        response = requests.post(QUERY_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            styled_print("\n✅ Answer Received:", "32") # Green
            
            # Print the answer with word-wrapping
            import textwrap
            answer = data.get('answer', 'No answer provided.')
            print("\n" + textwrap.fill(answer, width=80))
            
            # Print sources
            sources = data.get('sources', [])
            if sources:
                styled_print("\n--- Sources ---", "35") # Magenta
                for i, source in enumerate(sources):
                    filename = source.get('source', 'Unknown').split('/')[-1]
                    page = source.get('page_number', 'N/A')
                    print(f"  [{i+1}] File: {filename}, Page: {page}")
            else:
                styled_print("\n(No sources found for this answer)", "90") # Gray
                
        else:
            styled_print(f"\n❌ Unexpected Error: {response.status_code}", "31")
            styled_print(f"   Response: {response.text}", "31")

    except requests.exceptions.ConnectionError:
        styled_print("\n❌ Connection Error", "31")
        styled_print(f"   Could not connect to {BASE_URL}.", "31")
        styled_print("   Hint: Is the Uvicorn server running?", "33")
    except Exception as e:
        styled_print(f"\n❌ An unknown error occurred: {e}", "31")

def main():
    """Main function to parse arguments and call the correct API function."""
    parser = argparse.ArgumentParser(
        description="CLI client for the RAG Q&A API."
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")
    
    # --- Ingest Command ---
    parser_ingest = subparsers.add_parser(
        "ingest", 
        help="Trigger ingestion of documents from the 'Files' directory."
    )
    parser_ingest.set_defaults(func=trigger_ingest)
    
    # --- Query Command ---
    parser_query = subparsers.add_parser(
        "query", 
        help="Ask a question to the RAG system."
    )
    parser_query.add_argument(
        "text", 
        type=str, 
        help="The question you want to ask."
    )
    parser_query.set_defaults(func=perform_query)
    
    # If no arguments are given, print help
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()
    
    # Call the appropriate function based on the command
    if args.command == "ingest":
        args.func()
    elif args.command == "query":
        args.func(args.text)

if __name__ == "__main__":
    main()
