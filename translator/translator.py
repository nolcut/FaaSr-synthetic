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
        files(list[{str: int}]): A list of key value pair's specifying the names and sizes of the files in the workflow
        function_list(list[SyntheticFaaSrAction:]): A list of FaaSr actions in the workflow
        function_git_repos(list{str: str}): A list of key value pairs that specify the repos of the workflows R functions (R function: repo)
    """
    function_list = []
    first_function = None
    for t in workflow.tasks:
        if len(t.parents) == 0 and len(t.children) > 1:
            if first_function is not None:
                print("Multiple start tasks")
            first_function = SyntheticFaaSrAction(execution_time=t.runtime, name=t.name, input_files=t.input_files, output_files=t.output_files, invoke_next=t.children)
            function_list.append(first_function)
            continue
        function_list.append(SyntheticFaaSrAction(execution_time=t.runtime, name=t.id, input_files=t.input_files, output_files=t.output_files, invoke_next=t.children))

    return SyntheticFaaSrWorkflow(
                                  compute_server=compute_server, 
                                  data_store=data_store, 
                                  data_endpoint=data_endpoint, 
                                  bucket=bucket, 
                                  region=region, 
                                  writable=writable, 
                                  files=workflow.files,
                                  function_list=function_list, 
                                  start_function=first_function
                                  )


# creates WRENCH XML, execution controller, and sim from FaaSr JSON file.
def compile_faasr_to_wrench_sim(workflow: SyntheticFaaSrWorkflow):
    print("compile_faasr_to_wrench_sim not implemented")
