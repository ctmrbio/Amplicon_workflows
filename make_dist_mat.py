#!/usr/bin/env python

"""make_dist_mat.py: condenses an OTU table into a higher-order clade table

"""

from collections import defaultdict
import argparse
import csv
import re


def reader(intable):
	tab = defaultdict(dict)
	names=""
	with open(intable) as csvfile:
		reader = csv.reader(csvfile, delimiter="\t")
		names = next(reader)
		#print(names)
		othernames = list(names)
		for row in reader:
			#print(row)
			feat = row.pop(0)
			tab[feat][feat] = 0
			if(len(row)>0):
				del othernames[0]
				#print(othernames)
				#print( feat, feat)
				i = 0
				while (len(row) > 0):
					target = othernames[i]
					#print(feat, target)
					#print(row)
					item = row.pop(0)
					tab[target][feat] = item
					tab[feat][target] = item
					i += 1
				
	return(tab, names)

def printer(table, names):
	print("\t" + ("\t".join(names)))
	for i in range(0, len(names)):
		myline = names[i]
		for j in range(0, len(names)):
			myline = myline + "\t" + str(table[names[i]][names[j]])
		print(myline)


def main(intable):
	table, names = reader(intable)
	#print(names)
	printer(table, names)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Condenses an OTU table into a higher-order clade table')
	parser.add_argument('-i', '--intable', help='TSV OTU table with samples in columns and OTU in rows')
	args = parser.parse_args()

	main(args.intable)

