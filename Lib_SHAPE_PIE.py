import pya

from Lib_STL        import STL

class PIE(pya.PCellDeclarationHelper):
    def __init__(self):
        super().__init__()
        self.dimension_option_dict  = {
            "By Radius"   : 0, 
            "By Diameter" : 1, 
        }
        
        self.center_option_dict  = {
            "Round center : Yes" : 0, 
            "Round center : No"  : 1, 
        }
        self.param("name",         self.TypeString,  "Name",                              default =   "")
        self.param("main",         self.TypeLayer,   "Layer",                             default = pya.LayerInfo(1, 0))
        
        self.d_option = self.param("dimension_option", self.TypeString,  "Dimension Options",  default = 1)
        
        
        self.param("size",         self.TypeDouble,  "Size",               unit =  "um",  default =   10)
        self.param("start_a",      self.TypeDouble,  "Start Angle",        unit = "deg",  default =    0)
        self.param("stop_a",       self.TypeDouble,  "Stop Angle",         unit = "deg",  default =   90)
    
        
        self.param("pie_points",   self.TypeInt,     "Pie Points",         unit = "pts",  default =   32)
        self.param("rounding",     self.TypeDouble,  "Rounding",           unit =  "um",  default =    0)
        self.param("points",       self.TypeInt,     "Round Points",       unit = "pts",  default =   32)
        
        self.r_option = self.param("center_option", self.TypeString,  "Round Center Options",  default = 1)

        _ = [ self.d_option.add_choice(k,v) for k, v in self.dimension_option_dict.items()]
        _ = [ self.r_option.add_choice(k,v) for k, v in self.center_option_dict.items()]

    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = self.name
        param_name  = f"{self.size},{self.start_a}to{self.stop_a}deg)"
        
        return "_".join([ n for n in [custom_name, class_name, param_name] if n ])
    
        

    def coerce_parameters_impl(self):         
        self.size       =           0 if self.size       <= 0           else self.size
        self.rounding   =           0 if self.rounding   <= 0           else self.rounding
        self.pie_points =           4 if self.pie_points <= 4           else self.pie_points  
        self.points     =           4 if self.points     <= 4           else self.points 

    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
    
    def parameters_from_shape_impl(self):
        pass
    
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self): 
        radius        = (self.size * [1, 0.5][self.dimension_option])
        self.stop_a   = (self.start_a + 360) if abs(self.stop_a - self.start_a) > 360 else self.stop_a
        self.rounding = 0 if abs(self.stop_a - self.start_a) in [0, 360] else min(self.rounding, radius * 0.5)
        dpoints       = STL.arc(0, 0, r = radius,  p = self.pie_points, deg1 = self.start_a, deg2=self.stop_a, center_pt = False)

        if (self.rounding > 0):
            ignore  = 0
            for i in range(len(dpoints)):
                distance = (dpoints[i] - dpoints[0]).length()
                if distance <= self.rounding:
                    ignore += 1
                else:
                    break
              
            dpoints  = [dpoints[0]]  + dpoints [ignore  : len(dpoints)  - ignore ] + [dpoints [-1]]

        poly = pya.DPolygon( dpoints+ [pya.DPoint(0, 0)])     
        
        if (self.rounding > 0):
            poly_rnd = poly.round_corners(self.rounding, self.rounding, self.points)

            if self.center_option == 1:
                unit       = self.layout.dbu
                start_vec  = pya.DVector(dpoints[0])
                stop_vec   = pya.DVector(dpoints[-1])
                qdrt       = [start_vec.sprod_sign(stop_vec), start_vec.vprod_sign(stop_vec)]
                sign       = qdrt in [[-1, -1], [0, -1], [1, -1]]
                origin     = pya.DPoint(0, 0)
                
                if sign :
                    patched_p = [ (p if (poly.sized(2 * unit).inside(p)) else origin) for p in poly_rnd.each_point_hull()]
                else : 
                    patched_p = [ (p if (p.sq_abs() > (radius / 2)) else origin)  for p in poly_rnd.each_point_hull()]

                poly_rnd = pya.DPolygon(patched_p)
            poly = poly_rnd
                
        self.cell.shapes(self.main_layer).insert(poly)
        