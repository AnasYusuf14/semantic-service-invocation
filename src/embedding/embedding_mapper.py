import csv
import sys
from pathlib import Path
from collections import defaultdict

import numpy as np
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATASET_FILE = BASE_DIR / "dataset" / "service_dataset.csv"

RULE_BASED_DIR = BASE_DIR / "src" / "rule_based"
sys.path.append(str(RULE_BASED_DIR))

from rule_based_mapper import extract_parameters


MODEL_NAME = "all-MiniLM-L6-v2"


class EmbeddingMapper:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.dataset_rows = self.load_dataset()

        self.intent_examples = self.group_examples_by_intent()
        self.intent_metadata = self.build_intent_metadata()
        self.intent_embeddings = self.build_intent_embeddings()

    def load_dataset(self):
        with open(DATASET_FILE, mode="r", encoding="utf-8") as file:
            return list(csv.DictReader(file))

    def group_examples_by_intent(self):
        grouped = defaultdict(list)

        for row in self.dataset_rows:
            grouped[row["intent"]].append(row["query"])

        return grouped

    def build_intent_metadata(self):
        metadata = {}

        for row in self.dataset_rows:
            intent = row["intent"]

            if intent not in metadata:
                metadata[intent] = {
                    "domain": row["domain"],
                    "intent": row["intent"],
                    "endpoint": row["endpoint"],
                    "ontology_concept": row["ontology_concept"]
                }

        return metadata

    def build_intent_embeddings(self):
        embeddings = {}

        for intent, examples in self.intent_examples.items():
            embeddings[intent] = self.model.encode(
                examples,
                normalize_embeddings=True
            )

        return embeddings

    def predict(self, query: str) -> dict:
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        )[0]

        best_intent = None
        best_score = -1
        best_matched_query = None

        for intent, example_embeddings in self.intent_embeddings.items():
            similarities = np.dot(example_embeddings, query_embedding)

            intent_best_index = int(np.argmax(similarities))
            intent_best_score = float(similarities[intent_best_index])

            if intent_best_score > best_score:
                best_score = intent_best_score
                best_intent = intent
                best_matched_query = self.intent_examples[intent][intent_best_index]

        metadata = self.intent_metadata[best_intent]

        return {
            "domain": metadata["domain"],
            "intent": metadata["intent"],
            "endpoint": metadata["endpoint"],
            "parameters": extract_parameters(query, best_intent),
            "ontology_concept": metadata["ontology_concept"],
            "similarity_score": best_score,
            "matched_query": best_matched_query
        }


_mapper = None


def embedding_predict(query: str) -> dict:
    global _mapper

    if _mapper is None:
        _mapper = EmbeddingMapper()

    return _mapper.predict(query)


if __name__ == "__main__":
    test_queries = [
        "Should I carry an umbrella in Istanbul tomorrow?",
        "I need to get from Istanbul to Dubai tomorrow.",
        "What do customers say about P2?",
        "Where is my package O5 now?",
        "Put a call with Ali tomorrow at 2 PM."
    ]

    for query in test_queries:
        print(query)
        print(embedding_predict(query))
        print("-" * 60)