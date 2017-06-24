from strategies.base_strategy import Base_Strategy
'''
ema strategy
'''


class Ema(Base_Strategy):
    def __init__(self, args):
        super(Ema, self).__init__(args)
        self.name = 'ema'


    def calulate(self, interval):
        '''
        Returns next state
        '''
        print('running strategy ema')
        return 'buy'
