import chromadb
import dlso

ep = dlso.Endpoint(
    model='text-embedding-3-small',
    key='sk-fxZcN6GZbKn5hk6BjgwypFevWl5oO2rF6xNMA3YwVmZOR3WN',
    endpoint='http://yunwu.ai/v1'
)


db = chromadb.PersistentClient(path="./chroma_db")

ct = db.get_or_create_collection(name="test_collection")

def add_content(content):
    embedding = ep.embed(content)
    ct.upsert(
        ids=dlso.safecode(4),
        documents=content,
        embeddings=[embedding]
    )

def search_content(query, n_results=5):
    embedding = ep.embed(query)
    results = ct.query(
        query_embeddings=embedding,
        n_results=n_results
    )
    return results
