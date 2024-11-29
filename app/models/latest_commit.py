from pydantic import BaseModel


class LatestCommit(BaseModel):
    commit: str
    date: str

    def __str__(self):
        return f"{self.commit}"

    def sha(self):
        return self.commit[:7]
