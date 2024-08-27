import pya
from Lib_STL        import STL
from Lib_MISC       import MISC

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
        self.param("bias",         self.TypeDouble,  "Shape Bias",         unit = "um",   default =    0)
         
    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = self.name
        param_name  = f""
        
        return "_".join([ n for n in [custom_name, class_name, param_name] if n ])
           

    def coerce_parameters_impl(self):      
        self.size_h   = MISC.f_coerce(self.size_h,   0)
        self.size_w   = MISC.f_coerce(self.size_w,   0)
        self.rounding = MISC.f_coerce(self.rounding, 0)
        self.points   = MISC.f_coerce(self.points,   4)
        self.prime_a  = MISC.f_coerce(self.prime_a,  0, 179.9)
            
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
        
        obj = MISC.bias(poly, self.bias, self.layout.dbu)
            
        self.cell.shapes(self.main_layer).insert(obj)

