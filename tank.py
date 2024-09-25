import sys
import pygame
import random
from enum import Enum
from pygame.locals import *   #引入pygame中的所有常量

#定义窗口大小常量
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 500

#定义坦克大小常量
TANK_WIDTH = 50
TANK_HEIGHT = 50

#基地大小
BASE_WIDTH = 50
BASE_HEIGHT = 50

#定义子弹大小常量
BULLET_WIDTH = 20
BULLET_HEIGHT = 10

#定义子坦克和弹速度常量
TANK_SPEED = 5
BULLET_SPEED = 10

class Direction(Enum):
    DIR_UP = 1
    DIR_DOWN = 2
    DIR_LEFT = 3
    DIR_RIGHT = 4

class MenuItem(Enum):
    MENU_START = 1
    MENU_EXIT = 2

#游戏菜单
class GameMenu:
    def __init__(self):
        self.menu_items = {MenuItem.MENU_START: 'Start', MenuItem.MENU_EXIT: 'Exit'}
        self.current_item = 0
        self.font = pygame.font.Font(None, 28)
        #游戏结束图片
        self.game_over = pygame.image.load('images/game_over.png')
        self.game_over = pygame.transform.scale(self.game_over, (100, 100))

    def draw(self, screen):
        #居中显示Game Over
        pos_game_over = [SCREEN_WIDTH / 2 - self.game_over.get_width() / 2, SCREEN_HEIGHT / 2 - self.game_over.get_height() / 2]
        screen.blit(self.game_over, pos_game_over)
        for i, item in enumerate(self.menu_items.values()):
            #选中的菜单项颜色为红色
            if i == self.current_item:
                text = self.font.render(item, True, (255, 0, 0))
            else:
                text = self.font.render(item, True, (255, 255, 255))
            #基于Game Over的Y坐标，居中显示Menu
            pos = [SCREEN_WIDTH / 2 - text.get_width() / 2, pos_game_over[1] + self.game_over.get_height() + 10 + i * 40]
            screen.blit(text, pos)

    
    def next(self):
        self.current_item = (self.current_item + 1) % len(self.menu_items)
    
    def prev(self):
        self.current_item = (self.current_item - 1) % len(self.menu_items)

    def get_current_item(self):
        return list(self.menu_items.keys())[self.current_item]


#基类
class Body:
    def __init__(self, pos):
        self.pos = pos

    def getRect(self):
        return pygame.Rect(0,0,0,0)

#子弹类
class Bullet(Body):
    def __init__(self, pos, direction):
        super().__init__(pos)
        self.direction = direction
        #加载图片
        self.orgimage = pygame.image.load('images/bullet.png')
        self.orgimage = pygame.transform.scale(self.orgimage, (BULLET_WIDTH, BULLET_HEIGHT))
        self.image = self.orgimage.copy()
        #根据方向旋转图片
        if self.direction == Direction.DIR_UP:
            self.image = pygame.transform.rotate(self.orgimage, 0)
        elif self.direction == Direction.DIR_DOWN:
            self.image = pygame.transform.rotate(self.orgimage, 180)
        elif self.direction == Direction.DIR_LEFT:
            self.image = pygame.transform.rotate(self.orgimage, 90)
        elif self.direction == Direction.DIR_RIGHT:
            self.image = pygame.transform.rotate(self.orgimage, 270)

    #重写getRect方法
    def getRect(self):
        return pygame.Rect(self.pos[0], self.pos[1], BULLET_WIDTH, BULLET_HEIGHT)

    def move(self):
        if self.direction == Direction.DIR_UP:
            self.pos[1] -= BULLET_SPEED
        elif self.direction == Direction.DIR_DOWN:
            self.pos[1] += BULLET_SPEED
        elif self.direction == Direction.DIR_LEFT:
            self.pos[0] -= BULLET_SPEED
        elif self.direction == Direction.DIR_RIGHT:
            self.pos[0] += BULLET_SPEED
    
    #越界检测
    def isOut(self):
        if self.pos[0] < 0 or self.pos[0] > SCREEN_WIDTH or self.pos[1] < 0 or self.pos[1] > SCREEN_HEIGHT:
            return True
        return False

    def display(self, screen):
        screen.blit(self.image, self.pos)

#坦克类
class Tank(Body):
    def __init__(self, pos):
        super().__init__(pos)
        self.direction = Direction.DIR_UP
        self.speed = TANK_SPEED
        self.orgimage = pygame.image.load('images/tank.png')
        self.orgimage = pygame.transform.scale(self.orgimage, (TANK_WIDTH, TANK_HEIGHT))
        self.image = self.orgimage.copy()
        #子弹列表
        self.bullets = []

    #重写getRect方法
    def getRect(self):
        return pygame.Rect(self.pos[0], self.pos[1], TANK_WIDTH, TANK_HEIGHT)
    
    #碰撞检测
    def isColliding(self, pos, other_tanks):
        for other_tank in other_tanks:
            if pygame.Rect(other_tank.pos[0], other_tank.pos[1], TANK_WIDTH, TANK_HEIGHT).colliderect(pygame.Rect(pos[0], pos[1], TANK_WIDTH, TANK_HEIGHT)):
                return True
        return False

    def move(self, other_tanks):
        if self.direction == Direction.DIR_UP:
            self.pos[1] -= self.speed
        elif self.direction == Direction.DIR_DOWN:
            self.pos[1] += self.speed
        elif self.direction == Direction.DIR_LEFT:
            self.pos[0] -= self.speed
        elif self.direction == Direction.DIR_RIGHT:
            self.pos[0] += self.speed
        
        #越界检测
        if self.pos[0] < 0:
            self.pos[0] = 0
        if self.pos[0] > SCREEN_WIDTH - TANK_WIDTH:
            self.pos[0] = SCREEN_WIDTH - TANK_WIDTH
        if self.pos[1] < 0:
            self.pos[1] = 0
        if self.pos[1] > SCREEN_HEIGHT - TANK_HEIGHT:
            self.pos[1] = SCREEN_HEIGHT - TANK_HEIGHT
        
        #碰撞检测
        if self.isColliding(self.pos, other_tanks):
            if self.direction == Direction.DIR_UP:
                self.pos[1] += self.speed
            elif self.direction == Direction.DIR_DOWN:
                self.pos[1] -= self.speed
            elif self.direction == Direction.DIR_LEFT:
                self.pos[0] += self.speed
            elif self.direction == Direction.DIR_RIGHT:
                self.pos[0] -= self.speed


    def turn(self, direction):
        self.direction = direction
        if self.direction == Direction.DIR_UP:
            self.image = pygame.transform.rotate(self.orgimage, 0)
        elif self.direction == Direction.DIR_DOWN:
            self.image = pygame.transform.rotate(self.orgimage, 180)
        elif self.direction == Direction.DIR_LEFT:
            self.image = pygame.transform.rotate(self.orgimage, 90)
        elif self.direction == Direction.DIR_RIGHT:
            self.image = pygame.transform.rotate(self.orgimage, 270)

    def fire(self):
        #分方向计算子弹位置
        if self.direction == Direction.DIR_UP:
            bullet_pos = [self.pos[0] + (self.image.get_width() - BULLET_WIDTH) / 2, self.pos[1] - BULLET_HEIGHT]
        elif self.direction == Direction.DIR_DOWN:
            bullet_pos = [self.pos[0] + (self.image.get_width() - BULLET_WIDTH) / 2, self.pos[1] + self.image.get_height()]
        elif self.direction == Direction.DIR_LEFT:
            bullet_pos = [self.pos[0] - BULLET_WIDTH, self.pos[1] + (self.image.get_height() - BULLET_HEIGHT) / 2]
        elif self.direction == Direction.DIR_RIGHT:
            bullet_pos = [self.pos[0] + self.image.get_width(), self.pos[1] + (self.image.get_height() - BULLET_HEIGHT) / 2]
        self.bullets.append(Bullet(bullet_pos.copy(), self.direction))

    #移除越界的子弹
    def removeOutBullets(self):
        for bullet in self.bullets:
            if bullet.isOut():
                self.bullets.remove(bullet)

    def display(self, screen):
        screen.blit(self.image, self.pos)
        #显示子弹
        for bullet in self.bullets:
            bullet.move()
            bullet.display(screen)

#玩家坦克
class PlayerTank(Tank):
    def __init__(self, pos):
        super().__init__(pos)
        #生命数
        self.life = 3

    #重置
    def reset(self):
        self.life = 3
        self.pos = [275, 225]
        self.direction = Direction.DIR_UP
    
    #生命值减少
    def decreaseLife(self):
        if self.life > 0:
            self.life -= 1

    #是否存活
    def isAlive(self):
        return self.life > 0

#敌人坦克
class EnemyTank(Tank):
    def __init__(self, pos):
        super().__init__(pos)
        self.speed = TANK_SPEED - 2
        self.last_fire_time = 0
        #敌人坦克图片
        self.orgimage = pygame.image.load('images/enemy_tank.png')
        self.orgimage = pygame.transform.scale(self.orgimage, (TANK_WIDTH, TANK_HEIGHT))
        self.image = self.orgimage.copy()

    #敌人坦克随机移动
    def randomMove(self, other_tanks):
        if random.randint(0, 100) > 95:
            self.turn(random.choice([Direction.DIR_UP, Direction.DIR_DOWN, Direction.DIR_LEFT, Direction.DIR_RIGHT]))
        self.move(other_tanks)

    #敌人坦克间隔一定时间随机开火
    def randomFire(self):
        if pygame.time.get_ticks() - self.last_fire_time > 1000:
            if random.randint(0, 100) > 95:
                self.fire()
                self.last_fire_time = pygame.time.get_ticks()

class Explosion:
    def __init__(self, pos):
        self.images = [pygame.image.load(f'images/explosion{i}.png') for i in range(1, 6)]
        self.index = 0
        self.pos = pos
        self.active = True

        #缩放图片
        for i in range(len(self.images)):
            self.images[i] = pygame.transform.scale(self.images[i], (TANK_WIDTH, TANK_HEIGHT))

    def update(self):
        self.index += 1
        if self.index >= len(self.images):
            self.active = False

    def draw(self, screen):
        if self.active:
            screen.blit(self.images[self.index], self.pos)

#中央基地
class BasePlace(Body):
    def __init__(self, pos):
        super().__init__(pos)
        self.image = pygame.image.load('images/base.png')
        self.image = pygame.transform.scale(self.image, (BASE_WIDTH, BASE_HEIGHT))

    def getRect(self):
        return pygame.Rect(self.pos[0], self.pos[1], BASE_WIDTH, BASE_HEIGHT)

    def display(self, screen):
        screen.blit(self.image, self.pos)

#主函数
def main():
    #初始化
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) #创建窗口 大小为600*500
    pygame.display.set_caption('Tank Game') #设置窗口标题
    #设置窗口图标
    icon = pygame.image.load('images/tank.png')
    pygame.display.set_icon(icon)

    #暗黑灰色
    gray = (50, 50, 50)

    #创建时钟对象（控制游戏的FPS）
    clock = pygame.time.Clock()
    #坦克对象
    tank = PlayerTank([275, 225])
    #敌人坦克list
    enemyTanks = []
    #初始化爆炸列表
    explosions = []
    #随机生成5个敌人坦克, 避免重叠, 不能和玩家坦克重叠
    for i in range(5):
        enemyTank = EnemyTank([random.randint(0, SCREEN_WIDTH - TANK_WIDTH), random.randint(0, SCREEN_HEIGHT - TANK_HEIGHT)])
        while enemyTank.isColliding(enemyTank.pos, enemyTanks) or enemyTank.isColliding(enemyTank.pos, [tank]):
            enemyTank = EnemyTank([random.randint(0, SCREEN_WIDTH - TANK_WIDTH), random.randint(0, SCREEN_HEIGHT - TANK_HEIGHT)])
        enemyTanks.append(enemyTank)

    #基地对象，底部中间
    base = BasePlace([SCREEN_WIDTH / 2 - BASE_WIDTH / 2, SCREEN_HEIGHT - BASE_HEIGHT])

    #菜单对象
    menu = GameMenu()
    #分数
    score = 0
    #播放背景音乐
    pygame.mixer.music.load('sounds/bg_music.mp3')
    pygame.mixer.music.play(-1)

    #事件循环
    while True:
        clock.tick(30) #每秒执行30次
        #事件循环
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            #按键按下事件
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit()
                if tank.isAlive() == False: #游戏结束,操作菜单
                    if event.key == K_UP:
                        menu.prev()
                    if event.key == K_DOWN:
                        menu.next()
                    if event.key == K_RETURN:
                        if menu.get_current_item() == MenuItem.MENU_START:
                            tank.reset()
                            enemyTanks.clear()
                            for i in range(5):
                                enemyTank = EnemyTank([random.randint(0, SCREEN_WIDTH - TANK_WIDTH), random.randint(0, SCREEN_HEIGHT - TANK_HEIGHT)])
                                while enemyTank.isColliding(enemyTank.pos, enemyTanks):
                                    enemyTank = EnemyTank([random.randint(0, SCREEN_WIDTH - TANK_WIDTH), random.randint(0, SCREEN_HEIGHT - TANK_HEIGHT)])
                                enemyTanks.append(enemyTank)
                            score = 0
                        elif menu.get_current_item() == MenuItem.MENU_EXIT:
                            sys.exit()
                else:
                    if event.key == K_LEFT:
                        tank.turn(Direction.DIR_LEFT)
                    if event.key == K_RIGHT:
                        tank.turn(Direction.DIR_RIGHT)
                    if event.key == K_UP:
                        tank.turn(Direction.DIR_UP)
                    if event.key == K_DOWN:
                        tank.turn(Direction.DIR_DOWN)
                    if event.key == K_SPACE:
                        tank.fire()

        #判断是否按下了键盘
        pressed_keys = pygame.key.get_pressed()
        # 更新坦克位置，只处理一个按键
        if pressed_keys[K_LEFT]:
            tank.move(enemyTanks)
        elif pressed_keys[K_RIGHT]:
            tank.move(enemyTanks)
        elif pressed_keys[K_UP]:
            tank.move(enemyTanks)
        elif pressed_keys[K_DOWN]:
            tank.move(enemyTanks)

        #补充敌人坦克，随机生成，避免重叠
        if len(enemyTanks) < 5:
            enemyTank = EnemyTank([random.randint(0, SCREEN_WIDTH - TANK_WIDTH), random.randint(0, SCREEN_HEIGHT - TANK_HEIGHT)])
            while enemyTank.isColliding(enemyTank.pos, enemyTanks):
                enemyTank = EnemyTank([random.randint(0, SCREEN_WIDTH - TANK_WIDTH), random.randint(0, SCREEN_HEIGHT - TANK_HEIGHT)])
            enemyTanks.append(enemyTank)

        #敌人坦克随机移动
        for enemyTank in enemyTanks:
            #除去自己
            other_tanks = enemyTanks.copy()
            other_tanks.remove(enemyTank)
            other_tanks.append(tank)
            enemyTank.randomMove(other_tanks)

        #敌人坦克随机开火
        for enemyTank in enemyTanks:
            enemyTank.randomFire()

        #移除越界的子弹
        tank.removeOutBullets()

        #子弹和敌人坦克碰撞检测
        for bullet in tank.bullets:
            for enemyTank in enemyTanks:
                if pygame.Rect(enemyTank.pos[0], enemyTank.pos[1], TANK_WIDTH, TANK_HEIGHT).colliderect(pygame.Rect(bullet.pos[0], bullet.pos[1], BULLET_WIDTH, BULLET_HEIGHT)):
                    tank.bullets.remove(bullet)
                    enemyTanks.remove(enemyTank)
                    explosions.append(Explosion(enemyTank.pos))
                    score += 100

        #敌人子弹和玩家坦克碰撞检测
        for enemyTank in enemyTanks:
            for bullet in enemyTank.bullets:
                if pygame.Rect(tank.pos[0], tank.pos[1], TANK_WIDTH, TANK_HEIGHT).colliderect(pygame.Rect(bullet.pos[0], bullet.pos[1], BULLET_WIDTH, BULLET_HEIGHT)):
                    enemyTank.bullets.remove(bullet)
                    tank.decreaseLife()
                    explosions.append(Explosion(tank.pos))

        #玩家子弹和敌人子弹碰撞检测
        for bullet in tank.bullets:
            for enemyTank in enemyTanks:
                for enemyBullet in enemyTank.bullets:
                    if pygame.Rect(enemyBullet.pos[0], enemyBullet.pos[1], BULLET_WIDTH, BULLET_HEIGHT).colliderect(pygame.Rect(bullet.pos[0], bullet.pos[1], BULLET_WIDTH, BULLET_HEIGHT)):
                        tank.bullets.remove(bullet)
                        enemyTank.bullets.remove(enemyBullet)
        
        #显示
        screen.fill(gray)

        #右上角显示分数和生命数，不能被坦克遮挡
        font = pygame.font.Font(None, 28)
        text = font.render('Score: ' + str(score), True, (255, 255, 255))
        screen.blit(text, [SCREEN_WIDTH - text.get_width() - 5, 10])
        text = font.render('Life:  ' + str(tank.life), True, (255, 255, 255))
        screen.blit(text, [SCREEN_WIDTH - text.get_width() - 5, 38])

        #Tank如果死亡，显示Game Over
        if tank.isAlive() == False:
            #显示菜单
            menu.draw(screen)

        else: #否则显示游戏画面
            #显示坦克
            tank.display(screen)  
            #显示敌人坦克
            for enemyTank in enemyTanks:
                enemyTank.display(screen)
            #显示基地
            #base.display(screen)
            #显示爆炸
            for explosion in explosions:
                explosion.update()
                explosion.draw(screen)

        pygame.display.update()

if __name__ == "__main__":
    main()