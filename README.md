# Translator
This project provides tools to translate [WfFormat](https://wfcommons.org/) workflows into synthetic [FaaSr](https://faasr.io/) workflows containing two JSON files: 
* a FaaSr JSON, following the FaaSr schema
* a workflow file JSON, which specifies file names and sizes

## convert.py
Converts a WfFormat JSON to a FaaSr workflow and downloads the truncated files to S3

<pre><code>python3 convert.py [WfFormat JSON] [FaaSr workflow name]</code></pre>

To explore the console of the default S3 bucket that this program downloads the files to, go to https://play.min.io:9443, and log in using these credentials:
<pre><code>Username: Q3AM3UQ867SPQQA43P2F
Password: zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG</code></pre>

The files will be downloaded to a bucket called 'faasr'

<img width="738" alt="image" src="https://github.com/user-attachments/assets/98b690aa-55b8-40b5-83b4-3206f086db83" />

## download_faasr_files.py
Downloads the files specified in a FaaSr file JSON to S3

<pre><code>python3 download_faasr_files.py [FaaSr file JSON]</code></pre>

To view the download files, go to the same console as above and look for the faasr bucket


# Dependencies
* Minio

To install Minio, run the following command in your terminal:
<pre><code>pip3 install minio</code></pre>

# test
small_workflow_gh, small_workflow_ow, and small_workflow_lambda are FaaSr workflows that were translated from the WfInstance, 'blast-chameleon-small-004.json'

note: In order to run any of these examples, you must download their files to S3 with download_faasr_files.py

# To-do
- Make GUI to upload WfFormat files, take S3/FaaS credentials, and download FaaSr workflow's files to S3
- [x] Support for OW (tested)
- Lambda testing
- Create a tool for assigning compute servers to actions
- Support for multiple compute servers and data stores
- Method for setting compute service of task

<img width="828" alt="Screenshot 2025-02-24 at 6 13 16 PM" src="https://github.com/user-attachments/assets/3a758176-2479-4456-a547-d73632c9dcf3" />

# Future Additions
* Compile synthetic FaaSr workflows into WRENCH simulations



