from minio import Minio
from workflow import *
import json
import os

def write_faasr_obj_to_json(workflow: SyntheticFaaSrWorkflow, output_name: str):
    """"
    Writes faasr workflow to a FaaSr JSON and FaaSr file JSON
    :param_workflow: workflow object
    :param_output_name: output workflow name
    """
    start_function_name = workflow.start_function.name
    data_bucket = workflow.data_store
    faasr_data = {'ComputeServers' : {}, 'DataStores' : {}, 'FunctionList' : {}, 'ActionContainers' : {}, 'FunctionGitRepo' : workflow.function_git_repos, 'FunctionInvoke' : start_function_name, 'InvocationID' : '', 'FaaSrLog': 'FaaSrLog', 'LoggingDataStore': data_bucket, 'DefaultDataStore': data_bucket, 'FunctionCRANPackage': {"synthetic_faas_function": []}, 'FunctionGitHubPackage': {"synthetic_faas_function": []}}

    faasr_data['ComputeServers'][workflow.compute_server.name] = {}
    faasr_data['ComputeServers'][workflow.compute_server.name]['FaaSType'] = workflow.compute_server.faastype
    match (workflow.compute_server.faastype):
        case "GitHubActions":
            faasr_data['ComputeServers'][workflow.compute_server.name]['UserName'] = workflow.compute_server.username
            faasr_data['ComputeServers'][workflow.compute_server.name]['ActionRepoName'] = workflow.compute_server.action_repo_name
            faasr_data['ComputeServers'][workflow.compute_server.name]['Branch'] = workflow.compute_server.branch
        case "Lambda":
            faasr_data['ComputeServers'][workflow.compute_server.name]['Region'] = workflow.compute_server.region
        case "OpenWhisk":
            faasr_data['ComputeServers'][workflow.compute_server.name]['SSL'] = workflow.compute_server.ssl
            faasr_data['ComputeServers'][workflow.compute_server.name]['Namespace'] = workflow.compute_server.namespace
            faasr_data['ComputeServers'][workflow.compute_server.name]['Endpoint'] = workflow.compute_server.endpoint

    faasr_data['DataStores'][workflow.data_store] = {}
    faasr_data['DataStores'][workflow.data_store]['Endpoint'] = workflow.data_endpoint
    faasr_data['DataStores'][workflow.data_store]['Bucket'] = workflow.bucket
    faasr_data['DataStores'][workflow.data_store]['Region'] = workflow.region
    faasr_data['DataStores'][workflow.data_store]['Writable'] = workflow.writable

    for function in workflow.function_list:
        faasr_data['FunctionList'][function.name] = {'FunctionName': function.function_name, 'FaaSServer' : workflow.compute_server.name, 'Arguments' : {}, 'InvokeNext': []}
        faasr_data['FunctionList'][function.name]['Arguments']['execution_time'] = function.execution_time
        faasr_data['FunctionList'][function.name]['Arguments']['folder'] = workflow.files_folder
        faasr_data['FunctionList'][function.name]['Arguments']['input_files'] = function.input_files
        faasr_data['FunctionList'][function.name]['Arguments']['output_size_in_bytes'] = sum(workflow.files[file] for file in function.output_files)
        faasr_data['FunctionList'][function.name]['InvokeNext'] = function.invoke_next
        faasr_data['ActionContainers'][function.name] = function.action_container

    os.mkdir(output_name)
    outfile = open(f"{output_name}/{output_name}.json", "w")
    json.dump(faasr_data, outfile, indent=4)
    outfile.close()

    faasr_data_files = {'files' : {}}
    for file, size in workflow.files.items():
        faasr_data_files['files'][file] = size

    file_outfile = open(f"{output_name}/{output_name}_files.json", "w")
    json.dump(faasr_data_files, file_outfile, indent=4)
    file_outfile.close()



def create_file_of_size(file_path: str, size_in_bytes: int):
    """"
    Creates a file with a specified size
    :param_file_path: file path
    :param_size_in_bytes: number of bytes to set file to
    """
    newfile = open(file_path, "w")
    newfile.truncate(size_in_bytes)
    newfile.close()
    return newfile


def download_files_to_minio_from_obj(workflow: SyntheticFaaSrWorkflow, access_key: str, secret_key: str):
    """"
    Uploads files in a faasr workflow object to an S3 bucket
    :param_workflow: faasr workflow
    :param_access_key: S3 access key
    :param_secret_key: S3 secret key
    """
    client = Minio(endpoint=workflow.data_endpoint.replace("https://", "").replace("http://",""), access_key=access_key, secret_key=secret_key,)

    found = client.bucket_exists(workflow.bucket)
    if not found:
        client.make_bucket(workflow.bucket)

    if not os.path.exists("temp"):
        os.mkdir("temp")
    else:
        raise FileExistsError(f"Directory temp already exists.")


    for file, size in workflow.files.items():
        source_file = create_file_of_size("temp/" + file, size)
        destination = f"{workflow.files_folder}/{file}"
        client.fput_object(workflow.bucket, destination, "temp/" + file)
        os.remove("temp/" + file)

    os.rmdir("temp")
    print("Files downloaded to S3")

def download_files_to_minio_from_json(faasr_file_path: str, bucket_name: str, endpoint: str, access_key: str, secret_key: str, folder: str):
    """"
    Uploads files in a FaaSr file JSON to an S3 bucket
    :param_faasr_file_path: path to faasr file json
    :param_workflow: faasr workflow
    :param_bucket_name: S3 bucket name
    :param_folder: folder inside of S3 bucket to store data
    :param_endpoint: S3 endpoint
    :param_access_key: S3 access key
    :param_secret_key: S3 secret key
    """
    client = Minio(endpoint=endpoint.replace("https://", "").replace("http://",""), access_key=access_key, secret_key=secret_key)

    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)

    if not os.path.exists("temp"):
        os.mkdir("temp")
    else:
        raise FileExistsError(f"Directory temp already exists.")
    
    path = faasr_file_path
    if ".json" not in path:
        path += ".json"
    faasr_files = json.load(open(path, 'r'))
    for file, size in faasr_files['files'].items():
        source_file = create_file_of_size("temp/" + file, size)
        destination = f"{folder}/{file}"
        client.fput_object(bucket_name, destination, "temp/" + file)
        os.remove("temp/" + file)
    os.rmdir("temp")
    print("Files downloaded to S3")

def create_faasr_env_prompt(workflow: SyntheticFaaSrWorkflow, dir: str):
    """
    Creates a faasr_env from user input
    :param_workflow: FaaSr workflow object
    :param_dir: Directory that faasr_env will be written to
    """
    faasr_env = open(f"{dir}/faasr_env", "w")
    match workflow.compute_server.faastype:
        case "GitHubActions":
            print("Enter your github account token:")
            token = input()
            faasr_env.write(f'"My_GitHub_Account_TOKEN"="{token}"\n')
        case "OpenWhisk":
            print("Enter your OpenWhisk ID:")
            ow_id = input()
            print("Enter your OpenWhisk secret key:")
            ow_key = input()
            faasr_env.write(f'"My_OW_Account_API_KEY"="{ow_id}:{ow_key}"\n')
        case "Lambda":
            print("Enter your AWS Lambda acess key:")
            lambda_access_key = input()
            print("Enter your AWS Lambda secret key:")
            lambda_secret_key = input()
            faasr_env.write(f'"My_Lambda_Account_ACCESS_KEY"="{lambda_access_key}"\n')
            faasr_env.write(f'"My_Lambda_Account_SECRET_KEY"="{lambda_secret_key}"\n')
    print("Enter your MinIO access key:")
    minio_access_key = input()
    print("Enter your MinIO secret key:")
    minio_secret_key = input()
    faasr_env.write(f'"My_Minio_Bucket_ACCESS_KEY"="{minio_access_key}"\n')
    faasr_env.write(f'"My_Minio_Bucket_SECRET_KEY"="{minio_secret_key}"\n')
    print("faasr_env created")

def create_faasr_env_default(workflow: SyntheticFaaSrWorkflow, dir: str):
    """
    Creates a faasr_env from user input
    :param_workflow: FaaSr workflow object
    :param_dir: Directory that faasr_env will be written to
    """
    faasr_env = open(f"{dir}/faasr_env", "w")
    match workflow.compute_server.faastype:
        case "GitHubActions":
            faasr_env.write(f'"My_GitHub_Account_TOKEN"="REPLACE_WITH_YOUR_GITHUB_TOKEN"\n')
        case "OpenWhisk":
            faasr_env.write(f'"My_OW_Account_API_KEY"="REPLACE_WITH_YOUR_OPENWHISK_ID:SECRET_KEY"\n')
        case "Lambda":
            faasr_env.write(f'"My_Lambda_Account_ACCESS_KEY"="REPLACE_WITH_YOUR_AWS_LAMBDA_ACCESS_KEY"\n')
            faasr_env.write(f'"My_Lambda_Account_SECRET_KEY"="REPLACE_WITH_YOUR_AWS_LAMBDA_SECRET_KEY"\n')
    faasr_env.write(f'"My_Minio_Bucket_ACCESS_KEY"="Q3AM3UQ867SPQQA43P2F"\n')
    faasr_env.write(f'"My_Minio_Bucket_SECRET_KEY"="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG"\n')
    print("faasr_env created")