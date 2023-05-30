import math
import pygame
import random
from pygame.math import Vector2 #2D vector

G = 6.67428e-11
MASS_AREA_RATIO = 2 * (10 ** 9)
dots = []
collide = False

class Particle:
    #constructor
    def __init__(self, mass = math.inf, pos = (0, 0), vel = (0,0), momi = math.inf, angle = 0, avel = 0):
        self.mass = mass    #sets mass property of Particle object
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.momi = momi
        self.angle = angle
        self.avel = avel
        self.clear_force()

    def clear_force(self):
        self.force = Vector2(0 ,0)
        self.torque = 0
        self.acc = Vector2(0, 0)

    def add_impulse(self, impulse, point = None):
        self.vel += impulse / self.mass
        if point is not None:
            s = point - self.pos
            self.avel += s.cross(impulse) / self.momi

    def add_force(self, force, point = None):
        self.force += force
        if point is not None:
            s = point - self.pos
            self.torque += s.cross(force)

    def set_pos(self, pos):
        self.pos = Vector2(pos)

    def delta_pos(self, delta):
        self.pos += Vector2(delta)

    def update(self, dt):
        self.vel += (self.force / self.mass + self.acc) * dt
        self.pos += self.vel * dt
        self.avel += (self.torque / self.momi) * dt
        self.angle += self.avel * dt

class Circle(Particle):
    def __init__(self, radius = 100, color = (255, 255, 255), width = 0, **kwargs):
        #**kwargs catches mass, pos, vel, and any other keyword arguments
        self.radius = radius
        self.color = color
        self.width = width
        super().__init__(**kwargs) #pass on all the other keyword arguments to the superclass constuctor (Particle)
        self.contact_type = "circle"

    def draw(self, window):
        pygame.draw.circle(window, self.color, self.pos, self.radius, self.width)
        #pygame.draw.line(window, [255, 255, 255], self.pos, self.pos + self.radius * Vector2(0, 1).rotate_rad(self.angle))

class Wall(Particle):
    # assume walls wont have velocity, pos is ignored
    def __init__(self, point1 = (0, 0), point2 = (0,0), color = (0, 0, 0), width = 1, **kwargs):
        self.point1 = Vector2(point1)
        self.point2 = Vector2(point2)
        # normal is the direction perpendicular to the wall
        self.normal = (self.point2 - self.point1).rotate(90).normalize()
        self.color = color
        self.vel = Vector2(0, 0)
        self.width = width
        super().__init__(**kwargs)
        self.contact_type = "wall"

    def draw(self, window):
        pygame.draw.line(window, self.color, self.point1, self.point2, self.width)

class Polygon(Particle):
    def __init__(self, offsets = [], color = [0, 0, 0], width = 1, **kwargs):
        #list comphrehension for loop in one line
        self.offsets = [Vector2(offsets[i]) for i in range(len(offsets))]
        self.local_normals = [(self.offsets[i] - self.offsets[i - 1]).rotate(-90).normalize() for i in range(len(offsets))]
        self.color = color
        self.width = width
        super().__init__(**kwargs)
        self.contact_type = "polygon"
        self.update_polygon()

    def update(self, dt):
        super().update(dt)
        self.update_polygon()

    def set_pos(self, pos):
        super().set_pos(pos)
        self.update_polygon()

    def delta_pos(self, delta):
        super().delta_pos(delta)
        self.update_polygon()

    def update_polygon(self):
        sin = math.sin(self.angle)
        cos = math.cos(self.angle)
        self.points = [Vector2(cos * self.offsets[i].x - sin * self.offsets[i].y, sin * self.offsets[i].x + cos * self.offsets[i].y) + self.pos for i in range(len(self.offsets))]
        self.normals = [Vector2(cos * self.local_normals[i].x - sin * self.local_normals[i].y, sin * self.local_normals[i].x + cos * self.local_normals[i].y).normalize() for i in range(len(self.local_normals))]

    def draw(self, window):
        pygame.draw.polygon(window, self.color, self.points, self.width)
        #if True:
            #[pygame.draw.line(window, self.color, self.points[i], self.points[i] + 50 * self.normals[i]) for i in range(len(self.offsets))]

class UniformCircle(Circle):
    def __init__(self, density = 1, radius = 10, **kwargs):
        # calculate mass and moment of inertia
        mass = density * (math.pi * radius ** 2)
        momi = 0.5 * mass * (radius ** 2)
        super().__init__(mass=mass, momi=momi, radius = radius, **kwargs)

class UniformPolygon(Polygon):
    def __init__(self, density=1, offsets=[], pos = (0,0), angle=0, shift=True, type = "", **kwargs):
        # Calculate mass, moment of inertia, and center of mass
        total_mass = 0
        total_momi = 0
        com_numerator = Vector2(0, 0)

        self.density = density
        self.type = type

        # Make a local copy of offsets
        local_offsets = []
        for o in offsets:
            local_offsets.append(Vector2(o))

        # by looping over all "triangles" of the polygon
        for i in range(len(local_offsets)):
            # triangle mass
            s0 = Vector2(local_offsets[i-1])
            s1 = Vector2(local_offsets[i])
            mass = 0.5 * density * s0.cross(s1)
            # triangle moment of inertia
            momi = mass / 6 * (s0.dot(s0) + s1.dot(s1) + s0.dot(s1))
            # triangle center of mass
            com = (s0 + s1) / 3

            # add to total mass
            total_mass += mass
            # add to total moment of inertia
            total_momi += momi
            # add to center of mass numerator
            com_numerator += mass * com
            pass
        
        # calculate total center of mass by dividing numerator by denominator (total mass)
        com = com_numerator / total_mass

        if shift:
            # Shift offsets by com
            for i in range(len(local_offsets)):
                local_offsets[i] -= com
            # shift pos
            pos += com.rotate(angle)
            # Use parallel axis theorem to correct the moment of inertia
            total_momi -= total_mass * com.magnitude() ** 2

        # Then call super().__init__() with those correct values
        super().__init__(mass=total_mass, momi=total_momi, offsets=local_offsets, pos=pos, angle=angle, **kwargs) 


offsets = [Vector2(0, 0), Vector2(0, 100), Vector2(100, 100), Vector2(100, 0)]