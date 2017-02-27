Amplicon workflows
=========

Workflows for amplicon data processing, often based on 3rd party software.
All custom scripts mentioned in the tutorials are also included in this folder.

Amplicons_overlap uses [unoise](http://www.drive5.com/usearch/manual/unoise_pipeline.html) to process amplicon libraries where the forward and reverse sequencing reads overlap.

Amplicons_no-overlap does the same for the case where the reads don't (or rarely) overlap. This one is more convoluted, so do try to get overlaps. **this text is not up-to-date**

Quick_picrust helps you prepare your data for [picrust](http://picrust.github.io/picrust/) analysis if you absolutely refuse to use Qiime or Mothur.

Convert_to_phylogeny is a guide to calculating Unifrac like statistics from your OTU table.
