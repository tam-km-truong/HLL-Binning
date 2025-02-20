# HLL-Binning
HyperLogLog-based first-fit bin packing for genomes

## Prerequisites

- Snakemake
- Dashing: Hyperloglog based sketching tool for genomes. Obtain the latest binary release for your system from https://github.com/dnbaker/dashing-binaries and move it to your $PATH
- Python3
- Bash

## Guide

RUN WITH:

```
snakemake
```

### Step 1: 
Sketch Genomes and move all .hll files into tmp/sketches/.

### Step 2: Bin genomes using HLL Sketches

Use First-Fit HyperLogLog binning algorithm to sketch files and assign them to bins.

### Side note : Clean-up

Use scripts/clean_directories to clear output/ and tmp/ before running the workflow.


### Output Files
    output/{genomes_file}_bin_assignment.txt