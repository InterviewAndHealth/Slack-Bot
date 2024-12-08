from pydantic import BaseModel

from app import DEFAULT_PACKAGE_USERNAME


class Package(BaseModel):
    username: str = DEFAULT_PACKAGE_USERNAME
    image: str

    def __str__(self):
        return f"{self.username}/{self.image}"

    class Config:
        str_to_lower = True
