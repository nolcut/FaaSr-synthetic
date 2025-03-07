#!/usr/bin/env python3
import argparse
from wfformat_reader import *
from workflow import *
from translator import *
from writer import *


"""
python3 download_faasr_files.py [faasr files json]

This program downloads the files specificed in a faasr files json to a minio bucket in S3 that can be viewed here: https://play.min.io:9443
Use these credentials:
Username: Q3AM3UQ867SPQQA43P2F
Password: zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG
"""



def main():
    #parse arguments
    parser = argparse.ArgumentParser(description='read faasr file json')
    parser.add_argument('faasr_files', help='faasr file information')
    args = parser.parse_args()
    
    #download files to S3
    download_files_to_minio_from_json(args.faasr_files, bucket_name='faasr', endpoint='https://play.min.io', access_key="Q3AM3UQ867SPQQA43P2F", secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG", folder="synthetic_files")



if __name__ == "__main__":
    main()
