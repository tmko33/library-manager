class UserService:
    def __init__(self):
        self.users = []
        self._id_counter = 0

    def add_user(self, name, address, email, phone) -> User:
        user = User(self._id_counter, name, address, email, phone)
        self.users.append(user)
        self._id_counter += 1
        return user