import pandas


def from_list(data):

    try:
        dataframe = None
        error = None
        import numpy
        dataframe = pandas.DataFrame.from_records(numpy.array(data, ndmin=2))
    except ValueError as e:
        dataframe = None
        error = e
    finally:
        return dataframe, error


def from_csv(data, columns, prefix=False):

    try:
        dataframe = None
        error = None
        dataframe = pandas.read_csv(data, usecols=columns, engine='c')
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


def from_shp(data, prefix_column=False):

    try:
        dataframe = None
        error = None
        import shapefile
        sf = shapefile.Reader(data)
        shape_type = sf.shapes()[0].shapeType
        if prefix_column:
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
