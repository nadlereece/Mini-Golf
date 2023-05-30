import pygame
from pygame.constants import KEYUP
from pygame import *
from pygame.math import Vector2
from forces import Friction
from physics_objects import Circle, Polygon, Wall, UniformPolygon, UniformCircle
from contact import generate_contact, resolve_contact
import itertools
import math
from pygame import mixer

# initialize pygame and open window
pygame.init()

# ALL CREDIT TO NINTENDO CIRCA 1983 FROM KIRBY'S ADVENTURE FOR THIS MUSIC
mixer.music.load('Vegetable Valley - Kirbys Adventure.mp3')
mixer.music.play(-1)

def mag(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1])

def clamp(value,min,max): #clamps a value, used for limiting the charged velocity
    if(value > max):
        value = max
    elif(value < min):
        value = min
    return value

# Variables
BALL_STOPPED = 0
AIMING_BALL = 1
CHARGING_BALL = 2
BALL_ROLLING = 3
WIN = 4

width, height = 800, 600
window = pygame.display.set_mode([width, height])
center = Vector2(width/2, height/2)
bumper_center = 300

objects1 = []
objects2 = []
objects3 = []
holes = []
par = [0, 3, 4, 5]
balls = []
obstacles = []
rotators = []
strokes = 0
state = 1
stage = 0
seconds = 0
hold_time = 0
charging = False
hole1Win = False
hole2Win = False
hole3Win = False
ballSize = 6
k = ((2 * math.pi) / 3) ** 2
mousePosition = [400,300]

# set timing stuff
fps = 120
dt = 1/fps
clock = pygame.time.Clock()

#stage 1 objects
ground1 = Polygon(offsets = ([0, 0], [0, -100], [250, -100], [250, -350], [350, -350], [350, 0]), pos = (200, 450), color = [0, 255, 0], width = 0)
ball = Circle(radius = ballSize, color = [0, 0, 0], pos = (500, 100))
ground_wall1 = Polygon(offsets = ([0, 0], [0, -100], [250, -100], [250, -350], [350, -350], [350, 0]), pos = (200, 450), color = [150, 150, 150], width = 5)
bottom_wall1 = Polygon(offsets = ([0, 0], [350, 0], [350, 5], [0, 5]), pos = (200, 450), color = [150, 150, 150], width = 5)
right_wall1 = Polygon(offsets = ([350, -350], [355, -350], [355, 0], [350, 0]), pos = (200, 450), color = [150, 150, 150], width = 5)
upper_top_wall1 = Polygon(offsets = ([250, -355], [350, -355], [350, -350], [250, -350]), pos = (200, 450), color = [150, 150, 150], width = 5)
left_wall_middle1 = Polygon(offsets = ([250, -100], [250, -350], [255, -350], [255, -100]), pos = (200, 450), color = [150, 150, 150], width = 5)
lower_top_wall1 = Polygon(offsets = ([0, -100], [250, -100], [250, -95], [0, -95]), pos = (200, 450), color = [150, 150, 150], width = 5)
left_wall1 = Polygon(offsets = ([0, 0], [0, -100], [5, -100], [5, 0]), pos = (200, 450), color = [150, 150, 150], width = 5)
hole1 = Circle(radius = 10, color = [0, 0, 0], pos = (500, 125))
bumper1 = Polygon(offsets = ([0, 0], [60, -60], [65, -55], [5, 5]), pos = (490, 450), color = [150, 150, 150], width = 0)

#stage 2 objects
ground2 = Polygon(offsets = ([0, 0], [0, -200], [-120, -200], [-120, -320], [0, -320], [0, -520], [200, -520], [200, 0]), pos = (350, 575), color = [0, 255, 0], width = 0)
ground_wall2 = Polygon(offsets = ([0, 0], [0, -200], [-120, -200], [-120, -320], [0, -320], [0, -520], [200, -520], [200, 0]), pos = (350, 575), color = [150, 150, 150], width = 5)
bottom_wall2 = Polygon(offsets = ([0, 0], [200, 0], [200, 5], [0, 5]), pos = (350, 575), color = [150, 150, 150], width = 5)
right_wall2 = Polygon(offsets = ([205, -520], [205, 0], [200, 0], [200, -520]), pos = (350, 575), color = [150, 150, 150], width = 5)
top_wall2 = Polygon(offsets = ([0, -520], [0, -525], [200, -525], [200, -520]), pos = (350, 575), color = [150, 150, 150], width = 5)
lower_left_wall2 = Polygon(offsets = ([0, 0], [0, -200], [5, -200], [5, 0]), pos = (350, 575), color = [150, 150, 150], width = 5)
upper_left_wall2 = Polygon(offsets = ([0, -320], [0, -520], [5, -520], [5, -320]), pos = (350, 575), color = [150, 150, 150], width = 5)
top_left_wall2 = Polygon(offsets = ([-120, -320], [0, -320], [0, -315], [-120, -315]), pos = (350, 575), color = [150, 150, 150], width = 5)
bottom_left_wall2 = Polygon(offsets = ([0, -195], [-120, -195], [-120, -200], [0, -200],), pos = (350, 575), color = [150, 150, 150], width = 5)
left_wall2 = Polygon(offsets = ([-125, -200], [-125, -320], [-120, -320], [-120, -200]), pos = (350, 575), color = [150, 150, 150], width = 5)
hole2 = Circle(radius = 10, color = [0, 0, 0], pos = (525, 80))
ball2 = Circle(radius = ballSize, color = [254, 254, 254], pos = (375, 550))
bumper2 = Polygon(offsets = ([175, 0], [175, 20], [0, 20], [0, 0]), pos = (363, 125), color = [150, 150, 150], width = 0)

#stage 3 objects
ground3 = Polygon(offsets = ([0, 0], [0, -300], [240, -300], [240, -550], [540, -550], [540, -240], [300, -240], [300, 0]), pos = (100, 575), color = [0, 255, 0], width = 0)
ground_wall3 = Polygon(offsets = ([0, 0], [0, -300], [240, -300], [240, -550], [540, -550], [540, -240], [300, -240], [300, 0]), pos = (100, 575), color = [150, 150, 150], width = 5)
bottom_wall3 = Polygon(offsets = ([0, -5], [300, -5], [300, 0], [0, 0]), pos = (100, 575), color = [150, 150, 150], width = 5)
lower_middle_wall3 = Polygon(offsets = ([305, -240], [305, 0], [300, 0], [300, -240]), pos = (100, 575), color = [150, 150, 150], width = 5)
upper_bottom_wall3 = Polygon(offsets = ([540, -235], [300, -235], [300, -240], [540, -240]), pos = (100, 575), color = [150, 150, 150], width = 5)
right_wall3 = Polygon(offsets = ([540, -550], [540, -240], [535, -240], [535, -550]), pos = (100, 575), color = [150, 150, 150], width = 5)
top_wall3 = Polygon(offsets = ([240, -555], [540, -555], [540, -550], [240, -550]), pos = (100, 575), color = [150, 150, 150], width = 5)
upper_middle_wall3 = Polygon(offsets = ([240, -300], [240, -550], [245, -550], [245, -300]), pos = (100, 575), color = [150, 150, 150], width = 5)
lower_top_wall3 = Polygon(offsets = ([0, -305], [240, -305], [240, -300], [0, -300]), pos = (100, 575), color = [150, 150, 150], width = 5)
left_wall3 = Polygon(offsets = ([0, 0], [0, -300], [5, -300], [5, 0]), pos = (100, 575), color = [150, 150, 150], width = 5)
hole3 = Circle(radius = 10, color = [0, 0, 0], pos = (600, 60))
rotator1_part1 = UniformPolygon(offsets = ([0, 0], [0, -20], [320, -20], [320, 0]), color = [150, 150, 150], width = 0, avel = -1)
rotator1_part2 = UniformPolygon(offsets = ([0, 0], [0, -20], [320, -20], [320, 0]), color = [150, 150, 150], width = 0, angle = math.radians(90), avel = -1)
rotator1_part1.mass = math.inf
rotator1_part1.momi = math.inf
rotator1_part1.pos = (485, 420)
rotator1_part2.mass = math.inf
rotator1_part2.momi = math.inf
rotator1_part2.pos = (485, 420)
rotator2_part1 = UniformPolygon(offsets = ([0, 0], [0, -20], [320, -20], [320, 0]), color = [150, 150, 150], width = 0, angle = math.radians(-45), avel = 1)
rotator2_part2 = UniformPolygon(offsets = ([0, 0], [0, -20], [320, -20], [320, 0]), color = [150, 150, 150], width = 0, angle = math.radians(45), avel = 1)
rotator2_part1.mass = math.inf
rotator2_part1.momi = math.inf
rotator2_part1.pos = (255, 190)
rotator2_part2.mass = math.inf
rotator2_part2.momi = math.inf
rotator2_part2.pos = (255, 190)


#first stage pos = (255, 400), second stage pos = (375, 550), third stage pos = (125, 550)
ball = UniformCircle(density = 0.5, radius = 5, color = [255, 255, 255], pos = (255, 400))


# Append objects into their proper lists

# Golf ball
balls.append(ball)

# Rotators for Level 3
rotators.append(rotator1_part1)
rotators.append(rotator1_part2)
rotators.append(rotator2_part1)
rotators.append(rotator2_part2)

# Holes
holes.append(hole1)
holes.append(hole2)
holes.append(hole3)

# Stage 1 Objects
objects1.append(bottom_wall1)
objects1.append(right_wall1)
objects1.append(upper_top_wall1)
objects1.append(left_wall_middle1)
objects1.append(lower_top_wall1)
objects1.append(left_wall1)
objects1.append(bumper1)

# Stage 2 Objects
objects2.append(bottom_wall2)
objects2.append(top_wall2)
objects2.append(right_wall2)
objects2.append(lower_left_wall2)
objects2.append(upper_left_wall2)
objects2.append(left_wall2)
objects2.append(top_left_wall2)
objects2.append(bottom_left_wall2)

# Stage 3 Objects
objects3.append(bottom_wall3)
objects3.append(lower_middle_wall3)
objects3.append(upper_bottom_wall3)
objects3.append(right_wall3)
objects3.append(top_wall3)
objects3.append(upper_middle_wall3)
objects3.append(lower_top_wall3)
objects3.append(left_wall3)

# Obstacle in Level 2
obstacles.append(bumper2)

# Friction Variable
friction = Friction(objects_list = balls, fric_coe = .3, gravity = 980)

# Fonts
font = pygame.font.SysFont('calbri', 30, bold = False, italic = False)
win_font = pygame.font.SysFont('calbri', 60, bold = False, italic = False)

stage = AIMING_BALL

# game loop
running = True
while running:
    # EVENT loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if(event.type == MOUSEMOTION):
            mousePosition = event.pos
        if (event.type == pygame.USEREVENT):
            pygame.time.set_timer(pygame.USEREVENT, 0)
            state += 1
            stage = AIMING_BALL
            strokes = 0
            if state == 2:
                ball.pos = Vector2(375, 550)
            if state == 3:
                ball.pos = Vector2(125, 550)
            if state == 4:
                running = False
            
    # Collisions

    # Level 1
    if state == 1:
        for o1 in objects1:
            for b in balls:
                a = generate_contact(o1, b)
                resolve_contact(a, restitution = 0.4)

    # Level 2
    if state == 2:
        for o2 in objects2:
            for b in balls:
                c = generate_contact(o2, b)
                resolve_contact(c, restitution = 0.4)
        for ob in obstacles:
            for b in balls:
                h = generate_contact(ob, b)
                resolve_contact(h, restitution = 0.4)
                
    # Level 3
    if state == 3:
        for o3 in objects3:
            for b in balls:
                d = generate_contact(o3, b)
                resolve_contact(d, restitution = 0.4)
        for r in rotators:
            for b in balls:
                z = generate_contact(r, b)
                resolve_contact(z, restitution = 0.4)

    # Update ball
    for b in balls:
        b.clear_force()
    friction.apply()
    # update objects
    for ob in obstacles:
        ob.update(dt)
    for b in balls:
        b.update(dt)
    for r in rotators:
        r.update(dt)
    
    seconds += 1

    # DRAW section
    # clear the screen
    window.fill([26, 119, 0])

    # Level 1
    if state == 1:
      ground1.draw(window)
      hole1.draw(window)
      for o1 in objects1:
          o1.draw(window)

    # Level 2
    if state == 2:
        ground2.draw(window)
        hole2.draw(window)
        for o2 in objects2:
            o2.draw(window)
        for ob in obstacles:
            ob.draw(window)
        bumper2.acc.y = -k * (bumper2.pos.y - bumper_center)

    # Level 3
    if state == 3:
        ground3.draw(window)
        hole3.draw(window)
        for o3 in objects3:
            o3.draw(window)
        for r in rotators:
            r.draw(window)
    
    # Draw ball
    for b in balls:
        b.draw(window)

    # Stroke Text
    stroke_label = font.render("Strokes: ", 1, [0, 0, 0])
    window.blit(stroke_label, [10, 10])
    stroke_count = font.render(f"{strokes}", 1, [0, 0, 0])
    window.blit(stroke_count, [100, 10])

    # Click and Hold Left Mouse Button to charge your shot
    if(event.type == MOUSEBUTTONDOWN and event.button == BUTTON_LEFT):
        # Placing a new ball in the gray area
        if(stage == AIMING_BALL):
            hold_time = 0
            stage = CHARGING_BALL

    # Once the Left Mouse Button is Released
    if(event.type == MOUSEBUTTONUP and event.button == BUTTON_LEFT and stage == CHARGING_BALL):
        ball.vel = ((mousePosition - ball.pos)/mag(mousePosition - ball.pos)) * clamp(math.sqrt(hold_time) * 25,0,1000)
        stage = BALL_ROLLING

    # Aiming Stage
    if(stage == AIMING_BALL):
        if ball.vel.magnitude() > 0.3:
            stage == BALL_ROLLING
        if(mag(ball.pos - mousePosition) >200): # only draw the line up to a certain point
            pygame.draw.line(window, [0,0,0],ball.pos, ball.pos + 200 * (mousePosition-ball.pos)/(mag(ball.pos - mousePosition)), width=int(ball.radius/2))
        else:
            pygame.draw.line(window, [0,0,0],ball.pos, mousePosition, width=int(ball.radius/2))

    # Charging Stage
    if(stage == CHARGING_BALL): #show how much the ball has been charged on the aiming line
        if ball.vel.magnitude() > 0.3:
            stage == BALL_ROLLING
        pygame.draw.line(window, [0,0,0],ball.pos, ball.pos + 200 * ((clamp(math.sqrt(hold_time) * 25,0,1000))/1000) 
        * (mousePosition-ball.pos)/(mag(ball.pos - mousePosition)), width=int(ball.radius/2))
    
    # Ball Rolling Stage
    if(event.type == MOUSEBUTTONUP and event.button == BUTTON_LEFT and stage == CHARGING_BALL):
        ball.vel = ((mousePosition - ball.pos)/mag(mousePosition - ball.pos)) * clamp(math.sqrt(hold_time) * 25,0,1000)
        stage = BALL_ROLLING

    # While the Ball is Rolling
    if(stage == BALL_ROLLING):
        ## Check for balls rolling slow enough to stop
        ballStopped = True
        for b in balls:
            # Hole Contact Generators
            hole1_in = generate_contact(b, hole1)
            hole2_in = generate_contact(b, hole2)
            hole3_in = generate_contact(b, hole3)
            if mag(b.vel) > (friction.fric_coe * friction.gravity * dt):
                ballStopped = False
            else:
                b.vel = Vector2(0, 0)

            # Overlap Hole 1
            if state == 1:
                if hole1_in.overlap() > 1.3 * ball.radius:
                    ball.vel *= 0.9
                if hole1_in.overlap() > ball.radius:
                    if ball.vel.magnitude() < 0.3:
                        stage = WIN
                        pygame.time.set_timer(pygame.USEREVENT, 3000)

            # Overlap Hole 2
            if state == 2:
                if hole2_in.overlap() > 1.3 * ball.radius:
                    ball.vel *= 0.9
                if hole2_in.overlap() > ball.radius:
                    if ball.vel.magnitude() < 0.3:
                        stage = WIN
                        pygame.time.set_timer(pygame.USEREVENT, 3000)

            # Overlap Hole 3
            if state == 3:
                if hole3_in.overlap() > 1.3 * ball.radius:
                    ball.vel *= 0.9
                if hole3_in.overlap() > ball.radius:
                    if ball.vel.magnitude() < 0.3:
                        stage = WIN
                        pygame.time.set_timer(pygame.USEREVENT, 3000)  

        # When the Ball Stops
        if ballStopped:
            if stage != WIN:
                stage = BALL_STOPPED
            strokes += 1
    
    # When the level is complete
    if(stage == WIN):
        score = strokes - par[state]
        if strokes == 1:
            stroke_label = win_font.render("Hole in One!", 1, [0, 0, 0])
            window.blit(stroke_label, [300, 300])
        elif score == -3:
            stroke_label = win_font.render("ALBATROSS!!", 1, [0, 0, 0])
            window.blit(stroke_label, [300, 300])
        elif score == -2:
            stroke_label = win_font.render("Eagle!", 1, [0, 0, 0])
            window.blit(stroke_label, [325, 300])
        elif score == -1:
            stroke_label = win_font.render("Birdie!", 1, [0, 0, 0])
            window.blit(stroke_label, [325, 300])
        elif score == 0:
            stroke_label = win_font.render("Par", 1, [0, 0, 0])
            window.blit(stroke_label, [350, 300])
        elif score == 1:
            stroke_label = win_font.render("Bogey", 1, [0, 0, 0])
            window.blit(stroke_label, [325, 300])
        elif score == 2:
            stroke_label = win_font.render("Double Bogey", 1, [0, 0, 0])
            window.blit(stroke_label, [300, 300])
        elif score == 3:
            stroke_label = win_font.render("Triple Bogey", 1, [0, 0, 0])
            window.blit(stroke_label, [300, 300])
        elif strokes >= 6:
            stroke_label = win_font.render("Stroke Out", 1, [0, 0, 0])
            window.blit(stroke_label, [300, 300])

    # Resets the Ball to the Aiming Stage
    if stage == BALL_STOPPED:
        stage = AIMING_BALL

    # update the display
    pygame.display.update()

    # delay for correct timing
    time = clock.tick(fps)
    if stage == CHARGING_BALL:
        hold_time += time