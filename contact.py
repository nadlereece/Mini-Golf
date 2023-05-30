from pygame.constants import SCRAP_BMP
from pygame.math import Vector2
import math

# Returns a new contact object of the correct type
# This function has been done for you.
def generate_contact(a, b):
    # Check if a's type comes later than b's alphabetically.
    # We will label our collision types in alphabetical order, 
    # so the lower one needs to go first.
    if b.contact_type < a.contact_type:
        a, b = b, a
    # This calls the class of the appropriate name based on the two contact types.
    return globals()[f"Contact_{a.contact_type}_{b.contact_type}"](a, b)
    
# Resolves a contact (by the default method) and returns True if it needed to be resolved
def resolve_contact(contact, restitution=0):
    # Fill in stuff here
    overlap = contact.overlap()
    # check for overlap
    if overlap > 0:
        # resolve overlap
        a = contact.a
        b = contact.b
        normal = contact.normal()
        minv = 1/a.mass + 1/b.mass
        shift = overlap / minv*normal
        a.delta_pos(shift/a.mass)
        b.delta_pos(-shift/b.mass)
        M = 1 / minv

    # check for velocities coming toward each other
        point = contact.point()
        sa = point - a.pos
        sb = point - b.pos
        a_distance = Vector2(contact.point() - a.pos)
        a_tangent = Vector2(-a_distance.y, a_distance.x)
        a_velocity = a.vel + a.avel * a_tangent
        b_distance = Vector2(contact.point() - b.pos)
        b_tangent = Vector2(-b_distance.y, b_distance.x)
        b_velocity = b.vel + b.avel * b_tangent
        sap = a_tangent.dot(normal)
        sbp = b_tangent.dot(normal)
        relative_velocity = a_velocity - b_velocity
        vn = relative_velocity.dot(normal)
        tangent = normal.rotate(90)
        inerta_a = (sap ** 2) / a.momi
        inerta_b = (sbp ** 2) / b.momi

        if vn < 0:
            J = (-(1 + restitution) * vn) / (minv + inerta_a + inerta_b)
            impulse = (J * normal)
            a.add_impulse(impulse, point)
            b.add_impulse(-impulse, point)
        return True

    return False

def resolve_contact_friction(contact, restitution=0, friction = 0, jump = 0):
    # Fill in stuff here
    overlap = contact.overlap()
    # check for overlap
    if overlap > 0:
        # resolve overlap
        a = contact.a
        b = contact.b
        normal = contact.normal()
        minv = 1/a.mass + 1/b.mass
        shift = overlap / minv*normal
        a.delta_pos(shift/a.mass)
        b.delta_pos(-shift/b.mass)
        M = 1 / minv

    # check for velocities coming toward each other
        a_distance = Vector2(contact.point() - a.pos)
        a_tangent = Vector2(-a_distance.y, a_distance.x)
        a_velocity = a.vel + a.avel * a_tangent
        b_distance = Vector2(contact.point() - b.pos)
        b_tangent = Vector2(-b_distance.y, b_distance.x)
        b_velocity = b.vel + b.avel * b_tangent
        relative_velocity = a_velocity - b_velocity
        vn = relative_velocity.dot(normal)
        vt = relative_velocity.dot(normal.rotate(90))
        tangent = normal.rotate(90)
        if vt < 0:
            vt *= -1
            tangent *= -1
    
        jt = -1*M * vt
        if vn < 0:
            J = -(1 + restitution) * vn / minv
            J += jump / minv
            if jump == 0:
                if abs(jt) <= friction * J:
                    slide = -abs(vt / vn) * overlap
                    a.pos += (((1/a.mass)*M) * slide * tangent)
                    b.pos += (-((1/b.mass)*M) * slide * tangent)
                if abs(jt) > friction * J:
                    jt = -friction * J
                else:
                    jt = 0
            else:
                jt *= 0.01
            impulse = (J * normal) + (jt * tangent)
            a.add_impulse(impulse)
            b.add_impulse(-impulse)
        return True

    return False

# Generic contact class, to be overridden by specific scenarios
class Contact():
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.renew() # call at the end of constructor
 
    def renew(self): # virtual function
        pass

    def overlap(self):  # virtual function
        return 0

    def normal(self):  # virtual function
        return Vector2(0, 0)


# Contact class for two circles
class Contact_circle_circle(Contact):
    def __init__(self, a, b):
        super().__init__(a, b)

    def point(self):
        return self.a.pos - self.normal() * self.a.radius

    def overlap(self):
        r = self.a.pos - self.b.pos
        return self.a.radius + self.b.radius - r.magnitude()  # Fill in the appropriate expression

    def normal(self):
        return (self.a.pos - self.b.pos).normalize()  # Fill in the appropriate expression

class Contact_circle_polygon(Contact):
    def __init__(self, a, b):
        self.circle = a
        self.polygon = b
        super().__init__(a, b)

    def point(self):
        return self.a.pos - self.normal() * self.a.radius

    def renew(self):

        # identify which case is occuring and save the index of the vertex or normal involved

        # loop over all "sides"
        min_overlap = math.inf
        for i, (point, normal) in enumerate(zip(self.polygon.points, self.polygon.normals)):
            # overlap as if between a circle and a wall 
            overlap = self.circle.radius - (self.circle.pos - point).dot(normal)
            if overlap < min_overlap:
                min_overlap = overlap
                self.index = i
        self.circle_overlaps_side = True
        # default case is that the circle is overlapping the side

        # now to check and see if we are actually overlapping a vertex
        # first make sure the circle is not inside the polygon
        if min_overlap < self.circle.radius:
            r1 = self.polygon.points[self.index]
            r0 = self.polygon.points[self.index - 1]
            tangent = r1 - r0
            if tangent.dot(self.circle.pos - r1) > 0:
                self.circle_overlaps_side = False
                # self.index is already set to be the index of this point
            elif tangent.dot(self.circle.pos - r0) < 0:
                self.circle_overlaps_side = False
                self.index = self.index - 1 # set self.index to match the index of this point

    def overlap(self):
        if self.circle_overlaps_side:
            # compute the overlap between circle and wall
            return self.circle.radius - (self.circle.pos - self.polygon.points[self.index]).dot(self.polygon.normals[self.index])
        else:
            # compute the overlap between 2 circles, the 2nd is the point (radius = 0)
            return self.a.radius - (self.a.pos - self.b.points[self.index]).magnitude()

    def normal(self):
        if self.circle_overlaps_side:
            # return the normal of the correct index
            return self.polygon.normals[self.index]
        else:
            return (self.circle.pos - self.polygon.points[self.index]).normalize()

class Contact_circle_wall(Contact):
    def __init__(self, a, b):
        super().__init__(a, b)
        self.circle = a
        self.wall = b

    def point(self):
        return self.a.pos - self.normal() * self.a.radius

    def overlap(self):  # virtual function
        return self.circle.radius - (self.circle.pos - self.wall.point1).dot(self.wall.normal)

    def normal(self):  # virtual function
        return self.wall.normal

class Contact_wall_wall(Contact):
    def __init__(self, a, b):
        super().__init__(a, b)

class Contact_polygon_polygon(Contact):
    def __init__(self, a, b):
        self.sideIndex = 0
        self.pointIndex = 0
        self.isSideA = False
        super().__init__(a, b)
    
    def renew(self): #identify which case is occuring and save the index of the vertex or normal involved
        minOverlap = math.inf
        maxOverlap = -math.inf
        maxPoint = None
        #loop over all sides of a in contact with b
        for i, (wallPoint, wallNormal) in enumerate(zip(self.a.points, self.a.normals)):
            maxOverlap = -math.inf
            for (jpoint, otherPoint) in enumerate(self.b.points):
                overlap = -(otherPoint - wallPoint).dot(wallNormal)
                #find max overlap
                if overlap > maxOverlap:
                    maxOverlap = overlap                    
                    maxPoint = jpoint
            if maxOverlap < minOverlap:
                minOverlap = maxOverlap
                self.sideIndex = i
                self.pointIndex = maxPoint
                self.isSideA = True
        #loop over all sides of b in contact with a
        for i, (wallPoint, wallNormal) in enumerate(zip(self.b.points, self.b.normals)):
            maxOverlap = -math.inf
            for (jpoint, otherPoint) in enumerate(self.a.points):
                overlap = -(otherPoint - wallPoint).dot(wallNormal)
                #find max overlap
                if overlap > maxOverlap:
                    maxOverlap = overlap        
                    maxPoint = jpoint
            if maxOverlap < minOverlap:
                minOverlap = maxOverlap
                self.sideIndex = i
                self.pointIndex = maxPoint
                self.isSideA = False
    
    def overlap(self): #HELP
        if self.isSideA:
            return -(self.b.points[self.pointIndex] - self.a.points[self.sideIndex]).dot(self.a.normals[self.sideIndex])
        else:
            return -(self.a.points[self.pointIndex] - self.b.points[self.sideIndex]).dot(self.b.normals[self.sideIndex])

    def point(self):  # contact point
        if self.isSideA:
            return self.b.points[self.pointIndex]
        else:
            return self.a.points[self.pointIndex]
        
    def normal(self):
        if self.isSideA:
            return -self.a.normals[self.sideIndex]
        else:
            return self.b.normals[self.sideIndex]

class Contact_polygon_wall(Contact):
    def __init__(self, a, b):
        self.polygon = a
        self.wall = b
        super().__init__(a, b)

    def renew(self):
        max_overlap = -math.inf
        for i, point in enumerate(self.a.points):
            # overlap as if between a circle and a wall 
            overlap = 0 - (point - self.wall.point1).dot(self.wall.normal)
            if overlap > max_overlap:
                max_overlap = overlap
                self.index = i
        
    def point(self):
        return self.polygon.points[self.index]

    def normal(self):  # virtual function
        return self.wall.normal

    def overlap(self):  # virtual function
        return 0 - (self.polygon.points[self.index] - self.wall.point1).dot(self.wall.normal)

    
