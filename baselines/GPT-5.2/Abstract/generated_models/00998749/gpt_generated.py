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
        rect_h = 40.0                 # base sketch height (Y)
        rect_w = 2.0 * rect_h         # base sketch width (X), twice height
        base_thk = 4.0                # base extrusion depth (Z)
    
        wall_thk = 3.0                # wall thickness (ring width)
        wall_h = 30.0                 # wall height above base
        inner_fillet_r = 1.0          # rounding for inside top edges/corners
    
        # --- Base ---
        base = cq.Workplane("XY").rect(rect_w, rect_h).extrude(base_thk)
    
        # --- Walls (ring) on top of base ---
        outer_w = rect_w
        outer_h = rect_h
        inner_w = outer_w - 2.0 * wall_thk
        inner_h = outer_h - 2.0 * wall_thk
    
        box = (
            base
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(outer_w, outer_h)
            .rect(inner_w, inner_h)          # second rectangle creates a ring
            .extrude(wall_h)
        )
    
        # --- Round inside corners/edges of the wall (at the top opening) ---
        # Select the top face, then the inner wire (smallest area), then its edges.
        box = (
            box
            .faces(">Z")
            .wires(cq.selectors.AreaNthSelector(0))  # inner opening wire
            .edges()
            .fillet(inner_fillet_r)
        )
    
        return box
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00998749/gpt_generated.stl')
