Combining picrust with a vsearch-based approach
===============================================

`PiCrust <http://picrust.github.io/picrust/>`_ is a good piece of software for predicting the functional profiles of 
_bacterial_ communities, based on _16S sequencing_, if _most species in the environment are known_. If any of these 
criteria doesn't apply to your samples (if you used a different gene, if eukaryotes are important, or if >30% of your sequences
don't match to the `Greengenes <http://greengenes.secondgenome.com/downloads>`_ database, I can't recommend this approach.

Start by installing PiCrust and the associated libraries as explained `here <picrust.github.io/picrust/install.html>`_.

You'll also need to install `biom <http://biom-format.org/>`_ if you later want to export the PiCrust results to tsv.

**Preparation**
Set a variable corresponding to the path to the greengene references you've downloaded, such as
  DB=/path/to/gg_13_5_otus

**STEP 1: Selecting a subset of greengenes**
Start from a set of quality controled, merged, dereplicated sequences corresponding to your whole sample, 
such as is produced in Step 5 of the `regular amplicon workflow <https://github.com/ctmrbio/Amplicon_workflows/blob/master/amplicons-overlap.rst>`_.

  vsearch -usearch_global uniqs.fasta -db $DB/rep_set/99_otus.fasta -id 0.99 -uc map99.uc -strand both --dbmatched gg_matched.fa --matched=gg_centroids.fa

This is the slowest step in this workflow and can take up to a few hours. It will, however, save you up to 
a couple of days of computing time downstream.

The output gg_centroids.fa can continue to downstream processing by the standard amplicon workflow, since GreenGenes 
hasn't been updated in a few years and doesn't provide good resolution classification.

**STEP 2: Map reads to this subset**
Map each of your merged reads to the subset of Greengenes selected above. 
It's important to have a directory only for the mapping results.

  mkdir maps
  
  vsearch -usearch_global sample1.merge.fq -db gg_matched.fa -id 0.99 -uc maps/sample1.uc -strand both

**STEP 3: Build an OTU table from the matches**

  grep '^>' gg_matched.fa > matched.tsv
  
  perl /home/luisah/amplicons/extract_sample.pl --sample=matched.tsv --database=$DB/parse_db/99_otu_tax.tsv --type=tsv > matched_tax.tsv
 
  perl /home/luisah/Tutorials/otu_tables --classifier=tsv --samples=maps --classification=matched_tax.tsv --sequences=gg_matched.fa > full_table.tsv
  
  awk '{for(i=0;++i<NF-2;)printf $i"\t";print $(NF-2)}'  full_table.tsv > pi_table.tsv

**STEP 4: Run Picrust**

  ~/picrust-1.1.0/scripts/normalize_by_copy_number.py -f -i pi_table.tsv -o norm_table.biom

  ~/picrust-1.1.0/scripts/predict_metagenomes.py -i norm_table.biom -o metagenome.biom

  biom convert -i  metagenome.biom -o metagenomes.tsv --to-tsv

**OBS:** If you get an error at normalize_by_copy_number.py, run instead
  biom convert -i pi_table.tsv -o pi_table.biom --to-json

  ~/picrust-1.1.0/scripts/normalize_by_copy_number.py -i pi_table.biom -o norm_table.biom
 
 and then proceed to the next steps
 



