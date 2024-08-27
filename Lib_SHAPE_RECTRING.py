import pya

from Lib_STL        import STL

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

        _ = [ self.g_option.add_choice(k,v) for k, v in self.geometry_option_dict.items()]
        _ = [ self.m_option.add_choice(k,v) for k, v in self.modify_option_dict.items()]

    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = self.name
        param_name  = f"({self.size_w},{self.size_h})"
        
        return "_".join([ n for n in [custom_name, class_name, param_name] if n ])
    
        
    def coerce_parameters_impl(self):         
        self.size_w     = 0 if self.size_w     <= 0 else self.size_w     
        self.size_h     = 0 if self.size_h     <= 0 else self.size_h
        
        self.line_t     = 0 if self.line_t     <= 0 else self.line_t
        self.line_b     = 0 if self.line_b     <= 0 else self.line_b
        self.line_l     = 0 if self.line_l     <= 0 else self.line_l
        self.line_r     = 0 if self.line_r     <= 0 else self.line_r

        self.modify_in  = 0 if self.modify_in  <= 0 else self.modify_in
        self.modify_out = 0 if self.modify_out <= 0 else self.modify_out

        self.rounding   = 0 if self.rounding   <= 0 else self.rounding
        self.points    =  4 if self.points     <= 4 else self.points 

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
        x, y = box.center().x, box.center().y
        box_param = [
            self.name, self.main, 
            4, self.modify_option, 
            box.width(), box.height(),
            modify, modify, modify, modify, 
            0, self.points
        ]
        
        box_pcell = STL.pcell(self.layout, "SHAPE", "RECT", x, y, 0, box_param, pya.Vector(0, 0), pya.Vector(0, 0), 0, 0)
        inst      = self.cell.insert(box_pcell)
        shape     = list(self.cell.flatten(True).each_shape(0))[0]
        poly      = shape.polygon
        print("BBOX IN", x, y)
        print("BBOX POLY", poly.bbox().center())
        print("----")
        self.cell.clear(0)
        return poly
        
    def ring_modifier(self):
        in_box, out_box =  self.gen_box()
        poly_in  = self.box_modifier( in_box,  self.modify_in)
        poly_out = self.box_modifier(out_box, self.modify_out)
        ring_reg = pya.Region(poly_out) - pya.Region(poly_in)
        return list(ring_reg.each_merged())[0]
        
    def produce_impl(self):
        poly = self.ring_modifier()
        self.cell.shapes(self.main_layer).insert(poly)

        
