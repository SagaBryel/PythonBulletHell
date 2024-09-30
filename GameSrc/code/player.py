from settings import *


class Player(pygame.sprite.Sprite):
    # O Player recebe collision_sprites como argumento
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.load_images()

        self.state, self.frame_index = 'stand', 0
        self.image = pygame.image.load(join('..', 'images', 'player', 'stand', '0.png')).convert_alpha()

        self.rect = self.image.get_rect(center=pos)
        self.hitbox_rect = self.rect.inflate(-100, -85)

        # movement
        self.direction = pygame.Vector2()
        self.last_direction = pygame.Vector2(1, 0)  # Inicializa a última direção como "direita"
        self.speed = 500
        self.collision_sprites = collision_sprites

        # Ataque
        self.is_attacking = False
        self.attack_time = 0
        self.attack_button_pressed = False
        self.attack_cooldown = 600
        self.combo_timer = 0
        self.combo_max_time = 400
        self.combo = False

    def load_images(self):
        self.frames = {'atk': [], 'atk2': [], 'stand': [], 'walking': []}
        for state in self.frames.keys():
            for folder_path, sub_folders, file_names in walk(join('..', 'images', 'player', state)):
                if file_names:
                    for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.frames[state].append(surf)

    def input(self):
        keys = pygame.key.get_pressed()

        # Movimento
        if not self.is_attacking:
            self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
            self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
            self.direction = self.direction.normalize() if self.direction else self.direction

            if self.direction.x != 0:  # Atualiza a última direção se houver movimento horizontal
                self.last_direction.x = self.direction.x

        # Ataque
        if keys[pygame.K_SPACE]:
            self.attack_button_pressed = True
        else:
            if self.attack_button_pressed:  # Permite que o ataque seja chamado apenas uma vez por pressionamento
                self.attack()  # Chama o método de ataque quando o botão é solto
            self.attack_button_pressed = False

    def attack(self):
        current_time = pygame.time.get_ticks()

        if not self.is_attacking:
            # Inicia o primeiro ataque
            self.is_attacking = True
            self.combo = False
            self.state = 'atk'
            self.frame_index = 0
            self.attack_time = current_time

        elif self.is_attacking and self.state == 'atk':
            # Verifica se o tempo do combo ainda é válido
            if (current_time - self.attack_time) <= self.combo_max_time * 1000:
                if self.attack_button_pressed:  # Se o botão foi pressionado novamente
                    self.combo = True

    def move(self, dt):
        if not self.is_attacking:
            self.hitbox_rect.x += self.direction.x * self.speed * dt
            self.collision('horizontal')
            self.hitbox_rect.y += self.direction.y * self.speed * dt
            self.collision('vertical')
            self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top

    def animate(self, dt):
        if len(self.frames[self.state]) == 0:
            return

        if not self.is_attacking:
            if self.direction.length() == 0:
                self.state = 'stand'
            else:
                self.state = 'walking'

        # Atualiza o índice de frames
        if self.state == 'atk' or self.state == 'atk2':
            self.frame_index = (self.frame_index + 20 * dt)  #taxa de frames durante os ataques
        elif self.state == 'stand':
            self.frame_index = (self.frame_index + 5 * dt)  # Taxa para stand
        else:
            self.frame_index = (self.frame_index + 10 * dt)  # Taxa para walking

        # Carrega o frame atual da animação
        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]

        # Flipa a imagem se a última direção foi para a esquerda
        if self.last_direction.x < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def check_attack_end(self):
        if self.state in ['atk', 'atk2'] and self.frame_index >= len(self.frames[self.state]):
            if self.state == 'atk' and self.combo:
                self.state = 'atk2'
                self.frame_index = 0
                self.attack_time = pygame.time.get_ticks()
                self.combo = False
            else:
                self.is_attacking = False
                self.state = 'stand'
                self.frame_index = 0
                self.combo = False

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)
        self.check_attack_end()
