from pathlib import Path as Path
from bioplumber import configs

def index_bowtie_(
    sequence_dir: str,
    database_dir: str,
    configs: configs.Configs,
    container: str = "none",
    **kwargs
    ) -> str:
    """
    This function ouputs a command to use bowtie2 to index a genome.
    
    Args:
        sequence_dir (str): The path to the fasta file
        database_dir (str): The output directory for the indexed files
        container (str): The container to use
        **kwargs: Additional arguments to pass to bowtie2
    """
    if container=="none":
        sequence_dir=Path(sequence_dir).absolute()
        database_dir=Path(database_dir).absolute()
        command = f"bowtie2-build {sequence_dir} {database_dir}"
        for key,value in kwargs.items():
            command = command + f" --{key} {value}"
        
    elif container=="docker":
        sequence_dir=Path(sequence_dir).absolute()
        database_dir=Path(database_dir).absolute()
        command = f"docker run -v {sequence_dir}:{sequence_dir} -v {database_dir}:{database_dir} {configs.docker_container} bowtie2-build {sequence_dir} {database_dir}"
        for key,value in kwargs.items():
            command = command + f" --{key} {value}"
    
    elif container=="singularity":
        sequence_dir=Path(sequence_dir).absolute()
        database_dir=Path(database_dir).absolute()
        command = f"singularity exec {configs.singularity_container} bowtie2-build {sequence_dir} {database_dir}"
        for key,value in kwargs.items():
            command = command + f" --{key} {value}"
    
    return command

def align_bowtie_(
    read1:str,
    read2:str|None,
    database_dir:str,
    outdir:str,
    config:configs.Configs,
    container:str="none",
    **kwargs
    )->str:
    """
    This function ouputs a command to use bowtie2 to align fastq files to a genome.
    
    Args:
        read1 (str): The path to the first fastq file
        read2 (str): The path to the second fastq file
        database_dir (str): The path to the indexed genome
        outdir (str): The output directory for the sam file
        container (str): The container to use
        **kwargs: Additional arguments to pass to bowtie2
    """
    

    
    if read2 is not None:
        paired = True
    else:
        paired = False
    
    if container=="none":
        if paired:
            read1=Path(read1).absolute()
            read2=Path(read2).absolute()
            database_dir=Path(database_dir).absolute()
            outdir=Path(outdir).absolute()
            command = f"bowtie2 -x {database_dir} -1 {read1} -2 {read2} -S {outdir}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"
        
        else:
            read1=Path(read1).absolute()
            database_dir=Path(database_dir).absolute()
            outdir=Path(outdir).absolute()
            command = f"bowtie2 -x {database_dir} -U {read1} -S {outdir}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"
        
    elif container=="docker":
        if paired:
            read1=Path(read1).absolute()
            read2=Path(read2).absolute()
            database_dir=Path(database_dir).absolute()
            outdir=Path(outdir).absolute()
            command = f"docker run -v {read1}:{read1} -v {read2}:{read2} -v {database_dir}:{database_dir} -v {outdir}:{outdir} {config.docker_container} bowtie2 -x {database_dir} -1 {read1} -2 {read2} -S {outdir}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"

        else:
            read1=Path(read1).absolute()
            database_dir=Path(database_dir).absolute()
            outdir=Path(outdir).absolute()
            command = f"docker run -v {read1}:{read1} -v {database_dir}:{database_dir} -v {outdir}:{outdir} {config.docker_container} bowtie2 -x {database_dir} -U {read1} -S {outdir}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"
    
    elif container=="singularity":
        if paired:
            read1=Path(read1).absolute()
            read2=Path(read2).absolute()
            database_dir=Path(database_dir).absolute()
            outdir=Path(outdir).absolute()
            command = f"singularity exec -B {read1}:{read1} -B {read2}:{read2} -B {database_dir}:{database_dir} -B {outdir}:{outdir} {config.singularity_container} bowtie2 -x {database_dir} -1 {read1} -2 {read2} -S {outdir}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"

        else:
            read1=Path(read1).absolute()
            database_dir=Path(database_dir).absolute()
            outdir=Path(outdir).absolute()
            command = f"singularity exec -B {read1}:{read1} -B {database_dir}:{database_dir} -B {outdir}:{outdir} {config.singularity_container} bowtie2 -x {database_dir} -U {read1} -S {outdir}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"
    
    return command

def convert_sam_bam_(
    sam_file:str,
    outdir:str,
    config:configs.Configs,
    container:str="none",

    )->str:
    """
    This function ouputs a command to use samtools to convert a sam file to a bam file.
    
    Args:
        sam_file (str): The path to the sam file
        outdir (str): The output directory for the bam file
        container (str): The container to use
    """

    if container=="none":
        sam_file=Path(sam_file).absolute()
        outdir=Path(outdir).absolute()
        command = f"samtools view -bS {sam_file} > {outdir}"
        
    elif container=="docker":
        sam_file=Path(sam_file).absolute()
        outdir=Path(outdir).absolute()
        command = f"docker run -v {sam_file}:{sam_file} -v {outdir}:{outdir} {config.docker_container} samtools view -bS {sam_file} > {outdir}"
    
    elif container=="singularity":
        sam_file=Path(sam_file).absolute()
        outdir=Path(outdir).absolute()
        command = f"singularity exec -B {sam_file}:{sam_file} -B {outdir}:{outdir} {config.singularity_container} samtools view -bS {sam_file} > {outdir}"
        
    return command




def get_unmapped_reads_(
    bam_file:str,
    outdir:str,
    config:configs.Configs,
    container:str="none",
    **kwargs
    )->str:
    """
    This function ouputs a command to use samtools to extract unmapped reads from a bam file.
    
    Args:
        bam_file (str): The path to the bam file
        outdir (str): The output directory for the fastq file
        container (str): The container to use
        **kwargs: Additional arguments to pass to samtools
        
    Returns:
        str: The command to extract the unmapped reads
    """
    if container=="none":
        bam_file=Path(bam_file).absolute()
        outdir=Path(outdir).absolute()
        command = f"samtools fastq -f 4 {bam_file} > {outdir}"
    
    elif container=="docker":
        bam_file=Path(bam_file).absolute()
        outdir=Path(outdir).absolute()
        command = f"docker run -v {bam_file}:{bam_file} -v {outdir}:{outdir} {config.docker_container} samtools view -b -f 12 -F 256 {bam_file} > {outdir}"
        
    elif container=="singularity":
        bam_file=Path(bam_file).absolute()
        outdir=Path(outdir).absolute()
        command = f"singularity exec -B {bam_file}:{bam_file} -B {outdir}:{outdir} {config.singularity_container} samtools view -b -f 12 -F 256 {bam_file} > {outdir}"
        
    return command

def sort_bam_(
    bam_file:str,
    outdir:str,
    config:configs.Configs,
    container:str="none",
    **kwargs
    )->str:
    """
    This function ouputs a command to use samtools to sort a bam file.
    
    Args:
        bam_file (str): The path to the bam file
        outdir (str): The output directory for the sorted bam file
        container (str): The container to use
        **kwargs: Additional arguments to pass to samtools
    
    Returns:
        str: The command to sort the bam file
    """
    
    if container=="none":
        bam_file=Path(bam_file).absolute()
        outdir=Path(outdir).absolute()
        command = f"samtools sort -n"
        for key,value in kwargs.items():
            command = command + f" -{key} {value}"
        
        command = command + f"{bam_file} -o {outdir}"
    
    elif container=="docker":
        bam_file=Path(bam_file).absolute()
        outdir=Path(outdir).absolute()
        command = f"docker run -v {bam_file}:{bam_file} -v {outdir}:{outdir} {config.docker_container} samtools sort -n"
        for key,value in kwargs.items():
            command = command + f" -{key} {value}"
        
        command = command + f"{bam_file} -o {outdir}"
    
    elif container=="singularity":
        bam_file=Path(bam_file).absolute()
        outdir=Path(outdir).absolute()
        command = f"singularity exec {config.singularity_container} samtools sort -n"
        for key,value in kwargs.items():
            command = command + f" -{key} {value}"
        
        command = command + f"{bam_file} -o {outdir}"
    
    return command

def sam_tools_fasq_(
    input_file:str,
    paired:bool,
    outdir1:str,
    outdir2:str|None,
    config:configs.Configs,
    container:str="none",
    )->str:
    """
    This function ouputs a command to use samtools to convert a bam file to a fastq file.

    Args:
        input_file (str): The path to the input file
        paired (bool): Whether the input file is from a paired sequence alignment
        outdir1 (str): The output directory for the first fastq file
        outdir2 (str): The output directory for the second fastq file
        container (str): The container to use
        
    Returns:
        str: The command to convert the bam file to a fastq file
    
    """
    if container=="none":
        if paired:
            input_file=Path(input_file).absolute()
            outdir1=Path(outdir1).absolute()
            outdir2=Path(outdir2).absolute()
            command = f"samtools fastq {input_file} -1 {outdir1} -2 {outdir2} -0 /dev/null -s /dev/null  -n"
        else:
            input_file=Path(input_file).absolute()
            outdir=Path(outdir).absolute()
            command = f"samtools fastq {input_file} -1 {outdir} -0 /dev/null -s /dev/null  -n"
    
    elif container=="docker":
        if paired:
            input_file=Path(input_file).absolute()
            outdir=Path(outdir).absolute()
            command = f"docker run -v {input_file}:{input_file} -v {outdir}:{outdir} {config.docker_container} samtools fastq {input_file} -1 {outdir}_1.fastq -2 {outdir}_2.fastq -0 /dev/null -s /dev/null  -n"
        else:
            input_file=Path(input_file).absolute()
            outdir=Path(outdir).absolute()
            command = f"docker run -v {input_file}:{input_file} -v {outdir}:{outdir} {config.docker_container} samtools fastq {input_file} -1 {outdir}.fastq -0 /dev/null -s /dev/null  -n"
    
    elif container=="singularity":
        
        if paired:
            input_file=Path(input_file).absolute()
            outdir=Path(outdir).absolute()
            command = f"singularity exec  {config.singularity_container} samtools fastq {input_file} -1 {outdir}_1.fastq -2 {outdir}_2.fastq -0 /dev/null -s /dev/null  -n"
        else:
            input_file=Path(input_file).absolute()
            outdir=Path(outdir).absolute()
            command = f"singularity exec {config.singularity_container} samtools fastq {input_file} -1 {outdir}.fastq -0 /dev/null -s /dev/null  -n"

    
