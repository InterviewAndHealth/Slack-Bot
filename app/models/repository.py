from pydantic import BaseModel

from app import DEFAULT_BRANCH, DEFAULT_REPOSITORY_OWNER


class Repository(BaseModel):
    owner: str = DEFAULT_REPOSITORY_OWNER
    repo: str
    branch: str = DEFAULT_BRANCH

    def __str__(self):
        return f"{self.owner}/{self.repo}"
