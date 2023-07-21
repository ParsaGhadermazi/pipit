import pathlib
import configs

def bwa_index(refrence: pathlib.Path,
              output_name: str,
              container:str="none",
              config:configs.Containers=configs.Containers())->str:
    """ This function will return the command to index the refrence genome using bwa.
    Args:
        refrence (pathlib.Path): The path to the refrence sequence file.
        output (str): The name of the output file.
        container (str): The name of the container to run the command in:
        choose from "none","singularity","docker".
    Returns:
        str: The command to index the refrence genome.

    """
    if not refrence.exists():
        raise FileNotFoundError(f"{refrence} not found")

    if container == "none":
        cmd = f"bwa index {str(refrence)} -p {output_name}"

    elif container == "singularity":
        cmd = f"singularity exec --bind {str(refrence.parent)}:{str(refrence.parent)} {config.singularity['bwa']} bwa index {str(refrence)} -p {output_name}"
    
    elif container == "docker":
        cmd = f"docker run -v {str(refrence.parent)}:{str(refrence.parent)} {config.docker['bwa']} bwa index {str(refrence)} -p {output_name}"
    
    return cmd
        

def bwa_align(refrence: pathlib.Path,
              fastq: pathlib.Path,
              output_file: pathlib.Path,
              container:str="none",
              number_of_threads:int=1,
              config:configs.Containers=configs.Containers())->str:
    """ This function will return the command to align the fastq file to the refrence genome using bwa.
    Args:
        refrence (pathlib.Path): The path to the refrence sequence file.
        fastq (pathlib.Path): The path to the fastq file.
        output_file (pathlib.Path): The path to the output file.
        container (str): The name of the container to run the command in:
        choose from "none","singularity","docker".
        number_of_threads (int): The number of threads to use.
    Returns:
        str: The command to align the fastq file to the refrence genome.

    """
    if not refrence.exists():
        raise FileNotFoundError(f"{refrence} not found")
    
    if not fastq.exists():
        raise FileNotFoundError(f"{fastq} not found")
    
    if container == "none":
        cmd = f"bwa mem -t {number_of_threads} {str(refrence)} {str(fastq)} > {str(output_file)}"
    
    elif container == "singularity":
        cmd = f"singularity exec --bind {str(refrence.parent)}:{str(refrence.parent)} {config.singularity['bwa']} bwa mem -t {number_of_threads} {str(refrence)} {str(fastq)} > {str(output_file)}"

    elif container == "docker":
        cmd = f"docker run -v {str(refrence.parent)}:{str(refrence.parent)} {config.docker['bwa']} bwa mem -t {number_of_threads} {str(refrence)} {str(fastq)} > {str(output_file)}"
    
    return cmd


