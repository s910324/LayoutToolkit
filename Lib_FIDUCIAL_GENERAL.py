import pya
from Lib_STL        import STL
from Lib_MISC       import MISC

class GENERAL(pya.PCellDeclarationHelper):
    def __init__(self):
        super().__init__()       
        self.type_option_dict = {
            "F-MARK"     : lambda : self.f_mark         (),
            "I-MARK"     : lambda : self.i_mark         (),
            "L-MARK"     : lambda : self.l_mark         (),
            "T-MARK"     : lambda : self.t_mark         (),
            "DOVETAIL"   : lambda : self.dovetail       (),
            "CROSS"      : lambda : self.cross_mark     (),
            "CROSS-BOX1" : lambda : self.cross_box_mark1(),
            "CROSS-BOX2" : lambda : self.cross_box_mark2(),
            "CROSS-BOX3" : lambda : self.cross_box_mark3(),
            "BOX-CROSS1" : lambda : self.box_cross_mark1(),
            "BOX-CROSS2" : lambda : self.box_cross_mark2(),
        }
          
        self.param("name",         self.TypeString,  "Name",                               default =    "")
        self.param("main",         self.TypeLayer,   "Pattern Layer",                      default = pya.LayerInfo(1, 0))
        self.param("base",         self.TypeLayer,   "Base Layer",                         default = pya.LayerInfo(1, 0))

        self.t_option = self.param("type_option",    self.TypeString, "Type Options",  default = 0)
        
        self.param("size_p",       self.TypeDouble,  "Pattern Size",       unit =  "um",   default =    10)
        self.param("line_w",       self.TypeDouble,  "Line Width",         unit =  "um",   default =     2)
        self.param("base_w",       self.TypeDouble,  "Base Width",         unit =  "um",   default =    15)
        self.param("base_h",       self.TypeDouble,  "Base Height",        unit =  "um",   default =    15)
        
        self.param("rounding",     self.TypeDouble,  "Rounding",           unit =  "um",   default =     0)
        self.param("points",       self.TypeInt,     "Round Points",       unit = "pts",   default =    32)
        self.param("bias",         self.TypeDouble,  "Shape Bias",         unit =  "um",   default =     0)
        self.param("invert",       self.TypeBoolean, "Pattern invert",                     default = False)
        
        _ = [ self.t_option.add_choice(k,v) for k, v in enumerate(self.type_option_dict.keys())]
        
        
    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = self.name
        param_name  = f"({self.size_p},{self.line_w})"
        
        return "_".join([ n for n in [custom_name, class_name, param_name] if n ])
        
    def coerce_parameters_impl(self):         
        self.size_p   = MISC.f_coerce(self.size_p,            0)
        self.line_w   = MISC.f_coerce(self.line_w,            0)
        self.base_w   = MISC.f_coerce(self.base_w,  self.size_p)
        self.base_h   = MISC.f_coerce(self.base_h,  self.size_p)
        self.rounding = MISC.f_coerce(self.rounding,          0)
        self.points   = MISC.f_coerce(self.points,            4)
        
    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
    
    def parameters_from_shape_impl(self):
        pass
    
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())
    
    def f_mark(self):
        return pya.DPolygon(STL.fpoints(0, 0, self.size_p, self.line_w)) 
        
    def cross_mark(self):
        return pya.DPolygon(STL.cross(  0, 0, self.size_p, self.size_p, self.line_w)) 
        
    def produce_impl(self):  
        key  = list(self.type_option_dict.keys())[self.type_option]
        poly = self.type_option_dict[key]()
        
        if self.rounding:
            poly = poly.round_corners(self.rounding, self.rounding, self.points)
            
        obj = MISC.bias(poly, self.bias, self.layout.dbu)

        self.cell.shapes(self.main_layer).insert(obj)
            