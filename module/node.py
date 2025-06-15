from pygame import sprite, image, Surface, Vector2, transform

class NodeType(sprite.Sprite):
    image: Surface
    show_radius: int = 20

class Empty(NodeType):
    surface = transform.scale(image.load(r"asset\node\blank.png").convert_alpha(), (16, 16))
    def __init__(self, pos: Vector2 | tuple[int, int], hidden: bool = True):
        super().__init__()
        self.image = Empty.surface.copy()
        self.pos = Vector2(pos)
        self.rect = Empty.surface.get_rect(center=pos)

        # determines if the node will only show on mouse over (true) or always show (false)
        self.hidden = hidden
        # determines if the node is currently visible
        self.visible: bool = not self.hidden 

class NodeGroup(sprite.Group):
    def draw_visible(self, surface: Surface):
        for spr in self.sprites():
            if hasattr(spr, "visible") and not spr.visible:
                continue
            surface.blit(spr.image, spr.rect)