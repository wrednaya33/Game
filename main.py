import pygame
import os
import random
from threading import Thread
import time

def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image

pygame.init()

size = 300, 400
scr = pygame.display.set_mode(size)

font = pygame.font.SysFont('serif', 24)


image = load_image("road.jpg")
image2 = load_image("road.jpg")
rect = image.get_rect()
rect2 = image2.get_rect()
rect2.y = -rect.height
scr.blit(image, rect)
scr.blit(image2, rect2)
size_im = rect.width, rect.height

player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

class Player(pygame.sprite.Sprite):
    image = load_image("player.png", -1)
    image = pygame.transform.scale(image, (50, 100))
    MAX_V = 10

    def __init__(self):
        super().__init__(player_group)
        self.image = Player.image
        self.rect = self.image.get_rect()
        self.rect.x = size[0] // 2 - self.rect.width // 2
        self.rect.y = size[1] - 100
        self.step = 1
        self.v = 0
        self.napr = 0


    def update_v(self, v):
        self.v += v
        if self.v < 0:
            self.v = 0
        if self.v > self.MAX_V:
            self.v = self.MAX_V

    def update(self, napr):
        self.napr = napr
        self.rect.x += self.step * napr
        if self.rect.x >= size[0] - self.rect.width:
            self.rect.x = size[0] - self.rect.width
        if self.rect.x < 0:
            self.rect.x = 0


class Enemy(pygame.sprite.Sprite):
    image = load_image("enemy.png", -1)
    image = pygame.transform.scale(image, (50, 100))


    def __init__(self):
        super().__init__(enemy_group)
        self.image = Enemy.image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, size_im[0] - self.rect.width)
        self.rect.y = -self.rect.height

    def move(self):
        self.rect.y += 1

class Enemy_mafia(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name
        self.play = True

    def run(self):
        while self.play:
            amount = random.randint(300, 2000)
            time.sleep(amount / 1000)
            Enemy()


class Camera:
    def __init__(self, field_size):
        self.dx = 0
        self.dy = 0
        self.field_size = field_size
        self.dx_f = 0

    def clear(self):
        self.dx = 0
        self.dy = 0
        self.dx_f = 0

    def apply_dist(self):
        return self.dy

    def apply(self, obj):
        obj.rect.x += self.dx_f

    def apply_fon(self, rect):
        x = rect.x
        rect.x += self.dx
        if rect.x < -(rect.width - self.field_size[0]):
            rect.x = -(rect.width - self.field_size[0])
        if rect.x >= 0:
            rect.x = 0
        rect.y += self.dy
        if rect.y >= self.field_size[1]:
            rect.y = -size_im[1]
        self.dx_f = rect.x - x


    def update(self, target):
        self.dx = target.step * -target.napr
        self.dy = target.v


player = Player()

motion = 0
v = 0
camera = Camera(size)
life = 3
distance = 0
finish = 50000


running = True
playing = False
begin = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            enemy_thread.play = False
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and playing:
                motion = -1
                player.update(motion)
            if event.key == pygame.K_RIGHT and playing:
                motion = 1
                player.update(motion)
            if event.key == pygame.K_UP and playing:
                player.update_v(1)
            if event.key == pygame.K_DOWN and playing:
                player.update_v(-1)
            if event.key == pygame.K_SPACE and not playing:
                playing = True
                begin = False
                life = 3
                distance = 0
                enemy_group.empty()
                camera.clear()
                player.v = 0
                enemy_thread = Enemy_mafia(1)
                enemy_thread.start()
        if event.type == pygame.KEYUP:
            motion = 0

    if playing:
        player.update(motion)
        camera.update(player)
        camera.apply_fon(rect)
        camera.apply_fon(rect2)
        distance += camera.apply_dist()

        scr.blit(image,rect)
        scr.blit(image2,rect2)
        player_group.draw(scr)

        for e in enemy_group:
            e.move()
            camera.apply(e)
            if e.rect.y > size[1]:
                   enemy_group.remove(e)
            if pygame.sprite.spritecollideany(e, player_group):
                enemy_group.remove(e)
                life -= 1

        enemy_group.draw(scr)
        text = font.render("Жизни:" + str(life), 0, (0, 0, 0))
        scr.blit(text, (0, 0))


        if life < 0:
            enemy_thread.play = False
            playing = False
            lose = load_image("gameover.jpg")
            lose = pygame.transform.scale(lose, size)
            scr.blit(lose, lose.get_rect())
        if distance > finish:
            enemy_thread.play = False
            playing = False
            win = load_image("win.jpg")
            win = pygame.transform.scale(win, size)
            scr.blit(win, win.get_rect())

    if begin:
        bg = load_image("begin.jpg")
        bg = pygame.transform.scale(bg, size)
        scr.blit(bg, bg.get_rect())

    pygame.display.flip()

pygame.quit()