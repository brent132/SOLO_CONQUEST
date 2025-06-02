#!/usr/bin/env python3
"""
Performance test for the optimized rendering pipeline zoom operations.
Tests the frame rate during zoom operations to verify performance improvements.
"""
import pygame
import time
import sys
import os

# Add the game_core directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'game_core'))

from gameplay.play_screen import PlayScreen

def test_zoom_performance():
    """Test zoom performance with the optimized rendering pipeline"""
    pygame.init()
    
    # Create a test screen
    width, height = 1280, 720
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Zoom Performance Test - Optimized Rendering Pipeline")
    clock = pygame.time.Clock()
    
    # Create PlayScreen instance
    play_screen = PlayScreen(width, height, "firstlevel")
    
    # Performance tracking
    frame_times = []
    zoom_frame_times = []
    test_duration = 10.0  # Test for 10 seconds
    zoom_test_duration = 5.0  # Test zoom operations for 5 seconds
    
    print("Starting zoom performance test...")
    print("Phase 1: Baseline performance (no zoom changes)")
    
    # Phase 1: Baseline performance test
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < test_duration:
        frame_start = time.time()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        # Update and draw
        play_screen.update()
        play_screen.draw(screen)
        pygame.display.flip()
        
        # Track frame time
        frame_time = time.time() - frame_start
        frame_times.append(frame_time)
        frame_count += 1
        
        clock.tick(60)  # Target 60 FPS
    
    # Calculate baseline stats
    baseline_avg_fps = len(frame_times) / test_duration
    baseline_avg_frame_time = sum(frame_times) / len(frame_times)
    baseline_min_fps = 1.0 / max(frame_times) if frame_times else 0
    baseline_max_fps = 1.0 / min(frame_times) if frame_times else 0
    
    print(f"Baseline Results:")
    print(f"  Average FPS: {baseline_avg_fps:.1f}")
    print(f"  Average frame time: {baseline_avg_frame_time*1000:.2f}ms")
    print(f"  Min FPS: {baseline_min_fps:.1f}")
    print(f"  Max FPS: {baseline_max_fps:.1f}")
    print()
    
    # Phase 2: Zoom performance test
    print("Phase 2: Zoom operation performance")
    
    zoom_start_time = time.time()
    zoom_frame_count = 0
    zoom_change_count = 0
    last_zoom_change = 0
    
    while time.time() - zoom_start_time < zoom_test_duration:
        frame_start = time.time()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        # Simulate zoom operations every 30 frames (0.5 seconds at 60 FPS)
        if zoom_frame_count - last_zoom_change >= 30:
            if zoom_change_count % 4 == 0:
                # Zoom in
                play_screen.input_system.zoom_controller.zoom_in(play_screen.player.rect if play_screen.player else None)
                print(f"  Zoomed in to {play_screen.input_system.zoom_controller.zoom_factor:.1f}x")
            elif zoom_change_count % 4 == 1:
                # Zoom in more
                play_screen.input_system.zoom_controller.zoom_in(play_screen.player.rect if play_screen.player else None)
                print(f"  Zoomed in to {play_screen.input_system.zoom_controller.zoom_factor:.1f}x")
            elif zoom_change_count % 4 == 2:
                # Zoom out
                play_screen.input_system.zoom_controller.zoom_out(play_screen.player.rect if play_screen.player else None)
                print(f"  Zoomed out to {play_screen.input_system.zoom_controller.zoom_factor:.1f}x")
            else:
                # Reset zoom
                play_screen.input_system.zoom_controller.reset_zoom(play_screen.player.rect if play_screen.player else None)
                print(f"  Reset zoom to {play_screen.input_system.zoom_controller.zoom_factor:.1f}x")
            
            zoom_change_count += 1
            last_zoom_change = zoom_frame_count
        
        # Update and draw
        play_screen.update()
        play_screen.draw(screen)
        pygame.display.flip()
        
        # Track frame time
        frame_time = time.time() - frame_start
        zoom_frame_times.append(frame_time)
        zoom_frame_count += 1
        
        clock.tick(60)  # Target 60 FPS
    
    # Calculate zoom performance stats
    zoom_avg_fps = len(zoom_frame_times) / zoom_test_duration
    zoom_avg_frame_time = sum(zoom_frame_times) / len(zoom_frame_times)
    zoom_min_fps = 1.0 / max(zoom_frame_times) if zoom_frame_times else 0
    zoom_max_fps = 1.0 / min(zoom_frame_times) if zoom_frame_times else 0
    
    print(f"\nZoom Performance Results:")
    print(f"  Average FPS: {zoom_avg_fps:.1f}")
    print(f"  Average frame time: {zoom_avg_frame_time*1000:.2f}ms")
    print(f"  Min FPS: {zoom_min_fps:.1f}")
    print(f"  Max FPS: {zoom_max_fps:.1f}")
    print(f"  Zoom changes performed: {zoom_change_count}")
    print()
    
    # Performance comparison
    fps_difference = zoom_avg_fps - baseline_avg_fps
    frame_time_difference = (zoom_avg_frame_time - baseline_avg_frame_time) * 1000
    
    print("Performance Comparison:")
    print(f"  FPS difference: {fps_difference:+.1f} ({fps_difference/baseline_avg_fps*100:+.1f}%)")
    print(f"  Frame time difference: {frame_time_difference:+.2f}ms")
    
    if abs(fps_difference) < 2.0:
        print("  ✅ EXCELLENT: Zoom operations have minimal performance impact!")
    elif abs(fps_difference) < 5.0:
        print("  ✅ GOOD: Zoom operations have acceptable performance impact.")
    elif abs(fps_difference) < 10.0:
        print("  ⚠️  MODERATE: Zoom operations have noticeable performance impact.")
    else:
        print("  ❌ POOR: Zoom operations have significant performance impact.")
    
    # Frame drop analysis
    baseline_frame_drops = sum(1 for ft in frame_times if ft > 1.0/50)  # Frames slower than 50 FPS
    zoom_frame_drops = sum(1 for ft in zoom_frame_times if ft > 1.0/50)
    
    print(f"\nFrame Drop Analysis (frames slower than 50 FPS):")
    print(f"  Baseline frame drops: {baseline_frame_drops}/{len(frame_times)} ({baseline_frame_drops/len(frame_times)*100:.1f}%)")
    print(f"  Zoom frame drops: {zoom_frame_drops}/{len(zoom_frame_times)} ({zoom_frame_drops/len(zoom_frame_times)*100:.1f}%)")
    
    if zoom_frame_drops <= baseline_frame_drops * 1.2:
        print("  ✅ Frame drops are within acceptable range during zoom operations.")
    else:
        print("  ⚠️  Increased frame drops detected during zoom operations.")
    
    print("\nTest completed! Press any key to exit...")
    
    # Wait for user input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                waiting = False
    
    pygame.quit()

if __name__ == "__main__":
    test_zoom_performance()
