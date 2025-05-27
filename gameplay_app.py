"""
Gameplay module - contains the main gameplay application class
   - Initializes pygame and the game window
   - Handles events including window resizing
   - Contains the main game loop for gameplay features
   - Manages updates and drawing for gameplay screens
"""
import pygame
import sys
import os
import json

# Add game_core to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'game_core'))

# Import from game_core (IDE-friendly)
from game_core.settings import *
from game_core.menu import SplashScreen
from game_core.gameplay.settings_screen import SettingsScreen
from game_core.gameplay.play_screen import PlayScreen
from game_core.gameplay.map_select import WorldSelectScreen
from game_core.debug_utils import debug_manager
from game_core.performance_monitor import performance_monitor

class GameplayApp:
    def __init__(self):
        """Initialize the gameplay application"""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("SOLO CONQUEST - Gameplay")
        self.clock = pygame.time.Clock()
        self.running = True
        self.width = WIDTH
        self.height = HEIGHT

        # Game states for gameplay
        self.game_state = "splash"  # "splash", "playing", "settings", "map_select", "paused"

        # Initialize gameplay screens
        self.splash_screen = SplashScreen(self.width, self.height)
        self.settings_screen = SettingsScreen(self.width, self.height)
        self.map_select_screen = WorldSelectScreen(self.width, self.height)
        self.play_screen = PlayScreen(self.width, self.height)

        # Initialize debug manager
        debug_manager.enable_debug(False)  # Disable debug output for production

        # Enable specific debug categories (only used when debug is enabled)
        debug_manager.enable_category("enemy", False)
        debug_manager.enable_category("player", False)

        # Initialize performance monitor
        performance_monitor.enable(False)  # Set to True to enable performance monitoring

    def init_game(self):
        """Initialize game objects when starting the game"""
        # Removed actual game initialization
        pass

    def load_from_player_location(self):
        """Load the map from player_location.json in SaveData folder"""
        try:
            if os.path.exists("C:/Users/BR3NT3/Music/TEST/SaveData/player_location.json"):
                with open("C:/Users/BR3NT3/Music/TEST/SaveData/player_location.json", 'r') as f:
                    player_location_data = json.load(f)

                # Check if this is the new format with multiple worlds
                if isinstance(player_location_data, dict) and "worlds" in player_location_data:
                    # Get the current world
                    current_world = player_location_data.get("current_world", "main")

                    # Check if we have location data for this world
                    if current_world in player_location_data["worlds"]:
                        world_location = player_location_data["worlds"][current_world]
                        map_name = world_location.get("map_name", "")
                        folder_name = current_world
                    else:
                        # No location data for this world, use default
                        folder_name = current_world
                        map_name = ""
                else:
                    # Handle old format (backward compatibility)
                    folder_name = player_location_data.get("folder_name", "main")
                    map_name = player_location_data.get("map_name", "")

                print(f"Last folder: {folder_name}, Last map: {map_name}")

                # Check if we should load the folder's default map or the specific map
                if folder_name:
                    # First try to load a map with the same name as the folder (default map)
                    folder_default_map = folder_name
                    folder_path = os.path.join("Maps", folder_name)
                    default_map_path = os.path.join(folder_path, f"{folder_name}.json")

                    # Reset teleportation flags before loading the map
                    self.play_screen.is_teleporting = False
                    self.play_screen.teleport_info = None
                    if hasattr(self.play_screen, 'relation_handler'):
                        self.play_screen.relation_handler.current_teleport_point = None

                    # If we have a specific map name and it's in this folder, try to load it first
                    if map_name:
                        specific_map_path = os.path.join(folder_path, f"{map_name}.json")
                        if os.path.exists(specific_map_path):
                            print(f"Loading specific map: {map_name}")
                            load_success = self.play_screen.load_map(map_name)
                            if load_success:
                                self.game_state = "playing"
                                return True

                    # If no specific map or loading failed, try to load the default map
                    if os.path.exists(default_map_path):
                        print(f"Loading default map for folder {folder_name}: {folder_default_map}")
                        load_success = self.play_screen.load_map(folder_default_map)
                        if load_success:
                            # Update player location using the PlayerLocationTracker
                            if hasattr(self.play_screen, 'player_location_tracker'):
                                self.play_screen.player_location_tracker.save_location(
                                    folder_default_map,
                                    self.play_screen.player.rect.x if self.play_screen.player else 0,
                                    self.play_screen.player.rect.y if self.play_screen.player else 0,
                                    self.play_screen.player.direction if self.play_screen.player else "down",
                                    self.play_screen.player.current_health if self.play_screen.player else 100,
                                    self.play_screen.player.shield_durability if self.play_screen.player else 3,
                                    folder_name
                                )
                            self.game_state = "playing"
                            return True

                    # If both failed, try to load any map in the folder
                    if os.path.exists(folder_path) and os.path.isdir(folder_path):
                        for file_name in os.listdir(folder_path):
                            if file_name.endswith(".json"):
                                map_name = file_name[:-5]  # Remove .json extension
                                print(f"Loading first available map in folder: {map_name}")
                                load_success = self.play_screen.load_map(map_name)
                                if load_success:
                                    # Update player location using the PlayerLocationTracker
                                    if hasattr(self.play_screen, 'player_location_tracker'):
                                        self.play_screen.player_location_tracker.save_location(
                                            map_name,
                                            self.play_screen.player.rect.x if self.play_screen.player else 0,
                                            self.play_screen.player.rect.y if self.play_screen.player else 0,
                                            self.play_screen.player.direction if self.play_screen.player else "down",
                                            self.play_screen.player.current_health if self.play_screen.player else 100,
                                            self.play_screen.player.shield_durability if self.play_screen.player else 3,
                                            folder_name
                                        )
                                    self.game_state = "playing"
                                    return True
                                break

            return False
        except Exception as e:
            print(f"Error loading saved player location: {e}")
            return False

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize event
                new_width, new_height = event.size

                # Option 1: Allow any size (uncomment this line to use)
                self.width, self.height = new_width, new_height

                # Option 2: Maintain 16:9 aspect ratio (comment this out if you want free resizing)
                # self.width, self.height = maintain_aspect_ratio(new_width, new_height, 16/9)

                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)

                # Update screen dimensions based on current state
                if self.game_state == "splash":
                    self.splash_screen.resize(self.width, self.height)
                elif self.game_state == "settings":
                    self.settings_screen.resize(self.width, self.height)
                elif self.game_state == "map_select":
                    self.map_select_screen.resize(self.width, self.height)
                elif self.game_state == "playing":
                    self.play_screen.resize(self.width, self.height)

                # Also update other screens' dimensions to ensure they're ready when switched to
                if self.game_state != "splash":
                    self.splash_screen.resize(self.width, self.height)
                if self.game_state != "settings":
                    self.settings_screen.resize(self.width, self.height)
                if self.game_state != "map_select":
                    self.map_select_screen.resize(self.width, self.height)
                if self.game_state != "playing":
                    self.play_screen.resize(self.width, self.height)

            # Handle events based on current game state
            if self.game_state == "splash":
                action = self.splash_screen.handle_event(event)
                if action == "start":
                    # Always go to world selection screen when Start is clicked
                    # Refresh the world list to detect any deleted maps
                    self.map_select_screen.refresh_world_list()
                    self.game_state = "map_select"
                elif action == "settings":
                    self.game_state = "settings"
                elif action == "exit":
                    self.running = False

            elif self.game_state == "settings":
                action = self.settings_screen.handle_event(event)
                if action == "back":
                    self.game_state = "splash"

            elif self.game_state == "map_select":
                action = self.map_select_screen.handle_event(event)
                if action == "back":
                    self.game_state = "splash"
                elif isinstance(action, dict) and action.get("action") == "play":
                    # Reset teleportation flags before loading the map
                    self.play_screen.is_teleporting = False
                    self.play_screen.teleport_info = None
                    if hasattr(self.play_screen, 'relation_handler'):
                        self.play_screen.relation_handler.current_teleport_point = None

                    # Load the selected map
                    map_name = action.get("map")
                    load_success = self.play_screen.load_map(map_name)
                    if load_success:
                        self.game_state = "playing"

            elif self.game_state == "playing":
                action = self.play_screen.handle_event(event)
                if action == "back":
                    # Reset the play screen to clear any game over state
                    self.play_screen = PlayScreen(self.width, self.height)
                    # Refresh the world list to detect any deleted maps
                    self.map_select_screen.refresh_world_list()
                    self.game_state = "map_select"

    def update(self):
        """Update game logic"""
        if self.game_state == "splash":
            self.splash_screen.update()

        elif self.game_state == "settings":
            self.settings_screen.update()

        elif self.game_state == "map_select":
            self.map_select_screen.update()

        elif self.game_state == "playing":
            self.play_screen.update()

    def draw(self):
        """Draw game elements"""
        # Clear the screen
        self.screen.fill(BLACK)

        if self.game_state == "splash":
            # Draw splash screen
            self.splash_screen.draw(self.screen)

        elif self.game_state == "settings":
            # Draw settings screen
            self.settings_screen.draw(self.screen)

        elif self.game_state == "map_select":
            # Draw map selection screen
            self.map_select_screen.draw(self.screen)

        elif self.game_state == "playing":
            # Draw play screen
            self.play_screen.draw(self.screen)

        # Update the display
        pygame.display.flip()

    def run(self):
        """Main game loop"""
        while self.running:
            # Start frame timer
            performance_monitor.start_timer("frame")

            # Process events
            performance_monitor.start_timer("events")
            self.handle_events()
            performance_monitor.end_timer("events")

            # Update game state
            performance_monitor.start_timer("update")
            self.update()
            performance_monitor.end_timer("update")

            # Draw the frame
            performance_monitor.start_timer("draw")
            self.draw()
            performance_monitor.end_timer("draw")

            # Limit frame rate
            self.clock.tick(FPS)

            # End frame timer and record frame time
            frame_time = performance_monitor.end_timer("frame")
            if frame_time > 0:
                performance_monitor.record_frame_time(frame_time)

            # Log performance stats every 60 frames
            performance_monitor.increment_counter("frames")
            if performance_monitor.get_counter("frames") % 60 == 0:
                performance_monitor.log_performance_stats()

        # Quit pygame
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    print("Starting SOLO CONQUEST - Gameplay Mode...")
    app = GameplayApp()
    app.run()
