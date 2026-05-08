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
        w = 1.30586
        h_rect = 0.616516
        h_total = 1.25576
        thickness = 0.023051
    
        cut_base = 0.019678
        cut_h = 0.101205
    
        # Outer profile points (pentagon): rectangle with top isosceles triangle
        # Rectangle spans x=[-w/2, +w/2], y=[0, h_rect]; apex at (0, h_total)
        pts = [
            (-w/2, 0.0),
            ( w/2, 0.0),
            ( w/2, h_rect),
            ( 0.0, h_total),
            (-w/2, h_rect),
        ]
    
        # --- Create solid from outer profile ---
        solid = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(thickness)
        )
    
        # --- Cut out the two small bottom corner triangles (as through-thickness cuts) ---
        # Left corner triangle in XY: (-w/2,0), (-w/2+cut_base,0), (-w/2,cut_h)
        # Right corner triangle in XY: (w/2,0), (w/2-cut_base,0), (w/2,cut_h)
        solid = (
            solid
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .moveTo(-w/2, 0.0)
            .lineTo(-w/2 + cut_base, 0.0)
            .lineTo(-w/2, cut_h)
            .close()
            .moveTo(w/2, 0.0)
            .lineTo(w/2 - cut_base, 0.0)
            .lineTo(w/2, cut_h)
            .close()
            .cutBlind(thickness)  # cut down through the full plate thickness
        )
    
        # --- Rotate -90° about Z and translate to target center ---
        rotated = solid.rotate((0, 0, 0), (0, 0, 1), -90)
    
        target = cq.Vector(0.605354, -0.75, 0.0)
        bb = rotated.val().BoundingBox()
        current_center = cq.Vector(
            (bb.xmin + bb.xmax) / 2.0,
            (bb.ymin + bb.ymax) / 2.0,
            (bb.zmin + bb.zmax) / 2.0,
        )
        moved = rotated.translate((target - current_center).toTuple())
    
        return moved
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00997616/gpt_generated.stl')
