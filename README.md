# HLL-Binning
HyperLogLog-based first-fit bin packing for genomes

## Prerequisites

- Snakemake
- Dashing: Hyperloglog based sketching tool for genomes. Obtain the latest binary release for your system from https://github.com/dnbaker/dashing-binaries and move it to your $PATH
- Python3
- Bash

## Guide

HLL-Binning/
├── Snakefile             # Snakemake workflow definition
├── input/                # Directory for genome files (e.g., .fa or .fq files)
│   └── my_batch.txt      # List of genome file names
├── tmp/                  # Temporary files during workflow execution
│   ├── sketches/         # Generated HLL sketches
│   ├── completion/       # Completion markers for each rule
│   └── bins/             # Binned sketches after First-Fit algorithm
├── output/               # Final output files
│   └── my_batch_bin_assignment.txt  # Bin assignments for each genome
└── scripts/              # Python scripts (e.g., `first_fit_hyperloglog.py`)

### Step 1: 
Sketch Genomes and move all .hll files into tmp/sketches/.

### Step 2: Bin genomes using HLL Sketches

Use First-Fit HyperLogLog binning algorithm to sketch files and assign them to bins.

### Side note : Clean-up

Use scripts/clean_directories to clear output/ and tmp/ before running the workflow.


### Output Files
    output/{genomes_file}_bin_assignment.txt