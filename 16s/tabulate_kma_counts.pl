use strict;
use IO::Uncompress::Gunzip;

my $infile = shift or die "specify xxx.frag.gz from kma output\n";
open F, $infile or die "cannot open $infile";
my $gunzip = new IO::Uncompress::Gunzip $infile;
my %data;
my %sample;
my %amplicon;
while (<$gunzip>) {
	my @r = split "\t"; 
	my ($amplicon, $sample) = ($r[5], $r[6]);
	$sample =~ s/\..*//;
	#$sample =~ s/^\d\d-//;
	$sample{$sample}++;
	$amplicon{$amplicon}++;
	$data{$amplicon}{$sample}++;
}

#my @samples = sort {$sample{$b} <=> $sample{$a}} keys %sample;
my @samples = sort keys %sample;
my @amplicons = sort {$amplicon{$b} <=> $amplicon{$a}} keys %amplicon;

print "Reference\t" . join("\t", @samples) . "\n";
for my $amplicon (@amplicons) {
	print $amplicon;
	for my $sample (@samples) {
		my $val = 0;
		$val += $data{$amplicon}{$sample};
		print "\t$val";
	}
	print "\n";
}


my $comment = <<"EOF";      
GTAACGAGCGCAACCCTTAAGCTTAGTTGCCATCATTAAGTTGGGCACTCTAAGTTGACTGCCGGTGACAAACCGGAGGAAGGTGGGGATGACGTCAAATCATCATGCCCCTTATGACCTGGGCTACACACGTACTACAATGGCCGGTACAACGGGAAGCGAAGGAGCGATCTGGAGCCAATCCTAGAAAAGCCGGTCTCAGTTCGGATTGCAGGCTGCAACTCGCCTGCATGAAGTCGGAATTGCTAGTAATCGCGGATCAGCATGCCGCGGTGAATACGTTCCCGGGTCTTGTACACACCGCCCGTC	1	281	0	311	Round1_c00	03-AMP003.145465	0	309
GCAACGAGCGCAACCCTTGAACTTAGTTGCCAGCAGGTGAAGCTGGGCACTCTAAGTTGACTGCCGGTGACAAACCGGAGGAAGGCGGGGATGACGTCAAATCATCATGCCCCTTATGACCTGGGCTACACACGTACTACAATGGCCGGTACAACGGGAAGCGAAGGAGCGATCTGGAGCCAATCCTAGAAAAGCCGGTCTCAGTTCGGATTGCAGGCTGCAACTCGCCTGCATGAAGTCGGAATTGCTAGTAATCGCGGATCAGCATGCCGCGGTGAATACGTTCCCGGGTCTTGTACACACCGCCCGTC	1	302	0	311	Round1_c00	01-AMP001.299493	0	311
GCAACGAGCGCAACCCTTGAACTTAGTTGCCAGCAGGTGAAGCTGGGCACTCTACGTTGACTGCCGGTGACAAACCGGAGGAAGGCGGGGATGACGTCAAATCATCATGCCCCTTATGACCTGGGCTACACACGTACTACAATGGCCGGTACAACGGGAAGCGAAGGAGCGATCTGGAGCCAATCCTAGAAAAGCCGGTCTCAGTTCGGATTGCAGGCTGCAACTCGCCTGCATGAAGTCGGAATTGCTAGTAATCGCGGATCAGCATGCCGCGGTGAATACGTTCCCGGGTCTTGTACACACCGCCCGTCACACCACGAGAGTTTACAACACCCGAAGTCGGTGAGGTAACCGCAAGGGGCCAGCCGCCGAAGGTGGGGTAGATGATTGGGGTGAAGTCGTAACAAGGTA	1	299	0	311	Round1_c00	01-AMP001.305284	0	411
EOF
