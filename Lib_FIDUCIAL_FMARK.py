import pya
from Lib_STL        import STL
from Lib_MISC       import MISC

class FMARK(pya.PCellDeclarationHelper):
    def __init__(self):
        super().__init__()        
        self.param("name",         self.TypeString,  "Name",                               default =   "")
        self.param("main",         self.TypeLayer,   "Layer",                              default = pya.LayerInfo(1, 0))
        
        self.param("size",         self.TypeDouble,  "Size",               unit =  "um",   default =   10)
        self.param("line_w",       self.TypeDouble,  "Line Width",         unit =  "um",   default =    2)
        
        self.param("rounding",     self.TypeDouble,  "Rounding",           unit =  "um",   default =    0)
        self.param("points",       self.TypeInt,     "Round Points",       unit = "pts",   default =   32)
        self.param("bias",         self.TypeDouble,  "Shape Bias",         unit =  "um",   default =    0)
        
    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = self.name
        param_name  = f"({self.size},{self.line_w})"
        
        return "_".join([ n for n in [custom_name, class_name, param_name] if n ])
    
        
    def coerce_parameters_impl(self):         
        self.size     = MISC.f_coerce(self.size,       0)
        self.line_w   = MISC.f_coerce(self.line_w,     0)
        self.rounding = MISC.f_coerce(self.rounding,   0)
        self.points   = MISC.f_coerce(self.points,     4)

    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
    
    def parameters_from_shape_impl(self):
        pass
    
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())
    
        
    def produce_impl(self):  
        poly = pya.DPolygon(STL.fpoints(0, 0, self.size, self.line_w)) 
        
        if self.rounding:
            poly = poly.round_corners(self.rounding, self.rounding, self.points)
            
        obj = MISC.bias(poly, self.bias, self.layout.dbu)
        
        self.cell.shapes(self.main_layer).insert(obj)
            
            
            
            
            
            
            