#!/usr/bin/python

import sys
import re

""" read logodds file for all virulence factors (last field is logodds)
Then read multiple blastx files for multiple genomes, summing logodds for each matching VF (second space-separated field of 6th tab-seqarated field)
Write out filename and score
"""
reference_log_odds_file = "/scratch/cc8dm/iSentry_scripts/IVV_Pipeline/PathogenicityProfile/ffvf_means_logodds.txt"
lodata={}
F = open(reference_log_odds_file)
F.readline() # header
for line in F:
	(gene, freq1, freq2, logodds) = line.rstrip().split("\t")
	lodata[gene] = float(logodds)

for f in sys.argv[1:]:
	genome = f
	m = re.search(r"(\d+\.\d+)", f)
	if m:
		genome = m.group(1)
	sys.stderr.write(genome+"\n")
	F = open(f)
	genome_score = 0
	for line in F:
		fields = line.split("\t")
		if len(fields) < 6:
			continue
		subfields = fields[5].split(" ")
		if len(subfields) < 2:
			continue
		gene = subfields[1].strip("()")
		if gene in lodata:
			#print "found ", gene, " lo = ", lodata[gene]
			genome_score += lodata[gene]
	sys.stdout.write(genome + "\t%.3f\n"%genome_score)



"""
==> ffvf_means_logodds.txt <==
Foe	Friend	logodds
irtB	4.5210389021209	5.81954371878978	-0.252475111565807
rtxB	4.93716683679256	6.06501517673553	-0.205741626424912
irp6C	0.684019507769082	1.1099578967982	-0.484034830902171

==> ref_rep_vs_vfdb/312309.11_vfdb.blastx <==
NC_006841	VFG007277(gi:59713515)	711	0.0e+00	1387.9	VFG007277(gi:59713515) (hutR) hemin receptor [Heme receptors (CVF278)] [Vibrio fischeri ES114]
NC_006841	VFG006872(gi:59714051)	497	9.6e-289	999.2	VFG006872(gi:59714051) (tcpT) TcpT, toxin co-regulated pilus biosynthesis protein [Toxin-coregulated pilus (type IVB pilus) (CVF256)] [Vibrio fischeri ES114]
NC_006841	VFG006861(gi:59714055)	484	4.2e-260	904.0	VFG006861(gi:59714055) (tcpC) TcpC, toxin co-regulated pilus biosynthesis outer membrane protein [Toxin-coregulated pilus (type IVB pilus) (CVF256)] [Vibrio fischeri ES114]
NC_006841	VFG006855(gi:59714057)	445	3.3e-257	894.4	VFG006855(gi:59714057) (tcpB) TcpB, toxin co-regulated pilus biosynthesis protein [Toxin-coregulated pilus (type IVB pilus) (CVF256)] [Vibrio fischeri ES114]
"""
