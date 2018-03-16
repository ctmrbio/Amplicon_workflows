#!/usr/bin/env perl -w

=head1 NAME

extract_sample

=head1 SYNOPSIS

	extract_sample [--help] [--verbose] --sample=TSV --database=FASTAFILE --type=<fasta|tsv>

		Extracts from a database the sequences with IDs listed
		
		--help: This info.
		--sample: File with sequence IDs separated by tab and linebreak, optional '>' before ID
					Cluster size information will be ignored.
		--type: Database is either fasta (default) or TSV (eg SAM)
	   	--database: Fasta or TSV formated file with read ID in the first field

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
my $dbfile;
my $samples;
my $type = "fasta";
GetOptions(
  "database=s" => \$dbfile,
  "sample=s" => \$samples,
  "type=s" => \$type,
  "help!" => \$help,
  "verbose!" => \$verbose
);

pod2usage(0) if $help;

pod2usage(-msg => "Need a sample file", -exitval => 1) unless $samples;
open SAMPLE, $samples or die "Can't open $samples: $!";

my $infile;
if ($type eq "fasta"){
	$infile = Bio::SeqIO->new(-file=>"$dbfile", -format => "fasta") or die "Can't open $dbfile";
}
 else{
	open INFILE, $dbfile or die "Can't open tsv file $dbfile: $!";
 }

my %sample=();
while (my $line = <SAMPLE>){
	chomp $line;
	my @ids = split ("\t",$line);
	foreach my $id (@ids){
		$id=~/>?(\S+)/;
		$id = $1;
		if ($id=~/size=/){
			$id=~/(.+);size=\d+;/;
			$id = $1;
		}
		$sample{$id}=0;
	}
}

if ($type eq "fasta"){
	while (my $seq = $infile->next_seq){
		my $id = $seq->display_id;
#	$id=~/(.+)(;size=\d+;)/;
#	my $id = $1;
		if (exists ($sample{$id})){
			print (">", $seq->display_id, " ", $seq->desc, "\n", $seq->seq, "\n");
		}
	}
}
 else{
	while (my $line = <INFILE>){
		$line =~ /^(\S+)/;
		my $id = $1;
		print $line if (exists ($sample{$id}));
	}
 }

close SAMPLE;
close INFILE unless ($type eq "fasta");

