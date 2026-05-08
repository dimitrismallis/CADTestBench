import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import numpy as np
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters (units as given) ---
        rect_x = 0.5
        rect_y = 0.433013
        plate_thk = 0.125
    
        # Corner cut size (right-triangle legs along rectangle edges)
        corner_cut = 0.05
    
        # Hexagon "diameter" interpreted as across-flats
        hex_flat_d = 0.5
        hex_leg_len = 0.75
    
        # Regular hexagon: across-flats = sqrt(3) * Rcirc  (where Rcirc is circumradius)
        # => Rcirc = across_flats / sqrt(3)
        hex_Rcirc = hex_flat_d / math.sqrt(3)
    
        # --- Octagonal plate profile (rectangle with 4 corner triangles removed) ---
        hx = rect_x / 2.0
        hy = rect_y / 2.0
        c = min(corner_cut, hx * 0.999, hy * 0.999)
    
        pts = [
            (-hx + c,  hy),
            ( hx - c,  hy),
            ( hx,      hy - c),
            ( hx,     -hy + c),
            ( hx - c, -hy),
            (-hx + c, -hy),
            (-hx,     -hy + c),
            (-hx,      hy - c),
        ]
    
        plate = (
            cq.Workplane("XY")
            .polyline(pts).close()
            .extrude(plate_thk)
        )
    
        # --- Two hexagonal columns on top face, symmetric about origin along X ---
        # Keep centers within the plate length
        hex_center_x = max(0.0, hx - hex_flat_d / 2.0)
        hex_centers = [(-hex_center_x, 0.0), (hex_center_x, 0.0)]
    
        result = (
            plate
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints(hex_centers)
            .polygon(6, 2.0 * hex_Rcirc)   # circumscribed circle diameter
            .extrude(hex_leg_len)          # combine=True by default, fuses into one solid
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00998698/gpt_generated.stl')
