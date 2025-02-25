# Translator
[WfFormat](https://wfcommons.org/) workflows can be translated into synthetic [FaaSr](https://faasr.io/) workflows containing two JSON files: a FaaSr JSON (that follows the FaaSr schema) and a FaaSr file JSON (that specifes file names and sizes for I/O replication)

## convert.py
This program converts a WfFormat JSON to a FaaSr workflow and downloads the truncated files to S3

<pre><code>python3 convert.py [WfFormat JSON] [FaaSr workflow name]</code></pre>

To explore the console of the S3 bucket that this program downloads the files to, go to https://play.min.io:9443, and log in using these credentials:
<pre><code>Username: Q3AM3UQ867SPQQA43P2F
Password: zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG</code></pre>

The files will be downloaded to a bucket called 'faasr'

## download_faasr_files.py
This program downloads the files specified in a FaaSr file JSON to S3

<pre><code>python3 download_faasr_files.py [FaaSr file JSON]</code></pre>

To view the download files, go to the same console as above and look for the faasr bucket


# test
small_workflow is a FaaSr workflow that was translated from the WfInstance, 'blast-chameleon-small-004.json'

In order to run the workflow, you must download it's files to S3 with download_faasr_files.py

# To-do
* Make GUI to upload WfFormat files, take S3/FaaS credentials, and download FaaSr workflow's files to S3
* Support for AWS and OW
* Create a tool for assigning compute servers to actions
* Support for multiple compute servers and data stores
<img width="828" alt="Screenshot 2025-02-24 at 6 13 16 PM" src="https://github.com/user-attachments/assets/3a758176-2479-4456-a547-d73632c9dcf3" />

# Future Additions
* Compile synthetic FaaSr workflows into WRENCH simulations



