from minio import Minio
from workflow import *
import json
import os

def write_faasr_obj_to_json(workflow, output_name):
    """"
    Writes faasr workflow to a FaaSr JSON and FaaSr file JSON
    :param_workflow: workflow objec
    :param_output_name: output workflow name
    """
    start_function_name = workflow.start_function.name
    data_bucket = workflow.data_store
    faasr_data = {'ComputeServers' : {}, 'DataStores' : {}, 'FunctionList' : {}, 'ActionContainers' : {}, 'FunctionGitRepo' : workflow.function_git_repos, 'FunctionInvoke' : start_function_name, 'InvocationID' : '', 'FaaSrLog': 'FaaSrLog', 'LoggingDataStore': data_bucket, 'DefaultDataStore': data_bucket, 'FunctionCRANPackage': {"synthetic_faas_function": []}, 'FunctionGitHubPackage': {"synthetic_faas_function": []}}

    faasr_data['ComputeServers'][workflow.compute_server] = {}
    faasr_data['ComputeServers'][workflow.compute_server]['FaaSType'] = workflow.faas_type
    faasr_data['ComputeServers'][workflow.compute_server]['UserName'] = workflow.username
    faasr_data['ComputeServers'][workflow.compute_server]['ActionRepoName'] = workflow.action_repo_name
    faasr_data['ComputeServers'][workflow.compute_server]['Branch'] = workflow.branch

    faasr_data['DataStores'][workflow.data_store] = {}
    faasr_data['DataStores'][workflow.data_store]['Endpoint'] = workflow.data_endpoint
    faasr_data['DataStores'][workflow.data_store]['Bucket'] = workflow.bucket
    faasr_data['DataStores'][workflow.data_store]['Region'] = workflow.region
    faasr_data['DataStores'][workflow.data_store]['Writable'] = workflow.writable

    for function in workflow.function_list:
        faasr_data['FunctionList'][function.name] = {'FunctionName': function.function_name, 'FaaSServer' : workflow.compute_server, 'Arguments' : {}, 'InvokeNext': []}
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
    

def create_file_of_size(file_path, size_in_bytes):
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
        print("Created bucket", workflow.bucket)
    else:
        print("Bucket", workflow.bucket, "already exists")

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
        print("Created bucket", bucket_name)
    else:
        print("Bucket", bucket_name, "already exists")

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




