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
        # Parameters (mm)
        length = 120.0
        width = 30.0
        height = 20.0
    
        # Semi-circle cut parameters
        cut_radius = 10.0  # radius of the semicircle
        # Place the semicircle so its flat edge lies on the top face, cutting downward
        # (center of the full circle is on the top face plane)
        cut_center_y = 0.0
    
        # Base prism
        base = cq.Workplane("XY").box(length, width, height, centered=True)
    
        # Create a semicircle profile on the YZ plane and cut it through the full length (X direction)
        # On the YZ plane: x-axis corresponds to Y, y-axis corresponds to Z.
        semi_profile = (
            cq.Workplane("YZ")
            .center(cut_center_y, height / 2.0)  # move to top face level in Z
            .moveTo(-cut_radius, 0)
            .radiusArc((cut_radius, 0), cut_radius)  # top semicircle (bulges upward in +Z)
            .close()
        )
    
        # Extrude the profile along +X and -X to ensure it fully spans the prism length, then cut
        cutter = semi_profile.extrude(length * 1.2, both=True)
    
        result = base.cut(cutter)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00006892/gpt_generated.stl')
