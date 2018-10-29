We at `CTMR <https://ki.se/en/research/centre-for-translational-microbiome-research-ctmr>`_ 
adopt the `SILVA <https://www.arb-silva.de/>`_ taxonomy as our gold standard for 16S-based projects.
However, SILVA is only reliable down to the genus level, since it incorporates species-level information
from users, which has many problems, the main one being that whole genome projects are often contaminated by 
small amounts of other bacteria, so 16S contigs are assembled under a species that belong to another. In other
cases, the species-level information is lacking, and is replaced by an ecological or functional annotation. While
this is useful in its context, it isn't necessarily informative.

Therefore, `we <https://scholar.google.com/citations?user=7JXgYtsAAAAJ&hl=en>`_ have made an attempt to remedy this
situation by removing non-informative annotations. Before you proceed, please be aware of the following caveats:

* This work is essentially driven by a single person, and is bound to have some errors and omissions
* The Eukaryotic taxonomy isn't affected by the procedures described here. Feel free to develop a similar approach for Eukaryotes if this is within your expertise, or consider `specialised databases <http://eukref.org/databases/>`_
* The clean-up script is developed and tested for SILVA v.132, and will not perform as well with earlier or later versions. It should however not be hard to adapt it.
* Only minimal changes have been done to Cyanobacteria and Enterobacteriaceae, since these clades are notably messy
* Generally, a species-level annotation is only removed if it conflicts with a order-level annotation or higher. If the order is correct, but the family or genus are in conflict with the species, we don't see 16S evidence as strong enough alone to overrule the work of the original researchers.
* While species and sometimes strain-level annotations are kept in the database, please use your critical thinking skills. 300 bp of a single gene will never afford you strain-level resolution. 
* Feel free to open an issue if you believe further curation is needed to the final taxonomy.
* Feel free to make a pull request speeding up the current scripts.

Preparation Steps
-----------------

This will only need to be done once.

1. Download and extract the necessary files
...........................................

`SILVA Nr99 132 SSU database
<https://www.arb-silva.de/fileadmin/silva_databases/release_132/Exports/SILVA_132_SSURef_Nr99_tax_silva_trunc.fasta.gz>`_

`Auxilary file <https://raw.githubusercontent.com/ctmrbio/Amplicon_workflows/master/resources/contaminating_seqs.tsv>`_

`Clean-up script <https://raw.githubusercontent.com/ctmrbio/Amplicon_workflows/master/scripts/clean_silva.py>`_

2. Select only the taxonomy
............................

.. code::

  gunzip SILVA_132_SSURef_Nr99_tax_silva_trunc.fasta.gz
  grep '^>' SILVA_132_SSURef_Nr99_tax_silva_trunc.fasta | sed 's/ /\t/' > SILVA_132_SSURef_Nr99.tax.tsv
  
3. Run the clean-up script
..........................

.. code::

  python clean_silva.py -i SILVA_132_SSURef_Nr99.tax.tsv -o SILVA_132_SSURef_Nr99.tax.clean.tsv -a contaminating_seqs.tsv

Taxonomy assignment
-------------------

The following steps were developed by `Yue O.O. Hu <https://scholar.google.se/citations?user=cm4tmKkAAAAJ&hl=en>`_ for Eukaryotic
taxonomy based on the `PR2 <https://figshare.com/articles/Protist_Ribosomal_Reference_database_PR2_-_SSU_rRNA_gene_database/5913181>`_
database and were extended by `Luisa W. Hugerth <https://scholar.google.com/citations?user=7JXgYtsAAAAJ&hl=en>`_ 
to its current 16S/SILVA-based format.

1: Mapping OTU to a curated database
....................................

Use vsearch or a similar tool to map your amplicons to the database as fast as Usearch would, but produce a blast-like output.

Example::

    vsearch --usearch_global centroids.fa -db SILVA_132_SSURef_Nr99_tax_silva_trunc.fasta --blast6out centroids2silva.blast --id 0.9 --maxaccepts 45

2. Parse the taxonomy
.....................

The trick here is that we'll parse the same mapping result att diferent levels of similarity and keep the best classification possible for the level of similarity found. The similarity levels presented here work well in our experience, but they're not universal for all clades. Specific research questions might require optimizing them.

The script was originally meant for unmerged reads, therefore the ``-1`` and ``-2`` flags. Just repeat the same input file twice if reads were merged.

Example::

    SIMS=(90 95 97 99 100) for sim in ${SIMS[@]}; do
        python taxonomy_blast_parser.py -1 centroids2silva.blast -2 centroids2silva.blast -id $sim -tax silva_128_Nr99_no-euk_curated.tsv -l1 350 -l2 350 > parse.${sim}.out
    done
    python combine_taxonomy.py -i parse.100.out,parse.99.out,parse.97.out,parse.95.out,parse.90.out -n strain,species,genus,class,phylum -d 8,7,6,3,2 > taxonomy.out

