import pathlib
import conf
from typing import Iterable
import subprocess
import json

def bwa_index(refrence: pathlib.Path,
              output_name: str,
              container:str="none",
              config:conf.Containers=conf.Containers())->str:
    """ This function will return the command to index the refrence genome using bwa.
    Args:
        refrence (pathlib.Path): The path to the refrence sequence file.
        output (str): The name of the output file.
        container (str): The name of the container to run the command in:
        choose from "none","singularity","docker".
    Returns:
        str: The command to index the refrence genome.

    """

    if container == "none":
        cmd = f"bwa index {str(refrence)} -p {output_name}"

    elif container == "singularity":
        cmd = f"singularity exec --bind {str(refrence.parent)}:{str(refrence.parent)} {config.singularity['bwa']} bwa index {str(refrence)} -p {output_name}"
    
    elif container == "docker":
        cmd = f"docker run -v {str(refrence.parent)}:{str(refrence.parent)} {config.docker['bwa']} bwa index {str(refrence)} -p {output_name}"
    
    return cmd
        

def bwa_align(refrence: pathlib.Path,
                fastq_1: pathlib.Path,
                fastq_2: pathlib.Path,
                number_of_threads: int,
                output_file: pathlib.Path,
                container:str="none",
                config:conf.Containers=conf.Containers())->str:
                
    """ This function will return the command to align the fastq files to the refrence genome using bwa.
    Args:
        refrence (pathlib.Path): The path to the refrence sequence file.
        fastq_1 (pathlib.Path): The path to the first fastq file.
        fastq_2 (pathlib.Path): The path to the second fastq file.
        number_of_threads (int): The number of threads to use.
        output_file (pathlib.Path): The path to the output file.
        container (str): The name of the container to run the command in:
        choose from "none","singularity","docker".
    Returns:
        str: The command to align the fastq files to the refrence genome.
    """

    if container == "none":
        cmd = f"bwa mem -t {number_of_threads} {str(refrence.absolute())} {str(fastq_1.absolute())} {str(fastq_2.absolute())} > {str(output_file.absolute())}"

    elif container == "singularity":
        cmd = f"singularity exec --bind {str(refrence.parent.absolute())}:{str(refrence.parent.absolute())} {config.singularity['bwa']} bwa mem -t {number_of_threads} {str(refrence.absolute())} {str(fastq_1.absolute())} {str(fastq_2.absolute())} > {str(output_file.absolute())}"

    elif container == "docker":
        cmd = f"docker run -v {str(refrence.parent.absolute())}:{str(refrence.parent.absolute())} {config.docker['bwa']} bwa mem -t {number_of_threads} {str(refrence.absolute())} {str(fastq_1.absolute())} {str(fastq_2.absolute())} > {str(output_file.absolute())}"
    
    return cmd

def sam2bam(sam_file: pathlib.Path,
            output_file: pathlib.Path,
            container:str="none", 
            config:conf.Containers=conf.Containers()
            ) -> str:   
    """ This function will return the command to convert a sam file to a bam file.
    Args:
        sam_file (pathlib.Path): The path to the sam file.
        output_file (pathlib.Path): The path to the output file.
        container (str): The name of the container to run the command in:
        choose from "none","singularity","docker".
        config (conf.Containers): The configuration for the containers.
    Returns:
        str: The command to convert a sam file to a bam file.
    """

    if container == "none":
        cmd = f"samtools view -bS {str(sam_file.absolute())} > {str(output_file.absolute())}"

    elif container == "singularity":
        cmd = f"singularity exec --bind {str(sam_file.parent.absolute())}:{str(sam_file.parent.absolute())} {config.singularity['samtools']} samtools view -bS {str(sam_file.absolute())} > {str(output_file.absolute())}"
    
    elif container == "docker":
        cmd = f"docker run -v {str(sam_file.parent.absolute())}:{str(sam_file.parent.absolute())} {config.docker['samtools']} samtools view -bS {str(sam_file.absolute())} > {str(output_file.absolute())}"
    
    return cmd

def sort_bam(bam_file: pathlib.Path,
                output_file: pathlib.Path,
                container:str="none",
                config:conf.Containers=conf.Containers()
                ) -> str:
    """ This function will return the command to sort a bam file.
    Args:
        bam_file (pathlib.Path): The path to the bam file.
        output_file (pathlib.Path): The path to the output file.
        container (str): The name of the container to run the command in:
        choose from "none","singularity","docker".
        config (conf.Containers): The configuration for the containers.
    Returns:
        str: The command to sort a bam file.
    """
    
    if container == "none":
        cmd = f"samtools sort {str(bam_file.absolute())} > {str(output_file.absolute())}"
    
    elif container == "singularity":
        cmd = f"singularity exec --bind {str(bam_file.parent.absolute())}:{str(bam_file.parent.absolute())} {config.singularity['samtools']} samtools sort {str(bam_file.absolute())} > {str(output_file.absolute())}"
    
    elif container == "docker":
        cmd = f"docker run -v {str(bam_file.parent.absolute())}:{str(bam_file.parent.absolute())} {config.docker['samtools']} samtools sort {str(bam_file.absolute())} > {str(output_file.absolute())}"
    
    return cmd

def index_sorted_bam(bam_file: pathlib.Path,
                    container:str="none",
                    config:conf.Containers=conf.Containers()
                    ) -> str:
    """ This function will return the command to index a sorted bam file.
    Args:
        bam_file (pathlib.Path): The path to the bam file.
        container (str): The name of the container to run the command in:
        choose from "none","singularity","docker".
        config (conf.Containers): The configuration for the containers.
    Returns:
        str: The command to index a sorted bam file.
    """

    if container == "none":
        cmd = f"samtools index {str(bam_file.absolute())}"
    
    elif container == "singularity":
        cmd = f"singularity exec --bind {str(bam_file.parent.absolute())}:{str(bam_file.parent.absolute())} {config.singularity['samtools']} samtools index {str(bam_file.absolute())}"

    elif container == "docker":
        cmd = f"docker run -v {str(bam_file.parent.absolute())}:{str(bam_file.parent.absolute())} {config.docker['samtools']} samtools index {str(bam_file.absolute())}"
    
    return cmd
                     
                    

def cut_up_fasta(fasta_file: pathlib.Path,
                container:str="none",
                config:conf.Containers=conf.Containers())->str:
    
    """ This function will return the command to cut up a fasta file for concoct.
    Args:
        fasta_file (pathlib.Path): The path to the assembly files to split.
        container (str): The name of the container to run the command in:
        choose from "none","singularity","docker".
        config (conf.Containers): The configuration for the containers.
    Returns:
        str: The command to cut up a fasta file for concoct.
    """

    if container == "none":
        cmd =f"cut_up_fasta.py {fasta_file.absolute()} -c 10000 -o 0 --merge_last -b contigs_10K.bed > contigs_10K.fa"
    
    elif container == "singularity":
        cmd =f"singularity exec --bind {str(fasta_file.parent.absolute())}:{str(fasta_file.parent.absolute())} {config.singularity['concoct']} cut_up_fasta.py {fasta_file.absolute()} -c 10000 -o 0 --merge_last -b contigs_10K.bed > contigs_10K.fa"
    
    elif container == "docker":
        cmd =f"docker run -v {str(fasta_file.parent.absolute())}:{str(fasta_file.parent.absolute())} {config.docker['concoct']} cut_up_fasta.py {fasta_file.absolute()} -c 10000 -o 0 --merge_last -b contigs_10K.bed > contigs_10K.fa"
    
    return cmd






def get_slurm_queue_status(keys_to_include:Iterable=["name","job_id","job_state"])->list:
    """ This function will return the status of the slurm queue.
    Args:
        keys_to_include (Iterable): The keys to include in the output.
    Returns:
        list: The status of the slurm queue.
    """
    out=[]
    f=subprocess.check_output(["squeue -u $USER --json"],shell=True)
    f=json.loads(f)["jobs"]
    for i in f:
        out.append({key:i[key] for key in keys_to_include})
    return out