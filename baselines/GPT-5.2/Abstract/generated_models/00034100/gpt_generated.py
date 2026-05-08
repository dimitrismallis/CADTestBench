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
        # --- Parameters (mm) ---
        L = 80.0          # block length (X)
        W = 40.0          # block width  (Y)
        H = 12.0          # block thickness (Z)
    
        hole_d = 18.0
        hole_r = hole_d / 2.0
        hole_y = 8.0      # circle above midpoint (+Y)
    
        # Slit ("wire-cutter") parameters
        slit_d = 1.2
    
        # Slit runs from top of hole (in plan) to +Y short edge
        y0 = hole_y + hole_r
        y1 = W / 2.0 + 0.5  # slightly beyond edge for robust cut
    
        if y1 <= y0:
            y1 = y0 + 2.0
    
        slit_len = y1 - y0
        slit_center_y = (y0 + y1) / 2.0
    
        # --- Base block (z from 0 to H) ---
        block = cq.Workplane("XY").rect(L, W).extrude(H)
    
        # --- Circular through-hole ---
        block = (
            block
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(0, hole_y)
            .circle(hole_r)
            .cutThruAll()
        )
    
        # --- Slit cutter: 2D capsule (slot) extruded through thickness ---
        slit_tool = (
            cq.Workplane("XY")
            .center(0, slit_center_y)
            .slot2D(slit_len, slit_d, angle=90)  # length along Y, rounded ends
            .extrude(H)
        )
    
        result = block.cut(slit_tool)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00034100/gpt_generated.stl')
