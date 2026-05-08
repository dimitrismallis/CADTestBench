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
        page_w = 80.0          # width of each page measured from the hinge (x direction)
        page_h = 120.0         # page height (y direction)
        thickness = 4.0        # book thickness (z direction)
        open_angle = 140.0     # obtuse angle between the two page planes (degrees)
    
        # Hinge is the shared edge: line along Y at x=0, z=0
        # Left page lies in XY plane, spanning x in [-page_w, 0]
        left = (
            cq.Workplane("XY")
            .rect(page_w, page_h)
            .translate((-page_w / 2.0, 0, 0))  # move so right edge is on x=0 (hinge)
            .extrude(thickness)
        )
    
        # Right page: create a rotated workplane about the hinge axis (Y axis),
        # then draw the same rectangle spanning x in [0, page_w] in that plane.
        # Rotate by (180 - open_angle) so the dihedral between pages is open_angle.
        rot = 180.0 - open_angle
    
        right = (
            cq.Workplane(
                cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 0, 1))
            )
            .transformed(rotate=cq.Vector(0, rot, 0))  # rotate around Y axis
            .rect(page_w, page_h)
            .translate((page_w / 2.0, 0, 0))  # move so left edge is on x=0 (hinge)
            .extrude(thickness)
        )
    
        # Union: they should touch only along the hinge edge
        final_result = left.union(right)
        return final_result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00681053/gpt_generated.stl')
