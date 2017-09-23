from PythonClientAPI.Game import PointUtils
from PythonClientAPI.Game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.Game.Enums import Direction, MoveType, MoveResult
from PythonClientAPI.Game.World import World

class PlayerAI:

    def __init__(self):
        """
        Any instantiation code goes here
        """
        pass

    def do_move(self, world, friendly_units, enemy_units):
        """
        This method will get called every turn.

        :param world: World object reflecting current game state
        :param friendly_units: list of FriendlyUnit objects
        :param enemy_units: list of EnemyUnit objects
        """
        # Schedule clusters of fireflies to go to closest neutral tile and build a nest
        # And then hold the position
        for unit in friendly_units:
            path = world.get_shortest_path(unit.position,
                                           world.get_closest_capturable_tile_from(unit.position, None).position,
                                           None)
            if path: world.move(unit, path[0])
            sort_by_taxicab_distance_to((4,4), friendly_units)


def sort_by_taxicab_distance_to(point, units):
    """
    Return a sorted copy of units in increasing order of taxicab distance from point.

    :param (int, int) point: point to calculate distance from
    :param list of Unit units: list of Unit objects to sort
    :return: a sorted copy of units in increasing order
    :rtype: list of Unit
    """
    def taxicab_distance(p1, p2):
        return abs(p2[0] - p1[0]) + abs(p2[1] - p1[1])
    return sorted(units, key=lambda unit: taxicab_distance(unit.position, point))
