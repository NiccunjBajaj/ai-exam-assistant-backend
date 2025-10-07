from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union

model = SentenceTransformer("BAAI/bge-small-en")

def _get_embedding(text:str) -> str:
    """
    Generate embeddings for a single text.
    """
    if not text.strip():
        return [0.0]*384 # Return zero vector if input is empty
    return model.encode(text,normalize_embeddings=True).tolist()

def _get_embeddings(texts:List[str]) -> List[List[float]]:
    """
    Generate emneddings for a list of texts
    """
    return model.encode(texts,normalize_embeddings=True).tolist()