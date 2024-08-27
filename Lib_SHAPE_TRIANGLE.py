import re
import pya

from Lib_STL        import STL

class TRIANGLE(pya.PCellDeclarationHelper):
    def __init__(self):
        super().__init__()
        

        self.param("name",         self.TypeString,  "Name",                              default =   "")
        self.param("main",         self.TypeLayer,   "Layer",                             default = pya.LayerInfo(1, 0))
        
        self.param("size_h",       self.TypeDouble,  "Size Height",        unit = "um",   default =   30)
        self.param("size_w",       self.TypeDouble,  "Size Width",         unit = "um",   default =   10)
        self.param("prime_a",      self.TypeDouble,  "Prime Angle",        unit = "deg",  default =   90)

        self.param("rounding",     self.TypeDouble,  "Rounding",           unit =  "um",  default =    0)
        self.param("points",       self.TypeInt,     "Round Points",       unit = "pts",  default =   32)

         
    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = self.name
        param_name  = f""
        
        return "_".join([ n for n in [custom_name, class_name, param_name] if n ])
           

    def coerce_parameters_impl(self):      
        self.size_h   = 0 if self.size_h   < 0 else self.size_h
        self.size_w   = 0 if self.size_w   < 0 else self.size_w
        self.rounding = 0 if self.rounding < 0 else self.rounding
        self.points   = 4 if self.points   < 4 else self.points
        self.prime_a  = sorted([0, self.prime_a, 179.9])[1]
            
    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
    
    def parameters_from_shape_impl(self):
        pass
    
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self): 
        dx1 =   self.size_w
        dy2 =   self.size_h
        dx2 = - self.size_h * STL.tan(self.prime_a - 90)
        dpoints = [
            pya.DPoint(   0,    0), 
            pya.DPoint( dx1,    0),
            pya.DPoint( dx2,  dy2),
        ]

        poly    = pya.DPolygon(dpoints)
        
        if self.rounding:
            poly = poly.round_corners(self.rounding, self.rounding, self.points)
            
        self.cell.shapes(self.main_layer).insert(poly)

