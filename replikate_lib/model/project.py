from typing import Union, List, Dict

from replikate_lib.model.experiment import Experiment
from replikate_lib.model.requirement import Requirement
from replikate_lib.model.timeout import Timeout
from replikate_lib.model.versioning import Versioning


class Project:
    def __init__(
            self,
            comments: Union[str, None],
            path: str,
            requirements: List[Requirement],
            shortcuts: Dict[str, str],
            iterations: int,
            versioning: Versioning,
            compile: str,
            execute: str,
            experiments: List[Experiment],
            measures: List[str],
            stats: List[str],
            timeout: Timeout
    ):
        self.comments = comments
        self.path = path
        self.requirements = requirements
        self.shortcuts = shortcuts
        self.iterations = iterations
        self.versioning = versioning
        self.compile = compile
        self.execute = execute
        self.experiments = experiments
        self.measures = measures
        self.stats = stats
        self.timeout = timeout

    def restore(self, cmd: str) -> str:
        cmd = cmd.replace('{PROJECT}', self.path)
        shortcuts = self.shortcuts
        if shortcuts is None or len(shortcuts) == 0:
            return cmd
        else:
            while True:
                old = cmd
                for label, text in shortcuts.items():
                    cmd = cmd.replace('{' + label + '}', text)
                cmd = cmd.replace('{PROJECT}', self.path)
                if cmd == old:
                    break
            return cmd