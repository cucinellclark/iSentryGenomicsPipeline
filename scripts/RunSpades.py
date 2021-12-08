#!/home/cc8dm/miniconda3/bin/python

import sys,subprocess,argparse,os,shutil,glob

parser = argparse.ArgumentParser()
parser.add_argument('-t','--threads',default="1")
parser.add_argument('-r','--reads',help="either one read or comma separated reads: read1,read2 or read1",required=True)
parser.add_argument('-o','--outdir',default="Contigs")
parser.add_argument('-s','--spades_output',default="tmp_spades")
parser.add_argument('-p','--prefix',required=True)
parser.add_argument('-m',"--metagenomic",action="store_true")
parser.add_argument('-c',"--single_cell",action="store_true")

args = parser.parse_args()

args.reads = args.reads.split(",")
if len(args.reads) > 2 or len(args.reads) == 0:
    print("error, maximum of two reads  and minimum of one allowed")
if len(args.reads) == 2:
    reads_params = ["-1",args.reads[0],"-2",args.reads[1]] 
else:
    reads_params = ["-s",args.reads[0]]

contigs_file = os.path.join(args.spades_output,"contigs.fasta")
first_run = True
while not os.path.exists(contigs_file): 
    if first_run:
        spades_cmd = ["spades.py"]+reads_params+["-t",args.threads,"-o",args.spades_output]
        if args.metagenomic:
            spades_cmd.insert(1,"--meta")
        if args.single_cell:
            spades.cmd.insert(1,"--sc")
        first_run = False
        print(spades_cmd)
        subprocess.check_call(spades_cmd)
    else: #assumes spades failed, check for existence of the kmer directories
        kmer_path = os.path.join(args.spades_output,"k*")
        kmer_list = []
        for kmer_dir in glob.glob(kmer_path):
            kmer_val = int(os.path.basename(kmder_dir).replace("k","")) 
            kmer_list.append(kmer_val)
        if len(kmer_list) == 0:
            print("No existing Kmer directories, consult log file")
            sys.exit(-1)
        #get the sorted kmer list and omit the last element, assumes that the error occurred in the last kmer
        kmers_sorted = sorted(kmer_list)[:-1]
        kmers_sorted = [str(k) for k in kmers_sorted]
        #Restart spades at the last completed kmer and limit kmer processing
        last_kmer = "k"+kmers_sorted[-1]
        kmer_param = ",".join(kmers_sorted)
        spades_cmd = ["spades.py","-k",kmer_param,"--restart-from",last_kmer,"-o",args.spades_output]
        if args.metagenomic:
            spades_cmd.insert(1,"--meta")
        if args.single_cell:
            spades.cmd.insert(1,"--sc")
        print(spades_cmd)
        subprocess.check_call(spades_cmd)
#move contigs file to output file with prefix name 
if os.path.exists(contigs_file):
    contigs_output = os.path.join(args.outdir,args.prefix+".fa")
    py_v3 = 0x30000f0
    print(contigs_file)
    print(contigs_output)
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)
    if sys.hexversion < py_v3: #python version 2
        os.rename(contigs_file,contigs_output)
    else: #python version 3
        os.replace(contigs_file,contigs_output)
    if os.path.exists(contigs_output):
        shutil.rmtree(args.spades_output)
    else:
        print("error in moving output file")
else:
    print("contigs.fasta does not exist")
