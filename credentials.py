from typing import List


class Credentials:
    def __init__(self, host: str, port: int, user: str, password: str, paths: List[str]):
        self.host: str = host
        self.port = port
        self.user: str = user
        self.password: str = password
        self.paths: List[str] = paths