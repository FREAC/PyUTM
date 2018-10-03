# PyUTM

PyUTM is a Python package that creates standardized grid references for point data.
It can also use those grid references to create spatially meaningful unique identifiers for tasks such as asset naming.

Grid references can be created in US National Grid, MGRS and UTM formats.

To install PyUTM, use PyPI:[*](#nb)
```
pip install pyutm
```

[What is a grid reference?](#what-is-a-grid-reference)

[What is a unique identifier?](#what-is-a-unique-identifier)

[Examples](#examples)

- [Lists](#lists)
- [CSVs](#csvs)
- [Shapefiles](#shapefiles)

[References](#references)

### What is a grid reference?

Based on the Universal Transverse Mercator (UTM) and Universal Polar Stereographic (UPS) map projections,
**a grid reference allows any location in the world to be described by a string of up to 15 characters**.
The precision of a location increases as characters are added to its grid reference and
decreases as characters are removed.

The **first set** of characters in a grid reference describes its **Grid Zone Designation** (GZD).
- This can be either two or three characters long and is comprised of a number between 1 and 60 followed by a letter
(*e.g.* **33M**). By default, PyUTM adds a leading zero to numbers less than 10 (*e.g.* **02U**).
- The letters 'I' and 'O' are omitted to avoid confusion with the numbers '1' and '0'.
- With some exceptions in the northern latitudes and at the poles, the GZD describes a standard area encompassing
6° of longitude and 8° of latitude.

The **second set** of characters in a grid reference describes its **100 kilometer square** within the GZD.
- This is always two characters long and is comprised of two letters, again omitting 'I' and 'O' (*e.g.* **XS**).
 - Though the majority of squares within a GZD are 100 km on each side, those located on the edges of the GZD can be
smaller in area, due to the [conformal nature of the projections](https://en.wikipedia.org/wiki/Conformal_map_projection)
from which the grid references are derived.

The **third and fourth sets** of characters in a grid reference describe its distance in meters from the lower left
corner of the 100 km square. The third set of characters describes **the location's distance east** of the lower left corner (its *easting*),
while the fourth set of characters describes **the location's distance north** of the lower left corner (its *northing*).
- Both sets can be between zero and five characters long and are comprised entirely of digits; they must have the same
number of characters and are not separated by a space (*e.g.* **96496691**).
  - 96496691 represents a location of 9649 easting and 6691 northing.
- The number of digits used in each set determines the number of meters that those digits represent. As the number of
digits increases from zero to five, so does the precision with which a location can be established within the 100 km square:

Number of Digits | Precision in Meters | Size of Location
:---: | :---: | :---:
Zero | 100 000 | Regional Area
One | 10 000 | Local Area
Two | 1 000 | Neighborhood
Three | 100 | Football Field
Four | 10 | House
Five | 1 | Bath towel

### What is a unique identifier?

A unique identifier (UID) modifies a point's grid reference by adding descriptive prefixes and suffixes to insure that
each point's reference is unique. It can also remove character sets from the grid reference to make a UID shorter,
as well as separate character sets by a delimiter to improve readability.   

### Examples

PyUTM will create grid references and unique identifiers for point data supplied as a list, CSV file or Shapefile.
Here's how.

#### Lists
```python

```

#### CSVs

#### Shapefiles


### References

National Geospatial-Intelligence Agency, *The Universal Grids and the Transverse Mercator and Polar Stereographic Map Projections*,
[NGA Standardization Document NGA.SIG.0012_2.0.0_UTMUPS](http://earth-info.nga.mil/GandG/publications/NGA_SIG_0012_2_0_0_UTMUPS/NGA.SIG.0012_2.0.0_UTMUPS.pdf).
Washington, D.C.: Office of Geomatics, 2014.
- PyUTM implements the logic found in Sections 11, 12 and 14 of this document.

National Geospatial-Intelligence Agency, *Universal Grids and Grid Reference Systems*,
[NGA Standardization Document NGA.STND.0037_2.0.0_GRIDS](http://earth-info.nga.mil/GandG/publications/NGA_STND_0037_2_0_0_GRIDS/NGA.STND.0037_2.0.0_GRIDS.pdf).
Washington, D.C.: Office of Geomatics, 2014.
- Though broader in scope than the previous document, Chapter 3 and Appendices A and B are particularly helpful. 

#### N.B.

*Python 2.7 users must install the
[Microsoft Visual C++ Compiler for Python 2.7](https://www.microsoft.com/en-us/download/details.aspx?id=44266)
before using this package.*