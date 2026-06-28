from models.country import Country

@dataclass
class Author:
    """
    Represents a country.
    """
    
    def __init__(self, id, year, name, country):
        self.id = id
        self.year = year
        self.name = name
        self.country = list[country]
