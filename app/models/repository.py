from pydantic import BaseModel


class Repository(BaseModel):
    owner: str
    repo: str
    branch: str = "main"

    def __str__(self):
        return f"{self.owner}/{self.repo}"
