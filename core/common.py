import sys
from importlib import import_module
from termcolor import colored


def load_module(module_prefix, module_name):
    """
    Loads strategy module based on given name.
    """
    if module_name is None:
        print(colored('Not provided module,. please add it as an argument or in config file', 'red'))
        sys.exit()
    mod = import_module(module_prefix + module_name)
    module_class = getattr(mod, module_name.split('.')[-1].capitalize())
    return module_class


def handle_buffer_limits(df, max_size):
    """
    Handles dataframe limits (drops df, if the df > max_size)
    """
    df_size = len(df.index)
    if df_size > max_size:
        # print(colored('Max buffer memory exceeded, cleaning', 'yellow'))
        rows_to_delete = df_size - max_size
        df = df.ix[rows_to_delete:]
        df = df.reset_index(drop=True)
    return df


def parse_pairs(exchange, in_pairs):
    """
    Returns list of available pairs from exchange based on the given pairs string/list
    """
    all_pairs = exchange.get_pairs()
    if in_pairs == 'all':
        print('setting_all_pairs')
        return all_pairs
    else:
        pairs = []
        parsed_pairs = in_pairs.replace(" ", "").split(',')
        for in_pair in parsed_pairs:
            if '*' in in_pair:
                prefix = in_pair.replace('*', '')
                pairs_list = [p for p in all_pairs if prefix in p]
                pairs.extend(pairs_list)
                # remove duplicates
                # pairs = list(set(pairs))
            else:
                pairs.append(in_pair)
        return pairs


def get_dataset_count(df, group_by_field='pair'):
    """
    Returns count of dataset and pairs_count (group by provided string)
    """
    pairs_group = df.groupby([group_by_field])
    # cnt = pairs_group.count()
    pairs_count = len(pairs_group.groups.keys())
    dataset_cnt = pairs_group.size().iloc[0]
    return dataset_cnt, pairs_count
