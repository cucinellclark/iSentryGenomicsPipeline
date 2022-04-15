#!/home/cc8dm/miniconda3/bin/python

import os,json,shutil,subprocess,sys,argparse,time,glob,re

###import other scripts
sys.path.insert(0,"scripts")

###NOTE: dependencies
# - trim_galore (dependencies are fastqc and cutadapt)
# - kraken2 (gcc dependent)
# - mash
# - maxbin (perl dependent)
# - spades
# - diamond

def run_trimgalore(path_dict,read_list,threads):
    trim_cmd = ["trim_galore","--cores",threads,"--output_dir",path_dict["reads_output"]]
    paired_flag = False
    if len(read_list) == 2:
        trim_cmd = trim_cmd + ["--paired",read_list[0],read_list[1]]
        paired_flag = True
    else:
        trim_cmd = trim_cmd + [read_list[0]]
    try:
        if False:
            print(" ".join(trim_cmd))
            subprocess.check_call(trim_cmd)
        sample_files = []
        for f in glob.glob(path_dict["reads_output"]+"/*"):
            sample_files.append(f)
        for f in sample_files:
            if paired_flag:
                if "_val_1.fq" in f:
                    path_dict["read1"] = f
                if "_val_2.fq" in f:
                    path_dict["read2"] = f
            else:
                if "_trimmed.fq" in f:
                    path_dict["read1"] = f

    except Exception as e:
        print("error: \n {0}".format(e))
        return False
    return True 

def run_mash(genome_type,seq_file,mash_prefix,threads):
    mash_database = "/project/biocomplexity/isentry/ref_data/mash/patric_all.msh"
    if False:
        if genome_type == "isolate": #mash dist
            mash_cmd = ["python","scripts/Run_MashDist.py","-t",threads,"-d",mash_database,"-f",seq_file,"-s",mash_prefix]
            print(" ".join(mash_cmd))
            subprocess.check_call(mash_cmd)
        elif genome_type == "metagenomic": #mash screen
            mash_cmd = ["python","scripts/Run_MashScreen.py","-t",threads,"-d",mash_database,"-f",seq_file,"-s",mash_prefix]
            print(" ".join(mash_cmd))
            subprocess.check_call(mash_cmd)
        else:
            sys.exit() #not a valid option

def run_kraken(seq_file,kraken_reads_prefix,threads):
    kraken_read_log_stdout = kraken_reads_prefix+".stdout"
    kraken_read_log_stderr = kraken_reads_prefix+".stderr"
    if False:
        with open(kraken_read_log_stdout,"w") as klo, open(kraken_read_log_stderr,"w") as kle:
            kraken_cmd = ["python","scripts/RunKraken.py","-t",threads,"-p",kraken_reads_prefix,"-r",seq_file]
            print(" ".join(kraken_cmd))
            subprocess.check_call(kraken_cmd,stdout=klo,stderr=kle)

def run_spades(genome_type,path_dict,threads):
    try:
        print("Running SPAdes")
        spades_cmd = ["python","scripts/RunSpades.py","-t",threads]
        if "read2" in path_dict:
            spades_cmd+=["-r",path_dict["read1"]+","+path_dict["read2"]]
        else:
            spades_cmd+=["-r",path_dict["read1"]]
        spades_cmd+=["-o",path_dict["spades_output"],"-p",os.path.basename(path_dict["read1"]).split(".")[0]]
        spades_cmd+=["-s",os.path.join(path_dict["output_dir"],"tmp_spades")]
        if genome_type == "metagenomic":
            spades_cmd+=["-m"]
        spades_stdout = os.path.join(path_dict["output_dir"],"spades.stdout")
        spades_stderr = os.path.join(path_dict["output_dir"],"spades.stderr")
        if False:
            print(" ".join(spades_cmd))
            with open(spades_stdout,"w") as so, open(spades_stderr,"w") as se:
                subprocess.check_call(spades_cmd,stdout=so,stderr=se)
        path_dict["contigs"] = os.path.join(path_dict["spades_output"],os.path.basename(path_dict["read1"]).split(".")[0]+".fa")
        if not os.path.exists(path_dict["contigs"]):
            print("Error: contigs file does not exist")
            sys.exit(-1)
        return True
    except Exception as e:
        print("error running SPAdes: \n{0}".format(e))
        sys.exit(-1)

def run_checkm(contigs_dir,output_file,output_dir,threads,suffix):
    checkm_cmd = ["checkm","taxonomy_wf","-t",threads,"-f",output_file,"-x",suffix,"--individual_markers","domain","Bacteria",contigs_dir,output_dir]
    if False:
        print(" ".join(checkm_cmd))
        subprocess.check_call(checkm_cmd)

def run_maxbin(path_dict,contig_file,prefix,threads):
    maxbin_cmd = ["python","scripts/Run_Maxbin.py","-r1",path_dict["read1"]]
    if "read2" in path_dict:
        maxbin_cmd+=["-r2",path_dict["read2"]]
    maxbin_cmd+=["-c",contig_file,"-p",prefix,"-t",threads]
    if False:
        print(" ".join(maxbin_cmd))
        subprocess.check_call(maxbin_cmd)
    path_dict["bin_list"] = [] 
    for fasta in glob.glob(os.path.join(path_dict["maxbin_output"],"*fasta")):
        path_dict["bin_list"].append(fasta)

def run_diamond(seq_file,prefix,threads):
    #diamond against vfdb
    vfdbDB="/project/biocomplexity/isentry/ref_data/vfdb/VFDB_setB_pro.dmnd"
    blast_cmd = ["scripts/Run_Diamond.py","-t",threads,"-f",seq_file,"-d",vfdbDB,"-p",prefix]
    if False:
        print(" ".join(blast_cmd))
        subprocess.check_call(blast_cmd)
    #get blast results file

def run_pathogenicity_profile(blast_list,prefix):
    #run patho scoring script
    #python scripts/scoreGenomeByVfdbLogodds.py testing_paired_meta/spades_output/SRR17068071_1_val_1_contigs_pp.diamond.out
    patho_cmd = ["python","scripts/scoreGenomeByVfdbLogodds.py"] + blast_list
    patho_stdout = prefix+"_patho_profile.stdout"
    patho_stderr = prefix+"_patho_profile.stderr"
    with open(patho_stdout,"w") as stdout,open(patho_stderr,"w") as stderr:
        print(" ".join(patho_cmd))
        subprocess.check_call(patho_cmd,stdout=stdout,stderr=stderr)

def setup(output_dir,genome_type):

    path_dict = {}

    ###setup output paths
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    path_dict["output_dir"] = os.path.abspath(output_dir)
    path_dict["reads_output"] = os.path.join(path_dict["output_dir"],"reads_output")
    if not os.path.exists(path_dict["reads_output"]):
        os.mkdir(path_dict["reads_output"])
    #TODO: change spades output to contigs output
    path_dict["spades_output"] = os.path.join(path_dict["output_dir"],"spades_output")
    if not os.path.exists(path_dict["spades_output"]):
        os.mkdir(path_dict["spades_output"])

    if genome_type == "metagenomic":
        path_dict["maxbin_output"] = os.path.join(path_dict["output_dir"],"maxbin_output")
        if not os.path.exists(path_dict["maxbin_output"]):
            os.mkdir(path_dict["maxbin_output"])
        path_dict["bins_output"] = os.path.join(path_dict["output_dir"],"bins_output")
        if not os.path.exists(path_dict["bins_output"]):
            os.mkdir(path_dict["bins_output"])

    return path_dict 

def main(genome_type,output_dir,file_prefix,read_list,threads):
    
    print("Running WGS pipeline with parameters:\n {0} {1} {2} {3} {4}".format(genome_type,output_dir,file_prefix,read_list,threads))

    path_dict = setup(output_dir,genome_type)

    ###trim_galore
    print("trim_galore")
    run_trimgalore(path_dict,read_list,threads)

    ###Reads: mash on read1
    mash_prefix = os.path.join(path_dict["reads_output"],os.path.basename(path_dict["read1"]).split(".")[0])
    print("mash_reads")
    run_mash(genome_type,path_dict["read1"],mash_prefix,threads)

    ###kraken
    kraken_reads_prefix = os.path.join(path_dict["reads_output"],os.path.basename(path_dict["read1"]).split(".")[0]+"_reads_kraken")
    print("kraken_reads")
    run_kraken(path_dict["read1"],kraken_reads_prefix,threads)

    ###TODO: forgot how to run pathogenicity profile, do I need to diamond blastx first?
    #reads_patho_profile_output = os.path.join(path_dict["reads_output"],os.path.basename(path_dict["read1"]).split(".")[0]+"_reads_patho_profile.txt")

    ###assembly
    print("spades")
    run_spades(genome_type,path_dict,threads)

    ###mash on contigs
    mash_contigs_prefix = os.path.join(path_dict["spades_output"],os.path.basename(path_dict["contigs"]).split(".")[0])
    print("mash_contigs")
    run_mash(genome_type,path_dict["contigs"],mash_prefix,threads)

    ###kraken on contigs
    kraken_contigs_prefix = os.path.join(path_dict["spades_output"],os.path.basename(path_dict["contigs"]).split(".")[0]+"_contigs_kraken")
    print("kraken_contigs")
    run_kraken(path_dict["contigs"],kraken_contigs_prefix,threads)

    ###patho profile on contigs
    diamond_contigs_prefix = os.path.join(path_dict["spades_output"],os.path.basename(path_dict["contigs"]).split(".")[0]+"_contigs_pp")
    print("patho_contigs")
    run_diamond(path_dict["contigs"],diamond_contigs_prefix,threads)
    path_dict["contigs_vfdb"] = diamond_contigs_prefix+".diamond.out"
    print(path_dict["contigs_vfdb"])
    patho_contigs_prefix = os.path.join(os.path.dirname(diamond_contigs_prefix),os.path.basename(diamond_contigs_prefix)+"_results")
    run_pathogenicity_profile([path_dict["contigs_vfdb"]],patho_contigs_prefix)

    ###Run checkm on contigs
    print("checkm_contigs")
    run_checkm(path_dict["spades_output"],os.path.join(path_dict["output_dir"],"contigs_quality_checkm.txt"),os.path.join(path_dict["output_dir"],"Checkm_Results"),threads,"fa")

    ###If metagenomic, rerun on contig bins
    if genome_type == "metagenomic":

        ###maxbin
        maxbin_prefix = os.path.join(path_dict["maxbin_output"],os.path.basename(path_dict["read1"]).split(".")[0])
        print("maxbin")
        run_maxbin(path_dict,path_dict["contigs"],maxbin_prefix,threads)
    
        ###mash on bins
        print("mash_bins")
        for b in path_dict["bin_list"]:
            mash_bin_prefix = os.path.join(path_dict["bins_output"],"_".join(os.path.basename(b).split(".")[0:2]))
            run_mash("isolate",b,mash_bin_prefix,threads)

        ###kraken on bins
        print("kraken_bins")
        for b in path_dict["bin_list"]:
            kraken_bin_prefix = os.path.join(path_dict["bins_output"],"_".join(os.path.basename(b).split(".")[0:2])+"_bin_kraken")
            run_kraken(b,kraken_bin_prefix,threads)

        ###checkm on bins
        run_checkm(path_dict["maxbin_output"],os.path.join(path_dict["bins_output"],"bins_quality_checkm.txt"),os.path.join(path_dict["bins_output"],"Checkm_Results"),threads,"fasta")

        ###pathogenicity profile on bins
        for b in path_dict["bin_list"]:
            diamond_bin_prefix = os.path.join(path_dict["bins_output"],"_".join(os.path.basename(b).split(".")[0:2])+"_bin_pp")
            run_diamond(b,diamond_bin_prefix,threads)
            diamond_bin_output = diamond_bin_prefix+".diamond.out" 
            patho_bin_prefix = os.path.join(os.path.dirname(diamond_bin_prefix),os.path.basename(diamond_bin_prefix)+"_results")
            run_pathogenicity_profile([b],patho_bin_prefix)

    return True 

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    ###genome type: isolate, metagenomic, or droplet (not sure how droplet will change it yet)
    parser.add_argument("-m","--metagenomic",action="store_true",help="run in metagenomic mode: default",required=False)
    parser.add_argument("-i","--isolate",action="store_true",help="run in isolate mode",required=False)
    #parser.add_argument("-d","--droplet",action="store_true",help="run in droplet mode",required=False)

    ###directories and sample name parameters
    parser.add_argument("-o","--outdir",help="top-level output directory",default="iSentry_Output",required=False)
    parser.add_argument("-p","--prefix",help="name of the sample, used as a prefix for filenames",default="isentry_sample",required=False)

    ###reads parameters
    parser.add_argument("-1","--read1",help="first read file: must be fastq",required=True)
    parser.add_argument("-2","--read2",help="second read file: must be fastq",required=False,default=None)

    ###additional parameters
    parser.add_argument("-t","--threads",default="1",help="number of threads to use",required=False)

    args = parser.parse_args()

    ###From parameters, setup function call to main()
    genome_type = "metagenomic" if args.metagenomic else "isolate"
    read_list = []
    read_list.append(args.read1)
    if args.read2:
        read_list.append(args.read2)
    output_dir = args.outdir
    file_prefix = args.prefix
    threads = args.threads
    main(genome_type,output_dir,file_prefix,read_list,threads)
    
    
