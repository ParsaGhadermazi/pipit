from bioplumber import configs
from pathlib import Path as Path


def assemble_megahit_(
    read1:str,
    read2:str|None,
    output_dir:str,
    config:configs.Configs,
    container:str="none",
    **kwargs
)->str:
    """
    Generate a command to run MEGAHIT assembler.

    Args:
        read1 (str): Path to read1 file.
        read2 (str|None): Path to read2 file.
        output_dir (str): Path to output directory.
        config (configs.Configs): Configuration object.
        container (str): Container to use. Default is "none".
        **kwargs: Additional arguments.

    Returns:
        str: Command to run MEGAHIT.
    """
    if read2 is None:
        paired =False
    
    else:
        paired = True
    
    if container == "none":
        if paired:
            read1 = str(Path(read1).resolve().absolute())
            read2 = str(Path(read2).resolve().absolute())
            output_dir = str(Path(output_dir).resolve().absolute())
            command= f"megahit -1 {read1} -2 {read2} -o {output_dir} -t {config.megahit_cpus}"
            for key,value in kwargs.items():
                key=key.replace("_","-")
                command+= f" --{key} {value}"
        
        else:
            read1 = str(Path(read1).resolve().absolute())
            output_dir = str(Path(output_dir).resolve().absolute())
            command= f"megahit -r {read1} -o {output_dir} -t {config.megahit_cpus}"
            for key,value in kwargs.items():
                command+= f" --{key} {value}"
            
    elif container =="docker":
        if paired:
            read1 = str(Path(read1).resolve().absolute())
            read2 = str(Path(read2).resolve().absolute())
            output_dir = str(Path(output_dir).resolve().absolute())
            command= f"docker run -v {output_dir}:{output_dir} -v {read1}:{read1} -v {read2}:{read2} {config.docker_container} megahit -1 {read1} -2 {read2} -o {output_dir} -t {config.megahit_cpus}"
            for key,value in kwargs.items():
                command+= f" --{key} {value}"

        else:
            read1 = str(Path(read1).resolve().absolute())
            output_dir = str(Path(output_dir).resolve().absolute())
            command= f"docker run -v {output_dir}:{output_dir} -v {read1}:{read1} {config.docker_container} megahit -r {read1} -o {output_dir} -t {config.megahit_cpus}"
            for key,value in kwargs.items():
                command+= f" --{key} {value}"
    
    elif container =="singularity":
        if paired:
            read1 = str(Path(read1).resolve().absolute())
            read2 = str(Path(read2).resolve().absolute())
            output_dir = str(Path(output_dir).resolve().absolute())
            command= f"singularity exec {config.singularity_container} megahit -1 {read1} -2 {read2} -o {output_dir} -t {config.megahit_cpus}"
            for key,value in kwargs.items():
                command+= f" --{key} {value}"
        
        else:
            read1 = str(Path(read1).resolve().absolute())
            output_dir = str(Path(output_dir).resolve().absolute())
            command= f"singularity exec {config.singularity_container} megahit -r {read1} -o {output_dir} -t {config.megahit_cpus}"
            for key,value in kwargs.items():
                command+= f" --{key} {value}"
                
    return command
            
    
        
        
    
    