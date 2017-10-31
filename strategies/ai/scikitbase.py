from abc import ABC
import configargparse
from sklearn.externals import joblib
from termcolor import colored


class ScikitBase(ABC):
    """
    Base class for AI strategies
    """
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('-p', '--pipeline', help='trained model/pipeline', required=True)
    pipeline = None

    def __init__(self):
        args = self.arg_parser.parse_known_args()[0]
        super(ScikitBase, self).__init__()
        self.pipeline = self.load_pipeline(args.pipeline)

    @staticmethod
    def load_pipeline(pipeline_file):
        """
        Loads scikit model/pipeline
        """
        print(colored('Loading pipeline: ' + pipeline_file, 'green'))
        return joblib.load(pipeline_file)

    def fetch_pipeline_from_server(self):
        """
        Method fetches pipeline from server/cloud
        """
        # TODO
        pass

    def predict(self, df):
        """
        Returns predictions based on the model/pipeline
        """
        return self.pipeline.predict(df)
