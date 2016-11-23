Processing amplicons with overlapping reads
===========================================


This is a quick guide on how to use Usearch7 to go from fastq files all the way to a table of OTUs. This is based chiefly on the programmes `Vsearch <https://github.com/torognes/vsearch>`_ and `Cutadapt <https://github.com/marcelm/cutadapt>`_. Also refer to this page for download and installation instructions. I'm going to assume in this manual that you can call vsearch and cutadapt simply by typing the programme names, but this depends on the folder where you have installed it, how you have named it and the folder you're in.

This guide assumes that you have overlapping reads, that is, that your forward and reverse reads overlap each other in the middle. If this is not the case, or if you're not sure, please refer to the amplicons_no-overlap manual.

*Part I: filtering and merging*
-------------------------------

**STEP 1. Quality trimming and primer removal**
	In this step, you cut off bases with low quality. MiSeq reads usually have good qualities. On the other hand, there are gonna be further quality filtering later, so there's no need to be too stringent. We'll also remove primer sequences and reads that do not contain the primers. 

The command:

	cutadapt -g ^<forward primer> -G ^<reverse primer> --no-indels -O <length of shortest primer> -q <quality cutoff> --discard-untrimmed -m <minimal length> -o <output forward> -p <output reverse> <input forward> <input reverese>

Example:

	cutadapt -g ^CCTACGGGNGGCWGCAG -G ^GACTACHVGGGTATCTAATCC --no-indels -O 17 -q 15 --discard-untrimmed -m 200 -o trimmed_1.fq -p trimmed_2.fq reads_1.fq reads_2.fq


**STEP 2: Merging**
	In this step we will merge the forward and reverse reads into a single amplicon. When the overlap is perfect, they will simply be combined; where there are differences, the base with the highest Phred-score will be chosen. A new probability score will also be calculated for the bases in the overlap region. You can set a maximum limit of how many bases can be different between the reads in the overlap region without discarding the read pair. Think about the size of your expected overlap and the percentage of errors you find acceptable. If you choose not to set this value, there will be no upper limit (every read will be kept, no matter the differences).

The command:

	vsearch -fastq_mergepairs <forward_reads> -reverse <reverse_reads> -fastq_maxdiffs <maximum number of different bases> -fastqout <outfile>

Example

	vsearch -fastq_mergepairs trimmed_1.fq -reverse trimmed_2.fq -fastq_maxdiffs 6 -fastqout merge.fq


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

The command

	cat <all_fasta_files> > <outfile>

Example

	cat filtr1.fa filtr2.fa filtr3.fa > all.fa

**STEP 5: Dereplication**
	Here we combine all reads that are identical into a single one, keeping track of how many copies there are of each one. We'll also discard sequences that only show up once in the entire dataset, as they're very likely to be errors. This saves a lot of time down the road. We'll also give our OTU a better name than the standard read names.

The command:

	vsearch -derep_fulllength <infile> -output <outfile> -minuniquesize <minimal abundance> --relabel <label>
	
Example

	vsearch -derep_fulllength all.fa -output uniques.fa -minuniquesize 1 --relabel OTU-



**STEP 6: Clustering**
	Here we cluster our reads by similarity. Usearch uses average-linkage clustering, which means that it is possible that two sequences that are closer to each other than the similarity threshold can still end up in different OTU. One way to minimize this risk is to cluster at a higher similarity first, and then gradually expand these clusters.
	If you're having memory problems, you can use -cluster_smallmem instead of cluster_fast. This is slightly less accurate, and will require that you sort your sequences by length before clustering. 

The command:
	vsearch -cluster_smallmem <infile> -id <identity> -uc <uc_file> -idprefix <integer> -idsuffix <integer> --centroids <fasta output>

Example:
	vsearch -cluster_smallmem uniques.fa -id 0.99 -uc all.99.uc –centroids all.99.fa 

	vsearch -cluster_smallmem uniques.fa -id 0.98 -uc all.98.uc –centroids all.98.fa 


**STEP 7: Assigning reads to OTU**
	We will now look at each of our merged fastq files and assign them to OTU. At this point, take the opportunity to make a directory just for your new cluster files. This is important downstream. You're also requested to say how similar your sample must be to the centroid. This must be compatible with the similarity you used for clustering.

The command:

	vsearch -usearch_global <sample file> -db <numbered out file> -strand <plus/both> -id <similarity to the centroid> -uc <outfile>

Example:

	vsearch -usearch_global merge.fq -db all.98.fa -strand plus -id 0.98 -uc clusters/reads1.uc


**STEP 8: Classifying OTU**
	If you're working with 16S, I recommend using the online `RDP classifier <http://rdp.cme.msu.edu/classifier/classifier.jsp>`_. Download the fullrank result when you're done. You can also install RDP and run it locally. If you're working with 18S, 23S or 28S, I recommend the SINA classifier. Its `online version <http://www.arb-silva.de/aligner/>`_ only accepts 1000 sequences at a time. You can choose to divide your file into chunks of 1000 sequences, and then concatenate the results, or you can download and run the `SINA classifier locally <http://www.arb-silva.de/no_cache/download/archive/SINA/builds/2013/build-103/>`_. If you're using other databases, take a look at the 18S classification procedure and try to adapt it to your database.


**STEP 9: Creating an OTU table**
	Here we'll produce a table with OTUS on the lines, samples on the columns and the classification for each read and the sequence of the representative at the end of each line.

	If you use the RDP classifier, you can choose a confidence cut-off – classification assignments with lower confidence will be disregarded. Regardless of the classifier you also have the choice of assigning a fixed depth of classification, and all finer classifications will be disregarded. If you want the whole classification without any cut-offs, choose 0 as minimal confidence and a large number as maximum depth. If you don't give any parameters, a cut-off of 50% confidence will be taken for RDP files and a depth of 5 for Silva files.

	With online SINA you can choose different databases to use (EMBL, Greengenes, LTP, RDP and Silva, in this order). This script will only consider the last classification for each line, so consider that when choosing which databases to use.

	In all cases, you must choose which classifier was used: RDP (rdp), online SINA (sina-ol), standalone sina (sina-cl) or any other procedure generating a table with OTU on the leftmost column and classification on the rightmost (tsv)
	
	Every classification file that you want included in your OTU table should be in the same folder, and no other files should be in it.
	
	You also have the option of inputing sequence names at this step, if you don't want to use the file names as column headers in the results table.

The command:

	perl make_otu_tables.pl --names=<FILE> --threshold=INTEGER --samples=<FOLDER> --classification=<RDP_FILE> --sequences=<FASTA> --classifier=<classifier> > <output_file>

or

	perl make_otu_tables.pl --depth=INTEGER --samples=<FOLDER> --classification=<SINA_FILE> --sequences=<FASTA> --classifier=<sina-cl/sina-ol> > <output_file>


Example:

	perl make_otu_tables.pl --threshold=50 –samples=all_reads --classification=otus97.num.fa_classified.txt --sequences=otus97.num.fa --classifier=rdp > otu_table.tsv

or

	perl make_otu_tables.pl --depth=5 --samples=all_reads --classification=otus97.csv --sequences=otus97.num.fa --classifier=sina-ol --names=names.tsv > otu_table.tsv

**STEP 10: Elimiating 0 count OTUs**
	During assignment with usearch_global, some OTU that had been predicted earlier might end up with no reads assigned to them, since other OTU centroids had better matches to those reads. These make your OTU tables unnecessarily large, so you can eliminate them. The same approach can be used if you want to eliminate singletons at this step, for instance. We'll take the opportunity to fix a litte problem with the header line.
	
The command:

	awk 'NR>1{for(i=2;i<=(NF-2);i++) t+=$i; if(t>0){print $0}; t=0}' otu_table.tsv > temp
	
	sed '1s/ /\\t/g'  temp > otu_table.tsv
	
	rm temp
	
*PART V: BIOLOGY*
-----------------
It's beyond the scope of this tutorial to teach you how to draw biological conclusions from your OTU table. However, here are some useful links:

For visualizing your data in interactive hierarchical pie charts, use `Krona <http://sourceforge.net/p/krona/home/krona/>`_. For converting the OTU table you made here into a krona compatible input, use the script tsv2krona.py found in this repo and the ktImportText tool from krona.

For information and tutorials on statistical methods for analysis of microbial ecology, take a look at `Gustame <https://sites.google.com/site/mb3gustame/home>`_.

If you believe that there are interesting OTU that are worth looking deeper into for their specific ecology, consider `oligotyping <http://merenlab.org/projects/oligotyping/>`_.

If you're working with 16S in a well-characterized environments, such as the human microbiome, you can also consider `PiCrust <http://picrust.github.io/picrust/>`_ This repo also contains a guide on how to combine this approach with a PiCrust analysis.
