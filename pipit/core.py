import conf
from typing import Any, Iterable
from collections import namedtuple
from time import sleep
from pathlib import Path
from multiprocessing import Event,Process,Semaphore,Condition

class IO:
    def __init__(self,inputs:dict[str,Path],
                 outputs:dict[str,Path],
                 validate:bool,
                 notifier_input:Condition,
                 notifier_output:Condition):
        self.inputs = inputs
        self.outputs = outputs
        self._notifier_input = notifier_input
        self._notifier_output = notifier_output
        if validate:
            self._validate()
    
    def __str__(self):
        return f"Inputs: {self.inputs}\nOutputs: {self.outputs}"

    
    def _validate(self):
        for k,v in self.inputs.items():
            if not Path(v).exists():
                raise FileNotFoundError(f"Input file {k} not found at {v}")
    
    def _anounce_ready(self):
        with self._notifier_input:
            self._validate()
        with self._notifier_output:
            self._notifier_output.notify_all()
    
    def __call__(self,verbose:bool=False):
        self._anounce_ready()
        if verbose:
            print(f"{self.__str__()} is ready.")
    
def _notify_for_input(ios:Iterable[IO])->None:
    for io in ios:
        with io._notifier_input:
            io._notifier_input.notify()

    


class Task:
    
    def __init__(self,name:str,
                 command_genrator:callable,
                 io:IO,
                event_input_available:Event,
                event_output_available:Event,
                container:str,
                semaphore:Semaphore,
                 ):
        self.name = name
        self.command_genrator = command_genrator
        self.io = io
        self._event_input_available = event_input_available
        self._event_output_available = event_output_available
        self.container = container
        self.semaphore = semaphore
        
        
    
    def save_task(self,path:str):
        pass
        
    
    def _valdate_inputs(self):
        pass
        
    def _outputs_ready(self):
        pass
    
    def __call__(self,input_available:Event,output_available:Event):
        with self.semaphore:
            with self._event_input_available:
                self._valdate_inputs()
                self._event_input_available.set()
            
            self.command_genrator(io=IO,
                                container=self.container,
                                semaphore=self.semaphore)
                                  
            
            
            with output_available:
                self._outputs_ready()
                self._event_output_available.set()
        

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

def load_step(path:str)->Task:
    pass

def dump_pipeline(pipeline:Pipeline,path:str)->dict:
    pass

class TaskManager:
    def __init__(self,tasks:Iterable[Task]):
        self._tasks = tasks
        self.done = False
        self._get_current_state()
        
    
    @property
    def tasks(self):
        return self._tasks
    
    @tasks.setter
    def tasks(self,item):
        raise AttributeError("Task Manager objects are not supposed to be modified after creation.")
    
    def _get_current_state(self):
        state={
            "Pending":[],
            "Running":[],
            "Finished":[],
            "Failed":[],
            "Waiting":[],
            "Ready_to_Start":[],
            "Not Started":[],
        }
        
        for task in self.tasks:
            match task.state:
                case "Pending":
                    state["Pending"].append(task)
                case "Running":
                    state["Running"].append(task)
                case "Finished":
                    state["Finished"].append(task)
                case "Failed":
                    state["Failed"].append(task)
                case "Not Started":
                    state["Not Started"].append(task)
                case "Ready to Start":
                    state["Ready_to_Start"].append(task)
                case _:
                    raise ValueError(f"Task {task.name} has an invalid state: {task.state}")
        self.state = state
    
    def busy_loop(self,interval:int=30):
        while not self.done:
            self._get_current_state()
            if len(self.state["Finished"]) == len(self.tasks):
                self.done = True
            if self.state["Failed"]:
                raise RuntimeError("One or more tasks failed.")
            sleep(interval)
    
    
                
            
        