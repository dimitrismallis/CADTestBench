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
        # Parameters
        side_len = 1.47802
        hex_height = 0.5
    
        cyl_d = 1.2
        cyl_h = hex_height / 2.0  # ensure cylinder is half the hexagon height
    
        # For a regular hexagon, side length == circumradius
        hex_radius = side_len
    
        # Hexagon prism
        hex_prism = (
            cq.Workplane("XY")
            .polygon(6, 2 * hex_radius)  # polygon expects circumscribed diameter
            .extrude(hex_height)
        )
    
        # Cylinder on top (fused)
        result = (
            hex_prism
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .circle(cyl_d / 2.0)
            .extrude(cyl_h, combine=True)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00980651/gpt_generated.stl')
