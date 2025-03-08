
import playground
import random

from typing import List, Tuple, NewType

Pos = NewType('Pos', Tuple[int, int])


class Atom:

    def __init__(self, pos: Pos, vel: Pos, rad: int, col: str):
        """
        Initializer of Atom class

        :param x: x-coordinate
        :param y: y-coordinate
        :param rad: radius
        :param color: color of displayed circle
        """
        self.pos_x: int = pos[0]
        self.pos_y: int = pos[1]
        self.vel_x = vel[0]
        self.vel_y = vel[1]
        self.rad = rad
        self.col = col

    def to_tuple(self) -> Tuple[int, int, int, str]:
        """
        Returns tuple representing an atom.

        Example: pos = (10, 12,), rad = 15, color = 'green' -> (10, 12, 15, 'green')
        """
        return self.pos_x, self.pos_y, self.rad, self.col


    def apply_speed(self, size_x: int, size_y: int):
        """
        Applies velocity `vel` to atom's position `pos`.

        :param size_x: width of the world space
        :param size_y: height of the world space
        """
        # new positions
        new_x = self.pos_x + self.vel_x
        new_y = self.pos_y + self.vel_y

        # edges
        left = self.rad
        right = size_x - self.rad
        top = self.rad
        bottom = size_y - self.rad

        # bounce X
        if (new_x >= right) or (new_x <= left):
            if new_x >= right:
                over = new_x - right
                new_x = right - over
            else:
                over = left - new_x
                new_x = left + over
            self.vel_x *= -1
        # bounce Y
        if (new_y >= bottom) or (new_y <= top):
            if new_y >= bottom:
                over = new_y - bottom
                new_y = bottom - over
            else:
                over = top - new_y
                new_y = top + over
            self.vel_y *= -1

        self.pos_x = new_x
        self.pos_y = new_y


class FallDownAtom(Atom):
    """
    Class to represent atoms that are pulled by gravity.
     
    Set gravity factor to ~3.

    Each time an atom hits the 'ground' damp the velocity's y-coordinate by ~0.7.
    """
    def __init__(self, pos: Pos, vel: Pos, rad: int, col: str):
        self.g: float = 3
        self.damping: float = 0.7
        self.grounded = False
        super().__init__(pos, vel, rad, col)

    def apply_speed(self, size_x: int, size_y: int):
        # apply gravity
        self.vel_y += self.g

        # new positions
        new_x = self.pos_x + self.vel_x
        new_y = self.pos_y + self.vel_y

        # edges
        left = self.rad
        right = size_x - self.rad
        top = self.rad
        bottom = size_y - self.rad

        # bounce X
        if (new_x >= right) or (new_x <= left):
            if new_x >= right:
                over = new_x - right
                new_x = right - over
            else:
                over = left - new_x
                new_x = left + over
            self.vel_x *= -1
        self.pos_x = new_x

        if self.grounded:
            self.pos_y = bottom
            self.vel_x *= self.damping
            return
        # bounce Y top
        if new_y <= top:
            over = top - new_y
            new_y = top + over
            self.vel_y *= -1
        # bounce Y bottom
        if new_y >= bottom:
            over = new_y - bottom
            new_y = bottom - over
            self.vel_y *= -self.damping
            self.vel_x *= self.damping
            if -self.vel_y < self.g * 2:
                self.grounded = True
        self.pos_y = new_y



class ExampleWorld:

    def __init__(self, size_x: int, size_y: int, no_atoms: int, no_falldown_atoms: int):
        """
        ExampleWorld initializer.

        :param size_x: width of the world space
        :param size_y: height of the world space
        :param no_atoms: number of 'bouncing' atoms
        :param no_falldown_atoms: number of atoms that respect gravity
        """

        self.width = size_x
        self.height = size_y
        self.atoms = self.generate_atoms(no_atoms, no_falldown_atoms)

    def generate_atoms(self, no_atoms: int, no_falldown_atoms) -> List[Atom|FallDownAtom]:
        """
        Generates `no_atoms` Atom instances using `random_atom` method.
        Returns list of such atom instances.

        :param no_atoms: number of Atom instances
        :param no_falldown_atoms: numbed of FallDownAtom instances
        """
        atoms = [self.random_atom() for _ in range(no_atoms)]
        falldown_atoms = [self.random_falldown_atom() for _ in range(no_falldown_atoms)]
        return atoms + falldown_atoms


    def random_atom_stats(self) -> Tuple[Pos, Pos, int]:
        radius = random.randint(10, 50)
        velocity_x = random.randint(-10, 10)
        velocity_y = random.randint(-10, 10)
        position_x = random.randint(radius, self.width - radius)
        position_y = random.randint(radius, self.height - radius)
        return Pos((position_x, position_y)), Pos((velocity_x, velocity_y)), radius
    def random_atom(self) -> Atom:
        """
        Generates one Atom instance at random position in world, with random velocity, random radius
        and 'green' color.
        """
        stat = self.random_atom_stats()
        return Atom(stat[0], stat[1], stat[2], 'green')

    def random_falldown_atom(self):
        """
        Generates one FalldownAtom instance at random position in world, with random velocity, random radius
        and 'yellow' color.
        """
        stat = self.random_atom_stats()
        return FallDownAtom(stat[0], stat[1], stat[2], 'yellow')

    def add_atom(self, pos_x, pos_y):
        """
        Adds a new Atom instance to the list of atoms. The atom is placed at the point of left mouse click.
        Velocity and radius is random.

        :param pos_x: x-coordinate of a new Atom
        :param pos_y: y-coordinate of a new Atom

        Method is called by playground on left mouse click.
        """
        stat = self.random_atom_stats()
        self.atoms.append(Atom(Pos((pos_x, pos_y)), stat[1], stat[2], 'blue'))

    def add_falldown_atom(self, pos_x, pos_y):
        """
        Adds a new FallDownAtom instance to the list of atoms. The atom is placed at the point of right mouse click.
        Velocity and radius is random.

        self.atoms.append(self.random_atom())
        Method is called by playground on right mouse click.

        :param pos_x: x-coordinate of a new FallDownAtom
        :param pos_y: y-coordinate of a new FallDownAtom
        """
        stat = self.random_atom_stats()
        self.atoms.append(FallDownAtom(Pos((pos_x, pos_y)), stat[1], stat[2], 'red'))

    def tick(self):
        """
        Method is called by playground. Sends a tuple of atoms to rendering engine.

        :return: tuple or generator of atom objects, each containing (x, y, radius, color) attributes of atom 
        """
        vals = []
        for atom in self.atoms:
            atom.apply_speed(self.width, self.height)
            vals.append(atom.to_tuple())

        return vals


if __name__ == '__main__':
    size_x, size_y = 700, 400
    no_atoms = 2
    no_falldown_atoms = 3

    world = ExampleWorld(size_x, size_y, no_atoms, no_falldown_atoms)

    playground.run((size_x, size_y), world)
