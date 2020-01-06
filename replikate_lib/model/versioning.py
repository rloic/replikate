from typing import Union


class Versioning:
    def __init__(self, repository: str, commit: Union[str, None], authentication: bool):
        self.repository = repository
        self.commit = commit
        self.authentication = authentication