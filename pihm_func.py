#!/usr/bin/env python3

import sys
import os
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from textwrap import wrap


def read_mesh(simulation):
    filen = simulation + '/' + simulation + '.mesh'

    # Read mesh file into an array of strings with '#' and leading white spaces
    # removed
    meshstr = []
    with open(filen) as file:
        for line in file:
            if line.strip() and line.strip()[0] != '#':
                meshstr.append(line.strip())

    # Read number of elements
    nelem = int(meshstr[0].split()[1])

    # Read nodes information
    trimat = []
    for kelem in range(nelem):
        tri_str = meshstr[2 + kelem].split()[1:4]
        trimat.append([int(elem_str) - 1 for elem_str in tri_str])

    # Read number of nodes
    nnodes = int(meshstr[2 + nelem].split()[1])

    # Read X, Y, ZMIN, and ZMAX
    x = []
    y = []
    _zmin = []
    _zmax = []
    for knode in range(nnodes):
        strs = meshstr[4 + nelem + knode].split()[1:]
        x.append(float(strs[0]))
        y.append(float(strs[1]))
        _zmin.append(float(strs[2]))
        _zmax.append(float(strs[3]))

    # Calculate surface elevation of each triangular grid
    zmin = []
    zmax = []
    for i in range(nelem):
        zmin.append(np.mean([_zmax[ielem] for ielem in np.array(trimat)[i]]))
        zmax.append(np.mean([_zmax[ielem] for ielem in np.array(trimat)[i]]))


    return (nelem, nnodes, np.array(trimat), np.array(x), np.array(y),
        np.array(zmin), np.array(zmax))


def read_river(simulation):
    filen = simulation + '/' + simulation + '.riv'

    # Read river file into an array of strings with '#' and leading white spaces removed
    riverstr = []
    with open(filen) as file:
        for line in file:
            if line.strip() and line.strip()[0] != '#':
                riverstr.append(line.strip())

    # Read number of river segments
    nriver = int(riverstr[0].split()[1])

    # Read nodes information
    from_node = []
    to_node = []
    for kriver in range(nriver):
        strs = riverstr[2 + kriver].split()[1:3]
        from_node.append(int(strs[0]) - 1)
        to_node.append(int(strs[1]) - 1)

    return (nriver, from_node, to_node)

def read_attrib(simulation):
    filen = simulation + '/' + simulation + '.att'

    attribstr = []
    with open(filen) as file:
        for line in file:
            if line.strip() and line.strip()[0] != '#':
                attribstr.append(line.strip())

    soil = []
    lc = []
    meteo = []
    attribstr.pop(0)
    for line in attribstr:
        strs = line.split()[1:5]
        soil.append(int(strs[0]))
        lc.append(int(strs[2]))
        meteo.append(int(strs[3]))

    return (np.array(soil), np.array(lc), np.array(meteo))


def read_lsm(simulation):
    filen = simulation + '/' + simulation + '.lsm'

    # Read lsm file into an array of strings with '#' and leading white spaces removed
    lsmstr = []
    with open(filen) as file:
        for line in file:
            if line.strip() and line.strip()[0] != '#':
                lsmstr.append(line.strip())

    # Read number of river segments
    latitude = float(lsmstr[0].split()[1])
    longitude = float(lsmstr[1].split()[1])

    return (latitude, longitude)


def lutype(lu):
    lutext = [
        r'Evergreen Needleleaf Forest',
        r'Evergreen Broadleaf Forest',
        r'Deciduous Needleleaf Forest',
        r'Deciduous Broadleaf Forest',
        r'Mixed Forest',
        r'Closed Shrubland',
        r'Open Shrubland',
        r'Woody Savannas',
        r'Savannas',
        r'Grasslands',
        r'Permanent Wetlands',
        r'Croplands',
        r'Urban and Built-Up',
        r'Cropland/Natural Vegetation Mosaic',
        r'Snow and Ice',
        r'Barren or Sparsely Vegetated',
        r'Water',
        r'',
        r'',
        r'',
        r'Open Water',
        r'Perennial Ice/Snow',
        r'Developed Open Space',
        r'Developed Low Intensity',
        r'Developed Medium Intensity',
        r'Developed High Intensity',
        r'Barren Land',
        r'Deciduous Forest',
        r'Evergreen Forest',
        r'Mixed Forest',
        r'Dwarf Scrub',
        r'Shrub/Scrub',
        r'Grassland/Herbaceous',
        r'Sedge/Herbaceous',
        r'Lichens',
        r'Moss',
        r'Pasture/Hay',
        r'Cultivated Crops',
        r'Woody Wetland',
        r'Emergent Herbaceous Wetland']

    return lutext[lu - 1]


def lucolor(lu):
    lucmap = [
    [0,   128, 0  ],    # Evergreen Needleleaf Forest
    [0,   255, 0  ],    # Evergreen Broadleaf Forest
    [153, 204, 0  ],    # Deciduous Needleleaf Forest
    [153, 255, 153],    # Deciduous Broadleaf Forest
    [51,  153, 102],    # Mixed Forest
    [153, 51,  102],    # Closed Shrubland
    [255, 204, 153],    # Open Shrubland
    [204, 255, 204],    # Woody Savannas
    [255, 204, 0  ],    # Savannas
    [255, 153, 0  ],    # Grasslands
    [0,   102, 153],    # Permanent Wetlands
    [255, 255, 0  ],    # Croplands
    [255, 0,   0  ],    # Urban and Built-Up
    [153, 153, 102],    # Cropland/Natural Vegetation Mosaic
    [255, 255, 255],    # Snow and Ice
    [128, 128, 128],    # Barren or Sparsely Vegetated
    [0,   0,   128],    # Water
    [0,   0,   0  ],
    [0,   0,   0  ],
    [0,   0,   0  ],
    [71,  107, 160],    # Open Water
    [209, 221, 249],    # Perennial Ice/Snow
    [221, 201, 201],    # Developed Open Space
    [216, 147, 130],    # Developed Low Intensity
    [237, 0,   0  ],    # Developed Medium Intensity
    [170, 0,   0  ],    # Developed High Intensity
    [178, 173, 163],    # Barren Land
    [104, 170, 99 ],    # Deciduous Forest
    [28,  99,  48 ],    # Evergreen Forest
    [181, 201, 142],    # Mixed Forest
    [165, 140, 48 ],    # Dwarf Scrub
    [204, 186, 124],    # Shrub/Scrub
    [226, 226, 193],    # Grassland/Herbaceous
    [201, 201, 119],    # Sedge/Herbaceous
    [153, 193, 71 ],    # Lichens
    [119, 173, 147],    # Moss
    [219, 216, 61 ],    # Pasture/Hay
    [170, 112, 40 ],    # Cultivated Crops
    [186, 216, 234],    # Woody Wetland
    [112, 163, 186]]    # Emergent Herbaceous Wetland

    return lucmap[lu - 1]

def total_area(x, y, trimat):
    area = 0.0
    for tri in trimat:
        area += 0.5 * ((x[tri[1]] - x[tri[0]]) * (y[tri[2]] - y[tri[0]]) -
            (y[tri[1]] - y[tri[0]]) * (x[tri[2]] - x[tri[0]]))

    return area / 1.0E6


def main():
    if len(sys.argv) != 2:
        raise ValueError('Please specify a project to be plotted.')

    simulation = str(sys.argv[1])

    # Read input files
    (nelem, nnodes, trimat, x, y, zmin, zmax) = read_mesh(simulation)
    (nriver, from_node, to_node) = read_river(simulation)
    (soil, lc, meteo) = read_attrib(simulation)
    (latitude, longitude) = read_lsm(simulation)

    domain_shape = (np.max(x) - np.min(x)) / (np.max(y) - np.min(y))

    # Create line collection of river segments for plotting
    lines = [[(x[from_node[i]], y[from_node[i]]),
              (x[to_node[i]], y[to_node[i]])] for i in range(nriver)]
    river_segments = LineCollection(lines, linewidths=3, colors='blue',
                                    linestyle='solid')

    # Create images directory if don't exist
    if not os.path.exists(simulation + '/images'):
        os.mkdir(simulation + '/images')

    # Plot surface elevation
    fig = plt.figure(figsize=(12,9))
    if domain_shape < 1.33:
        ax = fig.add_axes([0, 0, 0.8, 1])
    else:
        ax = fig.add_axes([0, 0.2, 1, 0.8])
    tpc = ax.tripcolor(x, y, trimat, facecolors=zmax, edgecolors='k',
                                     alpha = 0.9, lw=0.1, cmap='terrain')
    ax.add_collection(river_segments)
    ax.set_aspect('equal')
    if domain_shape < 1.33:
        cbaxes = fig.add_axes([0.8, 0.2, 0.025, 0.6])
        cbar = fig.colorbar(tpc, shrink=0.8, cax=cbaxes)
    else:
        cbaxes = fig.add_axes([0.2, 0.15, 0.6, 0.04])
        cbar = fig.colorbar(tpc, orientation='horizontal', shrink=0.8,
            cax=cbaxes)
    cbar.set_label(label=r'Elevation (m)', weight='bold', size=25)
    cbar.ax.tick_params(labelsize=20)
    ax.axis('off')
    fig.savefig(simulation + '/images/topo.png')

    # Plot soil types
    fig = plt.figure(figsize=(12,9))
    ax = fig.add_axes([0, 0, 1, 1])
    tpc = ax.tripcolor(x, y, trimat, facecolors=soil, edgecolors='k',
                                      alpha = 0.9, lw=0.1, cmap='viridis_r')
    ax.set_aspect('equal')
    plt.axis('off')
    fig.savefig(simulation + '/images/soil.png')

    # Plot land cover types
    fig = plt.figure(figsize=(12,9))
    if domain_shape < 1.33:
        ax = fig.add_axes([0, 0, 0.75, 1])
    else:
        ax = fig.add_axes([0, 0.2, 1, 0.8])
    ax.triplot(x, y, trimat, lw=0.0)
    lh = []
    for lu in range(1, 41):
        if lu in lc:
            patches = []
            [patches.append((Polygon(np.array([x[i], y[i]]).transpose(), True)))
                for i in trimat[lc == lu]]
            p = PatchCollection(patches, facecolors=np.array(lucolor(lu))/255.0,
                edgecolors='k', alpha=0.9, lw=0.1)
            ax.add_collection(p)
            if domain_shape < 1.33:
                lh.append(mpatches.Patch(color=np.array(lucolor(lu))/255.0,
                    alpha=0.9, label=('\n'.join(wrap(lutype(lu), 16)))))
            else:
                lh.append(mpatches.Patch(color=np.array(lucolor(lu))/255.0,
                    alpha=0.9, label=lutype(lu)))

    if domain_shape < 1.33:
        fig.legend(handles=lh, bbox_to_anchor=([0.7, 0.2, 0.3, 0.6]),
            loc='center', borderaxespad=0, framealpha=0.9, fontsize=18)
    else:
        ncol = math.ceil(len(lh) / 4)
        fig.legend(handles=lh, bbox_to_anchor=([0.2, 0.05, 0.6, 0.2]),
            loc='center', ncol=ncol, borderaxespad=0, framealpha=0.9, fontsize=18)
    ax.set_aspect('equal')
    plt.axis('off')
    fig.savefig(simulation + '/images/lc.png')

    # Plot forcing zones
    fig = plt.figure(figsize=(12,9))
    if domain_shape < 1.33:
        ax = fig.add_axes([0, 0, 0.8, 1])
    else:
        ax = fig.add_axes([0, 0.2, 1, 0.8])
    tpc = ax.tripcolor(x, y, trimat, facecolors=meteo, edgecolors='k',
                                     alpha = 0.9, lw=0.1, cmap='viridis_r')
    ax.set_aspect('equal')
    if domain_shape < 1.33:
        cbaxes = fig.add_axes([0.8, 0.2, 0.025, 0.6])
        cbar = fig.colorbar(tpc, shrink=0.8, cax=cbaxes)
    else:
        cbaxes = fig.add_axes([0.2, 0.15, 0.6, 0.04])
        cbar = fig.colorbar(tpc, orientation='horizontal', shrink=0.8,
            cax=cbaxes)
    cbar.set_label(label=r'Forcing zone', weight='bold', size=25)
    cbar.ax.tick_params(labelsize=20)
    ax.axis('off')
    fig.savefig(simulation + '/images/meteo.png')

    # Write README.md
    readme = open(simulation + '/README.md', 'w')
    readme.write('# Watershed\n\n')
    readme.write('**Location:** ')
    if latitude >= 0.0:
        readme.write('%.3f &deg;N, ' %(latitude))
    else:
        readme.write('%.3f &deg;S, ' %(-latitude))
    if longitude >= 0.0:
        readme.write('%.3f &deg;E<br>\n' %(longitude))
    else:
        readme.write('%.3f &deg;W<br>\n' %(-longitude))
    readme.write('**Total area:** %.2f km<sup>2</sup><br>\n' %(total_area(x, y, trimat)))
    readme.write('**Number of triangular grids:** %d<br>\n' %(nelem))
    readme.write('**Number of river segments:** %d<br>\n' %(nriver))
    readme.write('**Calibration:**\n')
    readme.write('\n')
    readme.write('## Topography\n\n')
    readme.write('![Topography](https://github.com/PSUmodeling/PIHM-Simulations/blob/master/%s/images/topo.png "Topography")\n' %(simulation))
    readme.write('\n')
    readme.write('## Soil\n\n')
    readme.write('![Soil](https://github.com/PSUmodeling/PIHM-Simulations/blob/master/%s/images/soil.png "Soil")\n' %(simulation))
    readme.write('\n')
    readme.write('## Land cover\n\n')
    readme.write('![Land cover](https://github.com/PSUmodeling/PIHM-Simulations/blob/master/%s/images/lc.png "Land cover")\n' %(simulation))
    readme.write('\n')
    readme.write('## Forcing\n\n')
    readme.close()

if __name__ == '__main__':
    main()
