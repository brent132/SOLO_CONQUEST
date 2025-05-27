"""
Enemy Manager - Manages all enemies in the game
"""
import pygame
from enemy_system.phantom import Phantom
from enemy_system.bomberplant import Bomberplant
from enemy_system.spinner import Spinner
from enemy_system.spider import Spider
from enemy_system.pinkslime import Pinkslime
from enemy_system.pinkbat import Pinkbat

class EnemyManager:
    """Manages all enemies in the game"""
    def __init__(self):
        self.enemies = []  # List of all enemies
        self.enemy_types = {
            "phantom": Phantom,
            "phantom_left": Phantom,
            "phantom_right": Phantom,
            "bomberplant": Bomberplant,
            "spinner": Spinner,
            "spider": Spider,  # Using the new Spider class
            "pinkslime": Pinkslime,  # Using the new Pinkslime class
            "pinkbat_left": Pinkbat,  # Using the new Pinkbat class with left direction
            "pinkbat_right": Pinkbat  # Using the new Pinkbat class with right direction
        }

        # Use the debug manager instead of a local flag
        from debug_utils import debug_manager
        self.debug_manager = debug_manager

    def add_enemy(self, enemy_type, x, y):
        """Add a new enemy of the specified type at the given position"""
        if enemy_type in self.enemy_types:
            enemy_class = self.enemy_types[enemy_type]

            # Handle special cases for enemies that need direction parameter
            if enemy_type == "pinkbat_left":
                enemy = enemy_class(x, y, direction="left")
            elif enemy_type == "pinkbat_right":
                enemy = enemy_class(x, y, direction="right")
            else:
                enemy = enemy_class(x, y)

            # Set initial direction based on enemy type
            if enemy_type == "phantom_left":
                enemy.direction = "left"
            elif enemy_type == "phantom_right":
                enemy.direction = "right"

            # Convert grid coordinates to pixel coordinates
            # The grid cell size is 16 pixels
            # For enemies placed in the editor, x and y are grid coordinates
            pixel_x = x * 16
            pixel_y = y * 16

            # Set the rect position
            enemy.rect.x = pixel_x
            enemy.rect.y = pixel_y

            # Initialize float position for smooth movement if the enemy has these attributes
            if hasattr(enemy, 'float_x') and hasattr(enemy, 'float_y'):
                enemy.float_x = float(pixel_x)
                enemy.float_y = float(pixel_y)

            self.enemies.append(enemy)
            return enemy
        else:
            self.debug_manager.log(f"Warning: Unknown enemy type '{enemy_type}'", "enemy")
            return None

    def load_enemies_from_map(self, map_data):
        """Load enemies from map data"""
        # Clear existing enemies
        self.debug_manager.log(f"Clearing {len(self.enemies)} existing enemies", "enemy")
        self.enemies = []

        # Check if map has enemy data
        if "enemies" not in map_data:
            self.debug_manager.log("No enemies found in map data", "map")
            return

        self.debug_manager.log(f"Loading {len(map_data['enemies'])} enemies from map data", "map")

        # Track enemy positions to avoid duplicates
        enemy_positions = set()

        # Load each enemy
        for enemy_data in map_data["enemies"]:
            enemy_type = enemy_data.get("type", "phantom")
            x = enemy_data.get("x", 0)
            y = enemy_data.get("y", 0)

            # Check if we already have an enemy at this position
            position_key = (x, y)
            if position_key not in enemy_positions:
                enemy_positions.add(position_key)
                self.debug_manager.log(f"Adding enemy of type {enemy_type} at position ({x}, {y})", "enemy")
                enemy = self.add_enemy(enemy_type, x, y)
                if enemy:
                    self.debug_manager.log(f"Successfully added {enemy_type} at ({x}, {y})", "enemy")
                else:
                    self.debug_manager.log(f"Failed to add {enemy_type} at ({x}, {y})", "enemy")
            else:
                self.debug_manager.log(f"Skipping duplicate {enemy_type} at position ({x}, {y})", "enemy")

    def update(self, player_x, player_y, collision_handler=None, tile_mapping=None, map_data=None):
        """Update all enemies"""
        if not self.enemies:
            return

        # Create a list of enemies to remove (those that have completed death animation)
        enemies_to_remove = []

        for enemy in self.enemies:
            # Update enemy with collision data
            enemy.update(player_x, player_y, collision_handler, tile_mapping, map_data)

            # Check if enemy is dead and should be removed
            if hasattr(enemy, 'is_dead') and enemy.is_dead:
                self.debug_manager.log(f"Marking {enemy.enemy_type} at ({enemy.rect.x}, {enemy.rect.y}) for removal", "enemy")
                enemies_to_remove.append(enemy)

        # Remove dead enemies
        for enemy in enemies_to_remove:
            if enemy in self.enemies:
                self.debug_manager.log(f"Removing {enemy.enemy_type} at ({enemy.rect.x}, {enemy.rect.y})", "enemy")
                self.enemies.remove(enemy)

    def check_player_collisions(self, player, collision_handler=None, tile_mapping=None, map_data=None):
        """Check for collisions between enemies and the player, and apply effects"""
        if not self.enemies or not player:
            return

        for enemy in self.enemies:
            # Skip dead enemies
            if hasattr(enemy, 'is_dead') and enemy.is_dead:
                continue

            # Check if this enemy type has a knockback method
            if hasattr(enemy, 'apply_knockback_to_player'):
                # Apply knockback if colliding, passing collision data if available
                enemy.apply_knockback_to_player(
                    player,
                    collision_handler=collision_handler,
                    tile_mapping=tile_mapping,
                    map_data=map_data
                )



    def check_player_attacks(self, player, collision_handler=None, tile_mapping=None, map_data=None):
        """Check if player's attack hits any enemies"""
        if not self.enemies or not player or not player.is_attacking:
            return

        # Only check for hits on the first frame of the attack animation
        # This prevents multiple hits from a single attack
        if not hasattr(player, 'attack_frame') or player.attack_frame > 0:
            return

        # Get player's attack hitbox
        attack_rect = self.get_player_attack_hitbox(player)
        if not attack_rect:
            return

        # Check each enemy for collision with attack hitbox
        for enemy in self.enemies:
            # Skip dead or dying enemies
            if hasattr(enemy, 'is_dead') and enemy.is_dead:
                continue
            if hasattr(enemy, 'is_dying') and enemy.is_dying:
                continue

            # Check if enemy has take_damage method
            if hasattr(enemy, 'take_damage') and attack_rect.colliderect(enemy.rect):
                # Calculate knockback direction (away from player)
                knockback_x = enemy.rect.centerx - player.rect.centerx
                knockback_y = enemy.rect.centery - player.rect.centery

                # Apply damage to the enemy with knockback direction
                # Apply 7 damage specifically to Spinner entities, 30 damage to other enemies
                damage = 7 if enemy.enemy_type == "spinner" else 30
                enemy.take_damage(damage, knockback_x, knockback_y, collision_handler, tile_mapping, map_data)

                # Debug output
                self.debug_manager.log(f"Player hit enemy! Damage: {damage}, Current health: {enemy.current_health}/{enemy.max_health}", "enemy")
                self.debug_manager.log(f"Applied knockback: dx={knockback_x}, dy={knockback_y}", "enemy")

    def get_player_attack_hitbox(self, player):
        """Calculate the player's attack hitbox based on direction"""
        if not player.is_attacking:
            return None

        # Get player position and size
        player_x = player.rect.x
        player_y = player.rect.y
        player_width = player.rect.width
        player_height = player.rect.height

        # Create attack hitbox based on direction
        # The hitbox extends in the direction the player is facing
        attack_width = 32  # Width of attack hitbox
        attack_height = 32  # Height of attack hitbox

        if player.direction == "right":
            # Attack to the right
            attack_rect = pygame.Rect(
                player_x + player_width - 8,  # Slightly overlapping with player
                player_y - 8,  # Extend slightly above player
                attack_width,
                attack_height
            )
        elif player.direction == "left":
            # Attack to the left
            attack_rect = pygame.Rect(
                player_x - attack_width + 8,  # Slightly overlapping with player
                player_y - 8,  # Extend slightly above player
                attack_width,
                attack_height
            )
        elif player.direction == "up":
            # Attack upward
            attack_rect = pygame.Rect(
                player_x - 8,  # Extend slightly to both sides
                player_y - attack_height + 8,  # Slightly overlapping with player
                attack_width,
                attack_height
            )
        else:  # "down" or default
            # Attack downward
            attack_rect = pygame.Rect(
                player_x - 8,  # Extend slightly to both sides
                player_y + player_height - 8,  # Slightly overlapping with player
                attack_width,
                attack_height
            )

        return attack_rect

    def draw(self, surface, camera_x=0, camera_y=0):
        """Draw all enemies"""
        for enemy in self.enemies:
            enemy.draw(surface, camera_x, camera_y)
