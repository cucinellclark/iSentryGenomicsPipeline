#!/home/cc8dm/miniconda3/bin/python

import os,shutil,subprocess,sys,argparse,time

parser = argparse.ArgumentParser()
parser.add_argument("-t","--threads",default="1")
parser.add_argument("-f","--file",required=True)
parser.add_argument("-d","--database",required=True)
parser.add_argument("-p","--prefix",required=True)
parser.add_argument("-e","--evalue",default="0.000001")
        
args = parser.parse_args()

dmndHeaders=["qseqid","sseqid","length","evalue","bitscore","stitle"]

dmnd_out = args.prefix+".diamond.out"
dmnd_err = args.prefix+".diamond.err"
dmnd_cmd = ["diamond","blastx","--outfmt","6"]+dmndHeaders+["--db",args.database,"--evalue",args.evalue,"--query",args.file]
print(" ".join(dmnd_cmd))
with open(dmnd_out,"w") as do, open(dmnd_err,"w") as de:
    subprocess.check_call(dmnd_cmd,stdout=do,stderr=de)
