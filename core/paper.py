from core.bot import Bot

'''
Main class for Paper trading
'''



class Paper(Bot):
    def __init__(self, args):
        super(Paper, self).__init__(args)
        self.counter = 0


    def get_next(self, interval):
        '''
        Returns next state
        '''
        print('getting next ticker from Paper')
