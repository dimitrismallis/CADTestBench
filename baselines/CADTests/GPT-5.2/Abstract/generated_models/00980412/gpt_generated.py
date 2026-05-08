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
        base = 80.0                 # triangle base length
        height = 180.0              # > 2x base to match request
        frame_width = 10.0          # wall thickness of the rack frame
        thickness = 18.0            # extrusion thickness (Z)
        edge_fillet = 2.0           # soften edges a bit
    
        # Outer right triangle vertices (counter-clockwise)
        outer_pts = [(0, 0), (base, 0), (0, height)]
    
        # Inner triangle is an inward offset of the outer triangle
        # Use offset2D on the closed wire to keep it robust/parametric.
        outer_wire_wp = (
            cq.Workplane("XY")
            .polyline(outer_pts)
            .close()
        )
    
        inner_wire = outer_wire_wp.offset2D(-frame_width, kind="intersection").val()
    
        # Build a face: outer boundary minus inner boundary (hollow frame)
        outer_wire = outer_wire_wp.val()
        frame_face = cq.Face.makeFromWires(outer_wire, [inner_wire])
    
        # Extrude the face into a solid rack
        rack = (
            cq.Workplane("XY")
            .add(frame_face)
            .extrude(thickness)
        )
    
        # Optional: fillet vertical and top edges for a more "rack-like" feel
        rack = (
            rack
            .edges("|Z").fillet(edge_fillet)
            .faces(">Z").edges().fillet(edge_fillet * 0.6)
        )
    
        return rack
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00980412/gpt_generated.stl')
