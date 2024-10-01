import pygame

from player import Player
from collidersprytes import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites


from random import randint, choice

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Escape From Purgatory')
        self.clock = pygame.time.Clock()
        self.running = True
        self.start_time = pygame.time.get_ticks()

        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.arrow_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()


        # Bow timer
        self.can_shoot = True
        self.shoot_time = 0
        self.bow_cooldown = 1000


        # enemy timer
        self.initial_spawn_time = 3000  # Tempo inicial de respawn (3 segundos)
        self.min_spawn_time = 250  # Tempo mínimo de respawn (0,25 segundo)
        self.spawn_reduction_amount = 250  # Quanto reduzir a cada 10s
        self.current_spawn_time = self.initial_spawn_time
        # Evento para redução do tempo de respawn
        pygame.time.set_timer(pygame.USEREVENT + 2, 10000)  # 10 segundos

        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, self.current_spawn_time)
        self.spawn_positions = []

        # audio
        self.shoot_sound = pygame.mixer.Sound(join('..', 'audio', 'shoot.ogg'))
        self.shoot_sound.set_volume(0.10)
        self.impact_sound = pygame.mixer.Sound(join('..', 'audio', 'impact.ogg'))
        self.impact_sound.set_volume(0.10)
        self.music = pygame.mixer.Sound(join('..', 'audio', 'music1.ogg'))
        self.music.set_volume(0.05)
        self.music.play()

        #setup
        self.load_images()
        self.setup()

        #Sphere
        self.energy_sphere_cooldown = 3000  # 3 segundos de cooldown
        self.energy_sphere_duration = 2000  # 2 segundos de duração
        self.can_use_energy_sphere = True
        self.energy_sphere = None
        # usar a esfera automáticamente ao iniciar
        self.auto_use_energy_sphere()
        self.non_started_sphere = True


    def load_images(self):
        self.arrow_surf = pygame.image.load(join('..', 'images', 'bow', 'arrow.png')).convert_alpha()

        folders = list(walk(join('..', 'images', 'enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('..', 'images', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)




    def auto_use_energy_sphere(self):
        if self.can_use_energy_sphere and self.player.has_energy_sphere:
            self.energy_sphere = EnergySphere(self.player.rect.center, (self.all_sprites, ))
            print("Uma esfera de energia foi posicionada!")
            self.can_use_energy_sphere = False
            pygame.time.set_timer(pygame.USEREVENT + 1, self.energy_sphere_duration)  # Timer para a duração
            pygame.time.set_timer(pygame.USEREVENT, self.energy_sphere_cooldown)  # Timer para o cooldown


    def automatic_shooting(self):
        # Disparo automático do arco
        #if self.can_shoot:
        if self.can_shoot and self.player.has_bow:
            # Calcula o ângulo e a direção do arco
            radians_angle = radians(self.bow.angle)
            direction = pygame.Vector2(cos(radians_angle), sin(radians_angle))

            # A posição da flecha será na frente do arco, ajustada pela direção calculada
            pos = self.bow.rect.center + direction * 50

            # Cria a flecha, adicionando-a aos grupos apropriados e passando o ângulo para rotação correta
            Arrow(self.arrow_surf, pos, direction, radians_angle, (self.all_sprites, self.arrow_sprites))

            # Inicia a animação de disparo do arco
            self.bow.is_shooting = True
            self.shoot_sound.play()

            # Controla o cooldown do disparo
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def bow_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.bow_cooldown:
                self.can_shoot = True


    def setup(self):
        map = load_pygame(join('..', 'data', 'maps', 'mapa.tmx'))

        for x, y, image in map.get_layer_by_name('Camada1').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
        for obj in map.get_layer_by_name('Objetos'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
        for obj in map.get_layer_by_name('Collider'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)
        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x,obj.y), self.all_sprites, self.collision_sprites)
                self.bow = Bow(self.player, self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y))

    def arrow_collision(self):
        if self.arrow_sprites:
            for arrow in self.arrow_sprites:
                collision_sprites = pygame.sprite.spritecollide(arrow, self.enemy_sprites, False,
                                                                pygame.sprite.collide_mask)
                if collision_sprites:
                    self.impact_sound.play()  # Toca o som de impacto
                    for enemy in collision_sprites:
                        enemy.take_damage(ARROW_DAMAGE)  # Aplica dano ao inimigo
                    arrow.kill()  # Remove a flecha após a colisão

    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            # Verifica se o jogador não está invulnerável
            if not self.player.invulnerable:
                self.player.health -= 1
                self.player.last_hit_time = pygame.time.get_ticks()  # Atualiza o tempo do último hit
                self.player.invulnerable = True  # Ativa a invulnerabilidade
                print("A vida atual do jogador agora é: ", self.player.health, "!!!")
                if self.player.health <= 0:
                    self.running = False


    def reduce_spawn_time(self):
        if self.current_spawn_time > self.min_spawn_time:
            self.current_spawn_time -= self.spawn_reduction_amount
            self.current_spawn_time = max(self.current_spawn_time, self.min_spawn_time)  # Garante que não vá abaixo do mínimo
            print(f"Tempo de respawn reduzido para: {self.current_spawn_time} ms")


    def run(self):
        while self.running:
            # dt
            dt = self.clock.tick() / 1000

            # Verifica se 3 minutos se passaram
            elapsed_time = pygame.time.get_ticks() - self.start_time
            if elapsed_time >= 180000:  # 180000 milissegundos = 3 minutos
                print("VITORIA")
                self.running = False

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event:
                    Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())),
                          (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)
                if event.type == pygame.USEREVENT + 1:  # Duração da esfera de energia
                    if self.energy_sphere:
                        self.energy_sphere.kill()
                        self.energy_sphere = None
                        self.can_use_energy_sphere = True  # Permitir o uso novamente
                if event.type == pygame.USEREVENT:  # Cooldown da esfera de energia
                    if self.can_use_energy_sphere:
                        self.auto_use_energy_sphere()
                if event.type == pygame.USEREVENT + 2:
                    self.reduce_spawn_time()


            # update
            self.bow_timer()
            self.automatic_shooting()
            self.all_sprites.update(dt)
            self.arrow_collision()


            # Verifica colisão do ataque corpo a corpo do jogador com os inimigos
            if self.player.is_attacking:  # Verifique se o jogador está atacando
                for enemy in self.enemy_sprites:
                    if self.player.attack_hitbox.colliderect(enemy.rect):  # Verifique colisão
                        #  self.player.impact_sound.play()  # Toca o som de impacto
                        enemy.take_damage(self.player.current_attack_damage)  # Aplica dano ao inimigo

            # Verifica colisão do jogador com inimigos
            self.player_collision()

            # **Verifica colisão da esfera de energia com os inimigos**
            if self.energy_sphere:  # Verifica se a esfera de energia está ativa
                for enemy in self.enemy_sprites:
                    if self.energy_sphere.rect.colliderect(enemy.rect):  # Verifica colisão com inimigos
                        enemy.take_damage(self.energy_sphere.damage)  # Aplica dano ao inimigo

            #para dar partida na geração de esferas
            if self.player.has_energy_sphere:
                if self.non_started_sphere:
                    self.auto_use_energy_sphere()
                    self.non_started_sphere = False

            # draw
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)
            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()