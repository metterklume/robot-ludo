"""
Created on Fri Oct 23 14:00:00 2020

@author: abhishekroy
"""
import numpy as np
from matplotlib.patches import Circle, Wedge, Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt

import io
import PIL.Image as Image

def drawboard(board,size=7):
    '''Draw a board. Requires matplotlib and PIL'''
    fig, ax = plt.subplots()

    fig.set_size_inches(size,size)
    ax.set_ylim(-1.2, 1.2)
    ax.set_xlim(-2, 2)
    ax.set_aspect('equal')
    ax.set_axis_off()

    patches = []
    r = 1
    width = 0.45
    theta1 = 360 * np.array([x/board.length for x in range(board.length)])
    theta2 = theta1 + (360/board.length - 5)
    theta_offset = theta1[0]-theta2[0]/2
    theta1, theta2 = theta1+theta_offset, theta2+theta_offset

    for i,(t1,t2,is_safe) in enumerate(zip(theta1, theta2, board.safe)):
        wedge = Wedge((0, 0), r, t1, t2, width=width)
        if is_safe:
            wedge.set_color([0.1,.8,0.1,0.4])
        else:
            wedge.set_color([0.5,0.5,0.2,0.4])
        
        if i == 0:
            wedge.set_edgecolor([1,0,0,1])
        if i == board.length//2:
            wedge.set_edgecolor([0,0,1,1])
        patches.append(wedge)

    cr = 0.12
    R = r-width+cr
    for (i,count) in enumerate(board.blue):
        if count:
#             t = 0.7* theta1[i] + 0.3*theta2[i]
            t = 0.5*(theta1[i] + theta2[i])
            center = (R*np.cos(np.deg2rad(t)), R*np.sin(np.deg2rad(t)))
            circle = Circle(center, cr)
            circle.set_color([0,0,1,0.6])
            patches.append(circle)
        if count > 1:
            ax.annotate(count, center, fontsize=15, ha='center',va='center',
                       weight="bold")        
    
    R = r-cr
    for (i,count) in enumerate(board.red):
        if count:
            t = 0.5*(theta1[i] + theta2[i])
#             t = 0.3*theta1[i] +  0.7*theta2[i]
            center = (R*np.cos(np.deg2rad(t)), R*np.sin(np.deg2rad(t)))
            circle = Circle(center, cr)
            circle.set_color([1,0,0,0.6])
            patches.append(circle)

        if count > 1:
            ax.annotate(count, center, fontsize=15, ha='center',va='center',
                       weight="bold")

    R = r+0.15
    for i in range(board.length):
        t = (theta1[i] + theta2[i])/2
        center = (R*np.cos(np.deg2rad(t)), R*np.sin(np.deg2rad(t)))
        ax.annotate(str(i), center, fontsize=12, ha='center',va='center',
                       weight="light")

    R = r+0.45
    if board.redpen:
        t = 0
        center = (R*np.cos(np.deg2rad(t)), R*np.sin(np.deg2rad(t)))
        circle = Circle(center, cr)
        circle.set_color([1,0,0,0.4])
        patches.append(circle)
        ax.annotate(board.redpen, center, fontsize=15, ha='center',va='center')

    if board.bluepen:
        t = 180
        center = (R*np.cos(np.deg2rad(t)), R*np.sin(np.deg2rad(t)))
        circle = Circle(center, cr)
        circle.set_color([0,0,1,0.4])
        patches.append(circle)
        ax.annotate(board.bluepen, center, fontsize=15, ha='center',va='center')

    p = PatchCollection(patches, match_original=True)
    ax.add_collection(p)

    buf = io.BytesIO()
    fig.savefig(buf, format='png',bbox_inches='tight')
    buf.seek(0)
    im = Image.open(buf)
    plt.close(fig) #don't display image
    return im