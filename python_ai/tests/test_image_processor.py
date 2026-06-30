"""
Unit tests for ImageProcessor
"""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.core.image_processor import ImageProcessor


def test_image_operations():
    """Test image processing operations"""
    print("\n" + "="*60)
    print("TEST: Image Processing Operations")
    print("="*60)
    
    try:
        processor = ImageProcessor()
        
        # Create test image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        test_image[:] = (100, 150, 200)
        print("✓ Test image created: 640x480")
        
        # Test resize
        print("\n1. Testing resize...")
        resized = processor.resize(test_image, width=320)
        assert resized.shape[1] == 320, "Width should be 320"
        assert resized.shape[0] == 240, "Height should be 240 (aspect maintained)"
        print(f"✓ Resized: {test_image.shape} → {resized.shape}")
        
        # Test crop
        print("\n2. Testing crop...")
        cropped = processor.crop(test_image, 50, 50, 200, 100)
        assert cropped.shape == (100, 200, 3), "Crop dimensions should match"
        print(f"✓ Cropped: {cropped.shape}")
        
        # Test rotate
        print("\n3. Testing rotate...")
        rotated = processor.rotate(test_image, 45)
        assert rotated.shape == test_image.shape, "Rotated should maintain dimensions"
        print(f"✓ Rotated 45°: {rotated.shape}")
        
        # Test flip
        print("\n4. Testing flip...")
        flipped = processor.flip(test_image, mode="horizontal")
        assert flipped.shape == test_image.shape, "Flipped should maintain dimensions"
        print(f"✓ Flipped horizontally: {flipped.shape}")
        
        # Test grayscale
        print("\n5. Testing grayscale conversion...")
        gray = processor.to_grayscale(test_image)
        assert len(gray.shape) == 2, "Grayscale should be 2D"
        print(f"✓ Converted to grayscale: {gray.shape}")
        
        # Test brightness adjustment
        print("\n6. Testing brightness adjustment...")
        brighter = processor.adjust_brightness(test_image, 1.5)
        assert brighter.shape == test_image.shape, "Shape should be maintained"
        print(f"✓ Brightness adjusted: {brighter.shape}")
        
        # Test contrast adjustment
        print("\n7. Testing contrast adjustment...")
        contrasted = processor.adjust_contrast(test_image, 1.2)
        assert contrasted.shape == test_image.shape, "Shape should be maintained"
        print(f"✓ Contrast adjusted: {contrasted.shape}")
        
        # Test blur
        print("\n8. Testing blur...")
        blurred = processor.blur(test_image, kernel_size=5)
        assert blurred.shape == test_image.shape, "Shape should be maintained"
        print(f"✓ Blurred: {blurred.shape}")
        
        # Test sharpen
        print("\n9. Testing sharpen...")
        sharpened = processor.sharpen(test_image)
        assert sharpened.shape == test_image.shape, "Shape should be maintained"
        print(f"✓ Sharpened: {sharpened.shape}")
        
        # Test drawing
        print("\n10. Testing draw operations...")
        with_rect = processor.draw_rectangle(test_image, 50, 50, 200, 100)
        with_text = processor.draw_text(with_rect, "TraffiSight", 60, 90)
        assert with_text.shape == test_image.shape, "Shape should be maintained"
        print(f"✓ Drew rectangle and text: {with_text.shape}")
        
        # Test save
        print("\n11. Testing save image...")
        output_path = Path("./output/test_processed.jpg")
        success = processor.save_image(with_text, output_path)
        assert success, "Save should succeed"
        assert output_path.exists(), "Output file should exist"
        print(f"✓ Image saved: {output_path}")
        
        # Cleanup
        if output_path.exists():
            output_path.unlink()
        
        print("\n✅ ALL IMAGE PROCESSOR TESTS PASSED!")
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_image_operations()
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Image Processor Test: {'✅ PASSED' if success else '❌ FAILED'}")
    print("="*60)
    
    sys.exit(0 if success else 1)
