import os


def to_list(dataframe, column):
    """
    Converts a Pandas dataframe to a nested list in [X, Y, grid reference or UID] format.
    :param dataframe: Pandas dataframe, data
    :param column: string, column name containing the grid reference or UID
    :return: list, nested list in [X, Y, grid reference or UID] format
    """
    return dataframe.loc[:, [0, 1, column]].values.tolist()


def to_csv(fname, column, input_data, dataframe):
    """
    Adds a column containing grid references or UIDs to a CSV file.
    :param fname: string, file name of the output data
    :param column: string, column name containing the grid reference or UID
    :param input_data: string, path to original CSV file
    :param dataframe: Pandas dataframe, data to be written
    """
    # Only import pandas for CSV outputs
    import pandas
    fname = set_fname(fname, input_data)
    # Add the grid reference or UID to the existing CSV
    output_df = pandas.read_csv(input_data)
    output_df[column] = dataframe[column]
    output_df.to_csv(fname, index=False)


def to_shp(fname, column, input_data, dataframe, shape_type):
    """
    Adds an attribute column containing grid references/UIDs to a SHP file.
    :param fname: string, file name of the output data
    :param column: string, column name containing the grid reference or UID
    :param input_data: string, path to original SHP file
    :param dataframe: Pandas dataframe, data to be written
    :param shape_type: int, shape type as defined on page 4 of
    http://www.esri.com/library/whitepapers/pdfs/shapefile.pdf
    """
    # Only import shapefile for SHP outputs
    import shapefile
    fname = set_fname(fname, input_data)
    r = shapefile.Reader(input_data)
    w = shapefile.Writer(shape_type)
    w.fields = r.fields[1:]
    w.field(column, 'C', size=15)
    for index, shaperec in enumerate(r.iterShapeRecords()):
        w.point(*shaperec.shape.points[0])
        w.record(*shaperec.record + [dataframe[column].iloc[index]])
    w.save(fname)


def set_fname(path, input_data):
    """
    Validates the filename and path for output data.
    :param path: string, file name of the output data
    :param input_data: string, path to original data file
    :return: string, valid output path
    """
    if path:
        output_dir = os.path.dirname(path)
        output_check = os.path.basename(path).lower().endswith(('.csv', '.shp'))
        # If the directory specified exists and the filename is valid, return the given path
        if output_check and os.path.isdir(output_dir):
            return path
        # If no directory is specified but the filename is valid,
        # return the path as the directory to the original data file and the filename
        elif output_check and not output_dir:
            output_dir = os.path.dirname(input_data)
            return os.path.join(output_dir, path)
        else:
            raise FileNotFoundError
    # If no path is given, return the path to the original data file
    else:
        return input_data
