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
        # Cylinder 1: base cylinder
        r1 = 20.0       # radius=20, diameter=40
        h1 = 30.0       # height=30
    
        # Cylinder 2: smaller diameter, same height, connects to bottom of cyl1
        r2 = 10.0       # radius=10, diameter=20
        h2 = 30.0       # same height as cyl1
    
        # Cylinder 3: larger diameter, shorter height, connects to bottom of cyl2
        r3 = 30.0       # radius=30, diameter=60 (larger than cyl1)
        h3 = 15.0       # shorter height
    
        # Central cutout
        r_cut = 3.0     # radius=3, diameter=6
    
        # Total height
        total_h = h1 + h2 + h3  # 75
    
        # Layout (bottom to top):
        # Cylinder 3: z = -(h2+h3) to z = -h2  => center at z = -(h2 + h3/2)
        # Cylinder 2: z = -h2      to z = 0    => center at z = -h2/2
        # Cylinder 1: z = 0        to z = h1   => center at z = h1/2
    
        # --- Step 1: Create Cylinder 1 centered at z=h1/2 (spans z=0 to z=h1) ---
        cyl1 = cq.Workplane(cq.Plane(origin=(0, 0, h1/2), xDir=(1,0,0), normal=(0,0,1))).cylinder(h1, r1)
    
        # --- Step 2: Create Cylinder 2 centered at z=-h2/2 (spans z=-h2 to z=0) ---
        cyl2 = cq.Workplane(cq.Plane(origin=(0, 0, -h2/2), xDir=(1,0,0), normal=(0,0,1))).cylinder(h2, r2)
    
        # --- Step 3: Create Cylinder 3 centered at z=-(h2+h3/2) (spans z=-(h2+h3) to z=-h2) ---
        cyl3 = cq.Workplane(cq.Plane(origin=(0, 0, -(h2 + h3/2)), xDir=(1,0,0), normal=(0,0,1))).cylinder(h3, r3)
    
        # --- Step 4: Union all three cylinders ---
        result = cyl1.union(cyl2).union(cyl3)
    
        # --- Step 5: Create central cutout through entire assembly ---
        # The cutout runs from z=-(h2+h3) to z=h1 (total_h=75), centered on Z axis
        # Place workplane at top of cyl1 (z=h1) and cut downward through total height
        result = (
            result
            .faces(">Z").workplane()
            .circle(r_cut)
            .cutBlind(-total_h)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
        solid = result.val()
    
        # Bounding box checks
        # X and Y extents: dominated by cyl3 (largest, diameter=60)
        assert abs(bb.xlen - 2*r3) < TOL, f"X extent: expected {2*r3}, got {bb.xlen}"
        assert abs(bb.ylen - 2*r3) < TOL, f"Y extent: expected {2*r3}, got {bb.ylen}"
    
        # Z extents: from -(h2+h3) to +h1
        assert abs(bb.zmin - (-(h2 + h3))) < TOL, f"Z min: expected {-(h2+h3)}, got {bb.zmin}"
        assert abs(bb.zmax - h1) < TOL, f"Z max: expected {h1}, got {bb.zmax}"
        assert abs(bb.zlen - total_h) < TOL, f"Z length: expected {total_h}, got {bb.zlen}"
    
        # Volume check: union of 3 cylinders minus central hole
        vol_cyl1 = math.pi * r1**2 * h1
        vol_cyl2 = math.pi * r2**2 * h2
        vol_cyl3 = math.pi * r3**2 * h3
        vol_hole = math.pi * r_cut**2 * total_h
        expected_vol = vol_cyl1 + vol_cyl2 + vol_cyl3 - vol_hole
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Check cylindrical faces exist (at least 4: outer surfaces of 3 cylinders + inner hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 4, f"Expected at least 4 cylindrical faces, got {cyl_faces}"
    
        # Check the central hole exists by verifying points on the axis are OUTSIDE the solid
        # at multiple Z levels spanning all three cylinders
        # In cyl1 region (z=15): axis point should be outside (in hole)
        assert not solid.isInside((0, 0, h1/2), tolerance=0.01), \
            "Axis point in cyl1 region should be inside the cutout (outside solid)"
        # In cyl2 region (z=-15): axis point should be outside (in hole)
        assert not solid.isInside((0, 0, -h2/2), tolerance=0.01), \
            "Axis point in cyl2 region should be inside the cutout (outside solid)"
        # In cyl3 region (z=-37.5): axis point should be outside (in hole)
        assert not solid.isInside((0, 0, -(h2 + h3/2)), tolerance=0.01), \
            "Axis point in cyl3 region should be inside the cutout (outside solid)"
    
        # Check solid material exists at offset from axis in each cylinder region
        # In cyl1 region: point at (r1*0.5, 0, h1/2) should be inside solid
        assert solid.isInside((r1 * 0.5, 0, h1/2), tolerance=0.01), \
            "Point in cyl1 body should be inside the solid"
        # In cyl2 region: point at (r2*0.5, 0, -h2/2) should be inside solid
        assert solid.isInside((r2 * 0.5, 0, -h2/2), tolerance=0.01), \
            "Point in cyl2 body should be inside the solid"
        # In cyl3 region: point at (r3*0.5, 0, -(h2+h3/2)) should be inside solid
        assert solid.isInside((r3 * 0.5, 0, -(h2 + h3/2)), tolerance=0.01), \
            "Point in cyl3 body should be inside the solid"
    
        # Check center of mass is on Z axis (symmetry)
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"Center of mass X should be ~0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y should be ~0, got {com.y}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00003763/gpt_generated.stl')
