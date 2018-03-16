#!/usr/bin/env python

""" tsv2krona.py: converts OTU tables to multiple krona files

"""

from collections import defaultdict
from operator import add
import argparse
import csv
import re

__author__ = "Luisa W Hugerth"
__email__ = "luisa.hugerth@scilifelab.se"


def parse_tab(infile, field1, fieldZ, taxfield):
	count_dict = defaultdict(list)
	with open(infile) as csvfile:
		reader = csv.reader(csvfile, delimiter="\t")
		for row in reader:
			if (int(fieldZ) == -1):
				fieldZ = len(row)
			if row[0][0] != '#':
				line = list(map(int, row[field1:fieldZ+1]))
				tax = row[taxfield]
				if (tax in count_dict):
					count_dict[tax] = list(map(add, count_dict[tax], line))
				else:
					count_dict[tax] = line
			else:
				names = row[field1:fieldZ+1]
	return (count_dict, names)


def printer(table, prefix, names):
	i = 0
	fileno = len(names)
	while (i<fileno):
		filename = ".".join([prefix, names[i], "out"])
		f = open(filename, 'w')
		print("Printing file no." + str(i+1))
		for tax, counts in table.items():	##was .iteritems
			if counts[i] > 0:		## 'map' object is not subsettable
				tax = tax.replace(";", "\t")
				tax = tax.replace('"', '')
				line = "\t".join([str(counts[i]), tax, "\n"])
				f.write(line)
		i = i+1


def main(infile, prefix, field1, fieldZ, taxfield):
	counts, names = parse_tab(infile, field1, fieldZ, taxfield)
	printer(counts, prefix, names)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Parses tsv OTU tables into various tsv ready for krona input')
	parser.add_argument('-i', '--infile', help='TSV OTU table with samples on columns and OTU on rows')
	parser.add_argument('-n', '--name', default="krona", help='A prefix for the name of the files generated. Default: %(default)s')
	parser.add_argument('-1', '--field1', type=int, default=1, help='First field to create a file for. Default: %(default)i')
	parser.add_argument('-Z', '--fieldZ', type=int, default=-3, help='Last field to create a file for. Default: %(default)i')
	parser.add_argument('-tax', '--taxfield', type=int, default=-2, help='Field containing the taxonomic annotation. Default: %(default)i')
	args = parser.parse_args()

	main(args.infile, args.name, args.field1, args.fieldZ, args.taxfield)

