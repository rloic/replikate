import datetime
import os
import subprocess
from typing import List, TypeVar

from replikate_lib.model.ExecutionState import ExecutionState, Status
from replikate_lib.model.project import Project
from replikate_lib.services.serializers.csv import CSV
from replikate_lib.terminal.colors import info, warn, err

T = TypeVar('T')


def fill(a: List[T], value: T):
    for i in range(len(a)):
        a[i] = value


def run(p: Project, cmd: str) -> ExecutionState:
    try:
        status = subprocess.call(cmd.split(' '), cwd=p.path)
        if status != 0:
            return ExecutionState(Status.INVALID_SCRIPT_EXECUTION, cmd)
        else:
            return ExecutionState(Status.VALID, cmd)
    except:
        return ExecutionState(Status.INVALID_SCRIPT_EXECUTION, cmd)


def safe_run(p: Project, cmd: str):
    execution = run(p, cmd)
    if not execution:
        print(execution)
        exit(execution.status.value)


def check(status: ExecutionState):
    if not status:
        print(status)
        exit(status.status.value)


def join_multiline(elements: List[str]) -> str:
    content = ""
    curr_len = 0
    for i, element in enumerate(elements):
        content += element
        curr_len += len(element)
        if i + 1 < len(elements) and curr_len + len(elements[i + 1]) > 90:
            content += " \\\n   > "
            curr_len = 0
        else:
            content += " "
    return content


def execute(
        p: Project,
        folder: str,
        config_file_name: str,
):
    results_folder = folder + '/' + 'logs'
    summary = folder + '/' + config_file_name + '.tsv'
    if not os.path.exists(summary):
        with open(summary, 'a+') as summary_csv:
            summary_csv.write(CSV.header(p))
            summary_csv.close()

    for experiment in sorted(p.experiments, key=lambda it: it.level):
        exp_folder = results_folder + '/' + experiment.name
        if not os.path.exists(exp_folder):
            os.makedirs(exp_folder)
        lock_file = exp_folder + '/' + '_lock'
        if not os.path.exists(lock_file):
            open(lock_file, 'w+')
            now = datetime.datetime.now()
            print(' | Starting experiment [{}] @ {}'.format(experiment.name, now))

            times = [0.0 for _ in range(p.iterations)]

            for i in range(p.iterations):
                log_filename = exp_folder + '/' + str(i) + '.txt'
                err_filename = exp_folder + '/' + str(i) + '.err'

                timeout = None
                if p.timeout is not None:
                    timeout = p.timeout.to_seconds()
                if experiment.timeout is not None:
                    timeout = experiment.timeout.to_seconds()

                with open(log_filename, 'a+') as log_file, open(err_filename, 'w+') as err_file:
                    skip_next = False
                    try:
                        start = datetime.datetime.now()
                        execution = p.restore(p.execute).split(' ') + list(map(p.restore, map(str, experiment.parameters)))
                        print('   $ {}'.format(join_multiline(execution)), end='\t', flush=True)
                        subprocess.check_call(
                            execution,
                            stdout=log_file,
                            stderr=err_file,
                            timeout=timeout,
                            cwd=p.path
                        )
                        end = datetime.datetime.now()
                        diff = end - start
                        times[i] = round(diff.total_seconds() * 10) / 10.0
                        print('[' + info('V') + ']')

                    except subprocess.TimeoutExpired:
                        times[i] = 'T'
                        log_file.write('Timeout of {} seconds\n\n'.format(timeout))
                        log_file.flush()
                        print('[' + warn('T') + ']')

                        skip_next = True
                    except subprocess.CalledProcessError as c:
                        times[i] = 'E'
                        print('[' + err('E') + ']')

                        print(err('```'))
                        for line in open(err_filename):
                            print(err(line), end='')
                            log_file.write(line)
                        print(err('```'))

                        log_file.write('Subprocess error {}\n\n'.format(c))
                        log_file.flush()

                        skip_next = True
                os.remove(err_filename)

                if skip_next:
                    break

            with open(summary, 'a+') as summary_csv:
                summary_csv.write(CSV.row(p, experiment, exp_folder + '/0.txt', times))
                summary_csv.close()
