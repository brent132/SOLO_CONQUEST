"""
Bomberplant Enemy - A stationary enemy that launches bombs
"""
import pygame
import os
import math
from enemy_system.enemy import Enemy

class Bomberplant(Enemy):
    """Bomberplant enemy class - a stationary enemy that launches bombs"""
    def __init__(self, x, y):
        """Initialize the Bomberplant enemy"""
        super().__init__(x, y, enemy_type="bomberplant")

        # Load animations
        self._load_animations()

        # Create the rect but don't set position yet - EnemyManager will handle that
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # Initialize all properties
        self._init_basic_properties()
        self._init_combat_properties()
        self._init_targeting_properties()
        self._init_bomb_properties()
        self._init_health_properties()
        self._init_health_bar()

        # Set initial animation
        self.update_animation()

    def _load_animations(self):
        """Load all animation sprites for the bomberplant"""
        # Load bomberplant animations
        self.load_animation("idle", "right", "Enemies_Sprites/Bomberplant_Sprites/bomberplant_idle_anim_all_dir")
        self.load_animation("hit", "right", "Enemies_Sprites/Bomberplant_Sprites/bomberplant_hit_anim_all_dir")
        self.load_animation("death", "right", "Enemies_Sprites/Bomberplant_Sprites/bomberplant_death_anim_all_dir")
        self.load_animation("attack", "right", "Enemies_Sprites/Bomberplant_Sprites/bomberplant_attack_anim_all_dir")

        # Load mark and bomb animations
        self.mark_sprites = self.load_animation_frames("Enemies_Sprites/Bomberplant_Sprites/bomb_hit_marker_fx_anim")
        self.bomb_up_sprites = self.load_animation_frames("Enemies_Sprites/Bomberplant_Sprites/bomb_going_up_anim")
        self.bomb_down_sprites = self.load_animation_frames("Enemies_Sprites/Bomberplant_Sprites/bomb_going_down_anim")
        self.bomb_explosion_sprites = self.load_animation_frames("Enemies_Sprites/Bomberplant_Sprites/bomb_explosion_anim")

    def _init_basic_properties(self):
        """Initialize basic properties for the bomberplant"""
        # Bomberplant is stationary
        self.speed = 0
        self.debug_mode = False

        # Store position as floats for precise movement
        self.float_x = 0.0
        self.float_y = 0.0

    def _init_combat_properties(self):
        """Initialize combat-related properties"""
        # Knockback properties
        self.knockback_strength = 5.0
        self.knockback_cooldown = 0
        self.knockback_cooldown_time = 45  # 0.75 seconds at 60fps

        # Player damage properties
        self.player_knockback_strength = 4.0
        self.player_damage = 15

        # Bomb explosion properties
        self.bomb_explosion_damage = 20
        self.bomb_explosion_knockback_strength = 8.0
        self.bomb_explosion_radius = 40

    def _init_targeting_properties(self):
        """Initialize targeting and range properties"""
        # Range properties
        self.attack_range = 5 * 16  # 5 tiles
        self.show_range = True
        self.player_in_range = False
        self.player_detected = False
        self.player_in_range_timer = 0
        self.player_targeting_delay = 30  # 0.5 seconds at 60fps

        # Mark properties
        self.show_mark = True
        self.mark_position = [0, 0]
        self.mark_frame = 0
        self.mark_animation_timer = 0
        self.mark_animation_speed = 0.1
        self.mark_active = False
        self.mark_duration = 120  # 2 seconds at 60fps
        self.mark_timer = 0

        # Attack properties
        self.is_attacking = False
        self.attack_frame = 0
        self.attack_animation_timer = 0
        self.attack_animation_speed = 0.15
        self.attack_cooldown = 0
        self.attack_cooldown_time = 120  # 2 seconds at 60fps

    def _init_bomb_properties(self):
        """Initialize bomb-related properties"""
        # Bomb state and animation
        self.bomb_state = "none"  # none, up, down, explosion
        self.bomb_frame = 0
        self.bomb_animation_timer = 0
        self.bomb_animation_speed = 0.12

        # Bomb position and movement
        self.bomb_position = [0, 0]
        self.bomb_target_position = [0, 0]
        self.bomb_start_position = [0, 0]
        self.bomb_max_height = 60
        self.bomb_travel_progress = 0.0
        self.bomb_travel_speed = 0.01
        self.bomb_arc_type = "quadratic"

        # Explosion effects
        self.explosion_damage_applied = False
        self.explosion_knockback_direction = [0, 0]

    def _init_health_properties(self):
        """Initialize health and damage properties"""
        # Health properties
        self.max_health = 100
        self.current_health = 100

        # Hit animation properties
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 20
        self.hit_frame = 0
        self.hit_animation_speed = 0.15

        # Death animation properties
        self.is_dying = False
        self.is_dead = False
        self.death_timer = 0
        self.death_duration = 60
        self.death_frame = 0
        self.death_animation_speed = 0.1

        # Damage cooldown
        self.damage_cooldown = 0
        self.damage_cooldown_time = 30  # 0.5 seconds at 60fps

    def _init_health_bar(self):
        """Initialize health bar properties and assets"""
        # Health bar properties
        self.show_health_bar = False
        self.health_bar_timer = 0
        self.health_bar_duration = 120  # 2 seconds at 60fps

        # Load health bar assets
        self.health_bar_bg = self.load_image("Enemies_Sprites/Hud_Ui/health_hud.png")
        self.health_indicator = self.load_image("Enemies_Sprites/Hud_Ui/health_bar_hud.png")

        # Scale health bar
        self._scale_health_bar()

    def _scale_health_bar(self):
        """Scale health bar assets to appropriate size"""
        scale_factor = 0.5
        if self.health_bar_bg and self.health_indicator:
            # Scale background
            self.health_bar_bg = pygame.transform.scale(
                self.health_bar_bg,
                (int(self.health_bar_bg.get_width() * scale_factor),
                 int(self.health_bar_bg.get_height() * scale_factor))
            )

            # Scale indicator (90% of background width)
            indicator_scale = scale_factor * 0.9
            self.health_indicator = pygame.transform.scale(
                self.health_indicator,
                (int(self.health_indicator.get_width() * indicator_scale),
                 int(self.health_indicator.get_height() * indicator_scale))
            )

    def update(self, player_x, player_y, collision_handler=None, tile_mapping=None, map_data=None):
        """Update bomberplant position and animation

        Args:
            player_x (int): Player's x position
            player_y (int): Player's y position
            collision_handler (CollisionHandler, optional): Collision handler (unused)
            tile_mapping (dict, optional): Tile mapping data (unused)
            map_data (dict, optional): Map data (unused)
        """
        # Unused parameters are intentional for compatibility with enemy manager
        # pylint: disable=unused-argument

        # Skip updates if dead
        if self.is_dead:
            return

        # Update all timers and cooldowns
        self._update_timers()

        # Update bomb animations and check for explosion damage
        self._update_bomb_state(player_x, player_y)

        # Maintain position (bomberplant is stationary)
        self._maintain_position()

        # Handle player targeting and mark placement
        self._handle_targeting(player_x, player_y)

        # Update mark animation if active
        self._update_mark_animation()

        # Log debug information if debug mode is enabled
        self._log_debug_info()

        # Update state based on current condition
        self._update_state()

        # Update animation
        self.update_animation()

    def _update_timers(self):
        """Update all timers and cooldowns"""
        # Update knockback cooldown
        if self.knockback_cooldown > 0:
            self.knockback_cooldown -= 1

        # Update hit timer
        if self.hit_timer > 0:
            self.hit_timer -= 1
            if self.hit_timer <= 0:
                self.is_hit = False

        # Update death timer
        if self.death_timer > 0:
            self.death_timer -= 1

        # Update damage cooldown
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1

        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Update health bar timer
        if self.health_bar_timer > 0:
            self.health_bar_timer -= 1
            if self.health_bar_timer <= 0:
                self.show_health_bar = False

    def _update_bomb_state(self, player_x, player_y):
        """Update bomb animations and check for explosion damage"""
        # Update bomb animations
        self.update_bomb_animation()

        # Check for bomb explosion damage to player
        if self.bomb_state == "explosion" and not self.explosion_damage_applied:
            # Apply damage and knockback to player if they're within explosion radius
            self.check_explosion_damage(player_x, player_y)

    def _maintain_position(self):
        """Maintain the bomberplant's position (it's stationary)"""
        # Initialize float position if not already set
        if self.float_x == 0.0 and self.float_y == 0.0:
            self.float_x = float(self.rect.x)
            self.float_y = float(self.rect.y)

        # Ensure position is maintained - bomberplant never moves
        # Calculate the original grid position (16x16 grid)
        grid_x = round(self.float_x / 16) * 16
        grid_y = round(self.float_y / 16) * 16

        # Reset to grid position
        self.rect.x = grid_x
        self.rect.y = grid_y
        self.float_x = float(grid_x)
        self.float_y = float(grid_y)

    def _handle_targeting(self, player_x, player_y):
        """Handle player targeting and mark placement"""
        # Check if player is in range
        is_in_range = self.is_player_in_range(player_x, player_y)

        # Handle player entering and leaving range
        if is_in_range:
            # Player is in range, increment timer
            if self.player_in_range_timer < self.player_targeting_delay:
                self.player_in_range_timer += 1

            # Only set player_in_range to true after delay
            if self.player_in_range_timer >= self.player_targeting_delay:
                self.player_in_range = True
        else:
            # Player left range, reset timer and flag
            self.player_in_range_timer = 0
            self.player_in_range = False

        # Store whether player is in detection range (for circle color)
        self.player_detected = is_in_range

        # Place a new mark if conditions are met
        if (self.mark_sprites and len(self.mark_sprites) > 0 and
            self.player_in_range and self.show_mark and
            not self.mark_active and self.bomb_state == "none" and
            not self.is_attacking):

            # Set mark position to current player position
            self.mark_position = [player_x, player_y]
            self.mark_active = True
            self.mark_timer = self.mark_duration
            self.mark_frame = 0  # Reset animation frame

            # Debug output for new mark
            if self.debug_mode:
                from debug_utils import debug_manager
                debug_manager.log(f"New mark placed at: {self.mark_position}", "enemy")

    def _update_mark_animation(self):
        """Update mark animation if active"""
        if not self.mark_active or not self.mark_sprites or len(self.mark_sprites) == 0:
            return

        # Update mark animation
        self.mark_animation_timer += self.mark_animation_speed
        if self.mark_animation_timer >= 1:
            self.mark_animation_timer = 0
            self.mark_frame = (self.mark_frame + 1) % len(self.mark_sprites)

        # Update mark timer
        self.mark_timer -= 1
        if self.mark_timer <= 0:
            # Don't deactivate the mark yet - we need it for the bomb target
            # Instead, just start the attack animation if conditions are met
            if (not self.is_attacking and not self.is_hit and
                not self.is_dying and self.attack_cooldown <= 0 and
                self.bomb_state == "none"):
                self.start_attack_animation()
                # Mark will be deactivated after the bomb explosion completes

    def _log_debug_info(self):
        """Log debug information if debug mode is enabled"""
        if not self.debug_mode:
            return

        from debug_utils import debug_manager

        # Show targeting information
        if self.player_detected:
            debug_manager.log(f"Player DETECTED in range: {self.player_detected}, targeting timer: {self.player_in_range_timer}/{self.player_targeting_delay}", "enemy")

        if self.player_in_range:
            debug_manager.log(f"Player TARGETED (delay complete): {self.player_in_range}", "enemy")

        if self.mark_active and self.show_mark and self.mark_sprites and len(self.mark_sprites) > 0:
            debug_manager.log(f"Mark active at: {self.mark_position}, frame: {self.mark_frame}/{len(self.mark_sprites)-1}, time left: {self.mark_timer}/{self.mark_duration}", "enemy")

        if self.is_attacking:
            debug_manager.log(f"Bomberplant attacking! Frame: {self.attack_frame}", "enemy")

        if self.bomb_state != "none":
            debug_manager.log(f"Bomb state: {self.bomb_state}, frame: {self.bomb_frame}, position: {self.bomb_position}", "enemy")

    def _update_state(self):
        """Update state based on current condition"""
        if self.is_hit:
            self.state = "hit"
        elif self.is_dying:
            self.state = "death"
        elif self.is_attacking:
            self.state = "attack"
        else:
            self.state = "idle"

    def update_bomb_animation(self):
        """Update the bomb animation based on its current state"""
        # Skip if bomb state is none
        if self.bomb_state == "none":
            return

        # Validate bomb sprites are loaded for the current state
        if (self.bomb_state == "up" and (not self.bomb_up_sprites or len(self.bomb_up_sprites) == 0)) or \
           (self.bomb_state == "down" and (not self.bomb_down_sprites or len(self.bomb_down_sprites) == 0)) or \
           (self.bomb_state == "explosion" and (not self.bomb_explosion_sprites or len(self.bomb_explosion_sprites) == 0)):
            print(f"Error: Missing bomb sprites for state: {self.bomb_state}")
            # Reset to a safe state
            self.bomb_state = "none"
            self.bomb_frame = 0
            self.bomb_animation_timer = 0
            self.bomb_travel_progress = 0.0
            return

        # Update the bomb animation frame based on the current state
        self._update_bomb_frame()

        # Update the bomb position based on the current state
        if self.bomb_state in ["up", "down"]:
            # Update bomb travel progress
            self.bomb_travel_progress += self.bomb_travel_speed

            # Check for state transitions
            self._check_bomb_state_transitions()

            # Calculate and update bomb position
            self._calculate_bomb_position()

        # Handle explosion animation separately
        elif self.bomb_state == "explosion":
            # Explosion animation is handled in _update_bomb_frame
            pass

    def _update_bomb_frame(self):
        """Update the bomb animation frame based on its current state"""
        # Get the appropriate animation speed based on state
        animation_speed = self.bomb_animation_speed
        if self.bomb_state == "explosion":
            # Use a slightly slower animation speed for explosion
            animation_speed = self.bomb_animation_speed * 0.8

        # Update animation timer
        self.bomb_animation_timer += animation_speed
        if self.bomb_animation_timer >= 1:
            self.bomb_animation_timer = 0

            # For explosion, we don't loop the animation
            if self.bomb_state == "explosion":
                self.bomb_frame += 1

                # Check if explosion animation is complete
                if self.bomb_frame >= len(self.bomb_explosion_sprites):
                    self._reset_bomb_after_explosion()
                    return
            else:
                # For up and down animations, loop the frames
                sprite_list = self.bomb_up_sprites if self.bomb_state == "up" else self.bomb_down_sprites
                self.bomb_frame = (self.bomb_frame + 1) % len(sprite_list)

    def _check_bomb_state_transitions(self):
        """Check and handle bomb state transitions based on travel progress"""
        # Transition from up to down at the midpoint
        if self.bomb_state == "up" and self.bomb_travel_progress >= 0.5:
            self.bomb_state = "down"
            self.bomb_frame = 0
            self.bomb_animation_timer = 0
            # Don't reset travel progress - maintain continuity

        # Transition from down to explosion at the end
        elif self.bomb_state == "down" and self.bomb_travel_progress >= 1.0:
            # Ensure the bomb is exactly at the target position before explosion
            self.bomb_position = self.bomb_target_position.copy()
            self.bomb_state = "explosion"
            self.bomb_frame = 0
            self.bomb_animation_timer = 0

            # Set explosion flag to ensure damage is only applied once
            self.explosion_damage_applied = False

    def _calculate_bomb_position(self):
        """Calculate the bomb position along its arc trajectory"""
        # Get the start and target positions
        start_x, start_y = self.bomb_start_position
        target_x, target_y = self.bomb_target_position

        # Clamp travel progress to valid range
        t = max(0.0, min(1.0, self.bomb_travel_progress))

        # Calculate horizontal position with simple linear interpolation
        self.bomb_position[0] = start_x + (target_x - start_x) * t

        # Calculate vertical position with parabolic arc
        # For a complete arc from start to target:
        # - At t=0: position is at start
        # - At t=0.5: position is at highest point of arc
        # - At t=1: position is at target

        # Calculate base Y position (linear path from start to target)
        base_y = start_y + (target_y - start_y) * t

        # Calculate arc height using parabolic function
        # The 4 * h * t * (1-t) formula creates a parabola with max height at t=0.5
        arc_height = 4 * self.bomb_max_height * t * (1 - t)

        # Apply arc height to get final Y position
        self.bomb_position[1] = base_y - arc_height

    def _reset_bomb_after_explosion(self):
        """Reset all bomb-related states after explosion animation completes"""
        # Reset bomb state
        self.bomb_state = "none"
        self.bomb_frame = 0
        self.bomb_animation_timer = 0
        self.bomb_travel_progress = 0.0

        # Ensure explosion damage flag is reset
        self.explosion_damage_applied = False

        # Clear explosion knockback direction
        self.explosion_knockback_direction = [0, 0]

        # Clear bomb positions
        self.bomb_position = [0, 0]
        self.bomb_target_position = [0, 0]
        self.bomb_start_position = [0, 0]

        # Deactivate the mark
        self.mark_active = False
        self.mark_frame = 0
        self.mark_animation_timer = 0
        self.mark_timer = 0

        # Set state back to idle
        self.state = "idle"

    def check_explosion_damage(self, player_x, player_y):
        """Check if player is within explosion radius and apply damage and knockback

        Args:
            player_x (int): Player's x position
            player_y (int): Player's y position
        """
        # Only check for explosion damage at the start of the explosion animation
        # This ensures we only set the flag once at the beginning of the explosion
        if self.bomb_frame == 0 and not self.explosion_damage_applied:
            # Calculate distance between explosion center and player
            dx = player_x - self.bomb_position[0]
            dy = player_y - self.bomb_position[1]
            distance = ((dx ** 2) + (dy ** 2)) ** 0.5

            # Check if player is within explosion radius
            if distance <= self.bomb_explosion_radius:
                # We need to apply damage and knockback to the player
                # This will be handled by the enemy_manager in the next update cycle
                # We'll set a flag to indicate that damage should be applied
                self.explosion_damage_applied = True

                # Handle the case where player is at the center of the explosion
                if distance < 1.0:
                    # If player is at the center, we'll use a random direction in apply_knockback_to_player
                    # Just store zeros for now
                    self.explosion_knockback_direction = [0, 0]
                else:
                    # Store the knockback direction for use in apply_knockback_to_player
                    self.explosion_knockback_direction = [dx, dy]

                # We'll apply the actual damage and knockback in apply_knockback_to_player
                # which gets called by the enemy_manager with the actual player object

    def update_animation(self):
        """Update the bomberplant's animation frame"""
        # First, check if we need to update bomb animations
        # This takes priority over other animations to ensure bomb animations continue
        if self.bomb_state != "none":
            self._update_bomb_with_hit_flash()
            return

        # Get the appropriate animation key for the current state
        current_animation_key = self._get_animation_key()

        # If we don't have a valid animation, return
        if not current_animation_key:
            return

        # Handle different animation states
        if self.state == "death" and self.is_dying:
            self._update_death_animation(current_animation_key)
        elif self.state == "hit" and self.is_hit:
            self._update_hit_animation(current_animation_key)
        elif self.state == "attack" and self.is_attacking:
            self._update_attack_animation(current_animation_key)
        else:
            self._update_idle_animation(current_animation_key)

    def _update_bomb_with_hit_flash(self):
        """Update bomb animation with hit flash effect if hit"""
        # Continue updating bomb animations even if hit
        self.update_bomb_animation()

        # If we're also in hit state, we'll flash the hit animation
        # but continue the bomb animation in the background
        if self.is_hit and self.hit_timer > 0:
            # Flash hit animation every few frames
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                hit_key = "hit_right"
                if hit_key in self.sprites and self.sprites[hit_key]:
                    # Calculate hit frame
                    total_frames = len(self.sprites[hit_key])
                    progress = 1.0 - (self.hit_timer / self.hit_duration)
                    hit_frame = min(int(progress * total_frames), total_frames - 1)
                    # Show hit frame
                    self.image = self.sprites[hit_key][hit_frame]

    def _get_animation_key(self):
        """Get the appropriate animation key for the current state"""
        # Determine the animation key based on state
        if self.state == "hit":
            current_animation_key = "hit_right"
        elif self.state == "death":
            current_animation_key = "death_right"
        elif self.state == "attack":
            current_animation_key = "attack_right"
        else:
            current_animation_key = "idle_right"

        # If the animation doesn't exist, fall back to idle
        if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
            current_animation_key = "idle_right"

        # If we still don't have a valid animation, return None
        if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
            return None

        return current_animation_key

    def _update_death_animation(self, animation_key):
        """Update death animation"""
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

    def _update_hit_animation(self, animation_key):
        """Update hit animation"""
        # Calculate which frame to show based on hit timer
        total_frames = len(self.sprites[animation_key])

        # Calculate current frame based on remaining hit timer
        if self.hit_timer > 0:
            progress = 1.0 - (self.hit_timer / self.hit_duration)
            self.hit_frame = min(int(progress * total_frames), total_frames - 1)
        else:
            # If hit timer expired, use the last frame
            self.hit_frame = total_frames - 1

        # Use hit frame for rendering
        self.image = self.sprites[animation_key][self.hit_frame]

    def _update_attack_animation(self, animation_key):
        """Update attack animation"""
        # Update attack animation timer
        self.attack_animation_timer += self.attack_animation_speed
        if self.attack_animation_timer >= 1:
            self.attack_animation_timer = 0
            self.attack_frame += 1

            # Check if attack animation is complete
            if self.attack_frame >= len(self.sprites[animation_key]):
                self._handle_attack_completion()
                return

        # Use attack frame for rendering
        frame_index = min(self.attack_frame, len(self.sprites[animation_key]) - 1)
        self.image = self.sprites[animation_key][frame_index]

    def _handle_attack_completion(self):
        """Handle what happens when attack animation completes"""
        # Start the bomb going up animation if mark is still active and no bomb is already active
        if self.mark_active and self.bomb_state == "none":
            # Transition directly to bomb up animation without going back to idle
            # This creates a smoother transition between attack and bomb animations
            self.start_bomb_up_animation()

        # Reset attack state
        self.is_attacking = False
        self.attack_frame = 0
        self.attack_animation_timer = 0
        self.attack_cooldown = self.attack_cooldown_time

        # If we didn't start a bomb animation, reset to idle
        if self.bomb_state == "none":
            self.state = "idle"

    def _update_idle_animation(self, animation_key):
        """Update idle animation"""
        # Update animation timer
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.frame = (self.frame + 1) % len(self.sprites[animation_key])

        # Update image
        self.image = self.sprites[animation_key][self.frame]

    def take_damage(self, damage_amount=10, knockback_x=0, knockback_y=0, collision_handler=None, tile_mapping=None, map_data=None):
        """Apply damage to the bomberplant and trigger hit animation

        Args:
            damage_amount (int): Amount of damage to apply
            knockback_x (float): X component of knockback direction
            knockback_y (float): Y component of knockback direction
            collision_handler: Optional collision handler for wall detection (unused for bomberplant)
            tile_mapping: Optional tile mapping for collision detection (unused for bomberplant)
            map_data: Optional map data for collision detection (unused for bomberplant)
        """
        # Only take damage if not already dying or dead and not on cooldown
        if self.is_dying or self.is_dead or self.damage_cooldown > 0:
            return False

        # Reduce health
        self.current_health -= damage_amount

        # Show health bar
        self.show_health_bar = True
        self.health_bar_timer = self.health_bar_duration

        # Start damage cooldown to prevent multiple hits from a single attack
        self.damage_cooldown = self.damage_cooldown_time

        # Don't reset bomb animations when taking damage
        # Only reset attack animation if we're in the attack state
        if self.is_attacking and self.bomb_state == "none":
            self.is_attacking = False
            self.attack_frame = 0
            self.attack_animation_timer = 0

        # Check if bomberplant should die
        if self.current_health <= 0:
            self.current_health = 0
            self.start_death_animation()
            return True

        # Set direction based on knockback for animation purposes
        if knockback_x != 0 or knockback_y != 0:
            if abs(knockback_x) > abs(knockback_y):
                self.direction = "right" if knockback_x > 0 else "left"
            else:
                self.direction = "down" if knockback_y > 0 else "up"

        # Start hit animation
        self.start_hit_animation()

        return True

    def start_hit_animation(self):
        """Start the hit animation sequence"""
        # Don't restart the animation if already in hit state
        if self.is_hit:
            return

        # Save the current bomb state before setting hit state
        previous_bomb_state = self.bomb_state
        previous_bomb_frame = self.bomb_frame
        previous_bomb_animation_timer = self.bomb_animation_timer
        previous_bomb_travel_progress = self.bomb_travel_progress
        previous_bomb_position = self.bomb_position.copy() if self.bomb_position else [0, 0]
        previous_bomb_target_position = self.bomb_target_position.copy() if self.bomb_target_position else [0, 0]
        previous_bomb_start_position = self.bomb_start_position.copy() if self.bomb_start_position else [0, 0]
        previous_mark_active = self.mark_active
        previous_mark_position = self.mark_position.copy() if self.mark_position else [0, 0]

        # Set hit state
        self.is_hit = True
        self.hit_timer = self.hit_duration
        self.hit_frame = 0

        # Only change state to hit if we're not in a bomb animation
        if self.bomb_state == "none":
            self.state = "hit"

        # Always use the right direction for hit animation
        self.direction = "right"

        # Force the current frame to be the first frame of the hit animation
        hit_key = "hit_right"
        if hit_key in self.sprites and self.sprites[hit_key]:
            self.image = self.sprites[hit_key][0]

        # Restore bomb state if it was active
        if previous_bomb_state != "none":
            self.bomb_state = previous_bomb_state
            self.bomb_frame = previous_bomb_frame
            self.bomb_animation_timer = previous_bomb_animation_timer
            self.bomb_travel_progress = previous_bomb_travel_progress
            self.bomb_position = previous_bomb_position
            self.bomb_target_position = previous_bomb_target_position
            self.bomb_start_position = previous_bomb_start_position
            self.mark_active = previous_mark_active
            self.mark_position = previous_mark_position

    def reset_attack_states(self):
        """Reset all attack-related states"""
        # Debug output before reset
        if self.bomb_state != "none" or self.is_attacking or self.mark_active:
            print(f"Resetting attack states - previous states: bomb={self.bomb_state}, attacking={self.is_attacking}, mark_active={self.mark_active}")

        # Reset mark state
        self.mark_active = False
        self.mark_frame = 0
        self.mark_animation_timer = 0
        self.mark_timer = 0

        # Reset attack state
        self.is_attacking = False
        self.attack_frame = 0
        self.attack_animation_timer = 0

        # Reset bomb state
        self.bomb_state = "none"
        self.bomb_frame = 0
        self.bomb_animation_timer = 0
        self.bomb_travel_progress = 0.0

        # Clear bomb position and target
        self.bomb_position = [0, 0]
        self.bomb_target_position = [0, 0]

        # Set state back to idle
        self.state = "idle"

        # Note: We don't reset player_in_range or player_detected here
        # so the targeting can continue after attack animations are reset

    def start_attack_animation(self):
        """Start the attack animation sequence"""
        # Don't restart the animation if already attacking
        if self.is_attacking:
            return

        # Make sure no other attack animations are running
        if self.bomb_state != "none":
            return

        # Set attack state
        self.is_attacking = True
        self.attack_frame = 0
        self.attack_animation_timer = 0
        self.state = "attack"

        # Always use the right direction for attack animation
        self.direction = "right"

        # Force the current frame to be the first frame of the attack animation
        attack_key = "attack_right"
        if attack_key in self.sprites and self.sprites[attack_key]:
            self.image = self.sprites[attack_key][0]

    def start_bomb_up_animation(self):
        """Start the bomb going up animation"""
        # Don't start a new bomb animation if one is already active or if we're in a special state
        if self.bomb_state != "none" or self.is_hit or self.is_dying or self.is_dead:
            return

        # Don't start if no mark is active
        if not self.mark_active:
            return

        # Validate that bomb sprites are loaded
        if not self.bomb_up_sprites or len(self.bomb_up_sprites) == 0:
            return

        # Reset animation state
        self.bomb_state = "up"
        self.bomb_frame = 0
        self.bomb_animation_timer = 0
        self.bomb_travel_progress = 0.0

        # Set bomb starting position (slightly above the bomberplant to avoid clipping)
        self.bomb_start_position = [self.rect.centerx, self.rect.centery - 24]

        # Initialize current position to the starting position
        self.bomb_position = self.bomb_start_position.copy()

        # Set bomb target position to the mark position
        self.bomb_target_position = self.mark_position.copy()

        # Ensure we're not in attack state anymore
        if self.state == "attack":
            self.state = "idle"

        # Ensure the bomb animation is prioritized
        self.is_attacking = False

    def start_bomb_down_animation(self):
        """Start the bomb going down animation"""
        # This method is kept for compatibility but is no longer directly called
        # State transitions are now handled in _check_bomb_state_transitions

        # Only allow transition from "up" state to "down" state
        if self.bomb_state != "up":
            return

        # Validate that bomb sprites are loaded
        if not self.bomb_down_sprites or len(self.bomb_down_sprites) == 0:
            # Reset to a safe state
            self.bomb_state = "none"
            self.bomb_frame = 0
            self.bomb_animation_timer = 0
            self.bomb_travel_progress = 0.0
            return

        # Set bomb state to down
        self.bomb_state = "down"
        self.bomb_frame = 0
        self.bomb_animation_timer = 0
        # Don't reset travel progress - maintain continuity

    def start_bomb_explosion_animation(self):
        """Start the bomb explosion animation"""
        # This method is kept for compatibility but is no longer directly called
        # State transitions are now handled in _check_bomb_state_transitions

        # Only allow transition from "down" state to "explosion" state
        if self.bomb_state != "down":
            return

        # Validate that bomb sprites are loaded
        if not self.bomb_explosion_sprites or len(self.bomb_explosion_sprites) == 0:
            # Reset to a safe state
            self.bomb_state = "none"
            self.bomb_frame = 0
            self.bomb_animation_timer = 0
            self.bomb_travel_progress = 0.0
            self.mark_active = False  # Deactivate mark since we're skipping the explosion
            return

        # Ensure the bomb is exactly at the target position before explosion
        self.bomb_position = self.bomb_target_position.copy()

        # Set bomb state to explosion
        self.bomb_state = "explosion"
        self.bomb_frame = 0
        self.bomb_animation_timer = 0

    def start_death_animation(self):
        """Start the death animation sequence"""
        self.is_dying = True
        self.is_hit = False  # Cancel any hit animation
        self.death_timer = self.death_duration
        self.death_frame = 0
        self.animation_timer = 0
        self.state = "death"
        self.velocity = [0, 0]  # Stop movement

        # Reset all attack animations when dying
        self.reset_attack_states()

        # Always use the right direction for death animation
        self.direction = "right"

        # Force the current frame to be the first frame of the death animation
        death_key = "death_right"
        if death_key in self.sprites and self.sprites[death_key]:
            self.image = self.sprites[death_key][0]

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

    def load_animation_frames(self, directory):
        """Load all animation frames from a directory"""
        frames = []
        try:
            # Get the full path to the directory
            full_dir = os.path.join(os.getcwd(), directory)

            # Check if directory exists
            if not os.path.exists(full_dir):
                print(f"Animation directory not found: {directory}")
                return frames

            # Get all PNG files in the directory
            files = [f for f in os.listdir(full_dir) if f.endswith('.png')]

            # Sort files by name (assuming they're named with sequential numbers)
            files.sort()

            # Load each file as an image
            for file in files:
                file_path = os.path.join(full_dir, file)
                try:
                    image = pygame.image.load(file_path).convert_alpha()
                    frames.append(image)
                except pygame.error as e:
                    print(f"Error loading animation frame {file_path}: {e}")

            print(f"Loaded {len(frames)} animation frames from {directory}")
        except Exception as e:
            print(f"Error loading animation frames from {directory}: {e}")

        return frames

    def apply_knockback(self, direction_x, direction_y, collision_handler=None, tile_mapping=None, map_data=None):
        """Override the apply_knockback method to prevent movement but show hit animation

        Args:
            direction_x (float): X component of knockback direction (unused for bomberplant)
            direction_y (float): Y component of knockback direction (unused for bomberplant)
            collision_handler: Optional collision handler for wall detection (unused for bomberplant)
            tile_mapping: Optional tile mapping for collision detection (unused for bomberplant)
            map_data: Optional map data for collision detection (unused for bomberplant)
        """
        # Bomberplant doesn't move, just show hit animation
        # Only apply knockback if not already in a special state
        if not self.is_hit and not self.is_dying and not self.is_dead:
            # Start hit animation instead of actual knockback
            self.start_hit_animation()
            return True
        return False

    def toggle_range_visibility(self):
        """Toggle the visibility of the attack range circle"""
        self.show_range = not self.show_range
        return self.show_range

    def toggle_mark_visibility(self):
        """Toggle the visibility of the target mark"""
        self.show_mark = not self.show_mark
        return self.show_mark

    def place_mark(self, x, y):
        """Place a mark at the specified position

        Args:
            x (int): X position for the mark
            y (int): Y position for the mark

        Returns:
            bool: True if mark was placed, False otherwise
        """
        if not self.mark_active and self.mark_sprites and len(self.mark_sprites) > 0:
            self.mark_position = [x, y]
            self.mark_active = True
            self.mark_timer = self.mark_duration
            self.mark_frame = 0  # Reset animation frame
            return True
        return False

    def is_position_in_mark(self, x, y, radius=16):
        """Check if a position is within the mark's radius

        Args:
            x (int): X position to check
            y (int): Y position to check
            radius (int, optional): Radius to check within. Defaults to 16 (1 tile).

        Returns:
            bool: True if position is within mark radius, False otherwise
        """
        if not self.mark_active:
            return False

        # Calculate distance to mark
        dx = x - self.mark_position[0]
        dy = y - self.mark_position[1]
        distance = ((dx ** 2) + (dy ** 2)) ** 0.5

        # Check if position is within radius
        return distance <= radius

    def is_player_in_range(self, player_x, player_y):
        """Check if the player is within the bomberplant's attack range

        Args:
            player_x (int): Player's x position
            player_y (int): Player's y position

        Returns:
            bool: True if player is in range, False otherwise
        """
        # Calculate the center of the bomberplant
        center_x = self.rect.centerx
        center_y = self.rect.centery

        # Calculate distance to player
        dx = player_x - center_x
        dy = player_y - center_y
        distance = ((dx ** 2) + (dy ** 2)) ** 0.5

        # Check if player is within range
        return distance <= self.attack_range

    def apply_knockback_to_player(self, player, **_):
        """Apply knockback to the player when colliding or when bomb explodes

        Args:
            player: The player object to apply knockback to
            **_: Additional parameters (ignored for compatibility with enemy manager)
        """
        # Check if we need to apply explosion damage and knockback
        # Only apply damage during the first half of the explosion animation
        # This ensures damage is only applied once at the start of the explosion
        if self.bomb_state == "explosion" and self.explosion_damage_applied and self.bomb_frame < len(self.bomb_explosion_sprites) // 2:
            # Get the stored knockback direction
            dx, dy = self.explosion_knockback_direction

            # Calculate distance between player and explosion
            player_center_x = player.rect.centerx
            player_center_y = player.rect.centery
            explosion_x = self.bomb_position[0]
            explosion_y = self.bomb_position[1]

            # Calculate distance
            dx = player_center_x - explosion_x
            dy = player_center_y - explosion_y
            distance = ((dx ** 2) + (dy ** 2)) ** 0.5

            # Only apply damage and knockback if player is within explosion radius
            if distance <= self.bomb_explosion_radius:
                # Apply knockback to the player (away from explosion center)
                if hasattr(player, 'apply_knockback'):
                    # Check if player is at or very near the center of the explosion
                    if distance < 1.0:
                        # If player is at the center, apply random knockback direction
                        import random
                        angle = random.uniform(0, 2 * 3.14159)  # Random angle in radians
                        normalized_dx = math.cos(angle) * self.bomb_explosion_knockback_strength
                        normalized_dy = math.sin(angle) * self.bomb_explosion_knockback_strength
                        player.apply_knockback(normalized_dx, normalized_dy)
                    else:
                        # Normal case - knockback away from explosion center
                        normalized_dx = (dx / distance) * self.bomb_explosion_knockback_strength
                        normalized_dy = (dy / distance) * self.bomb_explosion_knockback_strength
                        player.apply_knockback(normalized_dx, normalized_dy)

                # Apply damage to the player
                if hasattr(player, 'take_damage'):
                    player.take_damage(self.bomb_explosion_damage)

                # Mark damage as applied by setting flag to false to prevent further damage
                self.explosion_damage_applied = False

                return True

        # Skip regular collision knockback if on cooldown, hit, dying or dead
        if self.knockback_cooldown > 0 or self.is_hit or self.is_dying or self.is_dead:
            return False

        # Check if we're colliding with the player
        if self.rect.colliderect(player.rect):
            # Calculate knockback direction (away from bomberplant)
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery

            # Always apply knockback effect to player with the calculated direction
            if hasattr(player, 'apply_knockback'):
                # Normalize the direction vector for consistent knockback
                distance = ((dx ** 2) + (dy ** 2)) ** 0.5
                if distance > 0:
                    # Scale by player_knockback_strength
                    normalized_dx = (dx / distance) * self.player_knockback_strength
                    normalized_dy = (dy / distance) * self.player_knockback_strength
                    player.apply_knockback(normalized_dx, normalized_dy)
                else:
                    # Fallback if distance is zero (should rarely happen)
                    player.apply_knockback(dx, dy)

            # Apply damage to the player if the method exists
            if hasattr(player, 'take_damage'):
                player.take_damage(self.player_damage)

            # Start cooldown
            self.knockback_cooldown = self.knockback_cooldown_time

            return True
        return False

    def draw(self, surface, camera_x=0, camera_y=0):
        """Draw the bomberplant on the given surface, accounting for camera position"""
        # Calculate screen position
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y

        # Draw the attack range circle if enabled
        if self.show_range and not self.is_dead:
            # Create a transparent surface for the range circle
            # The surface needs to be large enough to contain the entire circle
            circle_diameter = self.attack_range * 2
            circle_surface = pygame.Surface((circle_diameter, circle_diameter), pygame.SRCALPHA)

            # Draw the circle on the transparent surface
            # Use a semi-transparent color for the outline (RGBA)
            # Red when player is detected (even before targeting completes), green otherwise
            if self.player_detected:
                # Add pulsing effect when player is detected
                pulse_factor = abs(math.sin(pygame.time.get_ticks() / 200))  # Pulsing effect
                red_value = int(150 + 50 * pulse_factor)  # Pulsing between 150 and 200
                alpha_value = int(60 + 40 * pulse_factor)  # Pulsing between 60 and 100 (more transparent)
                circle_color = (red_value, 0, 0, alpha_value)  # Red with pulsing alpha
            else:
                circle_color = (0, 200, 0, 70)  # Green with lower alpha (more transparent)

            # Draw the circle outline with a width of 1 pixel (thin line)
            pygame.draw.circle(
                circle_surface,
                circle_color,
                (circle_diameter // 2, circle_diameter // 2),  # Center of the circle
                self.attack_range,  # Radius
                1  # Width of the outline (thin for subtlety)
            )

            # Calculate the position to blit the circle surface
            # Center the circle on the bomberplant
            circle_x = screen_x + (self.rect.width // 2) - (circle_diameter // 2)
            circle_y = screen_y + (self.rect.height // 2) - (circle_diameter // 2)

            # Blit the circle surface onto the main surface
            surface.blit(circle_surface, (circle_x, circle_y))

            # Draw the mark if it's active, mark animation is loaded, and bomb is not in explosion state
            if self.mark_active and self.show_mark and self.mark_sprites and len(self.mark_sprites) > 0 and self.bomb_state != "explosion":
                # Calculate screen position for the mark
                mark_screen_x = self.mark_position[0] - camera_x
                mark_screen_y = self.mark_position[1] - camera_y

                # Get the current frame of the mark animation
                mark_frame = min(self.mark_frame, len(self.mark_sprites) - 1)
                mark_image = self.mark_sprites[mark_frame]

                # Center the mark on the fixed position
                mark_rect = mark_image.get_rect()
                mark_rect.center = (mark_screen_x, mark_screen_y)

                # Draw the mark
                surface.blit(mark_image, mark_rect)

        # Draw the enemy
        surface.blit(self.image, (screen_x, screen_y))

        # Draw bomb animations if active and not in a special state
        if self.bomb_state != "none" and not self.is_dead and not self.is_dying:
            # Validate bomb position is set
            if not self.bomb_position or len(self.bomb_position) != 2:
                print(f"Error: Invalid bomb position: {self.bomb_position}")
                self.bomb_state = "none"
                return

            # Calculate screen position for the bomb
            bomb_screen_x = self.bomb_position[0] - camera_x
            bomb_screen_y = self.bomb_position[1] - camera_y

            # Get the current frame of the bomb animation based on state
            bomb_image = None

            # Only draw the bomb for the current state
            if self.bomb_state == "up" and self.bomb_up_sprites and len(self.bomb_up_sprites) > 0:
                bomb_frame = min(self.bomb_frame, len(self.bomb_up_sprites) - 1)
                bomb_image = self.bomb_up_sprites[bomb_frame]
                # Debug output for bomb position
                if self.debug_mode:
                    print(f"Drawing UP bomb at position: {self.bomb_position}, progress: {self.bomb_travel_progress:.2f}")
            elif self.bomb_state == "down" and self.bomb_down_sprites and len(self.bomb_down_sprites) > 0:
                bomb_frame = min(self.bomb_frame, len(self.bomb_down_sprites) - 1)
                bomb_image = self.bomb_down_sprites[bomb_frame]
                # Debug output for bomb position
                if self.debug_mode:
                    print(f"Drawing DOWN bomb at position: {self.bomb_position}, progress: {self.bomb_travel_progress:.2f}")
            elif self.bomb_state == "explosion" and self.bomb_explosion_sprites and len(self.bomb_explosion_sprites) > 0:
                bomb_frame = min(self.bomb_frame, len(self.bomb_explosion_sprites) - 1)
                bomb_image = self.bomb_explosion_sprites[bomb_frame]
                # Debug output for bomb position
                if self.debug_mode:
                    print(f"Drawing EXPLOSION at position: {self.bomb_position}")
            else:
                # If we don't have the right sprites for the current state, reset the bomb state
                print(f"Error: Missing bomb sprites for state: {self.bomb_state}")
                self.bomb_state = "none"
                return

            # Draw the bomb if we have a valid image
            if bomb_image:
                # Center the bomb on its position
                bomb_rect = bomb_image.get_rect()
                bomb_rect.center = (bomb_screen_x, bomb_screen_y)

                # Draw the bomb
                surface.blit(bomb_image, bomb_rect)

        # Draw health bar if needed
        if self.show_health_bar and not self.is_dead and self.health_bar_bg and self.health_indicator:
            # Calculate screen position for health bar (centered above the enemy)
            screen_x = self.rect.centerx - (self.health_bar_bg.get_width() // 2) - camera_x
            screen_y = self.rect.y - self.health_bar_bg.get_height() - 5 - camera_y  # 5 pixels above enemy

            # Calculate health percentage
            health_percent = max(0, min(1, self.current_health / self.max_health))

            # Calculate width of health_hud (background) based on current health
            health_width = int(self.health_bar_bg.get_width() * health_percent)

            if health_width > 0:
                try:
                    # Create a subsurface of the background (health_hud) with the appropriate width
                    health_rect = pygame.Rect(0, 0, health_width, self.health_bar_bg.get_height())
                    health_bg_part = self.health_bar_bg.subsurface(health_rect)

                    # Draw the health_hud (background) first
                    surface.blit(health_bg_part, (screen_x, screen_y))

                    # Draw the health_bar_hud (foreground) on top
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

                    # Draw the health_hud (background) with clipping
                    surface.set_clip(health_clip_rect)
                    surface.blit(self.health_bar_bg, (screen_x, screen_y))
                    surface.set_clip(clip_rect)

                    # Draw the health_bar_hud (foreground) on top
                    surface.blit(self.health_indicator, (screen_x, screen_y))

        # Debug visualization removed
