import pya

from Lib_STL        import STL

class ARC(pya.PCellDeclarationHelper):
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
        self.param("stop_a",       self.TypeDouble,  "Stop Angle",         unit = "deg",  default =   90)
        
        self.param("start_ext",    self.TypeDouble,  "Start End extend",   unit =  "um",  default =    0)
        self.param("stop_ext",     self.TypeDouble,  "Stop End extend",    unit =  "um",  default =    0)
        
        self.param("arc_points",   self.TypeInt,     "Arc Points",         unit = "pts",  default =   32)
        self.param("rounding",     self.TypeDouble,  "Rounding",           unit =  "um",  default =    0)
        self.param("points",       self.TypeInt,     "Round Points",       unit = "pts",  default =   32)
        

        _ = [ self.d_option.add_choice(k,v) for k, v in self.dimension_option_dict.items()]
        _ = [ self.g_option.add_choice(k,v) for k, v in self.geometry_option_dict.items()]

    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = self.name
        param_name  = f"{self.size},{self.line_w},{self.start_a}to{self.stop_a}deg)"
        
        return "_".join([ n for n in [custom_name, class_name, param_name] if n ])
    
        

    def coerce_parameters_impl(self):         
        self.line_w     =           0 if self.line_w     <= 0           else self.line_w     
        self.size       = self.line_w if self.size       <= self.line_w else self.size
        self.start_ext  =           0 if self.start_ext  <= 0           else self.start_ext
        self.stop_ext   =           0 if self.stop_ext   <= 0           else self.stop_ext
        self.rounding   =           0 if self.rounding   <= 0           else self.rounding
        self.arc_points =           4 if self.arc_points <= 4           else self.arc_points  
        self.points     =           4 if self.points     <= 4           else self.points 

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
        
        dpoints_in    = STL.arc(0, 0, r = radius_in,  p = self.arc_points, deg1 = self.start_a, deg2=self.stop_a, center_pt = False)
        dpoints_out   = STL.arc(0, 0, r = radius_out, p = self.arc_points, deg1 = self.start_a, deg2=self.stop_a, center_pt = False)
        
        if self.start_ext > 0 :
            start_vec       = (dpoints_in[0]  - dpoints_out[0]) 
            start_vec_ext   = pya.DVector(-start_vec.y,start_vec.x) / start_vec.length() * self.start_ext
            dpoints_in[0]   = dpoints_in[0]   + start_vec_ext
            dpoints_out[0]  = dpoints_out[0]  + start_vec_ext
 
        if self.stop_ext > 0 :
            stop_vec         = (dpoints_in[-1]  - dpoints_out[-1]) 
            stop_vec_ext     = pya.DVector(stop_vec.y, -stop_vec.x) / stop_vec.length() * self.stop_ext
            dpoints_in[-1]   = dpoints_in[-1]   + stop_vec_ext
            dpoints_out[-1]  = dpoints_out[-1]  + stop_vec_ext
        

        
        
        if (self.rounding > 0):
            self.rounding   = min(self.rounding, self.line_w * 0.5)
            ignor_start_in  = 0
            ignor_stop_in   = 0
            ignor_start_out = 0
            ignor_stop_out  = 0
            
            for i in range(len(dpoints_in)):
                distance = (dpoints_in[i] - dpoints_in[0]).length()
                if distance <= self.rounding:
                    ignor_start_in += 1
                else:
                    break
                    
            for i in range(len(dpoints_in)-1, 0, -1):
                distance = (dpoints_in[i] - dpoints_in[-1]).length()
                if distance <= self.rounding:
                    ignor_stop_in += 1
                else:
                    break
                        
            for i in range(len(dpoints_out)):
                distance = (dpoints_out[i] - dpoints_out[0]).length()
                if distance <= self.rounding:
                    ignor_start_out += 1
                else:
                    break
                    
            for i in range(len(dpoints_out)-1, 0, -1):
                distance = (dpoints_out[i] - dpoints_out[-1]).length()
                if distance <= self.rounding:
                    ignor_stop_out += 1
                else:
                    break
    
            dpoints_in  = [dpoints_in[0]]  + dpoints_in [ignor_start_in  : len(dpoints_in)  - ignor_stop_in ] + [dpoints_in [-1]]
            dpoints_out = [dpoints_out[0]] + dpoints_out[ignor_start_out : len(dpoints_out) - ignor_stop_out] + [dpoints_out[-1]]
            
        dpoints = dpoints_in + dpoints_out[::-1]
        poly    = pya.DPolygon(dpoints)     
        
        
        if (self.rounding > 0):
            poly = poly.round_corners(self.rounding, self.rounding, self.points)
            
        self.cell.shapes(self.main_layer).insert(poly)
        