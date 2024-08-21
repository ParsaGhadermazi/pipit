import pathlib
from typing import Iterable

def group_files(path:pathlib.Path,
                separator:str="_",
                group_on:Iterable[int]=[0,1],
                extension:str="fastq.gz")->dict[str,int]:
    
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
        "sample1_1.fastq.gz": 1,
        "sample1_2.fastq.gz": 1,
        "sample2_1.fastq.gz": 2,
        "sample2_2.fastq.gz": 2
    }
    
    Same files with the following parameters:
    separator: "_"
    group_on: [1]
    This will output:
    {
        "sample1_1.fastq.gz": 1,
        "sample1_2.fastq.gz": 2,
        "sample2_1.fastq.gz": 1,
        "sample2_2.fastq.gz": 2
    }
    NOTE: Indeces for group_on are 0-based
    
    Args:
        path (pathlib.Path): The path to the files
        separator (str): The separator to use to split the file names
        group_on (Iterable[int]): The index of the group to use after splitting the file names
        extension (str): The extension of the files
    
    Returns:
        dict[str,int]: A dictionary of the files and their group IDs
    """
    all_files = path.glob(f"*{extension}")
    group_files={}
    group_code={}
    
    for file in all_files:
        file_name = file.name
        file_parts = file_name.split(separator)
        code="".join([file_parts[i] for i in group_on])
        if code not in group_code:
            group_code[code]=len(group_code)+1  
        group_files[str(file.absolute())]=group_code[code]
        
    return group_files
        
def cat_files_(files:Iterable[str],output_name:str)->str:
    """this function ouputs a command to use cat to concatenate files provided in the input
    
    Args:
        files (Iterable[str]): A list of file addresses to concatenate
    
    Returns:
        str: The path to the concatenated file
    """
    cat_command = f"cat {' '.join(files)} > {output_name}"
    
    return cat_command



        