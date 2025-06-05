class BrushManager:
    """Placeholder BrushManager for future implementation."""
    def __init__(self):
        self.brush_size = 1

    def create_ui(self, *args, **kwargs):
        pass

    def handle_event(self, *args, **kwargs):
        return False

    def draw(self, *args, **kwargs):
        pass

    def set_selected_tile(self, *args, **kwargs):
        pass

    def get_brush_tiles(self, center_x, center_y):
        return [(center_x, center_y)]
