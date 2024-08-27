import pya
from Lib_STL        import STL
from Lib_MISC       import MISC

class RING(pya.PCellDeclarationHelper):
    def __init__(self):
        super().__init__()
        self.dimension_option_dict  = {
            "By Radius"   : 0, 
            "By Diameter" : 1, 
        }
        
        self.geometry_option_dict  = {
            "By Inner Geometry" : 0, 
            "By Center Line"    : 1, 
            "By Outer Geometry" : 2,
        }
        
        self.param("name",         self.TypeString,  "Name",                              default =   "")
        self.param("main",         self.TypeLayer,   "Layer",                             default = pya.LayerInfo(1, 0))
        
        self.d_option = self.param("dimension_option", self.TypeString,  "Dimension Options",  default = 1)
        self.g_option = self.param("geometry_option",  self.TypeString,  "Geometry Options",   default = 2)
        
        
        self.param("size",         self.TypeDouble,  "Size",               unit =  "um",  default =   10)
        self.param("line_w",       self.TypeDouble,  "Line Width",         unit =  "um",  default =    2)
        self.param("start_a",      self.TypeDouble,  "Start Angle",        unit = "deg",  default =    0)

        self.param("ring_points",  self.TypeInt,     "Ring Points",        unit = "pts",  default =   32)
        self.param("bias",         self.TypeDouble,  "Shape Bias",         unit = "um",   default =    0)

        _ = [ self.d_option.add_choice(k,v) for k, v in self.dimension_option_dict.items()]
        _ = [ self.g_option.add_choice(k,v) for k, v in self.geometry_option_dict.items()]

    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = self.name
        param_name  = f"{self.size},{self.line_w})"
        
        return "_".join([ n for n in [custom_name, class_name, param_name] if n ])
    
        
    def coerce_parameters_impl(self):         
        self.line_w      = MISC.f_coerce(self.line_w,         0)  
        self.size        = MISC.f_coerce(self.size, self.line_w) 
        self.ring_points = MISC.f_coerce(self.ring_points,    4)  


    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
    
    def parameters_from_shape_impl(self):
        pass
    
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self): 
        radius_center = (self.size * [1, 0.5][self.dimension_option]) + (self.line_w * [ 0.5, 0, -0.5][self.geometry_option])
        radius_in     = radius_center - (self.line_w * 0.5)
        radius_out    = radius_center + (self.line_w * 0.5)
        radius_in     = radius_in  if radius_in  > 0 else 0
        radius_out    = radius_out if radius_out > 0 else 0
        
        dpoints_in    = STL.arc(0, 0, r = radius_in,  p = self.ring_points, deg1 = self.start_a,     deg2=self.start_a + 360, center_pt = False)
        dpoints_out   = STL.arc(0, 0, r = radius_out, p = self.ring_points, deg1=self.start_a + 360, deg2 = self.start_a,     center_pt = False)
        poly          = pya.DPolygon(dpoints_in + dpoints_out)     
        obj           = MISC.bias(poly, self.bias, self.layout.dbu)
            
        self.cell.shapes(self.main_layer).insert(obj)
        