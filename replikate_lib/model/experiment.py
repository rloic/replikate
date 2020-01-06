from typing import List, Union

from replikate_lib.model.timeout import Timeout


class Experiment:
    def __init__(
            self,
            name: str,
            parameters: List[str],
            disable: bool,
            timeout: Union[Timeout, None],
            level: int
    ):
        self.name = name
        self.parameters = parameters
        self.disable = disable
        self.timeout = timeout
        self.level = level