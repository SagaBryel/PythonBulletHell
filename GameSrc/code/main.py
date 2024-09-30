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
        pygame.display.set_caption('Purgatory Escape')
        self.clock = pygame.time.Clock()
        self.running = True


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
        self.enemy_spawn_timer = 2000
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, self.enemy_spawn_timer)
        self.spawn_positions = []

        # audio
        self.shoot_sound = pygame.mixer.Sound(join('..', 'audio', 'shoot.ogg'))
        self.shoot_sound.set_volume(0.2)
        self.impact_sound = pygame.mixer.Sound(join('..', 'audio', 'impact.ogg'))
        self.impact_sound.set_volume(0.2)
        self.music = pygame.mixer.Sound(join('..', 'audio', 'music1.ogg'))
        self.music.set_volume(0.3)
        self.music.play()

        #setup
        self.load_images()
        self.setup()


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

    def automatic_shooting(self):
        # Disparo automático do arco
        if self.can_shoot:
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
                    self.impact_sound.play()
                    for sprite in collision_sprites:
                        sprite.destroy()
                    arrow.kill()

    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            self.running = False

    def run(self):
        while self.running:
            # dt
            dt = self.clock.tick() / 1000

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event:
                    Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())),
                          (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)

            # update
            self.bow_timer()
            self.automatic_shooting()
            self.all_sprites.update(dt)
            self.arrow_collision()


            # draw
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)
            pygame.display.update()
            print(self.arrow_sprites)

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()