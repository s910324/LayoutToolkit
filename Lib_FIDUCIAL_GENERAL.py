import pya
from Lib_STL        import STL
from Lib_MISC       import MISC

class GENERAL(pya.PCellDeclarationHelper):
    def __init__(self):
        super().__init__()       
        self.type_option_dict = {
            "F-MARK"     :  self.f_mark         ,
            "I-MARK"     :  self.i_mark         ,
            "L-MARK"     :  self.l_mark         ,
            "T-MARK"     :  self.t_mark         ,
            "X-MARK"     :  self.x_mark         ,

            "BOX"        :  self.box_mark       ,
            "CROSS-BOX1" :  self.cross_box_mark1,
            "CROSS-BOX2" :  self.cross_box_mark2,
            "CROSS-BOX3" :  self.cross_box_mark3,
            "BOX-CROSS1" :  self.box_cross_mark1,
            "BOX-CROSS2" :  self.box_cross_mark2,
            "DOVETAIL"   :  self.dovetail       ,
        }
          
        self.param("name",         self.TypeString,  "Name",                               default =    "")
        self.param("main",         self.TypeLayer,   "Pattern Layer",                      default = pya.LayerInfo(1, 0))
        self.param("base",         self.TypeLayer,   "Base Layer",                         default = pya.LayerInfo(1, 0))

        self.t_option = self.param("type_option",    self.TypeString, "Type Options",  default = 0)
        
        self.param("size_p",       self.TypeDouble,  "Pattern Size",       unit =  "um",   default =    10)
        self.param("line_w",       self.TypeDouble,  "Line Width",         unit =  "um",   default =     1)
        self.param("base_w",       self.TypeDouble,  "Base Width",         unit =  "um",   default =    15)
        self.param("base_h",       self.TypeDouble,  "Base Height",        unit =  "um",   default =    15)
        
        self.param("rounding",     self.TypeDouble,  "Rounding",           unit =  "um",   default =     0)
        self.param("points",       self.TypeInt,     "Round Points",       unit = "pts",   default =    64)
        self.param("bias",         self.TypeDouble,  "Shape Bias",         unit =  "um",   default =     0)
        self.param("invert",       self.TypeBoolean, "Pattern invert",                     default = False)
        
        _ = [ self.t_option.add_choice(k,i) for i, k in enumerate(self.type_option_dict.keys())]
        
        
    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = self.name
        param_name  = f"({round(self.size_p, 6)},{round(self.line_w, 6)})"
        
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
        
    def i_mark(self):
        return pya.DPolygon(STL.ipoints(0, 0, self.size_p, self.line_w)) 
        
    def l_mark(self):
        return pya.DPolygon(STL.lpoints(0, 0, self.size_p, self.line_w)) 
        
    def t_mark(self):
        return pya.DPolygon(STL.tpoints(0, 0, self.size_p, self.line_w)) 
        
    def x_mark(self):
        return pya.DPolygon(STL.cross(  0, 0, self.size_p, self.size_p, self.line_w)) 
        
    def f_mark(self):
        return pya.DPolygon(STL.fpoints(0, 0, self.size_p, self.line_w)) 
        
    def box_mark(self):
        return pya.DPolygon(STL.box_ring(0, 0, self.size_p, self.line_w)) 
    
    def dovetail(self):
        return pya.DPolygon(STL.dovetail_points (0, 0, self.size_p, self.line_w)) 
        
    def cross_box_mark1(self):
        cross_size = self.size_p - (self.line_w * 2)
        return pya.Region([
            pya.DPolygon(STL.box_ring(0, 0, self.size_p, self.line_w)).to_itype(self.layout.dbu),
            pya.DPolygon(STL.cross(   0, 0,  cross_size, cross_size, self.line_w)).to_itype(self.layout.dbu)
        ])
        
    def cross_box_mark2(self):
        cross_size = self.size_p - (self.line_w * 4)
        return pya.Region([
            pya.DPolygon(STL.box_ring(0, 0, self.size_p, self.line_w)).to_itype(self.layout.dbu),
            pya.DPolygon(STL.cross(   0, 0,  cross_size, cross_size, self.line_w)).to_itype(self.layout.dbu)
        ]) 
        
    def cross_box_mark3(self):
        offset = -((self.size_p-self.line_w) / 2) 
        
        return pya.Region([
            pya.DPolygon(STL.rect( offset, offset, self.line_w, self.line_w)).to_itype(self.layout.dbu),
            pya.DPolygon(STL.cross( 0, 0, self.size_p, self.size_p, self.line_w)).to_itype(self.layout.dbu)
        ]) 

    def box_cross_mark1(self):
        offset = -((self.size_p-self.line_w) / 2) 
        
        x0 = - self.size_p/2
        x1 = x0 + self.line_w
        y0 = x0
        y1 = x1
        
        return pya.Region([pya.DPolygon(b).to_itype(self.layout.dbu) for b in [
            pya.DBox( x0,  y0,  x1,  y1), pya.DBox(-x0, -y0, -x1, -y1), 
            pya.DBox( x0, -y0,  x1, -y1), pya.DBox(-x0,  y0, -x1,  y1)
        ]])
        
    def box_cross_mark2(self):
        offset = -((self.size_p-self.line_w) / 2) 
        
        x0 = - self.size_p/2
        x1 = x0 + self.line_w
        x2 = -self.line_w/2
        x3 =  self.line_w/2
        x4 =  self.size_p/2 - self.line_w
        x5 =  self.size_p/2
        y0, y1, y2 ,y3, y4, y5 = x0, x1, x2, x3, x4, x5


        
        return pya.Region([pya.DPolygon(b).to_itype(self.layout.dbu) for b in [
            pya.DBox( x0, y2, x1, y3), pya.DBox(x2, y2, x3, y3), pya.DBox(x4, y2, x5, y3), 
            pya.DBox( x2, y0, x3, y1), pya.DBox(x2, y4, x3, y5), 
        ]])
        
    def produce_impl(self):  
        key  = list(self.type_option_dict.keys())[self.type_option]
        poly = self.type_option_dict[key]()
        base = pya.DPolygon(STL.rect(0, 0, self.base_w, self.base_h))
        obj  = MISC.invert(poly, base, flag = self.invert, unit = self.layout.dbu)
        obj  = MISC.rounded (obj, self.rounding, self.rounding, self.points, unit = self.layout.dbu)
        obj  = MISC.bias(obj, self.bias, unit = self.layout.dbu)
        self.cell.shapes(self.main_layer).insert(obj)
        self.cell.shapes(self.base_layer).insert(base)
            