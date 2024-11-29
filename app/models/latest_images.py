from pydantic import BaseModel


class LatestImages(BaseModel):
    version: str
    commit: str

    def __str__(self):
        return f"version: {self.version}, commit: {self.commit}"

    def sha(self):
        return self.commit[:7]
