import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        base_length  = 80.0
        base_width   = 50.0
        base_height  = 10.0
        slot_length  = 40.0
        slot_width   = 25.0
        slot_depth   =  6.0
    
        # --- Step 1: Create base rectangular solid ---
        result = (
            cq.Workplane("XY")
            .rect(base_length, base_width)
            .extrude(base_height)
        )
    
        # --- Step 2: Cut a centered rectangular slot from the top face ---
        result = (
            result
            .faces(">Z")
            .workplane()
            .rect(slot_length, slot_width)
            .cutBlind(slot_depth)
        )
    
        # --- Debug: print ALL face info ---
        print(f"\nTotal faces: {result.faces().size()}")
        for i, f in enumerate(result.faces().vals()):
            n = f.normalAt()
            c = f.Center()
            bb_f = f.BoundingBox()
            print(f"  Face {i}: center=({c.x:.2f},{c.y:.2f},{c.z:.2f}), "
                  f"area={f.Area():.2f}, normal=({n.x:.2f},{n.y:.2f},{n.z:.2f}), "
                  f"bbox=({bb_f.xmin:.1f},{bb_f.xmax:.1f},{bb_f.ymin:.1f},{bb_f.ymax:.1f},{bb_f.zmin:.1f},{bb_f.zmax:.1f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00997580/gpt_generated.stl')
