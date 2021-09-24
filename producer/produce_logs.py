from queue import Queue
def produce_logs(work: Queue, finished: Queue,filename:str)->None:
  with open(filename,"r") as file:
    finished.put(False)
    for line in file:
      work.put(line.strip())
    finished.put(True)
