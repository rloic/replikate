import os
import shutil

from replikate_lib.model.ExecutionState import ExecutionState, Cancelled, Status, Ok
from replikate_lib.model.project import Project
from replikate_lib.services.workers.execute import run


def pull(p: Project) -> ExecutionState:
    if p.versioning is None:
        return ExecutionState(Status.MISSING_FIELD_ERROR, 'Project versioning is not filled.')

    path = p.path
    if os.path.exists(path) and not os.path.isdir(path):
        return ExecutionState(Status.FILE_SYSTEM_ERROR, '{} is already present and is not a directory.'.format(path))

    if len(os.listdir(path)) != 0:  # Source are already downloaded
        print(' | Some files are present in the source directory {}.\n'
              ' | Would you erase them and fetch the sources from the repository [y\\N]? '.format(path), end='')

        while True:
            response = input()
            if response in ['', 'y', 'Y', 'n', 'N']:
                break

        erase = response in ['y', 'Y']
        if erase:
            shutil.rmtree(path)
            os.makedirs(path)
        else:
            return Cancelled

    versioning = p.versioning
    git_cmd = 'git clone {} {}'.format(versioning.repository, '.')

    git_exec = run(p, git_cmd)
    if not git_exec:
        return git_exec

    if p.versioning.commit is not None:
        checkout_cmd = 'git checkout {}'.format(
            versioning.commit
        )
        checkout_execution = run(p, checkout_cmd)
        if not checkout_execution:
            return checkout_execution

    return Ok
