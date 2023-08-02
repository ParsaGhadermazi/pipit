import conf
from typing import Any, Iterable
from collections import namedtuple
from time import sleep
from pathlib import Path
from multiprocessing import Event,Process,Semaphore,Condition
import os
import json

N_LOCAL_EXECUTERS = 4
N_SLURM_EXECUTERS = 25

class ExecuterNotImplementedError(NotImplementedError):
    pass
            
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
    
    def _anounce_input_ready(self,time_out:int|str="inf"):
        if time_out == "inf":
            with self._notifier_input:
                self._notifier_input.wait()
                self._validate()
        else:
            with self._notifier_input:
                self._notifier_input.wait(time_out)
                self._validate()
    
    def _anounce_output_ready(self):
        with self._notifier_output:
            self._notifier_output.notify_all()
    
    def __call__(self,verbose:bool=False,time_out:int=0):
        self._anounce_input_ready(time_out=time_out)
        if verbose:
            print(f"{self.__str__()} is ready.")
    


    


class Task:
    
    def __init__(self,
                name:str,
                command_genrator:callable,
                io:IO,
                event_output_available:Condition,
                container:str,
                semaphore:Semaphore,
                config:conf.TaskConfig
                 ):
        self.name = name
        self.command_genrator = command_genrator
        self.io = io
        self._event_output_available = event_output_available
        self.container = container
        self.semaphore = semaphore
        self.config = config
        self.stats={name:{}}
        
    
    def save_task(self,path:str):
        pass
    
    def _submit_stats(self):
        with open(self.config.stats_file_path,"a") as f:
            json.dump(self.stats,f)
    
    def __call__(self,executer:str="local"):

        with self.semaphore:
            self.io()
            if executer == "local":
                status=os.system(self.command_genrator(io=IO,
                            container=self.container,
                            semaphore=self.semaphore))
                
                if status == 0:
                    with self._event_output_available:
                        self.io._anounce_input_ready()
                    

                
            
            elif executer == "slurm":
                pass
            
            
            else:
                raise NotImplementedError(f"Executer {executer} is not implemented.")
            
            with self._event_output_available:
                self._event_output_available.notify_all()

class BatchTask:
    def __init__(self,tasks:Iterable[Task],
                 name:str,
                 config:conf.BatchTaskConfig):
        self.tasks = tasks
        self.name = name
        self.config = config
    
    def __call__(self):
        pass
    
    def __str__(self):
        pass   



class TaskManager:
    def __init__(self,tasks:Iterable[Task|BatchTask],
                 n_local_executers:int=N_LOCAL_EXECUTERS,
                 n_slurm_executers:int=N_SLURM_EXECUTERS,):
        self._tasks = tasks
        self.done = False
        
        self._get_current_state()
        
    
    @property
    def tasks(self):
        return self._tasks
    
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
    

                
class Pipeline:
    def __init__(self,steps:list[Task],config:conf.PipelineConfig):
        self.steps = steps
        self.config = config


    def __call__(self):
        pass
    
    def __str__(self):
        pass
 
def _notify_for_input(ios:Iterable[IO])->None:
    for io in ios:
        io._validate()
        with io._notifier_input:
            io._notifier_input.notify_all()
            


if __name__ == "__main__":
    pass