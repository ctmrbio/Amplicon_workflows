Processing amplicons with overlapping reads
===========================================

This is a quick guide on how to use Usearch to go from fastq files all the way to a table of OTUs. This is based chiefly on the programmes `Usearch <http://drive5.com/usearch/>`_, `Vsearch <https://github.com/torognes/vsearch>`_  and `Cutadapt <https://github.com/marcelm/cutadapt>`_. Also refer to those pages for download and installation instructions. Vsearch and Usearch are very similar pieces of software and most steps can be performed equally well with one or the other, but some functionalities are exclusive to one of them, and both are needed. I'm going to assume in this workflow that you can call usearch, vsearch and cutadapt simply by typing the programme names, but this depends on the folder where you have installed it, how you have named it and the folder you're in.

I'm also assuming you have overlapping reads, that is, that your forward and reverse reads overlap each other in the 5'-end. If this is not the case, or if you're not sure, please refer to the amplicons_no-overlap manual.

Finally, notice you'll need both biopython and bioperl.

*Part I: filtering and merging*
-------------------------------

**STEP 1. Quality trimming and primer removal**
	In this step, you cut off bases with low quality. MiSeq reads usually have good qualities. On the other hand, there are gonna be further quality filtering later, so there's no need to be too stringent. We'll also remove primer sequences and discard reads that do not contain the primers and reads that are too short after trimming.

The command:

	cutadapt -g ^<forward primer> -G ^<reverse primer> --no-indels -O <length of shortest primer> -q <quality cutoff> --discard-untrimmed -m <minimal length> -o <output forward> -p <output reverse> <input forward> <input reverese>

Example:

	cutadapt -g ^CCTACGGGNGGCWGCAG -G ^GACTACHVGGGTATCTAATCC --no-indels -O 17 -q 15 --discard-untrimmed -m 200 -o trimmed_1.fq -p trimmed_2.fq reads_1.fq reads_2.fq


**STEP 2: Merging**
	In this step we will merge the forward and reverse reads into a single amplicon. When the overlap is perfect, they will simply be combined; where there are differences, the base with the highest Phred-score will be chosen. A new probability score will also be calculated for each base in the overlap region. You can set a maximum limit of how many bases can be different between the reads in the overlap region without discarding the read pair. Think about the size of your expected overlap and the percentage of errors you find acceptable. If you choose not to set this value, there will be no upper limit (every read will be kept, no matter the differences).

The command:

	usearch -fastq_mergepairs <forward_reads> -reverse <reverse_reads> -fastq_maxdiffs <maximum number of different bases> -fastqout <outfile>

Example:

	usearch -fastq_mergepairs trimmed_1.fq -reverse trimmed_2.fq -fastq_maxdiffs 4 -fastqout merge.fq


**STEP 3: Quality filtering**
	When merging, new base qualities were calculated for the overlapping region. In this step, we discard low quality reads and reads that are too short. To set these parameters, consider the length of your amplicon, the expected error rate in the read and your downstream applications. We will also take this opportunity to convert our reads from fastq to fasta.

The comand:

	vsearch -fastq_filter <infile> -fastq_minlen <minimal length> -fastq_maxlen <maximal length> -fastq_maxee <maximum number of errors> -fastaout <outfile>

Example:

	vsearch -fastq_filter merge.fq -fastq_minlen 400 -fastq_maxlen 500 -fastq_maxee 4 -fastaout filtr.fa


*Part II: Clustering*
---------------------
	
**STEP 4: Sample concatenation**
	In most applications, you want to compare communities from different environments, conditions etc. For this, you have to have the same OTU defined for all samples. Therefore, at this point we concatenate all files.

The command:

	cat <all_fasta_files> > <outfile>

Example:

	cat filtr1.fa filtr2.fa filtr3.fa > all.fa

**STEP 5: Dereplication**
	Here we combine all reads that are identical into a single one, keeping track of how many copies there are of each one. We'll also discard sequences that only show up once in the entire dataset, as they're very likely to be errors. This saves a lot of time down the road. We'll also give our OTU a better name than the standard read names.

The command:

	vsearch -derep_fulllength <infile> -output <outfile> -minuniquesize <minimal abundance> --relabel <label>
	
Example:

	vsearch -derep_fulllength all.fa -output uniques.fa -minuniquesize 2 --relabel OTU-


**STEP 6: OTU picking**
	This is the step where Usearch v.9 or above is really necessary. Instead of clustering OTU at any fixed percentage similarity, this will consider both the relative abundance of the reads and the Hamming distance between them to calculate the probability that an unique sequence is simply a faulty version of another, and then assign them to the same OTU. This gives good resolution for closely related species while not inflating the alpha-diversity. While other softwares exist that have similar approaches (eg `DADA2 <https://benjjneb.github.io/dada2/tutorial.html>`_), unoise is fastest.

The command:

	usearch -unoise <infile> -fastaout <outfile> -minampsize <minimal abundance>
	
Example:

	usearch -unoise uniques.fa -fastaout centroids.fa -minampsize 2

**STEP 7: Assigning reads to OTU**
	We will now look at each of our merged fastq files and assign them to OTU. At this point, take the opportunity to make a directory just for your new cluster files. This is important downstream. You're also requested to say how similar your sample must be to the centroid. This must be compatible with the similarity you used for clustering.

The command:

	vsearch -usearch_global <sample file> -db <numbered out file> -strand <plus/both> -id <similarity to the centroid> -uc <outfile> --query_cov <minimal coverage>

Example:

	vsearch -usearch_global merge.fq -db centroids.fa -strand plus -id 0.98 -uc clusters/reads1.uc --query_cov 1

*Part III: Taxonomy assignment*
-------------------------------

**STEP 8: Mapping OTU to a curated database**
	The classification approach used here was first developed by `Yue O. O. Hu <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4864665/>`_ for 18S assignment, and then rewritten in Python and adapted for 16S here. It requires highly curated databases, and for that a curated version of the `PR2 database <http://ssu-rrna.org/>`_ for protists and of the `SILVA database <https://www.arb-silva.de/download/arb-files/>`_ for bacteria and archaea can be used. Use the following download links:
	
+---------+---------------------------------+-------------------------------------+
|**16S**  |`SILVA 128 release`_             | `Curated SILVA 128 taxonomy table`_ |
+---------+---------------------------------+-------------------------------------+
|**18S**  |`Curated PR2 databse`_           | `PR2 taxonomy table`_               |
+---------+---------------------------------+-------------------------------------+


.. _`SILVA 128 release`:  https://www.arb-silva.de/fileadmin/silva_databases/release_128/Exports/SILVA_128_SSURef_Nr99_tax_silva_trunc.fasta.gz
.. _`Curated SILVA 128 taxonomy table`: https://export.uppmax.uu.se/b2016371/public/database/silva_128_Nr99_no-euk_curated.tsv
.. _`Curated PR2 databse`: https://export.uppmax.uu.se/b2010008/projects-public/database/PR2_derep_3000bp.fasta
.. _`PR2 taxonomy table`: https://export.uppmax.uu.se/b2010008/projects-public/database/PR2_derep_3000bp.tax.txt


Use vsearch to map your amplicons to the database as fast as Usearch would, but produce a blast-like output.
	
The command:
	
	vsearch --usearch_global <infile> -db <database> --blast6out <output> --id <minimal ID for a phylum-level assignemt> --maxaccepts <maximum number of top hits to keep>

Example:

	vsearch --usearch_global centroids.fa -db SILVA_128_SSURef_Nr99_tax_silva_trunc.fasta --blast6out centroids2silva.blast --id 0.9 --maxaccepts 45

If you have good reason to use SINA or the RDP classifier instead of this approach, please refer to `this older workflow <https://github.com/EnvGen/Tutorials/blob/master/amplicons-overlap.rst`_ and follow steps 12-14.
	
**STEP 9: Parsing the taxonomy**
	The trick here is that we'll parse the same mapping result att diferent levels of similarity and keep the best classification possible for the level of similarity found. The similarity levels presented here work well in our experience, but they're not universal for all clades. Specific research questions might require optimizing them.
	
The code:

	SIMS=<similarity levels>
	for sim in ${SIMS[@]}; do
	
      		python taxonomy_blast_parser.py -1 <output> -2 <output> -id $sim -tax <taxonomy DB> -l1 <length of amplicon> -l2 <length of amplicon> > parse.${sim}.out
	done
	
	python combine_taxonomy.py -i <output files separated by comma> -n <taxonomy level they correspond to> -d <depth of taxonomy to consider for each level> > <output>
	
Example:

	SIMS=(90 95 97 99 100)
	for sim in ${SIMS[@]}; do
        	python taxonomy_blast_parser.py -1 blast.$sim.out -2 blast.$sim.out -id $sim -tax silva_128_Nr99_no-euk_curated.tsv -l1 350 -l2 350 > parse.${sim}.out
	done
	
	python combine_taxonomy.py -i parse.100.out,parse.99.out,parse.97.out,parse.95.out,parse.90.out -n strain,species,genus,class,phylum -d 8,7,6,3,2 > taxonomy.out


*PART IV: BUILDING A TABLE*
-----------------

**STEP 10: Creating an OTU table**
.....

The command:

	perl make_otu_tables.pl --names=<FILE> --samples=<FOLDER> --classification=<RDP_FILE> --sequences=<FASTA> --classifier=tsv > temp

Example:

	perl make_otu_tables.pl --samples=clusters/ --classification=taxonomy.out --sequences=centroids.fa --classifier=tsv > temp

**STEP 10: Eliminating 0 count OTUs**
	During assignment with usearch_global, some OTU that had been predicted earlier might end up with no reads assigned to them, since other OTU centroids had better matches to those reads. These make your OTU tables unnecessarily large, so you can eliminate them. The same approach can be used if you want to eliminate singletons at this step, for instance. We'll take the opportunity to fix a litte problem with the header line.
	
The command:

	awk 'NR>1{for(i=2;i<=(NF-2);i++) t+=$i; if(t>0){print $0}; t=0}' temp | sed '1s/ /\\t/g' > otu_table.tsv
	
	rm temp

	
*PART V: BIOLOGY*
-----------------
It's beyond the scope of this tutorial to teach you how to draw biological conclusions from your OTU table. However, here are some useful links:

For visualizing your data in interactive hierarchical pie charts, use `Krona <http://sourceforge.net/p/krona/home/krona/>`_. For converting the OTU table you made here into a krona compatible input, use the script tsv2krona.py found in this repo and the ktImportText tool from krona.

For information and tutorials on statistical methods for analysis of microbial ecology, take a look at `Gustame <https://sites.google.com/site/mb3gustame/home>`_.

If you believe that there are interesting OTU that are worth looking deeper into for their specific ecology, consider `oligotyping <http://merenlab.org/projects/oligotyping/>`_.

If you're working with 16S in a well-characterized environments, such as the human microbiome, you can also consider `PiCrust <http://picrust.github.io/picrust/>`_ This repo also contains a guide on how to combine this approach with a PiCrust analysis.
