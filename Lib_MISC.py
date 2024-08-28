import re
import pya
import math

class MISC(object):
    def __init__(self):
        super(MISC, self).__init__()
        
    def f_coerce(in_float, min_val = 0, max_val = 1E5, step = None):            
        if step :
            in_float = int(in_float/step) * step
            
        return sorted([ min_val, in_float, max_val])[1]
                 
    def s_coerce(in_string, min_val = 0, max_val = 1E5, default_val = 0, step = None):
        reg_str = "^([-]?[0-9]+[.]?[0-9]*)$"
        match   = re.findall(reg_str, in_string)
        result  = default_val
        
        if not(len(match) > 0):
            return result
        try:
            result = float(match[0])
            result = sorted([min_val, result, max_val])[1]
            
        except:
            result  = default_val
            
        return result
    
    def to_region(obj, unit):
        if isinstance(obj, pya.DPolygon):
            return pya.Region(obj.to_itype(unit))
            
        if isinstance(obj, pya.DBox):
            return pya.Region(pya.DPolygon(obj).to_itype(unit))
            
        if isinstance(obj, pya.Region):
            return obj
            
    def invert(obj, base, flag, unit):

        if not(flag):
            return obj
            
        return MISC.to_region(base, unit) - MISC.to_region(obj, unit)

            
    def bias(obj, bias, unit):
        bias = bias/unit
        
        if (bias == 0):
            return obj
            
        return MISC.to_region(obj, unit).sized(bias)

            
    def rounded(obj, round_in, round_out, points, unit):
        round_in  = round_in/unit
        round_out = round_out/unit
        if (round_out == 0) and (round_out == 0):
            return obj
           
        return MISC.to_region(obj, unit).rounded_corners(round_in, round_out, points)