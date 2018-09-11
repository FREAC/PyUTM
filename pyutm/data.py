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


def from_csv(data, columns):

    try:
        dataframe = None
        error = None
        dataframe = pandas.read_csv(data, usecols=columns, engine='c')
        dataframe = dataframe[list(columns)]
        dataframe.columns = (0, 1)
    except (FileNotFoundError, ValueError) as e:
        dataframe = None
        error = e
    finally:
        return dataframe, error


def from_shapefile(data):

    try:
        dataframe = None
        error = None
        import shapefile
        sf = shapefile.Reader(data)
        shape_type = sf.shapes()[0].shapeType
        # Only accept Point, PointZ and PointM geometries
        if shape_type in (1, 11, 21):
            coords = [shape.points[0] for shape in sf.iterShapes()]
            dataframe = pandas.DataFrame(columns=(0, 1), data=coords)
    except shapefile.ShapefileException as e:
        dataframe = None
        error = e
    finally:
        return dataframe, shape_type, error
