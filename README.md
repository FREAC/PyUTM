# PyUTM

PyUTM is a Python package that creates UTM (and UPS) grid references for point data.
It can also use those grid references to create spatially meaningful unique identifiers for tasks such as asset naming.

To install PyUTM, use PyPI:[*](#nb)
```
pip install pyutm
```

[What is a UTM grid reference?](#what-is-a-utm-grid-reference)

 - [Creating a UTM grid reference with PyUTM](#creating-a-utm-grid-reference-with-pyutm)

[What is a Unique Identifier?](#what-is-a-unique-identifier)

 - [Creating a Unique Identifier with PyUTM](#creating-a-unique-identifier-with-pyutm)

### What is a UTM grid reference?

The *Universal Transverse Mercator* (UTM) projection and grid allows any location in the world to be described by a
string of up to 15 characters. The precision of a location increases as characters are added to its description and
decreases as characters are removed.

The first set of characters in a UTM grid reference describes its *Grid Zone Designation* (GZD).
- This can be either two or three characters long and is comprised of a number between 1 and 60 followed by a letter: **33M**.
- The letters 'I' and 'O' are omitted to avoid confusion with the numbers '1' and '0'.
- With some exceptions in the northern latitudes, the GZD describes a standard area encompassing 6° of longitude and 8° of latitude.

The second set of characters in a UTM grid reference describes its 100 kilometer square within the GZD.
- This is always two characters long and is comprised of two letters, again omitting 'I' and 'O': **XS**.
 - Though the majority of squares within a GZD are 100 km on each side, those located on the edges of the GZD can be
smaller in area, due to the
[conformal nature of the Transverse Mercator projection](https://en.wikipedia.org/wiki/Conformal_map_projection).

The third and fourth sets of characters in a UTM grid reference describe its distance in meters from the lower left
corner of the 100 km square. The third set of characters describes the location's distance east of the lower left corner (its *easting*),
while the fourth set of characters describes the location's distance north of the lower left corner (its *northing*).
- Both sets can be between one and five characters long and are comprised entirely of digits; they must have the same
number of characters, which are not separated by a space: **96496691**.
  - 96496691 represents a location of 9649 easting and 6691 northing
- The number of digits used in each set determines the number of meters that those digits represent: as the number of
digits increases from one to five, so does the precision with which a location can be established within the 100 km square.

Number of Digits | Number of Meters | Size of Location
:---: | :---: | :---:
One | 10 000 | Local Area
Two | 1 000 | Neighborhood
Three | 100 | Football Field
Four | 10 | House
Five | 1 | Bath towel

### Creating a UTM Grid Reference with PyUTM

PyUTM will create UTM grid references for point data supplied as a list, CSV file, or Shapefile.

### What is a Unique Identifier?



### Creating a Unique Identifier with PyUTM

##### N.B.

*Python 2.7 users must install the
[Microsoft Visual C++ Compiler for Python 2.7](https://www.microsoft.com/en-us/download/details.aspx?id=44266)
before using this package.*