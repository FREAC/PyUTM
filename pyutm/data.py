import os

import pandas
import shapefile


def from_list(data):
    """
    Converts a list into a two dimensional Numpy array, then into a Pandas dataframe.
    :param data: tuple or list, point coordinates in (X, Y) format
    :return: Pandas dataframe, error message
    """
    dataframe = None
    error = None
    try:
        # Only import numpy for list inputs
        import numpy
        dataframe = pandas.DataFrame.from_records(numpy.array(data, ndmin=2))
    except ValueError as e:
        dataframe = None
        error = e
    finally:
        return dataframe, error


def from_csv(data, columns, prefix=False):
    """
    Converts a CSV file of coordinates or prefixes into a Pandas dataframe.
    :param data: string, path to CSV file
    :param columns: tuple or list of length 2, column names containing X and Y coordinates, in that order
    :param prefix: boolean, default=False, whether column parameter contains prefix values for the UID
    :return: Pandas dataframe, error message
    """
    dataframe = None
    error = None
    try:
        dataframe = pandas.read_csv(data, usecols=columns, engine='c')
        # Select only the relevant columns from the dataframe
        dataframe = dataframe[list(columns)]
        if not prefix:
            dataframe.columns = (0, 1)
        else:
            dataframe.columns = 0
    except (FileNotFoundError, ValueError) as e:
        dataframe = None
        error = e
    finally:
        return dataframe, error


def from_shp(data, prefix_column=None):
    """
    Converts a SHP file's geometry or prefix attributes into a Pandas dataframe.
    :param data: string, path to SHP file
    :param prefix_column: string, default=None, attribute column name containing prefix values for the UID
    :return: Pandas dataframe, integer specifying shape type of shapefile, error message
    """
    dataframe = None
    shape_type = None
    error = None
    try:
        sf = shapefile.Reader(data)
        shape_type = sf.shapes()[0].shapeType
        if prefix_column:
            # Get the index of the specified prefix column
            index = [field[0] for field in sf.fields].index(prefix_column[0]) - 1
            prefixes = [rec[index] for rec in sf.iterRecords()]
            dataframe = pandas.DataFrame(data=prefixes, columns=(0,))
            return
        # Only accept Point, PointZ and PointM geometries
        if shape_type in (1, 11, 21):
            coords = [shape.points[0] for shape in sf.iterShapes()]
            dataframe = pandas.DataFrame(data=coords, columns=(0, 1))
    except shapefile.ShapefileException as e:
        dataframe = None
        error = e
    finally:
        return dataframe, shape_type, error


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


# For compatibility between Python 2.x and 3.x
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError
