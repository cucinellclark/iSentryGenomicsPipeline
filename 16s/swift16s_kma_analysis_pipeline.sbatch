#!/bin/bash

#SBATCH -A isentry
#SBATCH -p bii

#SBATCH -o swift16_analysis.out
#SBATCH -e swift16_analysis.err

date
start_seconds=`date +%s`

program_dir="/project/biocomplexity/isentry/16s_analysis/swift16_kma_pipeline"
usearch=/home/awd5y/bin/usearch

fastq_dir=$1
for f in $fastq_dir/*fq $fastq_dir/*fastq
do
	b=${f##*/}_unique.fa
	$usearch -fastx_uniques $f -sizeout -relabel Uniq -fastaout $b -minuniquesize 4
	cat $b >> all_unique.fa
	rm $b
done
$usearch -sortbysize all_unique.fa -fastaout all_unique_sorted.fa 
rm all_unique.fa

#Make 97% OTUs and filter chimeras
$usearch -cluster_otus all_unique_sorted.fa -otus all_otu97.fa -relabel Otu
rm all_unique_sorted.fa

module load blast
db=/project/biocomplexity/isentry/ref_data/ncbi_16s_blast/16S_ribosomal_RNA

cmd="blastn -query all_otu97.fa -db $db -outfmt 6 -out all_otu97_vs_ncbi16s.bl6 -evalue 1e-20 -max_target_seqs 1"
echo $cmd
$cmd

cut -f 2 all_otu97_vs_ncbi16s.bl6 | sort | uniq > all_otu97_vs_ncbi16s.ids

cmd="blastdbcmd -db $db -entry_batch all_otu97_vs_ncbi16s.ids"
echo $cmd
$cmd > all_otu97_vs_ncbi16s.fa

# first index prior to dereplication
cmd="kma index -i all_otu97_vs_ncbi16s.fa -o kma_round1_index"
echo $cmd
$cmd

cmd="kma -t_db kma_round1_index -o kma_round1 -i $fastq_dir/*fq"
echo $cmd
$cmd

# calculate reduncancy in selected references
cmd="$usearch -cluster_fast all_otu97_vs_ncbi16s.fa -uc all_otu97_vs_ncbi16s.uc -id 0.96"
$cmd

# reject redundant sequences (at 0.97 similarity), favoring the better scoring of each redundant pair
cmd="perl $program_dir/dereplicate_references.pl all_otu97_vs_ncbi16s.uc kma_round1.res all_otu97_vs_ncbi16s.fa"
echo $cmd
$cmd  > dereplicated_representatives.fa

cmd="kma index -i dereplicated_representatives.fa -o kma_round2_index"
echo $cmd
$cmd

cmd="kma -t_db kma_round2_index -o kma_round2 -i $fastq_dir/*fq"
echo $cmd
$cmd

cmd="blastn -query kma_round2.fsa -db $db -outfmt 6 -out round2_references.bl6 -evalue 1e-20 -max_target_seqs 1"
echo $cmd
$cmd

cut -f 2 round2_references.bl6 | sort | uniq > round2_references.ids

cmd="blastdbcmd -db $db -entry_batch round2_references.ids"
echo $cmd
$cmd > round2_references.fa

# calculate reduncancy in round2 references
cmd="$usearch -cluster_fast round2_references.fa -uc round2_references.uc -id 0.97"
$cmd

# reject redundant sequences (at 0.97 similarity), favoring the better scoring of each redundant pair
cmd="perl $program_dir/dereplicate_references.pl round2_references.uc kma_round2.res round2_references.fa"
echo $cmd
$cmd  > round2_references_dereplicated.fa

# first index prior to dereplication
cmd="kma index -i round2_references_dereplicated.fa -o kma_round3_index"
echo $cmd
$cmd

cmd="kma -t_db kma_round3_index -o kma_round3 -i $fastq_dir/*fq"
echo $cmd
$cmd

cmd="perl $program_dir/tabulate_kma_counts.pl kma_round3.frag.gz"
echo $cmd
$cmd > kma_round3_counts.tsv

cmd="perl $program_dir/summarize_kma_results.pl kma_round3"
echo $cmd
$cmd > kma_round3_summary.tsv

date
end_seconds=`date +%s`
echo "elapsed seconds:"$(( $end_seconds - $start_seconds ))


