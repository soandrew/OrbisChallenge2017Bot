from PythonClientAPI.Game.Enums import Team
from PythonClientAPI.Game import PointUtils
from PythonClientAPI.Game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.Game.Enums import Direction, MoveType, MoveResult
from PythonClientAPI.Game.World import World

from functools import reduce

class PlayerAI:
    def __init__(self):
        """
        Any instantiation code goes here
        """
        self.turn_count = 0
        # self.nest_middle = Tile((0,0), Team.NEUTRAL, False)
        self.targets = {}
        self.uuid_to_target = {}
        # value = [position, bool reached]
        self.nest_points = set()
        self.nest_avoid_points = set()

    def do_move(self, world, friendly_units, enemy_units):
        """
        This method will get called every turn.

        :param world: World object reflecting current game state
        :param friendly_units: list of FriendlyUnit objects
        :param enemy_units: list of EnemyUnit objects
        """
        # Fly away to freedom, daring fireflies
        # Build thou nests
        # Grow, become stronger
        # Take over the world

        # Cache world information used for attacking
        enemy_nest_neighbour_positions = sum([list(world.get_neighbours(point).values())
                                     for point in world.get_enemy_nest_positions()],
                                   [])
        enemy_positions = {enemy.position for enemy in enemy_units}
        average_enemy_health = sum(enemy.health for enemy in enemy_units)/len(enemy_units)
        friendly_nest_positions = world.get_friendly_nest_positions()

        if self.turn_count == 0:
            first_nest = world.get_friendly_nest_positions()[0]
            self.nest_points.add(first_nest)
            self.nest_avoid_points |= get_nest_avoid_points_around(first_nest)
        i = 0
        for unit in friendly_units:
            # Schedule new nest to build every fourth turn
            if self.turn_count % 4 == 0 and ((i != 0 and i % 4 == 0) or self.turn_count == 0):
                nest = world.get_closest_neutral_tile_from(unit.position, self.nest_avoid_points)
                if nest:
                    self.targets = world.get_tiles_around(nest.position)

                    self.nest_points.add(nest.position)
                    self.nest_avoid_points |= get_nest_avoid_points_around(nest.position)
                else:
                    self.targets = None

            attack = True
            if self.targets:
                # Assign unit a target if not already have one
                if unit.uuid not in self.uuid_to_target:
                    idx = i % 4

                    if idx > (len(self.targets) - 1):
                        self.uuid_to_target[unit.uuid] = [(0, 0), True]
                    else:
                        direction = Direction.ORDERED_DIRECTIONS[idx]
                        while idx < 4 and (direction not in self.targets):
                            direction = Direction.ORDERED_DIRECTIONS[idx]
                            idx += 1

                        if idx == 4:
                            self.uuid_to_target[unit.uuid] = [(0,0), True]
                        else:
                            self.uuid_to_target[unit.uuid] = [self.targets[direction].position,
                                                              False]

                # If unit is already in target position
                if self.uuid_to_target[unit.uuid][0] == unit.position:
                    # change bool to True
                    self.uuid_to_target[unit.uuid][1] = True

                # If unit hasn't reached it's target yet
                if not self.uuid_to_target[unit.uuid][1]:
                    # Calculate path for unit to go to target
                    path = world.get_shortest_path(unit.position, self.uuid_to_target[unit.uuid][0], self.nest_points)
                    attack = False
            if attack:
                # Locate enemy units stronger than this unit
                strong_enemy_positions = {enemy.position for enemy in enemy_units
                                           if enemy.health > unit.health}

                # Look at neighbouring points to make best decision
                target = None
                for point in world.get_neighbours(unit.position).values():
                    if ((point in enemy_nest_neighbour_positions
                          or point in enemy_positions)
                          and point not in strong_enemy_positions):
                        target = point
                        break
                if not target:  # No good targets in neighbouring points
                    # Check if it's smarter to just rest
                    if unit.health <= average_enemy_health and unit.position not in friendly_nest_positions:
                        continue
                    # Best decision is to target closest capturable tile
                    target = world.get_closest_capturable_tile_from(unit.position, None).position

                # Get path
                path = world.get_shortest_path(unit.position, target, None)

            if path:
                world.move(unit, path[0])
            i += 1
        self.turn_count += 1

        # else:
        #     for unit in friendly_units:
        #         target = world.get_closest_capturable_tile_from(unit.position,
        #                                                         None)
        #         path = world.get_shortest_path(unit.position,
        #                                        target.position,
        #                                        None)
        #         if path:
        #             world.move(unit, path[0])


def get_nest_avoid_points_around(point):
    """
    Return the set of points around point, including point, to avoid scheduling a nest on.

    :param (int, int) point: a nest point
    :return: the set of points around point to avoid scheduling a nest on
    :rtype: set of points
    """
    x, y = point[0], point[1]
    return {(x, y - 2),
            (x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
            (x - 2, y), (x - 1, y), point, (x + 1, y), (x + 2, y),
            (x - 1, y + 1), (x, y + 1), (x + 1, y + 1),
            (x, y + 2)}
