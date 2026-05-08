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
        # Given dimensions (units as provided)
        rect_len_x = 0.043025   # "length"
        rect_wid_y = 0.985934   # "width"
        extrude_h  = 1.39258
    
        # Cut definitions per prompt
        # "remaining top edge lengths are equal to the height of the box minus 1.19693 units"
        # Interpreting "height of the box" as the rectangle's Y-size (rect_wid_y) in the 2D sketch.
        top_edge_y_drop = rect_wid_y - 1.19693
    
        # "width of each cut from the side edges should be half of the difference between the box width and 0.563939 units"
        # Interpreting "box width" as the rectangle's X-size (rect_len_x) in the 2D sketch.
        cut_inset_x = 0.5 * (rect_len_x - 0.563939)
    
        # Build an explicit 2D wire for the irregular hexagon (centered rectangle with top corners cut)
        xL = -rect_len_x / 2.0
        xR =  rect_len_x / 2.0
        yB = -rect_wid_y / 2.0
        yT =  rect_wid_y / 2.0
    
        # Points defining the hexagon (clockwise)
        # Bottom edge: (xL,yB) -> (xR,yB)
        # Right side up to start of chamfer: (xR, yT - top_edge_y_drop)
        # Chamfer to top edge: (xR - cut_inset_x, yT)
        # Top edge: to (xL + cut_inset_x, yT)
        # Chamfer down left: (xL, yT - top_edge_y_drop)
        # Left side back to bottom: (xL, yB)
        pts = [
            (xL, yB),
            (xR, yB),
            (xR, yT - top_edge_y_drop),
            (xR - cut_inset_x, yT),
            (xL + cut_inset_x, yT),
            (xL, yT - top_edge_y_drop),
        ]
    
        profile = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
        )
    
        tile = profile.extrude(extrude_h)
    
        return tile
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00681547/gpt_generated.stl')
