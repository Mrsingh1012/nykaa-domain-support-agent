from src.semantic_rag import search_knowledge


def main():
    questions = [
        "What is your return policy?",
        "How can I get a refund?",
        "How long does delivery take?",
    ]

    for question in questions:
        print(f"\nQUESTION: {question}")

        try:
            results = search_knowledge(question, top_k=3)

            if not results:
                print("No relevant documents found.")
                continue

            for result in results:
                print(
                    f"Source: {result['source']} | "
                    f"Distance: {result['distance']}"
                )

        except Exception as exc:
            print(f"Search failed: {exc}")


if __name__ == "__main__":
    main()