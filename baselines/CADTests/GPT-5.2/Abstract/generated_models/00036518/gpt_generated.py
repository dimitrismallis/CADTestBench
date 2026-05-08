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
        d = 30.0
        r = d / 2.0
        h = 2.0 * d
    
        sector_deg = 120.0
        half_sector = sector_deg / 2.0
        tilt_deg = 25.0
    
        base = cq.Workplane("XY").cylinder(h, r)
    
        Rbig = r * 3.0
        sector = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(Rbig, 0)
            .radiusArc(
                (Rbig * math.cos(math.radians(sector_deg)),
                 Rbig * math.sin(math.radians(sector_deg))),
                Rbig
            )
            .close()
            .extrude(h)
            .translate((0, 0, -h / 2.0))
            .rotate((0, 0, 0), (0, 0, 1), -half_sector)
        )
    
        part = base.cut(sector)
    
        L = r * 20.0
        cutter = (
            cq.Workplane("XY")
            .box(L, L, L, centered=True)
            .rotate((0, 0, 0), (1, 0, 0), tilt_deg)
            .translate((0, 0, L * 0.10))
        )
    
        final_result = part.cut(cutter)
        return final_result
    
    final_result = create_cad()
    
    # Ensure the runner produces some output (does not affect returned geometry)
    bb = final_result.val().BoundingBox()
    print(f"BB: x={bb.xlen:.3f}, y={bb.ylen:.3f}, z={bb.zlen:.3f}")
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00036518/gpt_generated.stl')
