import subprocess
import os
import glob
import sys

def get_cardinality(sketch):
    """
    Get the cardinality of a given HLL sketch using Dashing.
    
    :param sketch: Path to the HLL sketch file.
    :return: Estimated cardinality (integer).
    """
    result = subprocess.run(["dashing", "card", "--presketched", sketch], 
                            capture_output=True, text=True, check=True)
    result = result.stdout.strip().split('\t')[-1]
    return float(result)

def union_sketch(bin_sketch, genome_sketch, output_sketch):
    """
    Compute the union of two HLL sketches and save it as a new sketch.
    """
    subprocess.run(["dashing", "union", "-o", output_sketch, bin_sketch, genome_sketch],
                    check=True, stdout=subprocess.DEVNULL)


def extract_genome_name(filepath):
    """
    Extract the genome name from a given file path.

    Example:
    path/to/file/SAMEA897824.fa.gz.w.31.spacing.10.hll → SAMEA897824
    """
    filename = os.path.basename(filepath)  # Get the file name
    parts = filename.split(".")  # Split by '.'
    # Find the first part that does not contain known extensions
    for part in parts:
        if part not in ["fa", "fq", "gz", "w", "31", "spacing", "10", "hll"]:
            return part  # Return the first valid part as genome name

    return filename  # If nothing found, return original filename

def firstfit_hyperloglog(bin_capacity, sketches_dir="tmp/sketches", bin_dir="tmp/bins"):
    """
    First-Fit bin packing algorithm for HyperLogLog genome sketches.

    :param bin_capacity: Maximum allowed cardinality per bin.
    :param sketches_dir: Directory containing genome HLL sketches.
    :param bin_dir: Directory where bin sketches will be stored.
    :return: List of bins (each bin is a list of genome names assigned to it).
    """
    os.makedirs(bin_dir, exist_ok=True)

    # Get all .hll files in tmp/sketches
    genome_sketches = sorted(glob.glob(os.path.join(sketches_dir, "*.hll")))

    bin_result = []  # A list of lists, each sub-list is a bin containing genome names
    bin_paths = []   # A list storing paths of the bin sketches
    bin_cardinalities = []  # A list storing the cardinality of each bin

    if not genome_sketches:
        return bin_result,bin_cardinalities  # No genomes to process

    # Initialize first bin
    first_sketch = genome_sketches[0]
    genome_name = extract_genome_name(first_sketch)  # Extract genome name
    bin_result.append([genome_name])  # Create first bin

    # Copy the first sketch into bin_0.hll
    bin_0_path = os.path.join(bin_dir, "bin_0.hll")
    subprocess.run(["cp", first_sketch, bin_0_path], check=True)
    bin_paths.append(bin_0_path)  # Store bin path

    # Mark bins as available
    bin_available = [True]

    # Get initial cardinality
    initial_cardinality = get_cardinality(bin_0_path)
    bin_cardinalities.append(initial_cardinality)  # Store initial cardinality

    # Process remaining genomes
    for genome_sketch in genome_sketches[1:]:
        genome_name = extract_genome_name(genome_sketch)
        placed = False
        print('Binning', genome_name)

        # Try placing in an existing bin
        for i, bin_path in enumerate(bin_paths):
            if bin_available[i]:  # Check if the bin is still available
                temp_union_path = os.path.join(bin_dir, f"temp_bin.hll")
                
                # Compute union of bin and genome
                union_sketch(bin_path, genome_sketch, temp_union_path)
                
                # Get cardinality of the new union sketch
                union_card = get_cardinality(temp_union_path)

                if union_card <= bin_capacity:
                    # Update the bin with the new union sketch
                    subprocess.run(["mv", temp_union_path, bin_path], check=True)
                    bin_result[i].append(genome_name)
                    bin_cardinalities[i] = union_card  # Update cardinality
                    if union_card >= 0.95 * bin_capacity:
                        bin_available[i] = False
                    placed = True
                    break  # Stop checking further bins

        # If no existing bin can hold the genome, create a new bin
        if not placed:
            new_bin_index = len(bin_result)
            new_bin_path = os.path.join(bin_dir, f"bin_{new_bin_index}.hll")

            # Copy genome sketch as new bin
            subprocess.run(["cp", genome_sketch, new_bin_path], check=True)

            bin_result.append([genome_name])
            bin_paths.append(new_bin_path)
            bin_available.append(True)
            # Get the new bin's cardinality
            new_cardinality = get_cardinality(new_bin_path)
            bin_cardinalities.append(new_cardinality)

    return bin_result,bin_cardinalities


if __name__ == "__main__":
    
    sketches_dir = "tmp/sketches"
    bin_dir = "tmp/bins"
    bin_capacity = float(sys.argv[1])
    file_name = sys.argv[2]

    bins, cardinalities = firstfit_hyperloglog(bin_capacity, sketches_dir, bin_dir)

    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)

    # Save bin assignments to output/bin_assignment.txt
    with open(f'output/{file_name}_bin_assignment.txt', "w") as f:
        for i, (bin_content, bin_card) in enumerate(zip(bins, cardinalities)):
            f.write(f"Bin {i}: {', '.join(bin_content)}; Cardinality: {bin_card}\n")

    # Create completion marker
    open(f'tmp/completion/{file_name}_binned.done', "w").close()
