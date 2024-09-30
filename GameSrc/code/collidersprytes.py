from settings import *
from math import atan2, degrees, radians, cos, sin


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





class Bow(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        # player connection
        self.player = player
        self.distance = 140  # Distância entre o jogador e o arco
        self.angle = 0  # Ângulo inicial da rotação
        self.rotation_speed = 90  # Velocidade de rotação em graus por segundo
        self.arrow_released = False  # Controle para verificar se a flecha foi disparada

        # sprite setup
        super().__init__(groups)
        self.frames = [
            pygame.image.load(join('..', 'images', 'bow', 'animatebow', f'{i}.png')).convert_alpha()
            for i in range(9)  # Supondo que você tenha 9 frames
        ]
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=self.player.rect.center + pygame.Vector2(0, 1) * self.distance)
        self.is_shooting = False  # Controle da animação de disparo
        self.animation_speed = 10  # Controle da velocidade da animação

    def animate_bow(self, dt):
        if self.is_shooting:
            self.frame_index += self.animation_speed * dt
            if self.frame_index >= len(self.frames):
                self.frame_index = 0  # Reseta após a animação do disparo
                self.is_shooting = False
                self.arrow_released = False  # Reseta para o próximo tiro

            self.image = self.frames[int(self.frame_index)]

            # Dispara a flecha quando o arco está completamente puxado (por exemplo, no frame 5)
            if int(self.frame_index) == 5 and not self.arrow_released:
                self.arrow_released = True  # Impede que dispare várias vezes
                return True  # Indica que a flecha deve ser disparada

        return False  # Indica que a flecha ainda não deve ser disparada

    def rotate_bow(self, dt):
        """Rotaciona o arco automaticamente ao redor do jogador."""
        self.angle += self.rotation_speed * dt
        if self.angle >= 360:
            self.angle -= 360  # Mantém o ângulo no intervalo de 0 a 360 graus

        # Converte o ângulo para radianos e calcula a nova posição do arco
        radians_angle = radians(self.angle)
        direction = pygame.Vector2(cos(radians_angle), sin(radians_angle))

        # Gira a imagem do arco
        self.image = pygame.transform.rotozoom(self.frames[int(self.frame_index)], -self.angle, 1)
        self.rect = self.image.get_rect(center=self.player.rect.center + direction * self.distance)

    def update(self, dt):
        # Atualiza a rotação do arco automaticamente e animação de disparo
        arrow_should_shoot = self.animate_bow(dt)
        self.rotate_bow(dt)
        #Importante para a flexa sair no momento certo
        return arrow_should_shoot



class Arrow(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, angle, groups):
        super().__init__(groups)

        # Armazena a superfície original para não distorcer após várias rotações
        self.original_image = surf
        self.image = pygame.transform.rotozoom(self.original_image, -degrees(angle), 1)  # Roda a imagem da flecha de acordo com o ângulo
        self.rect = self.image.get_rect(center=pos)

        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000

        self.direction = direction  # A direção já está normalizada (tem magnitude 1)
        self.speed = 1200

    def update(self, dt):
        # Atualiza a posição da flecha com base na direção e velocidade
        self.rect.center += self.direction * self.speed * dt

        # Destrói a flecha quando sua "vida útil" expirar
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(groups)
        self.player = player

        # image
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.animation_speed = 6

        # rect
        self.rect = self.image.get_rect(center=pos)
        self.hitbox_rect = self.rect.inflate(-20, -40)
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.speed = 200

        # timer
        self.death_time = 0
        self.death_duration = 400

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def move(self, dt):
        # get direction
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self.direction = (player_pos - enemy_pos).normalize()

        # update the rect position + collision
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

    def destroy(self):
        # start a timer
        self.death_time = pygame.time.get_ticks()
        # change the image
        surf = pygame.mask.from_surface(self.frames[0]).to_surface()
        surf.set_colorkey('black')
        self.image = surf

    def death_timer(self):
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:
            self.kill()

    def update(self, dt):
        if self.death_time == 0:
            self.move(dt)
            self.animate(dt)
        else:
            self.death_timer()



