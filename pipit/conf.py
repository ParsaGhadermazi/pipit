from dataclasses import dataclass,field

class PipelineConfig:
    pass

class StepConfig:
    pass

class TaskConfig:
    pass

@dataclass  
class Containers:
    """ This class stores the default containers for the pipelines.
    """
    singularity:dict=lambda:dict(
        bwa="docker://biocontainers/bwa:v0.7.17_cv1",
    )
