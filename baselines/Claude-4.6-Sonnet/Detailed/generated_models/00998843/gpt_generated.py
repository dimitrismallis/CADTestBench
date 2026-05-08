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
        # --- Parameters ---
        base_len   = 0.5    # X
        base_wid   = 0.75   # Y
        base_h     = 0.15   # Z
        upper_len  = 0.5    # X
        upper_wid  = 0.35   # Y
        upper_h    = 0.15   # Z
        hole_dia   = 0.2
        hole_r     = hole_dia / 2  # 0.1
    
        # --- Step 1: Base block (centered in XY, sitting on Z=0) ---
        # X: -0.25 to 0.25, Y: -0.375 to 0.375, Z: 0 to 0.15
        base = cq.Workplane("XY").box(base_len, base_wid, base_h,
                                       centered=(True, True, False))
    
        # --- Step 2: Upper block on top of base, at one Y-end ---
        # Upper block: 0.5 x 0.35 x 0.15
        # Positioned at the +Y end of the base:
        #   Y range: (0.375 - 0.35) to 0.375 = 0.025 to 0.375
        #   Center Y of upper block: 0.025 + 0.35/2 = 0.025 + 0.175 = 0.2
        #   Center X: 0
        #   Center Z: 0.15 + 0.15/2 = 0.225
        upper_center_y = (base_wid/2 - upper_wid) + upper_wid/2  # = 0.375 - 0.35 + 0.175 = 0.2
        upper_center_z = base_h + upper_h / 2  # = 0.15 + 0.075 = 0.225
    
        upper = cq.Workplane("XY").box(upper_len, upper_wid, upper_h,
                                        centered=(True, True, False))
        upper = upper.translate((0, upper_center_y - 0, base_h))
        # upper block center: (0, 0.2, 0.225)
    
        # --- Step 3: Union base and upper block ---
        result = base.union(upper)
    
        # --- Step 4: Circular hole through center of upper block ---
        # Hole center in XY: (0, 0.2)
        # Hole passes through both blocks: from Z=0 to Z=0.30 (thruAll)
        # We drill from the top face of the upper block downward through all
        result = (
            result
            .faces(">Z")
            .workplane()
            .center(0, upper_center_y)   # move to hole center in workplane coords
            .circle(hole_r)
            .cutThruAll()
        )
    
        # --- Step 5: Center the entire model at the origin ---
        # Current bounding box:
        #   X: -0.25 to 0.25 → center X = 0
        #   Y: -0.375 to 0.375 → center Y = 0
        #   Z: 0 to 0.30 → center Z = 0.15
        # Shift by (0, 0, -0.15)
        total_h = base_h + upper_h  # 0.30
        result = result.translate((0, 0, -total_h / 2))
    
        # --- Final object verification ---
        TOL = 0.001
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - base_len) < TOL, \
            f"X length: expected {base_len}, got {bb.xlen}"
        assert abs(bb.ylen - base_wid) < TOL, \
            f"Y length: expected {base_wid}, got {bb.ylen}"
        assert abs(bb.zlen - total_h) < TOL, \
            f"Z length: expected {total_h}, got {bb.zlen}"
    
        # Bounding box center at origin
        cx = (bb.xmin + bb.xmax) / 2
        cy = (bb.ymin + bb.ymax) / 2
        cz = (bb.zmin + bb.zmax) / 2
        assert abs(cx) < TOL, f"Center X: expected 0, got {cx}"
        assert abs(cy) < TOL, f"Center Y: expected 0, got {cy}"
        assert abs(cz) < TOL, f"Center Z: expected 0, got {cz}"
    
        # Volume check
        # Base volume: 0.5 * 0.75 * 0.15 = 0.05625
        # Upper volume: 0.5 * 0.35 * 0.15 = 0.02625
        # Hole volume: pi * r^2 * total_h = pi * 0.01 * 0.30
        base_vol  = base_len * base_wid * base_h
        upper_vol = upper_len * upper_wid * upper_h
        hole_vol  = math.pi * hole_r**2 * total_h
        expected_vol = base_vol + upper_vol - hole_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.5f}, got {actual_vol:.5f}"
    
        # Cylindrical face check (hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, \
            f"Cylindrical faces: expected at least 1 (hole), got {cyl_faces}"
    
        # Face count: base has 6 faces, upper adds faces, hole adds 1 cylinder
        # At minimum we expect more than 6 faces due to the staircase + hole
        total_faces = result.faces().size()
        assert total_faces > 6, \
            f"Total faces: expected > 6 for tiered shape with hole, got {total_faces}"
    
        # Check hole passes through: a point at the hole center should be outside the solid
        # Hole center after translation: (0, 0.2, 0) — but 0.2 is in original coords
        # After centering: Y stays 0.2 (base Y center was 0), Z shifts by -0.15
        # Hole center in final coords: (0, 0.2, 0) — midpoint of Z range [-0.15, 0.15]
        hole_center_final = (0, upper_center_y, 0)
        solid = result.val()
        assert not solid.isInside(hole_center_final, tolerance=0.001), \
            f"Point at hole center {hole_center_final} should be outside (in hole), but is inside"
    
        # Check a point inside the upper block (away from hole) is inside the solid
        inside_upper = (0.2, upper_center_y, 0.05)  # X=0.2 away from hole, in upper block Z range
        assert solid.isInside(inside_upper, tolerance=0.001), \
            f"Point {inside_upper} should be inside the upper block"
    
        # Check a point inside the base (away from hole) is inside the solid
        inside_base = (0.2, -0.3, -0.05)  # in base region, away from hole
        assert solid.isInside(inside_base, tolerance=0.001), \
            f"Point {inside_base} should be inside the base block"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00998843/gpt_generated.stl')
