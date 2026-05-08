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
        main_w, main_h = 60.0, 40.0
        small_w, small_h = 25.0, 15.0
        thickness = 5.0
    
        # Main rectangle is centered at origin:
        # right edge at x = main_w/2, mid-height at y = 0
        # Small rectangle should:
        # - touch main rectangle on the right: small left edge at x = main_w/2
        # - start halfway up main rectangle: small bottom edge at y = 0
        small_center_x = (main_w / 2.0) + (small_w / 2.0)
        small_center_y = (small_h / 2.0)  # bottom at y=0
    
        result = (
            cq.Workplane("XY")
            .rect(main_w, main_h)
            .center(small_center_x, small_center_y)
            .rect(small_w, small_h)
            .extrude(thickness)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00000960/gpt_generated.stl')
