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
        # --- Parameters ---
        r_outer = 30.0          # outer radius
        r_inner = 24.0          # inner cut radius
        inner_offset_x = 10.0   # offset of inner circle to form crescent
        thickness = 8.0         # extrusion thickness
        edge_fillet = 0.8       # optional edge fillet
    
        # Base: extruded outer circle
        outer = cq.Workplane("XY").circle(r_outer).extrude(thickness)
    
        # Cut: extruded inner circle, shifted in +X
        inner_cut = (
            cq.Workplane("XY")
            .center(inner_offset_x, 0)
            .circle(r_inner)
            .extrude(thickness)
        )
    
        crescent = outer.cut(inner_cut)
    
        # Light edge finishing (safe: only if radius > 0)
        if edge_fillet and edge_fillet > 0:
            crescent = crescent.edges().fillet(edge_fillet)
    
        return crescent
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00673733/gpt_generated.stl')
