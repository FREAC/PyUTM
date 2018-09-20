import pandas


def from_list(data):
    """
    Converts a list into a two dimensional Numpy array, then into a Pandas dataframe.
    :param data: tuple or list, point coordinates in (X, Y) format
    :return: Pandas dataframe, error message
    """
    try:
        dataframe = None
        error = None
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
    try:
        dataframe = None
        error = None
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
    try:
        dataframe = None
        error = None
        # Only import shapefile for SHP file inputs
        import shapefile
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
