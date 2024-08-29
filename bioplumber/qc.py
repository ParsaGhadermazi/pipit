import bioplumber.configs as configs
from pathlib import Path as Path

def qc_fastp_(
    read1:str,
    read2:str|None,
    outdir1:str,
    outdir2:str|None,
    config:configs.Configs,
    container:str="none",
    **kwargs
    )->str:
    """
    This function ouputs a command to use fastp to quality control fastq files.

    Args:
        read1 (str): The path to the first fastq file
        read2 (str): The path to the second fastq file
        outdir1 (str): The output directory for the first fastq file
        outdir2 (str): The output directory for the second fastq file
        container (str): The container to use
        **kwargs: Additional arguments to pass to fastp
    
    """

    if read2 is None and outdir2 is not None:
        raise ValueError("read2 is None but outdir2 is not None")
    
    if read2 is not None:
        paired = True
    else:
        paired = False
    
    if container=="none":
        if paired:
            read1=Path(read1).absolute()
            read2=Path(read2).absolute()
            qcd1=Path(outdir1).absolute()
            qcd2=Path(outdir2).absolute()
            json_file=Path(outdir1).parent / "fastp.json"
            html_file=Path(outdir1).parent / "fastp.html"
            command = f"fastp -i {read1} -I {read2} -o {qcd1} -O {qcd2} -j {json_file} -h {html_file}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"
        
        else:
            read1=Path(read1).absolute()
            qcd1=Path(outdir1).absolute()
            json_file=Path(outdir1).parent / "fastp.json"
            html_file=Path(outdir1).parent / "fastp.html"
            command = f"fastp -i {read1} -o {qcd1} -j {json_file} -h {html_file}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"
        
    elif container=="docker":
        if paired:
            read1=Path(read1).absolute()
            read2=Path(read2).absolute()
            qcd1=Path(outdir1).absolute()
            qcd2=Path(outdir2).absolute()
            json_file=Path(outdir1).parent / "fastp.json"
            html_file=Path(outdir1).parent / "fastp.html"
            mapfiles = f"-v {read1}:{read1} -v {read2}:{read2} -v {qcd1}:{qcd1} -v {qcd2}:{qcd2} -v {json_file}:{json_file} -v {html_file}:{html_file}"
            command = f"docker run {mapfiles} {config.docker_container} fastp -i {read1} -I {read2} -o {qcd1} -O {qcd2} -j {json_file} -h {html_file}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"
        
        else:
            read1=Path(read1).absolute()
            qcd1=Path(outdir1).absolute()
            json_file=Path(outdir1).parent / "fastp.json"
            html_file=Path(outdir1).parent / "fastp.html"
            mapfiles = f"-v {read1}:{read1} -v {qcd1}:{qcd1} -v {json_file}:{json_file} -v {html_file}:{html_file}"
            command = f"docker run {mapfiles} {config.docker_container} fastp -i {read1} -o {qcd1} -j {json_file} -h {html_file}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"
        
    elif container=="singularity":
        if paired:
            read1=Path(read1).absolute()
            read2=Path(read2).absolute()
            qcd1=Path(outdir1).absolute()
            qcd2=Path(outdir2).absolute()
            json_file=Path(outdir1).parent / "fastp.json"
            html_file=Path(outdir1).parent / "fastp.html"
            mapfiles = f"{read1}:{read1},{read2}:{read2},{qcd1}:{qcd1},{qcd2}:{qcd2},{json_file}:{json_file},{html_file}:{html_file}"
            command = f"singularity exec --bind {mapfiles} {config.singularity_container} fastp -i {read1} -I {read2} -o {qcd1} -O {qcd2} -j {json_file} -h {html_file}"
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"
        
        else:
            read1=Path(read1).absolute()
            qcd1=Path(outdir1).absolute()
            json_file=Path(outdir1).parent / "fastp.json"
            html_file=Path(outdir1).parent / "fastp.html"
            mapfiles = f"{read1}:{read1},{qcd1}:{qcd1},{json_file}:{json_file},{html_file}:{html_file}"
            command = f"singularity exec --bind {mapfiles} {config.singularity_container} fastp -i {read1} -o {qcd1} -j {json_file} -h {html_file}"
            
            for key,value in kwargs.items():
                command = command + f" --{key} {value}"
        
    return command

    

        
        

