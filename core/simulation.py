from core.environment import Environment
'''
Main class for Simulation trading
'''


class Simulation(Environment):
    def __init__(self):
        self.counter = 0

    def finished(self):
        '''
        Checks if the simulation is finished
        '''
        return False


    def get_next(self, interval):
        '''
        Returns next state
        '''
        self.counter += 1
