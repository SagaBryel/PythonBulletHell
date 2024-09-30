from settings import *

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        # para verificação no "draw" de groups.py a fim de resolver o problema do player ser cortado pelo mapa, observado
        # após a inclusão da logica de camera e mais especificamente da logica de sobreposição e suporposição do player
        self.ground = True


class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)