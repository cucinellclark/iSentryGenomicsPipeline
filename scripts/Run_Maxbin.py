#!/home/cc8dm/miniconda3/bin/python

import os,shutil,subprocess,sys,argparse,time

parser = argparse.ArgumentParser()
parser.add_argument("-t","--threads",default="1")
parser.add_argument("-r1","--read1",required=True,help="Forward reads file")
parser.add_argument("-r2","--read2",required=False,help="Reverse reads file")
parser.add_argument("-c","--contig",required=True,help="Contig file")
parser.add_argument("-p","--prefix",required=True)

args = parser.parse_args()

maxbin="/project/biocomplexity/isentry/src/MaxBin-2.2.7/run_MaxBin.pl"

maxbin_stdout = args.prefix+".maxbin.stdout"
maxbin_stderr = args.prefix+".maxbin.stderr"
maxbin_cmd = [maxbin,"-thread",args.threads,"-contig",args.contig,"-reads",args.read1]
if args.read2:
    maxbin_cmd+=["-reads2",args.read2]
maxbin_cmd+=["-out",args.prefix]
print(" ".join(maxbin_cmd))
with open(maxbin_stdout,"w") as mo, open(maxbin_stderr,"w") as me:
    subprocess.check_call(maxbin_cmd,stdout=mo,stderr=me)
