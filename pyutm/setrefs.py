import pandas


def to_list(dataframe):

    return dataframe.values.tolist()


def to_csv(fname, input_data, dataframe, column):

    output_df = pandas.read_csv(input_data)
    output_df[column] = dataframe[column]
    output_df.to_csv(fname, index=False)


def to_shp(fname, input_data, dataframe):


    return
