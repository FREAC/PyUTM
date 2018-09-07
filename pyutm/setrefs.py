import os

import pandas


def to_list(dataframe):

    return dataframe.values.tolist()


def to_csv(fname, input_data, dataframe, column):

    fname = set_fname(fname, input_data)
    output_df = pandas.read_csv(input_data)
    output_df[column] = dataframe[column]
    output_df.to_csv(fname, index=False)


def to_shp(fname, input_data, dataframe):

    fname = set_fname(fname, input_data)



def set_fname(fname, input_data):

    if fname:
        output_dir = os.path.dirname(fname)
        if output_dir and os.path.isdir(output_dir):
            return fname
        elif not output_dir:
            output_dir = os.path.dirname(input_data)
            return os.path.join(output_dir, fname)
        else:
            raise FileNotFoundError
    else:
        return input_data
