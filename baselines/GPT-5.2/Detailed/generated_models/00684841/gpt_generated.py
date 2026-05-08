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
        R_outer = 0.18
        R_inner = 0.179  # marginally smaller to create hollow sector
        sector_angle_deg = 20.0  # "minor sector" (not specified; choose a small angle)
    
        path_w = 0.0075
        path_h = 0.750037
        path_center = (-0.00375, 0.0)
    
        # Final transform
        final_translate = (0.180047, -0.375015, 0.0)
        final_rotate_deg = 180.0
    
        # --- Helper: make a sector wire on a given workplane ---
        def sector_wire(wp: cq.Workplane, radius: float, angle_deg: float) -> cq.Workplane:
            a = math.radians(angle_deg)
            p1 = (radius, 0.0)
            p2 = (radius * math.cos(a), radius * math.sin(a))
            # Build a closed wire: center -> p1 -> arc to p2 -> back to center
            return (
                wp
                .moveTo(0, 0)
                .lineTo(p1[0], p1[1])
                .radiusArc(p2, radius)
                .close()
            )
    
        # --- Sweep path: rectangle on XY, centered at (-0.00375, 0) ---
        path = (
            cq.Workplane("XY")
            .center(path_center[0], path_center[1])
            .rect(path_w, path_h)
            .wire()
        )
    
        # --- Outer swept solid: sector on XZ swept along rectangular path ---
        outer = (
            sector_wire(cq.Workplane("XZ"), R_outer, sector_angle_deg)
            .sweep(path, makeSolid=True, isFrenet=False)
        )
    
        # --- Inner cut: slightly smaller sector, extruded through the swept solid ---
        # Place on a plane that will cut through the whole object: use YZ plane at x=0
        # (sector is defined in that plane's local XY; it will be concentric with outer sector)
        inner_cut = (
            sector_wire(cq.Workplane("YZ"), R_inner, sector_angle_deg)
            .extrude(2.0, both=True)  # long enough to pass through the swept body
        )
    
        hollow = outer.cut(inner_cut)
    
        # --- Final positioning: translate then rotate 180° about Z axis ---
        result = (
            hollow
            .translate(final_translate)
            .rotate((0, 0, 0), (0, 0, 1), final_rotate_deg)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00684841/gpt_generated.stl')
