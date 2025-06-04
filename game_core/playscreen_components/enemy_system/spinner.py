"""
Spinner Enemy - A spinning enemy that attacks players using pathfinding
"""
import pygame
import os
import heapq
import math
from .enemy import Enemy
from game_core.other_components.debug_tools import debug_manager

class Spinner(Enemy):
    """Spinner enemy class - a spinning enemy that attacks players"""
    def __init__(self, x, y):
        """Initialize the Spinner enemy"""
        super().__init__(x, y, enemy_type="spinner")

        # Set initial direction and state
        self.direction = "right"
        self.state = "idle"

        # Load animations
        self._load_animations()

        # Set initial image
        initial_anim_key = f"idle_{self.direction}"
        if initial_anim_key in self.sprites and self.sprites[initial_anim_key]:
            self.image = self.sprites[initial_anim_key][0]
        elif "idle_right" in self.sprites and self.sprites["idle_right"]:
            self.image = self.sprites["idle_right"][0]

        # Create the rect but don't set position yet - EnemyManager will handle that
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # Initialize all properties
        self._init_basic_properties()
        self._init_combat_properties()
        self._init_health_properties()

        # Set initial animation
        self.update_animation()

    def _load_animations(self):
        """Load all animation sprites for the spinner"""
        # Load spinner animations for all directions
        for direction in ["right", "left", "up", "down"]:
            self.load_animation("idle", direction, "Enemies_Sprites/Spinner_Sprites/spinner_idle_anim_all_dir")
            self.load_animation("hit", direction, "Enemies_Sprites/Spinner_Sprites/spinner_hit_anim_all_dir")
            self.load_animation("death", direction, "Enemies_Sprites/Spinner_Sprites/spinner_death_anim_all_dir")
            self.load_animation("run", direction, "Enemies_Sprites/Spinner_Sprites/spinner_run_attack_anim_all_dir")

        # Load wall hit animations
        self.load_animation("wall_hit_up", "right", "Enemies_Sprites/Spinner_Sprites/hitting_wall_fx_anim_up")
        self.load_animation("wall_hit_down", "right", "Enemies_Sprites/Spinner_Sprites/hitting_wall_fx_anim_down")
        self.load_animation("wall_hit_left", "right", "Enemies_Sprites/Spinner_Sprites/hitting_wall_fx_anim_left")
        self.load_animation("wall_hit_right", "right", "Enemies_Sprites/Spinner_Sprites/hitting_wall_fx_anim_right")

    def _init_basic_properties(self):
        """Initialize basic properties for the spinner"""
        # Spinner movement properties
        self.speed = 0.5  # Slower normal movement speed
        self.debug_mode = False  # Disable debug output for pathfinding

        # Store position as floats for precise movement
        self.float_x = float(self.rect.x)
        self.float_y = float(self.rect.y)

        # Movement properties
        self.velocity = [0, 0]
        self.move_cooldown = 0
        self.move_cooldown_time = 5

        # Direction persistence to reduce zig-zagging (like Phantom)
        self.last_direction = None  # Track the last movement direction
        self.direction_persistence = 15  # Frames to maintain the same direction

        # Player tracking
        self.last_player_x = 0
        self.last_player_y = 0

        # Pathfinding properties
        self.path = []  # List of grid positions to follow
        self.path_update_timer = 0
        self.path_update_interval = 30  # Update path every 30 frames (0.5 seconds)
        self.max_path_length = 20  # Maximum number of steps to calculate
        self.current_path_index = 0
        self.grid_size = 16  # Size of each grid cell (16x16 pixels)

        # Movement range - 15 tiles
        self.movement_range = 15 * 16  # 15 tiles (each tile is 16 pixels)

        # Ramming attack properties
        self.detection_range = 3 * 16  # 3 tiles (each tile is 16 pixels) - reduced from 7 to match pinkbat
        self.is_ramming = False
        self.ram_cooldown = 0
        self.ram_cooldown_time = 180  # 3 seconds at 60fps
        self.ram_duration = 45  # Reduced from 60 to make the dash complete faster
        self.ram_timer = 0
        self.ram_speed = 5.5  # Increased from 3.5 to make the dash faster
        self.ram_direction = [0, 0]  # Direction of the ram attack
        self.max_ram_distance = 7 * 16  # Maximum distance to ram (7 tiles)
        self.ram_start_position = (0, 0)  # Starting position for the ram
        self.has_hit_player = False  # Flag to track if we've hit the player during this ram

        # Wall collision effect properties
        self.is_showing_wall_hit = False
        self.wall_hit_timer = 0
        self.wall_hit_duration = 30  # 0.5 seconds at 60fps
        self.wall_hit_frame = 0
        self.wall_hit_direction = "up"  # Direction of wall hit (up, down, left, right)

    def _init_combat_properties(self):
        """Initialize combat-related properties"""
        # Knockback properties
        self.knockback_strength = 5.0
        self.knockback_cooldown = 0
        self.knockback_cooldown_time = 45  # 0.75 seconds at 60fps

        # Player damage properties
        self.player_knockback_strength = 6.0  # Increased from 4.0 to make knockback more impactful
        self.player_damage = 15

    def _init_health_properties(self):
        """Initialize health and damage properties"""
        # Health properties
        self.max_health = 60
        self.current_health = 60

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

        # Health bar properties
        self.show_health_bar = False
        self.health_bar_timer = 0
        self.health_bar_duration = 120  # Show health bar for 2 seconds (60 frames per second)

        # Load health bar assets
        self.health_bar_bg = self.load_image("Enemies_Sprites/Hud_Ui/health_hud.png")
        self.health_indicator = self.load_image("Enemies_Sprites/Hud_Ui/health_bar_hud.png")

        # Scale health bar
        self._scale_health_bar()

    def update(self, player_x, player_y, collision_handler=None, tile_mapping=None, map_data=None):
        """Update spinner position and animation

        Args:
            player_x (int): Player's x position
            player_y (int): Player's y position
            collision_handler: Optional collision handler for wall detection
            tile_mapping: Optional tile mapping for collision detection
            map_data: Optional map data for collision detection
        """
        # Skip updates if dead
        if self.is_dead:
            return

        # Update timers
        self._update_timers()

        # Handle movement and collision
        if not self.is_hit and not self.is_dying:
            # Store original position for collision detection
            original_x = self.rect.x
            original_y = self.rect.y
            original_float_x = self.float_x
            original_float_y = self.float_y

            # Update movement
            self._handle_movement(player_x, player_y, collision_handler, tile_mapping, map_data)

            # Check for collisions with walls if collision data is available
            if collision_handler and tile_mapping and map_data:
                # Create a player rect to exclude from collision check
                player_rect = pygame.Rect(player_x - 16, player_y - 16, 32, 32)  # Slightly larger than player

                # Check if we're colliding with a wall
                wall_collision = collision_handler.check_collision(self.rect, tile_mapping, map_data)
                player_collision = self.rect.colliderect(player_rect)

                # Special handling for ramming
                if self.is_ramming:
                    # If we're ramming and hit a wall (not player), show wall hit animation and stop the ram
                    if wall_collision and not player_collision:
                        # Revert position completely
                        self.rect.x = original_x
                        self.rect.y = original_y
                        self.float_x = original_float_x
                        self.float_y = original_float_y

                        # Show wall hit animation
                        self.start_wall_hit_animation()

                        # Stop ramming and set full cooldown
                        self.is_ramming = False
                        self.ram_cooldown = self.ram_cooldown_time  # Full 3-second cooldown after hitting a wall
                        self.move_cooldown = 30  # Short movement cooldown (0.5 seconds)

                        # Stop movement
                        self.velocity = [0, 0]

                    # If we're ramming through a player, allow it even near walls
                    elif player_collision:
                        # Allow the ram to continue through the player
                        pass

                # Normal movement (not ramming)
                else:
                    # If we hit a wall during normal movement, just revert position
                    if wall_collision and not player_collision:
                        self.rect.x = original_x
                        self.rect.y = original_y
                        self.float_x = original_float_x
                        self.float_y = original_float_y
                        self.velocity = [0, 0]  # Stop movement to prevent getting stuck

                    # If we're colliding with the player, allow it for damage
                    elif player_collision:
                        # Allow the collision with the player
                        pass

        # Update animation
        self.update_animation()

    def _update_timers(self):
        """Update all timers and cooldowns"""
        # Update hit timer
        if self.is_hit:
            self.hit_timer -= 1
            if self.hit_timer <= 0:
                self.is_hit = False
                # Default to idle state after hit
                self.state = "idle"

        # Update death timer
        if self.is_dying:
            self.death_timer -= 1
            if self.death_timer <= 0:
                self.is_dead = True

        # Update damage cooldown
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1

        # Update knockback cooldown
        if self.knockback_cooldown > 0:
            self.knockback_cooldown -= 1

        # Update health bar timer
        if self.health_bar_timer > 0:
            self.health_bar_timer -= 1
            if self.health_bar_timer <= 0:
                self.show_health_bar = False

        # Update wall hit timer
        if self.is_showing_wall_hit:
            self.wall_hit_timer -= 1
            if self.wall_hit_timer <= 0:
                self.is_showing_wall_hit = False

    def _handle_movement(self, player_x, player_y, collision_handler=None, tile_mapping=None, map_data=None):
        """Handle spinner movement and collision

        Args:
            player_x (int): Player's x position
            player_y (int): Player's y position
            collision_handler: Optional collision handler for wall detection
            tile_mapping: Optional tile mapping for collision detection
            map_data: Optional map data for collision detection
        """
        # Keep track of player position
        self.last_player_x = player_x
        self.last_player_y = player_y

        # Calculate distance to player
        dx = player_x - self.rect.centerx
        dy = player_y - self.rect.centery
        distance = (dx**2 + dy**2)**0.5

        # Debug output for distance
        if self.debug_mode:
            from game_core.other_components.debug_tools import debug_manager
            in_attack_range = "IN ATTACK RANGE" if distance <= self.detection_range else "out of attack range"
            in_movement_range = "IN MOVEMENT RANGE" if distance <= self.movement_range else "out of movement range"
            debug_manager.log(f"Spinner distance to player: {distance:.1f}px ({distance/16:.1f} tiles)", "enemy")
            debug_manager.log(f"Attack range: {self.detection_range}px (3 tiles) - {in_attack_range}", "enemy")
            debug_manager.log(f"Movement range: {self.movement_range}px (15 tiles) - {in_movement_range}", "enemy")
            debug_manager.log(f"Ram cooldown: {self.ram_cooldown}, Is ramming: {self.is_ramming}", "enemy")

        # Default to idle state with no movement
        self.velocity = [0, 0]

        # If already ramming, continue the ram in the same direction
        if self.is_ramming:
            # Set state to run/attack
            self.state = "run"

            # Calculate current distance from start position
            current_x = self.rect.centerx
            current_y = self.rect.centery
            start_x, start_y = self.ram_start_position
            distance_traveled = ((current_x - start_x)**2 + (current_y - start_y)**2)**0.5

            # Check if we've reached the maximum ram distance (7 tiles)
            if distance_traveled >= self.max_ram_distance:
                # Stop ramming if we've gone far enough
                self.is_ramming = False
                self.ram_cooldown = self.ram_cooldown_time  # Full 3-second cooldown
                self.velocity = [0, 0]  # Stop movement immediately
            else:
                # Continue moving in the same direction
                self.velocity[0] = self.ram_direction[0] * self.speed * self.ram_speed
                self.velocity[1] = self.ram_direction[1] * self.speed * self.ram_speed

                # We'll handle wall collisions in the main update method
                # This allows the ram to continue even if there's a wall collision
                # The wall hit animation will be triggered in the main update method if needed

                # Check for wall collision before updating position
                if collision_handler and tile_mapping and map_data:
                    # Create a test rect for the next position
                    test_rect = pygame.Rect(
                        int(self.float_x + self.velocity[0]),
                        int(self.float_y + self.velocity[1]),
                        self.rect.width,
                        self.rect.height
                    )

                    # Only update position if not colliding with a wall
                    if not collision_handler.check_collision(test_rect, tile_mapping, map_data):
                        self.float_x += self.velocity[0]
                        self.float_y += self.velocity[1]
                        self.rect.x = int(self.float_x)
                        self.rect.y = int(self.float_y)
                else:
                    # If no collision data, just update position
                    self.float_x += self.velocity[0]
                    self.float_y += self.velocity[1]
                    self.rect.x = int(self.float_x)
                    self.rect.y = int(self.float_y)

            # Decrement ram timer
            self.ram_timer -= 1
            if self.ram_timer <= 0:
                self.is_ramming = False
                self.ram_cooldown = self.ram_cooldown_time

        # Check if not on cooldown and player is within 7 tiles for dash attack
        elif (self.ram_cooldown <= 0 and
              distance <= self.detection_range):  # detection_range is 7 tiles (112 pixels)
            # Start ramming
            self.is_ramming = True
            self.ram_timer = self.ram_duration
            self.state = "run"
            self.has_hit_player = False  # Reset hit player flag

            # Store starting position
            self.ram_start_position = (self.rect.centerx, self.rect.centery)

            # Calculate direction to player (will be fixed for the entire ram)
            if distance > 0:
                self.ram_direction[0] = dx / distance
                self.ram_direction[1] = dy / distance

                # Set direction based on movement for animation
                if abs(self.ram_direction[0]) > abs(self.ram_direction[1]):
                    self.direction = "right" if self.ram_direction[0] > 0 else "left"
                else:
                    self.direction = "down" if self.ram_direction[1] > 0 else "up"

        # If not ramming, use pathfinding to move toward the player if within 15 tiles
        elif distance <= self.movement_range:  # movement_range is 15 tiles (240 pixels)
            if self.debug_mode:
                debug_manager.log("Spinner in movement range, using pathfinding", "enemy")

            # Update path periodically
            self.path_update_timer += 1
            if self.path_update_timer >= self.path_update_interval or not self.path:
                if self.debug_mode:
                    debug_manager.log(f"Updating path (timer: {self.path_update_timer}, interval: {self.path_update_interval})", "enemy")
                self.path_update_timer = 0
                self.find_path_to_player(player_x, player_y, collision_handler, tile_mapping, map_data)
                self.current_path_index = 0
                if self.debug_mode:
                    debug_manager.log(f"Path found with {len(self.path)} waypoints", "enemy")

            # Follow the path if we have one
            if self.path and self.current_path_index < len(self.path):
                if self.debug_mode:
                    debug_manager.log(f"Following path at index {self.current_path_index}/{len(self.path)}", "enemy")
                # Follow the path
                self.follow_path(collision_handler, tile_mapping, map_data)
            else:
                # If no path, go idle
                if self.debug_mode:
                    debug_manager.log("No path found or reached end of path, going idle", "enemy")
                self.velocity = [0, 0]
                self.state = "idle"
                return

        # If player is too far away (beyond 15 tiles), go idle
        else:
            self.velocity = [0, 0]
            self.state = "idle"
            return

        # Update ram cooldown
        if self.ram_cooldown > 0:
            self.ram_cooldown -= 1

    def update_animation(self):
        """Update the spinner's animation frame"""
        # Get the appropriate animation key for the current state
        current_animation_key = self._get_animation_key()

        # If we don't have a valid animation, return
        if not current_animation_key or current_animation_key not in self.sprites:
            return

        # Make sure we have frames for this animation
        if not self.sprites[current_animation_key]:
            return

        # Update animation timer
        self.animation_timer += self.animation_speed

        # Update frame when timer exceeds 1
        if self.animation_timer >= 1:
            self.animation_timer = 0

            # Special handling for hit animation
            if self.is_hit:
                self.hit_frame += 1
                if self.hit_frame >= len(self.sprites[current_animation_key]):
                    self.hit_frame = 0
                self.frame = self.hit_frame
            # Special handling for death animation
            elif self.is_dying:
                self.death_frame += 1
                if self.death_frame >= len(self.sprites[current_animation_key]):
                    self.death_frame = len(self.sprites[current_animation_key]) - 1
                self.frame = self.death_frame
            # Regular animation
            else:
                self.frame = (self.frame + 1) % len(self.sprites[current_animation_key])

        # Make sure frame index is valid
        if self.frame >= len(self.sprites[current_animation_key]):
            self.frame = 0

        # Set the current image
        self.image = self.sprites[current_animation_key][self.frame]

    def _get_animation_key(self):
        """Get the appropriate animation key based on current state"""
        # Death animation takes priority
        if self.is_dying:
            return "death_right"

        # Hit animation takes priority over movement
        if self.is_hit:
            return "hit_right"

        # Update direction based on velocity for normal movement
        if self.velocity[0] != 0 or self.velocity[1] != 0:
            # Determine direction based on velocity
            if abs(self.velocity[0]) > abs(self.velocity[1]):
                self.direction = "right" if self.velocity[0] > 0 else "left"
            else:
                self.direction = "down" if self.velocity[1] > 0 else "up"

        # Use idle animation when state is idle
        if self.state == "idle":
            return f"idle_{self.direction}"

        # Use run animation for ramming and normal movement
        return f"run_{self.direction}"

    def take_damage(self, damage, knockback_x=0, knockback_y=0, collision_handler=None, tile_mapping=None, map_data=None):
        """Take damage and update health

        Args:
            damage (int): Amount of damage to take
            knockback_x (float, optional): X direction of knockback
            knockback_y (float, optional): Y direction of knockback
            collision_handler: Optional collision handler for wall detection
            tile_mapping: Optional tile mapping for collision detection
            map_data: Optional map data for collision detection

        Returns:
            bool: True if damage was applied, False if on cooldown or already dead
        """
        # Skip if already dead or on damage cooldown
        if self.is_dead or self.is_dying or self.damage_cooldown > 0:
            return False

        # Apply damage
        self.current_health -= damage

        # Show health bar
        self.show_health_bar = True
        self.health_bar_timer = self.health_bar_duration

        # Start damage cooldown
        self.damage_cooldown = self.damage_cooldown_time

        # Apply knockback if provided
        if knockback_x != 0 or knockback_y != 0:
            self.apply_knockback(knockback_x, knockback_y, collision_handler, tile_mapping, map_data)

        # Check if dead
        if self.current_health <= 0:
            self.current_health = 0
            self.start_death_animation()
        else:
            self.start_hit_animation()

        return True

    def apply_knockback(self, knockback_x, knockback_y, collision_handler=None, tile_mapping=None, map_data=None):
        """Apply knockback to the spinner

        Args:
            knockback_x (float): X direction of knockback
            knockback_y (float): Y direction of knockback
            collision_handler: Optional collision handler for wall detection
            tile_mapping: Optional tile mapping for collision detection
            map_data: Optional map data for collision detection

        Returns:
            bool: True if knockback was applied, False if on cooldown or already dead
        """
        # Skip if already dead, dying, or on knockback cooldown
        if self.is_dead or self.is_dying or self.knockback_cooldown > 0:
            return False

        # Start knockback cooldown
        self.knockback_cooldown = self.knockback_cooldown_time

        # Calculate knockback distance
        distance = max(0.1, (knockback_x**2 + knockback_y**2)**0.5)
        normalized_x = knockback_x / distance
        normalized_y = knockback_y / distance

        # Calculate new position after knockback
        new_float_x = self.float_x + normalized_x * self.knockback_strength
        new_float_y = self.float_y + normalized_y * self.knockback_strength

        # Check for wall collision before applying knockback
        if collision_handler and tile_mapping and map_data:
            # Create a test rect for the knockback position
            test_rect = pygame.Rect(
                int(new_float_x),
                int(new_float_y),
                self.rect.width,
                self.rect.height
            )

            # Only update position if not colliding with a wall
            if not collision_handler.check_collision(test_rect, tile_mapping, map_data):
                self.float_x = new_float_x
                self.float_y = new_float_y
                self.rect.x = int(self.float_x)
                self.rect.y = int(self.float_y)
            else:
                # If would collide with wall, apply reduced knockback
                self.float_x += normalized_x * (self.knockback_strength * 0.5)
                self.float_y += normalized_y * (self.knockback_strength * 0.5)
                self.rect.x = int(self.float_x)
                self.rect.y = int(self.float_y)
        else:
            # If no collision data, just apply knockback
            self.float_x = new_float_x
            self.float_y = new_float_y
            self.rect.x = int(self.float_x)
            self.rect.y = int(self.float_y)

        # Start hit animation
        self.start_hit_animation()
        return True

    def start_hit_animation(self):
        """Start the hit animation sequence"""
        self.is_hit = True
        self.hit_timer = self.hit_duration
        self.hit_frame = 0
        self.animation_timer = 0
        self.state = "hit"

    def start_death_animation(self):
        """Start the death animation sequence"""
        self.is_dying = True
        self.is_hit = False  # Cancel any hit animation
        self.is_showing_wall_hit = False  # Cancel any wall hit animation
        self.death_timer = self.death_duration
        self.death_frame = 0
        self.animation_timer = 0
        self.state = "death"
        self.velocity = [0, 0]  # Stop movement

    def start_wall_hit_animation(self):
        """Start the wall hit animation sequence"""
        self.is_showing_wall_hit = True
        self.wall_hit_timer = self.wall_hit_duration
        self.wall_hit_frame = 0

        # Set a cooldown to prevent immediate movement after hitting a wall
        self.move_cooldown = 30  # 0.5 seconds at 60fps

        # Ensure ram cooldown is set
        self.ram_cooldown = self.ram_cooldown_time  # Full 3-second cooldown

        # Determine wall hit direction based on movement direction
        if abs(self.ram_direction[0]) > abs(self.ram_direction[1]):
            # Horizontal movement
            self.wall_hit_direction = "right" if self.ram_direction[0] > 0 else "left"
        else:
            # Vertical movement
            self.wall_hit_direction = "down" if self.ram_direction[1] > 0 else "up"

    def load_image(self, path):
        """Load an image from the specified path"""
        full_path = os.path.join(os.getcwd(), path)
        try:
            image = pygame.image.load(full_path).convert_alpha()
            return image
        except pygame.error as e:
            pass  # Error loading image
            # Return a placeholder image (red square)
            placeholder = pygame.Surface((16, 16), pygame.SRCALPHA)
            placeholder.fill((255, 0, 0, 128))
            return placeholder

    def _scale_health_bar(self):
        """Scale health bar to be smaller for enemies"""
        if not self.health_bar_bg or not self.health_indicator:
            return

        # Scale health bar to be smaller for enemies
        scale_factor = 0.5

        # Scale the background (health_bar_hud.png)
        self.health_bar_bg = pygame.transform.scale(
            self.health_bar_bg,
            (int(self.health_bar_bg.get_width() * scale_factor),
             int(self.health_bar_bg.get_height() * scale_factor))
        )

        # Scale the indicator (health_hud.png) to be slightly smaller than the background
        # Make it 90% of the background width to ensure it fits inside
        indicator_scale = scale_factor * 0.9
        self.health_indicator = pygame.transform.scale(
            self.health_indicator,
            (int(self.health_indicator.get_width() * indicator_scale),
             int(self.health_indicator.get_height() * indicator_scale))
        )

    def find_path_to_player(self, player_x, player_y, collision_handler, tile_mapping, map_data):
        """Find a path to the player using A* algorithm"""
        # Convert positions to grid coordinates (16x16 tiles)
        start_x = self.rect.centerx // 16
        start_y = self.rect.centery // 16
        goal_x = player_x // 16
        goal_y = player_y // 16

        # Debug output
        if self.debug_mode:
            debug_manager.log(f"Spinner pathfinding: Start=({start_x},{start_y}), Goal=({goal_x},{goal_y})", "enemy")

        # Don't pathfind if player is too far away
        distance = math.sqrt((goal_x - start_x)**2 + (goal_y - start_y)**2)
        distance_pixels = distance * 16  # 16 pixels per tile
        if distance_pixels > self.movement_range:  # Only pathfind within movement range (15 tiles)
            self.path = []
            return

        # A* algorithm
        open_set = []
        closed_set = set()
        came_from = {}
        g_score = {(start_x, start_y): 0}
        f_score = {(start_x, start_y): self.heuristic(start_x, start_y, goal_x, goal_y)}

        # Add start node to open set
        heapq.heappush(open_set, (f_score[(start_x, start_y)], (start_x, start_y)))

        # Limit search to prevent infinite loops
        max_iterations = 225  # 15x15 grid around the enemy
        iterations = 0

        while open_set and iterations < max_iterations:
            iterations += 1

            # Get node with lowest f_score
            current = heapq.heappop(open_set)[1]

            # Check if we reached the goal (player position)
            if current == (goal_x, goal_y):
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]

                # Reverse path (from start to goal)
                path.reverse()

                # Limit path length
                if len(path) > self.max_path_length:
                    path = path[:self.max_path_length]

                # Debug output
                if self.debug_mode:
                    debug_manager.log(f"Spinner found path with {len(path)} steps", "enemy")

                self.path = path
                return

            # Add current to closed set
            closed_set.add(current)

            # Check neighbors (four cardinal directions)
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor_x = current[0] + dx
                neighbor_y = current[1] + dy
                neighbor = (neighbor_x, neighbor_y)

                # Skip if out of bounds
                if (neighbor_y < 0 or neighbor_x < 0 or
                    neighbor_y >= len(map_data) or neighbor_x >= len(map_data[0])):
                    continue

                # Skip if already evaluated
                if neighbor in closed_set:
                    continue

                # Check if this neighbor is walkable (no collision)
                # Create a test rect for the center of the tile
                test_rect = pygame.Rect(
                    neighbor_x * 16,  # Exact 16x16 grid
                    neighbor_y * 16,
                    16,  # Full tile size
                    16
                )

                # Check for collision with walls
                if collision_handler.check_collision(test_rect, tile_mapping, map_data):
                    # Collision detected, treat as wall
                    closed_set.add(neighbor)  # Mark as evaluated
                    continue

                # Calculate tentative g_score
                tentative_g_score = g_score.get(current, float('inf')) + 1

                # Skip if this path is worse
                if neighbor in g_score and tentative_g_score >= g_score[neighbor]:
                    continue

                # This path is better, record it
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + self.heuristic(neighbor_x, neighbor_y, goal_x, goal_y)

                # Add to open set if not already there
                if not any(neighbor == node[1] for node in open_set):
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        # If we get here, no path was found
        if self.debug_mode:
            debug_manager.log(f"Spinner could not find path to player after {iterations} iterations", "enemy")
        self.path = []

    def heuristic(self, x1, y1, x2, y2):
        """Manhattan distance heuristic for A* algorithm"""
        return abs(x1 - x2) + abs(y1 - y2)

    def follow_path(self, collision_handler, tile_mapping, map_data):
        """Follow the calculated path"""
        if not self.path or self.current_path_index >= len(self.path):
            return

        # Get current target position (center of the 16x16 tile)
        target_x, target_y = self.path[self.current_path_index]
        target_pixel_x = target_x * 16 + 8  # Center of the 16x16 tile
        target_pixel_y = target_y * 16 + 8

        # Calculate direction to target
        dx = target_pixel_x - self.rect.centerx
        dy = target_pixel_y - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)

        # Debug output
        if self.debug_mode:
            debug_manager.log(f"Spinner following path: target=({target_x},{target_y}), distance={distance:.1f}px", "enemy")

        # Check if we've reached the current target
        if distance < self.speed * 1.5:
            self.current_path_index += 1
            if self.debug_mode:
                debug_manager.log(f"Spinner reached waypoint {self.current_path_index-1}, moving to next", "enemy")
            return

        # Move towards target
        if distance > 0:
            # Normalize direction
            dx /= distance
            dy /= distance

            # Set velocity
            self.velocity[0] = dx * self.speed
            self.velocity[1] = dy * self.speed

            # Set direction for animation
            if abs(dx) > abs(dy):
                self.direction = "right" if dx > 0 else "left"
            else:
                self.direction = "down" if dy > 0 else "up"

            # Set animation state
            self.state = "run"

            # Check for collisions with the new velocity
            if collision_handler and tile_mapping and map_data:
                # Create a rect for the next position
                next_rect = pygame.Rect(
                    int(self.float_x + self.velocity[0]),
                    int(self.float_y + self.velocity[1]),
                    self.rect.width,
                    self.rect.height
                )

                # Check if we would collide with a wall
                if collision_handler.check_collision(next_rect, tile_mapping, map_data):
                    # If we would collide, recalculate the path
                    if self.debug_mode:
                        debug_manager.log("Spinner collision detected, recalculating path", "enemy")
                    self.path = []
                    self.path_update_timer = self.path_update_interval
                    self.velocity = [0, 0]
                else:
                    # If no collision, update position
                    self.float_x += self.velocity[0]
                    self.float_y += self.velocity[1]
                    self.rect.x = int(self.float_x)
                    self.rect.y = int(self.float_y)
                    if self.debug_mode:
                        debug_manager.log(f"Spinner moved to ({self.rect.x}, {self.rect.y})", "enemy")
            else:
                # If no collision data, just update position
                self.float_x += self.velocity[0]
                self.float_y += self.velocity[1]
                self.rect.x = int(self.float_x)
                self.rect.y = int(self.float_y)
                if self.debug_mode:
                    debug_manager.log(f"Spinner moved to ({self.rect.x}, {self.rect.y})", "enemy")
        else:
            self.velocity = [0, 0]
            self.state = "idle"

    def apply_knockback_to_player(self, player, **_):
        """Apply knockback and damage to the player

        Args:
            player: The player object to apply knockback to
            **_: Additional keyword arguments (not used, but kept for compatibility)
        """
        if player and self.rect.colliderect(player.rect):
            # Different behavior based on whether we're ramming or not
            if self.is_ramming and not self.has_hit_player:
                # Mark that we've hit the player during this ram
                self.has_hit_player = True

                # Calculate knockback direction perpendicular to ram direction
                # This will knock the player to the side instead of directly away
                perp_x = -self.ram_direction[1]  # Perpendicular is (-y, x)
                perp_y = self.ram_direction[0]

                # Determine which side of the ram path the player is on
                player_offset_x = player.rect.centerx - self.rect.centerx
                player_offset_y = player.rect.centery - self.rect.centery

                # Dot product to determine side (positive = right side, negative = left side)
                dot_product = player_offset_x * perp_x + player_offset_y * perp_y

                # Ensure knockback is away from the ram path
                if dot_product < 0:
                    perp_x = -perp_x
                    perp_y = -perp_y

                # Apply knockback to player
                if hasattr(player, 'apply_knockback'):
                    # Scale the perpendicular direction by the knockback strength
                    scaled_dx = perp_x * self.player_knockback_strength * 2.5  # Significantly increased side knockback (was 1.5)
                    scaled_dy = perp_y * self.player_knockback_strength * 2.5
                    player.apply_knockback(scaled_dx, scaled_dy)

                # Apply damage to player
                if hasattr(player, 'take_damage'):
                    player.take_damage(self.player_damage)

            # For normal collision (not during ram or already hit during ram)
            elif not self.is_ramming or (self.is_ramming and self.has_hit_player):
                # Only apply damage and knockback if not on cooldown
                if self.knockback_cooldown <= 0:
                    # Calculate knockback direction (away from spinner)
                    dx = player.rect.centerx - self.rect.centerx
                    dy = player.rect.centery - self.rect.centery

                    # Normalize the direction
                    distance = max(0.1, (dx**2 + dy**2)**0.5)
                    normalized_dx = dx / distance
                    normalized_dy = dy / distance

                    # Apply knockback to player
                    if hasattr(player, 'apply_knockback'):
                        # Scale the direction by the knockback strength
                        scaled_dx = normalized_dx * self.player_knockback_strength
                        scaled_dy = normalized_dy * self.player_knockback_strength
                        player.apply_knockback(scaled_dx, scaled_dy)

                    # Apply damage to player
                    if hasattr(player, 'take_damage'):
                        player.take_damage(self.player_damage // 2)  # Half damage for normal collision

                    # Set knockback cooldown to prevent continuous damage
                    self.knockback_cooldown = self.knockback_cooldown_time

    def draw(self, surface, camera_x=0, camera_y=0, zoom_factor=1.0):
        """Draw the spinner on the given surface

        Args:
            surface: Surface to draw on
            camera_x (int, optional): Camera X offset
            camera_y (int, optional): Camera Y offset
            zoom_factor (float, optional): Zoom factor for scaling
        """
        # Calculate screen position accounting for zoom
        screen_x = (self.rect.x - camera_x) * zoom_factor
        screen_y = (self.rect.y - camera_y) * zoom_factor

        # Draw the spinner (scale with zoom)
        if zoom_factor != 1.0:
            scaled_width = int(self.image.get_width() * zoom_factor)
            scaled_height = int(self.image.get_height() * zoom_factor)
            scaled_image = pygame.transform.scale(self.image, (scaled_width, scaled_height))
            surface.blit(scaled_image, (screen_x, screen_y))
        else:
            surface.blit(self.image, (screen_x, screen_y))

        # Draw wall hit effect if active
        if self.is_showing_wall_hit:
            # Get the wall hit animation key
            wall_hit_key = f"wall_hit_{self.wall_hit_direction}"

            if wall_hit_key in self.sprites and self.sprites[wall_hit_key]:
                # Calculate frame index
                frame_progress = 1.0 - (self.wall_hit_timer / self.wall_hit_duration)
                frame_count = len(self.sprites[wall_hit_key])
                frame_index = min(int(frame_progress * frame_count), frame_count - 1)

                # Get the wall hit image
                wall_hit_image = self.sprites[wall_hit_key][frame_index]

                # Scale the wall hit image with zoom
                if zoom_factor != 1.0:
                    scaled_width = int(wall_hit_image.get_width() * zoom_factor)
                    scaled_height = int(wall_hit_image.get_height() * zoom_factor)
                    wall_hit_image = pygame.transform.scale(wall_hit_image, (scaled_width, scaled_height))

                # Calculate scaled rect dimensions
                scaled_rect_width = int(self.rect.width * zoom_factor)
                scaled_rect_height = int(self.rect.height * zoom_factor)

                # Position the wall hit effect based on direction (accounting for zoom)
                if self.wall_hit_direction == "up":
                    # Position above the spinner
                    wall_hit_x = screen_x
                    wall_hit_y = screen_y - wall_hit_image.get_height()
                elif self.wall_hit_direction == "down":
                    # Position below the spinner
                    wall_hit_x = screen_x
                    wall_hit_y = screen_y + scaled_rect_height
                elif self.wall_hit_direction == "left":
                    # Position to the left of the spinner
                    wall_hit_x = screen_x - wall_hit_image.get_width()
                    wall_hit_y = screen_y
                else:  # right
                    # Position to the right of the spinner
                    wall_hit_x = screen_x + scaled_rect_width
                    wall_hit_y = screen_y

                # Draw the wall hit effect
                surface.blit(wall_hit_image, (wall_hit_x, wall_hit_y))

        # Draw health bar if needed
        if self.show_health_bar and not self.is_dead and self.health_bar_bg and self.health_indicator:
            # Calculate the entity's screen position accounting for zoom
            entity_screen_x = (self.rect.centerx - camera_x) * zoom_factor
            entity_screen_y = (self.rect.y - camera_y) * zoom_factor

            # Calculate health bar position relative to the scaled entity position
            health_bar_width = self.health_bar_bg.get_width()
            health_bar_height = self.health_bar_bg.get_height()
            health_bar_x = entity_screen_x - (health_bar_width // 2)
            health_bar_y = entity_screen_y - health_bar_height - (5 * zoom_factor)  # 5 pixels above enemy, scaled

            # Calculate health percentage
            health_percent = max(0, min(1, self.current_health / self.max_health))

            # Calculate width of health bar based on current health
            health_width = int(health_bar_width * health_percent)

            if health_width > 0:
                try:
                    # Create a subsurface of the background with the appropriate width
                    health_rect = pygame.Rect(0, 0, health_width, self.health_bar_bg.get_height())
                    health_bg_part = self.health_bar_bg.subsurface(health_rect)

                    # Draw the health background first
                    surface.blit(health_bg_part, (health_bar_x, health_bar_y))

                    # Draw the health indicator on top
                    surface.blit(self.health_indicator, (health_bar_x, health_bar_y))
                except ValueError:
                    # If subsurface fails, use clipping rect
                    clip_rect = surface.get_clip()

                    health_clip_rect = pygame.Rect(
                        health_bar_x,
                        health_bar_y,
                        health_width,
                        self.health_bar_bg.get_height()
                    )

                    # Draw the health background with clipping
                    surface.set_clip(health_clip_rect)
                    surface.blit(self.health_bar_bg, (health_bar_x, health_bar_y))
                    surface.set_clip(clip_rect)

                    # Draw the health indicator on top
                    surface.blit(self.health_indicator, (health_bar_x, health_bar_y))

        # Draw debug information if enabled
        if self.debug_mode:
            # Draw bounding box
            pygame.draw.rect(surface, (255, 0, 0),
                            (screen_x, screen_y, self.rect.width, self.rect.height),
                            1)
