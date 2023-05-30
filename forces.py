import pygame
from pygame.math import Vector2
import itertools
import math

from physics_objects import Circle

class SingleForce:
    def __init__(self, objects_list = []):
        self.objects_list = objects_list

    def apply(self):
        for obj in self.objects_list:
            force = self.force(obj)
            obj.add_force(force)

    def force(self, obj):
        return Vector2(0, 0)


class PairForce:
    def __init__(self, objects_list = []):
        self.objects_list = objects_list

    def apply(self):
        #loops that set a and b
        #double for loop (taking care to do each pair once)
        for a, b in itertools.combinations(self.objects_list, 2):
            force = self.force(a, b)
            a.add_force(force)
            b.add_force(-force)

    def force(self, a, b):
        return Vector2(0, 0)


class BondForce:
    def __init__(self, pairs_list = []):
        self.pairs_list = pairs_list

    def apply(self):
        for a, b in self.pairs_list:
            force = self.force(a, b)
            if a.locked == False:   
                a.add_force(force)
            if b.locked == False:
                b.add_force(-force)
 
    def force(self, a, b):
        return Vector2(0, 0)

# Add Gravity, SpringForce, SpringRepulsion, AirDrag
class Gravity(SingleForce):
    def __init__(self, acc = (0,0), **kwargs):
        self.acc = Vector2(acc)
        super().__init__(**kwargs)
        
    def force(self, obj):
        if obj.mass == math.inf:
            return Vector2(0,0)
        return obj.mass * self.acc

class Spring(BondForce):
    def __init__(self, stiffness = 0, natural_length = 0, damping = 0, **kwargs):
        self.stiffness = stiffness
        self.natural_length = natural_length
        self.damping = damping
        super().__init__(**kwargs)

    def force(self, a, b):
        return ((-self.stiffness) * ((a.pos - b.pos).magnitude() - self.natural_length) - ((self.damping) * (a.vel - b.vel).dot((a.pos - b.pos).normalize()))) * (a.pos - b.pos).normalize()

class Repulsion(PairForce):
    def __init__(self, stiffness = 0, **kwargs):
        self.stiffness = stiffness
        super().__init__(**kwargs)

    def force(self, a, b):
        repForce = 0
        repForce = (a.radius + b.radius - (a.pos - b.pos).magnitude())
        if repForce > 0:
            return self.stiffness * repForce * (a.pos - b.pos).normalize()
        else:
            return Vector2(0, 0)

class Drag(SingleForce):
    def __init__(self, density = 0, dragCoe = 0, wind = Vector2(0, 0), **kwargs):
        self.density = density
        self.dragCoe = dragCoe
        self.wind = wind
        super().__init__(**kwargs)
    
    def force(self, obj):
        vel = obj.vel - self.wind
        return -(1/2) * self.dragCoe * self.density * (math.pi * (obj.radius ** 2)) * vel.magnitude() * vel

class Friction(SingleForce):
    def __init__(self, fric_coe = 0, gravity = 0, **kwargs):
        self.fric_coe = fric_coe
        self.gravity = gravity
        super().__init__(**kwargs)

    def force(self, obj):
        mass = obj.mass
        vel = obj.vel
        if vel != Vector2(0, 0):
            return -self.fric_coe * mass * self.gravity * vel.normalize()
        else:
            return Vector2(0, 0)