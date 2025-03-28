import random
from workflow import *

def translate_wf_to_faasr_gh(
        workflow: WfFormatWorkflow, 
        compute_server: ComputeServer,
        data_store="My_Minio_Bucket",
        data_endpoint="https://play.min.io", 
        bucket="faasr", 
        region="us-east-1", 
        writable="TRUE", 
        files_folder="synthetic_files",
        funtion_gitrepos={"synthetic_faas_function": "nolcut/FaaSr-synthetic"}
        ):
    """"
    Copies data from WfFormat workflow object and initializes a FaaSr workflow object that uses GitHub actions

    Args:
        compute_server(ComputeServer): FaaS compute server
        data_store(str): Name of data store
        data_endpoint(str): S3 endpoint
        bucket(str): Name of S3 bucket
        region(str): Region for S3 data_store
        writable(str): Specifies if S3 bucket is writable
        files_folder(str): Name of folder in S3 containing workflow files
        files({str: int}): A dictionary specifying the names and sizes of the files in the workflow
        function_list(list[SyntheticFaaSrAction:]): A list of FaaSr actions in the workflow
        function_git_repos(list{str: str}): A list of key value pairs that specify the repos of the workflows R functions (R function: repo)
    """
    match (compute_server.faastype):
        case "GitHubActions":
            action_container = "ghcr.io/faasr/github-actions-tidyverse:latest"
        case "Lambda":
            action_container = ".amazonaws.com/aws-lambda-tidyverse:latest"
        case "OpenWhisk":
            action_container = "faasr/openwhisk-tidyverse:latest"
    function_list = []
    entry_functions = []
    for t in workflow.tasks:
        function = SyntheticFaaSrAction(compute_server=compute_server, execution_time=t.runtime, name=t.id, action_container=action_container, input_files=t.input_files, output_files=t.output_files, invoke_next=t.children)
        function_list.append(function)
        if len(t.parents) == 0:
            entry_functions.append(function)

    # no entry node
    if len(entry_functions) == 0:
        print("No entry function")
        quit()
    # if there is multiple functions with no children, then
    # we create a new node that invokes all of these entry nodes
    elif len(entry_functions) > 1:
        rand_num = random.getrandbits(32)
        entry_function_names = [action.name for action in entry_functions]
        entry = SyntheticFaaSrAction(compute_server=compute_server, execution_time=0, name=f"start{rand_num}", action_container=action_container, invoke_next=entry_function_names)
        function_list.append(entry)
    # only one entry node
    else:
        entry = entry_functions[0]
        function_list.append(entry)

    return SyntheticFaaSrWorkflow(
                                  compute_server=compute_server, 
                                  data_store=data_store, 
                                  data_endpoint=data_endpoint, 
                                  bucket=bucket, 
                                  region=region, 
                                  writable=writable, 
                                  files=workflow.files,
                                  function_list=function_list, 
                                  start_function=entry
                                  )


# creates WRENCH XML, execution controller, and sim from FaaSr JSON file.
def compile_faasr_to_wrench_sim(workflow: SyntheticFaaSrWorkflow):
    print("compile_faasr_to_wrench_sim not implemented")
