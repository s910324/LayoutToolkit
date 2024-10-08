import re
import pya
import math
import numpy as np

from Lib_STL        import STL

class Util_Wafer(object):
    def __init__(self):
        super(Util_Wafer, self).__init__()
       
    def inside_wafer(rect_center, rect_w, rect_h, ebr_poly, mask_poly):
        x1, x2 = rect_center.x - rect_w / 2, rect_center.x + rect_w / 2
        y1, y2 = rect_center.y - rect_h / 2, rect_center.y + rect_h / 2
        rect   = pya.DBox(pya.DPoint(x1, y1), pya.DPoint(x2, y2))
        valid  = (ebr_poly.touches(rect), mask_poly.touches(rect))
        return {
            (True,  True ) : "PARTIAL",
            (True,  False) : "FULL",
            (False, True ) : "OUT",
            (False, False) : "OUT",

        }[valid]

    def chip_full_scribe(x, y, unit, chip_w, chip_h, scribe_w, scribe_h):
        cp             = pya.DPoint(x, y)
        x_offset       = (chip_w + scribe_w) / 2
        y_offset       = (chip_h + scribe_h) / 2
        scribe_hori_w  = chip_w + (scribe_w * 2)
        scribe_vert_h  = chip_h + (scribe_h * 2)

        return {
            "chip"      : pya.DPolygon(STL.rect(cp.x, cp.y, chip_w, chip_h)) ,
            "scribe_l"  : pya.DPolygon(STL.rect(cp.x - x_offset, cp.y, scribe_w, scribe_vert_h )),
            "scribe_r"  : pya.DPolygon(STL.rect(cp.x + x_offset, cp.y, scribe_w, scribe_vert_h )), 
            "scribe_t"  : pya.DPolygon(STL.rect(cp.x, cp.y + y_offset, scribe_hori_w, scribe_h )),
            "scribe_b"  : pya.DPolygon(STL.rect(cp.x, cp.y - y_offset, scribe_hori_w, scribe_h )),
        }

    def chip_half_scribe(x, y, unit, chip_w, chip_h, scribe_w, scribe_h):
        cp             = pya.DPoint(x, y)
        x_offset       = (chip_w + scribe_w / 2) / 2
        y_offset       = (chip_h + scribe_h / 2) / 2
        scribe_hori_w  = chip_w + (scribe_w)
        scribe_vert_h  = chip_h + (scribe_h)

        return {
            "chip"      : pya.DPolygon(STL.rect(cp.x, cp.y, chip_w, chip_h)) ,
            "scribe_l"  : pya.DPolygon(STL.rect(cp.x - x_offset, cp.y, scribe_w / 2, scribe_vert_h )),
            "scribe_r"  : pya.DPolygon(STL.rect(cp.x + x_offset, cp.y, scribe_w / 2, scribe_vert_h )), 
            "scribe_t"  : pya.DPolygon(STL.rect(cp.x, cp.y + y_offset, scribe_hori_w, scribe_h / 2 )),
            "scribe_b"  : pya.DPolygon(STL.rect(cp.x, cp.y - y_offset, scribe_hori_w, scribe_h / 2 )),
        }

    def chip_L_scribe(x, y, unit, chip_w, chip_h, scribe_w, scribe_h):
        cp             = pya.DPoint(x, y)
        lx_offset      = (chip_w + scribe_w) / 2
        ly_offset      = (scribe_h) / 2
        bx_offset      = (scribe_w) / 2
        by_offset      = (chip_h + scribe_h) / 2
        scribe_hori_w  = chip_w + scribe_w
        scribe_vert_h  = chip_h + scribe_h

        return {
            "chip"      : pya.DPolygon(STL.rect(cp.x, cp.y, chip_w, chip_h)) ,
            "scribe_l"  : pya.DPolygon(STL.rect(cp.x - lx_offset, cp.y - ly_offset, scribe_w, scribe_vert_h )),
            "scribe_b"  : pya.DPolygon(STL.rect(cp.x - bx_offset, cp.y - by_offset, scribe_hori_w, scribe_h )),
        }    
         
    def chip_with_scribe(x, y, unit, chip_w, chip_h, scribe_w, scribe_h, scribe_option = 1, mask_poly = None):
        chip_data = None

        if scribe_option == 0:
            chip_data = Util_Wafer.chip_full_scribe(x, y, unit, chip_w, chip_h, scribe_w, scribe_h)

        if scribe_option == 1:
            chip_data = Util_Wafer.chip_half_scribe(x, y, unit, chip_w, chip_h, scribe_w, scribe_h)

        if scribe_option == 2:
            chip_data = Util_Wafer.chip_L_scribe   (x, y, unit, chip_w, chip_h, scribe_w, scribe_h)
        
        if None in [mask_poly, chip_data]:
            return chip_data

        
        chip_poly     = chip_data.get("chip")
        scribe_l_poly = chip_data.get("scribe_l")
        scribe_r_poly = chip_data.get("scribe_r")
        scribe_t_poly = chip_data.get("scribe_t")
        scribe_b_poly = chip_data.get("scribe_b")
        mask_reg      = pya.Region(mask_poly.to_itype(unit))
        get_partial   = lambda poly : [(mask_reg & pya.Region(poly.to_itype(unit))).each()][0] if poly else None

        return {
            "chip"      : get_partial(chip_poly    ), 
            "scribe_l"  : get_partial(scribe_l_poly), 
            "scribe_r"  : get_partial(scribe_r_poly), 
            "scribe_t"  : get_partial(scribe_t_poly), 
            "scribe_b"  : get_partial(scribe_b_poly), 
        }

    def shot(x, y, unit, shot_w, shot_h, chip_w, chip_h, scribe_w, scribe_h, scribe_option = 1, teg_loc = "", skip_loc = "", partial_loc = "", mask_poly = None):
        result = {
            "row"        :  0,
            "column"     :  0,
            "teg_count"  :  0, 
            "chip_count" :  0,
            "placement"  : {},
        }

        pitch_x      = chip_w + scribe_w
        pitch_y      = chip_h + scribe_h
        area_adj     = 1 if (scribe_option in [1, 2] ) else 0
        cp_adj       = 2 if (scribe_option in [1   ] ) else 1
        shot_base    = pya.DPolygon(STL.rect(0, 0, shot_w, shot_h))
        column       = round((shot_w - (scribe_w * area_adj)) / pitch_x)
        row          = round((shot_h - (scribe_h * area_adj)) / pitch_y)    
        shot_llp     = pya.DPoint(-shot_w / 2, -shot_h / 2)
        chip_cp      = shot_llp + pya.DPoint((chip_w / 2) + (scribe_w / cp_adj), (chip_h / 2) + (scribe_h / cp_adj))

        chip_count       = 0
        teg_count        = 0
        teg_row_col      = []
        skip_row_col     = []
        partial_row_col  = []
        teg_row_col_dict = {}
        
        if teg_loc:
            teg_loc_str      = re.sub(';+', ' ', re.sub(' +', '',  teg_loc))
            teg_name_row_col = [f for f in re.findall( r"[[\(][\w]+[\)]]?[0-9]+,[0-9]+|[0-9]+,[0-9]+", teg_loc_str)]
            
            for name_row_col in teg_name_row_col:
                name    = ""
                row_col = ""
                if ")" in name_row_col:
                    name, row_col = name_row_col.replace("(", "").split(")")
                else:
                    row_col = name_row_col
                teg_row_col_dict[row_col] = name
            
            teg_row_col = list(teg_row_col_dict.keys())
            
        if skip_loc:
            skip_loc_str = re.sub(';+', ' ', re.sub(' +', '',  skip_loc))
            skip_row_col = [f for f in re.findall( r"[0-9]+,[0-9]+", skip_loc_str)]

        if partial_loc:
            partial_loc_str = re.sub(';+', ' ', re.sub(' +', '',  partial_loc))
            partial_row_col = [f for f in re.findall( r"[0-9]+,[0-9]+", partial_loc_str)]

        for r, c in np.ndindex((row+1, column+1)) :
            recog        = f"{r+1},{c+1}"
            chip_content = {}
            attri        = 1
            
            is_teg       = (recog in teg_row_col)
            is_skip      = (recog in skip_row_col)
            is_partial   = (recog in partial_row_col)
            place_cell   = not(r == row) and not(c == column)
            pitch_loc    = pya.DPoint(c * pitch_x, r * pitch_y)
            chip_name    = teg_row_col_dict.get(recog) if is_teg else ""

            if is_skip : continue

            if place_cell:
                chip_loc     = chip_cp + pitch_loc
                chip_content = Util_Wafer.chip_with_scribe(chip_loc.x, chip_loc.y, unit, chip_w, chip_h, scribe_w, scribe_h, scribe_option)

                if   [is_teg, is_partial] == [ True, False]:
                    attri       = 2
                    teg_count  += 1

                elif [is_teg, is_partial] == [False, False]:
                    attri       = 1
                    chip_count += 1

                elif [is_teg, is_partial] == [False,  True]:
                    attri       = -1

                elif [is_teg, is_partial] == [ True,  True]:
                    attri       = -2

                else : 
                    attri       = 0

            result["placement"][recog] = {
                "attri"  : attri,
                "name"   : chip_name if chip_name else "", 
                "chip"   : chip_content.get("chip"),
                "scribe" : [chip_content.get("scribe_l"), chip_content.get("scribe_r"), chip_content.get("scribe_t"), chip_content.get("scribe_b")]
            }
                
        result["row"]        = row
        result["column"]     = column
        result["teg_count"]  = teg_count
        result["chip_count"] = chip_count
        return result

  
    def waferDimension(inch):
        mm = 1000 
        return { 
            2: {
                "diameter" : 50.80 * mm,
                "notch"    :       None,
                "flat"     : 15.88 * mm,
            }, 
                    
            4 : {
                "diameter" : 100.0 * mm,
                "notch"    :       None,
                "flat"     : 32.50 * mm,
            },
                    
            6 : {
                "diameter" : 150.0 * mm,
                "notch"    :       None,
                "flat"     : 57.50 * mm,
            },
    
            8 : {
                "diameter" : 200.0 * mm,
                "notch"    : [3.0  * mm, 1.0 * mm, 0.5 * mm], # w&h, rounding, y-offset
                "flat"     :       None, 
            }, 
    
            12 : {
                "diameter" : 300.0 * mm,
                "notch"    : [3.0  * mm, 1.0 * mm, 0.5 * mm], # w&h, rounding, y-offset
                "flat"     :       None,
            },
        }[inch]
        
    def wafer(x, y, inch, unit, ebr = 3, p = 128, no_rounding = False, rotation = 0):
        mm              = 1000
        dim_params      = Util_Wafer.waferDimension(inch)
        wafer_diameter  = dim_params["diameter"]
        primary_flat    = dim_params["flat"]
        primary_notch   = dim_params["notch"]      
        wafer_radius    = wafer_diameter / 2
        ebr_radius      = wafer_radius - (ebr * mm)
        
        
        if primary_flat :
            h = 2 * (wafer_radius - (wafer_radius ** 2 - (primary_flat/2) ** 2 ) ** (0.5))
            flat_notch_poly = pya.DPolygon(STL.rect(x, -wafer_radius, wafer_diameter, h))
            
        if primary_notch :
            width, rounding, offset = primary_notch
            pts             = STL.rect(0, 0, width, width)
            flat_notch_poly = pya.DPolygon(pts)
            flat_notch_poly.transform(pya.DCplxTrans (1.0, 45, False, 0, (-wafer_radius-offset) ))
            
        guide_poly     = pya.DPolygon(STL.circle(x, y, wafer_radius, p = p))
        ebr_guide_poly = pya.DPolygon(STL.circle(x, y, ebr_radius, p = p))
        
        guide_reg      = pya.Region(guide_poly.to_itype(unit))
        ebr_guide_reg  = pya.Region(ebr_guide_poly.to_itype(unit))
        
        flat_notch_reg = pya.Region(flat_notch_poly.to_itype(unit))
        
        wafer_reg      = ( guide_reg     - flat_notch_reg).transform(pya.ICplxTrans(1, rotation, False, 0, 0))
        ebr_reg        = ( ebr_guide_reg - flat_notch_reg).transform(pya.ICplxTrans(1, rotation, False, 0, 0))
        
        if not(no_rounding):
            wafer_reg = wafer_reg.rounded_corners(1 * mm / unit, 1 * mm / unit, 16)
            ebr_reg   = ebr_reg.rounded_corners(  1 * mm / unit, 1 * mm / unit, 16)
        
        wafer_poly     = [ p.to_dtype(unit) for p in wafer_reg.each()][0]
        ebr_poly       = [ p.to_dtype(unit) for p in   ebr_reg.each()][0]
        
        return {
            "guide"    : guide_poly, 
            "wafer"    : wafer_poly,
            "ebr"      : ebr_poly,
            "diameter" : wafer_diameter,
        }