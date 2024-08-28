import pya
from Lib_STL        import STL
from Lib_MISC       import MISC

class ASML_PM(pya.PCellDeclarationHelper):
    def __init__(self):
        super(ASML_PM, self).__init__()
        self.param("name",        self.TypeString,   "Name",                               default =   "")
        self.param("main",        self.TypeLayer,    "Pattern Layer",                      default = pya.LayerInfo(1, 0))
        self.param("clear",       self.TypeLayer,    "Clearout Layer",                     default = pya.LayerInfo(1, 0))
        self.param("size_clr",    self.TypeDouble,   "Clear our size",     unit = "um",    default =  610 ) 
        self.param("invert",      self.TypeBoolean,  "Pattern invert",                     default = False)
        self.param("bias",        self.TypeDouble,   "Shape Bias",         unit = "um",    default =     0)
        
    def display_text_impl(self):
        return "ASML_PM"
        
    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
        
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())
    
    def coerce_parameters_impl(self):
        self.size_clr = MISC.f_coerce(self.size_clr,  610)
  
    def produce_impl(self):
        dx, dy         = -2.5, -2.5
        baseSize       = self.size_clr
        unit           = self.layout.dbu
        regionBase     = pya.Region()
        regionPositive = pya.Region()
        regionNegative = pya.Region()
        
        stripArrays = [
            STL.box_array(  -28.6,  109.0, 8.8,  190, -17.6,     0, 11,  1), #***
            STL.box_array(  109.0,   24.0, 190,  8.0,     0,  16.0,  1, 12), #*** 
            
            STL.box_array( -113.5,  -28.6,  191, 8.8,     0, -17.6,  1, 11), #***
            STL.box_array(   24.0, -113.5,  8.0, 191,  16.0,     0,  12, 1), #***
        ]
        
        for stripArray in stripArrays:
            for strip in stripArray:
                regionPositive.insert(strip.to_itype(unit))
        
        regionBase.insert(pya.DBox(dx-baseSize/2, dy-baseSize/2, dx+baseSize/2, dy+baseSize/2).to_itype(unit))
        regionPositive.insert(pya.DPolygon(STL.cross(0, 0, 100, 100, 10)).to_itype(unit))
        regionNegative.insert(pya.DPolygon(STL.cross(0, 0,   5,   5,  1)).to_itype(unit))
        result = regionPositive - regionNegative
        result = MISC.bias(result, self.bias, self.layout.dbu)
        
        if self.invert: 
            self.cell.shapes(self.main_layer).insert(regionBase - result)
            
        else:
            self.cell.shapes(self.main_layer).insert(result)
            self.cell.shapes(self.clear_layer).insert(regionBase)