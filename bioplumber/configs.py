from dataclasses import dataclass
import json


@dataclass
class Configs:
    singularity_container:str
    docker_container:str
    bwa_cpus:int
    megahit_cpus:int
    
    @classmethod
    def from_dict(cls,dictionary:dict):
        return cls(**dictionary)



        

DEFAULT_CONFIGS = Configs(
    singularity_container="docker://quay.io/biocontainers/megahit:1.2.9--py36h6bb024c_0",
    docker_container="quay.io/biocontainers/megahit:1.2.9--py36h6bb024c_0",
    bwa_cpus=1,
    megahit_cpus=1
)

