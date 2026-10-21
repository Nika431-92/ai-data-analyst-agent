
from app.rag import retrieve_documents

question = "What counts as delivered revenue?"

print(f"\nQuestion: {question}\n")

try:
    results = retrieve_documents(question, top_k=3)

    if not results:
        print("No relevant documents found.")
    else:
        for index, result in enumerate(results, start=1):
            print(f"Result {index}")
            print(f"Source: {result['source']}")
            print(f"Relevance: {result['score']:.3f}")
            print(f"Content: {result['text']}\n")

except Exception as error:
    print(f"RAG test failed: {error}")
