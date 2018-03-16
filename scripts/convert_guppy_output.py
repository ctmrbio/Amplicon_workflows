#!/usr/bin/env python3
__author__ = "Fredrik Boulund, Luisa Hugerth"
__year__ = "2017"
__doc__ = """Convert Guppy upper triangular output to symmetric matrix."""

from sys import argv, exit, stdout, stderr
from collections import defaultdict
import argparse

def parse_args():
    """Parse commandline arguments.
    """

    desc = __doc__ + " Copyright (c) " + __year__ + " " + __author__ + "."
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("GUPPY",
            help="Guppy output in upper triangular format (txt).")
    parser.add_argument("-o", "--output", metavar="OUTFILE",
            default="",
            help="Write output to OUTFILE instead of printing to stdout.")

    if len(argv) < 2:
        parser.print_help()
        exit(1)
    
    return parser.parse_args()


def read_guppy_lines(guppy_fn):
    """Yield Guppy lines.
    """
    with open(guppy_fn) as f:
        firstline = f.readline()
        if not firstline.startswith(" "):
            print("File doesn't look like Guppy output:", 
                    guppy_fn, file=stderr)
            exit(2)
        yield firstline
        for line in f:
            yield line


def convert_guppy_to_symmetric_dict(guppy_lines):
    """Convert Guppy lines to symmetric nested dict.

    Returns:
        samples  list of samples in observed order.
        matrix   nested dict emulating symmetric matrix, 
                 indexed as matrix[sample1][sample2].
    """
    matrix = defaultdict(dict)
    first_line = next(guppy_lines)
    samples = first_line.split()
    for idx, line in enumerate(guppy_lines):
        row = line.split()
        for jdx, sample in enumerate(samples[idx:]):
            if row[0] == sample:
                matrix[row[0]][sample] = "0"
                matrix[sample][row[0]] = "0"
            else:
                matrix[row[0]][sample] = row[jdx]
                matrix[sample][row[0]] = row[jdx]
    return samples, matrix 


def print_matrix(samples, matrix, dest):
    """Print matrix to dest.
    """
    print("\t{}".format("\t".join(samples)), file=dest)
    for sample in samples:
        outline = [matrix[sample][sample2] for sample2 in samples]
        print("{}\t{}".format(sample, "\t".join(outline)), file=dest)


def main(guppy_fn, outfile):
    """Main logic.
    """
    guppy_lines = read_guppy_lines(guppy_fn)
    samples, matrix = convert_guppy_to_symmetric_dict(guppy_lines)
    if outfile:
        with open(outfile, "w") as outhandle:
            print_matrix(samples, matrix, outhandle)
    else:
        print_matrix(samples, matrix, stdout)


if __name__ == "__main__":
    options = parse_args()
    main(options.GUPPY, options.output)
