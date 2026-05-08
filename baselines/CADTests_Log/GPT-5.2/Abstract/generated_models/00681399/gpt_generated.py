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
        block_size = 40.0
        block_height = 20.0
    
        hole_d = 12.0
    
        pipe_wall = 2.0
        pipe_id = hole_d
        pipe_od = pipe_id + 2.0 * pipe_wall
    
        # "Almost the same amount as the square" (slightly shorter than block height)
        pipe_height = block_height - 2.0
    
        # --- Model ---
        # 1) Square block
        result = cq.Workplane("XY").rect(block_size, block_size).extrude(block_height)
    
        # 2) Centered circular hole (negative extrusion from top face)
        result = (
            result
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .circle(hole_d / 2.0)
            .cutBlind(-block_height)  # cut down through the block
        )
    
        # 3) Annulus on top face, inner diameter matches hole, outer slightly bigger
        result = (
            result
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .circle(pipe_od / 2.0)
            .circle(pipe_id / 2.0)
            .extrude(pipe_height)     # hollow pipe sticking out
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00681399/gpt_generated.stl')
