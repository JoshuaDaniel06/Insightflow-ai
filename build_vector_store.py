import os
import pickle
import faiss

from sentence_transformers import SentenceTransformer


KNOWLEDGE_FILE = "data/knowledge.txt"
VECTOR_STORE_DIR = "vector_store"

INDEX_FILE = os.path.join(
    VECTOR_STORE_DIR,
    "customer_policy.index"
)

CHUNKS_FILE = os.path.join(
    VECTOR_STORE_DIR,
    "chunks.pkl"
)


def load_knowledge():

    with open(
        KNOWLEDGE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        text = file.read()

    return text


def create_chunks(text):

    # Split knowledge into sections
    sections = text.split("\n\n")

    chunks = []

    for section in sections:

        section = section.strip()

        if section:
            chunks.append(section)

    return chunks


def build_vector_store():

    print("\nLoading knowledge...")

    text = load_knowledge()

    chunks = create_chunks(text)

    print(f"Knowledge chunks created: {len(chunks)}")

    print("\nLoading embedding model...")

    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

    print("Embedding model loaded.")

    print("\nCreating embeddings...")

    embeddings = model.encode(
        chunks,
        convert_to_numpy=True
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    os.makedirs(
        VECTOR_STORE_DIR,
        exist_ok=True
    )

    faiss.write_index(
        index,
        INDEX_FILE
    )

    with open(
        CHUNKS_FILE,
        "wb"
    ) as file:

        pickle.dump(
            chunks,
            file
        )

    print("\nVector store created successfully.")

    print(f"Vectors: {index.ntotal}")

    print(f"Index: {INDEX_FILE}")

    print(f"Chunks: {CHUNKS_FILE}")


if __name__ == "__main__":

    build_vector_store()