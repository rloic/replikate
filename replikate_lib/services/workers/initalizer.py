import os

from replikate_lib.model.project import Project


def init(p: Project, folder):
    if not os.path.exists(p.path):
        os.makedirs(p.path)
    if not os.path.exists(folder):
        os.makedirs(folder)

    p.shortcuts['LOGS'] = folder + '/logs'
    for experiment in p.experiments:
        exp_folder = folder + '/' + 'logs' + '/' + str(experiment.name)
        if not os.path.exists(exp_folder):
            os.makedirs(exp_folder)