import os
from typing import Union, List

from replikate_lib.services.computation.stats import Stats
from replikate_lib.model.experiment import Experiment
from replikate_lib.model.project import Project


def remove_nl(s: str) -> str:
    return s.replace('\n', '')


class CSV:
    @staticmethod
    def header(p: Project) -> str:
        header = 'experiments\t'
        for measure in p.measures:
            if measure != 'skip':
                header += measure + '\t'
        for stat in p.stats:
            header += stat + '\t'
        header += '\n'
        return header

    @staticmethod
    def row(p: Project, exp: Experiment, log_file: Union[str, None], times: List[Union[float, str]]) -> str:
        row = '"' + exp.name + '"\t'

        timeout = None
        if p.timeout is not None:
            timeout = p.timeout
        if exp.timeout is not None:
            timeout = exp.timeout

        if log_file is not None and os.path.isfile(log_file):
            content = list(map(remove_nl, open(log_file, 'r').readlines()[-1].split(',')))
            for i in range(len(p.measures)):
                if p.measures[i] != 'skip':
                    if len(content) > i:
                        row += content[i]
                    row += '\t'

        for stat in p.stats:
            value = None
            if stat == 'min' or stat == 'MIN':
                value = Stats.min(times)
            elif stat == 'mean' or stat == 'MEAN' or stat == 'avg' or stat == 'AVERAGE':
                value = Stats.mean(times)
            elif stat == 'max' or stat == 'MAX':
                value = Stats.max(times)
            elif stat == 'time' or stat == 'TIME':
                value = Stats.first(times)
            else:
                print('Unknown stat {}'.format(stat))
            if 'T' in times:
                row += 'Timeout (> {} sec)'.format(timeout.to_seconds())
            elif 'E' in times:
                row += 'Error'
            elif value is None:
                row += 'Unknown'
            else:
                row += str(value)
            row += '\t'

        for parameter in exp.parameters:
            row += str(p.restore(str(parameter)))
            row += '\t'

        return row + '\n'
