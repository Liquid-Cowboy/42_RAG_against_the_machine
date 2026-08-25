from pydantic import BaseModel
from student.constants import (
    MAX_CHUNK_SIZE
)


class UserCLI(BaseModel):
    def index(self, max_chunk_size: int = MAX_CHUNK_SIZE):
        """
        Index the repository.
        """
        try:
            if (not isinstance(max_chunk_size, int) or
               max_chunk_size < 1):
                raise ValueError('"--max_chunk_size must be a positive integer."')
        except:
            pass


    def search(self):
        """
        Search for a single query.
        """
        pass

    def search_dataset(self):
        """
        Process multiple questions and output search results.
        """
        pass

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
