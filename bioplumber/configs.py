from dataclasses import dataclass
import json


@dataclass
class Configs:
    singularity_container:str
    docker_container:str
    bwa_cpus:int
    megahit_cpus:int
    
    @classmethod
    def from_dict(cls,dict_:dict):
        return cls(**dict_)
    
    @classmethod
    def from_json(cls,json_file:str):
        with open(json_file,"r") as f:
            return cls.from_dict(json.load(f))
    
    @classmethod
    def from_toml(cls,toml_file:str):
        import tomli
        with open(toml_file,"r") as f:
            return cls.from_dict(tomli.load(f))
    
    def to_dict(self):
        return self.__dict__

    def to_json(self,json_file:str):
        with open(json_file,"w") as f:
            json.dump(self.to_dict(),f)
    
    def to_toml(self,toml_file:str):
        import tomli
        with open(toml_file,"w") as f:
            tomli.dump(self.to_dict(),f)

DEFAULT_CONFIGS = Configs(
    singularity_container="docker://quay.io/biocontainers/megahit:1.2.9--py36h6bb024c_0",
    docker_container="quay.io/biocontainers/megahit:1.2.9--py36h6bb024c_0",
    bwa_cpus=1,
    megahit_cpus=1
)