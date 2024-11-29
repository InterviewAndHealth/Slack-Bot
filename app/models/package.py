from pydantic import BaseModel


class Package(BaseModel):
    username: str
    image: str

    def __str__(self):
        return f"{self.username}/{self.image}"

    class Config:
        str_to_lower = True
