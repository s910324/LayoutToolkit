import pya
from Lib_STL        import STL
from Lib_MISC       import MISC

class RECT(pya.PCellDeclarationHelper):
    def __init__(self):
        super().__init__()
        self.center_option_dict  = {
            "Left Top"       : 0, 
            "Left Center"    : 1,
            "Left Bottom"    : 2,
            
            "Middle Top"     : 3,
            "Middle Center"  : 4,
            "Middle Bottom"  : 5,
            
            "Right Top"      : 6,
            "Right Center"   : 7,
            "Right Bottom"   : 8,
        }
        
        self.modify_option_dict  = {
            "Corner Rounding" : 0, 
            "Corner Chamfer"  : 1, 
        }
        
        self.param("name",         self.TypeString,  "Name",                               default =   "")
        self.param("main",         self.TypeLayer,   "Layer",                              default = pya.LayerInfo(1, 0))
        
        self.c_option = self.param("center_option", self.TypeString,  "Center Options",        default = 4)
        self.m_option = self.param("modify_option", self.TypeString,  "Corner Modify Options", default = 1)
        
        self.param("size_w",       self.TypeDouble,  "Width",              unit =  "um",   default =    5)
        self.param("size_h",       self.TypeDouble,  "Height",             unit =  "um",   default =   10)
        
        self.param("modify_lt",    self.TypeDouble,  "Corner LT Modify",   unit =  "um",   default =    0)
        self.param("modify_lb",    self.TypeDouble,  "Corner LB Modify",   unit =  "um",   default =    0)
        self.param("modify_rt",    self.TypeDouble,  "Corner RT Modify",   unit =  "um",   default =    0)
        self.param("modify_rb",    self.TypeDouble,  "Corner RB Modify",   unit =  "um",   default =    0)
        
        self.param("rounding",     self.TypeDouble,  "Global Rounding",    unit =  "um",   default =    0)
        self.param("points",       self.TypeInt,     "Round Points",       unit = "pts",   default =   32)
        self.param("bias",         self.TypeDouble,  "Shape Bias",         unit = "um",    default =    0)
        _ = [ self.c_option.add_choice(k,v) for k, v in self.center_option_dict.items()]
        _ = [ self.m_option.add_choice(k,v) for k, v in self.modify_option_dict.items()]

    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = self.name
        param_name  = f"({self.size_w},{self.size_h})"
        
        return "_".join([ n for n in [custom_name, class_name, param_name] if n ])
    
        
    def coerce_parameters_impl(self):         
        self.size_w    = MISC.f_coerce(self.size_w,    0)      
        self.size_h    = MISC.f_coerce(self.size_h,    0)  

        self.modify_lt = MISC.f_coerce(self.modify_lt, 0)   
        self.modify_lb = MISC.f_coerce(self.modify_lb, 0) 
        self.modify_rt = MISC.f_coerce(self.modify_rt, 0)   
        self.modify_rb = MISC.f_coerce(self.modify_rb, 0)
        
        self.rounding  = MISC.f_coerce(self.rounding,  0)
        self.points    = MISC.f_coerce(self.points,    4)

    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
    
    def parameters_from_shape_impl(self):
        pass
    
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())
    
    def corner_modifier(self, x, y, d, deg1, deg2):
    
        if d > 0:
            unit = self.layout.dbu
            counter = pya.DPoint(x, y) + {
                0   : pya.DVector( d, d),
                90  : pya.DVector(-d, d),
                180 : pya.DVector(-d,-d),
                270 : pya.DVector( d,-d),
            }[deg1]
            
            if self.modify_option == 0:
                dpoints = STL.arc(x, y, d, deg1 = deg1, deg2 = deg2, p = self.points, center_pt = False)
                dpoints.append(counter)

            else:
                dpoints = STL.triangle( counter.x, counter.y, d, d, deg1 = (deg1 + 180), deg2 = (deg2 + 180) )
            return pya.DPolygon(dpoints)
        return None

    def modify_all(self, poly):
        unit           = self.layout.dbu
        self.modify_rt = min ([self.modify_rt, self.size_w/2, self.size_h/2])
        self.modify_lt = min ([self.modify_lt, self.size_w/2, self.size_h/2])
        self.modify_lb = min ([self.modify_lb, self.size_w/2, self.size_h/2])
        self.modify_rb = min ([self.modify_rb, self.size_w/2, self.size_h/2])
        
        offset_xyd     = lambda d, sign_x, sign_y : (sign_x * (self.size_w / 2 - d), sign_y * (self.size_h / 2 - d), d)
        
        modifers = [ m.to_itype(unit) for m in [
            self.corner_modifier( * offset_xyd(self.modify_rt,  1,  1),  0,   90),
            self.corner_modifier( * offset_xyd(self.modify_lt, -1,  1),  90, 180),
            self.corner_modifier( * offset_xyd(self.modify_lb, -1, -1), 180, 270),
            self.corner_modifier( * offset_xyd(self.modify_rb,  1, -1), 270, 360),
        ] if m ]
               
        if modifers:
            box_r    = pya.Region(poly.to_itype(unit))
            mpoly_r  = pya.Region(modifers)
            result_r = (box_r - mpoly_r)
            ipoly    = list(result_r.each_merged())[0]
            poly     = ipoly.to_dtype(unit)
        return poly

    def moveCenter(self, poly):
        x, y = self.size_w/2, self.size_h/2
        
        move = {
            0 : pya.DVector(  x, -y), # "Left Top"     
            1 : pya.DVector(  x,  0), # "Left Center"  
            2 : pya.DVector(  x,  y), # "Left Bottom"  
            
            3 : pya.DVector(  0, -y), # "Middle Top"   
            4 : pya.DVector(  0,  0), # "Middle Center"
            5 : pya.DVector(  0,  y), # "Middle Bottom"
            
            6 : pya.DVector( -x, -y), # "Right Top"    
            7 : pya.DVector( -x,  0), # "Right Center" 
            8 : pya.DVector( -x,  y), # "Right Bottom" 
        }[self.center_option]
        
        
        return poly.transformed(pya.DTrans(move))
        
    def produce_impl(self):  
        poly = pya.DPolygon(pya.DBox(self.size_w, self.size_h)) 
        poly = self.modify_all(poly)
        poly = self.moveCenter(poly)
        
        if self.rounding:
            poly = poly.round_corners(self.rounding, self.rounding, self.points)
            
        obj = MISC.bias(poly, self.bias, self.layout.dbu)
            
        self.cell.shapes(self.main_layer).insert(obj)
            
            
            
            
            
            
            