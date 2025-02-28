import argparse
from wfformat_reader import *
from workflow import *
from translator import *
from writer import *
from faasr_reader import *

""""
python3 convert.py [WfFormat JSON] [output file name]

This program does the following:
1. Initializes a WfFormatWorkflow using a WfFormat JSON
2. Initializes a SyntheticFaaSrWorkflow using the WfFormatWorkflow
3. Dumps the FaaSr workflow to a JSON file
4. Optionally downloads the files in the FaaSr workflow to S3
5. Optionally creates faasr_env for the workflow
"""

def prompt_y_or_n(prompt: str):
    """prompts user for 'y' or 'n' input and returns a boolean
    args:
        prompt(str): prompt message
    """
    print(prompt)
    response = input().lower()
    while response not in ('y', 'n'):
        print("Please input 'y' or 'n'")
        response = input().lower()
    if response == 'y':
        return True
    else:
        return False
    


def main():
    #parse args
    parser = argparse.ArgumentParser(description='reads wfformat json file and output name')
    parser.add_argument('data_file', help='JSON instance file')
    parser.add_argument('output_name', help='name for output file')
    args = parser.parse_args()
    data = json.loads(open(args.data_file).read())

    #create WfWorkflow
    wf_workflow = wfformat_to_workflow_obj(data)

    #create compute server
    print("""What FaaS provider do you want to use for this workflow? ["GH", "OW", or "Lambda"]""")
    faas_type = input().lower()
    while faas_type not in ("gh", "ow", "lambda"):
        print("Please input a valid FaaS provider")
        faas_type = input().lower() 

    #prompt for FaaS credentials
    default_faas = prompt_y_or_n("Would you like to use the default compute server configuration? (y/n)")

    match faas_type:
        case "gh":
            print('GH')
            if default_faas:
                compute_server = GH_ComputeServer(name="My_GitHub_Account", faastype="GitHubActions", username="YOUR_GITHUB_USERNAME", action_repo_name="faasr-synthetic-example", branch="main")
            else:
                print("Enter your github username:")
                username = input()
                print("Enter your action repo name:")
                action_repo_name = input()
                print("Enter branch name:")
                branch = input()
                compute_server = GH_ComputeServer(name="My_GitHub_Account", faastype="GitHubActions", username=username, action_repo_name=action_repo_name, branch=branch)
        case 'ow':
            if default_faas:
                compute_server = OW_ComputeServer(name="My_OW_Account", faastype="OpenWhisk", namespace="YOUR_OW_USERNAME", endpoint="YOUR_OW_ENDPOINT")
            else:
                print("Please enter your OpenWhisk namespace:")
                namespace = input()
                print("Please open your OpenWhisk endpoint:")
                endpoint = input()
                compute_server = OW_ComputeServer(name="My_OW_Account", faastype="OpenWhisk", namespace=namespace, endpoint=endpoint)
        case "lambda":
            if default_faas:
                compute_server = Lambda_ComputeServer(name="My_Lambda_Account", faastype="Lambda", region="us-east-1")
            else:
                print("Please enter AWS Lambda region:")
                region = input()
                compute_server = Lambda_ComputeServer(name="My_Lambda_Account", faastype="Lambda", region=region)
    
    #Display workflow data
    print(wf_workflow)


    #Create SyntheticFaaSrWorkflow from WfWorkflow
    faasr_workflow = translate_wf_to_faasr_gh(workflow=wf_workflow, compute_server=compute_server)

    #Display FaaSr workflow
    print(faasr_workflow)

    #Dumps FaaSr workflow to JSON
    write_faasr_obj_to_json(faasr_workflow, args.output_name)

    #Downloads files from FaaSr workflow to S3
    print("Downloading files to S3...\nAccess Key: Q3AM3UQ867SPQQA43P2F Secret Key: zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG")
    download_files_to_minio_from_obj(faasr_workflow, access_key="Q3AM3UQ867SPQQA43P2F", secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG")

    #Generate faasr_env if user wants
    create_faasr_env = prompt_y_or_n("Would you like to create a faasr_env for this workflow? (y/n)")
    if create_faasr_env:
        faasr_default = prompt_y_or_n("Would you like to use the default credentials? (y/n)")
        if faasr_default:
            create_faasr_env_default(faasr_workflow, f"{args.output_name}")
        else:
            create_faasr_env_prompt(faasr_workflow, f"{args.output_name}")           


    exit(1)


if __name__ == "__main__":
    main()
