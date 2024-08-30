import pya
from Lib_STL        import STL
from Lib_MISC       import MISC

class RECTRING(pya.PCellDeclarationHelper):
    def __init__(self):
        super().__init__()
        self.geometry_option_dict  = {
            "By Inner Geometry" : 0, 
            "By Center Line"    : 1, 
            "By Outer Geometry" : 2,
        }
        
        self.modify_option_dict  = {
            "Corner Rounding" : 0, 
            "Corner Chamfer"  : 1, 
        }
        
        self.param("name",         self.TypeString,  "Name",                               default =   "")
        self.param("main",         self.TypeLayer,   "Layer",                              default = pya.LayerInfo(1, 0))
        
        self.g_option = self.param("geometry_option", self.TypeString,  "Geometry Options",      default = 2)
        self.m_option = self.param("modify_option",   self.TypeString,  "Corner Modify Options", default = 1)
        
        self.param("size_w",       self.TypeDouble,  "Width",               unit =  "um",   default =  5)
        self.param("size_h",       self.TypeDouble,  "Height",              unit =  "um",   default = 10)
                
        self.param( "line_t",      self.TypeDouble,  "Top Width" ,          unit =  "um",   default =  2)
        self.param( "line_b",      self.TypeDouble,  "Bottom Width",        unit =  "um",   default =  2)
        self.param( "line_l",      self.TypeDouble,  "Left Width",          unit =  "um",   default =  2)
        self.param( "line_r",      self.TypeDouble,  "Right Width",         unit =  "um",   default =  2)

        self.param("modify_in",    self.TypeDouble,  "Corner Modify (IN)",  unit =  "um",   default =  0)
        self.param("modify_out",   self.TypeDouble,  "Corner Modify (OUT)", unit =  "um",   default =  0)

        self.param("rounding",     self.TypeDouble,  "Global Rounding",     unit =  "um",   default =  0)
        self.param("points",       self.TypeInt,     "Round Points",        unit = "pts",   default = 32)
        self.param("bias",         self.TypeDouble,  "Shape Bias",          unit = "um",    default =  0)
        _ = [ self.g_option.add_choice(k,v) for k, v in self.geometry_option_dict.items()]
        _ = [ self.m_option.add_choice(k,v) for k, v in self.modify_option_dict.items()]

    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = self.name
        param_name  = f"({self.size_w},{self.size_h})"
        
        return "_".join([ n for n in [custom_name, class_name, param_name] if n ])
    
        
    def coerce_parameters_impl(self):         
        self.size_w     = MISC.f_coerce(self.size_w,     0)   
        self.size_h     = MISC.f_coerce(self.size_h,     0)   
        
        self.line_t     = MISC.f_coerce(self.line_t,     0)   
        self.line_b     = MISC.f_coerce(self.line_b,     0)   
        self.line_l     = MISC.f_coerce(self.line_l,     0)   
        self.line_r     = MISC.f_coerce(self.line_r,     0)   

        self.modify_in  = MISC.f_coerce(self.modify_in,  0)   
        self.modify_out = MISC.f_coerce(self.modify_out, 0)   

        self.rounding   = MISC.f_coerce(self.rounding,   0)   
        self.points     = MISC.f_coerce(self.points,     4) 

    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
    
    def parameters_from_shape_impl(self):
        pass
    
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())

    def gen_box(self):
        in_box  = None
        out_box = None
        hw, hh  = self.size_w/2, self.size_h/2

        #by inside
        if (self.geometry_option == 0) : 
            in_p1  = pya.DPoint( -hw, -hh) 
            in_p2  = pya.DPoint(  hw,  hh)
            out_p1 = in_p1 + pya.DVector( - self.line_l, - self.line_b)
            out_p2 = in_p2 + pya.DVector(   self.line_r,   self.line_t)
            in_box  = pya.DBox(in_p1,  in_p2)
            out_box = pya.DBox(out_p1, out_p2)
         
        #by center
        if (self.geometry_option == 1) : 
            if (self.line_l/2 + self.line_r/2) >= self.size_w:
                self.line_l = self.size_w
                self.line_r = self.size_w
                
            if (self.line_t/2 + self.line_b/2) >= self.size_h:
                self.line_t = self.size_h
                self.line_b = self.size_h
                
            cl_p1   = pya.DPoint( -hw, -hh) 
            cl_p2   = pya.DPoint(  hw,  hh)
            out_p1  = cl_p1 + pya.DVector( - self.line_l/2, - self.line_b/2)
            out_p2  = cl_p2 + pya.DVector(   self.line_r/2,   self.line_t/2)
            in_p1   = cl_p1 + pya.DVector(   self.line_l/2,   self.line_b/2)
            in_p2   = cl_p2 + pya.DVector( - self.line_r/2, - self.line_t/2)
            
            in_box  = pya.DBox(in_p1,  in_p2)
            out_box = pya.DBox(out_p1, out_p2)
            
        #by outside
        if (self.geometry_option == 2) : 
            if (self.line_l + self.line_r) >= self.size_w:
                self.line_l = self.size_w/2
                self.line_r = self.size_w/2
                
            if (self.line_t + self.line_b) >= self.size_h:
                self.line_t = self.size_h/2
                self.line_b = self.size_h/2
                
            out_p1  = pya.DPoint( -hw, -hh) 
            out_p2  = pya.DPoint(  hw,  hh)
            in_p1   = out_p1 + pya.DVector(   self.line_l,   self.line_b)
            in_p2   = out_p2 + pya.DVector( - self.line_r, - self.line_t)
            
            in_box  = pya.DBox(in_p1,  in_p2)
            out_box = pya.DBox(out_p1, out_p2)
            
        return in_box, out_box
    
    def box_modifier(self, box, modify):
        
        if 0 in [box.width(), box.height()]:
            return pya.DPolygon()
            
        x, y = box.center().x, box.center().y
        box_param = [
            self.name, self.main, 
            4, self.modify_option, 
            box.width(), box.height(),
            modify, modify, modify, modify, 
            0, self.points
        ]

        box_pcell  = STL.pcell(self.layout, "SHAPE", "RECT", 0, 0, 0, box_param, pya.Vector(0, 0), pya.Vector(0, 0), 0, 0)
        pcell_poly = MISC.pcell_to_poly(self.layout, box_pcell)        
        poly       = pcell_poly.transformed(pya.DTrans(x, y))
        return poly
        
    def ring_modifier(self):
        unit = self.layout.dbu
        in_box, out_box =  self.gen_box()
        margin_l = out_box.left   - in_box.left
        margin_t = out_box.top    - in_box.top
        margin_r = out_box.right  - in_box.right
        margin_b = out_box.bottom - in_box.bottom
        '''       
        self.modify_out = min([
            min([margin_l, margin_t]),
            min([margin_l, margin_b]),
            min([margin_r, margin_t]),
            min([margin_r, margin_b]),
            self.modify_out,
        ])
        '''
        poly_in  = self.box_modifier( in_box,  self.modify_in)
        poly_out = self.box_modifier(out_box, self.modify_out)        
        ring_reg = pya.Region(poly_out.to_itype(unit)) - pya.Region(poly_in.to_itype(unit))
        
        if self.rounding:
            ring_reg.round_corners(self.rounding/unit, self.rounding/unit, self.points)
        
        return ring_reg
        
    def produce_impl(self):
        unit     = self.layout.dbu
        ring_reg = self.ring_modifier()
        obj      = MISC.bias(ring_reg, self.bias, self.layout.dbu)
        self.cell.shapes(self.main_layer).insert(obj)

        
