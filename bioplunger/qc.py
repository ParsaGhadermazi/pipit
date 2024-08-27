import bioplunger.configs as configs


def qc_fastp_(
    read1:str,
    read2:str|None,
    ourdir1:str,
    ourdir2:str|None,
    config:configs.Configs,
    paired:bool=True,
    container:str="none",
    **kwargs
    )->str:
    """
    This function ouputs a command to use fastp to quality control fastq files.

    Args:
        read1 (str): The path to the first fastq file
        read2 (str): The path to the second fastq file
        ourdir1 (str): The output directory for the first fastq file
        ourdir2 (str): The output directory for the second fastq file
        paired (bool): If the fastq files are paired
        container (str): The container to use
        **kwargs: Additional arguments to pass to fastp
    
    """
    if read2 is None and paired:
        raise ValueError("Paired reads must have two files")
    
    if read2 is None and ourdir2 is not None:
        raise ValueError("Paired reads must have two output directories")
    
    if paired:
        

