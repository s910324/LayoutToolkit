import re
import pya

from Lib_STL        import STL

class TRIANGLE_ISO(pya.PCellDeclarationHelper):
    def __init__(self):
        super().__init__()
        
        self.dimension_option_dict  = {
            "By Height and Width"   : 0, 
            "By Height and Angle"   : 1, 
            "By Width  and Angle"   : 2, 
        }
        self.param("name",         self.TypeString,  "Name",                              default =   "")
        self.param("main",         self.TypeLayer,   "Layer",                             default = pya.LayerInfo(1, 0))
        
        self.d_option = self.param("dimension_option",  self.TypeString,  "Dimension Options",   default = 0)
        
        self.param("size_h",       self.TypeString,  "Size Height",        unit = "um",   default =   "10")
        self.param("size_w",       self.TypeString,  "Size Width",         unit = "um",   default =   "30")
        self.param("prime_a",      self.TypeString,  "Prime Angle",        unit = "deg",  default =   "--")

        self.param("rounding",     self.TypeDouble,  "Rounding",           unit =  "um",  default =    0)
        self.param("points",       self.TypeInt,     "Round Points",       unit = "pts",  default =   32)
        
        _ = [ self.d_option.add_choice(k,v) for k, v in self.dimension_option_dict.items()]
         
    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = self.name
        param_name  = f""
        
        return "_".join([ n for n in [custom_name, class_name, param_name] if n ])
    
    def float_coerce(self, in_val, min_val = 0, max_val = 1E5, default_val = 0):
        reg_str = "^([-]?[0-9]+[.]?[0-9]*)$"
        match   = re.findall(reg_str, in_val)
        result  = default_val
        
        if not(len(match) > 0):
            return result
        try:
            result = float(match[0])
            result = sorted([min_val, result, max_val])[1]
            
        except:
            result  = default_val
            
        return result


    def coerce_parameters_impl(self):      
        self.size_w_float  = self.float_coerce(self.size_w,  0, 1E5,   10)
        self.size_h_float  = self.float_coerce(self.size_h,  0, 1E5,   30)
        self.prime_a_float = self.float_coerce(self.prime_a, 0, 179.9, 30)

        if self.dimension_option == 0 : #"By Height and Width"
            self.size_w  = str(self.size_w_float)
            self.size_h  = str(self.size_h_float)
            self.prime_a = "--"
        
        elif self.dimension_option == 1: # "By Height and Angle"
            self.size_w  = "--"   
            self.size_h  = str(self.size_h_float)
            self.prime_a = str(self.prime_a_float)
        
        elif self.dimension_option == 2: # "By Width  and Angle"
            self.size_w  = str(self.size_w_float)
            self.size_h  = "--" 
            self.prime_a = str(self.prime_a_float)

        self.rounding = 0 if self.rounding < 0 else self.rounding
        self.points   = 4 if self.points   < 4 else self.points
            
    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
    
    def parameters_from_shape_impl(self):
        pass
    
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self): 
        dpoints  =[]
        
        if self.dimension_option == 0 : #"By Height and Width"
            dx = self.size_w_float / 2
            dy = self.size_h_float
            
            dpoints = [
                pya.DPoint(  0,   0), 
                pya.DPoint(-dx, -dy),
                pya.DPoint( dx, -dy),
            ]

        elif self.dimension_option == 1: # "By Height and Angle"
            dx = self.size_h_float * STL.tan(self.prime_a_float / 2)
            dy = self.size_h_float
            
            dpoints = [
                pya.DPoint(  0,   0), 
                pya.DPoint(-dx, -dy),
                pya.DPoint( dx, -dy),
            ]
            
        elif self.dimension_option == 2: # "By Width  and Angle"
            dx = self.size_w_float / 2
            dy =  dx / STL.tan(self.prime_a_float / 2) 
            
            dpoints = [
                pya.DPoint(  0,   0), 
                pya.DPoint(-dx, -dy),
                pya.DPoint( dx, -dy),
            ]
            
        poly    = pya.DPolygon(dpoints)
        
        if self.rounding:
            poly = poly.round_corners(self.rounding, self.rounding, self.points)
            
        self.cell.shapes(self.main_layer).insert(poly)

