import re
import pya
import math
import numpy as np

from Lib_STL        import STL
from Lib_MISC       import MISC
from Lib_Util_Wafer import Util_Wafer

class Chip(pya.PCellDeclarationHelper):
    def __init__(self):
        super().__init__()
        self.param("name",                 self.TypeString,  "Name",                           default = "")
        self.param("chip",                 self.TypeLayer,   "Layer for chip",                 default = pya.LayerInfo(0, 10))
        self.param("scribe",               self.TypeLayer,   "Layer for scribe",               default = pya.LayerInfo(0, 30))
        self.param("chip_w",               self.TypeDouble,  "Chip   width",                   default =   3000,   unit = "um")
        self.param("chip_h",               self.TypeDouble,  "Chip   height",                  default =   2000,   unit = "um")
        self.param("scribe_w",             self.TypeDouble,  "Scribe width",                   default =     80,   unit = "um")
        self.param("scribe_h",             self.TypeDouble,  "Scribe height",                  default =     80,   unit = "um")
        self.scribe_confg_dict  = {"Fully surrounded" : 0, "Half  surrounded" : 1, "L shaped" : 2}
        self.scribe_option = self.param("scribe_config", self.TypeString,  "Scribe config",  default =      0)
        _ = [ self.scribe_option.add_choice(k,v) for k, v in self.scribe_confg_dict.items()]

    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = (self.name + "_" if self.name else "") 
        chip_size   = "_%.2fx%.2f" % (self.chip_w, self.chip_h)

        return "%s%s%s" % (custom_name, class_name, chip_size)

    def coerce_parameters_impl(self):                  
        self.chip_w   = MISC.f_coerce(self.chip_w,  1000)
        self.chip_h   = MISC.f_coerce(self.chip_h,  1000)
        self.scribe_w = MISC.f_coerce(self.scribe_w,   0)
        self.scribe_h = MISC.f_coerce(self.scribe_h,   0)

    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
    
    def parameters_from_shape_impl(self):
        pass
    
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self): 
        unit          = self.layout.dbu
        chip_content  = Util_Wafer.chip_with_scribe(0, 0, unit, self.chip_w, self.chip_h, self.scribe_w, self.scribe_h, self.scribe_config) 
        scribes       = [chip_content.get("scribe_l"), chip_content.get("scribe_r"), chip_content.get("scribe_t"), chip_content.get("scribe_b")]
        self.cell.shapes(self.chip_layer).insert(chip_content.get("chip"))

        for scribe in scribes:
            if scribe:
                self.cell.shapes(self.scribe_layer).insert(scribe)

class Shot(pya.PCellDeclarationHelper):
    '''
        todo 
        hide partial parameters
        partial scribeline
    '''
    def __init__(self):
        super().__init__()
        self.param("name",                 self.TypeString,  "Name",                           default = "")
        self.param("shot",                 self.TypeLayer,   "Layer for shot",                 default = pya.LayerInfo(0, 20))
        
        self.param("chip",                 self.TypeLayer,   "Layer for chip",                 default = pya.LayerInfo(0, 10))
        self.param("teg",                  self.TypeLayer,   "Layer for TEG",                  default = pya.LayerInfo(0, 11))
        self.param("chip_partial",         self.TypeLayer,   "Layer for partial chip",         default = pya.LayerInfo(0, 12))
        self.param("teg_partial",          self.TypeLayer,   "Layer for partial TEG",          default = pya.LayerInfo(0, 13))
        
        self.param("scribe",               self.TypeLayer,   "Layer for scribe",               default = pya.LayerInfo(0, 30))
        self.param("scribe_partial",       self.TypeLayer,   "Layer for partial scribe",       default = pya.LayerInfo(0, 31))
        self.param("direction",            self.TypeLayer,   "Layer for shot direction",       default = pya.LayerInfo(0, 29))
        
        self.param("shot_w",               self.TypeDouble,  "Shot   width",                   default =  18560,   unit = "um")
        self.param("shot_h",               self.TypeDouble,  "Shot   height",                  default =  29200,   unit = "um")
        
        self.param("place_chip",           self.TypeBoolean, "Place  chip",                    default = True)
        self.param("chip_w",               self.TypeDouble,  "Chip   width",                   default =   3000,   unit = "um")
        self.param("chip_h",               self.TypeDouble,  "Chip   height",                  default =   2000,   unit = "um")
        self.param("scribe_w",             self.TypeDouble,  "Scribe width",                   default =     80,   unit = "um")
        self.param("scribe_h",             self.TypeDouble,  "Scribe height",                  default =     80,   unit = "um")
        
        self.scribe_confg_dict  = {"Fully surrounded" : 0, "Half  surrounded" : 1, "L shaped" : 2}
        self.scribe_option = self.param("scribe_config", self.TypeString,  "Scribe config",  default =      0)
        _ = [ self.scribe_option.add_choice(k,v) for k, v in self.scribe_confg_dict.items()]

        self.param("teg_loc",              self.TypeString,  "TEG Location\n - using 'Row, Col;' syntax\n - reference using lower left corner\n",         default = "")
        self.param("skip_loc",             self.TypeString,  "Skip Location\n - using 'Row, Col;' syntax\n - reference using lower left corner\n",        default = "")
        self.param("partial_loc",          self.TypeString,  "Partial Location\n - using 'Row, Col;' syntax\n - reference using lower left corner\n",     default = "")
        
    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = (self.name + "_" if self.name else "") 
        shot_size  = "_%.2fx%.2f" % (self.shot_w, self.shot_h)

        return "%s%s%s" % (custom_name, class_name, shot_size)
    
    def coerce_parameters_impl(self):                  
        self.shot_w   = MISC.f_coerce(self.shot_w,  5000)
        self.shot_h   = MISC.f_coerce(self.shot_h,  5000)
        self.chip_w   = MISC.f_coerce(self.chip_w,  1000)
        self.chip_h   = MISC.f_coerce(self.chip_h,  1000)
        self.scribe_w = MISC.f_coerce(self.scribe_w,   0)
        self.scribe_h = MISC.f_coerce(self.scribe_h,   0)

    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
    
    def parameters_from_shape_impl(self):
        pass
    
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())

    def insert_chip_cell(self, x, y, layer_chip, layer_scribe, name = ""):
        um         = 1/ self.layout.dbu
        chip_param = [
            name, layer_chip, layer_scribe, self.chip_w, self.chip_h, self.scribe_w, self.scribe_h, self.scribe_config
        ]
        chip_pcell = STL.pcell(self.layout, "SEMI", "Chip",  x * um, y * um, 0, chip_param, pya.Vector(0, 0), pya.Vector(0, 0), 0, 0)
        self.cell.insert(chip_pcell)

    def produce_impl(self): 
        unit        = self.layout.dbu
        shot_base   = pya.DPolygon(STL.rect(0, 0, self.shot_w, self.shot_h))

        if self.place_chip :            
            shot_params   = Util_Wafer.shot(0, 0, unit, self.shot_w, self.shot_h, self.chip_w, self.chip_h, self.scribe_w, self.scribe_h, self.scribe_config, self.teg_loc, self.skip_loc, self.partial_loc)
            row           = shot_params.get("row")
            column        = shot_params.get("column")
            teg_count     = shot_params.get("teg_count")
            chip_count    = shot_params.get("chip_count")
            placement     = shot_params.get("placement")

            for k in placement:
                attri      = placement[k].get("attri")
                chip_name  = placement[k].get("name")
                chip_rect  = placement[k].get("chip")
                scribes    = [s for s in placement[k].get("scribe") if s]
                chip_layer = {
                    -2 : self.teg_partial,
                    -1 : self.chip_partial,
                     0 : self.shot,
                     1 : self.chip,
                     2 : self.teg,
                }[attri]
                
                scribe_layer = {
                    False : self.scribe_partial,
                    True  : self.scribe,
                }[attri > 0 ]

                if chip_rect:
                    self.insert_chip_cell(chip_rect.bbox().center().x, chip_rect.bbox().center().y, chip_layer, scribe_layer, name = chip_name)
            
        fsize  = min([self.shot_w, self.shot_h])/2
        fwidth = fsize * 0.1
        fmark  = pya.DPolygon(STL.fpoints(0, 0, fsize, fwidth))
        
        self.cell.shapes(self.direction_layer).insert(fmark)
        self.cell.shapes(self.shot_layer).insert(shot_base)
        
class Wafer(pya.PCellDeclarationHelper):
    def __init__(self):
        super().__init__() 
        self.param("name",                 self.TypeString,  "Name",                           default = "")
        wafer_size_option  = self.param( "wafer_size_option",  self.TypeString,  "Wafer Size", default=3)
        self.param("edge_exclude",         self.TypeDouble,  "Edge exclusion",                 default = 3.0,      unit = "mm")  
        self.param("gulde",                self.TypeLayer,   "Layer for guide line",           default = pya.LayerInfo(0,  1))
        self.param("wafer",                self.TypeLayer,   "Layer for wafer",                default = pya.LayerInfo(0,  2))
        self.param("ebr",                  self.TypeLayer,   "Layer for EBR",                  default = pya.LayerInfo(0,  3))
        self.param("wafer_center",         self.TypeLayer,   "Layer for wafer center",         default = pya.LayerInfo(0,  8))
        self.param("wafer_direction",      self.TypeLayer,   "Layer for wafer direction",      default = pya.LayerInfo(0,  9))  
        
        self.wafer_size_dict = {2 : 0, 4 : 1, 6 : 2, 8 : 3, 12 : 4}
        _ = [ wafer_size_option.add_choice(f"{k}-inch",v) for k, v in self.wafer_size_dict.items()]
        
        self.param("circle_dots",          self.TypeInt,     "Points per circle",              default = 128)    
        #self.active_reg = None
    
    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = (self.name + "_" if self.name else "")
        wafer_inch  = list(self.wafer_size_dict.keys())[list(self.wafer_size_dict.values()).index( self.wafer_size_option)]
        wafer_size  = "_%d_inch" % (wafer_inch)

        return "%s%s%s" % (custom_name, class_name, wafer_size,)
    
    def coerce_parameters_impl(self):  
        self.edge_exclude = MISC.f_coerce(self.edge_exclude,  0)
        self.circle_dots  = MISC.f_coerce(self.circle_dots,  32)

    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
    
    def parameters_from_shape_impl(self):
        pass
    
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())
    
    def produce_impl(self): 
        unit         = self.layout.dbu
        inch         = list(self.wafer_size_dict.keys())[list(self.wafer_size_dict.values()).index( self.wafer_size_option)]
        wafer_params = Util_Wafer.wafer(0, 0, inch, unit, self.edge_exclude, p = self.circle_dots)

        self.cell.shapes(self.gulde_layer).insert(wafer_params.get("guide"))
        self.cell.shapes(self.wafer_layer).insert(wafer_params.get("wafer"))
        self.cell.shapes(self.ebr_layer  ).insert(wafer_params.get("ebr"))
        self.cell.shapes(self.wafer_center_layer).insert(pya.DPolygon(STL.cross(0, 0, 6000, 6000, 20)))
        self.cell.shapes(self.wafer_direction_layer).insert(pya.DPolygon(STL.fpoints(0, 0, inch * 10000, inch * 1000)))
        
        
        
class WaferMap(pya.PCellDeclarationHelper):
    '''
        todo 
        partial scribeline
    ''' 
    def __init__(self):
        super().__init__() 
        self.param("name",                 self.TypeString,  "Name",                           default = "")
        
        wafer_size_option  = self.param( "wafer_size_option",  self.TypeString,  "Wafer Size", default=3)
        self.wafer_size_dict = {2 : 0, 4 : 1, 6 : 2, 8 : 3, 12 : 4}
        _ = [ wafer_size_option.add_choice(f"{k}-inch",v) for k, v in self.wafer_size_dict.items()]
        
        wafer_rot_option  = self.param( "wafer_rot_option",  self.TypeString,  "Wafer Rotation", default=0)
        self.wafer_rot_dict = {"Down" : 0, "Left" : 1, "Right" : 2, "Top" : 3}
        _ = [ wafer_rot_option.add_choice(f"Flat/Notch {k}",v) for k, v in self.wafer_rot_dict.items()]
        
        self.param("edge_exclude",         self.TypeDouble,  "Edge exclusion",                 default = 3.0,      unit = "mm")   
        
        self.param("gulde",                self.TypeLayer,   "Layer for guide line",           default = pya.LayerInfo(0,  1))
        self.param("wafer",                self.TypeLayer,   "Layer for wafer",                default = pya.LayerInfo(0,  2))
        self.param("ebr",                  self.TypeLayer,   "Layer for EBR",                  default = pya.LayerInfo(0,  3))
        self.param("wafer_center",         self.TypeLayer,   "Layer for wafer center",         default = pya.LayerInfo(0,  8))
        self.param("wafer_direction",      self.TypeLayer,   "Layer for wafer direction",      default = pya.LayerInfo(0,  9))
        
        self.param("shot_full",            self.TypeLayer,   "Layer for shot (full)",          default = pya.LayerInfo(0, 20))
        self.param("shot_partial",         self.TypeLayer,   "Layer for shot (partial)",       default = pya.LayerInfo(0, 21))
        
        self.param("chip",                 self.TypeLayer,   "Layer for chip",                 default = pya.LayerInfo(0, 10))
        self.param("teg",                  self.TypeLayer,   "Layer for TEG",                  default = pya.LayerInfo(0, 11))
        self.param("chip_partial",         self.TypeLayer,   "Layer for partial chip",         default = pya.LayerInfo(0, 12))
        self.param("teg_partial",          self.TypeLayer,   "Layer for partial TEG",          default = pya.LayerInfo(0, 13))
        
        
        self.param("scribe",               self.TypeLayer,   "Layer for shot scribe",          default = pya.LayerInfo(0, 30))
        self.param("scribe_partial",       self.TypeLayer,   "Layer for partial scribe",       default = pya.LayerInfo(0, 31))
        self.param("shot_direction",       self.TypeLayer,   "Layer for shot direction",       default = pya.LayerInfo(0, 29))
        self.param("central_shot",         self.TypeLayer,   "Layer for central shot",         default = pya.LayerInfo(0,  7))

        self.param("place_shot",           self.TypeBoolean, "Place shot",                     default = True)
        self.param("skip_partial_shot",    self.TypeBoolean, "Skip partial shots",             default = False)
        self.param("skip_partial_chip",    self.TypeBoolean, "Skip partial chips",             default = True)
        
        self.param("shot_offset_x",        self.TypeDouble,  "Shot offset X",                  default =      0,   unit = "um")
        self.param("shot_offset_y",        self.TypeDouble,  "Shot offset Y",                  default =      0,   unit = "um")
        
        self.param("shot_w",               self.TypeDouble,  "Shot width",                     default =  18560,   unit = "um")
        self.param("shot_h",               self.TypeDouble,  "Shot height",                    default =  29200,   unit = "um")
        
        self.param("shot_step_x",          self.TypeDouble,  "Shot stepping X",                default =  18480,   unit = "um")
        self.param("shot_step_y",          self.TypeDouble,  "Shot stepping Y",                default =  29120,   unit = "um")     
        
        self.param("place_chip",           self.TypeBoolean, "Place chip",                     default = False)
        self.param("chip_w",               self.TypeDouble,  "Chip   width",                   default = 3000,     unit = "um")   
        self.param("chip_h",               self.TypeDouble,  "Chip   height",                  default = 2000,     unit = "um")
        self.param("scribe_w",             self.TypeDouble,  "Scribe width",                   default =   80,     unit = "um")
        self.param("scribe_h",             self.TypeDouble,  "Scribe height",                  default =   80,     unit = "um")      

        
        self.scribe_confg_dict  = {"Fully surrounded" : 0, "Half  surrounded" : 1, "L shaped" : 2}
        self.scribe_option = self.param("scribe_config", self.TypeString,  "Scribe config",      default =      0)
        _ = [ self.scribe_option.add_choice(k,v) for k, v in self.scribe_confg_dict.items()]
        
        self.param("teg_loc",              self.TypeString,  "TEG Location\n - using 'Row, Col;' syntax\n - reference using Lower left chip\n",       default = "")
        self.param("skip_shot_loc",        self.TypeString,  "Skip shot Location\n - using 'Row, Col;' syntax\n - reference using center shot\n",     default = "")
        self.param("skip_chip_cnt",        self.TypeInt,     "Skip if shot Gross die less than", default = 1, unit = "e.a.")
        self.param("skip_teg_cnt",         self.TypeInt,     "Skip if shot TEG   die less than", default = 1, unit = "e.a.")
        self.param("circle_dots",          self.TypeInt,     "Points per circle",                default = 128) 
        
    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = (self.name + "_" if self.name else "")
        wafer_inch  = list(self.wafer_size_dict.keys())[list(self.wafer_size_dict.values()).index( self.wafer_size_option)]
        wafer_size  = "_%d_inch" % (wafer_inch)

        return "%s%s%s" % (custom_name, class_name, wafer_size,)
    
    def coerce_parameters_impl(self):  
        self.shot_step_x        = MISC.f_coerce(self.shot_step_x,  5000)
        self.shot_step_y        = MISC.f_coerce(self.shot_step_y,  5000)
        self.shot_w             = MISC.f_coerce(self.shot_w,       5000)
        self.shot_h             = MISC.f_coerce(self.shot_h,       5000)
        self.chip_w             = MISC.f_coerce(self.chip_w,       1000)
        self.chip_h             = MISC.f_coerce(self.chip_h,       1000)
        self.scribe_w           = MISC.f_coerce(self.scribe_w,        0)
        self.scribe_h           = MISC.f_coerce(self.scribe_h,        0)
        self.skip_chip_cnt      = MISC.f_coerce(self.skip_chip_cnt,   0)
        self.skip_teg_cnt       = MISC.f_coerce(self.skip_teg_cnt,    0)
        self.inch               = list(self.wafer_size_dict.keys())[list(self.wafer_size_dict.values()).index( self.wafer_size_option)]
        self.flat_notch_dir     = list(self.wafer_rot_dict.keys())[list(self.wafer_rot_dict.values()).index( self.wafer_rot_option)]
        self.wafer_diameter     = Util_Wafer.waferDimension(self.inch)["diameter"]
        self.flat_notch         = ("Notch" if self.inch >= 8 else "Flat") + " " + self.flat_notch_dir
        self.wafer_radius       = self.wafer_diameter/2
        self.chip_count         = 0
        self.teg_count          = 0
        self.partial_shot_count = 0
        self.full_shot_count    = 0
        self.wafer_rot_angle   = {
            0 :  0,  #"Down"
            1 : -90, #"Left"
            2 :  90, #"Right"
            3 : 180, #"TOP"
        }[self.wafer_rot_option]

    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
    
    def parameters_from_shape_impl(self):
        pass
    
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())
        
    def insert_wafer_cell(self):
        wafer_param = [
            self.name, self.wafer_size_option, self.edge_exclude, self.gulde, self.wafer, self.ebr, 
            self.wafer_center, self.wafer_direction,  self.circle_dots
        ]
        
        wafer_pcell = STL.pcell(self.layout, "SEMI", "Wafer", 0, 0, self.wafer_rot_angle, wafer_param, pya.Vector(0, 0), pya.Vector(0, 0), 0, 0)
        self.cell.insert(wafer_pcell)
        
    def insert_shot_cell(self, x, y, layer_shot, skip_loc, partial_loc):
        um         = 1/ self.layout.dbu
        shot_param = [
            "", layer_shot, self.chip, self.teg, self.chip_partial, self.teg_partial, self.scribe, self.scribe_partial, self.shot_direction, 
            self.shot_w, self.shot_h, self.place_chip, self.chip_w, self.chip_h, self.scribe_w, self.scribe_h, self.scribe_config, self.teg_loc, skip_loc, partial_loc
        ]
        shot_pcell = STL.pcell(self.layout, "SEMI", "Shot",  x * um, y * um, 0, shot_param, pya.Vector(0, 0), pya.Vector(0, 0), 0, 0)
        self.cell.insert(shot_pcell)

    def insert_misc(self):
        cross_size  = 6000
        cross_width = 20
        central_shot_cross = pya.DPolygon(STL.cross(self.shot_offset_x, self.shot_offset_y, cross_size, cross_size, cross_width))
        central_shot_base  = pya.DPolygon(STL.rect( self.shot_offset_x, self.shot_offset_y, self.shot_w, self.shot_h))
        self.cell.shapes(self.central_shot_layer).insert(central_shot_cross)
        self.cell.shapes(self.central_shot_layer).insert(central_shot_base)

        show_chips       = (self.chip_count + self.teg_count) > 0
        chip_count_txt   = "\n".join([ txt for txt in [
            f"Name       : {self.name}"                                                     if self.name else "",
            f'Wafer      : {self.inch}" EBR {self.edge_exclude} mm {self.flat_notch}',
            f"Shot size  : {round(self.shot_w, 6)} um x {round(self.shot_h, 6)} um",
            f"Step size  : {round(self.shot_step_x, 6)} um x {round(self.shot_step_y, 6)} um",
            f"Shot offset: {round(self.shot_offset_x, 6)} um, {round(self.shot_offset_y, 6)} um",
            f"Shot count : Full {self.full_shot_count}, Partial {self.partial_shot_count}, Total {self.full_shot_count + self.partial_shot_count}",
            f"Chip size  : {round(self.chip_w, 6)} um x {round(self.chip_h, 6)} um"         if show_chips else "", 
            f"Scribe     : W {round(self.scribe_w, 6)} um, H {round(self.scribe_h, 6)} um"  if show_chips else "",
            f"----------------------------------------",
            f"Chip count : {self.chip_count}"                                               if show_chips else "", 
            f"TEG  count : {self.teg_count}"                                                if show_chips else "",
        ] if len(txt) > 0])

        chip_count_trans = pya.DTrans((self.wafer_radius), -(self.wafer_radius - 100))
        self.cell.shapes(self.gulde_layer).insert(pya.DText(chip_count_txt, chip_count_trans))
        
    def virtual_wafer(self):
        return Util_Wafer.wafer(0, 0, self.inch, self.layout.dbu, self.edge_exclude, p = 32, no_rounding = True, rotation = self.wafer_rot_angle)
        
    def virtual_shot(self, teg_loc = "", skip_loc = "", partial_loc = ""):
        return Util_Wafer.shot(0, 0, self.layout.dbu, self.shot_w, self.shot_h, self.chip_w, self.chip_h, self.scribe_w, self.scribe_h, self.scribe_config, teg_loc, skip_loc, partial_loc)

    def check_regs(self):
        unit         = self.layout.dbu
        wafer_params = self.virtual_wafer()
        ebr_poly     = wafer_params.get("ebr")
        base_poly    = pya.DPolygon(STL.rect(0, 0, self.wafer_diameter + self.shot_w * 4, self.wafer_diameter + self.shot_h * 4))

        ebr_reg      = pya.Region(ebr_poly.to_itype(unit))
        masking_reg  = pya.Region(base_poly.to_itype(unit))
        masking_reg  = masking_reg - ebr_reg
        
        mask_poly    = [ p.to_dtype(unit) for p in masking_reg.each()][0]
        return {"ebr" : ebr_poly, "mask" : mask_poly}
        
    def calc_start_point(self):
        shift_left   = math.ceil((self.shot_offset_x - (self.shot_w / 2) + self.wafer_radius) / self.shot_w)
        shift_down   = math.ceil((self.shot_offset_y - (self.shot_h / 2) + self.wafer_radius) / self.shot_h)
        
        x0           = - shift_left * self.shot_step_x + self.shot_offset_x
        y0           = - shift_down * self.shot_step_y + self.shot_offset_y
        
        col          = math.ceil((self.wafer_radius - (x0 - (self.shot_w / 2))) / self.shot_w)
        row          = math.ceil((self.wafer_radius - (y0 - (self.shot_h / 2))) / self.shot_h)
        return x0, y0, row, col
        
    def calc_relative_row_col(self, shot_center_pi):
        center_dist  = shot_center_pi - pya.Point(self.shot_offset_x, self.shot_offset_y)
        relative_col = round(center_dist.x / self.shot_step_x)
        relative_row = round(center_dist.y / self.shot_step_y)
        return f"{relative_row},{relative_col}"

    def shot_chip_skipper(self, shot_center_pi, shot_template, ebr_poly, mask_poly):
        skip_locs    = []
        partial_locs = []
        for k, chip in map((lambda kv : [kv[0], kv[1].get("chip")]), shot_template.items()):
            if not chip : continue
            
            valid_chip = Util_Wafer.inside_wafer(chip.bbox().center() + shot_center_pi, self.chip_w, self.chip_h, ebr_poly, mask_poly)
            if valid_chip  == "OUT":
                skip_locs.append(k)

            if valid_chip == "PARTIAL":
                if self.skip_partial_chip:
                    skip_locs.append(k)
                else:
                    partial_locs.append(k)

        skip_loc_str    = ";".join(skip_locs)
        partial_loc_str = ";".join(partial_locs)
        virtual_shot_params = self.virtual_shot(teg_loc = self.teg_loc, skip_loc = skip_loc_str, partial_loc = partial_loc_str)
        return skip_loc_str, partial_loc_str, virtual_shot_params.get("chip_count"), virtual_shot_params.get("teg_count")

    def produce_impl(self): 
        self.insert_wafer_cell()

        if self.place_shot :            
            check_dict       = self.check_regs()
            ebr_poly         = check_dict.get("ebr")
            mask_poly        = check_dict.get("mask") 
            shot_template    = self.virtual_shot().get("placement") if self.place_chip else None
            x0, y0, row, col = self.calc_start_point()
            skip_rrow_rcol   = []

            if self.skip_shot_loc:
                skip_loc_str   = re.sub(';+', ' ', re.sub(' +', '',  self.skip_shot_loc))
                skip_rrow_rcol = [f for f in re.findall( r"[-0-9]+,[-0-9]+", skip_loc_str)]

            for r, c in np.ndindex((row, col)):
                pi         = pya.DPoint(x0 + self.shot_step_x * c, y0 + self.shot_step_y * r)
                rrow_rcol  = self.calc_relative_row_col(pi)
                if rrow_rcol in skip_rrow_rcol : continue


                valid_shot = Util_Wafer.inside_wafer(pi, self.shot_w, self.shot_h, ebr_poly, mask_poly)
                
                if valid_shot  == "OUT"                                : continue # not inside
                if valid_shot  == "PARTIAL" and self.skip_partial_shot : continue # skip partial shots 
                
                is_partial_shot  =     valid_shot[1] == True 
                is_full_shot     = not(valid_shot[1] == True)
                layer_shot       = self.shot_partial if is_partial_shot else self.shot_full

                skip_loc, partial_loc, chip_count, teg_count = "", "", 0, 0
                
                if self.place_chip:
                    skip_loc, partial_loc, chip_count, teg_count = self.shot_chip_skipper(pi, shot_template, ebr_poly, mask_poly) 
                    if (chip_count >= self.skip_chip_cnt) or (teg_count >= self.skip_teg_cnt):
                        self.chip_count         += chip_count
                        self.teg_count          += teg_count
                        self.partial_shot_count += 1 if is_partial_shot else 0
                        self.full_shot_count    += 1 if is_full_shot    else 0
                        self.insert_shot_cell( pi.x, pi.y, layer_shot, skip_loc, partial_loc)
                else:
                    self.partial_shot_count += 1 if is_partial_shot else 0
                    self.full_shot_count    += 1 if is_full_shot    else 0
                    self.insert_shot_cell( pi.x, pi.y, layer_shot, skip_loc, partial_loc)
                
            self.insert_misc()

