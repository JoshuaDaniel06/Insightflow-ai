import os
import pickle

import faiss
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from google import genai


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

KNOWLEDGE_FILE = "data/knowledge.txt"

INDEX_FILE = "vector_store/customer_policy.index"

CHUNKS_FILE = "vector_store/chunks.pkl"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# ============================================================
# CHECK GEMINI API KEY
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


if not GEMINI_API_KEY:

    print(
        "ERROR: GEMINI_API_KEY not found in .env file."
    )

    exit()


# ============================================================
# INITIALIZE GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)

print("Embedding model loaded.")


# ============================================================
# LOAD FAISS INDEX
# ============================================================

if not os.path.exists(INDEX_FILE):

    print(
        f"ERROR: FAISS index not found: "
        f"{INDEX_FILE}"
    )

    print(
        "Run the vector-store creation step first."
    )

    exit()


index = faiss.read_index(
    INDEX_FILE
)


# ============================================================
# LOAD CHUNKS
# ============================================================

if not os.path.exists(CHUNKS_FILE):

    print(
        f"ERROR: Chunks file not found: "
        f"{CHUNKS_FILE}"
    )

    exit()


with open(
    CHUNKS_FILE,
    "rb"
) as file:

    chunks = pickle.load(file)


print(
    f"Vector store loaded: "
    f"{index.ntotal} vectors"
)

print(
    f"Knowledge chunks loaded: "
    f"{len(chunks)}"
)


# ============================================================
# RETRIEVE RELEVANT CHUNKS
# ============================================================

def retrieve_documents(
    question,
    top_k=3
):

    # Convert question into embedding
    question_embedding = embedding_model.encode(
        [question],
        convert_to_numpy=True
    )

    # Search FAISS
    distances, indices = index.search(
        question_embedding,
        top_k
    )

    retrieved_chunks = []

    for index_position in indices[0]:

        if index_position == -1:
            continue

        retrieved_chunks.append(
            chunks[index_position]
        )

    return retrieved_chunks


# ============================================================
# GENERATE ANSWER USING GEMINI
# ============================================================

def generate_answer(
    question,
    retrieved_chunks
):

    # Combine retrieved chunks
    context = "\n\n".join(
        retrieved_chunks
    )

    prompt = f"""
You are an AI Customer Support Assistant.

Answer the user's question using ONLY the
information provided in the CONTEXT below.

If the answer cannot be found in the context,
say:

"I don't have enough information in the
available customer policy documents."

Do not invent policies or facts.

CONTEXT:
{context}

USER QUESTION:
{question}

Provide a clear and concise answer.
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    return interaction.output_text


# ============================================================
# ASK QUESTION
# ============================================================

def ask_question(question):

    print("\n" + "=" * 60)

    print("USER QUESTION")

    print(question)

    print("=" * 60)


    # --------------------------------------------------------
    # RETRIEVAL
    # --------------------------------------------------------

    retrieved_chunks = retrieve_documents(
        question,
        top_k=3
    )


    print("\nRETRIEVED KNOWLEDGE")

    print("-" * 60)


    for number, chunk in enumerate(
        retrieved_chunks,
        start=1
    ):

        print(
            f"\nChunk {number}:"
        )

        print(chunk)


    # --------------------------------------------------------
    # GENERATION
    # --------------------------------------------------------

    print("\n" + "-" * 60)

    print("GENERATING ANSWER...")


    answer = generate_answer(
        question,
        retrieved_chunks
    )


    # --------------------------------------------------------
    # DISPLAY ANSWER
    # --------------------------------------------------------

    print("\nAI ANSWER")

    print("-" * 60)

    print(answer)

    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 60)
    print("AI CUSTOMER INTELLIGENCE - RAG ASSISTANT")
    print("=" * 60)

    print(
        "\nRAG system ready."
    )

    print(
        "Type 'exit' to stop."
    )


    while True:

        question = input(
            "\nAsk a customer policy question: "
        )


        if question.lower().strip() == "exit":

            print(
                "\nRAG assistant stopped."
            )

            break


        if not question.strip():

            print(
                "Please enter a question."
            )

            continue


        try:

            ask_question(
                question
            )

        except Exception as error:

            print(
                "\nERROR:"
            )

            print(error)