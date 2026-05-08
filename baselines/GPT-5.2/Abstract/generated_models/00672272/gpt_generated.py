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
        base_len = 160.0          # "long" dimension
        base_wid = 30.0           # "rectangles shorter edge" length
        base_thk = 6.0            # "small amount" extrusion
    
        # Two small squares (tabs)
        tab_len = base_len / 16.0     # along X, sticking out from short edge
        tab_wid = 10.0                # square width (Y) - same for both
        tab_thk = base_thk / 3.0      # 1/3 the extrusion of the rectangle
    
        # --- Base ---
        base = cq.Workplane("XY").rect(base_len, base_wid).extrude(base_thk)
    
        # --- Tabs: connect to center of the rectangle's shorter edges (±X faces) ---
        # Place each tab so its inner face is flush with the base end face.
        tab1 = (
            cq.Workplane("XY")
            .center(base_len / 2 + tab_len / 2, 0)
            .rect(tab_len, tab_wid)
            .extrude(tab_thk)
        )
        tab2 = (
            cq.Workplane("XY")
            .center(-base_len / 2 - tab_len / 2, 0)
            .rect(tab_len, tab_wid)
            .extrude(tab_thk)
        )
    
        result = base.union(tab1).union(tab2)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00672272/gpt_generated.stl')
