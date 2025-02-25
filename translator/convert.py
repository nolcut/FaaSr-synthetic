import argparse
from wfformat_reader import *
from workflow import *
from translator import *
from write_faasr_json import *
from faasr_reader import *


""""
python3 convert.py [WfFormat JSON] [output file name]

This program does the following:
1. Initializes a WfFormatWorkflow using a WfFormat JSON, 
2. Initializes a SyntheticFaaSrWorkflow using the WfFormatWorkflow
3. Dumps the FaaSr workflow to a JSON file
4. Downloads the files in the FaaSr workflow to S3
"""

def main():
    #parse args
    parser = argparse.ArgumentParser(description='reads wfformat json file and output name')
    parser.add_argument('data_file', help='JSON instance file')
    parser.add_argument('output_name', help='name for output file')
    args = parser.parse_args()
    data = json.loads(open(args.data_file).read())

    #create WfWorkflow
    wf_workflow = wfformat_to_workflow_obj(data)

    #Display workflow data
    print(wf_workflow)

    #Create SyntheticFaaSrWorkflow from WfWorkflow
    faasr_workflow = translate_wf_to_faasr_gh(workflow=wf_workflow, compute_server="My_GitHub_Account", data_store="My_Minio_Bucket")

    #Display FaaSr workflow
    print(faasr_workflow)

    #Dumps FaaSr workflow to JSON
    write_faasr_obj_to_json(faasr_workflow, args.output_name)

    #Creates a FaaSr workflow object from the JSON we just dumped
    new_faasr_workflow = faasr_json_to_workflow_obj(faasr_json=f"{args.output_name}/{args.output_name}.json", faasr_file_json=f"{args.output_name}/{args.output_name}_files.json")

    #Prints whether or not the JSON matches the FaaSr workflow object
    if new_faasr_workflow.__str__() == faasr_workflow.__str__():
        print("JSON successfully saved")
    else:
        print("FaaSr JSON may be corrupted")

    #Downloads files from FaaSr workflow to S3
    download_files_to_minio_from_obj(faasr_workflow, access_key="Q3AM3UQ867SPQQA43P2F", secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG")

    exit(1)


if __name__ == "__main__":
    main()
