from core.bot import Bot
'''
Main class for Simulation trading
'''


class Simulation(Bot):
    def __init__(self, args):
        super(Simulation, self).__init__(args)
        self.counter = 0


    def get_next(self, interval):
        '''
        Returns next state
        '''
        print('getting next ticker from Sim')
