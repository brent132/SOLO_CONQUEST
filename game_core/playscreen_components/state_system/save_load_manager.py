"""
Save/Load Manager - Centralized save and load system for essential game data

This module provides a unified interface for saving and loading:
- Game state (enemies, items, map data)
- Player inventory and character data
- Player locations across worlds
- Map-specific data and settings

RESPONSIBILITY: Centralized save/load operations
FEATURES:
- Unified save/load interface
- Essential data persistence
- Inventory persistence
- Location tracking
"""
import os
from typing import Dict, Tuple, Optional, Any
from .game_state_saver import GameStateSaver
from ..player_system.character_inventory_saver import CharacterInventorySaver
from ..player_system.player_location_tracker import PlayerLocationTracker


class SaveLoadManager:
    """Centralized manager for all save and load operations"""
    
    def __init__(self):
        """Initialize the save/load manager with all sub-systems"""
        # Initialize sub-systems
        self.game_state_saver = GameStateSaver()
        self.character_inventory_saver = CharacterInventorySaver()
        self.player_location_tracker = PlayerLocationTracker()
        
        # Save directories
        self.save_dir = "SaveData"

        # Ensure directories exist
        self._ensure_directories()
        
        # Save file paths
        self.settings_file = os.path.join(self.save_dir, "game_settings.json")
        
    def _ensure_directories(self):
        """Ensure all necessary directories exist"""
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
                
    def save_all(self, play_screen) -> Tuple[bool, str]:
        """
        Save all game data including state, inventory, location, and progress
        
        Args:
            play_screen: The PlayScreen instance containing all game data
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Save game state to map file
            state_success, state_message = self.game_state_saver.save_game_state(play_screen)
            
            # Save character inventory
            inventory_success, inventory_message = self.character_inventory_saver.save_inventory(
                play_screen.player_inventory
            )
            
            # Save player location
            if play_screen.player and play_screen.map_name:
                self.player_location_tracker.save_location(
                    play_screen.map_name,
                    play_screen.player.rect.x,
                    play_screen.player.rect.y,
                    play_screen.player.direction,
                    play_screen.player.current_health,
                    play_screen.player.shield_durability
                )
                location_success = True
                location_message = "Location saved"
            else:
                location_success = False
                location_message = "No player or map to save location"
            
            # Determine overall success
            if state_success and inventory_success and location_success:
                return True, "All game data saved successfully"
            else:
                # Collect error messages
                errors = []
                if not state_success:
                    errors.append(f"Game state: {state_message}")
                if not inventory_success:
                    errors.append(f"Inventory: {inventory_message}")
                if not location_success:
                    errors.append(f"Location: {location_message}")

                return False, "Partial save failure: " + "; ".join(errors)
                
        except Exception as e:
            return False, f"Save operation failed: {str(e)}"
    
    def load_all(self, play_screen) -> Tuple[bool, str]:
        """
        Load all game data including inventory, location, and progress
        
        Args:
            play_screen: The PlayScreen instance to load data into
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Load character inventory
            inventory_success, inventory_message = self.character_inventory_saver.load_inventory(
                play_screen.player_inventory
            )

            # Update inventory images if needed
            if inventory_success and hasattr(play_screen, '_update_inventory_images'):
                play_screen._update_inventory_images()

            # Sync HUD inventory from player inventory after loading
            if inventory_success and hasattr(play_screen, 'player_inventory') and hasattr(play_screen, 'hud'):
                play_screen._sync_player_to_hud_inventory()

            # Determine overall success
            if inventory_success:
                return True, "Game data loaded successfully"
            else:
                return False, f"Inventory load failed: {inventory_message}"
                
        except Exception as e:
            return False, f"Load operation failed: {str(e)}"
    
    def save_quick(self, play_screen) -> Tuple[bool, str]:
        """
        Quick save - saves only essential data without backup
        
        Args:
            play_screen: The PlayScreen instance
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Save game state
            state_success, state_message = self.game_state_saver.save_game_state(play_screen)
            
            # Save player location
            if play_screen.player and play_screen.map_name:
                self.player_location_tracker.save_location(
                    play_screen.map_name,
                    play_screen.player.rect.x,
                    play_screen.player.rect.y,
                    play_screen.player.direction,
                    play_screen.player.current_health,
                    play_screen.player.shield_durability
                )
                location_success = True
            else:
                location_success = False
                state_message = "No player or map for quick save"
            
            if state_success and location_success:
                return True, "Quick save completed"
            else:
                return False, f"Quick save failed: {state_message}"
                
        except Exception as e:
            return False, f"Quick save failed: {str(e)}"
    

    

    

    
    def get_player_location(self, map_name: str) -> Optional[Dict[str, Any]]:
        """Get player location for a specific map"""
        return self.player_location_tracker.get_location(map_name)
    
    def has_save_data(self) -> bool:
        """Check if any save data exists"""
        return (os.path.exists(self.character_inventory_saver.inventory_save_path) or
                os.path.exists(self.player_location_tracker.save_path))
