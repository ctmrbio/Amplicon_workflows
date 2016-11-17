Processing amplicons with non-overlapping reads
===============================================
This is a quick guide on how to use Usearch7 to go from fastq files all the way to a table of OTUs. This is based chiefly on the programmes `FastQC <http://www.bioinformatics.babraham.ac.uk/projects/fastqc/>`_ and `Vsearch <https://github.com/torognes/vsearch>`_. Also refer to this page for download and installation instructions. I'm going to assume in this manual that you can call vsearch and cutadapt simply by typing the programme names, but this depends on the folder where you have installed it, how you have named it and the folder you're in.

This guide is to be used if your forward and reverse reads do not overlap or if you're not sure if that's the case. If you know you have an overlap, please refer to the Usearch_overlap.pdf manual. If you're still planning your experiment, do your best to have an overlap.



*PART I: FILTERING AND MERGING*
-------------------------------

**STEP 1: Quality statistics**
	In the next step, you will have to decide how many bases you want to cut off from the end of your reads, to simultaneously preserve as many bases as possible and guarantee the quality of your reads. Therefore, in this step, you simply get some statistics on quality. For this, you can use Usearch, Vsearch, Fastx, FastQC and others. If using Usearch7, the statistics are explained at length `here <http://www.drive5.com/usearch/manual/fastq_stats.html>`_. For FastQC, `check here <http://www.bioinformatics.babraham.ac.uk/projects/fastqc/>`_. FastQC produces an html report that should be opened on a browser.

The command: 
	fastqc -o <output_directory> --noextract --nogroup <infiles>

Example:
	fastqc -o fastqc --noextract --nogroup file1_r1.fastq file1_R2.fastq file2_R1.fastq file2_R2.fastq


**STEP 2. Quality trimming**
	In this step, you cut off bases with low quality and trim all reads to the same length. You can use different lengths for the forward and reverse reads, but you should use the same cut-off for every sample you intend to compare. You can also choose to throw away sequences that have too low quality. These cutoffs should be decided based on your FastQC reports. We'll also remove our primer sequences.

The command:
	vsearch --fastq_filter <infile> --fastq_maxee_rate <max error rate per read> --fastq_stripleft <length of primer>  --fastq_trunclen <length to keep> --fastq_minlen <length to keep> --fastaout <output file>

Example:
	vsearch --fastq_filter file1_R1.fastq --fastq_maxee_rate 0.01 --fastq_stripleft 18 --fastq_trunclen 270 --fastq_minlen 270 --fastaout reads1_R1.fa

	
	vsearch --fastq_filter file1_R2.fastq --fastq_maxee_rate 0.01 --fastq_stripleft 18 --fastq_trunclen 270 --fastq_minlen 270 --fastaout reads1_R2.fa

**STEP 3: Synchronizing files**
	After the trimming is done, we might have discarded some forward or reverse reads and not their partners. At this point, we correct this problem with a custom script. It selects the output file name automatically by adding the suffix "sync"

The comand:
	perl resync_fastx.pl --file1=<fwd_fasta> --file2=<rev_fasta> > <output_fasta>

Example:
	perl resync_fastx.pl --file1=reads1_R1.fa --file2=reads1_R2.fasta

**STEP 4: Concatenating reads**
	In this step we will concatenate the forward and reverse reads into a single artificial amplicon. You can include a separator between them, so they can be split later. Due to downstream applications, this separator can only contain the letters A, C, T, G, N. Keep in mind that the spacer you choose should be rare (long) enough that it's not likely to appear at random in your reads. However, if your forward reads have all been trimmed to the same size, you can skip the spacer and do the splitting based on length. Notice that the outfile names are defined automatically; this will be changed soon.

The command:
	perl cat_reads --revcom --file1=<forward_reads> --file2=<reverse_reads> > <output_file>

Example
	perl cat_reads --revcom --file1=reads_R1.fa --file2=reads_R2.fa > reads_cat.fa

*PART II: CLUSTERING*
---------------------
	
**STEP 5: File concatenation**
	In most applications, you want to compare communities from different environments, conditions etc. For this, you have to have the same OTU defined for all samples. Therefore, at this point we concatenate all files.

The command:
	cat <all_fasta_files> > <outfile>

Example:
	cat reads1.fa reads2.fa reads3.fa > all.fa

**STEP 6: Dereplication**
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



**STEP 8: Splitting the concatenated reads**
	Now that we've assigned the reads to OTU, we have to split them again to be able to assign them a taxonomy. 

The command:
	perl uncat_reads.pl --length=<length> --in=<infile> --out1=<fwd_file> --out2=<rev_file>

Example:
	perl uncat_reads.pl --length=252 --in=all.98.fa --out1=all98_R1.fa --out2=all98_R2.fa

*PART III: CLASSIFYING*
-----------------------

**If you're working on 18S reads:**
Please refer to the `18S taxonomy workflow <https://github.com/EnvGen/Tutorials/blob/master/18S_taxonomy.rst>`_ and then proceed to Part IV here. Otherwise, follow Steps 9 and 10 as described below.


**STEP 9: Classifying OTU**
	There are many tools for assigning taxonomy to a read. Here we use the `SINA classifier <http://www.arb-silva.de/aligner/>`_. Its online version only accepts 1000 sequences at a time. You can choose to divide your file into chunks of 1000 sequences, and then concatenate the results, or you can download and run the SINA classifier locally.


**STEP 10: Parsing taxonomy**
	The taxonomy assigned to a forward read won't always agree with the reverse read. What we do here is to take the part in which both agree.

The command:
	perl sina2otu.pl --pair --sina=<sina_csv_table> --sina2=<sina_csv_table> > <outfile>

Example:
	perl sina2otu.pl --pair --sina=all_R1.97.csv –sina2=all_R2.97.csv > all.97.tsv

*PART IV: OTU TABLES*
-----------------------

**STEP 11: Making OTU tables**
	Here we'll produce a table with OTUS on the lines, samples on the columns and the classification for each read and the sequence of the representative at the end of each line.

	If you use the RDP classifier, you can choose a confidence cut-off – classification assignments with lower confidence will be disregarded. Regardless of the classifier you also have the choice of assigning a fixed depth of classification, and all finer classifications will be disregarded. If you want the whole classification without any cut-offs, choose 0 as minimal confidence and a large number as maximum depth. If you don't give any parameters, a cut-off of 50% confidence will be taken for RDP files and a depth of 5 for Silva files.

	With online SINA you can choose different databases to use (EMBL, Greengenes, LTP, RDP and Silva, in this order). This script will only consider the last classification for each line, so consider that when choosing which databases to use.

	In all cases, you must choose which classifier was used: RDP (rdp), online SINA (sina-ol), standalone sina (sina-cl) or any other procedure generating a table with OTU on the leftmost column and classification on the rightmost (tsv). Choose tsv if you follwed the 18S taxonomy procedure.
	
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

**STEP 12: Elimiating 0 count OTUs**
	During assignment with usearch_global, some OTU that had been predicted earlier might end up with no reads assigned to them, since other OTU centroids had better matches to those reads. These make your OTU tables unnecessarily large, so you can eliminate them. The same approach can be used if you want to eliminate singletons at this step, for instance. We'll take the opportunity to fix a litte problem with the header line.
	
The command:

	awk 'NR>1{for(i=2;i<=(NF-2);i++) t+=$i; if(t>0){print $0}; t=0}' otu_table.tsv > temp
	
	sed '1s/ /\\t/g'  temp > otu_table.tsv
	
	rm temp

*PART V: BIOLOGY*
-----------------
It's beyond the scope of this tutorial to teach you how to draw biological conclusions from your OTU table. However, here are some useful links:

For visualizing your data in interactive hierarchical pie charts, use `Krona <http://sourceforge.net/p/krona/home/krona/>`_.

For information and tutorials on statistical methods for analysis of microbial ecology, take a look at `Gustame <https://sites.google.com/site/mb3gustame/home>`_.

If you believe that there are interesting OTU that are worth looking deeper into for their specific ecology, consider `oligotyping <http://merenlab.org/projects/oligotyping/>`_.
