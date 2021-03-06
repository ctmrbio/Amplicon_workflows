#!/usr/bin/env perl -w

=head1 NAME

otu_tables

=head1 SYNOPSIS

	make_otu_tables [--help] [--verbose] [--threshold=INTEGER] [--depth=INTEGER] [--names=<FILE>]--classifier=<sina/rdp> --samples=<FOLDER> --classification=<FILE> --sequences=<FASTA>


		--samples: folder containing the -usearch_global output for each sample to be analysed,
				and nothing else (important!)
		--classification: allrank result from RDP classifier or SINA
		--sequences: fasta file with representatives from each OTU
		--classifier: which ever was used to generate the classification; default sina-cl
			sina-cl: command line sina
			sina-ol: online sina
			rdp: online RDP
			tsv: tsv file with OTU ID on column 1 and classification on the last column
		--threshold: minimum precentage confidence level to retain an RDP classification; default 70
		--depth: maximum taxonomic depth to retain a SINA classification; default 5
		--names: tsv connecting sample file name to sample name. If not provided, file name is used
		--help: This info.
	    
=head1 AUTHOR

luisa.hugerth@scilifelab.se

=cut


use warnings;
use strict;

use Bio::SeqIO;
use Getopt::Long;
use Pod::Usage;

my $help = 0;
my $verbose = 0;
my $samples_folder;
my $class_file;
my $sequences;
my $name_file="";
my $classifier="sina-cl";
my $threshold=70;
my $depth=5;
GetOptions(
  "samples=s" => \$samples_folder,
  "classification=s" => \$class_file,
  "threshold=i" => \$threshold,
  "classifier=s" => \$classifier,
  "names=s" => \$name_file,
  "sequences=s" => \$sequences,
  "depth=i" => \$depth,
  "help!" => \$help,
  "verbose!" => \$verbose,
);

pod2usage(0) if $help;

pod2usage(-msg => "Need a samples folder", -exitval => 1) unless $samples_folder;
opendir(DIR, $samples_folder) or die "Cannot open $samples_folder";

pod2usage(-msg => "Need a classification file", -exitval => 1) unless $class_file;
open CLASS, $class_file  or die "Cannot open $class_file";

pod2usage(-msg => "Classifier must be one of the four allowed ones", -exitval => 1) unless (($classifier eq "sina-cl") or ($classifier eq "rdp") or ($classifier eq "tsv") or ($classifier eq "sina-ol"));

pod2usage(-msg => "Need a fasta file", -exitval => 1) unless $sequences;
my $seqfile = Bio::SeqIO->new(-file=>"$sequences", -format => "fasta") or die "Can't open $sequences";

if ($name_file ne ""){
	open NAMES, $name_file or die "Cannot open $name_file";
}

sub rdp_parse{
	my $line = $_[0];
	my @samples = @{$_[1]};
	my $samples_ref = $_[2];
	my $seq_ref = $_[3];
	my $threshold = $_[4];
	my @fields = split(';',$line);
	my $otu = shift (@fields);
	my $print="$otu\t";
	shift @fields; shift @fields; shift @fields;
	foreach my $sample (@samples){
		if (exists ${$samples_ref}{$otu}{$sample}){
			$print = $print.${$samples_ref}{$otu}{$sample}."\t";
		}
		 else{
			$print = $print."0\t";
		 }
	}
	my $count = 0;
	my $classified = 'F';
	foreach my $taxon (@fields){
		unless ($taxon=~/%$/){
			$fields[$count+1]=~/(\d+)/;
			my $confidence = $1;
			if ($confidence >= $threshold){
				$taxon=~s/ /_/g;
				$print = $print.$taxon.";";
				$classified = 'T';
			}
		}
		$count++;
	}
	$print = $print."Unclassified;" if $classified eq 'F';
	print "$print\t".${$seq_ref}{$otu}."\n";
}

sub sina_cl_parse{
	my $line = $_[0];
	my @samples = @{$_[1]};
	my $samples_ref = $_[2];
	my $seq_ref = $_[3];
	my $depth = $_[4];
	chomp $line;
	my @fields = split(',',$line);
	my $otu = $fields[0];
	my $print = "$otu\t";
	foreach my $sample (@samples){
		if (exists ${$samples_ref}{$otu}{$sample}){
			$print = $print.${$samples_ref}{$otu}{$sample}."\t";
		}
		 else{
			$print = $print."0\t";
		 }
	}
	my $taxonomy=$fields[-5];
	my @taxonomy=split(';',$taxonomy);
	my $count = 1;
	foreach my $taxon (@taxonomy){
		if ($count <= $depth and $taxon!~/^"/){
			$taxon=~s/ /_/g;
			$print = $print.$taxon.";";
			$count++;
		}
	}
	print "$print\t".${$seq_ref}{$otu}."\n";
}

sub sina_ol_parse{
	my $line = $_[0];
	my @samples = @{$_[1]};
	my $samples_ref = $_[2];
	my $seq_ref = $_[3];
	my $depth = $_[4];
	chomp $line;
	my @fields = split('";"',$line);
	my $otu = $fields[2];
	my $print = "$otu\t";
	foreach my $sample (@samples){
		if (exists ${$samples_ref}{$otu}{$sample}){
			$print = $print.${$samples_ref}{$otu}{$sample}."\t";
		}
		 else{
			$print = $print."0\t";
		 }
	}
	my $taxonomy=$fields[-1];
	chop $taxonomy;
	my @taxonomy=split(';',$taxonomy);
	my $count = 1;
	foreach my $taxon (@taxonomy){
		if ($count <= $depth and $taxon!~/^"/){
			$taxon=~s/ /_/g;
			$print = $print.$taxon.";";
			$count++;
		}
	}
	print "$print\t".${$seq_ref}{$otu}."\n";
}

sub tsv_parse{
	my $line = $_[0];
	my @samples = @{$_[1]};
	my $samples_ref = $_[2];
	my $seq_ref = $_[3];
	my $depth = $_[4];
	chomp $line;
	my @fields = split('\t',$line);
	my $otu = $fields[0];
	my $print = "$otu\t";
	foreach my $sample (@samples){
		if (exists ${$samples_ref}{$otu}{$sample}){
			$print = $print.${$samples_ref}{$otu}{$sample}."\t";
		}
		 else{
			$print = $print."0\t";
		 }
	}
	my $taxonomy=$fields[-1];
	chop $taxonomy;
	my @taxonomy=split(';',$taxonomy);
	my $count = 1;
	foreach my $taxon (@taxonomy){
		if ($count <= $depth and $taxon!~/^"/){
			$taxon=~s/ /_/g;
			$print = $print.$taxon.";";
			$count++;
		}
	}
	print "$print\t".${$seq_ref}{$otu}."\n";
}


my %sequences;
while (my $seq = $seqfile->next_seq){
	$sequences{$seq->display_id} = uc($seq->seq);
}

my %names;
if ($name_file ne ""){
	while (my $line = <NAMES>){
		chomp $line;
		$line=~/^(\S+)\t(\S+)/;
		$names{$1} = $2;
	}
}
close NAMES;

my %samples;
my @samples = readdir(DIR);
shift @samples; shift @samples;
foreach my $sample (@samples){
	open (SAMPLE, "$samples_folder/$sample") or die "Failed to open $sample";
	while (my $line = <SAMPLE>){
		$line=~/(\S+)$/;
		my $otu=$1;
		unless ($otu eq '*'){
			$samples{$otu}{$sample}++;
		}
	} 
	close SAMPLE;
}
close DIR;
@samples = sort(@samples);

print "OTU\t";
foreach my $sample (@samples){
	if (exists($names{$sample})){
		print $names{$sample}."\t";
	}
	else{
		print $sample."\t";
	}
}
print "Taxonomy\tCentroid\n";

while (my $line = <CLASS>){
	chomp $line;
	$"="\t"; ## Sets the separator for arrays as tab
	if ($classifier eq "rdp"){
		if ($line!~/^(Classifier\:|Taxonomical |Query File|Submit Date|Confidence |Symbol |)/ and ($line ne "")){
			rdp_parse($line, \@samples, \%samples, \%sequences, $threshold);
		}
	}
	 elsif(($classifier eq "sina-cl") and ($line!~/name/) and ($line ne "")){
		sina_cl_parse($line, \@samples, \%samples, \%sequences, $depth);
	 }
	 elsif(($classifier eq "sina-ol") and ($line!~/job_id/) and ($line ne "")){
		sina_ol_parse($line, \@samples, \%samples, \%sequences, $depth);
	 }
	 elsif($classifier eq "tsv" and ($line ne "")){
		tsv_parse($line, \@samples, \%samples, \%sequences, $depth);		
	 }
}
close CLASS;
