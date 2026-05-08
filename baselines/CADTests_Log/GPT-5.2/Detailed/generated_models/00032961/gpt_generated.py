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
        # Parameters (units as given)
        length = 1.49973
        width = 0.16071
        thickness = 0.05357
        hole_d = 0.080357
    
        r = width / 2.0
        end_center_x = (length / 2.0) - r  # center of each semicircular end
    
        # Build a single 2D capsule profile (rectangle + two circles), then extrude
        profile = (
            cq.Workplane("XY")
            .rect(2 * end_center_x, width)
            .pushPoints([(end_center_x, 0.0), (-end_center_x, 0.0)])
            .circle(r)
            .combine()  # merge overlapping wires into one face
        )
    
        base = profile.extrude(thickness)
    
        # Through holes at the centers of the rounded ends
        result = (
            base.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .pushPoints([(end_center_x, 0.0), (-end_center_x, 0.0)])
            .hole(hole_d)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00032961/gpt_generated.stl')
