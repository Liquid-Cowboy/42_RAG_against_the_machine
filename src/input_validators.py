from pydantic import BaseModel, model_validator, Field
from pathlib import Path
from src.constants import (
    MAX_CHUNK_SIZE,
    REPO_PATH,
    INDEX_PATH,
    CHUNKS_PATH,
    OUTPUT_PATH,
    DATASET_UNANSWERED)

class InputError(Exception):
    pass


class CLIArgs(BaseModel):
    # index
    max_chunk_size: int = Field(default=MAX_CHUNK_SIZE, gt=0, le=2000)
    index_path: Path = Field(default=Path(INDEX_PATH))
    chunks_path: Path = Field(default=Path(CHUNKS_PATH))
    repository_path: Path = Field(default=Path(REPO_PATH))

    # search / answer
    query: str = ''
    k: int = Field(default=5, gt=0)
    dataset_path: Path = Field(default=Path(DATASET_UNANSWERED))
    save_directory: Path = Field(default=Path(OUTPUT_PATH))

    def validate_index(self) -> None:
        self._validate_path(self.index_path, 'index_path')
        self._validate_path(self.chunks_path, 'chunks_path', True)

        if not self.repository_path.exists():
            raise InputError(f'(--repository_path) {self.repository_path} '
                             'does not exist.')

    def validate_search(self) -> None:
        if not self.query.strip():
            raise InputError('No "--query" provided.')
        if not self.index_path.exists():
            raise InputError(f'(--index_path) {self.index_path} '
                             'does not exist.')
        if not self.chunks_path.exists():
            raise InputError(f'(--chunks_path) {self.chunks_path}'
                             ' does not exist.')

    def validate_search_dataset(self) -> None:
        if not self.dataset_path.exists():
            raise InputError(f'(--dataset_path) {self.dataset_path} '
                             'does not exist.')
        if not str(self.dataset_path).endswith('.json'):
            raise InputError(f'(--dataset_path) {self.dataset_path} '
                             'does not lead to a valid JSON file.')
        if not self.index_path.exists():
            raise InputError(f'(--index_path) {self.index_path} '
                             'does not exist.')
        if not self.chunks_path.exists():
            raise InputError(f'(--chunks_path) {self.chunks_path}'
                             ' does not exist.')
        self._validate_path(self.save_directory, 'save_directory')

    def _validate_path(self, path: str | Path,
                       field_name: str, is_file: bool = False) -> Path:

        if not str(path).strip():
            raise InputError(f'"--{field_name}" empty.')

        path = (Path(path) if isinstance(path, str)
                else path)
        if is_file:
            path.parent.mkdir(parents=True, exist_ok=True)
        else:
            path.mkdir(parents=True, exist_ok=True)
        return path
