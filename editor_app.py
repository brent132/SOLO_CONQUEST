"""
Editor module - contains the main editor application class
   - Initializes pygame and the editor window
   - Handles events including window resizing
   - Contains the main editor loop for map editing features
   - Manages updates and drawing for editor screens
"""
import pygame
import sys
import os

# Add game_core to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'game_core'))

# Import from game_core (IDE-friendly)
from game_core.settings import *
from game_core.edit_mode import EditScreen
from game_core.debug_utils import debug_manager
from game_core.performance_monitor import performance_monitor
from game_core.menu import Button
from game_core.base_screen import BaseScreen

class EditorSplashScreen(BaseScreen):
    """Custom splash screen for editor mode with only relevant buttons"""
    def __init__(self, screen_width, screen_height):
        # Initialize the base screen
        super().__init__(screen_width, screen_height)
        self.active = True

        # ===== BACKGROUND ANIMATION SETTINGS =====
        # Load background image
        self.background_path = "Menu Assets/Menu-Background.png"
        self.background = pygame.image.load(self.background_path).convert_alpha()
        # Make background wider for scrolling effect (2x width)
        self.bg_width = self.width * 2
        self.bg_height = self.height
        self.background = pygame.transform.scale(self.background, (self.bg_width, self.bg_height))
        # Background animation variables
        self.bg_x = 0  # Starting x position
        self.bg_scroll_speed = 0.2  # Pixels per frame - lower = slower, smoother scrolling

        # Button configuration - only editor and exit buttons
        self.button_paths = {
            'edit': "Menu Assets/Edit-Button.png",
            'exit': "Menu Assets/Exit-Button.png"
        }

        # Button scaling factor
        button_scale = 1.0

        # Load button dimensions from the first image to calculate spacing
        temp_img = pygame.image.load(self.button_paths['edit'])
        original_width = temp_img.get_width()
        original_height = temp_img.get_height()
        button_width = int(original_width * button_scale)
        button_height = int(original_height * button_scale)
        button_spacing = 20

        # ===== TITLE ANIMATION SETTINGS =====
        # Load game title image
        self.title_path = "Menu Assets/Game-Title.png"
        self.title_image = pygame.image.load(self.title_path).convert_alpha()

        # Title size
        title_scale = 1.0
        title_width = int(self.title_image.get_width() * title_scale)
        title_height = int(self.title_image.get_height() * title_scale)
        self.title_image = pygame.transform.scale(self.title_image, (title_width, title_height))

        # Title "floating" animation (up and down movement)
        self.title_float_speed = 5.0
        self.title_float_range = 5.0
        self.title_float_offset = 0

        self.title_rect = self.title_image.get_rect()

        # Position buttons and title
        title_y = self.height // 4 - self.title_rect.height // 2
        start_y = self.height // 2 - 25  # Center the two buttons

        # Center title
        self.title_rect.centerx = self.width // 2
        self.title_rect.y = title_y

        # Create buttons - only edit and exit
        center_x = self.width // 2 - button_width // 2
        self.buttons = {
            'edit': Button(center_x, start_y, self.button_paths['edit'], button_scale),
            'exit': Button(center_x, start_y + button_height + button_spacing,
                          self.button_paths['exit'], button_scale)
        }

    def handle_event(self, event):
        """Handle events for the editor splash screen"""
        mouse_pos = pygame.mouse.get_pos()

        # Handle common events (back and reload buttons)
        result = self.handle_common_events(event, mouse_pos)
        if result:
            return result

        # Update all buttons
        for button in self.buttons.values():
            button.update(mouse_pos)

        # Check for button clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttons['edit'].is_clicked(event):
                debug_manager.log("Edit Mode clicked", "menu")
                return "edit"

            elif self.buttons['exit'].is_clicked(event):
                debug_manager.log("Exit clicked", "menu")
                return "exit"

        return None

    def update(self):
        """Update splash screen logic and animations"""
        import math
        # ===== BACKGROUND SCROLLING ANIMATION =====
        # Update background position for scrolling effect
        self.bg_x -= self.bg_scroll_speed
        # Reset position when the first image is completely off-screen
        if self.bg_x <= -self.width:
            self.bg_x = 0

        # ===== TITLE FLOATING ANIMATION =====
        # Update title position for up and down floating effect
        self.title_float_offset = math.sin(pygame.time.get_ticks() * 0.001 * self.title_float_speed) * self.title_float_range

    def draw(self, surface):
        """Draw the splash screen with animations"""
        # ===== DRAW SCROLLING BACKGROUND =====
        # Draw background image twice side by side for seamless scrolling
        surface.blit(self.background, (int(self.bg_x), 0))
        surface.blit(self.background, (int(self.bg_x) + self.bg_width, 0))

        # ===== DRAW ANIMATED TITLE =====
        # Apply floating animation to title position
        title_pos = self.title_rect.copy()
        exact_y = title_pos.y + self.title_float_offset
        title_pos.y = int(exact_y)
        surface.blit(self.title_image, title_pos)

        # ===== DRAW BUTTONS =====
        # Draw all buttons
        for button in self.buttons.values():
            button.draw(surface)

        # Draw common elements (back and reload buttons)
        self.draw_common_elements(surface)

    def resize(self, new_width, new_height):
        """Handle screen resize"""
        # Call the base class resize method
        super().resize(new_width, new_height)

        # Resize background image for scrolling
        self.bg_width = self.width * 2
        self.bg_height = self.height
        self.background = pygame.image.load(self.background_path).convert_alpha()
        self.background = pygame.transform.scale(self.background, (self.bg_width, self.bg_height))

        # Get button dimensions from the first button
        button_width = self.buttons['edit'].rect.width
        button_height = self.buttons['edit'].rect.height
        button_spacing = 20

        # Recalculate positions
        title_y = self.height // 4 - self.title_rect.height // 2
        start_y = self.height // 2 - 25

        # Center buttons horizontally
        center_x = self.width // 2 - button_width // 2

        # Update button positions
        self.buttons['edit'].rect.topleft = (center_x, start_y)
        self.buttons['exit'].rect.topleft = (center_x, start_y + button_height + button_spacing)

        # Update title position
        self.title_rect.centerx = self.width // 2
        self.title_rect.y = title_y


class EditorApp:
    def __init__(self):
        """Initialize the editor application"""
        pygame.init()

        # Try to enable VSync for consistent frame rate
        if ENABLE_VSYNC:
            try:
                # Set VSync hint before creating display
                import os
                os.environ['SDL_HINT_RENDER_VSYNC'] = '1'
                self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                print("VSync enabled for consistent 60 FPS")
            except:
                # Fallback without VSync
                self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                print("VSync not available, using software frame limiting")
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            print("VSync disabled, using software frame limiting")

        pygame.display.set_caption("SOLO CONQUEST - Map Editor")
        self.clock = pygame.time.Clock()
        self.running = True
        self.width = WIDTH
        self.height = HEIGHT

        # Frame rate control
        self.target_fps = FPS
        self.frame_time_target = 1.0 / self.target_fps  # Target time per frame (1/60 = 0.0167 seconds)

        # Frame rate monitoring
        self.fps_counter = 0
        self.fps_timer = 0
        self.current_fps = 0

        # Game states for editor
        self.game_state = "splash"  # "splash", "edit"

        # Initialize editor screens
        self.splash_screen = EditorSplashScreen(self.width, self.height)
        self.edit_screen = EditScreen(self.width, self.height)

        # Initialize debug manager
        debug_manager.enable_debug(False)  # Disable debug output for production

        # Initialize performance monitor
        performance_monitor.enable(False)  # Set to True to enable performance monitoring

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize event
                new_width, new_height = event.size

                # Allow any size
                self.width, self.height = new_width, new_height

                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)

                # Update screen dimensions based on current state
                if self.game_state == "splash":
                    self.splash_screen.resize(self.width, self.height)
                elif self.game_state == "edit":
                    self.edit_screen.resize(self.width, self.height)

                # Also update other screens' dimensions to ensure they're ready when switched to
                if self.game_state != "splash":
                    self.splash_screen.resize(self.width, self.height)
                if self.game_state != "edit":
                    self.edit_screen.resize(self.width, self.height)

            # Handle events based on current game state
            if self.game_state == "splash":
                action = self.splash_screen.handle_event(event)
                if action == "edit":
                    self.game_state = "edit"
                elif action == "exit":
                    self.running = False

            elif self.game_state == "edit":
                action = self.edit_screen.handle_event(event)
                if action == "back":
                    self.game_state = "splash"

    def update(self):
        """Update editor logic"""
        if self.game_state == "splash":
            self.splash_screen.update()

        elif self.game_state == "edit":
            self.edit_screen.update()

    def draw(self):
        """Draw editor elements"""
        # Clear the screen
        self.screen.fill(BLACK)

        if self.game_state == "splash":
            # Draw splash screen
            self.splash_screen.draw(self.screen)

        elif self.game_state == "edit":
            # Draw edit mode screen
            self.edit_screen.draw(self.screen)

        # Update the display
        pygame.display.flip()

    def run(self):
        """Main editor loop with precise 60 FPS limiting"""
        import time

        while self.running:
            frame_start_time = time.time()

            # Start frame timer
            performance_monitor.start_timer("frame")

            # Process events
            performance_monitor.start_timer("events")
            self.handle_events()
            performance_monitor.end_timer("events")

            # Update editor state
            performance_monitor.start_timer("update")
            self.update()
            performance_monitor.end_timer("update")

            # Draw the frame
            performance_monitor.start_timer("draw")
            self.draw()
            performance_monitor.end_timer("draw")

            # Precise frame rate limiting
            self._limit_frame_rate(frame_start_time)

            # End frame timer and record frame time
            frame_time = performance_monitor.end_timer("frame")
            if frame_time > 0:
                performance_monitor.record_frame_time(frame_time)

            # Update FPS monitoring
            self._update_fps_monitoring()

            # Log performance stats every 60 frames

        # Quit pygame
        pygame.quit()
        sys.exit()

    def _limit_frame_rate(self, frame_start_time):
        """Implement precise frame rate limiting to ensure consistent 60 FPS"""
        import time

        # Calculate how long this frame took
        frame_elapsed = time.time() - frame_start_time

        # Calculate how long we need to wait to maintain target FPS
        sleep_time = self.frame_time_target - frame_elapsed

        if sleep_time > 0:
            # Use pygame's clock for the main delay (more accurate for games)
            self.clock.tick(self.target_fps)

            # Add a small additional sleep if needed for extra precision
            remaining_time = self.frame_time_target - (time.time() - frame_start_time)
            if remaining_time > 0.001:  # Only sleep if more than 1ms remaining
                time.sleep(remaining_time * 0.9)  # Sleep for 90% of remaining time to avoid overshooting
        else:
            # Frame took longer than target, just tick the clock
            self.clock.tick(self.target_fps)

    def _update_fps_monitoring(self):
        """Update FPS monitoring to track actual frame rate"""
        import time

        current_time = time.time()
        self.fps_counter += 1

        # Update FPS every second
        if current_time - self.fps_timer >= 1.0:
            self.current_fps = self.fps_counter / (current_time - self.fps_timer)
            self.fps_counter = 0
            self.fps_timer = current_time


if __name__ == "__main__":
    print("Starting SOLO CONQUEST - Map Editor...")
    app = EditorApp()
    app.run()
