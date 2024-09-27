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



def bowtie2_decontaminate_(
    read1:str,
    read2:str|None,
    sample_name:str,
    database_dir:str,
    outdir:str,
    config:configs.Configs,
    container:str="none",
    **kwargs
    )->str:
    """
    This function ouputs a command to use bowtie2 to decontaminate fastq by providing the indexed bowtie database.

    Args:
        read1 (str): The path to the first fastq file
        read2 (str): The path to the second fastq file
        sample_name (str): The name of the sample
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
            if paired:
                output_files_zipped_unaligned=Path(outdir)/f"{sample_name}_host_removed"
                output_files_zipped_aligned=Path(outdir)/f"{sample_name}_host_aligned"
                
                command =f"bowtie2 -p {config.bowtie2_cpus} -x {database_dir} -1 {read1} -2 {read2} --un-conc-gz {output_files_zipped_unaligned} --al-conc-gz {output_files_zipped_aligned}"
                for key,value in kwargs.items():
                    command = command + f" --{key} {value}"
            
        else:
            output_files_zipped_unaligned=Path(outdir)/f"{sample_name}_host_removed"
            output_files_zipped_aligned=Path(outdir)/f"{sample_name}_host_aligned"
            
            command =f"bowtie2 -p {config.bowtie2_cpus} -x {database_dir} -U {read1} --un-gz {output_files_zipped_unaligned} --al-gz {output_files_zipped_aligned}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"
                    
    elif container=="docker":
        read1=Path(read1).absolute()
        database_dir=Path(database_dir).absolute()
        outdir=Path(outdir).absolute()
        if paired:
            output_files_zipped_unaligned=Path(outdir)/f"{sample_name}_host_removed"
            output_files_zipped_aligned=Path(outdir)/f"{sample_name}_host_aligned"
            
            command =f"docker run -v {read1}:{read1} -v {read2}:{read2} -v {database_dir}:{database_dir} -v {outdir}:{outdir} {config.docker_container} bowtie2 -p {config.bowtie2_cpus} -x {database_dir} -1 {read1} -2 {read2} --un-conc-gz {output_files_zipped_unaligned} --al-conc-gz {output_files_zipped_aligned}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"
        
        else:
            output_files_zipped_unaligned=Path(outdir)/f"{sample_name}_host_removed"
            output_files_zipped_aligned=Path(outdir)/f"{sample_name}_host_aligned"
            
            command =f"docker run -v {read1}:{read1} -v {database_dir}:{database_dir} -v {outdir}:{outdir} {config.docker_container} bowtie2 -p {config.bowtie2_cpus} -x {database_dir} -U {read1} --un-gz {output_files_zipped_unaligned} --al-gz {output_files_zipped_aligned}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"
        
    elif container=="singularity":
        read1=Path(read1).absolute()
        database_dir=Path(database_dir).absolute()
        outdir=Path(outdir).absolute()
        if paired:
            output_files_zipped_unaligned=Path(outdir)/f"{sample_name}_host_removed"
            output_files_zipped_aligned=Path(outdir)/f"{sample_name}_host_aligned"
            
            command =f"singularity exec {config.singularity_container} bowtie2 -p {config.bowtie2_cpus} -x {database_dir} -1 {read1} -2 {read2} --un-conc-gz {output_files_zipped_unaligned} --al-conc-gz {output_files_zipped_aligned}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"
        
        else:
            output_files_zipped_unaligned=Path(outdir)/f"{sample_name}_host_removed"
            output_files_zipped_aligned=Path(outdir)/f"{sample_name}_host_aligned"
            
            command =f"singularity exec  {config.singularity_container} bowtie2 -p {config.bowtie2_cpus} -x {database_dir} -U {read1} --un-gz {output_files_zipped_unaligned} --al-gz {output_files_zipped_aligned}"
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
        command = f"samtools view -bS {sam_file}| samtools sort -o {outdir}"
        
    elif container=="docker":
        sam_file=Path(sam_file).absolute()
        outdir=Path(outdir).absolute()
        command = f"docker run -v {sam_file}:{sam_file} -v {outdir}:{outdir} {config.docker_container} samtools view -bS {sam_file}| samtools sort -o {outdir}"
    
    elif container=="singularity":
        sam_file=Path(sam_file).absolute()
        outdir=Path(outdir).absolute()
        command = f"singularity exec -B {sam_file}:{sam_file} -B {outdir}:{outdir} {config.singularity_container} samtools view -bS {sam_file}| samtools sort -o {outdir}"
        
    return command

def get_mapped_reads_(
    bam_file:str,
    outdir:str,
    config:configs.Configs,
    paired:bool=True,
    container:str="none",
    **kwargs
    )->str:
    """
    This function ouputs a command to use samtools to extract mapped reads from a bam file.
    
    Args:
        bam_file (str): The path to the bam file
        outdir (str): The output directory for the fastq file
        container (str): The container to use
        **kwargs: Additional arguments to pass to samtools
    
    Returns:
        str: The command to extract the mapped reads
    """
    if container=="none":
        bam_file=Path(bam_file).absolute()
        outdir=Path(outdir).absolute()
        if paired:
            command = f"samtools view -b -f 3 {bam_file} > {outdir}"
        else:
            command = f"samtools view -b -F 4 {bam_file} > {outdir}"
        
    elif container=="docker":
        bam_file=Path(bam_file).absolute()
        outdir=Path(outdir).absolute()
        if paired:
            command = f"docker run -v {bam_file}:{bam_file} -v {outdir}:{outdir} {config.docker_container} samtools view -b -f 3 {bam_file} > {outdir}"
        else:
            command = f"docker run -v {bam_file}:{bam_file} -v {outdir}:{outdir} {config.docker_container} samtools view -b -F 4 {bam_file} > {outdir}"
        
    elif container=="singularity":
        bam_file=Path(bam_file).absolute()
        outdir=Path(outdir).absolute()
        if paired:
            command = f"singularity exec -B {bam_file}:{bam_file} -B {outdir}:{outdir} {config.singularity_container} samtools view -b -f 3 {bam_file} > {outdir}"
        else:
            command = f"singularity exec -B {bam_file}:{bam_file} -B {outdir}:{outdir} {config.singularity_container} samtools view -b -F 4 {bam_file} > {outdir}"

    return command






def get_unmapped_reads_(
    bam_file:str,
    outdir:str,
    config:configs.Configs,
    paired:bool=True,
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
        if paired:
            command = f"samtools view -b -f 12 -F 256 {bam_file} > {outdir}"
        else:
            command = f"samtools view -b -f 4 {bam_file} > {outdir}"
            
    elif container=="docker":
        bam_file=Path(bam_file).absolute()
        outdir=Path(outdir).absolute()
        if paired:
            command = f"docker run -v {bam_file}:{bam_file} -v {outdir}:{outdir} {config.docker_container} samtools view -b -f 12 -F 256 {bam_file} > {outdir}"
        else:
            command = f"docker run -v {bam_file}:{bam_file} -v {outdir}:{outdir} {config.docker_container} samtools view -b -f 4 {bam_file} > {outdir}"
    
    elif container=="singularity":
        bam_file=Path(bam_file).absolute()
        outdir=Path(outdir).absolute()
        if paired:
            command = f"singularity exec -B {bam_file}:{bam_file} -B {outdir}:{outdir} {config.singularity_container} samtools view -b -f 12 -F 256 {bam_file} > {outdir}"
        else:
            command = f"singularity exec -B {bam_file}:{bam_file} -B {outdir}:{outdir} {config.singularity_container} samtools view -b -f 4 {bam_file} > {outdir}"
            
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
    outdir1:str,
    outdir2:str|None,
    config:configs.Configs,
    paired:bool=True,
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
        input_file=Path(input_file).absolute()
        outdir1=Path(outdir1).absolute()
        if paired:
            outdir2=Path(outdir2).absolute()
            command = f"samtools fastq -1 {outdir1} -2 {outdir2} {input_file}"
        else:
            command = f"samtools fastq {outdir1} > {input_file}"
    
    elif container=="docker":
        input_file=Path(input_file).absolute()
        outdir1=Path(outdir1).absolute()
        if paired:
            outdir2=Path(outdir2).absolute()
            command = f"docker run -v {input_file}:{input_file} -v {outdir1}:{outdir1} -v {outdir2}:{outdir2} {config.docker_container} samtools fastq -1 {outdir1} -2 {outdir2} {input_file}"
        else:
            command = f"docker run -v {input_file}:{input_file} -v {outdir1}:{outdir1} {config.docker_container} samtools fastq {outdir1} > {input_file}"
    
    elif container=="singularity":
        input_file=Path(input_file).absolute()
        outdir1=Path(outdir1).absolute()
        if paired:
            outdir2=Path(outdir2).absolute()
            command = f"singularity exec -B {input_file}:{input_file} -B {outdir1}:{outdir1} -B {outdir2}:{outdir2} {config.singularity_container} samtools fastq -1 {outdir1} -2 {outdir2} {input_file}"
        else:
            command = f"singularity exec -B {input_file}:{input_file} -B {outdir1}:{outdir1} {config.singularity_container} samtools fastq {outdir1} > {input_file}"
    
    return command


    
def index_bwa_(
    sequence_dir:str,
    config:configs.Configs,
    container:str="none",
    **kwargs
    )->str:
    """
    This function ouputs a command to use bwa to index a genome.
    
    Args:
        sequence_dir (str): The path to the fasta file
        container (str): The container to use
        **kwargs: Additional arguments to pass to bwa
    """
    if container=="none":
        sequence_dir=Path(sequence_dir).absolute()
        command = f"bwa index {sequence_dir}"
        for key,value in kwargs.items():
            command = command + f" --{key} {value}"
        
    elif container=="docker":
        sequence_dir=Path(sequence_dir).absolute()
        command = f"docker run -v {sequence_dir}:{sequence_dir} {config.docker_container} bwa index {sequence_dir}"
    
    elif container=="singularity":
        sequence_dir=Path(sequence_dir).absolute()
        command = f"singularity exec {config.singularity_container} bwa index {sequence_dir}"
        for key,value in kwargs.items():
            command = command + f" --{key} {value}"
    
    return command


def align_bwa_(
    read1:str,
    read2:str|None,
    database_dir:str,
    outdir:str,
    config:configs.Configs,
    container:str="none",
    **kwargs
    )->str:
    """
    This function ouputs a command to use bwa to align fastq files to a genome.
    
    Args:
        read1 (str): The path to the first fastq file
        read2 (str): The path to the second fastq file
        database_dir (str): The path to the indexed genome
        outdir (str): The output directory for the sam file
        container (str): The container to use
        **kwargs: Additional arguments to pass to bwa
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
            command = f"bwa mem -t {config.bwa_cpus} {database_dir} {read1} {read2} > {outdir}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"
        
        else:
            read1=Path(read1).absolute()
            database_dir=Path(database_dir).absolute()
            outdir=Path(outdir).absolute()
            command = f"bwa mem  -t {config.bwa_cpus} {database_dir} {read1} > {outdir}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"
        
    elif container=="docker":
        if paired:
            read1=Path(read1).absolute()
            read2=Path(read2).absolute()
            database_dir=Path(database_dir).absolute()
            outdir=Path(outdir).absolute()
            command = f"docker run -v {read1}:{read1} -v {read2}:{read2} -v {database_dir}:{database_dir} -v {outdir}:{outdir} {config.docker_container} bwa mem  -t {config.bwa_cpus} {database_dir} {read1} {read2} > {outdir}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"

        else:
            read1=Path(read1).absolute()
            database_dir=Path(database_dir).absolute()
            outdir=Path(outdir).absolute()
            command = f"docker run -v {read1}:{read1} -v {database_dir}:{database_dir} -v {outdir}:{outdir} {config.docker_container} bwa mem {database_dir} {read1} > {outdir}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"

                    
    elif container=="singularity":
        if paired:
            read1=Path(read1).absolute()
            read2=Path(read2).absolute()
            database_dir=Path(database_dir).absolute()
            outdir=Path(outdir).absolute()
            command = f"singularity exec  {config.singularity_container} bwa mem -t {config.bwa_cpus} {database_dir} {read1} {read2} > {outdir}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"

        else:
            read1=Path(read1).absolute()
            database_dir=Path(database_dir).absolute()
            outdir=Path(outdir).absolute()
            command = f"singularity exec {config.singularity_container} bwa mem -t {config.bwa_cpus} {database_dir} {read1} > {outdir}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"
                
    
    return command