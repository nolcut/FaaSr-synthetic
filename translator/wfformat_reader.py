import json
from workflow import *

def wfformat_to_workflow_obj(data):
    """"
    Takes WfFormat JSON and uses it to initialize a WfFormatWorkflow object
    :param_data: JSON instance
    """

    task_runtimes = {}
    tasks = []
    files = {}

    for f in data['workflow']['specification']['files']:
        files[f['id']] = f['sizeInBytes']
    
    for e in data['workflow']['execution']['tasks']:
        task_runtimes[e['id']] = e['runtimeInSeconds']

    for t in data['workflow']['specification']['tasks']:
        tasks.append(Task(runtime=task_runtimes[t['id']], name=t['name'], id=t['id'], children=t['children'], parents=t['parents'], input_files=t['inputFiles'], output_files=t['outputFiles']))

    return WfFormatWorkflow(files, tasks)