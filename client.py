import requests

BASE_URL = "http://127.0.0.1:8000"
INGEST_URL = f"{BASE_URL}/ingest"
QUERY_URL = f"{BASE_URL}/query"

show_sources = True

while True:
    print("1. Ingest Documents")
    print("2. Query the RAG System")
    print("3. Exit")
    choice = int(input("Select an option (1-3): ").strip())
    match choice:
        case 1:
            r = requests.post(INGEST_URL)
            if r.status_code == 200:
                print("Ingestion triggered successfully.")
        case 2: 
            query_text = input("QUERY: ").strip()
            payload = {"query": query_text}
            r = requests.post(QUERY_URL, json=payload)
            if r.status_code == 200:
                data = r.json()
                answer = data.get("answer", "No answer found.")
                sources = data.get("sources", [])

                print(f"\nANSWER: {answer}\n")
                if show_sources:
                    print("\nSOURCES:")
                    for i, source in enumerate(sources):
                        print(f"{i+1}) ")
                        print(f"\033[32m{source}\033[0m")
                        print("-----")
            else:
                print(f"Error: Received status code {r.status_code}")
        case 3:
            print("Exiting...")
            break
        case _:
            print("Invalid choice. Please select 1, 2, or 3.")
            continue