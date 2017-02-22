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

**STEP 2: Align OTU to reference alignment**

**STEP 3: Run pplacer**

**STEP 4: Reduplicate**

**STEP 5: Run guppy**
