import pya

from Lib_STL        import STL

class SERPANT(pya.PCellDeclarationHelper):
    def __init__(self):
        super().__init__()
        self.orentation_option_dict  = {
            "Verticle"   : 0, 
            "Horizontal" : 1, 
        }
        
        self.end_option_dict  = {
            "Flat"     : 0, 
            "Rounded"  : 1, 
        }

        
        self.param("name",         self.TypeString,  "Name",                               default =   "")
        self.param("main",         self.TypeLayer,   "Layer",                              default = pya.LayerInfo(1, 0))
        
        self.o_option = self.param("orentation_option", self.TypeString,  "Orentation Options",      default = 1)
        
        self.param("line_w",       self.TypeDouble,  "Line Width",          unit =  "um",   default =  1)
        self.param("line_s",       self.TypeDouble,  "Line Space",          unit =  "um",   default =  2)
                
        self.param("jog_l",        self.TypeDouble,  "Jog Length",          unit =  "um",   default =  50)
        self.param("jog_t",        self.TypeDouble,  "Jog Turns (min 0.5)", unit =  "turns",default =  5)
        self.param("start_ext",    self.TypeDouble,  "Start Extend",        unit =  "um",   default =  5)
        self.param("stop_ext",     self.TypeDouble,  "End Extend",          unit =  "um",   default =  5)

        self.param("jog_r",        self.TypeDouble,  "Jog Rounding",        unit =  "um",   default =  0)
        self.param("points",       self.TypeInt,     "Round Points",        unit = "pts",   default = 32)
        
        self.e_option = self.param("end_option",        self.TypeString,  "Line End Options",      default = 0)
        
        _ = [ self.o_option.add_choice(k,v) for k, v in self.orentation_option_dict.items()]
        _ = [ self.e_option.add_choice(k,v) for k, v in self.end_option_dict.items()]

    def display_text_impl(self):
        class_name  = self.__class__.__name__
        custom_name = self.name
        param_name  = f"({self.line_w},{self.line_s},{self.jog_l},{self.jog_t}, )"
        
        return "_".join([ n for n in [custom_name, class_name, param_name] if n ])
    
        
    def coerce_parameters_impl(self):         
        self.line_w     = 0   if self.line_w     <= 0   else self.line_w     
        self.line_s     = 0   if self.line_s     <= 0   else self.line_s
        
        self.jog_l      = 0   if self.jog_l      <= 0   else self.jog_l
        self.jog_t      = 0.5 if self.jog_t      <= 0.5 else int (self.jog_t / 0.5) * 0.5
        self.start_ext  = 0   if self.start_ext  <= 0   else self.start_ext
        self.stop_ext   = 0   if self.stop_ext   <= 0   else self.stop_ext

        self.jog_r      = 0   if self.jog_r      <= 0   else self.jog_r
        self.points     = 4   if self.points     <= 4   else self.points 

    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
    
    def parameters_from_shape_impl(self):
        pass
    
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())

  
    def produce_impl(self):
        points     = []
        half_jog   = self.jog_l/2
        pitch      = (self.line_w + self.line_s)
        half_turns = int(self.jog_t / 0.5)
        for half_turn in range(half_turns):
            sign_0, sign_1 = (-1,  1) if half_turn % 2 == 0 else ( 1, -1)
            points += [
                pya.DPoint(sign_0 * half_jog, ((half_turns/2) - half_turn - 0.5) * pitch),
                pya.DPoint(sign_1 * half_jog, ((half_turns/2) - half_turn - 0.5) * pitch)
            ]
                
        if (self.orentation_option == 0):
            path   = pya.DPath(points, 0)
            points = [p for p in path.transformed(pya.DTrans(1, False, 0.0, 0.0)).each_point()]
            points = [points[ 0] - pya.DVector( self.start_ext, 0) ] + points + [points[-1] + pya.DVector( self.stop_ext,  0)]

        else:
            points[ 0] = points[ 0] - pya.DVector( self.start_ext, 0) 
            points[-1] = points[-1] + pya.DVector( self.stop_ext,  0) * {0 :-1, 1 :  1}[half_turns % 2]
            
        path = pya.DPath(points, self.line_w)
        
        if self.jog_r:
            path = path.round_corners(self.jog_r, self.points, self.layout.dbu)
        
        if self.end_option == 1 :
            path.round   = True
            path.bgn_ext = self.line_w/2
            path.end_ext = self.line_w/2
            
        self.cell.shapes(self.main_layer).insert(path)

        
