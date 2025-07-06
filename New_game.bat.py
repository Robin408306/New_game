import pygame
import sys
import random
import os

pygame.init()

# Fixed virtual resolution
VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 800, 600
game_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

fullscreen = False
screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
pygame.display.set_caption("Rock Dodge Game")

clock = pygame.time.Clock()

WHITE, BLACK, RED = (255,255,255), (0,0,0), (200,0,0)
LEVEL_COLORS = [(255,255,255), (220,240,255), (200,230,250),
                (180,220,240), (160,210,230), (140,200,220)]
player_colors = [(random.randint(0,255),random.randint(0,255),random.randint(0,255)) for _ in range(100)]
current_color_index = 0
player_size = (50, 50)
player_speed = 5

rock_size = (40, 40)
num_rocks = 5

volume = 0.5
bg_tracks = ["bg_music1.mp3", "bg_music2.mp3", "bg_music3.mp3"]
current_track = 0
pygame.mixer.music.load(bg_tracks[current_track])
pygame.mixer.music.set_volume(volume)
pygame.mixer.music.play(-1)

highscore_file = "highscore.txt"
if os.path.exists(highscore_file):
    try: highscore = int(open(highscore_file).read())
    except: highscore = 0
else: highscore = 0

def draw_text(surface, text, size, color, x, y):
    font = pygame.font.SysFont(None, size)
    img = font.render(text, True, color)
    surface.blit(img, (x, y))

def create_rocks(num, speed):
    return [{"rect": pygame.Rect(random.randint(0, VIRTUAL_WIDTH - rock_size[0]),
                                 random.randint(-100, -40), *rock_size),
             "speed": random.randint(3+speed, 6+speed)} for _ in range(num)]

def toggle_fullscreen():
    global fullscreen, screen
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

def settings_menu():
    global current_color_index, volume
    color_input = ""
    while True:
        game_surface.fill(WHITE)
        draw_text(game_surface,"=== SETTINGS ===", 48, BLACK, 100, 50)
        draw_text(game_surface,f"Player Color Index: {current_color_index}", 36, BLACK, 100, 120)
        draw_text(game_surface,f"(type 0–99, current input: {color_input})", 24, BLACK, 100, 160)
        draw_text(game_surface,f"Volume: {int(volume*100)}%", 36, BLACK, 100, 220)
        draw_text(game_surface,"(+ to increase, - to decrease)", 24, BLACK, 100, 260)
        draw_text(game_surface,"Press Q to return to game", 24, BLACK, 100, 300)
        pygame.draw.rect(game_surface, player_colors[current_color_index], (500,120,100,100))
        scaled = pygame.transform.smoothscale(game_surface, screen.get_size())
        screen.blit(scaled,(0,0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_q: return
                elif event.key in [pygame.K_0,pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4,
                                   pygame.K_5,pygame.K_6,pygame.K_7,pygame.K_8,pygame.K_9]:
                    color_input += event.unicode
                    try:
                        idx=int(color_input)
                        if 0<=idx<100: current_color_index=idx
                    except: pass
                elif event.key==pygame.K_BACKSPACE: color_input=color_input[:-1]
                elif event.key==pygame.K_PLUS or event.key==pygame.K_EQUALS:
                    volume=min(1.0,volume+0.1); pygame.mixer.music.set_volume(volume)
                elif event.key==pygame.K_MINUS:
                    volume=max(0.0,volume-0.1); pygame.mixer.music.set_volume(volume)

def game_over_screen(score):
    global highscore
    if score>highscore:
        highscore=score
        with open(highscore_file,"w") as f: f.write(str(highscore))
    while True:
        game_surface.fill(RED)
        draw_text(game_surface,"GAME OVER", 72, WHITE, 200,150)
        draw_text(game_surface,f"Score: {score}",48, WHITE,250,250)
        draw_text(game_surface,f"High Score: {highscore}",36,WHITE,250,320)
        draw_text(game_surface,"R=Restart | N=New Game | Q=Quit",24,WHITE,200,380)
        scaled = pygame.transform.smoothscale(game_surface, screen.get_size())
        screen.blit(scaled,(0,0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key in [pygame.K_r,pygame.K_n]: game_loop(); return
                if event.key==pygame.K_q: pygame.quit(); sys.exit()

def start_screen():
    while True:
        game_surface.fill(WHITE)
        draw_text(game_surface,"ROCK DODGE GAME", 64, BLACK,150,150)
        draw_text(game_surface,"Press P to Play | S=Settings | Q=Quit",32,BLACK,150,300)
        scaled = pygame.transform.smoothscale(game_surface, screen.get_size())
        screen.blit(scaled,(0,0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_p: return
                if event.key==pygame.K_s: settings_menu()
                if event.key==pygame.K_q: pygame.quit(); sys.exit()

def game_loop():
    global current_color_index, current_track
    player_pos=[VIRTUAL_WIDTH//2,VIRTUAL_HEIGHT-player_size[1]-10]
    rocks=create_rocks(num_rocks,0)
    paused=False; score=0; level_speed=0; current_level=1
    start_ticks=pygame.time.get_ticks()
    while True:
        clock.tick(60)
        elapsed=(pygame.time.get_ticks()-start_ticks)//1000
        score=elapsed
        if elapsed%5==0: level_speed=int(elapsed//5)
        current_level=min(len(LEVEL_COLORS),(score//30)+1)
        new_track=(score//30)%len(bg_tracks)
        if new_track!=current_track:
            current_track=new_track
            pygame.mixer.music.load(bg_tracks[current_track])
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_p: paused=not paused
                if event.key==pygame.K_s: settings_menu()
                if event.key==pygame.K_f: toggle_fullscreen()
        if not paused:
            keys=pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: player_pos[0]-=player_speed
            if keys[pygame.K_RIGHT]: player_pos[0]+=player_speed
            if keys[pygame.K_UP]: player_pos[1]-=player_speed
            if keys[pygame.K_DOWN]: player_pos[1]+=player_speed
            player_pos[0]=max(0,min(player_pos[0],VIRTUAL_WIDTH - player_size[0]))
            player_pos[1]=max(0,min(player_pos[1],VIRTUAL_HEIGHT - player_size[1]))
            for rock in rocks:
                rock["rect"].y+=rock["speed"]+int(level_speed**0.7)
                if rock["rect"].y>VIRTUAL_HEIGHT:
                    rock["rect"].y=random.randint(-100,-40)
                    rock["rect"].x=random.randint(0,VIRTUAL_WIDTH - rock_size[0])
                    rock["speed"]=random.randint(3+level_speed,6+level_speed)
            player_rect=pygame.Rect(*player_pos,*player_size)
            for rock in rocks:
                if player_rect.colliderect(rock["rect"]): game_over_screen(score); return
        game_surface.fill(LEVEL_COLORS[(current_level-1)%len(LEVEL_COLORS)])
        pygame.draw.rect(game_surface, player_colors[current_color_index], (*player_pos,*player_size))
        for rock in rocks: pygame.draw.rect(game_surface,(128,128,128),rock["rect"])
        draw_text(game_surface,f"Score:{score}",36,BLACK,10,10)
        draw_text(game_surface,f"Level:{current_level}",24,BLACK,10,50)
        draw_text(game_surface,f"High Score:{highscore}",24,BLACK,10,80)
        draw_text(game_surface,"P=Pause | S=Settings | F=Fullscreen",24,BLACK,10,110)
        scaled=pygame.transform.smoothscale(game_surface,screen.get_size())
        screen.blit(scaled,(0,0))
        pygame.display.flip()

start_screen()
game_loop()
pygame.quit()
