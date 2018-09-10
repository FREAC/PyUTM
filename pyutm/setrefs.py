import os


def to_list(dataframe):

    return dataframe.values.tolist()


def to_csv(fname, column, input_data, dataframe):

    import pandas
    fname = set_fname(fname, input_data)
    output_df = pandas.read_csv(input_data)
    output_df[column] = dataframe[column]
    output_df.to_csv(fname, index=False)


def to_shp(fname, column, input_data, dataframe, shape_type):

    import shapefile
    fname = set_fname(fname, input_data)
    try:
        r = shapefile.Reader(input_data)
        w = shapefile.Writer(shape_type)
        w.fields = r.fields[1:]
        w.field(column, 'C', size=15)

        for index, shaperec in enumerate(r.iterShapeRecords()):
            w.point(*shaperec.shape.points[0])
            w.record(*shaperec.record + [dataframe[column].iloc[index]])
        w.save(fname)
    finally:
        try:
            w.close()
        except AttributeError:
            pass


def set_fname(path, input_data):

    if path:
        output_dir = os.path.dirname(path)
        output_check = os.path.basename(path).lower().endswith(('.csv', '.shp'))
        if output_check and os.path.isdir(output_dir):
            return path
        elif output_check and not output_dir:
            output_dir = os.path.dirname(input_data)
            return os.path.join(output_dir, path)
        else:
            raise FileNotFoundError
    else:
        return input_data
