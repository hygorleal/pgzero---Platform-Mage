import pgzrun
import random
import math

WIDTH = 800
HEIGHT = 400

MENU = 'menu'
PLAYING = 'playing'
GAME_OVER = 'game_over'
VICTORY = 'victory'
CONTROLS = 'controls'  
current_state = MENU

hero_run = [f"hero_run{i}" for i in range(1, 5)]
hero_idle = [f"hero_idle{i}" for i in range(1, 3)]
enemy_anim = [f"enemy{i}" for i in range(1, 3)]
bullet_img = "bullet"
trophy_img = "trophy"
background_img = "background"

hero = Actor(hero_idle[0], pos=(50, HEIGHT - 60))
hero.vx = 0
hero.vy = 0
hero.speed = 3
hero.gravity = 0.5
hero.jump_strength = -12
hero.on_ground = True
hero.lives = 2
hero.frame = 0
hero.facing_right = True

bullets = []
enemies = []
trophy = Actor(trophy_img, pos=(750, HEIGHT - 60))

music_on = True
sounds_on = True

menu_buttons = {
    "start": Rect((WIDTH//2 - 80, 120, 160, 40)),
    "controls": Rect((WIDTH//2 - 80, 180, 160, 40)),  
    "toggle_sound": Rect((WIDTH//2 - 80, 240, 160, 40)),
    "exit": Rect((WIDTH//2 - 80, 300, 160, 40)),  
}

back_button = Rect((WIDTH//2 - 80, HEIGHT - 60, 160, 40)) 
restart_button = Rect((WIDTH//2 - 80, HEIGHT//2 + 40, 160, 40))

class Platform:
    def __init__(self, x, y, width):
        self.actor = Actor("platform", pos=(x, y))
        self.width = width
        self.actor.width = width
        
    def draw(self):
        self.actor.draw()

platforms = [
    Platform(300, HEIGHT - 80, 200),
    Platform(500, HEIGHT - 150, 250),
]

def spawn_enemies():
    for i in range(4):
        enemy = Actor(enemy_anim[0], pos=(250 + i*150, HEIGHT - 60))
        enemy.direction = 1
        enemy.speed = 1.5
        enemy.frame = 0
        enemies.append(enemy)

spawn_enemies()

def update():
    global current_state

    if current_state == PLAYING:
        update_hero()
        update_bullets()
        update_enemies()
        check_collisions()

def update_hero():
    global hero
    hero.frame += 0.1
    previous_y = hero.y

    if keyboard.right:
        hero.x += hero.speed
        hero.facing_right = True
        hero.image = hero_run[int(hero.frame) % len(hero_run)]
    elif keyboard.left:
        hero.x -= hero.speed
        hero.facing_right = False
        hero.image = hero_run[int(hero.frame) % len(hero_run)]
    else:
        hero.image = hero_idle[int(hero.frame) % len(hero_idle)]

    if keyboard.space and hero.on_ground:
        hero.vy = hero.jump_strength
        hero.on_ground = False
        if sounds_on:
            try:
                sounds.jump.play()
            except:
                pass

    hero.vy += hero.gravity
    hero.y += hero.vy

    if hero.y >= HEIGHT - 60:
        hero.y = HEIGHT - 60
        hero.vy = 0
        hero.on_ground = True
    else:
        hero.on_ground = False

    for platform in platforms:
        if (hero.x + hero.width/2 > platform.actor.x - platform.width/2 and 
            hero.x - hero.width/2 < platform.actor.x + platform.width/2):
            
            if previous_y + hero.height/2 <= platform.actor.y - platform.actor.height/2 and hero.y + hero.height/2 >= platform.actor.y - platform.actor.height/2:
                hero.on_ground = True
                hero.y = platform.actor.y - platform.actor.height/2 - hero.height/2
                hero.vy = 0
                break

def update_bullets():
    for bullet in bullets[:]:
        bullet.x += 5 if bullet.dir == 'right' else -5
        if bullet.x < 0 or bullet.x > WIDTH:
            bullets.remove(bullet)

def update_enemies():
    for enemy in enemies:
        enemy.frame += 0.1
        enemy.image = enemy_anim[int(enemy.frame) % len(enemy_anim)]
        enemy.x += enemy.direction * enemy.speed
        if enemy.x < 200 or enemy.x > 600:
            enemy.direction *= -1

def check_collisions():
    global current_state

    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if bullet.colliderect(enemy):
                bullets.remove(bullet)
                enemies.remove(enemy)
                break

    for enemy in enemies:
        if hero.colliderect(enemy):
            hero.lives -= 1
            hero.x = 50
            if hero.lives <= 0:
                current_state = GAME_OVER

    if hero.colliderect(trophy):
        current_state = VICTORY

def on_key_down(key):
    global current_state
    
    if current_state == PLAYING:
        if key == keys.Z:
            fire_bullet()

def fire_bullet():
    if len(bullets) == 0:
        direction = 'right' if hero.facing_right else 'left'
        bullet = Actor(bullet_img, pos=(hero.x, hero.y))
        bullet.dir = direction
        bullets.append(bullet)
        if sounds_on:
            try:
                sounds.shoot.play()
            except:
                pass

def draw():
    screen.clear()

    if current_state == MENU:
        draw_menu()
    elif current_state == PLAYING:
        draw_game()
    elif current_state == GAME_OVER:
        draw_game_over()
    elif current_state == VICTORY:
        draw_victory()
    elif current_state == CONTROLS:
        draw_controls()

def draw_game():
    screen.blit(background_img, (0, 0))
    hero.draw()
    trophy.draw()
    for bullet in bullets:
        bullet.draw()
    for enemy in enemies:
        enemy.draw()
    for platform in platforms:
        platform.draw()

    screen.draw.text(f"Lives: {hero.lives}", topleft=(10, 10), fontsize=30)

def draw_menu():
    screen.draw.text("Platform Mage", center=(WIDTH//2, 60), fontsize=50, color="white")
    screen.draw.filled_rect(menu_buttons["start"], "blue")
    screen.draw.text("Start Game", center=menu_buttons["start"].center, color="white")
    
    screen.draw.filled_rect(menu_buttons["controls"], "purple")  
    screen.draw.text("Controls", center=menu_buttons["controls"].center, color="white")
    
    sound_button_color = "green" if music_on else "gray"
    screen.draw.filled_rect(menu_buttons["toggle_sound"], sound_button_color)
    screen.draw.text("Toggle Sound", center=menu_buttons["toggle_sound"].center, color="white")
    
    screen.draw.filled_rect(menu_buttons["exit"], "red")
    screen.draw.text("Exit", center=menu_buttons["exit"].center, color="white")

def draw_controls():
    screen.fill((0, 0, 50))  
    screen.draw.text("Controles", center=(WIDTH//2, 60), fontsize=50, color="white")
    
  
    controls_text = [
        "Setas Esquerda/Direita - Mover",
        "Barra de Espaco - Pular",
        "Tecla Z - Atirar",
        "Alcance o trofeu para vencer!",
        "Evite os inimigos!"
    ]
    
    y_pos = 120
    for text in controls_text:
        screen.draw.text(text, center=(WIDTH//2, y_pos), fontsize=30, color="white")
        y_pos += 40
    
    screen.draw.filled_rect(back_button, "blue")
    screen.draw.text("Voltar", center=back_button.center, color="white")

def draw_game_over():
    screen.draw.text("Game Over!", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="red")
    screen.draw.filled_rect(restart_button, "blue")
    screen.draw.text("Restart", center=restart_button.center, color="white")

def draw_victory():
    screen.draw.text("You Win!", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="green")
    screen.draw.filled_rect(restart_button, "blue")
    screen.draw.text("Restart", center=restart_button.center, color="white")

def on_mouse_down(pos):
    global current_state, music_on, sounds_on

    if current_state == MENU:
        if menu_buttons["start"].collidepoint(pos):
            current_state = PLAYING
            if music_on:
                music.play("background")
        elif menu_buttons["controls"].collidepoint(pos):
            current_state = CONTROLS
        elif menu_buttons["toggle_sound"].collidepoint(pos):
            music_on = not music_on
            if not music_on:
                music.stop()
        elif menu_buttons["exit"].collidepoint(pos):
            exit()
    elif current_state in [GAME_OVER, VICTORY]:
        if restart_button.collidepoint(pos):
            reset_game()
    elif current_state == CONTROLS:
        if back_button.collidepoint(pos):
            current_state = MENU

def reset_game():
    global current_state, hero, bullets, enemies, platforms
    current_state = PLAYING
    hero = Actor(hero_idle[0], pos=(50, HEIGHT - 60))
    hero.vx = 0
    hero.vy = 0
    hero.speed = 3
    hero.gravity = 0.5
    hero.jump_strength = -12
    hero.on_ground = True
    hero.lives = 2
    hero.frame = 0
    hero.facing_right = True
    bullets.clear()
    enemies.clear()
    spawn_enemies()

pgzrun.go()