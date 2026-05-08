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
        length   = 0.875     # X dimension (long side of rectangle)
        width    = 0.15      # Y dimension (short side / extrusion width)
        height   = 1.5       # Z dimension (extrusion height)
        fillet_r = 0.25      # fillet radius on two corners of same long edge
        hole_dia = 0.3       # hole diameter
        hole_r   = hole_dia / 2   # 0.15
        padding  = -0.639071      # padding applied to length and height for hole placement
    
        hx = length / 2     # 0.4375
        hy = width  / 2     # 0.075
        hz = height / 2     # 0.75
        r  = fillet_r       # 0.25
    
        # --- Step 1: Build 2D profile in XZ plane, centered at origin ---
        # Rectangle 0.875 (X) × 1.5 (Z) with two BOTTOM corners (Z = -hz) filleted r=0.25.
        # r=0.25 < min(hx, hz) = 0.4375  ✓
        #
        # Arc at bottom-right corner (hx, -hz):
        #   centre = (hx-r, -hz+r) = (0.1875, -0.5)
        #   start  = (hx,   -hz+r) = (0.4375, -0.5)   ← tangent to right edge
        #   end    = (hx-r, -hz  ) = (0.1875, -0.75)  ← tangent to bottom edge
        #   midpoint at 45°: (hx-r + r*sin45, -hz+r - r*cos45) = (0.3643, -0.6768)
        # Arc at bottom-left corner (-hx, -hz): symmetric
    
        sq2 = math.sqrt(2) / 2
    
        arc_mid_right = ( hx - r + r * sq2,  -hz + r - r * sq2)   # ( 0.3643, -0.6768)
        arc_mid_left  = (-hx + r - r * sq2,  -hz + r - r * sq2)   # (-0.3643, -0.6768)
    
        # Build profile using a plane whose normal is +Y and xDir is +X.
        # yDir = Z (up), so moveTo(x, z) maps to global (x, 0, z).
        # Extrude width=0.15 in +Y, starting from Y=-hy so solid is centred at Y=0.
        plane = cq.Plane(origin=(0, -hy, 0), xDir=(1, 0, 0), normal=(0, 1, 0))
    
        # In this plane: xDir=(1,0,0), normal=(0,1,0)
        # yDir = normal × xDir ... CadQuery computes yDir as xDir × normal? 
        # Let's verify: CadQuery uses yDir = zDir × xDir where zDir=normal
        # yDir = (0,1,0) × (1,0,0) = (0*0-0*0, 0*1-0*0, 0*0-1*1) = (0,0,-1)  ← -Z!
        # So moveTo(x, z_sketch) maps to global (x, -hy, -z_sketch).
        # That means the profile is Z-flipped. To get rounded corners at global Z=-hz,
        # we need z_sketch = +hz in the sketch.
        #
        # To avoid confusion, use a plane where yDir = +Z explicitly:
        plane = cq.Plane(origin=(0, -hy, 0), xDir=(1, 0, 0), normal=(0, -1, 0))
        # yDir = normal × xDir ... CadQuery: yDir = zDir × xDir, zDir = normal = (0,-1,0)
        # yDir = (0,-1,0) × (1,0,0) = ((-1)*0-0*0, 0*1-0*0, 0*0-(-1)*1) = (0,0,1) = +Z ✓
        # So moveTo(x, z) maps to global (x, -hy, z). Extrude in -normal = +Y direction.
    
        profile = (
            cq.Workplane(plane)
            .moveTo(-hx,    hz)          # top-left  (-0.4375,  0.75) → global (-0.4375, -hy,  0.75)
            .lineTo( hx,    hz)          # top-right  (0.4375,  0.75) → global ( 0.4375, -hy,  0.75)
            .lineTo( hx,   -hz + r)      # right edge down to arc start (0.4375, -0.5)
            .threePointArc(arc_mid_right, (hx - r, -hz))   # bottom-right arc → (0.1875, -0.75)
            .lineTo(-hx + r, -hz)        # bottom edge → (-0.1875, -0.75)
            .threePointArc(arc_mid_left,  (-hx, -hz + r))  # bottom-left arc → (-0.4375, -0.5)
            .close()                     # left edge back to top-left
            .extrude(width)              # extrude in +Y by 0.15 → solid from Y=-hy to Y=+hy
        )
    
        result = profile
    
        # Verify the solid is centred correctly
        bb_check = result.val().BoundingBox()
    
        # --- Step 2: Drill two holes near the rounded corners ---
        # Rounded corners are at the BOTTOM (Z = -hz = -0.75).
        # Holes are on the bottom face (same side as rounded corners).
        # hole_x = |length/2 + padding| = |0.4375 - 0.639071| = 0.201571
        # Holes drilled through full height (Z direction, from bottom upward).
    
        hole_x = abs(hx + padding)   # 0.201571
    
        result = (
            result
            .faces("<Z")
            .workplane()
            .pushPoints([(hole_x, 0), (-hole_x, 0)])
            .hole(hole_dia)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb  = result.val().BoundingBox()
        vol = result.val().Volume()
    
        # 1. Bounding box must match the specified dimensions
        assert abs(bb.xlen - length) < TOL, \
            f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, \
            f"Y width:  expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, \
            f"Z height: expected {height}, got {bb.zlen}"
    
        # 2. Volume must be less than the base box (fillets + holes remove material)
        base_vol = length * width * height   # 0.196875
        assert vol > 0,        f"Volume must be positive, got {vol}"
        assert vol < base_vol, f"Volume {vol:.6f} must be < base box {base_vol:.6f}"
    
        # 3. Approximate volume check
        fillet_removed = 2 * (r**2 - math.pi * r**2 / 4) * width
        hole_vol_calc  = 2 * math.pi * hole_r**2 * height
        expected_vol   = base_vol - fillet_removed - hole_vol_calc
        assert abs(vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.6f}, got {vol:.6f}"
    
        # 4. Cylindrical faces: 2 from fillets + 2 from holes = 4
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 4, \
            f"Expected at least 4 cylindrical faces (2 fillets + 2 holes), got {cyl_faces}"
    
        # 5. Hole existence: points at hole axes (mid-height, Y=0) must NOT be inside the solid
        solid = result.val()
        assert not solid.isInside(( hole_x, 0, 0), tolerance=0.01), \
            f"Point ({hole_x:.4f}, 0, 0) should be void (inside hole)"
        assert not solid.isInside((-hole_x, 0, 0), tolerance=0.01), \
            f"Point ({-hole_x:.4f}, 0, 0) should be void (inside hole)"
    
        # 6. Solid interior: centre of the box must be inside the solid
        assert solid.isInside((0, 0, 0), tolerance=0.01), \
            "Centre (0,0,0) must be inside the solid"
    
        # 7. Rounded corners removed: the exact corner points (±hx, 0, -hz) must be outside
        # the solid because the fillet arc removes that region.
        # The fillet arc at bottom-right has centre (hx-r, -hz+r)=(0.1875,-0.5).
        # The original corner (hx, -hz)=(0.4375,-0.75) is at distance
        # sqrt(0.25²+0.25²)=0.354 > r=0.25 from the arc centre, so it IS in the removed region.
        # Check a point clearly inside the removed corner region:
        # Use the exact corner location (on the boundary of the original rectangle but outside fillet)
        corner_right = ( hx,  0, -hz)   # (0.4375, 0, -0.75) — original sharp corner
        corner_left  = (-hx,  0, -hz)   # (-0.4375, 0, -0.75)
        assert not solid.isInside(corner_right, tolerance=0.005), \
            f"Original bottom-right corner {corner_right} should be outside solid (removed by fillet)"
        assert not solid.isInside(corner_left, tolerance=0.005), \
            f"Original bottom-left corner {corner_left} should be outside solid (removed by fillet)"
    
        # 8. Top corners (not filleted) should be inside the solid
        top_corner_right = (hx - 0.01, 0,  hz - 0.01)
        top_corner_left  = (-hx + 0.01, 0, hz - 0.01)
        assert solid.isInside(top_corner_right, tolerance=0.005), \
            f"Top-right corner region {top_corner_right} should be inside solid (not filleted)"
        assert solid.isInside(top_corner_left, tolerance=0.005), \
            f"Top-left corner region {top_corner_left} should be inside solid (not filleted)"
    
        # 9. Two holes confirmed by line intersection (line along Z through each hole centre)
        hits1 = solid.facesIntersectedByLine(( hole_x, 0, -hz - 0.1), (0, 0, 1))
        hits2 = solid.facesIntersectedByLine((-hole_x, 0, -hz - 0.1), (0, 0, 1))
        assert len(hits1) >= 2, \
            f"Line through hole 1 should intersect ≥2 faces, got {len(hits1)}"
        assert len(hits2) >= 2, \
            f"Line through hole 2 should intersect ≥2 faces, got {len(hits2)}"
    
        print(f"Bounding box : {bb.xlen:.4f} × {bb.ylen:.4f} × {bb.zlen:.4f}")
        print(f"Volume       : {vol:.6f}  (base box {base_vol:.6f}, expected ~{expected_vol:.6f})")
        print(f"Cyl. faces   : {cyl_faces}")
        print(f"Hole centres : (±{hole_x:.4f}, 0) on bottom face, drilled through Z")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00986712/gpt_generated.stl')
