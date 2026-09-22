from pathlib import Path
import os
from src.constants import (CHUNK_OVERLAP)
from src.data_models import MinimalSource
from langchain_text_splitters import (
     RecursiveCharacterTextSplitter as Splitter,
     TextSplitter,
     Language)
import bm25s
import json
from time import perf_counter


class Indexer():
    def __init__(self, max_chunk_size: int,
                 index_path: Path, chunks_path: Path) -> None:
        """
        Initializes the indexer object, providing methods and atributes
        to keep track
        """
        self.max_chunk_size: int = max_chunk_size
        self.file_paths: list[Path] = []
        self.chunks = []
        self.index_path = index_path
        self.chunks_path = chunks_path

    def store_chunks(self) -> None:
        chunks = [c.get('source').model_dump() for c in self.chunks]
        with open(self.chunks_path, 'w+', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2)

    def save_file_paths(self, dir_path: str) -> None:
        """
        Finds all non-hidden files in a given directory path.

        Parameters:
            dir_path: directory path string.
        """
        if not Path(dir_path).exists():
            raise ValueError(f'"{dir_path}" is not a valid directory.')
        for dirpath, dirnames, filenames in os.walk(dir_path):
            dirnames[:] = [d for d in dirnames if not d.startswith('.')]
            self.file_paths.extend([Path(os.path.join(dirpath, p))
                                    for p in filenames
                                    if not p.startswith('.')])
        if not self.file_paths:
            raise ValueError(f'No files found at "{dir_path}".')

    def _get_splitter(self, file_path: Path) -> TextSplitter:
        """
        Evaluates the type of document by checking it's
        extension and returns a custom text splitter.

        Parameters:
            file_path: Path to file.
        """
        if str(file_path).endswith('.py'):
            return Splitter.from_language(
                 language=Language.PYTHON,
                 chunk_size=self.max_chunk_size,
                 chunk_overlap=int(self.max_chunk_size * CHUNK_OVERLAP),
                 add_start_index=True,
                 keep_separator=True,
                 strip_whitespace=False,
            )

        elif str(file_path).endswith('.md'):
            return Splitter.from_language(
                language=Language.MARKDOWN,
                chunk_size=self.max_chunk_size,
                chunk_overlap=int(self.max_chunk_size * CHUNK_OVERLAP),
                add_start_index=True,
                keep_separator=True,
                strip_whitespace=False,
                        )

        return Splitter(
            chunk_size=self.max_chunk_size,
            chunk_overlap=int(self.max_chunk_size * CHUNK_OVERLAP),
            add_start_index=True,
            keep_separator=True,
            strip_whitespace=False,
        )

    def chunk_docs(self) -> None:
        """
        Chunks the docs.
        """
        start = perf_counter()
        if not self.file_paths:
            raise ValueError('No files to chunk.')
        for path in self.file_paths:
            splitter = self._get_splitter(path)
            content = path.read_text(encoding='utf-8',
                                     errors='ignore')
            docs = splitter.create_documents([content])
            for doc in docs:
                f_index = doc.metadata.get('start_index', 0)
                l_index = f_index + len(doc.page_content)
                source = MinimalSource(
                        file_path=str(path),
                        first_character_index=f_index,
                        last_character_index=l_index
                    )
                self.chunks.append({
                    'source': source,
                    'content': content[f_index: l_index]
                })
        print(f'Took {perf_counter() - start} seconds...', flush=True)

    def index_chunks(self) -> None:
        print()
        print('Getting content...', flush=True)
        start = perf_counter()
        corpus = [c.get('content', '') for c in self.chunks]
        print(f'Took {perf_counter() - start} seconds...', flush=True)
        if not corpus:
            raise ValueError('Nothing to index.')
        print('Tokenizing corpus...')
        corpus_tokens = bm25s.tokenize(corpus)
        print('Creating retriever...', flush=True)
        retriever = bm25s.BM25(corpus=corpus)
        print('Indexing corpus...', flush=True)
        retriever.index(corpus_tokens)
        retriever.save(self.index_path)
