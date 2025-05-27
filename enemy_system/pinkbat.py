"""
Pinkbat Enemy - A flying pinkbat enemy that moves in a straight line and uses dashing attacks
"""
import pygame
import os
import math
from enemy_system.enemy import Enemy

class Pinkbat(Enemy):
    """Pinkbat enemy class - a flying pinkbat that moves in a straight line and uses dashing attacks"""
    def __init__(self, x, y, direction="left"):
        """Initialize the Pinkbat enemy

        Args:
            x (int): X position
            y (int): Y position
            direction (str): Initial direction ("left" or "right")
        """
        # Set the enemy type based on direction
        enemy_type = f"pinkbat_{direction}"
        super().__init__(x, y, enemy_type=enemy_type)

        # Set initial direction and state
        self.direction = direction
        self.state = "idle"

        # Load animations
        self._load_animations()

        # Create the rect but don't set position yet - EnemyManager will handle that
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # Health and damage properties
        self._init_health_properties()

        # Load health bar assets
        self._init_health_bar()

        # Movement and attack properties
        self._init_movement_properties()

        # Line of sight and pathfinding properties
        self._init_pathfinding_properties()

        # Set initial image
        initial_anim_key = f"idle_{self.direction}"
        if initial_anim_key in self.sprites and self.sprites[initial_anim_key]:
            self.image = self.sprites[initial_anim_key][0]
        elif "idle_left" in self.sprites and self.sprites["idle_left"]:
            self.image = self.sprites["idle_left"][0]

        # Set initial animation
        self.update_animation()

    def _load_animations(self):
        """Load animation sprites for the pinkbat"""
        # Load pinkbat idle, hit, and death animations for left and right directions
        self.load_animation("idle", "left", "Enemies_Sprites/Pinkbat_Sprites/pinkbat_idle_left_anim")
        self.load_animation("idle", "right", "Enemies_Sprites/Pinkbat_Sprites/pinkbat_idle_right_anim")
        self.load_animation("hit", "left", "Enemies_Sprites/Pinkbat_Sprites/pinkbat_hit_left_anim")
        self.load_animation("hit", "right", "Enemies_Sprites/Pinkbat_Sprites/pinkbat_hit_right_anim")
        self.load_animation("death", "left", "Enemies_Sprites/Pinkbat_Sprites/pinkbat_death_anim_left")
        self.load_animation("death", "right", "Enemies_Sprites/Pinkbat_Sprites/pinkbat_death_anim_right")

        # Load attack animations
        self.load_animation("run", "left", "Enemies_Sprites/Pinkbat_Sprites/pinkbat_run_attack_left_anim")
        self.load_animation("run", "right", "Enemies_Sprites/Pinkbat_Sprites/pinkbat_run_attack_right_anim")

    def _init_health_properties(self):
        """Initialize health-related properties"""
        # Health properties
        self.max_health = 100
        self.current_health = self.max_health
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 20  # Frames to show hit effect
        self.is_dying = False
        self.is_dead = False
        self.death_timer = 0
        self.death_duration = 60  # Frames to show death animation
        self.death_frame = 0
        self.damage_cooldown = 0
        self.damage_cooldown_time = 30  # Frames between taking damage

        # Health bar properties
        self.show_health_bar = False
        self.health_bar_timer = 0
        self.health_bar_duration = 120  # Show health bar for 2 seconds

    def _init_health_bar(self):
        """Initialize health bar assets"""
        # Load health bar assets
        self.health_bar_bg = self.load_image("Enemies_Sprites/Hud_Ui/health_hud.png")
        self.health_indicator = self.load_image("Enemies_Sprites/Hud_Ui/health_bar_hud.png")

        # Scale health bar to be smaller for enemies
        scale_factor = 0.5
        if self.health_bar_bg and self.health_indicator:
            # Scale the background
            self.health_bar_bg = pygame.transform.scale(
                self.health_bar_bg,
                (int(self.health_bar_bg.get_width() * scale_factor),
                 int(self.health_bar_bg.get_height() * scale_factor))
            )

            # Scale the indicator to be slightly smaller than the background
            indicator_scale = scale_factor * 0.9
            self.health_indicator = pygame.transform.scale(
                self.health_indicator,
                (int(self.health_indicator.get_width() * indicator_scale),
                 int(self.health_indicator.get_height() * indicator_scale))
            )

    def _init_movement_properties(self):
        """Initialize movement-related properties"""
        # Movement properties
        self.speed = 0.5  # Movement speed (reduced from 1.0)
        self.float_x = float(self.rect.x)  # Floating-point position for smoother movement
        self.float_y = float(self.rect.y)

        # Initialize velocity
        self.velocity = [0, 0]

        # Knockback properties
        self.knockback_strength = 4.0  # Strength of knockback when hit by player
        self.knockback_cooldown = 0
        self.knockback_cooldown_time = 45  # Frames to wait between knockbacks (about 0.75 seconds)

        # Player damage properties
        self.player_knockback_strength = 4.0
        self.player_damage = 10

        # Movement cooldown to prevent jittery movement
        self.move_cooldown = 0
        self.move_cooldown_time = 5  # Frames to wait between movement updates

    def _init_pathfinding_properties(self):
        """Initialize movement and detection properties"""
        # Detection properties
        self.detection_range = 240  # 15 tiles (16 pixels per tile)

        # Dash attack properties
        self.dash_range = 48  # 3 tiles (16 pixels per tile) - only dash when player is within 3 tiles
        self.dash_cooldown = 0
        self.dash_cooldown_time = 180  # 3 seconds (60 frames per second)
        self.is_dashing = False
        self.dash_speed = 3.0  # Faster speed during dash
        self.normal_speed = self.speed  # Store original speed
        self.dash_target_x = 0
        self.dash_target_y = 0
        self.dash_duration = 40  # Increased frames to dash to cover the longer distance
        self.dash_timer = 0
        self.dash_through_player = True  # Flag to make the dash go through the player
        self.dash_distance = 320  # Fixed dash distance of 20 tiles (16 pixels per tile)

    def load_image(self, path):
        """Load an image from the specified path"""
        full_path = os.path.join(os.getcwd(), path)
        try:
            image = pygame.image.load(full_path).convert_alpha()
            return image
        except pygame.error as e:
            print(f"Error loading image {path}: {e}")
            # Return a placeholder image (red square)
            placeholder = pygame.Surface((16, 16), pygame.SRCALPHA)
            placeholder.fill((255, 0, 0, 128))
            return placeholder

    def update(self, player_x, player_y, collision_handler=None, tile_mapping=None, map_data=None):
        """Update pinkbat position and animation

        Args:
            player_x (int): Player's x position
            player_y (int): Player's y position
            collision_handler: Optional collision handler for collision detection
            tile_mapping: Optional tile mapping for collision detection
            map_data: Optional map data for collision detection
        """
        # Skip updates if dead
        if self.is_dead:
            return

        # Update timers
        self._update_timers()

        # Initialize float position if not already set
        if self.float_x == 0.0 and self.float_y == 0.0:
            self.float_x = float(self.rect.x)
            self.float_y = float(self.rect.y)

        # Check if being knocked back
        if self.is_knocked_back:
            # Update knockback movement
            self._update_knockback(collision_handler, tile_mapping, map_data)

            # Check for collisions after knockback
            if collision_handler and tile_mapping and map_data:
                # If we collided with a wall during knockback, stop the knockback and move back to a valid position
                if collision_handler.check_collision(self.rect, tile_mapping, map_data):
                    # Store original position
                    original_x = self.rect.x
                    original_y = self.rect.y

                    # Try moving back in the opposite direction of knockback
                    # First try X direction
                    if self.knockback_velocity[0] != 0:
                        # Move back in the opposite direction of X knockback
                        self.rect.x -= int(self.knockback_velocity[0] * 2)

                        # Check if we're still colliding
                        if collision_handler.check_collision(self.rect, tile_mapping, map_data):
                            # Restore original X position
                            self.rect.x = original_x

                            # Try moving back in the opposite direction of Y knockback
                            if self.knockback_velocity[1] != 0:
                                self.rect.y -= int(self.knockback_velocity[1] * 2)

                                # If still colliding, restore original position
                                if collision_handler.check_collision(self.rect, tile_mapping, map_data):
                                    self.rect.y = original_y

                    # If we didn't try X direction or it didn't work, try Y direction
                    elif self.knockback_velocity[1] != 0:
                        # Move back in the opposite direction of Y knockback
                        self.rect.y -= int(self.knockback_velocity[1] * 2)

                        # Check if we're still colliding
                        if collision_handler.check_collision(self.rect, tile_mapping, map_data):
                            # Restore original Y position
                            self.rect.y = original_y

                    # Update float position from rect position
                    self.float_x = float(self.rect.x)
                    self.float_y = float(self.rect.y)

                    # Stop knockback
                    self.knockback_velocity = [0, 0]
                    self.is_knocked_back = False

        # Only move normally if not hit, dying, or knocked back
        elif not self.is_hit and not self.is_dying:
            # Move towards player in a straight line
            self._move_towards_player(player_x, player_y)

            # Update float position based on velocity
            self.float_x += self.velocity[0]
            self.float_y += self.velocity[1]

            # Update rect position from float position
            self.rect.x = int(self.float_x)
            self.rect.y = int(self.float_y)

        # Update animation
        self.update_animation()

    def _update_timers(self):
        """Update all timers"""
        # Update damage cooldown
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1

        # Update hit timer
        if self.hit_timer > 0:
            self.hit_timer -= 1
            if self.hit_timer <= 0 and self.is_hit:
                self.is_hit = False
                self.state = "idle"

        # Update death timer
        if self.death_timer > 0:
            self.death_timer -= 1
            # Check if death timer has expired and we're still dying
            if self.death_timer <= 0 and self.is_dying:
                self.is_dead = True

        # Update health bar timer
        if self.health_bar_timer > 0:
            self.health_bar_timer -= 1
            if self.health_bar_timer <= 0:
                self.show_health_bar = False

        # Update dash cooldown
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

        # Update dash timer
        if self.is_dashing:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                # End dash
                self.is_dashing = False
                self.speed = self.normal_speed
                self.state = "idle"

    def _update_death_animation(self, animation_key):
        """Update death animation

        Args:
            animation_key (str): The animation key for the death animation
        """
        # Make sure we have a valid animation key
        if animation_key not in self.sprites or not self.sprites[animation_key]:
            # Try to find a valid death animation
            if f"death_{self.direction}" in self.sprites and self.sprites[f"death_{self.direction}"]:
                animation_key = f"death_{self.direction}"
            elif "death_left" in self.sprites and self.sprites["death_left"]:
                animation_key = "death_left"
            elif "death_right" in self.sprites and self.sprites["death_right"]:
                animation_key = "death_right"
            else:
                # No valid death animation found, use idle animation
                if f"idle_{self.direction}" in self.sprites and self.sprites[f"idle_{self.direction}"]:
                    animation_key = f"idle_{self.direction}"
                elif "idle_left" in self.sprites and self.sprites["idle_left"]:
                    animation_key = "idle_left"
                elif "idle_right" in self.sprites and self.sprites["idle_right"]:
                    animation_key = "idle_right"
                else:
                    # No valid animation found at all
                    return

        # Calculate which frame to show based on death timer
        total_frames = len(self.sprites[animation_key])

        # Calculate current frame based on death timer
        if self.death_timer > 0:
            progress = 1.0 - (self.death_timer / self.death_duration)
            self.death_frame = min(int(progress * total_frames), total_frames - 1)
        else:
            # If death timer expired, mark as dead and use the last frame
            self.is_dead = True
            self.death_frame = total_frames - 1

        # Use death frame for rendering
        self.image = self.sprites[animation_key][self.death_frame]

    def _update_knockback(self, collision_handler=None, tile_mapping=None, map_data=None):
        """Update knockback movement and check for collisions

        Args:
            collision_handler: Optional collision handler for collision detection
            tile_mapping: Optional tile mapping for collision detection
            map_data: Optional map data for collision detection
        """
        # Update knockback timer
        self.knockback_timer -= 1
        if self.knockback_timer <= 0:
            # Reset knockback state
            self.is_knocked_back = False
            self.knockback_velocity = [0, 0]
            self.state = "idle"
            return

        # Store original position for collision detection
        original_x = self.rect.x
        original_y = self.rect.y

        # Apply knockback movement to float position
        self.float_x += self.knockback_velocity[0]
        self.float_y += self.knockback_velocity[1]

        # Update rect position from float position
        self.rect.x = int(self.float_x)
        self.rect.y = int(self.float_y)

        # Check for collisions after knockback if collision data is available
        if collision_handler and tile_mapping and map_data:
            if collision_handler.check_collision(self.rect, tile_mapping, map_data):
                # We'll handle this in the main update method for more sophisticated collision response
                # Just revert position for now
                self.rect.x = original_x
                self.rect.y = original_y
                self.float_x = float(original_x)
                self.float_y = float(original_y)
                return

        # Gradually reduce knockback effect
        self.knockback_velocity[0] *= 0.9
        self.knockback_velocity[1] *= 0.9

    def _move_towards_player(self, player_x, player_y):
        """Move the pinkbat towards the player in a straight line with dash attacks

        Args:
            player_x (int): Player's x position
            player_y (int): Player's y position
        """

        # Decrement cooldown
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        # Calculate distance to player
        dx = player_x - self.rect.centerx
        dy = player_y - self.rect.centery
        distance_to_player = math.sqrt(dx**2 + dy**2)

        # Check if player is outside detection range
        if distance_to_player > self.detection_range:
            # Player too far away, stop moving
            self.velocity = [0, 0]
            self.state = "idle"
            return

        # If we're currently dashing, continue the dash
        if self.is_dashing:
            # When dashing, we don't stop at the player - we go through them
            return  # Dash movement is handled in _update_timers

        # Check if we should dash (within dash range and cooldown is ready)
        if distance_to_player <= self.dash_range and self.dash_cooldown <= 0 and not self.is_dashing:
            # Start dash
            self.is_dashing = True
            self.dash_timer = self.dash_duration
            self.speed = self.dash_speed

            # Calculate dash target position - always dash the full 15 tiles
            if distance_to_player > 0:  # Avoid division by zero
                # Normalize direction
                norm_dx = dx / distance_to_player
                norm_dy = dy / distance_to_player

                # Always use the full dash distance (20 tiles) regardless of player position
                # This ensures the pinkbat always completes the full dash and goes through the player
                self.dash_target_x = self.rect.centerx + norm_dx * self.dash_distance
                self.dash_target_y = self.rect.centery + norm_dy * self.dash_distance

                # Set velocity for dash
                self.velocity[0] = norm_dx * self.speed
                self.velocity[1] = norm_dy * self.speed

                # Set direction based on horizontal movement for animation
                if norm_dx != 0:
                    self.direction = "right" if norm_dx > 0 else "left"

                # Set animation state to run for dash
                self.state = "run"

                # Start cooldown after dash
                self.dash_cooldown = self.dash_cooldown_time
            return

        # Move in a straight line towards the player
        self.move_in_straight_line(player_x, player_y)

        # Set cooldown to prevent jittery movement
        self.move_cooldown = self.move_cooldown_time

    def move_in_straight_line(self, player_x, player_y):
        """Move the pinkbat in a straight line towards the player

        Args:
            player_x (int): Player's x position
            player_y (int): Player's y position
        """
        # Calculate direction to player
        dx = player_x - self.rect.centerx
        dy = player_y - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)

        # Check if player is outside detection range
        if distance > self.detection_range:
            # Player too far away, stop moving
            self.velocity = [0, 0]
            self.state = "idle"
            return False

        # Normalize direction
        if distance > 0:
            dx = dx / distance
            dy = dy / distance

            # Set velocity
            self.velocity[0] = dx * self.speed
            self.velocity[1] = dy * self.speed

            # Set direction based on horizontal movement for animation
            if dx != 0:
                self.direction = "right" if dx > 0 else "left"

            # Set animation state
            self.state = "run"
            return True
        else:
            # We're at the player position, stop moving
            self.velocity = [0, 0]
            self.state = "idle"
            return False

    def check_collision(self, *args, **kwargs):
        """Check if the pinkbat would collide with any solid tile corners
        Since pinkbat is flying, it ignores all collisions

        Returns:
            bool: Always False since pinkbat ignores collisions
        """
        # Pinkbat is flying, so it ignores all collisions
        return False

    def find_path_direction(self, target_x, target_y):
        """Find the direction to move towards the target
        Since pinkbat is flying, it always moves directly towards the target

        Args:
            target_x (int): Target x position
            target_y (int): Target y position

        Returns:
            tuple: (dx, dy) direction vector to move in
        """
        # Calculate direct direction to target
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery

        # Calculate distance to target
        distance = ((dx ** 2) + (dy ** 2)) ** 0.5

        # If we're at the target, no movement
        if distance == 0:
            return 0, 0

        # Return the direct vector to the target
        return dx, dy

    def update_animation(self):
        """Update the pinkbat's animation frame"""
        # Handle death animation
        if self.is_dying:
            # Use death animation
            current_animation_key = f"death_{self.direction}"
            # Fallback to idle if death animation doesn't exist
            if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
                current_animation_key = f"idle_{self.direction}"
        # Handle hit animation
        elif self.is_hit:
            # Use hit animation
            current_animation_key = f"hit_{self.direction}"
            # Fallback to idle if hit animation doesn't exist
            if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
                current_animation_key = f"idle_{self.direction}"
        # Handle run/attack animation
        elif self.state == "run":
            # Use run animation
            current_animation_key = f"run_{self.direction}"
            # Fallback to idle if run animation doesn't exist
            if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
                current_animation_key = f"idle_{self.direction}"
        else:
            # Normal idle animation
            current_animation_key = f"idle_{self.direction}"

        # Check if the animation exists
        if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
            # Try the appropriate direction if this one doesn't exist
            if current_animation_key.startswith("death_"):
                # For death animations, try the other direction
                if self.direction == "left":
                    current_animation_key = "death_right"
                else:
                    current_animation_key = "death_left"
            elif current_animation_key.startswith("hit_"):
                # For hit animations, try the other direction
                if self.direction == "left":
                    current_animation_key = "hit_right"
                else:
                    current_animation_key = "hit_left"
            else:
                # For idle animations, try the other direction
                if self.direction == "left":
                    current_animation_key = "idle_right"
                else:
                    current_animation_key = "idle_left"

            # If we still don't have a valid animation, try fallbacks
            if (current_animation_key.startswith("death_") and
                (current_animation_key not in self.sprites or not self.sprites[current_animation_key])):
                # Fallback to idle animation if death animation doesn't exist
                if self.direction == "left":
                    current_animation_key = "idle_left"
                else:
                    current_animation_key = "idle_right"

        # If we still don't have a valid animation, return
        if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
            return

        # Special handling for death animation
        if self.is_dying and current_animation_key.startswith("death_"):
            self._update_death_animation(current_animation_key)
            return

        # Update animation frame for non-death animations
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            # Ensure we have a valid animation list
            if current_animation_key in self.sprites and self.sprites[current_animation_key]:
                # Reset frame if it's out of range (this can happen when switching animations)
                if self.frame >= len(self.sprites[current_animation_key]):
                    self.frame = 0
                # Update to next frame
                self.frame = (self.frame + 1) % len(self.sprites[current_animation_key])

        # Update image - with safety checks
        if (current_animation_key in self.sprites and
            self.sprites[current_animation_key] and
            self.frame < len(self.sprites[current_animation_key])):
            self.image = self.sprites[current_animation_key][self.frame]

    def draw(self, surface, camera_x=0, camera_y=0):
        """Draw the pinkbat

        Args:
            surface (pygame.Surface): The surface to draw on
            camera_x (int): Camera x offset
            camera_y (int): Camera y offset
        """
        # Skip drawing if dead
        if self.is_dead:
            return

        # Calculate position with camera offset
        draw_x = self.rect.x - camera_x
        draw_y = self.rect.y - camera_y
        draw_rect = pygame.Rect(draw_x, draw_y, self.rect.width, self.rect.height)

        # Draw the pinkbat
        surface.blit(self.image, draw_rect)

        # Draw health bar if needed
        if self.show_health_bar and not self.is_dead and self.health_bar_bg and self.health_indicator:
            # Calculate screen position for health bar (centered above the enemy)
            screen_x = self.rect.centerx - (self.health_bar_bg.get_width() // 2) - camera_x
            screen_y = self.rect.y - self.health_bar_bg.get_height() - 5 - camera_y  # 5 pixels above enemy

            # Calculate health percentage
            health_percent = max(0, min(1, self.current_health / self.max_health))

            # Calculate width of health indicator based on percentage
            health_width = int(self.health_bar_bg.get_width() * health_percent)

            if health_width > 0:
                try:
                    # Create a subsurface of the background with the appropriate width
                    health_rect = pygame.Rect(0, 0, health_width, self.health_bar_bg.get_height())
                    health_bg_part = self.health_bar_bg.subsurface(health_rect)

                    # Draw the health background
                    surface.blit(health_bg_part, (screen_x, screen_y))

                    # Draw the health indicator on top
                    surface.blit(self.health_indicator, (screen_x, screen_y))
                except ValueError:
                    # If subsurface fails, use clipping rect
                    clip_rect = surface.get_clip()

                    health_clip_rect = pygame.Rect(
                        screen_x,
                        screen_y,
                        health_width,
                        self.health_bar_bg.get_height()
                    )

                    # Draw with clipping
                    surface.set_clip(health_clip_rect)
                    surface.blit(self.health_bar_bg, (screen_x, screen_y))
                    surface.set_clip(clip_rect)

                    # Draw the health indicator on top
                    surface.blit(self.health_indicator, (screen_x, screen_y))

    def take_damage(self, damage_amount=10, knockback_x=0, knockback_y=0, collision_handler=None, tile_mapping=None, map_data=None):
        """Apply damage to the pinkbat and trigger hit animation

        Args:
            damage_amount (int): Amount of damage to apply
            knockback_x (float): X component of knockback direction
            knockback_y (float): Y component of knockback direction
            collision_handler: Optional collision handler for wall detection
            tile_mapping: Optional tile mapping for collision detection
            map_data: Optional map data for collision detection
        """
        # Only take damage if not already dying or dead and not on cooldown
        if self.is_dying or self.is_dead or self.damage_cooldown > 0:
            return False

        # Store the original direction before applying damage
        original_direction = self.direction

        # Reduce health
        self.current_health -= damage_amount

        # Show health bar
        self.show_health_bar = True
        self.health_bar_timer = self.health_bar_duration

        # Start damage cooldown to prevent multiple hits from a single attack
        self.damage_cooldown = self.damage_cooldown_time

        # Check if pinkbat should die
        if self.current_health <= 0:
            self.current_health = 0
            # Ensure the direction is preserved for death animation
            self.direction = original_direction
            self.start_death_animation()
            return True

        # Apply knockback if direction is provided
        if knockback_x != 0 or knockback_y != 0:
            # Normalize the knockback direction
            distance = ((knockback_x ** 2) + (knockback_y ** 2)) ** 0.5
            if distance > 0:
                # Scale knockback by a factor
                knockback_factor = min(distance, 10) / distance
                normalized_x = (knockback_x / distance) * knockback_factor * self.knockback_strength
                normalized_y = (knockback_y / distance) * knockback_factor * self.knockback_strength

                # Use our overridden apply_knockback method which preserves direction
                self.apply_knockback(normalized_x, normalized_y, collision_handler, tile_mapping, map_data)
            else:
                # Fallback if direction is invalid
                self.apply_knockback(knockback_x, knockback_y, collision_handler, tile_mapping, map_data)

        # Ensure the direction is preserved after knockback
        self.direction = original_direction

        # Start hit animation
        self.start_hit_animation()
        return True

    def start_hit_animation(self):
        """Start the hit animation sequence"""
        self.is_hit = True
        self.hit_timer = self.hit_duration
        self.animation_timer = 0
        self.state = "hit"

        # Force the current frame to be the first frame of the hit animation for the current direction
        hit_key = f"hit_{self.direction}"
        if hit_key in self.sprites and self.sprites[hit_key]:
            self.image = self.sprites[hit_key][0]
            self.frame = 0

    def start_death_animation(self):
        """Start the death animation sequence"""
        self.is_dying = True
        self.is_hit = False  # Cancel any hit animation
        self.death_timer = self.death_duration
        self.death_frame = 0  # Reset death frame
        self.animation_timer = 0
        self.state = "death"
        self.velocity = [0, 0]  # Stop movement

        # Keep the current direction (left or right) for the death animation
        # Don't change the direction - this is important for pinkbat since it has specific left/right animations

        # Force the current frame to be the first frame of the death animation
        death_key = f"death_{self.direction}"
        if death_key in self.sprites and self.sprites[death_key]:
            self.image = self.sprites[death_key][0]
        # Fallback if the animation doesn't exist for the current direction
        elif "death_left" in self.sprites and self.sprites["death_left"]:
            self.image = self.sprites["death_left"][0]
        elif "death_right" in self.sprites and self.sprites["death_right"]:
            self.image = self.sprites["death_right"][0]

    def apply_knockback(self, direction_x, direction_y, collision_handler=None, tile_mapping=None, map_data=None):
        """Override the base apply_knockback method to preserve the original direction

        Args:
            direction_x (float): X component of knockback direction
            direction_y (float): Y component of knockback direction
            collision_handler: Optional collision handler for wall detection
            tile_mapping: Optional tile mapping for collision detection
            map_data: Optional map data for collision detection
        """
        # Store the original direction
        original_direction = self.direction

        # Call the parent class method to apply knockback
        result = super().apply_knockback(direction_x, direction_y, collision_handler, tile_mapping, map_data)

        # Restore the original direction
        self.direction = original_direction

        return result

    def apply_knockback_to_player(self, player, **_):
        """Apply knockback to the player when colliding

        Args:
            player: The player object to apply knockback to
            **_: Additional parameters (ignored for compatibility with enemy manager)
        """
        # Skip if on cooldown, hit, dying or dead
        if self.damage_cooldown > 0 or self.is_hit or self.is_dying or self.is_dead:
            return False

        # Check if we're colliding with the player
        if self.rect.colliderect(player.rect):
            # When dashing, apply knockback to the side (perpendicular to dash direction)
            if self.is_dashing:
                # Get the dash direction vector
                if hasattr(self, 'velocity') and (self.velocity[0] != 0 or self.velocity[1] != 0):
                    # Normalize the dash direction
                    dash_dx = self.velocity[0]
                    dash_dy = self.velocity[1]
                    dash_length = ((dash_dx ** 2) + (dash_dy ** 2)) ** 0.5

                    if dash_length > 0:
                        # Normalize
                        dash_dx /= dash_length
                        dash_dy /= dash_length

                        # Calculate perpendicular vector (rotate 90 degrees)
                        # For a vector (x,y), the perpendicular vectors are (-y,x) or (y,-x)
                        perp_dx = -dash_dy
                        perp_dy = dash_dx

                        # Determine which side of the dash path the player is on
                        # Calculate the vector from pinkbat to player
                        to_player_dx = player.rect.centerx - self.rect.centerx
                        to_player_dy = player.rect.centery - self.rect.centery

                        # Dot product to determine side (positive = right side, negative = left side)
                        dot_product = to_player_dx * perp_dx + to_player_dy * perp_dy

                        # Ensure knockback is in the correct direction
                        if dot_product < 0:
                            perp_dx = -perp_dx
                            perp_dy = -perp_dy

                        # Apply sideways knockback to player
                        if hasattr(player, 'apply_knockback'):
                            # Calculate distance between centers
                            center_distance = ((player.rect.centerx - self.rect.centerx) ** 2 +
                                              (player.rect.centery - self.rect.centery) ** 2) ** 0.5

                            # Apply stronger knockback when dashing
                            knockback_multiplier = 3.0  # Increased for more noticeable side knockback

                            # If player is very close to center and shielded, we need to force knockback
                            if center_distance <= 8 and hasattr(player, 'is_shielded') and player.is_shielded:
                                # Store original shield state
                                was_shielded = player.is_shielded

                                # Temporarily disable shield to allow knockback
                                player.is_shielded = False

                                # Apply knockback
                                player.apply_knockback(perp_dx * knockback_multiplier, perp_dy * knockback_multiplier)

                                # Restore shield state but keep the knockback active
                                player.is_shielded = was_shielded
                            else:
                                # Normal knockback application
                                player.apply_knockback(perp_dx * knockback_multiplier, perp_dy * knockback_multiplier)
                    else:
                        # Fallback if velocity is zero (shouldn't happen during dash)
                        dx = player.rect.centerx - self.rect.centerx
                        dy = player.rect.centery - self.rect.centery

                        # Calculate distance between centers
                        center_distance = ((dx ** 2) + (dy ** 2)) ** 0.5

                        # If player is very close to center and shielded, we need to force knockback
                        if center_distance <= 8 and hasattr(player, 'is_shielded') and player.is_shielded:
                            # Store original shield state
                            was_shielded = player.is_shielded

                            # Temporarily disable shield to allow knockback
                            player.is_shielded = False

                            # Apply knockback
                            player.apply_knockback(dx * 2.0, dy * 2.0)

                            # Restore shield state but keep the knockback active
                            player.is_shielded = was_shielded
                        else:
                            # Normal knockback application
                            player.apply_knockback(dx * 2.0, dy * 2.0)
                else:
                    # Fallback if velocity is not available
                    dx = player.rect.centerx - self.rect.centerx
                    dy = player.rect.centery - self.rect.centery

                    # Calculate distance between centers
                    center_distance = ((dx ** 2) + (dy ** 2)) ** 0.5

                    # If player is very close to center and shielded, we need to force knockback
                    if center_distance <= 8 and hasattr(player, 'is_shielded') and player.is_shielded:
                        # Store original shield state
                        was_shielded = player.is_shielded

                        # Temporarily disable shield to allow knockback
                        player.is_shielded = False

                        # Apply knockback
                        player.apply_knockback(dx * 2.0, dy * 2.0)

                        # Restore shield state but keep the knockback active
                        player.is_shielded = was_shielded
                    else:
                        # Normal knockback application
                        player.apply_knockback(dx * 2.0, dy * 2.0)
            else:
                # For normal collisions (not dashing), use regular knockback away from pinkbat
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery

                # Calculate distance between centers
                center_distance = ((dx ** 2) + (dy ** 2)) ** 0.5

                # Apply knockback to the player
                if hasattr(player, 'apply_knockback'):
                    # If player is very close to center and shielded, we need to force knockback
                    if center_distance <= 8 and hasattr(player, 'is_shielded') and player.is_shielded:
                        # Store original shield state
                        was_shielded = player.is_shielded

                        # Temporarily disable shield to allow knockback
                        player.is_shielded = False

                        # Apply knockback
                        player.apply_knockback(dx, dy)

                        # Restore shield state but keep the knockback active
                        player.is_shielded = was_shielded
                    else:
                        # Normal knockback application
                        player.apply_knockback(dx, dy)

            # Apply damage to the player
            if hasattr(player, 'take_damage'):
                # Apply more damage when dashing
                damage = 20 if self.is_dashing else 10

                # Check if player is at the center of the bat
                # Calculate distance between centers
                center_distance = ((player.rect.centerx - self.rect.centerx) ** 2 +
                                  (player.rect.centery - self.rect.centery) ** 2) ** 0.5

                # If player is very close to center (within 8 pixels), bypass shield protection
                if center_distance <= 8 and hasattr(player, 'is_shielded') and player.is_shielded:
                    # Temporarily store shield state
                    was_shielded = player.is_shielded

                    # Temporarily disable shield to allow damage
                    player.is_shielded = False

                    # Apply damage
                    player.take_damage(damage)

                    # Restore shield state
                    player.is_shielded = was_shielded
                else:
                    # Normal damage application
                    player.take_damage(damage)

            # Start cooldown - shorter cooldown when dashing to allow multiple hits
            if self.is_dashing:
                self.damage_cooldown = 15  # Quarter second cooldown during dash
            else:
                self.damage_cooldown = self.damage_cooldown_time

            # Don't stop dashing when hitting the player - continue through
            if self.is_dashing:
                return True

            return True
        return False