from PythonClientAPI.Game.Enums import Team
from PythonClientAPI.Game import PointUtils
from PythonClientAPI.Game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.Game.Enums import Direction, MoveType, MoveResult
from PythonClientAPI.Game.World import World


class PlayerAI:
    def __init__(self):
        """
        Any instantiation code goes here
        """
        self.turn_count = 0
        # self.nest_middle = Tile((0,0), Team.NEUTRAL, False)
        self.targets = {}
        self.uuid_to_target = {}
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

        i = 0
        for unit in friendly_units:
            # Schedule new nest to build every fourth turn
            if self.turn_count % 4 == 0:
                nest = world.get_closest_neutral_tile_from(unit.position, self.nest_avoid_points)
                self.targets = world.get_tiles_around(nest.position)

                self.nest_points.add(nest.position)
                self.nest_avoid_points |= get_nest_avoid_points_around(nest.position)
            # Assign unit a target if not already have one
            if unit.uuid not in self.uuid_to_target:
                self.uuid_to_target[unit.uuid] = self.targets[Direction.ORDERED_DIRECTIONS[i]].position
            # Calculate path for unit
            path = world.get_shortest_path(unit.position, self.uuid_to_target[unit.uuid], self.nest_points)
            if path:
                world.move(unit, path[0])
            i = (i + 1) % 4
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
    return  {                           (x, y - 2),
                           (x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
               (x - 2, y), (x - 1, y),     point,      (x + 1, y),    (x + 2, y),
                           (x - 1, y + 1), (x, y + 1), (x + 1, y + 1),
                                           (x, y + 2)}