from pydantic import BaseModel
from src.input_validators import CLIArgs
from src.constants import (
    MAX_CHUNK_SIZE,
    REPO_PATH,
    INDEX_PATH,
    CHUNKS_PATH,
    OUTPUT_PATH,
    SEARCH_TEMPLATE,
    DATASET_UNANSWERED,
)
from src.data_models import RagDataset
from src.retrieval.Indexer import Indexer
from src.retrieval.Retriever import Retriever
from src.utils import (
    get_unique_filepath,)
import json
from os.path import join as join_path, split as split_path
from pathlib import Path


class UserCLI(BaseModel):

    def index(self, max_chunk_size: int = MAX_CHUNK_SIZE,
              index_path: str = INDEX_PATH,
              chunks_path: str = CHUNKS_PATH,
              repository_path: str = REPO_PATH):
        """
        Index the repository.
        """

        args = CLIArgs(max_chunk_size=max_chunk_size,
                       index_path=Path(index_path),
                       chunks_path=Path(chunks_path),
                       repository_path=Path(repository_path))
        args.validate_index()

        indexer = Indexer(args.max_chunk_size,
                          args.index_path,
                          args.chunks_path)

        print('Storing paths...', flush=True)
        indexer.save_file_paths(repository_path)

        print('Chunking docs...', flush=True)
        indexer.chunk_docs()
        if not [c.get('content', '').strip() for c in indexer.chunks]:
            raise Exception('No content to index.')

        print('Storing chunks...', flush=True)
        indexer.store_chunks()

        print('Indexing chunks...', flush=True)
        indexer.index_chunks()

    def search(self, query: str, k: int = 5,
               index_path: str = INDEX_PATH,
               chunks_path: str = CHUNKS_PATH,
               save_directory: str = OUTPUT_PATH):
        """
        Search for a single query.
        """
        args = CLIArgs(
            query=query,
            k=k,
            index_path=Path(index_path),
            chunks_path=Path(chunks_path),
            save_directory=Path(save_directory)
        )
        args.validate_search()

        retriever = Retriever(
            args.index_path,
            args.chunks_path)

        print(f'Searching database for "{query}"...', flush=True)
        search_res = retriever.retrieve_search_results([query], k)

        path = get_unique_filepath(join_path(save_directory, 'user_searches'),
                                   SEARCH_TEMPLATE)
        with open(path, 'w+', encoding='utf-8') as f:
            json.dump(search_res.model_dump(), f, indent=2)

        print(f'Results saved to {path}.', flush=True)

    def search_dataset(self,
                       dataset_path: str = DATASET_UNANSWERED,
                       save_directory: str = OUTPUT_PATH,
                       k: int = 5,
                       index_path: str = INDEX_PATH,
                       chunks_path: str = CHUNKS_PATH,
                       ):
        """
        Process multiple questions and output search results.
        """

        args = CLIArgs(
            dataset_path=Path(dataset_path),
            save_directory=Path(save_directory),
            k=k,
            index_path=Path(index_path),
            chunks_path=Path(chunks_path),
        )
        args.validate_search_dataset()

        with open(dataset_path, 'r', encoding='utf-8') as f:
            queries = [q for q in RagDataset(**json.load(f)).rag_questions]
        if not queries:
            raise Exception('No queries to process.')

        retriever = Retriever(
            args.index_path,
            args.chunks_path,
        )

        print(f'Searching dataset {dataset_path}...', flush=True)
        search_res = retriever.retrieve_search_results(queries, k)
        save_path = join_path(save_directory, split_path(dataset_path)[1])

        with open(save_path, 'w+', encoding='utf-8') as f:
            json.dump(search_res.model_dump(), f, indent=2)

        print(f'Results saved to {save_path}.', flush=True)

    def answer(self):
        """
        Answer a single question with context.
        """
        pass

    def answer_dataset(self):
        """
        Generate answers from search results.
        """
        pass

    def evaluate(self):
        """
        Evaluate search results against ground truth.
        """
        pass
