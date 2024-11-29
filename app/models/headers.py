from enum import StrEnum

from pydantic import BaseModel


class Headers(BaseModel):
    authorization: str
    accept: str

    def to_dict(self):
        return {
            "Authorization": f"Bearer {self.authorization}",
            "Accept": self.accept,
        }

    class ACCEPT(StrEnum):
        JSON = "application/vnd.github+json"
        V3_JSON = "application/vnd.github.v3+json"
        RAW_JSON = "application/vnd.github.raw+json"
