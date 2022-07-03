import pygame
import pygame.font as fonts
from assets.data.data import levels as levels
from assets.data.data import leveldescs as leveldescs
import assets.data.colors as colors
import assets.hax as hax
from enum import Enum, unique, auto

# import os

pygame.init()
# hax.active = True
# os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 0'
screenwidth = 1072
screenheight = 1072
width = 1024
height = 1024
win = pygame.display.set_mode((screenwidth, screenheight), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Platman")
clock = pygame.time.Clock()
levelx = 0
levely = 0

prespacetiles = []
spacetiles = pygame.sprite.Group()
preblocktiles = []
blocktiles = pygame.sprite.Group()
prespawn = []
prelavatiles = []
lavatiles = pygame.sprite.Group()
preesctiles = []
esctiles = pygame.sprite.Group()
preelevtiles = []
elevtiles = pygame.sprite.Group()
precircuittiles = []
circuittiles = pygame.sprite.Group()
preswitchtiles = []
switchtiles = pygame.sprite.Group()
predoortiles = []
doortiles = pygame.sprite.Group()
sprites = pygame.sprite.Group()
sprites2 = pygame.sprite.Group()
collidetiles = pygame.sprite.Group()
elevcollidetiles = pygame.sprite.Group()

if hax.active:
    levelcount = hax.startlevel - 2
else:
    levelcount = 1
size = 32
currentlvl = [0]


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = size / 2
        self.height = size / 2
        self.momentum = 0
        self.acceleration = 1
        self.vel = 10
        self.alive = True
        self.spawn = [5000, 5000]
        self.escape = pygame.Rect(-5000, -5000, size, size)
        self.vertforce = 0
        self.gravity = 0.7
        self.jumpheight = 14
        self.tvel = 21
        self.jumping = False
        self.grounded = False
        self.escaped = True
        self.image = pygame.image.load("assets/img/platterman.png")
        self.rect = self.image.get_rect()
        self.levelcount = -1
        self.coyotetime = 4
        self.buffertime = 0
        self.buffering = False
        self.mask = pygame.mask.from_surface(self.image)

    def gravitycalc(self):
        self.grounded = False
        self.buffering = False
        self.rect.y += 3
        grounded = pygame.sprite.spritecollide(plat, collidetiles, False)
        if len(grounded) > 0 or self.rect.bottom >= height:
            self.rect.y -= 3
            self.grounded = True
        else:
            self.rect.y -= 3
            if self.jumping or self.vertforce < 0 or self.vertforce - self.gravity >= 0:
                if self.vertforce - self.gravity < -self.tvel:
                    self.vertforce = -self.tvel
                else:
                    self.vertforce -= self.gravity
            else:
                if self.buffertime > 0:
                    self.buffertime -= 1
                    self.buffering = True
                else:
                    self.vertforce -= self.gravity
        if self.grounded:
            self.jumping = False
            self.buffertime = self.coyotetime

    def move(self):
        # acceleration:vel ratio = 1:10
        # gravity:jumpheight:tvel ratio = 1:20:30

        # change motion values correspondingly to achieve different levels of "controlled speed" and "jump power"

        keys = pygame.key.get_pressed()

        if keys[pygame.K_p]:
            self.rect.y -= hax.flyspeed
        self.gravitycalc()

        if not keys[pygame.K_a] and not keys[pygame.K_d] and not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            if self.momentum < 0:
                self.momentum += 1
            if self.momentum > 0:
                self.momentum -= 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            if abs(self.momentum - self.acceleration) < self.vel:
                self.momentum -= self.acceleration
            else:
                self.momentum = -self.vel
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            if self.momentum + self.acceleration < self.vel:
                self.momentum += self.acceleration
            else:
                self.momentum = self.vel
        if keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]:
            if self.grounded or self.buffering:
                self.vertforce += self.jumpheight
                self.jumping = True

        if self.momentum < self.vel * -1:
            self.momentum += self.acceleration
        if self.momentum > self.vel:
            self.momentum -= self.acceleration

        self.rect.x += self.momentum
        collidedtiles = pygame.sprite.spritecollide(plat, collidetiles, False)

        for tile1 in collidedtiles:
            if self.momentum > 0:
                self.rect.right = tile1.rect.left
                self.momentum = 0
            elif self.momentum < 0:
                self.rect.left = tile1.rect.right
                self.momentum = 0
        if self.rect.right > width:
            self.rect.right = width
            self.momentum = 0
        if self.rect.left < 0:
            self.rect.left = 0
            self.momentum = 0

        self.rect.y -= self.vertforce
        collidedtiles = pygame.sprite.spritecollide(plat, collidetiles, False)

        for tile1 in collidedtiles:
            if self.vertforce < 0:
                self.rect.bottom = tile1.rect.top
                self.vertforce = 0
            elif self.vertforce > 0:
                self.rect.top = tile1.rect.bottom
                self.vertforce = 0
        if self.rect.bottom > height:
            self.rect.bottom = height
            self.vertforce = 0
        if self.rect.top < 0:
            self.rect.top = 0
            self.vertforce = 0

        collidedtiles = pygame.sprite.spritecollide(plat, collidetiles, False)
        if len(collidedtiles) > 0:
            die()


def die():
    plat.rect.x = spawn.x + size / 4
    plat.rect.y = spawn.y + size / 2


class Space(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.width = size
        self.height = size
        self.image = pygame.image.load("assets/img/space.png")
        self.rect = self.image.get_rect()


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.width = size
        self.height = size
        self.image = pygame.image.load("assets/img/block.png")
        self.rect = self.image.get_rect()


class Spawn(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.width = size
        self.height = size
        self.image = pygame.image.load("assets/img/spawn.png")
        self.rect = self.image.get_rect()


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.width = size
        self.height = size
        self.image = pygame.image.load("assets/img/lava.png")
        self.rect = self.image.get_rect()


class Esc(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.width = size
        self.height = size
        self.image = pygame.image.load("assets/img/escape.png")
        self.rect = self.image.get_rect()


class Elev(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.width = size
        self.height = size
        self.image = pygame.image.load("assets/img/elevator.png")
        self.rect = self.image.get_rect()
        self.direction = 0
        self.speed = 2

    # noinspection PyArgumentList
    @unique
    class Direction(Enum):
        up = auto()
        left = auto()
        down = auto()
        right = auto()
        
    def update(self):
        plat.downmoving = 0

        plat.rect.y +=3
        charcollide = pygame.sprite.collide_rect(self, plat)
        plat.rect.y -=3

        self.rect.y -= self.speed
        upcollidedtiles = pygame.sprite.spritecollide(self, circuittiles, False)
        upcanmove = pygame.sprite.spritecollide(self, elevcollidetiles, False)
        self.rect.y += self.speed

        self.rect.x -= self.speed
        leftcollidedtiles = pygame.sprite.spritecollide(self, circuittiles, False)
        leftcanmove = pygame.sprite.spritecollide(self, elevcollidetiles, False)
        self.rect.x += self.speed

        self.rect.y += self.speed
        downcollidedtiles = pygame.sprite.spritecollide(self, circuittiles, False)
        downcanmove = pygame.sprite.spritecollide(self, elevcollidetiles, False)
        self.rect.y -= self.speed

        self.rect.x += self.speed
        rightcollidedtiles = pygame.sprite.spritecollide(self, circuittiles, False)
        rightcanmove = pygame.sprite.spritecollide(self, elevcollidetiles, False)
        self.rect.x -= self.speed

        if self.direction == 0:
            self.direction = self.Direction.up

        if self.direction == self.Direction.up:
            if len(upcanmove) == 0 and len(upcollidedtiles) > 0 and self.rect.top - self.speed >= 0:
                self.rect.y -= self.speed
                if charcollide or pygame.sprite.collide_rect(self, plat):
                    plat.rect.y -= self.speed
            else:
                self.direction = self.Direction.left
        if self.direction == self.Direction.left:
            if len(leftcanmove) == 0 and len(leftcollidedtiles) > 0 and self.rect.left - self.speed >= 0:
                self.rect.x -= self.speed
                if charcollide or pygame.sprite.collide_rect(self, plat):
                    plat.rect.x -= self.speed
            else:
                self.direction = self.Direction.down
        if self.direction == self.Direction.down:
            if len(downcanmove) == 0 and len(downcollidedtiles) > 0 and self.rect.bottom + self.speed <= height:
                self.rect.y += self.speed
                if charcollide or pygame.sprite.collide_rect(self, plat):
                    plat.rect.y += self.speed
            else:
                self.direction = self.Direction.right
        if self.direction == self.Direction.right:
            if len(rightcanmove) == 0 and len(rightcollidedtiles) > 0 and self.rect.right + self.speed <= width:
                self.rect.x += self.speed
                if  charcollide or pygame.sprite.collide_rect(self, plat):
                    plat.rect.x += self.speed
            else:
                self.direction = self.Direction.up
                self.update()


class Circuit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.width = size
        self.height = size
        self.image = pygame.image.load("assets/img/circuit.png")
        self.rect = self.image.get_rect()


class Switch(pygame.sprite.Sprite):
    def __init__(self, x, y, ident):
        super().__init__()
        self.x = x
        self.y = y
        self.ident = ident
        self.width = size
        self.height = size
        self.image = pygame.image.load("assets/img/switch.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.pressed = False
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        if pygame.sprite.collide_mask(plat, self):
            if not self.pressed:
                self.pressed = True
                doortiles.update(self.ident)
        else:
            self.pressed = False


class Door(pygame.sprite.Sprite):
    def __init__(self, x, y, ident):
        super().__init__()
        self.x = x
        self.y = y
        self.ident = ident
        self.width = size
        self.height = size
        self.image = pygame.image.load("assets/img/door.png").convert_alpha()
        self.rect = self.image.get_rect()

    def update(self, ident):
        if self.ident == ident:
            if sprites2.has(self):
                self.remove(sprites2, collidetiles, elevcollidetiles)
            else:
                sprites2.add(self)
                collidetiles.add(self)
                elevcollidetiles.add(self)


def redrawgamewindow():
    sprites.draw(win)
    sprites2.draw(win)
    win.blit(leveltext, (4, 1024))
    win.blit(plat.image, plat.rect)
    # print(plat.rect.x, plat.rect.y)
    pygame.display.flip()


# final inits
plat = Player()
plat.rect.x, plat.rect.y = 100, 100

font1 = fonts.Font("assets/data/fonts/pixel-piss.ttf", 20)
leveltext = font1.render("???", False, colors.WHITE)

# main loop
run = True
while run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.mod & pygame.KMOD_CTRL:
                if pygame.key.get_pressed()[pygame.K_w]:
                    run = False

    if plat.escaped is True:
        plat.escaped = False
        levelcount += 1
        # print(levelcount)
        # print("escaped")
        currentlvl = levels[levelcount]
        leveltext = font1.render(f"Level {levelcount + 1} : {leveldescs[levelcount]}", False, colors.WHITE)

        prespacetiles.clear()
        spacetiles.empty()
        preblocktiles.clear()
        blocktiles.empty()
        prespawn = []
        spawn = Spawn(-10, -10)
        prelavatiles.clear()
        lavatiles.empty()
        preesctiles.clear()
        esctiles.empty()
        preelevtiles.clear()
        elevtiles.empty()
        precircuittiles.clear()
        circuittiles.empty()
        preswitchtiles.clear()
        switchtiles.empty()
        predoortiles.clear()
        doortiles.empty()
        sprites.empty()
        sprites2.empty()
        collidetiles.empty()

        for strip in currentlvl:
            for tile in strip:
                if tile == 0:
                    prespacetiles.append([levelx, levely])
                if tile == 1:
                    preblocktiles.append([levelx, levely])
                if tile == 2:
                    prespawn.append([levelx, levely])
                if tile == 3:
                    prelavatiles.append([levelx, levely])
                if tile == 4:
                    preesctiles.append([levelx, levely])
                if tile == 5:
                    precircuittiles.append([levelx, levely])
                    preelevtiles.append([levelx, levely])
                if tile == 6:
                    precircuittiles.append([levelx, levely])
                if int(str(tile)[0]) == 7:
                    prespacetiles.append([levelx, levely])
                    preswitchtiles.append([levelx, levely, int(str(tile)[1])])
                if int(str(tile)[0]) == 8:
                    if int(str(tile)[2]) == 0:
                        prespacetiles.append([levelx, levely])
                    if int(str(tile)[2]) == 1:
                        preblocktiles.append([levelx, levely])
                    if int(str(tile)[2]) == 2:
                        prespawn.append([levelx, levely])
                    if int(str(tile)[2]) == 3:
                        prelavatiles.append([levelx, levely])
                    if int(str(tile)[2]) == 4:
                        preesctiles.append([levelx, levely])
                    if int(str(tile)[2]) == 5:
                        preelevtiles.append([levelx, levely])
                    if int(str(tile)[2]) == 6:
                        precircuittiles.append([levelx, levely])
                    predoortiles.append([levelx, levely, int(str(tile)[1])])

                levelx += 1 * size
            levelx = 0
            levely += 1 * size
        levely = 0

        for pre in prespacetiles:
            tile = Space(pre[0], pre[1])
            tile.rect.x, tile.rect.y = tile.x, tile.y
            spacetiles.add(tile)
        for pre in preblocktiles:
            tile = Block(pre[0], pre[1])
            tile.rect.x, tile.rect.y = tile.x, tile.y
            blocktiles.add(tile)
        for pre in prespawn:
            tile = Spawn(pre[0], pre[1])
            tile.rect.x, tile.rect.y = tile.x, tile.y
            spawn = tile
        for pre in prelavatiles:
            tile = Lava(pre[0], pre[1])
            tile.rect.x, tile.rect.y = tile.x, tile.y
            lavatiles.add(tile)
        for pre in preesctiles:
            tile = Esc(pre[0], pre[1])
            tile.rect.x, tile.rect.y = tile.x, tile.y
            esctiles.add(tile)
        for pre in preelevtiles:
            tile = Elev(pre[0], pre[1])
            tile.rect.x, tile.rect.y = tile.x, tile.y
            elevtiles.add(tile)
        for pre in precircuittiles:
            tile = Circuit(pre[0], pre[1])
            tile.rect.x, tile.rect.y = tile.x, tile.y
            circuittiles.add(tile)
        for pre in preswitchtiles:
            tile = Switch(pre[0], pre[1], pre[2])
            tile.rect.x, tile.rect.y = tile.x, tile.y
            switchtiles.add(tile)
        for pre in predoortiles:
            tile = Door(pre[0], pre[1], pre[2])
            tile.rect.x, tile.rect.y = tile.x, tile.y
            doortiles.add(tile)

        if spawn == Spawn(-10, -10):
            print("Error: No spawn found")
            run = False

        sprites.add(spacetiles, blocktiles, spawn, lavatiles, esctiles, circuittiles)
        sprites2.add(elevtiles, switchtiles, doortiles)
        collidetiles.add(blocktiles, elevtiles, doortiles)
        elevcollidetiles.add(spacetiles, blocktiles, spawn, lavatiles, esctiles, switchtiles, doortiles)
        die()

    if pygame.sprite.spritecollide(plat, lavatiles, False):
        die()
    if pygame.sprite.spritecollide(plat, esctiles, False):
        plat.escaped = True

    elevtiles.update()
    switchtiles.update()
    plat.move()
    win.fill((0, 0, 0))
    redrawgamewindow()
pygame.quit()
