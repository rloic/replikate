#!/usr/bin/python3
import os
import shutil
import subprocess
import sys
from typing import Union, TypeVar

import yaml

from replikate_lib.model.experiment import Experiment
from replikate_lib.model.project import Project
from replikate_lib.model.requirement import Requirement
from replikate_lib.model.timeout import Timeout
from replikate_lib.model.versioning import Versioning
from replikate_lib.services.workers.build import build
from replikate_lib.services.workers.execute import execute, check
from replikate_lib.services.workers.initalizer import init
from replikate_lib.services.workers.pull_src import pull

T = TypeVar('T')


def versioning_from_yml(yml) -> Versioning:
    return Versioning(
        yml['repository'],
        yml['commit'] if 'commit' in yml else None,
        bool(yml['authentication']) if 'authentication' in yml else False
    )


def experiment_from_yml(yml) -> Experiment:
    return Experiment(
        yml['name'],
        yml['parameters'],
        bool(yml['disable'] == 'true') if 'disable' in yml else None,
        timeout_from_yml(yml['timeout']) if 'timeout' in yml else None,
        int(yml['level']) if 'level' in yml else 0
    )


def timeout_from_yml(yml) -> Timeout:
    return Timeout(yml['duration'], yml['unit'])


def requirement_from_yml(yml) -> Requirement:
    return Requirement(yml['name'], yml['version'])


def project_from_file(f) -> Union[Project, None]:
    data = yaml.safe_load(f)
    return Project(
        data['comments'] if 'comments' in data else None,
        data['dev_path'] if 'dev_path' in data else None,
        list(map(requirement_from_yml, data['requirements'])) if 'requirements' in data else [],
        data['shortcuts'] if 'shortcuts' in data else {},
        int(data['iterations']),
        versioning_from_yml(data['versioning']) if 'versioning' in data else None,
        data['compile'],
        data['execute'],
        list(map(experiment_from_yml, data['experiments'])),
        data['measures'],
        data['stats'],
        timeout_from_yml(data['timeout']) if 'timeout' in data else None
    )


def clean(folder: str, config_filename: str):
    shutil.rmtree(folder + '/' + 'logs')
    if os.path.isfile(folder + '/' + config_filename + '.tsv'):
        os.remove(folder + '/' + config_filename + '.tsv')
    print(' | Done')


def generate_file(p: Project, config_file_name: str, model: str):
    hash = subprocess.check_output('git rev-parse --verify HEAD'.split(' '))
    hash = hash.decode('UTF-8').replace('\n', '')
    short_hash = hash[:6]
    print('\\begin{{model}}[{} {}] \\label{{md:{}:{}}}'
        .format(
        model.replace('_', ' '),
        short_hash,
        config_file_name[:config_file_name.rindex('.')][config_file_name.rindex('/') + 1:].replace('_', '-'),
        short_hash
    )
    )
    print('\\configfile{{{}}}{{{}}}'.format(hash, config_file_name.replace('_', '\\_')))
    print(p.comments)
    print('\\end{model}')


def mslice(s):
    i = s.rfind('/')
    if i == -1:
        return ('.', s)
    ls = slice(i)
    rs = slice(i + 1, len(s))
    return (s[ls], s[rs])


if __name__ == '__main__':
    path = sys.argv[1]

    (folder, config_filename) = mslice(path[:path.rindex('.')])

    folder = folder + '/' + config_filename

    with open(path) as stream:
        project = project_from_file(stream)
        project.path = folder + '/' + 'src'

        if '--dev' in sys.argv:
            if project.dev_path is None:
                print('Development path is not defined')
                exit(1)
            project.path = project.dev_path.replace('{FILE}', folder)
        else:
            project.path = project.path.replace('{FILE}', folder)


        if len(sys.argv) == 2:
            print('Project requirements: ')
            for requirement in project.requirements:
                print(' - {} >= {}'.format(requirement.name, requirement.version))
            print()
            print('Commands: ')
            print(' -g or --git:\t Retrieves the sources from the remote repository (if exists)')
            print(' -b or --build:\t Compile the project')
            print(
                ' -r or --run:\t Run the experiments. The summary file will be located in {}'
                    .format(project.path)
            )
            print(' --clean:\t Clean the logs folder and remove the summary file (.tsv)')
            print(' --mail: Configure the automatic email sending. ex --email:to=me@my-mail.com --email:frequency=each')
            print('    to: add an email to the recipients')
            print('    frequency: send an email foreach experiment (each) or when the full summary is complete (end).')
            print('    on_failure: indicates whenever an email must be send when an experiment fails, '
                  'valid options are [never, first, always]')
            print('    on_timeout: indicates whenever an email must be send when an experiment produces a timeout, '
                  'valid options are [never, first, always]')
            print()
            if project.comments is not None:
                print('Notes: ')
                print(project.comments)

        verbose = '-v' in sys.argv or '--verbose' in sys.argv
        init(project, folder)

        if '-g' in sys.argv or '--git' in sys.argv:
            print('--- Fetch source code ---')
            check(pull(project))
            print('--- Fetch source code ---')

        if '-b' in sys.argv or '--build' in sys.argv:
            print('--- Build project ---')
            check(build(project))
            print('--- Build project ---')

        if '--clean' in sys.argv:
            print('--- Clean old results ---')
            clean(folder, config_filename)
            init(project, folder)
            print('--- Clean old results ---')

        if '-r' in sys.argv or '--run' in sys.argv:
            print('--- Execute instances ---')
            end = False
            try:
                execute(project, folder, config_filename)
                print('--- Execute instances ---')
                end = True
            except KeyboardInterrupt:
                if not end:
                    print(flush=True)
                    print('--- Execute instances ---')
                print('Ctrl C was pressed.')

        file_generation = list(filter(lambda arg: arg.startswith('--file='), sys.argv))
        if len(file_generation) == 1:
            generate_file(project, path, file_generation[0][7:])
