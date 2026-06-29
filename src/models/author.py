from dataclasses import dataclass
from models.country import Country

@dataclass
class Author:

    id: int
    year: int
    name: str
    country: list[Country]