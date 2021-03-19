import os
from typing import List, Optional

import csv
from replikate_lib.model.experiment import Experiment
from replikate_lib.model.project import Project
from replikate_lib.services.computation.stats import Stats


def remove_nl(s: str) -> str:
    return s.replace('\n', '')


class HTML:
    @staticmethod
    def header(p: Project) -> str:
        header = '<tr><th>experiments</th>'
        for measure in p.measures:
            if measure != 'skip':
                header += '<th>' + measure + '</th>'
        for stat in p.stats:
            header += '<th>' + stat + '</th>'
        header += '<th>arguments</th>'
        header += '</tr>'
        return header

    @staticmethod
    def from_csv_file(file):
        html = '<table>'
        with open(file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
            is_header = True
            for row in csv_reader:
                html += '<tr>'
                tag = 'td'
                end = ''
                if is_header:
                    is_header = False
                    tag = 'th'
                    end = '</th><th>arguments'
                html += '<' + tag + '>'
                html += ('</' + tag + '><' + tag + '>').join(row)
                html += end
                html += '</' + tag + '></tr>'

        html += '</table>'
        return html

    @staticmethod
    def row(p: Project, exp: Experiment, log_file: Optional[str], times: List[int]) -> str:
        row = '<tr><td>' + exp.name + '</td>'

        timeout = None
        if p.timeout is not None:
            timeout = p.timeout
        if exp.timeout is not None:
            timeout = exp.timeout

        if log_file is not None and os.path.isfile(log_file):
            content = list(map(remove_nl, open(log_file, 'r').readlines()[-1].split(',')))
            for i in range(len(p.measures)):
                row += '<td>'
                if p.measures[i] != 'skip' and len(content) > i:
                    row += content[i]
                row += '</td>'

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
            if times[0] == -2:
                row += '<td>error</td>'
            elif times[0] == -1:
                row += '<td>timeout (> {} sec)</td>'.format(timeout.to_seconds())
            elif value is None:
                row += '<td>nan</td>'
            else:
                row += '<td>' + str(value) + '</td>'

        row += '<td>'
        for parameter in exp.parameters:
            row += str(parameter)
            row += '&nbsp;&nbsp;&nbsp;&nbsp;'
        row += '</td>'
        return row + '</tr>'
