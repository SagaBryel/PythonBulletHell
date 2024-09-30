from settings import * 

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        #Usado para calcular o deslocamento da posição dos sprites na tela, de forma que o jogador fique sempre centralizado
        self.offset = pygame.Vector2()
    
    def draw(self, target_pos):
        #Calcula o deslocamento necessário para centralizar
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)

        # Separação dos sprites em duas camadas:
        # ground_sprites (objetos no chão) e object_sprites (objetos e personagens).
        ground_sprites = [sprite for sprite in self if hasattr(sprite, 'ground')] 
        object_sprites = [sprite for sprite in self if not hasattr(sprite, 'ground')] 

        # Este for segue a ordem >>, assim ground-sprites sempre são desenhados primeiro
        for layer in [ground_sprites, object_sprites]:
            # Ordena os sprites com base na posição Y do centro do retângulo (centery).
            # Logica de superposição/sobreposição
            for sprite in sorted(layer, key = lambda sprite: sprite.rect.centery):
                self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)