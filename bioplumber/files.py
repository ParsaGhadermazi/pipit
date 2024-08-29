import pathlib
from typing import Iterable
import bioplumber.configs as configs

def group_files(path:str,
                separator:str="_",
                group_on:Iterable[int]=[0,1],
                extension:str="fastq.gz")->dict[int,list[str]]:
    
    """This function groups files based on their names.
    The files are grouped based on the separator and the group_on.
    for example if the files are named as follows:
    
    sample1_1.fastq.gz
    sample1_2.fastq.gz
    sample2_1.fastq.gz
    sample2_2.fastq.gz
    
    The function will group the files as follows:
    separator: "_"
    group_on: [0]
    This will output:
    {
        1: ["sample1_1.fastq.gz","sample1_2.fastq.gz"],
        2: ["sample2_1.fastq.gz","sample2_2.fastq.gz"]
    }
    
    Same files with the following parameters:
    separator: "_"
    group_on: [1]
    This will output:
    {
        1: ["sample1_1.fastq.gz","sample2_1.fastq.gz"],
        2: ["sample1_2.fastq.gz","sample2_2.fastq.gz"]
    }
    NOTE: Indeces for group_on are 0-based
    
    Args:
        path (str): The path to the files
        separator (str): The separator to use to split the file names
        group_on (Iterable[int]): The index of the group to use after splitting the file names
        extension (str): The extension of the files
    
    Returns:
        dict[int,list]: A dictionary with the group number as the key and the list of files as the value
    """
    path = pathlib.Path(path)
    all_files = path.rglob(f"*{extension}")
    group_files={}
    code_map={}    
    for file in all_files:
        file_name = file.name.replace(extension,"")
        file_parts = file_name.split(separator)
        code="".join([file_parts[i] for i in group_on])
    
        group_files.setdefault(code_map.setdefault(code,len(code_map)+1),[]).append(str(file.absolute()))
    
    for key in group_files:
        group_files[key].sort()
        
    return group_files

    

        
def cat_files_(files:Iterable[str],
               output_name:str,
               configs:configs.Configs,
               container:str="none",
               **kwargs)->str:
    """this function ouputs a command to use cat to concatenate files provided in the input
    
    Args:
        files (Iterable[str]): A list of file addresses to concatenate
        output_name (str): The name of the output file
        configs (configs.Configs): The configurationobjet to use
        container (str): The container to use to run the command: "none","singularity","docker"
    
    Returns:
        str: The path to the concatenated file
    """
    parents=[pathlib.Path(file).parent for file in files]
    if len(set(parents))>1:
        raise ValueError("All files should be in the same directory")

    output_path = pathlib.Path(parents[0]) / output_name
    if container=="none":
        cat_command = f"cat {' '.join(files)} > {output_path.absolute()}"
        for key,value in kwargs.items():
            cat_command = cat_command + f" --{key} {value}"
    
    
    elif container=="docker":
        mapfiles=" ".join([f"-v {str(pathlib.Path(file).absolute())}:{str(pathlib.Path(file).absolute())}" for file in files])
        cmd= " ".join([f"{str(pathlib.Path(file).absolute())}" for file in files])
        cat_command = f"docker run {mapfiles} {configs.docker_container} cat {cmd} > {str(output_path.absolute())}"
        for key,value in kwargs.items():
            cat_command = cat_command + f" --{key} {value}"
    
    
    elif container=="singularity":
        mapfiles=",".join([f"{str(pathlib.Path(file).absolute())}:{str(pathlib.Path(file).absolute())}" for file in files])
        cmd= " ".join([f"{str(pathlib.Path(file).absolute())}" for file in files])
        cat_command = f"singularity exec --bind {mapfiles} {configs.singularity_container} cat {cmd} > {str(output_path.absolute())}"
        for key,value in kwargs.items():
            cat_command = cat_command + f" --{key} {value}"
    
    return cat_command



        