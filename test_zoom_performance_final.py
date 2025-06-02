#!/usr/bin/env python3
"""
Final zoom performance test to verify the optimizations are working.
This test measures cache performance and zoom operation smoothness.
"""
import pygame
import time
import sys
import os

# Add the game_core directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'game_core'))

from gameplay.play_screen import PlayScreen

def test_zoom_cache_performance():
    """Test the zoom cache performance improvements"""
    pygame.init()
    
    # Create a test screen
    width, height = 1280, 720
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Zoom Cache Performance Test")
    clock = pygame.time.Clock()
    
    # Create PlayScreen instance
    play_screen = PlayScreen(width, height)

    # Load the map
    play_screen.load_map("firstlevel")
    
    print("=== Zoom Cache Performance Test ===")
    print("Testing the optimized zoom-level caching system...")
    print()
    
    # Let the game initialize
    for _ in range(10):
        play_screen.update()
        play_screen.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    # Get initial cache stats
    if hasattr(play_screen, 'rendering_pipeline') and play_screen.rendering_pipeline.is_initialized:
        layer_renderer = play_screen.rendering_pipeline.layer_renderer
        initial_stats = layer_renderer.get_cache_stats()
        print(f"Initial cache state:")
        print(f"  Zoom levels cached: {initial_stats['zoom_levels_cached']}")
        print(f"  Total cached tiles: {initial_stats['total_cached_tiles']}")
        print(f"  Current zoom factor: {initial_stats['current_zoom_factor']:.1f}x")
        print()
    
    # Test zoom operations and measure performance
    zoom_times = []
    frame_times = []
    
    print("Performing zoom operations...")
    
    # Test multiple zoom operations
    for i in range(8):  # Test 8 zoom operations
        start_time = time.time()
        
        # Perform zoom operation
        if i % 4 == 0:
            play_screen.input_system.zoom_controller.zoom_in(play_screen.player.rect if play_screen.player else None)
            operation = "Zoom In"
        elif i % 4 == 1:
            play_screen.input_system.zoom_controller.zoom_in(play_screen.player.rect if play_screen.player else None)
            operation = "Zoom In"
        elif i % 4 == 2:
            play_screen.input_system.zoom_controller.zoom_out(play_screen.player.rect if play_screen.player else None)
            operation = "Zoom Out"
        else:
            play_screen.input_system.zoom_controller.reset_zoom(play_screen.player.rect if play_screen.player else None)
            operation = "Reset Zoom"
        
        zoom_time = time.time() - start_time
        zoom_times.append(zoom_time)
        
        current_zoom = play_screen.input_system.zoom_controller.zoom_factor
        print(f"  {operation} to {current_zoom:.1f}x - Time: {zoom_time*1000:.2f}ms")
        
        # Render several frames to test performance at this zoom level
        frame_start = time.time()
        for frame in range(10):  # Render 10 frames
            play_screen.update()
            play_screen.draw(screen)
            pygame.display.flip()
            clock.tick(60)
        frame_time = (time.time() - frame_start) / 10  # Average per frame
        frame_times.append(frame_time)
        
        # Get cache stats after zoom
        if hasattr(play_screen, 'rendering_pipeline') and play_screen.rendering_pipeline.is_initialized:
            stats = layer_renderer.get_cache_stats()
            print(f"    Cache: {stats['zoom_levels_cached']} levels, {stats['current_zoom_tiles']} tiles at current zoom")
    
    print()
    
    # Performance analysis
    avg_zoom_time = sum(zoom_times) * 1000 / len(zoom_times)  # Convert to ms
    max_zoom_time = max(zoom_times) * 1000
    avg_frame_time = sum(frame_times) * 1000 / len(frame_times)  # Convert to ms
    avg_fps = 1.0 / (sum(frame_times) / len(frame_times))
    
    print("=== Performance Results ===")
    print(f"Zoom Operations:")
    print(f"  Average zoom time: {avg_zoom_time:.2f}ms")
    print(f"  Maximum zoom time: {max_zoom_time:.2f}ms")
    print(f"  All zoom operations: {'✅ FAST' if max_zoom_time < 5.0 else '⚠️ SLOW'} (target: <5ms)")
    print()
    
    print(f"Rendering Performance:")
    print(f"  Average frame time: {avg_frame_time:.2f}ms")
    print(f"  Average FPS: {avg_fps:.1f}")
    print(f"  Frame performance: {'✅ EXCELLENT' if avg_fps > 55 else '✅ GOOD' if avg_fps > 45 else '⚠️ NEEDS IMPROVEMENT'}")
    print()
    
    # Final cache stats
    if hasattr(play_screen, 'rendering_pipeline') and play_screen.rendering_pipeline.is_initialized:
        final_stats = layer_renderer.get_cache_stats()
        print("Final Cache Statistics:")
        print(f"  Zoom levels cached: {final_stats['zoom_levels_cached']}")
        print(f"  Total cached tiles: {final_stats['total_cached_tiles']}")
        print(f"  Cache efficiency: {'✅ EXCELLENT' if final_stats['zoom_levels_cached'] >= 3 else '✅ GOOD'}")
        print()
    
    # Overall assessment
    zoom_performance_good = max_zoom_time < 5.0
    frame_performance_good = avg_fps > 45
    
    print("=== Overall Assessment ===")
    if zoom_performance_good and frame_performance_good:
        print("🎉 EXCELLENT: Zoom performance optimizations are working perfectly!")
        print("   - Fast zoom operations with minimal frame drops")
        print("   - Efficient tile caching across zoom levels")
        print("   - Smooth rendering performance maintained")
    elif zoom_performance_good:
        print("✅ GOOD: Zoom operations are fast, but frame rate could be improved")
    elif frame_performance_good:
        print("✅ GOOD: Frame rate is good, but zoom operations could be faster")
    else:
        print("⚠️ NEEDS IMPROVEMENT: Both zoom and frame performance need optimization")
    
    print()
    print("Test completed! Press any key to exit...")
    
    # Wait for user input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                waiting = False
    
    pygame.quit()

if __name__ == "__main__":
    test_zoom_cache_performance()
