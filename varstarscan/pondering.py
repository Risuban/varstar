import numpy as np
from math import e

def proximity_ponderation(xpoints):
    """
    Function that gives a ponderation to the points acording to how far they
    are from the others (takes the x coordenates).
    """
    xpoints= np.array(xpoints)
    deltas= np.abs(xpoints-np.transpose([xpoints]))
    effects= np.exp(-deltas)
    weights= np.exp(-np.sum(effects,axis=0))
    return weights

def outlier_ponderation(ypoints,minreldesv=3.5,maxreldesv=5.0):
    """
    Function that gives a ponderation according to how likely is a point to be
    an outlier (takes the y coordenates).
    """
    ypoints= np.array(ypoints)
    mean= np.mean(ypoints)
    stddev= np.std(ypoints)
    reldesv= np.abs(ypoints-mean)/stddev
    ponders= np.maximum(0.0,np.minimum(1.0,(maxreldesv-reldesv)/(maxreldesv-minreldesv)))
    return ponders
