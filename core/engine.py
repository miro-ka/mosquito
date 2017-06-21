from core.simulation import Simulation

'''
Main class for Simulation Engine (main class where all is happening
'''


class Engine:
    def __init__(self, args, config):
        self.args = args
        self.config = config
        self.sim = Simulation()


    def run(self):
        print('starting simulation')

        #TODO: initialize wallet

        #TODO load simulation. trade or paper

        #TODO load strategies

        #TODO run loop
        while self.sim.finished():
            self.sim.get_next(2)

            #TODO simulation/paper/trade - get next sample(sample_size)
            #action = strategy.run
            #TODO Update wallet
            #TODO report