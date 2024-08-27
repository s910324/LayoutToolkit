import pya
import math
class STL(object):
    def __init__(self):
        super(STL, self).__init__()
        
    def sin(deg):
        return math.sin(STL.deg_2_arc(deg))
    
    def cos(deg):
        return math.cos(STL.deg_2_arc(deg))
    
    def tan(deg):
        return math.tan(STL.deg_2_arc(deg)) 
        
    def asin(val):
        return STL.arc_2_deg(math.asin(val))
    
    def acos(val):
        return STL.arc_2_deg(math.acos(val))
    
    def atan(val):
        return STL.arc_2_deg(math.atan(val)) 
              
    def deg_2_arc(deg):
        return (deg / 360) * 2 * math.pi
        
    def arc_2_deg(arc):
        return (arc / 2 / math.pi) * 360
        

    def circle(x, y, r, p = 64, deg1 = 0, checker = None):
        pts = []
        if isinstance(checker, (float, int)):
            if ((x ** 2 + y ** 2) ** (0.5) > (checker - r)):
                return pts

        if isinstance(checker, (list, tuple)):
            if ((x ** 2 + y ** 2)**(0.5) > (max(checker) - r)) or ((x ** 2 + y ** 2) ** (0.5) < (min(checker) - r)):
                return pts
                
        for i in range(p):
            ccx = x + r * STL.cos(deg1 + (360 / p) * i) 
            ccy = y + r * STL.sin(deg1 + (360 / p) * i) 
            pts.append(pya.DPoint(ccx, ccy))
        return pts + [pts[0]]

    def arc(x, y, r, p = 64, deg1 = 0, deg2=0, center_pt = False):
        pts = []
        for i in range(p + 1):
            ccd = deg1 + ((deg2 - deg1) / p) * i
            ccx = x + r * STL.cos(ccd) 
            ccy = y + r * STL.sin(ccd) 
            pts.append(pya.DPoint(ccx , ccy ))
        if center_pt:
            pts.append(pya.DPoint(x, y))
        return pts
    
    def triangle(x, y, d1, d2, deg1 = 0, deg2 = 90):
        pts = [
            pya.DPoint(                       x,                       y), 
            pya.DPoint((x + d1 * STL.cos(deg1)), (y + d1 * STL.sin(deg1))),
            pya.DPoint((x + d2 * STL.cos(deg2)), (y + d2 * STL.sin(deg2)))
        ]
        return pts
        
    
    def rect(x, y, w, h):
        return [
            pya.DPoint((x + (w/2)), (y + (h/2))),
            pya.DPoint((x - (w/2)), (y + (h/2))),
            pya.DPoint((x - (w/2)), (y - (h/2))),
            pya.DPoint((x + (w/2)), (y - (h/2))),
            pya.DPoint((x + (w/2)), (y + (h/2))),
        ]
        
    def diamond(x, y, w, h):
        return [
            pya.DPoint((x + (w/2)),           0),
            pya.DPoint(          0, (y + (h/2))),
            pya.DPoint((x - (w/2)),           0),
            pya.DPoint(          0, (y - (h/2))),
            pya.DPoint((x + (w/2)),           0)
        ]
        
    def cross(x, y, w, h, linewidth):
        half_lw = linewidth / 2
        half_w  = w / 2
        half_h  = h / 2
        x0, x1, x2, x3 = [x - half_w, x - half_lw, x + half_lw, x + half_w]
        y0, y1, y2, y3 = [y - half_h, y - half_lw, y + half_lw, y + half_h]
            
        return [
            pya.DPoint(x0, y1), pya.DPoint(x0, y2), pya.DPoint(x1, y2), pya.DPoint(x1, y3), 
            pya.DPoint(x2, y3), pya.DPoint(x2, y2), pya.DPoint(x3, y2), pya.DPoint(x3, y1), 
            pya.DPoint(x2, y1), pya.DPoint(x2, y0), pya.DPoint(x1, y0), pya.DPoint(x1, y1), 
        ]
        
    def fpoints(x, y, size, linewidth):
        w       = size * 0.7
        h       = size
        half_w  = w / 2
        half_h  = h / 2
        half_lw = linewidth / 2
        
        x0, x1, x2, x3     = [x - half_w, x - half_w + linewidth, x + linewidth, x + half_w]
        y0, y1, y2, y3, y4 = [y - half_h, y - half_lw, y + half_lw, y + half_h - linewidth, y + half_h]

        return [
            pya.DPoint(x0, y0), pya.DPoint(x0, y4), pya.DPoint(x3, y4), pya.DPoint(x3, y3), 
            pya.DPoint(x1, y3), pya.DPoint(x1, y2), pya.DPoint(x2, y2), pya.DPoint(x2, y1), 
            pya.DPoint(x1, y1), pya.DPoint(x1, y0), 
        ]
               
    def wafer(x, y, inch, p = 128):
        mm              = 1000 
        wafer_diameter  = 0
        primary_flat    = 0
        primary_notch   = 0
        
        if inch == 2: #2 unch
            wafer_diameter = 50.80 * mm
            primary_flat   = 15.88 * mm
            
        if inch == 4: #4 unch
            wafer_diameter = 100.0 * mm
            primary_flat   = 32.50 * mm
            
        if inch == 6: #6 unch
            wafer_diameter = 150.0 * mm
            primary_flat   = 57.50 * mm
            
        if inch == 8: #8 unch
            wafer_diameter = 200.0 * mm
            primary_notch = [3.0   * mm, 1.0 * mm, 0.5 * mm] # w&h, rounding, y-offset
            
        if inch == 12: #12 unch
            wafer_diameter = 300.0 * mm
            primary_notch = [3.0   * mm, 1.0 * mm, 0.5 * mm] # w&h, rounding, y-offset
        
        
        wafer_radius   = wafer_diameter/2
        
        wafer_circle_poly = pya.DPolygon(STL.circle(x, y, wafer_radius, p = p))
        flat_notch_poly   = None
        
        if primary_flat != 0:
            h = 2*(wafer_radius - (wafer_radius ** 2 - (primary_flat/2) ** 2 ) ** (0.5))
            flat_notch_poly  = pya.DPolygon(STL.rect(x, -wafer_radius, wafer_diameter, h))
            
        if primary_notch != 0:
            width, rounding, offset = primary_notch
            pts             = STL.rect(0, 0, width, width)
            flat_notch_poly = pya.DPolygon(pts)
            flat_notch_poly.transform(pya.DCplxTrans (1.0, 45, False, 0, (-wafer_radius-offset) ))
            
        
        return {"guide" : wafer_circle_poly, "flat_notch" : flat_notch_poly}
        
    def pcell(layout, lib_name, pcell_name, x, y, angle, pcell_parameters, va, vb, na, nb):
        unit       = layout.dbu
        lib        = pya.Library.library_by_name(lib_name)
        pcell_decl = lib.layout().pcell_declaration(pcell_name)
        pcell_var  = layout.add_pcell_variant(lib, pcell_decl.id(), pcell_parameters) 
        return pya.CellInstArray(pcell_var, pya.DCplxTrans (1.0, angle, False, x, y ), va, vb, na, nb)