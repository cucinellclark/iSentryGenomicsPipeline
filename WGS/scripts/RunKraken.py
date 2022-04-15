#!/home/cc8dm/miniconda3/bin/python

import os,shutil,subprocess,sys,argparse,time

parser = argparse.ArgumentParser()
parser.add_argument("-t","--threads",default="1")
parser.add_argument("-p","--prefix",required=True)
parser.add_argument("-r","--read",required=True)

args = parser.parse_args()

bacteriaDB="/project/biocomplexity/isentry/ref_data/kraken2/bacteria"
rdpDB="/project/biocomplexity/isentry/ref_data/kraken2/rdp/"
ggDB="/project/biocomplexity/isentry/ref_data/kraken2/greengenes/"
silvaDB="/project/biocomplexity/isentry/ref_data/kraken2/silva/"

#bacteria
bacteria_output = args.prefix+".bacteria.output"
bacteria_report = args.prefix+".bacteria.report"
kraken_cmd = ["kraken2","--db",bacteriaDB,"--threads",args.threads,args.read,"--output",bacteria_output,"--report",bacteria_report]
print(" ".join(kraken_cmd))
subprocess.check_call(kraken_cmd)
