import os

from player import Player
from collidersprytes import *
from pytmx.util_pygame import load_pygame

from random import randint

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Purgatory Escape')
        self.clock = pygame.time.Clock()
        self.running = True

        # groups
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        self.setup()

        # sprites
        self.player = Player((500,500), self.all_sprites, self.collision_sprites)
        #for i in range(6):
            # Adicionando o Sprite a dois grupos. O que não acontece com o player que só está no grupo all_sprytes.
            # Porem o player recebe collision_sprites como argumento (verificar no construtor do player)
            # Isso é feito pois não queremos o player nesse grupo, não queremos que ele colida com ele mesmo.
            # CollisionSprite((x,y), (w,h), (self.all_sprites, self.collision_sprites))

    def setup(self):
        #map_path = os.path.join('data', 'maps', 'mapa.tmx')
        #map = load_pygame(map_path)
        map = load_pygame(join('..', 'data', 'maps', 'mapa.tmx'))

        for x, y, image in map.get_layer_by_name('Camada1').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
        for obj in map.get_layer_by_name('Objetos'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
        for obj in map.get_layer_by_name('Collider'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

    def run(self):
        while self.running:
            # dt
            dt = self.clock.tick() / 1000

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # update
            self.all_sprites.update(dt)

            # draw
            self.display_surface.fill('black')
            self.all_sprites.draw(self.display_surface)
            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()