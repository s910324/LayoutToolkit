import pya
from Lib_STL        import STL
from Lib_MISC       import MISC


class CIRCLE(pya.PCellDeclarationHelper):
    def __init__(self):
        super().__init__()
        self.dimension_option_dict  = {
            "By Radius"   : 0, 
            "By Diameter" : 1, 
        }

        self.param("name",         self.TypeString,  "Name",                               default =   "")
        self.param("main",         self.TypeLayer,   "Layer",                              default = pya.LayerInfo(1, 0))
        
        self.d_option = self.param("dimension_option", self.TypeString,  "Dimension Options",    default = 1)

        self.param("size",         self.TypeDouble,  "Size",               unit =  "um",   default =   10)
        self.param("sides",        self.TypeInt,     "Circle Points",      unit = "pts",   default =   32)
        self.param("bias",         self.TypeDouble,  "Shape Bias",         unit = "um",    default =    0)
        _ = [ self.d_option.add_choice(k,v) for k, v in self.dimension_option_dict.items()]

    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = self.name
        param_name  = f"size={self.size}"
        
        return "_".join([ n for n in [custom_name, class_name, param_name] if n ])
    
        
    def coerce_parameters_impl(self):         
        self.size  = MISC.f_coerce(self.size,  0)
        self.sides = MISC.f_coerce(self.sides, 4)   

    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
    
    def parameters_from_shape_impl(self):
        pass
    
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self): 
        radius = self.size * {
            0: 1.00,
            1: 0.50,
        }[self.dimension_option]
        
        dpoints = STL.circle(0, 0, radius, p = self.sides, deg1 = 0)   
        poly    = pya.DPolygon(dpoints + [dpoints[0]])          
        obj     = MISC.bias(poly, self.bias, self.layout.dbu)
            
        self.cell.shapes(self.main_layer).insert(obj)
