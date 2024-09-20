from settings import *


class Player(pygame.sprite.Sprite):
    # O Player recebe collision_sprites como argumento
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.image = pygame.image.load(join('..', 'images', 'player', 'stand', '0.png')).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        # Retangulo para colisão com largura ajustada para ignorar o espaço em branco
        self.hitbox_rect = self.rect.inflate(-100, -85)

        # movement
        self.direction = pygame.Vector2()
        self.speed = 500
        self.collision_sprites = collision_sprites

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction

    def move(self, dt):
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        # Importante, o sprite desenha a imagem onde quer que o retangulo esteja,
        # mas até então não estavamos movendo o retangulo
        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        # Percorre todos os sprites com os quais o player pode colidir
        for sprite in self.collision_sprites:
            # Verifica se o retângulo de colisão do player (hitbox) colidiu com o retângulo de colisão de outro sprite
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    # Se o jogador está se movendo para a direita, ajusta a posição para que a hitbox do jogador
                    # toque na lateral esquerda do sprite colidido, prevenindo o movimento
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    # idem, para a esquerda
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                else:
                    # Se o jogador está se movendo para cima, ajusta a posição para que a hitbox do jogador
                    # toque na parte inferior do sprite colidido, prevenindo o movimento
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom
                    # idem, para baixo
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top

    def update(self, dt):
        self.input()
        self.move(dt)