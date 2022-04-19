use strict;

my ($uc_file, $res_file, $fasta_file) = @ARGV;
print STDERR "uc_file = $uc_file";

#read fasta file to memory
open F, $fasta_file or die "can't open $fasta_file";
my %seq;
my $id;
while (<F>) {
	chomp;
	if (/>(.*\S)/) {
		$id = $1;
	}
	else {
		$seq{$id} .= $_;
	}
}

#read score of each sequence
open F, $res_file;
my %score;
while (<F>) {
	my ($id, $score) = split("\t");
	$score{$id} = $score;
}

# read redundancy file, eliminate lower scoring redundant seq
open F, $uc_file;
while (<F>) {
	chomp;
	my @fields = split("\t");
	my $id1 = $fields[8];
	my $id2 = $fields[9];
	next unless exists $score{$id1};
	next unless exists $score{$id2};
	next if $id2 eq '*';
	die "id1 $id1 not found in seqs" unless exists $seq{$id1};
	my $score1 = $score{$id1};
	die "id2 $id2 not found in seqs" unless exists $seq{$id2};
	my $score2 = $score{$id2};
	if ($score2 < $score1) {
		$score{$id2} = 0;
		print STDERR ("Suppressing $id2\n");
	}
	else {
		$score{$id1} = 0;
		print STDERR ("Suppressing $id1\n");
	}
}

my @ids = sort {$score{$b} <=> $score{$a}} keys %score;
for my $id (@ids) {
	last unless $score{$id};
	print STDERR ("seq length zero: $id\n") unless length($seq{$id});
	print ">$id\n$seq{$id}\n";
}



my $comment=<<EOF;
==> combined.uc <==
S	0	1442	*	.	*	*	*	NR_024644.1 Serratia rubidaea strain JCM1240 16S ribosomal RNA, partial sequence	*
S	1	1404	*	.	*	*	*	NR_029318.1 Listeria innocua strain 58/1971 16S ribosomal RNA, partial sequence	*
H	1	1418	98.7	+	0	0	14D1404M	NR_036809.1 Listeria ivanovii subsp. londoniensis strain CLIP 12229 16S ribosomal RNA gene, partial sequence	NR_029318.1 Listeria innocua strain 58/1971 16S ribosomal RNA, partial sequence

==> ../kma/E-16S_S1_trim_merged.res <==
#Template	Score	Expected	Template_length	Template_Identity	Template_Coverage	Query_Identity	Query_Coverage	Depth	q_value	p_value
NR_024644.1 Serratia rubidaea strain JCM1240 16S ribosomal RNA, partial sequence	 1682265	 2253940	    1442	   70.04	   70.11	   99.90	  142.63	 1222.16	83027.28	1.0e-26
NR_029318.1 Listeria innocua strain 58/1971 16S ribosomal RNA, partial sequence	 3363609	 2169158	    1404	   70.37	   72.15	   97.53	  138.60	 2543.18	257865.88	1.0e-26

==> combined.fa <==
>NR_024644.1 Serratia rubidaea strain JCM1240 16S ribosomal RNA, partial sequence
ACGCTGGCGGCAGGCCTAACACATGCAAGTCGAGCGGCAGCGGGAGGAAGCTTGCTTCCTCGCCGGCGAGCGGCGGACGG
GTGAGTAATGTCTGGGGATCTGCCCGATGGAGGGGGATAACCACTGGAAACGGTGGCTAATACCGCATAACGTCGCAAGA
EOF
