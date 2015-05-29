'''
Created on May 29, 2015

@author: roth
'''
import arcpy
import arcpy.da as da
import numpy as np

def AssignQuant(a,pso):
    ps = [x for x in pso] # converting to a list from an array for ease of use
    ps = [0.0] + ps
    print(ps)
    out = []
    rng = range(1,len(ps)+1)
    print(rng)
    for x in np.nditer(a,op_flags=['readwrite']):
        for i in rng: 
            if  ps[i-1] < x <= ps[i]:
                #x = i+1
                out.append(i)
                break
    outarr = np.array(out)
    return(outarr)


def Quantiles(in_features, in_field, in_quant, in_qdir):
    print("converting to numpy")
    nparray = da.FeatureClassToNumPyArray(in_features,["OID@",in_field],skip_nulls = True)
    
    print("calculating quantiles")
    n = 1.0/float(in_quant)
    qs = [n*x*100 for x in xrange(1,int(in_quant)+1)]
    print(qs)
    
    print("calculating percentiles")
    flcol = np.array(nparray[[in_field]], np.float)
    #mafldcol = ma.masked_invalid(flcol)
    ps = np.percentile(flcol, qs)
    print(ps)
    
    print("Adding new numpy field")
    newfldname = "".join(["Q",in_field])
    fldtype = (newfldname,'int',)
    dtype=nparray.dtype.descr
    dtype.append(fldtype)
    dtype2 = np.dtype(dtype)
    nparray2 = np.empty(nparray.shape, dtype=dtype2)
    for name in nparray.dtype.names:
        nparray2[name] = nparray[name]
    
    print("Apply along Axis")
    #out = np.apply_along_axis(AssignQuant, 0, flcol, qs=qs)
    out = AssignQuant(flcol,ps)
    if in_qdir == "Reverse":
        out = (int(in_quant) + 1) - out
    
    nparray2[newfldname] = out
    nparray3 = nparray2[['OID@',newfldname]]
    
    
    print("Extend table to include the new values")
    da.ExtendTable(in_features,"OBJECTID" ,nparray3,"OID@")
    
    
    print("Done")
    
    
in_features = r"D:\Projects\crc\QuantileCalc\Quantiles.gdb\Roi_data"
in_field = "people_mean"
in_quant = 5
in_qdir = "Normal"


Quantiles(in_features, in_field, in_quant, in_qdir)