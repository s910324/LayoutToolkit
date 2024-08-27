import pya
from Lib_STL        import STL
from Lib_MISC       import MISC

class CIRCLERECT(pya.PCellDeclarationHelper):
    def __init__(self):
        super().__init__()
        self.center_option_dict  = {
            "Left Top"          : 0, 
            "Left Center"       : 1,
            "Left Bottom"       : 2,
            
            "Middle Top"        : 3,
            "Middle Center"     : 4,
            "Middle Bottom"     : 5,
            
            "Right Top"         : 6,
            "Right Center"      : 7,
            "Right Bottom"      : 8,
        }
        
        self.bool_option_dict  = {
            "Rect not Circle"   : 0,
            "Circle not Rect"   : 1,
            "Circle and Rect"   : 2,
            "Circle or  Rect"   : 3,
            "Circle diff Rect"  : 4,
        }
        
        self.dimension_option_dict  = {
            "By Radius"   : 0, 
            "By Diameter" : 1, 
        }
        
        self.param("name",         self.TypeString,  "Name",                              default =   "")
        self.param("main",         self.TypeLayer,   "Layer",                             default = pya.LayerInfo(1, 0))
        
        self.c_option = self.param("center_option",    self.TypeString, "Center Options",           default = 0)
        self.b_option = self.param("bool_option",      self.TypeString, "Shape Boolean Options",    default = 0)
        self.r_option = self.param("dimension_option", self.TypeString, "Circle Dimension Options", default = 1)
        
        self.param("size_w",       self.TypeDouble,  "Rect Width",         unit =  "um",  default =   10)
        self.param("size_h",       self.TypeDouble,  "Rect Height",        unit =  "um",  default =   10)
        self.param("size_r",       self.TypeDouble,  "Circle Size",        unit =  "um",  default =   20)
        self.param("circle_x",     self.TypeDouble,  "Circle Origin X",    unit =  "um",  default =    0)
        self.param("circle_y",     self.TypeDouble,  "Circle Origin Y",    unit =  "um",  default =    0)
        self.param("points",       self.TypeInt,     "Circle Points",      unit = "pts",  default =   32)
        self.param("bias",         self.TypeDouble,  "Shape Bias",         unit = "um",   default =    0)
        
        _ = [ self.c_option.add_choice(k,v) for k, v in self.center_option_dict.items()]
        _ = [ self.b_option.add_choice(k,v) for k, v in self.bool_option_dict.items()]
        _ = [ self.r_option.add_choice(k,v) for k, v in self.dimension_option_dict.items()]

    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = self.name
        param_name  = f"{self.size_w},{self.size_h},{self.size_r}"
        
        return "_".join([ n for n in [custom_name, class_name, param_name] if n ])

    def coerce_parameters_impl(self):         
        self.size_w = MISC.f_coerce(self.size_w,  0)
        self.size_h = MISC.f_coerce(self.size_h,  0)
        self.size_r = MISC.f_coerce(self.size_r,  0)
        self.points = MISC.f_coerce(self.points,  4)

    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
    
    def parameters_from_shape_impl(self):
        pass
    
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self): 
        unit = self.layout.dbu
        rx, ry = 0, 0
        
        if   self.center_option in [0, 1, 2]:
            rx =  self.size_w/2
            
        elif self.center_option in [6, 7, 8]:
            rx = -self.size_w/2
            
        if   self.center_option in [0, 3, 6]:
            ry = -self.size_h/2
            
        elif self.center_option in [2, 5, 8]:
            ry =  self.size_h/2
            
        radius   = (self.size_r * [1, 0.5][self.dimension_option])
        cdpoints = STL.circle(self.circle_x, self.circle_y, radius, p = self.points, deg1 = 0)   
        rdpoints = STL.rect(rx, ry, self.size_w, self.size_h)   
        cpoly    = pya.DPolygon(cdpoints + [cdpoints[0]])          
        rpoly    = pya.DPolygon(rdpoints)  
        cir_r    = pya.Region(cpoly.to_itype(unit))
        rect_r   = pya.Region(rpoly.to_itype(unit))
        result   = pya.Region()
        
        if   self.bool_option == 0 : # "Rect not Circle"   
            result = rect_r - cir_r
        elif self.bool_option == 1 : # "Circle not Rect"   
            result = cir_r - rect_r
        elif self.bool_option == 2 : # "Circle and Rect"
            result = rect_r & cir_r   
        elif self.bool_option == 3 : # "Circle or  Rect"   
            result = rect_r + cir_r
        elif self.bool_option == 4 : # "Circle diff Rect" 
            result = rect_r ^ cir_r 

        obj = MISC.bias(result, self.bias, self.layout.dbu)
            
        self.cell.shapes(self.main_layer).insert(obj)

        