"""
Player Character module - implements the playable character with animations
"""
import pygame
import math
from settings import *
from character_system.animation_handler import blit_aligned
from character_system.sprite_loader import load_character_sprites

class PlayerCharacter(pygame.sprite.Sprite):
    """Player character class with sprite animations"""
    def __init__(self, x, y):
        super().__init__()
        self.width = 16  # Standard size for character sprite
        self.height = 16
        self.speed = 1  # Movement speed changed from 2 to 1

        # Animation variables
        self.direction = "down"  # Current facing direction
        self.state = "idle"  # Current animation state (idle, walk, attack)
        self.frame = 0  # Current animation frame
        self.animation_speed = 0.1  # Animation speed (frames per update)
        self.animation_timer = 0  # Timer for animation updates

        # Attack variables
        self.is_attacking = False
        self.attack_frame = 0
        self.attack_speed = 0.2  # Attack animation speed (faster than idle)

        # Animation frame counts (will be set after loading sprites)
        self.animation_frame_counts = {}

        # Load character sprites
        self.sprites = load_character_sprites()

        # Set initial image and rect
        self.image = self.sprites["idle_down"][0]
        self.current_animation_image = self.image  # Store the visual representation
        self.rect = self.image.get_rect()

        # Store the character's center-bottom position (feet position)
        # This will be our reference point for all animations
        self.rect.x = x
        self.rect.y = y

        # Store the original center-bottom position for reference
        # Use a tuple since pygame.Vector2 doesn't have a copy method
        self.reference_position = (self.rect.midbottom[0], self.rect.midbottom[1])

        # Movement variables
        self.velocity = [0, 0]
        self.base_speed = 1  # Base movement speed (changed from 2 to 1)
        self.speed = self.base_speed  # Current movement speed (affected by multipliers)

        # Map boundaries
        self.min_x = 0
        self.min_y = 0
        self.max_x = 2000  # Default value, will be updated
        self.max_y = 2000  # Default value, will be updated

        # Knockback effect
        self.is_knocked_back = False
        self.knockback_timer = 0
        self.knockback_duration = 25  # Increased frames to show knockback effect
        self.knockback_strength = 2.5  # Reduced strength of knockback when hit by enemies (was 5.0)
        self.knockback_velocity = [0, 0]  # Direction and speed of knockback
        self.hit_frame = 0  # Current frame of hit animation
        self.hit_animation_speed = 0.15  # Speed of hit animation

        # Health system
        self.max_health = 100
        self.current_health = 100
        self.invincibility_timer = 0
        self.invincibility_duration = 60  # 1 second of invincibility after being hit (60 frames)

        # Death animation
        self.is_dead = False
        self.death_animation_timer = 0
        self.death_animation_speed = 0.1
        self.death_frame = 0
        self.death_animation_complete = False

        # Shield system
        self.is_shielded = False
        self.shield_cooldown = 0
        self.shield_cooldown_duration = 60  # 1 second cooldown after shield deactivation (60 frames per second)
        self.shield_active_timer = 0
        self.shield_max_duration = 180  # 3 seconds maximum duration (60 frames per second)
        self.shield_hit_duration = 20  # Duration of shield hit animation in frames

        # Shield durability
        self.shield_max_durability = 3  # Maximum number of hits the shield can take
        self.shield_durability = self.shield_max_durability  # Current shield durability

        # Shield break effect
        self.shield_break_active = False
        self.shield_break_time = 0
        self.shield_break_duration = 500  # Effect lasts for 500ms

        # Slowing effect (for pinkslime)
        self.speed_multiplier = 1.0  # Current speed multiplier (1.0 = 100% speed)
        self.slow_timer = 0  # Timer for slowing effect

    def handle_input(self):
        """Handle keyboard input for player movement"""
        keys = pygame.key.get_pressed()

        # Reset velocity
        self.velocity = [0, 0]

        # Handle shield activation with space key
        if keys[pygame.K_SPACE]:
            # Only activate shield if not on cooldown and not already attacking or knocked back
            if self.shield_cooldown <= 0 and not self.is_attacking and not self.is_knocked_back:
                if not self.is_shielded:
                    self.activate_shield()

                # Keep shield active while space is held
                self.state = "shield"

                # When shielded, WASD only changes direction, not movement
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.direction = "left"
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.direction = "right"
                elif keys[pygame.K_UP] or keys[pygame.K_w]:
                    self.direction = "up"
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    self.direction = "down"

                # No movement while shielded
                return
        else:
            # Deactivate shield when space is released
            if self.is_shielded:
                self.deactivate_shield()

        # Only process movement if not shielded
        if not self.is_shielded:
            # Set velocity based on key presses
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.velocity[0] = -self.speed
                self.direction = "left"
                self.state = "run"  # Use run animation for walking
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.velocity[0] = self.speed
                self.direction = "right"
                self.state = "run"  # Use run animation for walking
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                self.velocity[1] = -self.speed
                self.direction = "up"
                self.state = "run"  # Use run animation for walking
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.velocity[1] = self.speed
                self.direction = "down"
                self.state = "run"  # Use run animation for walking
            else:
                self.state = "idle"

    def update_animation(self):
        """Update the character's animation frame"""
        # Handle death animation first
        if self.is_dead:
            current_animation_key = f"death_{self.direction}"

            # Update death animation timer
            self.death_animation_timer += self.death_animation_speed
            if self.death_animation_timer >= 1:
                self.death_animation_timer = 0
                self.death_frame += 1

                # Check if death animation is complete
                if current_animation_key in self.sprites and self.death_frame >= len(self.sprites[current_animation_key]):
                    self.death_frame = len(self.sprites[current_animation_key]) - 1  # Stay on last frame
                    self.death_animation_complete = True

            # Set the current frame to the death frame
            if current_animation_key in self.sprites and len(self.sprites[current_animation_key]) > 0:
                frame_index = min(self.death_frame, len(self.sprites[current_animation_key]) - 1)
                self.image = self.sprites[current_animation_key][frame_index]
                self.current_animation_image = self.image
            return

        # For normal animations
        # Determine the animation key based on state and direction
        if self.is_knocked_back and self.is_shielded:
            # Use shielded hit animation when knocked back while shielded
            current_animation_key = f"shield_hit_{self.direction}"
        elif self.is_knocked_back:
            current_animation_key = f"hit_{self.direction}"
        elif self.is_attacking:
            current_animation_key = f"attack_{self.direction}"
        elif self.is_shielded:
            current_animation_key = f"shield_{self.direction}"
        else:
            current_animation_key = f"{self.state}_{self.direction}"

        # Check if the animation exists
        if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
            # If we don't have the specific animation, try to find a fallback
            if "shield_hit" in current_animation_key:
                # If shielded hit animation doesn't exist, try regular hit animation
                hit_key = f"hit_{self.direction}"
                if hit_key in self.sprites and self.sprites[hit_key]:
                    current_animation_key = hit_key
                    print(f"Fallback to regular hit animation: {hit_key}")
                else:
                    # If hit animation doesn't exist, use shield animation
                    shield_key = f"shield_{self.direction}"
                    if shield_key in self.sprites and self.sprites[shield_key]:
                        current_animation_key = shield_key
                        print(f"Fallback to shield animation: {shield_key}")
                    else:
                        current_animation_key = "idle_down"  # Default fallback
            elif "attack" in current_animation_key:
                # If attack animation doesn't exist, use idle for that direction
                idle_key = f"idle_{self.direction}"
                if idle_key in self.sprites and self.sprites[idle_key]:
                    current_animation_key = idle_key
                else:
                    current_animation_key = "idle_down"  # Default fallback
            elif self.state == "run":
                # Use run animation for movement
                run_key = f"run_{self.direction}"
                if run_key in self.sprites and self.sprites[run_key]:
                    current_animation_key = run_key
                else:
                    # If run animation doesn't exist, fall back to idle
                    idle_key = f"idle_{self.direction}"
                    if idle_key in self.sprites and self.sprites[idle_key]:
                        current_animation_key = idle_key
                    else:
                        current_animation_key = "idle_down"  # Default fallback
            else:
                # For idle state, use the correct direction if available
                if f"idle_{self.direction}" in self.sprites and self.sprites[f"idle_{self.direction}"]:
                    current_animation_key = f"idle_{self.direction}"
                else:
                    current_animation_key = "idle_down"  # Default fallback

        # Store the current position before updating the animation
        current_midbottom = self.rect.midbottom

        # Handle hit animation (knockback)
        if self.is_knocked_back:
            # Update hit animation timer
            self.animation_timer += self.hit_animation_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.hit_frame += 1

                # Check if hit animation is complete
                if self.hit_frame >= len(self.sprites[current_animation_key]):
                    # Reset hit frame but keep knockback state
                    # The knockback state will be reset in the update method
                    self.hit_frame = len(self.sprites[current_animation_key]) - 1

                # Use hit frame for rendering
                frame_index = min(self.hit_frame, len(self.sprites[current_animation_key]) - 1)
                self.image = self.sprites[current_animation_key][frame_index]
            else:
                # Use current hit frame for rendering
                frame_index = min(self.hit_frame, len(self.sprites[current_animation_key]) - 1)
                self.image = self.sprites[current_animation_key][frame_index]

        # Handle attack animation
        elif self.is_attacking:
            # Update attack animation timer (faster than regular animations)
            self.animation_timer += self.attack_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.attack_frame += 1

                # Check if attack animation is complete
                if self.attack_frame >= len(self.sprites[current_animation_key]):
                    # Reset attack state
                    self.is_attacking = False
                    self.attack_frame = 0
                    self.state = "idle"

                    # Switch to idle animation
                    idle_key = f"idle_{self.direction}"
                    if idle_key in self.sprites and self.sprites[idle_key]:
                        self.image = self.sprites[idle_key][0]
                    else:
                        self.image = self.sprites["idle_down"][0]
                else:
                    # Use attack frame for rendering
                    frame_index = min(self.attack_frame, len(self.sprites[current_animation_key]) - 1)
                    self.image = self.sprites[current_animation_key][frame_index]
            else:
                # Use current attack frame for rendering
                frame_index = min(self.attack_frame, len(self.sprites[current_animation_key]) - 1)
                self.image = self.sprites[current_animation_key][frame_index]
        # Handle shield animation (which has only one frame)
        elif self.is_shielded:
            # Shield animations have only one frame, so just use the first frame
            if len(self.sprites[current_animation_key]) > 0:
                self.image = self.sprites[current_animation_key][0]
            else:
                # Fallback to idle if shield animation is missing
                idle_key = f"idle_{self.direction}"
                if idle_key in self.sprites and self.sprites[idle_key]:
                    self.image = self.sprites[idle_key][0]
                else:
                    self.image = self.sprites["idle_down"][0]
        else:
            # Regular animation handling (idle/walk)
            # Update animation timer
            self.animation_timer += self.animation_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.frame = (self.frame + 1) % len(self.sprites[current_animation_key])

            # Update image
            self.image = self.sprites[current_animation_key][self.frame]

        # Store the current animation image for drawing
        self.current_animation_image = self.image

        # For collision purposes, maintain a consistent 16x16 rect regardless of animation
        # This prevents the character from being pushed when attack animations change size
        if self.is_attacking:
            # Keep the rect at 16x16 for collision purposes
            # We'll only use the larger image for visual display in the draw method
            self.rect.midbottom = current_midbottom
        else:
            # For non-attack animations, update rect normally
            self.rect = self.image.get_rect()
            self.rect.midbottom = current_midbottom

    def attack(self):
        """Trigger an attack animation"""
        # Only start attack if not already attacking
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_frame = 0
            self.animation_timer = 0
            self.state = "attack"
            return True
        return False

    def handle_mouse_event(self, event):
        """Handle mouse events for the player character"""
        # Check for left-click to attack
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            return self.attack()
        return False

    def set_map_boundaries(self, min_x, min_y, max_x, max_y):
        """Set the map boundaries for player movement"""
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

    def update_position(self):
        """Update the player's position and ensure all internal state is consistent"""
        # This method is called after teleportation to ensure the player's position is properly updated
        # Store the current midbottom position
        current_midbottom = self.rect.midbottom

        # Update the image and rect
        if self.state == "idle":
            current_animation_key = f"idle_{self.direction}"
        elif self.state == "run":
            current_animation_key = f"run_{self.direction}"
        elif self.state == "attack":
            current_animation_key = f"attack_{self.direction}"
        elif self.state == "shield":
            current_animation_key = f"shield_{self.direction}"
        else:
            current_animation_key = f"idle_{self.direction}"

        # Make sure the animation key exists
        if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
            current_animation_key = "idle_down"

        # Update the image
        self.image = self.sprites[current_animation_key][0]
        self.current_animation_image = self.image

        # Reset animation frame
        self.frame = 0
        self.animation_timer = 0

        # Update the rect while preserving the midbottom position
        self.rect = self.image.get_rect()
        self.rect.midbottom = current_midbottom

    def activate_shield(self):
        """Activate the shield"""
        self.is_shielded = True
        self.shield_active_timer = self.shield_max_duration
        self.invincibility_timer = self.shield_max_duration  # Make player invincible while shield is active
        self.shield_durability = self.shield_max_durability  # Reset shield durability

    def deactivate_shield(self):
        """Deactivate the shield"""
        self.is_shielded = False
        self.shield_cooldown = self.shield_cooldown_duration
        self.invincibility_timer = 0  # Remove invincibility when shield is deactivated

    def create_shield_break_effect(self):
        """Create a visual effect when the shield breaks"""
        # This method will be called when the shield breaks
        # We'll store the shield break effect data here
        self.shield_break_time = pygame.time.get_ticks()
        self.shield_break_duration = 500  # Effect lasts for 500ms
        self.shield_break_active = True

        # We'll use this in the draw method to render the effect

    def update(self):
        """Update character position and animation"""
        # If player is dead, only update death animation
        if self.is_dead:
            self.update_animation()
            return

        # Update shield cooldown
        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1

        # Update shield break effect
        if self.shield_break_active:
            current_time = pygame.time.get_ticks()
            if current_time - self.shield_break_time > self.shield_break_duration:
                self.shield_break_active = False

        # Update knockback timer if active
        if self.is_knocked_back:
            self.knockback_timer -= 1
            if self.knockback_timer <= 0:
                self.is_knocked_back = False
                self.knockback_velocity = [0, 0]  # Reset knockback velocity
            elif not self.is_shielded and (self.knockback_velocity[0] != 0 or self.knockback_velocity[1] != 0):
                # Only apply knockback movement if not shielded
                midbottom_x, midbottom_y = self.rect.midbottom
                # Round knockback velocity to prevent sub-pixel movement that causes jitter
                midbottom_x += round(self.knockback_velocity[0])
                midbottom_y += round(self.knockback_velocity[1])

                # Keep character within map boundaries
                center_x = midbottom_x
                center_y = midbottom_y - self.height // 2

                # Calculate the margins based on the character's size
                margin_x = self.width // 2
                margin_y = self.height // 2

                # Apply boundaries with margins to keep the character fully visible
                center_x = max(self.min_x + margin_x, min(center_x, self.max_x - margin_x))
                center_y = max(self.min_y + margin_y, min(center_y, self.max_y - margin_y))

                # Convert back to midbottom coordinates
                midbottom_x = center_x
                midbottom_y = center_y + self.height // 2

                # Update the character's position
                self.rect.midbottom = (midbottom_x, midbottom_y)

                # Gradually reduce knockback effect with a smoother decay
                # Use a consistent reduction factor to prevent jitter
                knockback_reduction = 0.92  # Slightly higher value for smoother deceleration
                self.knockback_velocity[0] *= knockback_reduction
                self.knockback_velocity[1] *= knockback_reduction

                # Stop knockback completely if velocity is very small to prevent tiny movements
                if abs(self.knockback_velocity[0]) < 0.1 and abs(self.knockback_velocity[1]) < 0.1:
                    self.knockback_velocity = [0, 0]

        # Update invincibility timer if active
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1

        # Update slowing effect timer if active
        if self.slow_timer > 0:
            self.slow_timer -= 1
            if self.slow_timer <= 0:
                # Reset speed multiplier when timer expires
                self.speed_multiplier = 1.0
                self.speed = self.base_speed  # Restore original speed

        # Only handle input if not attacking and not knocked back
        if not self.is_attacking and not self.is_knocked_back:
            self.handle_input()

            # Only update position if not shielded
            if not self.is_shielded and (self.velocity[0] != 0 or self.velocity[1] != 0):
                # Update position using midbottom as reference
                midbottom_x, midbottom_y = self.rect.midbottom
                midbottom_x += self.velocity[0]
                midbottom_y += self.velocity[1]

                # Keep character within map boundaries
                # Calculate the character's center position
                center_x = midbottom_x
                center_y = midbottom_y - self.height // 2

                # Calculate the margins based on the character's size
                margin_x = self.width // 2
                margin_y = self.height // 2

                # Apply boundaries with margins to keep the character fully visible
                center_x = max(self.min_x + margin_x, min(center_x, self.max_x - margin_x))
                center_y = max(self.min_y + margin_y, min(center_y, self.max_y - margin_y))

                # Convert back to midbottom coordinates
                midbottom_x = center_x
                midbottom_y = center_y + self.height // 2

                # Update the character's position
                self.rect.midbottom = (midbottom_x, midbottom_y)

        # Update animation
        self.update_animation()

    def apply_knockback(self, direction_x=0, direction_y=0):
        """Apply knockback effect to the player

        Args:
            direction_x (float): X component of knockback direction (defaults to 0)
            direction_y (float): Y component of knockback direction (defaults to 0)
        """
        # If shielded, only play the hit animation without actual knockback
        if self.is_shielded:
            # Set the direction for the shield hit animation
            if direction_x != 0 or direction_y != 0:
                # Don't change direction when hit while shielded
                # Keep the current direction for the shield hit animation

                # Reduce shield durability
                self.shield_durability -= 1

                # Check if shield is broken
                if self.shield_durability <= 0:
                    # Shield breaks - create a shield break effect
                    self.create_shield_break_effect()

                    # Deactivate shield
                    self.deactivate_shield()

                    # Apply normal knockback since shield is broken
                    self.is_knocked_back = True
                    self.knockback_timer = self.knockback_duration
                    self.hit_frame = 0
                    self.animation_timer = 0

                    # Calculate knockback velocity
                    distance = ((direction_x ** 2) + (direction_y ** 2)) ** 0.5
                    if distance > 0:
                        # Round to 2 decimal places to avoid floating point precision issues
                        self.knockback_velocity[0] = round((direction_x / distance) * self.knockback_strength, 2)
                        self.knockback_velocity[1] = round((direction_y / distance) * self.knockback_strength, 2)
                    return

                # Shield still has durability, play shield hit animation
                self.is_knocked_back = True
                self.knockback_timer = self.shield_hit_duration  # Use shield hit animation duration
                self.hit_frame = 0  # Reset hit animation frame
                self.animation_timer = 0  # Reset animation timer

                # Set zero knockback velocity (no movement)
                self.knockback_velocity = [0, 0]
            return

        # Only apply knockback if not already knocked back and not shielded
        if not self.is_knocked_back:
            self.is_knocked_back = True
            self.knockback_timer = self.knockback_duration
            self.hit_frame = 0  # Reset hit animation frame
            self.animation_timer = 0  # Reset animation timer

            # Set knockback direction if provided
            if direction_x != 0 or direction_y != 0:
                # Normalize the direction
                distance = ((direction_x ** 2) + (direction_y ** 2)) ** 0.5
                if distance > 0:
                    # Set knockback velocity based on direction and strength
                    # Round to 2 decimal places to avoid floating point precision issues
                    self.knockback_velocity[0] = round((direction_x / distance) * self.knockback_strength, 2)
                    self.knockback_velocity[1] = round((direction_y / distance) * self.knockback_strength, 2)

                    # Don't change direction when knocked back
                    # Keep the current direction for the hit animation
            else:
                # Default to zero velocity if no direction provided
                self.knockback_velocity = [0, 0]

    def take_damage(self, damage_amount=10):
        """Apply damage to the player and trigger invincibility frames"""
        # Don't take damage if shielded, invincible, or already dead
        if self.is_shielded or self.invincibility_timer > 0 or self.is_dead:
            return False

        # Reduce health
        self.current_health -= damage_amount

        # Ensure health doesn't go below 0
        if self.current_health < 0:
            self.current_health = 0

        # Check if player has died
        if self.current_health <= 0:
            self.die()
            return True

        # Start invincibility timer
        self.invincibility_timer = self.invincibility_duration

        # Return True if damage was applied
        return True

    def die(self):
        """Start the death animation and set player as dead"""
        if not self.is_dead:
            self.is_dead = True
            self.death_frame = 0
            self.death_animation_timer = 0
            self.death_animation_complete = False
            self.velocity = [0, 0]  # Stop movement
            self.is_knocked_back = False
            self.is_attacking = False
            self.is_shielded = False

    def heal(self, heal_amount=10):
        """Heal the player by the specified amount"""
        self.current_health += heal_amount

        # Ensure health doesn't exceed max health
        if self.current_health > self.max_health:
            self.current_health = self.max_health

    def apply_slowing_effect(self, speed_multiplier=0.9, duration=60):
        """Apply a slowing effect to the player

        Args:
            speed_multiplier (float): Multiplier for player speed (0.9 = 90% speed, 10% reduction)
            duration (int): Duration of the effect in frames (60 frames = 1 second at 60fps)
        """
        # Only apply if the new multiplier is slower than the current one
        if speed_multiplier < self.speed_multiplier:
            self.speed_multiplier = speed_multiplier
            self.slow_timer = duration

            # Update the current speed
            self.speed = self.base_speed * self.speed_multiplier

    def draw(self, surface, camera_x=0, camera_y=0):
        """Draw the character on the given surface, accounting for camera position"""
        # Calculate screen position for the character's feet (midbottom)
        screen_x = self.rect.midbottom[0] - camera_x
        screen_y = self.rect.midbottom[1] - camera_y

        # Determine the animation type based on the current state
        animation_type = "idle"
        if self.is_dead:
            animation_type = "death"
        elif self.is_knocked_back and self.is_shielded:
            animation_type = "shield_hit"
        elif self.is_knocked_back:
            animation_type = "hit"
        elif self.is_attacking or self.state == "attack":
            animation_type = "attack"
        elif self.is_shielded:
            animation_type = "shield"
        elif self.state == "run":
            animation_type = "run"

        # Use the current animation image directly
        draw_image = self.current_animation_image

        # Draw the character with custom alignment based on animation type and direction
        # Use the potentially modified image while self.rect maintains a consistent 16x16 collision box
        blit_aligned(
            surface,
            draw_image,
            (screen_x, screen_y),
            (16, 16),  # Base size (idle animation size)
            animation_type,
            self.direction
        )

        # Draw shield break effect if active
        if self.shield_break_active:
            # Calculate effect progress (0.0 to 1.0)
            current_time = pygame.time.get_ticks()
            progress = (current_time - self.shield_break_time) / self.shield_break_duration

            # Create expanding circle effect
            break_radius = max(1, int(40 * progress))  # Grows from 1 to 40 pixels (avoid 0)
            alpha = int(255 * (1 - progress))  # Fades from 255 to 0

            # Create surface for the effect
            break_surface = pygame.Surface((break_radius * 2, break_radius * 2), pygame.SRCALPHA)

            # Draw shattered shield effect (multiple lines radiating outward)
            for angle in range(0, 360, 30):  # 12 lines at 30-degree intervals
                rad_angle = math.radians(angle)
                inner_x = break_radius + int(break_radius * 0.3 * math.cos(rad_angle))
                inner_y = break_radius + int(break_radius * 0.3 * math.sin(rad_angle))
                outer_x = break_radius + int(break_radius * 0.9 * math.cos(rad_angle))
                outer_y = break_radius + int(break_radius * 0.9 * math.sin(rad_angle))

                # Draw line with fading color
                # Make sure alpha is clamped between 0 and 255
                clamped_alpha = max(0, min(255, alpha))
                pygame.draw.line(
                    break_surface,
                    (100, 150, 255, clamped_alpha),
                    (inner_x, inner_y),
                    (outer_x, outer_y),
                    2
                )

            # Draw the effect centered on the character
            effect_x = screen_x - break_radius
            effect_y = screen_y - break_radius - 8  # Same vertical offset as shield aura
            surface.blit(break_surface, (effect_x, effect_y))

        # Draw shield active indicator
        if self.is_shielded:
            # Draw a shield aura effect
            aura_radius = 20 + int(5 * math.sin(pygame.time.get_ticks() / 200))  # Pulsing effect
            aura_surface = pygame.Surface((aura_radius * 2, aura_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surface, (100, 150, 255, 40), (aura_radius, aura_radius), aura_radius)

            # Center the aura on the character's body, not at the feet
            # screen_y is at the feet, so move up by half the character height (8 pixels)
            aura_x = screen_x - aura_radius
            aura_y = screen_y - aura_radius - 8  # Move up by 8 pixels (half of character height)
            surface.blit(aura_surface, (aura_x, aura_y))

            # Draw shield durability indicator
            durability_width = 20
            durability_height = 3
            durability_x = screen_x - durability_width // 2
            durability_y = screen_y - 20  # Position above the character

            # Draw background bar (dark blue)
            pygame.draw.rect(surface, (20, 50, 100),
                            (durability_x, durability_y, durability_width, durability_height))

            # Draw current durability (bright blue)
            current_width = int(durability_width * (self.shield_durability / self.shield_max_durability))
            pygame.draw.rect(surface, (50, 150, 255),
                            (durability_x, durability_y, current_width, durability_height))

            # Removed the 3/3 text indicator as requested

        elif self.shield_cooldown > 0:
            # Draw a small cooldown indicator at the bottom of the character
            cooldown_width = 16
            cooldown_height = 2
            cooldown_x = screen_x - cooldown_width // 2
            cooldown_y = screen_y + 2  # Just below the character's feet

            # Calculate cooldown progress (0.0 to 1.0)
            cooldown_progress = self.shield_cooldown / self.shield_cooldown_duration

            # Draw background bar (gray)
            pygame.draw.rect(surface, (100, 100, 100),
                            (cooldown_x, cooldown_y, cooldown_width, cooldown_height))

            # Draw remaining cooldown (red)
            remaining_width = int(cooldown_width * cooldown_progress)
            pygame.draw.rect(surface, (200, 50, 50),
                            (cooldown_x, cooldown_y, remaining_width, cooldown_height))

        # Debug: Draw a dot at the character's feet (midbottom) for reference
        # Uncomment this to see the alignment point
        # pygame.draw.circle(surface, (255, 0, 0), (screen_x, screen_y), 2)

        # Debug: Draw the collision box (16x16)
        # Uncomment this to see the collision box
        # debug_rect = pygame.Rect(
        #     self.rect.x - camera_x,
        #     self.rect.y - camera_y,
        #     self.rect.width,
        #     self.rect.height
        # )
        # pygame.draw.rect(surface, (255, 0, 0), debug_rect, 1)

