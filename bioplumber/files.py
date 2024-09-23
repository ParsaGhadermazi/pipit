import pathlib
from typing import Iterable
import bioplumber.configs as configs
import requests
import rich
from rich.progress import Progress
import rich
REFERENCE_GENOMES={
    "homo_sapiens":"http://igenomes.illumina.com.s3-website-us-east-1.amazonaws.com/Homo_sapiens/UCSC/hg38/Homo_sapiens_UCSC_hg38.tar.gz",
    "PhiX":"https://webdata.illumina.com/downloads/productfiles/igenomes/phix/PhiX_Illumina_RTA.tar.gz",
    "Mus musculus (Mouse)":"http://igenomes.illumina.com.s3-website-us-east-1.amazonaws.com/Mus_musculus/Ensembl/GRCm38/Mus_musculus_Ensembl_GRCm38.tar.gz"
}
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



def download_url(url:str, output_path:str)->None:
    """This function downloads a file from a url and saves it to the output path
    
    Args:
        url (str): The url to download the file from
        output_path (str): The path to save the downloaded file
    
    Returns:
        None
    """    
    r = requests.get(url, allow_redirects=True,stream=True,timeout=10)
     
    total_size = int(r.headers.get('content-length', 0))
    block_size = total_size // 1000 + 1  # Progress bar updates every 1%
    if not pathlib.Path(output_path).parent.exists():
        pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'wb') as f:
        with Progress() as progress:
            task = progress.add_task("[cyan]Downloading...", total=total_size)
            for data in r.iter_content(block_size):
                f.write(data)
                progress.update(task, advance=len(data))
    
    
        
        