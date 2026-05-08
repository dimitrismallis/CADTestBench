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
        side = 0.929516
        extrude_h = 0.3
        semi_diam = (2.0 / 3.0) * side  # ~0.619677333...
        r = semi_diam / 2.0
    
        # Equilateral triangle height
        tri_h = (math.sqrt(3) / 2.0) * side
    
        # Vertices with centroid at origin, one vertex pointing down (-Y)
        v_bottom = (0.0, -2.0 * tri_h / 3.0)
        v_left   = (-side / 2.0,  tri_h / 3.0)
        v_right  = ( side / 2.0,  tri_h / 3.0)
    
        # Semicircle cutout: diameter is horizontal chord through the bottom vertex,
        # with the arc bulging downward. Endpoints of the diameter:
        p1 = (v_bottom[0] - r, v_bottom[1])
        p2 = (v_bottom[0] + r, v_bottom[1])
        p_arc = (v_bottom[0], v_bottom[1] - r)  # lowest point on arc
    
        # Build 2D profile: triangle minus semicircle
        wp = cq.Workplane("XY")
    
        # Triangle face
        wp = wp.polyline([v_bottom, v_left, v_right]).close()
    
        # Subtractive semicircle as a closed wire (arc + chord)
        wp = (
            wp.moveTo(p1[0], p1[1])
              .threePointArc(p_arc, p2)
              .lineTo(p1[0], p1[1])
              .close()
        )
    
        # Convert to face(s) and extrude; use cut by making the semicircle a separate face
        # via .wire()/.toPending() is tricky; simplest is Sketch API for robust 2D booleans.
        tri = cq.Sketch().polygon([v_bottom, v_left, v_right])
        semi = (
            cq.Sketch()
            .segment(p1, p2, tag="chord")
            .arc(p1, p_arc, p2, tag="arc")
            .assemble()
        )
        # Subtract semicircle from triangle
        face = tri.face(semi, mode="s")
    
        result = cq.Workplane("XY").placeSketch(face).extrude(extrude_h)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00998714/gpt_generated.stl')
