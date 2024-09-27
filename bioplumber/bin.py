from bioplumber import configs
from pathlib import Path as Path

def get_contig_coverage_metabat_(bam_file:str,
                                 out_dir:str, 
                                 config:configs.Configs,
                                 container:str="none")->str:
    
    """
    This function will return the script to generate the coverage of contigs using metabat2.
    
    Args:
    bam_file (str): The path to the bam file.
    out_dir (str): The path to the output directory.
    config (configs.Configs): The configuration object.
    container (str): The container to use. Default is "none".
    
    Returns:
    str: The script to generate the coverage of contigs using metabat2.
    
    """
    bam_file = str(Path(bam_file).resolve().absolute())
    out_dir = str(Path(out_dir).resolve().absolute())
    if container == "none":
        command = f"jgi_summarize_bam_contig_depths --outputDepth {out_dir} {bam_file}"

    elif container == "docker":
        command = f"docker run -v {bam_file}:{bam_file} -v {out_dir}:{out_dir} {config.metabat_docker} jgi_summarize_bam_contig_depths --outputDepth {out_dir} {bam_file}"
    
    elif container == "singularity":
        command = f"singularity exec {config.metabat_singularity} jgi_summarize_bam_contig_depths --outputDepth {out_dir} {bam_file}"
    
    else:
        raise ValueError("Invalid container")
    
    return command        
    
def bin_with_coverage_table_metabat2_(
    contigs_file:str,
    depth_file:str,
    out_dir:str,
    config:configs.Configs,
    container:str="none")->str:
    """
    This function will return the script to bin contigs using metabat2.

    Args:
    contigs_file (str): The path to the contigs file.
    depth_file (str): The path to the depth file.
    out_dir (str): The path to the output directory.
    config (configs.Configs): The configuration object.
    container (str): The container to use. Default is "none".
    
    Returns:
    str: The script to bin contigs using metabat2.
    """
    contigs_file = str(Path(contigs_file).resolve().absolute())
    depth_file = str(Path(depth_file).resolve().absolute())
    out_dir = str(Path(out_dir).resolve().absolute())
    if container == "none":
        command = f"metabat2 -i {contigs_file} -a {depth_file} -o {out_dir}"
    
    elif container == "docker":
        command = f"docker run -v {contigs_file}:{contigs_file} -v {depth_file}:{depth_file} -v {out_dir}:{out_dir} {config.metabat_docker} metabat2 -i {contigs_file} -a {depth_file} -o {out_dir}"
    
    elif container == "singularity":
        command = f"singularity exec {config.metabat_singularity} metabat2 -i {contigs_file} -a {depth_file} -o {out_dir}"
    
    else:
        raise ValueError("Invalid container")
