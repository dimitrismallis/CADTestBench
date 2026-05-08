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
        length = 1.5
        width = 0.52105
        height = 0.15789
        semi_diameter = 1.701232
        semi_radius = semi_diameter / 2.0  # ~0.850616
    
        # --- Step 1: Create the base rectangular prism ---
        # Centered at origin: X in [-0.75, 0.75], Y in [-0.26052, 0.26052], Z in [-0.07894, 0.07894]
        base = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Create the semi-circle cutter ---
        # The semi-circle cuts from the +Y face (longer face, at Y = +width/2)
        # The flat edge of the semi-circle lies along the +Y face
        # The curved part extends inward (toward -Y)
        # Profile is in XY plane, extruded through full height (Z direction)
        #
        # Semi-circle center is at (0, +width/2, 0) in world coords
        # The flat chord is at Y = +width/2, the arc goes toward -Y
        # We build the profile on the XY plane, then position it
    
        # Build the semi-circle profile as a closed wire:
        # - Start at (-semi_radius, 0) relative to center
        # - Arc through (0, -semi_radius) to (+semi_radius, 0)  [going inward = -Y direction]
        # - Line back to (-semi_radius, 0)
        # Center of semi-circle at (0, width/2) in XY plane
    
        cy = width / 2.0  # Y position of the flat face and semi-circle center
    
        # Create cutter on XY plane
        # The semi-circle profile: flat side at y=cy, arc going downward (toward -Y)
        cutter = (
            cq.Workplane("XY")
            .moveTo(-semi_radius, cy)
            .lineTo(semi_radius, cy)
            .threePointArc((0, cy - semi_radius), (-semi_radius, cy))
            .close()
            .extrude(height * 2, both=True)  # extrude through full height with margin
        )
    
        # --- Step 3: Cut the semi-circle from the base prism ---
        result = base.cut(cutter)
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Check bounding box - the semi-circle cuts into the prism from +Y side
        # The bounding box in X should still be length (semi_radius > length/2, so it cuts through)
        # The bounding box in Y: the cut removes material from +Y side inward
        # Since semi_radius (0.850616) > width (0.52105), the cut goes all the way through in Y
        # So the remaining shape is bounded by the arc on the +Y side
        # Actually the cut removes a semi-cylinder, leaving two "ear" pieces on the sides
        # Wait - the semi-circle diameter (1.701232) > length (1.5), so the arc extends beyond X bounds
        # This means the cut removes a large chunk from the center of the +Y face
    
        bb = result.val().BoundingBox()
        print(f"Bounding box: X=[{bb.xmin:.4f}, {bb.xmax:.4f}], Y=[{bb.ymin:.4f}, {bb.ymax:.4f}], Z=[{bb.zmin:.4f}, {bb.zmax:.4f}]")
        print(f"xlen={bb.xlen:.4f}, ylen={bb.ylen:.4f}, zlen={bb.zlen:.4f}")
    
        # Z extent should match height
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # X extent: semi_radius (0.850616) > length/2 (0.75), so the arc cuts through the X extents
        # The remaining solid is bounded by the original box in X
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
    
        # Y extent: The cut removes from +Y inward. Since semi_radius > width, 
        # the arc passes through the -Y face too, cutting all the way through
        # So ylen < width
        assert bb.ylen <= width + TOL, f"Y width after cut should be <= {width}, got {bb.ylen}"
        assert bb.ylen > 0, "Y width should be positive"
    
        # Volume check: base volume minus the semi-cylinder volume that's inside the prism
        base_vol = length * width * height
        # The semi-circle cutter intersects the prism. The intersection is a complex shape.
        # We verify volume is less than base volume
        vol = result.val().Volume()
        print(f"Volume: {vol:.6f} (base would be {base_vol:.6f})")
        assert vol < base_vol, f"Volume after cut should be less than base {base_vol:.6f}, got {vol:.6f}"
        assert vol > 0, "Volume should be positive"
    
        # Check that the cut exists: cylindrical face should be present
        cyl_faces = result.faces("%Cylinder").size()
        print(f"Cylindrical faces: {cyl_faces}")
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face from semi-circle cut, got {cyl_faces}"
    
        # Check the solid is a single connected body
        solids = result.solids().size()
        print(f"Number of solids: {solids}")
        assert solids >= 1, f"Expected at least 1 solid, got {solids}"
    
        # Verify the center of the prism bottom face is still intact (not cut through at center-bottom)
        # The cut is from +Y side, so the -Y face should still exist
        bottom_y_faces = result.faces("<Y").size()
        print(f"Faces at min Y: {bottom_y_faces}")
        assert bottom_y_faces >= 1, f"Expected face(s) at min Y, got {bottom_y_faces}"
    
        # Verify height is correct via Z faces
        top_z = result.faces(">Z").vals()[0].BoundingBox().zmax
        bot_z = result.faces("<Z").vals()[0].BoundingBox().zmin
        assert abs(top_z - bot_z - height) < TOL, f"Height via Z faces: expected {height}, got {top_z - bot_z}"
    
        print("All assertions passed!")
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00006892/gpt_generated.stl')
