import time
import logging


class Timer (object):
    #class level warnThreshold default to 60 seconds
    _warnThreshold = 60

    def __init__(self, name, config ='seconds'): #config is optional with default of seconds
        #check if config is acceptable
        if config not in ['seconds','minutes','hours']:
            raise ValueError('Error: invalid time display option')
        # adding attribute name to Timer class
        self._name = name
        self._t_start = 0
        self._t_end = 0
        self._config = config
        #run = 1 means start() has been called and 0 otherwise
        self._run = 0

    def start(self):
        if self._run == 1: #check if Timer is already running
            raise Exception('Error: Timer is already started')
        else:
            self._t_start = time.time()
            #set run = 1 to indicate that the start funciton was called
            self._run = 1

    def end(self):
        if self._run == 0: #check if the timer is running
            raise Exception('Error: Timer is not running')
        else:
            self._t_end = time.time()
            self._run = 0
            runtime = self._t_end - self._t_start
            logFunc = logging.info if runtime < self._warnThreshold else logging.warning
            divDict = {'seconds':1,'hours': 3600, 'minutes': 60}
            logFunc(f'{self._name}: {runtime /  divDict.get(self._config)} {self._config}')


    def retrieveLastResult(self): #method to retrieve last timer
        divDict = {'seconds': 1, 'hours': 3600, 'minutes': 60}
        return (self._t_end - self._t_start) / divDict.get(self._config)


    #function to change time display that take inputs as 'seconds','minutes','hours'
    def configureTimerDisplay(self,config):
        #check if config is appropriate input
        if config not in ['seconds','minutes','hours']:
            raise ValueError('Error: invalid time display option')
        self._config = config

    #adding context manager to Timer class
    def __enter__(self):
        #start the timer
        self.start()
        #return self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        #end timer
        self.end()