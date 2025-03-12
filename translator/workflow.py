from typing import Dict
import textwrap

class ComputeServer:
    """Holds data about compute server in the FaaSr workflow
    
    args:
        name(str): name of compute server
        faastype(str): FaaS provider
    """
    def __init__(self, faastype: str, name: str):
        self.name = name
        self.faastype = faastype
class OW_ComputeServer(ComputeServer):
    """Holds data about OpenWhisk compute server in the FaaSr workflow
    
    args:
        name(str): name of compute server
        faastype(str): FaaS provider
        namespace(str): OpenWhisk username
        ssl(str): Whether or not SSL is used for trigger
        endpoint(str): OpenWhisk endpoint
    """
    def __init__(self, name: str, faastype:str, namespace: str, ssl: str, endpoint: str):
        super().__init__(name=name, faastype=faastype)
        self.namespace = namespace
        self.ssl = ssl
        self.endpoint = endpoint

class Lambda_ComputeServer(ComputeServer):
    """Holds data about AWS Lambda compute server in the FaaSr workflow
    
    args:
        name(str): name of compute server
        faastype(str): FaaS provider
        region(str): AWS Lambda region
    """
    def __init__(self, name: str, faastype: str, region: str):
        super().__init__(name=name, faastype=faastype)
        self.region = region

class GH_ComputeServer(ComputeServer):
    """Holds data about OpenWhisk compute server in the FaaSr workflow
    
    args:
        name(str): name of compute server
        faastype(str): FaaS provider
        username(str): GitHub username
        action_repo_name(str): GitHub repo for GH Actions
        Branch(str): Branch of action repo
    """
    def __init__(self, name: str, faastype: str, username: str, action_repo_name: str, branch: str):
        super().__init__(name=name, faastype=faastype)
        self.username = username
        self.action_repo_name = action_repo_name
        self.branch = branch
    

class SyntheticFaaSrAction:
    """"
    Represents an action in the faasr workflow.

    Args:
        compute_server(ComputeServer): the compute server that the function will run on
        execution_time(float): Execution time of the function in seconds
        name(str): Action name
        action_continaer(str): Path to function's container
        input_files(list[str]): A list of input files for the function
        output_files(list[str]): A list of output files for the function
        invoke_next(list[str]): A list of functions to invoke next
        function_name(str): Name of FaaS function that the function calls
    """
    def __init__(
        self, 
        compute_server: ComputeServer,
        execution_time: float,
        name: str,
        input_files=[], 
        output_files=[], 
        invoke_next=[], 
        function_name="synthetic_faas_function"
    ):
        if execution_time < 0:
            raise ValueError("Execution time cannot be negative")
        self.compute_server = compute_server
        self.execution_time = execution_time
        self.name = name
        self.input_files = input_files
        self.output_files = output_files
        self.invoke_next = invoke_next
        self.function_name = function_name
        self.action_container = ""

    



class Task:
    """"
    Represents a task in the WfFormat workflow.

    Args:
        runtime(float): Time that task runs for after it begins execution
        name(str): Task name
        id(str): Unique task identifier
        children(list[str]): List of tasks that the task is dependant on
        parents(list[str]: List of tasks that are dependant on the task
        input_files(list[str]): A list of input files for the task
        output_files(list[str]): A list of output files for the task
    """
    def __init__(
        self, 
        runtime: float, 
        name: str, 
        id: str, 
        children=None, 
        parents=None, 
        input_files=None, 
        output_files=None
    ):
        if runtime < 0:
            raise ValueError("Runtime cannot be negative")
        self.runtime = runtime
        self.name = name
        self.id = id
        self.children = children if children is not None else []
        self.parents = parents if parents is not None else []
        self.input_files = input_files if input_files is not None else []
        self.output_files = output_files if output_files is not None else []


class WfFormatWorkflow:
    """"
    Represents WfFormat workflow

    Args:
        files(list[{str: int}]): List of key value pairs for files in the workflow's names and size. 
        tasks(list[Task]): List of tasks in the workflow
    """
    def __init__(self, files=None, tasks=None):
        self.files = files if files is not None else {str: int}
        self.tasks = tasks if tasks is not None else [Task]
    
    def __str__(self):
        """"
        Returns WfFormatWorkflow data as a readable string
        """
        file_names = self.files.keys()
        task_lst = []
    
        output = "--------------WF WORKFLOW--------------" + "\nFiles: "
        for f in file_names:
            output += f" {f} | "
        
        output += "\n\nTasks: "
        for t in self.tasks:
            output += f"{t.name} ({t.runtime:.3f}s) | "
        return output




class SyntheticFaaSrWorkflow:
    """"
    Represents a FaaSr workflow

    Args:
        compute_server(str): Name of compute server used for FaaS calls
        data_stores(str): Name of S3 used for data stores
        data_endpoint(str): S3 endpoint
        bucket(str): Name of S3 bucket
        region(str): Region for S3 data_store
        writable(str): Specifies if S3 bucket is writable
        files_folder(str): Name of folder in S3 containing workflow files
        files(list[{str: int}]): A list of key value pair's specifying the names and sizes of the files in the workflow
        function_list(list[SyntheticFaaSAction:]): A list of FaaSr actions in the workflow
        function_git_repos(list{str: str}): A list of key value pairs that specify the repos of the workflows R functions (R function: repo)
    """
    def __init__(
        self, 
        compute_server: ComputeServer, 
        data_store="My_Minio_Bucket", 
        data_endpoint="https://play.min.io", 
        bucket="faasr", 
        region="us-east-1", 
        writable="TRUE", 
        files_folder="synthetic_files",
        files=None, 
        function_list=None, 
        start_function=None,
        function_git_repos=None
        ):
        self.files = files if files is not None else []
        self.compute_server = compute_server
        self.data_store = data_store
        self.data_endpoint = data_endpoint
        self.bucket = bucket
        self.region = region
        self.writable = writable
        self.files_folder=files_folder
        self.function_list = function_list
        self.start_function = start_function
        self.function_git_repos = function_git_repos if function_git_repos is not None else {"synthetic_faas_function": "nolcut/FaaSr-synthetic"}


    def __str__(self):
        """"
        returns FaaSr workflow data as a readable string
        """
        file_names = self.files.keys()
        task_lst = []
    
        files_str = ""
        for f in file_names:
            files_str += f" {f} |"
        
        functions_str = ""
        for function in self.function_list:
            functions_str += f"{function.name} ({function.execution_time:.3f}s) | "


        output = (f"--------------FAASR WORKFLOW--------------\n"
        f"Compute Server: {self.compute_server.name}\n"
        f"FaaS Type: {self.compute_server.faastype}\n")


        match self.compute_server.faastype:
            case "GitHubActions":
                output += f"Username: {self.compute_server.username}\n"
                output += f"Action Repo Name: {self.compute_server.action_repo_name}\n"
                output += f"Branch: {self.compute_server.branch}\n"
            case "Lambda":
                output += f"\nRegion: {self.compute_server.region}\n"
            case "OpenWhisk":
                output += f
                output += f"Namespace: {self.compute_server.namespace}\n"
                output += f"Endpoint: {self.compute_server.endpoint}\n"

        output += (f"Data Store: {self.data_store}\n"
        f"Data Endpoint: {self.data_endpoint}\n"
        f"Bucket: {self.bucket}\n"
        f"Region: {self.region}\n"
        f"Writable: {self.writable}\n"
        f"\nFiles: {files_str}\n"
        f"\nFunction List: {functions_str}\n"
        f"\nStart Function: {self.start_function.name} ({self.start_function.execution_time:.3f}s)\n"
        f"Function Git Repos: {self.function_git_repos}")
        return output
