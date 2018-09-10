import pandas


def from_list(data):

    try:
        df = None
        error = None
        import numpy
        df = pandas.DataFrame.from_records(numpy.array(data, ndmin=2))
    except ValueError as e:
        df = None
        error = e
    finally:
        return df, error


def from_csv(data, columns):

    try:
        df = None
        error = None
        df = pandas.read_csv(data, usecols=columns, engine='c')
        df = df[list(columns)]
        df.columns = (0, 1)
    except (FileNotFoundError, ValueError) as e:
        df = None
        error = e
    finally:
        return df, error


def from_shapefile(data):

    try:
        df = None
        error = None
        import shapefile
        sf = shapefile.Reader(data)
        shape_type = sf.shapes()[0].shapeType
        # Only accept Point, PointZ and PointM geometries
        if shape_type in (1, 11, 21):
            coords = [shape.points[0] for shape in sf.iterShapes()]
            df = pandas.DataFrame(columns=(0, 1), data=coords)
    except shapefile.ShapefileException as e:
        df = None
        error = e
    finally:
        return df, shape_type, error
