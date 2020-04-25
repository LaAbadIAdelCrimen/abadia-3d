import numpy as np
import pandas as pd

# Reading the data from a CSV file using pandas
alturas = pd.read_csv('files/alturas-final.csv', sep=',', header=0)
alturas.head(10)

maps = np.zeros((3, 256, 256))
bigmaps = np.zeros ((3, 256, 256, 256))
for index, dd in alturas.iterrows():
    dd['height'] &= 0x0f
    #print (f"{dd}")
    if (dd['Level'] >= 0):
       maps[dd['Level'], dd['X'], dd['Y']] = max(dd['height'], maps[dd['Level'], dd['X'], dd['Y']])
       bigmaps[dd['Level'], dd['X'], dd['Y'], dd['height']] = 1

import seaborn as sns
import matplotlib.pylab as plt
print(maps[0])
dd = maps[0]  # [:150][:200]
# dd = np.random.rand(10, 12)
fig  = plt.figure(figsize=(10,10),facecolor = 'white', dpi=100)
ax = sns.heatmap(dd, linewidth=0)
plt.show()

import math
import stl
from stl import mesh
import numpy


# find the max dimensions, so we can know the bounding box, getting the height,
# width, length (because these are the step size)...
def find_mins_maxs(obj):
    minx = maxx = miny = maxy = minz = maxz = None
    for p in obj.points:
        # p contains (x, y, z)
        if minx is None:
            minx = p[stl.Dimension.X]
            maxx = p[stl.Dimension.X]
            miny = p[stl.Dimension.Y]
            maxy = p[stl.Dimension.Y]
            minz = p[stl.Dimension.Z]
            maxz = p[stl.Dimension.Z]
        else:
            maxx = max(p[stl.Dimension.X], maxx)
            minx = min(p[stl.Dimension.X], minx)
            maxy = max(p[stl.Dimension.Y], maxy)
            miny = min(p[stl.Dimension.Y], miny)
            maxz = max(p[stl.Dimension.Z], maxz)
            minz = min(p[stl.Dimension.Z], minz)
    return minx, maxx, miny, maxy, minz, maxz


def translate(_solid, step, padding, multiplier, axis):
    if axis == 'x':
        items = [0, 3, 6]
    elif axis == 'y':
        items = [1, 4, 7]
    elif axis == 'z':
        items = [2, 5, 8]
    for p in _solid.points:
        # point items are ((x, y, z), (x, y, z), (x, y, z))
        for i in range(3):
            p[items[i]] += (step * multiplier) + (padding * multiplier)


def copy_obj(obj, dims, num_rows, num_cols, num_layers):
    w, l, h = dims
    copies = []
    for layer in range(num_layers):
        for row in range(num_rows):
            for col in range(num_cols):
                # skip the position where original being copied is
                if row == 0 and col == 0 and layer == 0:
                    continue
                _copy = mesh.Mesh(obj.data.copy())
                # pad the space between objects by 10% of the dimension being
                # translated
                if col != 0:
                    translate(_copy, w, 0, col, 'x')
                if row != 0:
                    translate(_copy, l, 0, row, 'y')
                if layer != 0:
                    translate(_copy, h, 0, layer, 'z')
                copies.append(_copy)
    return copies

# Using an existing stl file:
main_body = mesh.Mesh.from_file('files/cube.stl')

# Dont want to rotate along Y
# main_body.rotate([0.0, 0.5, 0.0], math.radians(90))

minx, maxx, miny, maxy, minz, maxz = find_mins_maxs(main_body)
w1 = maxx - minx
l1 = maxy - miny
h1 = maxz - minz
copies = copy_obj(main_body, (w1, l1, h1), 1, 1, 1)

# I wanted to add another related STL to the final STL
twist_lock = mesh.Mesh.from_file('files/cube.stl')

minx, maxx, miny, maxy, minz, maxz = find_mins_maxs(twist_lock)
w2 = maxx - minx
l2 = maxy - miny
h2 = maxz - minz


translate(twist_lock, w1, 0, 3, 'x')

copies2 = copy_obj(twist_lock, (w2, l2, h2), 2, 2, 2)
combined = mesh.Mesh(numpy.concatenate([main_body.data, twist_lock.data] +
                                    [copy.data for copy in copies] +
                                    [copy.data for copy in copies2]))

combined.save('combined.stl', mode=stl.Mode.BINARY)  # save as bin

# Optionally render the rotated cube faces
from matplotlib import pyplot
from mpl_toolkits import mplot3d

# Create a new plot
figure = pyplot.figure()
axes = mplot3d.Axes3D(figure)

# Render the cube
axes.add_collection3d(mplot3d.art3d.Poly3DCollection(combined.vectors))

# Auto scale to the mesh size
scale = combined.points.flatten('C')
axes.auto_scale_xyz(scale, scale, scale)

# Show the plot to the screen
pyplot.show()

for ii in range(0, 3):
    level = mesh.Mesh.from_file('files/cube.stl')

    copies = []
    for keys, val in np.ndenumerate(bigmaps[ii]):
        if (val == 1):
            for hh in range(0,keys[2]+1):
                _copy = mesh.Mesh(level.data.copy())
                translate(_copy, 1, 0, keys[1], 'x')
                translate(_copy, 1, 0, keys[0], 'y')
                translate(_copy, 1, 0, keys[2]-hh, 'z')
                copies.append(_copy)

    combined2 = mesh.Mesh(numpy.concatenate([copy.data for copy in copies]))
    combined2.save(f"level{ii}.stl", mode=stl.Mode.BINARY)

# Create a new plot
figure = pyplot.figure()
axes = mplot3d.Axes3D(figure)

# Render the cube
axes.add_collection3d(mplot3d.art3d.Poly3DCollection(combined2.vectors))

# Auto scale to the mesh size
scale = combined2.points.flatten('C')
print(scale)
axes.auto_scale_xyz(scale, scale, scale)

# Show the plot to the screen
pyplot.show()

# testing the rooms around the first room (23)

level = mesh.Mesh.from_file('files/cube.stl')

copies = []
for keys, val in np.ndenumerate(bigmaps[0]):
  if (val == 1):
    _copy = mesh.Mesh(level.data.copy())
    translate(_copy, 1, 0, keys[0] - 100, 'x')
    translate(_copy, 1, 0, keys[1] - 100, 'y')
    translate(_copy, 1, 0, keys[2], 'z')
    copies.append(_copy)

combined2 = mesh.Mesh(numpy.concatenate([copy.data for copy in copies]))
combined2.save(f"test.stl", mode=stl.Mode.BINARY)

# Create a new plot
figure = pyplot.figure()
axes = mplot3d.Axes3D(figure)

# Render the cube
axes.add_collection3d(mplot3d.art3d.Poly3DCollection(combined2.vectors))

# Auto scale to the mesh size
scale = combined2.points.flatten('C')
print(scale)
axes.auto_scale_xyz(scale, scale, range(20))

# Show the plot to the screen
pyplot.show()
