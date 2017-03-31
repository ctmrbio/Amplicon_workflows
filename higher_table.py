#!/usr/bin/env python

"""higher_table.py: condenses an OTU table into a higher-order clade table

"""

from collections import defaultdict
import argparse
import csv
import re

def read_table(intable, taxfield, depth, first, last):
	taxdict = defaultdict(dict)
	with open(intable) as csvfile:
		reader = csv.reader(csvfile, delimiter="\t")
		header = next(reader)[first:last]
		for row in reader:
			counts = row[first:last]
			tax = row[taxfield].split(";")
			tax = ";".join(tax[0:depth])
			for i in range(len(header)):
				taxdict[tax][header[i]] = counts[i]
	return(header, taxdict)
		
def print_tab(header, counts):
	print("Taxon\t" + "\t".join(header))
	for taxon, line in counts.iteritems():
		out = taxon
		for sample in header:
			out = out + "\t" + line[sample]
		print(out)

def main(intable, depth, taxfield,  first, last):
	header, counts = read_table(intable, taxfield, depth, first, last)
	print_tab(header, counts)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Condenses an OTU table into a higher-order clade table')
	parser.add_argument('-i', '--intable', help='TSV OTU table with samples in columns and OTU in rows')
	parser.add_argument('-tax', '--taxonomy', type=int, default=-2, help='Which field contains the ;-separated taxonomy. Default -2')
	parser.add_argument('-d', '--depth', type=int, default=3, help='Depth to which condense table. Default 3 (class)')
	parser.add_argument('-1', '--firstfield', type=int, default=1, help='First field to consider as counts. Default 1 (0-based)')
	parser.add_argument('-z', '--lastfield', type=int, default=-3, help='Last field to consider as counts. Default -3 (0-based)')

	args = parser.parse_args()

	main(args.intable, args.depth, args.taxonomy, args.firstfield, args.lastfield)

