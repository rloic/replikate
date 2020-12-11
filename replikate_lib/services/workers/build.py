from replikate_lib.model.ExecutionState import Ok, ExecutionState
from replikate_lib.model.project import Project
from replikate_lib.services.workers.execute import run


def build(p: Project) -> ExecutionState:
    build_cmd = p.restore(p.compile).split(" && ")
    status = Ok
    for cmd in build_cmd:
        print("  $ {}".format(cmd))
        status &= run(p, cmd)
    return status
