from pygame import sprite, image, Surface, Vector2

class NodeType(sprite.Sprite):
    surface: Surface
    number: int

class Empty(NodeType):
    print("loading image")
    surface = image.load(r"asset\node\blank.png").convert_alpha()
    def __init__(self, pos: Vector2 | tuple[int, int]):
        super().__init__()
        self.surface = Empty.surface.copy()
        self.rect = Empty.surface.get_rect()
        self.pos = Vector2(pos)