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

**STEP 2: Remove duplicated sequences**

**STEP 3: Build a phylogenetic tree**

**STEP 4: Create a reference package**


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

As mentioned above, many statistical operations can be perfomed within Guppy. However, if you wish to read he files kr.csv or unifrac.csv into R, some post-processing is needed. For the time being, this consists of a manual step and one automatic.

The manual part:

 1. Open the files into a text editor and replace all cases of "  " (2 spaces in a row) with a single one until there's none left
 
 2. Remove all trailing spaces in the beginning and end of lines
 
 3. Replace all spaces for tabs
 
The automated part is done by the make_dist_mat.py script:

 $ make_dist_mat.py -i unifrac.csv > unifrac4R.tsv
