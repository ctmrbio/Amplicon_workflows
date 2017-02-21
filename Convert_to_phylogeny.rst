This workflow uses a lot of different tools that are themselves well documented. 
We will therefore only give one example of usage, but the user can refer to the documentation
to adjust it to their use case.

Tools you'll need to set up a new reference library:
 * Seqmagik
 * FastTree or another tree building algorithm
 * Taxtastic
 * (Optional) Degeprime

Tools you'll need for running each new sample batch:
 * ClustalO or another multiple sequence aligner
 * Pplacer
 * Guppy

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

**STEP 2: Align OTU to reference alignment**

**STEP 3: Run pplacer**

**STEP 4: Reduplicate**

**STEP 5: Run guppy**
