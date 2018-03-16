#!/usr/bin/env python

""" prepare4dedup.py: takes 1 OTU tab and prepares all files for pplacers's deduplicate script

"""

from collections import defaultdict
from operator import add
import argparse
import csv
import re

__author__ = "Luisa W Hugerth"
__email__ = "luisa.hugerth@scilifelab.se"


def parse_tab(infile, field1, fieldZ, seqfield):
	count_dict = defaultdict(dict)
	centroids = dict()
	maxi=0
	with open(infile) as csvfile:
		reader = csv.reader(csvfile, delimiter="\t")
		for row in reader:
			if (int(fieldZ) == -3):
				fieldZ = len(row)-2
			if row[0][0] == '#':
				names = row[field1:fieldZ]
			else:
				otu_id = row[0]
				line = row[field1:fieldZ]
				i = 0
				for field in line:
					if int(field) > 0:
						count_dict[otu_id][names[i]] = field
						if i > maxi:
							maxi = i
					i += 1
				centroid = row[seqfield]
				centroids[otu_id] = centroid
	return (count_dict, names, centroids)


def printer(counts, prefix, names, seqs):
	fastaname = prefix + ".fasta"
	fastaout = open(fastaname, 'w')
	countname = prefix + ".counts.csv"
	countout = open(countname, 'w')
	mapname = prefix + ".map.csv"
	mapout = open(mapname, 'w')
	for otu_id, fields in counts.iteritems():
		seq = seqs[otu_id]
		for sample, count in fields.iteritems():
			newname = sample + "_" + otu_id
			fastaline = ">" + newname + "\n" + seq + "\n"
			fastaout.write(fastaline)
			countline = newname + "," + fields[sample] + "\n"
			countout.write(countline)
			splitline = newname + "," + sample + "\n"
			mapout.write(splitline)

	

def main(infile, prefix, field1, fieldZ, seqfield):
	counts, names, seqs = parse_tab(infile, field1, fieldZ, seqfield)
	printer(counts, prefix, names, seqs)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Parses tsv OTU tables into various tsv ready for krona input')
	parser.add_argument('-i', '--infile', help='TSV OTU table with samples on columns and OTU on rows')
	parser.add_argument('-p', '--prefix', default="dedup", help='A prefix for the name of the files generated. Default: %(default)s')
	parser.add_argument('-1', '--field1', type=int, default=1, help='First field to create a file for. Default: %(default)i')
	parser.add_argument('-Z', '--fieldZ', type=int, default=-3, help='Last field to create a file for. Default: %(default)i')
	parser.add_argument('-seq', '--seqfield', type=int, default=-1, help='Field containing the centroid sequence. Default: %(default)i')
	args = parser.parse_args()

	main(args.infile, args.prefix, args.field1, args.fieldZ, args.seqfield)

