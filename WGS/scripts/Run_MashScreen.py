#!/home/cc8dm/miniconda3/bin/python

import sys
import subprocess
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-t','--threads',default="1")
parser.add_argument('-d','--database')
parser.add_argument('-f','--filename')
parser.add_argument('-s','--sample')

args = parser.parse_args()

outfile = args.sample+".mash_screen.out"
errfile = args.sample+".mash_screen.err"

p_val_threshold = 0.05

#Construct Mash Screen command from input arguments
command = ["mash","screen","-w","-p",args.threads,"-v",str(p_val_threshold),args.database,args.filename]  

#Open output file and error file for writing and run Mash Screen
print(" ".join(command))
with open(outfile,"w") as out, open(errfile,"w") as err:
    process = subprocess.check_call(command,stdout=out,stderr=err)
    #process.wait()

#Check if a problem occurred and the run failed
if not os.path.exists(outfile) or os.path.getsize(outfile) == 0: 
    with open(errfile,"a+") as err:
        err.write("Error occured and Mash Screen did not finish successfully: check log or error files\n")
    sys.exit(1)
else:
    sys.exit(0)
