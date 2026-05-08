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
        outer_radius = 40.0
        inner_radius = 25.0
        height = 30.0
        cap_thickness = 2.0  # thickness of the bottom closing disk
    
        # --- Annulus sketch and extrusion (hollow cylinder) ---
        ring = (
            cq.Workplane("XY")
            .circle(outer_radius)
            .circle(inner_radius)   # second circle on same plane creates an inner wire (hole)
            .extrude(height)
        )
    
        # --- Bottom cap: add a disk on the bottom face to close the cylinder ---
        # Cap uses the inner radius so it closes the central opening.
        capped = (
            ring
            .faces("<Z")
            .workplane(centerOption="CenterOfMass")
            .circle(inner_radius)
            .extrude(cap_thickness, combine=True)
        )
    
        return capped
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00520675/gpt_generated.stl')
