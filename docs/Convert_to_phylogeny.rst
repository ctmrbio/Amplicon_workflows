This workflow uses a lot of different tools that are themselves well documented. 
We will therefore only give one example of usage, but the user can refer to the documentation
to adjust it to their use case.

Tools you'll need to set up a new reference library:
 * Seqmagick_
 * FastTree_ or another tree building algorithm
 * Taxtastic_
 * (Optional) Degeprime_

Tools you'll need for running each new sample batch:
 * ClustalO_ or another multiple sequence aligner
 * Pplacer_
 * Guppy_
 
.. _Seqmagick: http://seqmagick.readthedocs.io/en/latest/
.. _FastTree: http://www.microbesonline.org/fasttree/
.. _Taxtastic: https://pypi.python.org/pypi/taxtastic
.. _Degeprime: https://github.com/envgen/DEGEPRIME
.. _ClustalO: http://www.clustal.org/omega/
.. _Pplacer: https://matsen.github.io/pplacer/generated_rst/pplacer.html
.. _Guppy: https://matsen.github.io/pplacer/generated_rst/guppy.html

=====
PREPARATION STEPS
=====

These steps will only need to be run once for every reference library.

**STEP 1: Select your sequences of interest**

Select from an apropriate database (such as the latest Silva_ or PR2_ releases) sequences appropriate to your environment of interest. For example, if your primers only amplify bacterial DNA, removing archaeal and eukaryotic sequences from the DB will save you a lot of time. If you have a list of sequence ID:s, you can use the script select_sample.pl to extract them from a Fasta file. Unless you're planning on working on a very small subset, I recommend starting from a pre-aligned database.

.. _Silva: https://www.arb-silva.de/no_cache/download/archive/
.. _PR2: https://figshare.com/articles/PR2_rRNA_gene_database/3803709

**STEP 2: Remove excessive gaps and duplicated sequences**

If your reference database was unaligned, now you need to align it. I recommend ClustalO for that task.

Otherwise, since only a subset of sequences were selected, there are now positions which are entirely gapped, and that's no good. You can also save time by removing sequences that are *mostly* gaps, since they are usually found at the edges of the alignment and are not particularly informative. One way to do this is with the following script from the DegePrime suite:

 $ perl TrimAlignment.pl -i <infile> -o <infile>.trim.fasta -min 0.3 -trailgap

This will only keep positions where at least 30% of the sequences have a base, not a gap.

Now that this is done, you've probably ended up with some identical sequences, since they only differed by a few trailing bases. This will make tree building very slow, so we remove it with SeqMagick:

 $ seqmagick mogrify --deduplicate-sequences <infile>.trim.fasta

Note that mogrify converts the file *in place*. If you want to keep both files, use convert instead of mogrify.

**STEP 3: Build a phylogenetic tree**

Now we can build a reference tree of our selected sequences! For this use case, speed is a primary concern, so we use FastTree in its fastest mode:

 $ FastTree -nt -gtr -log TREE.log -fastest <infile>.trim.fasta > <infile>.trim.nwk 

This will take quite a bit of memory and probably > 24h

**STEP 4: Create a reference package**

The only thing left to do is organise the information in a helpful way for Pplacer! This should take less than an hour and requires biopython to be installed and available:

 $ taxit create -l <gene used> -P <name for the new package> --aln-fasta <infile>.trim.fasta --tree-stats TREE.log  --tree-file <infile>.trim.nwk --stats-type FastTree -a <your name>  


=====
RUNNING STEPS
=====

These steps will need to be run everytime you want to get phylogenetic distances out of an OTU table.
It assumes that you have a TSV OTU table with samples as columns and OTU as rows, such as the ones generated
by the other workflows in this repo.

**STEP 1: Convert OTU table into appropriate formats**

Pplacer needs a single fasta file. Guppy needs information on how many copies of each OTU are in each sample. We combine these two needs with a custom script, found in this repo:

 $ prepare4dedup.py -i <infile> -p <prefix for output files>

3 files will be generated, *prefix*.fasta, *prefix*.counts.cv and *prefix*.map.csv. For the rest of this protocol, I'll use the default prefix "dedup" in the examples.

**STEP 2: Align OTU to reference alignment**

Now, before we run pplacer, the OTU centroids must be aligned to the reference sequences. If you're running ClustalO, your file is gonna look something like:

 $ clustalo --infile=dedup.fasta --profile1=aligned_reference.fasta --seqtype=DNA  --outfile=dedup.aln.fasta --verbose --log=clustalo.log

**STEP 3: Run pplacer**

Now you can run pplacer! It parallelises very well, so take advantage of your cores.

$ pplacer --out-dir <output_dir> -j <num_threads> -c <ref_package> cluster/ALL_SILVA.aln.fa 

**STEP 4: Reduplicate**

Now we use Guppy to add the OTU count information back to  fasta file:

 $ guppy redup -o redup.fasta -d dedup.counts.csv dedup.fasta

**STEP 5: Run Guppy**

Finally, you can run guppy to get all sorts of cool statistics and graphs! Some of the main ones are unweighted unifrac and Kantorovich-Rubinstein distance, which is a variant of weighted unifrac with better mathematical properties. Guppy also includes specific statistical tools for dealing with tree structures, such as edge squashing, a PCA for trees. Some examples:

 $ guppy unifrac --csv -o unifrac.csv redup.fasta:dedup.map.csv
 
 $ guppy kr -c <ref_package> -o kr.csv redup.fasta:dedup.map.csv

**STEP 6: Convert guppy output to R format (optional)**

As mentioned above, many statistical operations can be perfomed within Guppy. However, if you wish to read he files kr.csv or unifrac.csv into R, some post-processing is needed to convert these space-separated awkward files into tab-separated symmetric distance matrices. This can be done with the following script, written in Python 3:

 $ convert_guppy_output.py -o kr4R.tsv kr.csv
