#!/home/cc8dm/miniconda3/bin/python

import sys
import subprocess
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-t','--threads',default="1")
parser.add_argument('-d','--database')
parser.add_argument('-f','--filename')
parser.add_argument('-s','--sample_id')

args = parser.parse_args()

outfile = args.sample_id+".mash_dist.out"
errfile = args.sample_id+".mash_dist.err"

threshold_list = [0.0,0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
threshold_index = 0

#Continue through while loop if the file doesn't exist or if Mash doesn't output with the current threshold
while not os.path.isfile(outfile) or os.path.getsize(outfile) == 0 and os.path.getsize(errfile) == 0:
    mash_threshold = threshold_list[threshold_index]
    print("Running Mash Dist at threshold {0}".format(str(mash_threshold)))
    command = "mash dist -d " + str(mash_threshold) + " -p " + args.threads + " " + args.database + " " + args.filename  

    with open(outfile,"w") as out, open(errfile,"w") as err:
        process = subprocess.Popen(command,shell=True,stdout=out,stderr=err)
        process.wait()

    if os.path.getsize(outfile) == 0:
        threshold_index = threshold_index + 1
