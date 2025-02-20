# Rule all that collects the final output to trigger all steps
rule all:
    input:
        expand("tmp/completion/{genomes_file}_binned.done", genomes_file=glob_wildcards("input/{genomes_file}.txt").genomes_file)

# Rule to sketch genomes and create sketches
rule sketch_genomes:
    input:
        genomes_file="input/{genomes_file}.txt"
    output:
        completion_marker="tmp/completion/{genomes_file}_completed.done"
    shell:
        """
        # Clear and recreate necessary directories
        rm -rf tmp/sketches/*
        mkdir -p tmp/sketches tmp/completion

        # Run Dashing to generate sketches from the genome list file
        dashing sketch -F {input.genomes_file}

        # Mark completion of the rule
        touch {output.completion_marker}
        """

# Rule to move HLL files to the target folder
rule move_hll_files:
    input:
        genomes_file="input/{genomes_file}.txt",
        sketch_done="tmp/completion/{genomes_file}_completed.done"  # This ensures it depends on sketching being done
    output:
        completion_marker="tmp/completion/{genomes_file}_hll_moved.done"
    shell:
        """
        # Move all generated .hll files corresponding to each genome prefix using a for loop
        for genome in $(cat {input.genomes_file}); do
            base_name=$(basename "$genome")
            dir_name=$(dirname "$genome")

            # Move all .hll files corresponding to each genome prefix using a for loop
            mv "$dir_name"/"$base_name"*.hll tmp/sketches/ 2>/dev/null || true
        done

        # Mark completion of the rule
        touch {output.completion_marker}
        """

# Rule to bin the HLL sketches using First-Fit HyperLogLog
rule bin_hll_sketches:
    input:
        sketches_dir="tmp/sketches",
        hll_moved="tmp/completion/{genomes_file}_hll_moved.done"
    output:
        bin_assignment="output/{genomes_file}_bin_assignment.txt",  # Wildcard included
        completion_marker="tmp/completion/{genomes_file}_binned.done"  # Matching wildcard
    params:
        bin_capacity=2e7  # Adjust as needed
    shell:
        "python scripts/first_fit_hyperloglog.py {params.bin_capacity} {wildcards.genomes_file}"
