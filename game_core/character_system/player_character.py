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

        # Animation and state variables
        self.direction = "down"  # Current facing direction
        self.state = "idle"  # Current animation state (idle, walk, attack)
        self.is_attacking = False  # Attack state flag

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

        # Health system
        self.max_health = 100
        self.current_health = 100
        self.invincibility_timer = 0
        self.invincibility_duration = 60  # 1 second of invincibility after being hit (60 frames)

        # Death state
        self.is_dead = False

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

        # Fractional position tracking for smooth movement
        self.precise_x = float(x)  # Precise X position (with decimals)
        self.precise_y = float(y)  # Precise Y position (with decimals)

        # Initialize movement system (import here to avoid circular imports)
        from game_core.playscreen_components.player_system.player_movement import PlayerMovement
        self.movement_system = PlayerMovement(self)

        # Initialize animation system (import here to avoid circular imports)
        from game_core.playscreen_components.player_system.player_animation import PlayerAnimation
        self.animation_system = PlayerAnimation(self)

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
            # Use the new movement system to handle input
            movement_data = self.movement_system.handle_movement_input(keys)

            # Apply movement data to player
            self.velocity = movement_data['velocity']
            self.direction = movement_data['direction']
            self.state = movement_data['state']

            # Update speed for compatibility with existing systems
            self.speed = movement_data['current_speed'] * self.speed_multiplier

    def get_movement_info(self):
        """Get information about the current movement state"""
        if hasattr(self, 'movement_system'):
            return self.movement_system.get_movement_state_info()
        return {}

    def update_animation(self):
        """Update the character's animation frame using the animation system"""
        # Use the new animation system to handle all animation logic
        animation_data = self.animation_system.update_animation()

        # Apply the animation data to the player
        self.image = animation_data['image']
        self.current_animation_image = animation_data['image']

        # Handle death animation completion
        if self.is_dead and animation_data.get('animation_complete', False):
            # Death animation is complete - could trigger game over or other logic
            pass

        # Store the current position before updating the rect
        current_midbottom = self.rect.midbottom

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
            self.animation_system.start_attack_animation()
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

        # Reset animation state and get the first frame of the current animation
        self.animation_system.reset_animation_state()
        animation_data = self.animation_system.update_animation()

        # Update the image
        self.image = animation_data['image']
        self.current_animation_image = animation_data['image']

        # Update the rect while preserving the midbottom position
        self.rect = self.image.get_rect()
        self.rect.midbottom = current_midbottom

        # Sync precise position with rect position
        self.precise_x = float(current_midbottom[0])
        self.precise_y = float(current_midbottom[1] - self.height // 2)

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
                # Sync precise position with rect after knockback to prevent jitter
                self.precise_x = float(self.rect.midbottom[0])
                self.precise_y = float(self.rect.midbottom[1] - self.height // 2)
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
                # Update precise position with fractional movement
                self.precise_x += self.velocity[0]
                self.precise_y += self.velocity[1]

                # Calculate midbottom position from precise coordinates
                # precise_x and precise_y represent the character's center
                midbottom_x = self.precise_x
                midbottom_y = self.precise_y + self.height // 2

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

                # Update precise position if boundaries were hit
                if center_x != midbottom_x:
                    self.precise_x = center_x
                if center_y != midbottom_y - self.height // 2:
                    self.precise_y = center_y

                # Convert back to midbottom coordinates
                midbottom_x = center_x
                midbottom_y = center_y + self.height // 2

                # Update the character's rect position (rounded to integers)
                self.rect.midbottom = (int(round(midbottom_x)), int(round(midbottom_y)))



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
                    self.animation_system.start_hit_animation()

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
                self.animation_system.start_hit_animation()

                # Set zero knockback velocity (no movement)
                self.knockback_velocity = [0, 0]
            return

        # Only apply knockback if not already knocked back and not shielded
        if not self.is_knocked_back:
            self.is_knocked_back = True
            self.knockback_timer = self.knockback_duration
            self.animation_system.start_hit_animation()

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
            self.animation_system.start_death_animation()
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

    def draw(self, surface, camera_x=0, camera_y=0, zoom_factor=1.0):
        """Draw the character on the given surface, accounting for camera position and zoom"""
        # Calculate screen position for the character's feet (midbottom)
        # Keep logical coordinates, only scale for visual representation
        logical_screen_x = self.rect.midbottom[0] - camera_x
        logical_screen_y = self.rect.midbottom[1] - camera_y

        # Scale the screen position for zoom
        screen_x = logical_screen_x * zoom_factor
        screen_y = logical_screen_y * zoom_factor

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

        # Scale the image if zoom factor is not 1.0
        if zoom_factor != 1.0:
            # Calculate new size based on zoom factor
            original_size = draw_image.get_size()
            new_width = int(original_size[0] * zoom_factor)
            new_height = int(original_size[1] * zoom_factor)
            draw_image = pygame.transform.scale(draw_image, (new_width, new_height))

        # Calculate scaled base size for alignment
        scaled_base_size = (int(16 * zoom_factor), int(16 * zoom_factor))

        # Draw the character with custom alignment based on animation type and direction
        # Use the potentially modified image while self.rect maintains a consistent 16x16 collision box
        blit_aligned(
            surface,
            draw_image,
            (screen_x, screen_y),
            scaled_base_size,  # Scaled base size for proper alignment
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
            durability_width = int(20 * zoom_factor)  # Scale with zoom
            durability_height = int(3 * zoom_factor)  # Scale with zoom
            durability_x = screen_x - durability_width // 2
            durability_y = screen_y - (20 * zoom_factor)  # Position above the character, scaled

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
            cooldown_width = int(16 * zoom_factor)  # Scale with zoom
            cooldown_height = int(2 * zoom_factor)  # Scale with zoom
            cooldown_x = screen_x - cooldown_width // 2
            cooldown_y = screen_y + (2 * zoom_factor)  # Just below the character's feet, scaled

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

