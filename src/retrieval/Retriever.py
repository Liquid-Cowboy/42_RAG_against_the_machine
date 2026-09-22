import bm25s
from src.data_models import (MinimalSearchResults,
                             UnansweredQuestion,
                             MinimalSource,
                             StudentSearchResults)
from pathlib import Path
import json


class Retriever():
    """Utility class to deal with retrieval events."""
    def __init__(self, index_path: Path, chunks_path: Path) -> None:
        """
        Instantiates the retriever object.

        Parameters:
            -index_path: Path object leading to index folder
            -chunks_path: Path object leading to chunks file
        
        Atributes:
            -self.retriever: bm25 algorithm based retriever
            -self.sources: list of MinimalSource objs representing
            units of information
        """
        try:
            self.retriever = bm25s.BM25.load(index_path)
        except Exception as e:
            raise Exception(f'Failed to load index - {e}.')

        self.sources = [MinimalSource(**s)
                        for s in json.loads(chunks_path.read_text(
                            encoding='utf-8', errors='ignore'))]
        if not self.sources:
            raise ValueError('No sources to retrieve.')


    def _retrieve_single_query(self,
                               query: str | UnansweredQuestion,
                               k: int) -> MinimalSearchResults:
        if isinstance(query, str):
            question_model = UnansweredQuestion(question=query)
            question_tokens = bm25s.tokenize(query)
        elif isinstance(query, UnansweredQuestion):
            question_model = query
            question_tokens = bm25s.tokenize(query.question)
        else:
            raise ValueError()

        docs, _ = self.retriever.retrieve(question_tokens,
                                          k=k)
        sources = [self.sources[s] for s in docs[0]]
        return MinimalSearchResults(
            question_id=question_model.question_id,
            question=query if isinstance(query, str) else query.question,
            retrieved_sources=sources
        )

    def retrieve_search_results(self,
                                queries: list[str] | list[UnansweredQuestion],
                                k: int) -> StudentSearchResults:
        return StudentSearchResults(
            search_results=[self._retrieve_single_query(q, k)
                            for q in queries],
            k=k)
