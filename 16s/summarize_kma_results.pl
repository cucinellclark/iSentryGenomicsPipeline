use strict;
use IO::Uncompress::Gunzip;

my $file_prefix = shift or die "specify file prefix to xxx.frag.gz and xxx.res for kma output\n";
my $frag_file = $file_prefix . ".frag.gz";
open F, $frag_file or die "cannot open $frag_file";
my $gunzip = new IO::Uncompress::Gunzip $frag_file;
my %data;
my %sample;
my %template;
while (<$gunzip>) {
	my @r = split "\t"; 
	my ($template, $sample) = ($r[5], $r[6]);
	$sample =~ s/\..*//;
	#$sample =~ s/^\d\d-//;
	$sample{$sample}++;
	$template{$template}++;
	$data{$template}{$sample}++;
}

my $res_file = $file_prefix . ".res";
#Template       Score   Expected        Template_length Template_Identity       Template_Coverage       Query_Identity  Query_Coverage  Depth   q_value p_value
#NR_024644.1 Serratia rubidaea strain JCM1240 16S ribosomal RNA, partial sequence        10566250        12405212            1442           70.11           70.18           99.90          142.49         7644.29        147216.64       1.0e-26
open F, $res_file;
my $header = <F>;
my %res;
while (<F>) {
	my ($template, $score, $exp, $temp_len, $temp_ident, $temp_cov, $query_ident, $query_cov, $depth) = split("\t");
	$res{$template} = [$score, $temp_ident, $temp_cov, $depth];
}

my @samples = sort {$sample{$b} <=> $sample{$a}} keys %sample;
my @templates = sort {$template{$b} <=> $template{$a}} keys %template;

print "Reference\tkma_score\ttempl_ident\ttempl_cov\tdepth\t" . join("\t", @samples) . "\n";
for my $template (@templates) {
	my $display_name = $template;
	$display_name =~ s/ 16S ribosomal.*//;
	$display_name =~ s/(\S+) (.*)/$2 $1/;
	print $display_name;
	print "\t$res{$template}->[0]\t$res{$template}->[1]\t$res{$template}->[2]\t$res{$template}->[3]";
	for my $sample (@samples) {
		my $val = 0;
		$val += $data{$template}{$sample};
		print "\t$val";
	}
	print "\n";
}


my $comment = <<"EOF";      
GTAACGAGCGCAACCCTTAAGCTTAGTTGCCATCATTAAGTTGGGCACTCTAAGTTGACTGCCGGTGACAAACCGGAGGAAGGTGGGGATGACGTCAAATCATCATGCCCCTTATGACCTGGGCTACACACGTACTACAATGGCCGGTACAACGGGAAGCGAAGGAGCGATCTGGAGCCAATCCTAGAAAAGCCGGTCTCAGTTCGGATTGCAGGCTGCAACTCGCCTGCATGAAGTCGGAATTGCTAGTAATCGCGGATCAGCATGCCGCGGTGAATACGTTCCCGGGTCTTGTACACACCGCCCGTC	1	281	0	311	Round1_c00	03-AMP003.145465	0	309
GCAACGAGCGCAACCCTTGAACTTAGTTGCCAGCAGGTGAAGCTGGGCACTCTAAGTTGACTGCCGGTGACAAACCGGAGGAAGGCGGGGATGACGTCAAATCATCATGCCCCTTATGACCTGGGCTACACACGTACTACAATGGCCGGTACAACGGGAAGCGAAGGAGCGATCTGGAGCCAATCCTAGAAAAGCCGGTCTCAGTTCGGATTGCAGGCTGCAACTCGCCTGCATGAAGTCGGAATTGCTAGTAATCGCGGATCAGCATGCCGCGGTGAATACGTTCCCGGGTCTTGTACACACCGCCCGTC	1	302	0	311	Round1_c00	01-AMP001.299493	0	311
GCAACGAGCGCAACCCTTGAACTTAGTTGCCAGCAGGTGAAGCTGGGCACTCTACGTTGACTGCCGGTGACAAACCGGAGGAAGGCGGGGATGACGTCAAATCATCATGCCCCTTATGACCTGGGCTACACACGTACTACAATGGCCGGTACAACGGGAAGCGAAGGAGCGATCTGGAGCCAATCCTAGAAAAGCCGGTCTCAGTTCGGATTGCAGGCTGCAACTCGCCTGCATGAAGTCGGAATTGCTAGTAATCGCGGATCAGCATGCCGCGGTGAATACGTTCCCGGGTCTTGTACACACCGCCCGTCACACCACGAGAGTTTACAACACCCGAAGTCGGTGAGGTAACCGCAAGGGGCCAGCCGCCGAAGGTGGGGTAGATGATTGGGGTGAAGTCGTAACAAGGTA	1	299	0	311	Round1_c00	01-AMP001.305284	0	411
EOF
