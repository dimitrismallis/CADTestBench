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
        # --- Convert meters to millimeters (CadQuery default units) ---
        m_to_mm = 1000.0
    
        # Vertical rectangle (stem)
        stem_len = 0.036 * m_to_mm     # along X
        stem_w   = 0.0135 * m_to_mm    # along Y
        stem_h   = 0.9 * m_to_mm       # along Z
    
        # Horizontal rectangle (bar)
        bar_len = 0.24 * m_to_mm       # along X
        bar_w   = stem_w               # along Y
        bar_thk = stem_len             # extrude height along Z (same as stem_len)
    
        # Placement: bar is 0.15 m below the top of the stem
        offset_below_top = 0.15 * m_to_mm
        bar_center_z = (stem_h / 2.0) - offset_below_top  # stem is centered at Z=0
    
        # --- Build stem (extrude from XY) ---
        stem = cq.Workplane("XY").rect(stem_len, stem_w).extrude(stem_h)
    
        # --- Build bar (extrude from XY, then translate up near top) ---
        bar = (
            cq.Workplane("XY")
            .rect(bar_len, bar_w)
            .extrude(bar_thk)
            .translate((0, 0, bar_center_z))
        )
    
        # Union to form T-shape
        result = stem.union(bar)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00998300/gpt_generated.stl')
