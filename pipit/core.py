import conf

class IO:
    pass

class Command:
    pass

class Layer:
    pass

class State:
    pass

class Step:
    
    def __init__(self,name:str,
                 command:Command,
                 inputs:IO,
                 outputs:IO,
                 ):
        self.name = name
        self.command = command
        self.inputs = inputs,
        self.outputs = outputs
        self.id = None
        self._output_available = False
        def submit(sel,executor:str="local"):
            pass
        
    
    def _valdate_inputs(self):
        pass
        
    def _outputs_ready(self):
        pass

class Pipeline:
    def __init__(self,steps:list[Layer],config:conf.PipelineConfig):
        self.steps = steps
        self.config = config


    def __call__(self):
        pass
    
    def __str__(self):
        pass

def load_pipeline(path:str)->Pipeline:
    pass

def load_step(path:str)->Step:
    pass

def dump_pipeline(pipeline:Pipeline,path:str)->dict:
    pass

