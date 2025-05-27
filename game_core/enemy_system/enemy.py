"""
Base Enemy class - provides common functionality for all enemy types
"""
import pygame
import os

class Enemy(pygame.sprite.Sprite):
    """Base class for all enemies in the game"""
    def __init__(self, x, y, enemy_type="base"):
        super().__init__()
        self.x = x
        self.y = y
        self.width = 16  # Standard size for enemy sprite
        self.height = 16
        self.enemy_type = enemy_type

        # Animation variables
        self.direction = "right"  # Current facing direction
        self.state = "idle"  # Current animation state (idle, run)
        self.frame = 0  # Current animation frame
        self.animation_speed = 0.1  # Animation speed (frames per update)
        self.animation_timer = 0  # Timer for animation updates

        # Movement variables
        self.velocity = [0, 0]
        self.speed = 0.8  # Base movement speed

        # Sprites dictionary - will be populated by subclasses
        self.sprites = {}

        # Default image and rect
        self.image = pygame.Surface((16, 16))
        self.image.fill((255, 0, 0))  # Red placeholder
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # Debug flag
        self.debug_mode = False

        # Knockback properties
        self.knockback_strength = 4.0  # Strength of knockback when hit by player
        self.is_knocked_back = False
        self.knockback_timer = 0
        self.knockback_duration = 15  # Frames to show knockback effect
        self.knockback_velocity = [0, 0]  # Direction and speed of knockback

    def load_animation(self, anim_type, direction, folder_path):
        """Load animation frames from a folder"""
        anim_key = f"{anim_type}_{direction}"
        self.sprites[anim_key] = []

        # Check if the animation directory exists
        if not os.path.exists(folder_path):
            print(f"Warning: Animation directory not found: {folder_path}")
            return

        # Find all PNG files in the directory
        frame_files = []
        try:
            for file in os.listdir(folder_path):
                if file.startswith("tile") and file.endswith(".png"):
                    frame_files.append(file)

            # Sort the files to ensure correct order
            frame_files.sort()
        except Exception as e:
            print(f"Error reading directory {folder_path}: {e}")
            return

        # Load each frame
        for file in frame_files:
            try:
                img_path = os.path.join(folder_path, file)
                img = pygame.image.load(img_path).convert_alpha()
                self.sprites[anim_key].append(img)
            except Exception as e:
                print(f"Error loading sprite {img_path}: {e}")

    def update_animation(self):
        """Update the enemy's animation frame"""
        # Determine the animation key based on state and direction
        current_animation_key = f"{self.state}_{self.direction}"

        # Check if the animation exists
        if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
            # If we don't have the specific animation, try to find a fallback
            if self.state != "idle":
                # Try idle animation for that direction
                idle_key = f"idle_{self.direction}"
                if idle_key in self.sprites and self.sprites[idle_key]:
                    current_animation_key = idle_key
                else:
                    # Try any idle animation
                    for key in self.sprites.keys():
                        if key.startswith("idle_") and self.sprites[key]:
                            current_animation_key = key
                            break
            else:
                # Try any animation
                for key in self.sprites.keys():
                    if self.sprites[key]:
                        current_animation_key = key
                        break

        # If we still don't have a valid animation, return
        if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
            return

        # Make sure we have frames in this animation
        if len(self.sprites[current_animation_key]) == 0:
            return

        # Update animation timer
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.frame = (self.frame + 1) % len(self.sprites[current_animation_key])

        # Make sure frame index is valid
        if self.frame >= len(self.sprites[current_animation_key]):
            self.frame = 0

        # Update image
        self.image = self.sprites[current_animation_key][self.frame]

        # Update rect position
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center

    def move_towards_player(self, player_x, player_y):
        """Move the enemy towards the player using cardinal directions"""
        # Use debug manager instead of print statements
        if self.debug_mode:
            from debug_utils import debug_manager
            debug_manager.log(f"Enemy at ({self.rect.x}, {self.rect.y}), Player at ({player_x}, {player_y})", "enemy")

        # Calculate direction to player
        dx = player_x - self.rect.centerx
        dy = player_y - self.rect.centery

        # Determine which direction to move (up, down, left, right)
        # We'll move in one direction at a time, prioritizing the larger distance
        if abs(dx) > abs(dy):
            # Move horizontally
            self.velocity[0] = self.speed if dx > 0 else -self.speed
            self.velocity[1] = 0
            self.direction = "right" if dx > 0 else "left"
        else:
            # Move vertically
            self.velocity[0] = 0
            self.velocity[1] = self.speed if dy > 0 else -self.speed
            # Keep the left/right direction for animation purposes
            if self.direction not in ["left", "right"]:
                self.direction = "right"  # Default direction

        # Set animation state based on movement
        if self.velocity[0] != 0 or self.velocity[1] != 0:
            self.state = "run"
        else:
            self.state = "idle"

    def apply_knockback(self, direction_x, direction_y, collision_handler=None, tile_mapping=None, map_data=None):
        """Apply knockback effect to the enemy

        Args:
            direction_x (float): X component of knockback direction
            direction_y (float): Y component of knockback direction
            collision_handler: Optional collision handler for wall detection
            tile_mapping: Optional tile mapping for collision detection
            map_data: Optional map data for collision detection
        """
        # Only apply knockback if not already knocked back
        if not self.is_knocked_back:
            self.is_knocked_back = True
            self.knockback_timer = self.knockback_duration

            # Normalize the direction
            distance = ((direction_x ** 2) + (direction_y ** 2)) ** 0.5
            if distance > 0:
                # Set knockback velocity based on direction and strength
                self.knockback_velocity[0] = (direction_x / distance) * self.knockback_strength
                self.knockback_velocity[1] = (direction_y / distance) * self.knockback_strength

                # Set direction for animation
                if abs(direction_x) > abs(direction_y):
                    self.direction = "right" if direction_x > 0 else "left"

                # Set state to hit if available
                if f"hit_{self.direction}" in self.sprites:
                    self.state = "hit"
                    self.frame = 0
                    self.animation_timer = 0

            if self.debug_mode:
                from debug_utils import debug_manager
                debug_manager.log(f"Enemy knockback applied: dx={direction_x:.2f}, dy={direction_y:.2f}", "enemy")

            return True
        return False

    def update(self, player_x, player_y, collision_handler=None, tile_mapping=None, map_data=None):
        """Update enemy position and animation"""
        # Update knockback timer if active
        if self.is_knocked_back:
            self.knockback_timer -= 1
            if self.knockback_timer <= 0:
                self.is_knocked_back = False
                self.knockback_velocity = [0, 0]
                self.state = "idle"
            else:
                # Store original position for collision detection
                original_x = self.rect.x
                original_y = self.rect.y

                # Apply knockback movement
                self.rect.x += self.knockback_velocity[0]
                self.rect.y += self.knockback_velocity[1]

                # Check for collisions after knockback if collision data is available
                if collision_handler and tile_mapping and map_data:
                    if collision_handler.check_collision(self.rect, tile_mapping, map_data):
                        # Collision detected, revert to original position
                        self.rect.x = original_x
                        self.rect.y = original_y

                        # Stop knockback
                        self.knockback_velocity = [0, 0]
                        self.is_knocked_back = False
                        self.state = "idle"
                        return

                # Gradually reduce knockback effect
                self.knockback_velocity[0] *= 0.9
                self.knockback_velocity[1] *= 0.9
        else:
            # Normal movement when not knocked back
            self.move_towards_player(player_x, player_y)

            # Update position based on velocity
            self.rect.x += self.velocity[0]
            self.rect.y += self.velocity[1]

        # Update animation
        self.update_animation()

    def take_damage(self, damage_amount=10, knockback_x=0, knockback_y=0, collision_handler=None, tile_mapping=None, map_data=None):
        """Apply damage to the enemy and trigger knockback

        Args:
            damage_amount (int): Amount of damage to apply
            knockback_x (float): X component of knockback direction
            knockback_y (float): Y component of knockback direction
            collision_handler: Optional collision handler for wall detection
            tile_mapping: Optional tile mapping for collision detection
            map_data: Optional map data for collision detection

        Returns:
            bool: True if damage was applied, False otherwise
        """
        # Base implementation - subclasses should override this
        # Apply knockback if provided
        if knockback_x != 0 or knockback_y != 0:
            self.apply_knockback(knockback_x, knockback_y, collision_handler, tile_mapping, map_data)

        return True

    def draw(self, surface, camera_x=0, camera_y=0):
        """Draw the enemy on the given surface, accounting for camera position"""
        # Calculate screen position
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y

        # Draw the enemy
        surface.blit(self.image, (screen_x, screen_y))

        # Draw a rectangle around the enemy for debugging
        if self.debug_mode:
            pygame.draw.rect(surface, (255, 0, 0),
                            pygame.Rect(screen_x, screen_y, self.rect.width, self.rect.height),
                            1)
