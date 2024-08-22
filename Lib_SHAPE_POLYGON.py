import pya

from Lib_STL        import STL

class POLYGON(pya.PCellDeclarationHelper):
    def __init__(self):
        super().__init__()
        self.dimension_option_dict  = {
            "By Radius Length" : 0, 
            "By Side Length"   : 1, 
            "By Shape Width"   : 2,
        }
        
        self.normal_option_dict  = {
            "Top"    : 0, 
            "Bottom" : 1, 
            "Left"   : 2,
            "Right"  : 3,
        }
        
        self.param("name",         self.TypeString,  "Name",                               default =   "")
        self.param("main",         self.TypeLayer,   "Layer",                              default = pya.LayerInfo(1, 0))
        
        self.d_option = self.param("dimension_option", self.TypeString,  "Dimension Options",    default = 1)
        self.n_option = self.param("normal_option",    self.TypeString,  "Shape normal Options", default = 1)
        
        self.param("sides",        self.TypeInt,     "Polygon sides",      unit = "side",  default =    5)
        self.param("size",         self.TypeDouble,  "Size",               unit =  "um",   default =   10)
        self.param("start_a",      self.TypeDouble,  "Rotate Angle",       unit = "deg",   default =    0)
        
        self.param("rounding",     self.TypeDouble,  "Rounding",           unit =  "um",   default =    0)
        self.param("points",       self.TypeInt,     "Round Points",       unit = "pts",   default =   32)

        _ = [ self.d_option.add_choice(k,v) for k, v in self.dimension_option_dict.items()]
        _ = [ self.n_option.add_choice(k,v) for k, v in self.normal_option_dict.items()]

    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = self.name
        param_name  = f"({self.sides},{self.size})"
        
        return "_".join([ n for n in [custom_name, class_name, param_name] if n ])
    
        
    def coerce_parameters_impl(self):         
        self.sides    = 3 if self.sides    <= 3 else self.sides     
        self.size     = 0 if self.size     <= 0 else self.size
        self.rounding = 0 if self.rounding <= 0 else self.rounding
        self.points   = 4 if self.points   <= 4 else self.points  


    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
    
    def parameters_from_shape_impl(self):
        pass
    
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self): 
        radius = self.size / {
            0: 1,
            1: ( STL.sin(360/self.sides/2) * 2),
            2: ( 1 + STL.cos(360/self.sides/2)) if self.sides%2 ==1 else self.size /STL.cos(360/self.sides/2)/2,
        }[self.dimension_option]
        
        offset = (0.5 * 360 / self.sides) + 90 * {
            0: 1, #Top
            1: 3, #Bottom
            2: 2, #Left
            3: 0, #Right
        }[self.normal_option]
    
        dpoints = STL.circle(0, 0, radius, p = self.sides, deg1 = offset)   
        poly    = pya.DPolygon(dpoints + [dpoints[0]])
        
        if self.rounding > 0:
            poly = poly.round_corners(self.rounding, self.rounding, self.points)
            
        self.cell.shapes(self.main_layer).insert(poly)
