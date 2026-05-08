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
        # --- Input dimensions (meters) ---
        base_w_m = 0.767871
        top_w_m  = 1.04978
        height_m = 0.576632
        length_m = 0.012814
    
        # --- Convert to mm (CadQuery default) ---
        mm = 1000.0
        base_w = base_w_m * mm
        top_w  = top_w_m * mm
        height = height_m * mm
        length = length_m * mm
    
        # --- 2D isosceles trapezoid profile, centered about origin in XY ---
        # Place bottom base at y = -height/2, top base at y = +height/2
        yb = -height / 2.0
        yt =  height / 2.0
        xb = base_w / 2.0
        xt = top_w / 2.0
    
        profile = (
            cq.Workplane("XY")
            .moveTo(-xb, yb)
            .lineTo( xb, yb)
            .lineTo( xt, yt)
            .lineTo(-xt, yt)
            .close()
        )
    
        # --- Extrude to 3D (along +Z) ---
        solid = profile.extrude(length, combine=True)
    
        # --- Orientation: rotate for "proper orientation" ---
        # 1) Rotate 90° about X: moves extrusion axis from +Z to -Y
        # 2) Rotate 90° about Z: swaps X/Y in the final orientation
        solid = (
            solid
            .rotate((0, 0, 0), (1, 0, 0), 90)
            .rotate((0, 0, 0), (0, 0, 1), 90)
        )
    
        # --- Translation adjustment: move so bounding box min corner is at origin ---
        bb = solid.val().BoundingBox()
        solid = solid.translate((-bb.xmin, -bb.ymin, -bb.zmin))
    
        return solid
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00520570/gpt_generated.stl')
