#!/usr/bin/env python3

AUTOTILE_WALL_WIDTH = 2
AUTOTILE_WALL_HEIGHT = 2
AUTOTILE_TERRAIN_WIDTH = 2
AUTOTILE_TERRAIN_HEIGHT = 3
TILED_WALL_WIDTH = 4
TILED_WALL_HEIGHT = 4
TILED_TERRAIN_WIDTH = 7
TILED_TERRAIN_HEIGHT = 7

# Terrain and wall subtile combinations are procedurally generated and placed in a 7x7 grid in the order they are
# generated. This manual mapping reorders them for better visual grouping.
REORDERING = (
    # 3x3.
    ((0, 0), (0, 0)),
    ((4, 0), (1, 0)),
    ((5, 0), (2, 0)),
    ((1, 1), (0, 1)),
    ((5, 1), (1, 1)),
    ((6, 1), (2, 1)),
    ((3, 1), (0, 2)),
    ((0, 2), (1, 2)),
    ((1, 2), (2, 2)),

    # Single-tile vertical.
    ((1, 0), (3, 0)),
    ((2, 1), (3, 1)),
    ((4, 1), (3, 2)),

    # Single-tile horizontal.
    ((2, 0), (0, 3)),
    ((6, 0), (1, 3)),
    ((0, 1), (2, 3)),

    # Preview 1x1 tile.
    ((3, 0), (3, 3)),

    # Terrain-only from here on.
    # 3x3 with four islands.
    ((2, 4), (4, 0)),
    ((3, 4), (5, 0)),
    ((4, 3), (6, 0)),
    ((4, 4), (4, 1)),
    ((4, 6), (5, 1)),
    ((0, 5), (6, 1)),
    ((5, 3), (4, 2)),
    ((1, 5), (5, 2)),
    ((6, 4), (6, 2)),

    # 3x2 channel with two islands.
    ((5, 2), (4, 3)),
    ((6, 2), (5, 3)),
    ((3, 2), (6, 3)),
    ((1, 4), (4, 4)),
    ((6, 5), (5, 4)),
    ((5, 5), (6, 4)),

    # 2x3 channel with two islands.
    ((2, 3), (0, 4)),
    ((0, 4), (1, 4)),
    ((3, 3), (0, 5)),
    ((4, 5), (1, 5)),
    ((0, 3), (0, 6)),
    ((3, 5), (1, 6)),

    # Single diagonal island parts.
    ((1, 6), (2, 4)),
    ((6, 3), (3, 4)),

    # 2x2 with single island.
    ((2, 2), (2, 5)),
    ((4, 2), (3, 5)),
    ((1, 3), (2, 6)),
    ((0, 6), (3, 6)),

    # 2x2 with '+'-formation islands.
    ((5, 4), (4, 5)),
    ((2, 6), (5, 5)),
    ((3, 6), (4, 6)),
    ((2, 5), (5, 6)),

    # Empty patches.
    ((5, 6), (6, 5)),
    ((6, 6), (6, 6)),
)


def run():
    combinations_wall, combinations_terrain = subtile_combinations()
    print('Wall:\n' + ',\n'.join(str(combination) for combination in combinations_wall))
    print('Terrain:\n' + ',\n'.join(str(combination) for combination in combinations_terrain))


def subtile_combinations():
    combinations = generate_terrain_subtile_combinations()

    # Terrain autotiles have the additional '+'-shaped tile in the first two subtile rows, so any combinations including
    # any of these subtiles are exclusive to terrain autotiles.
    combinations_wall_unordered = [
        combination for combination in combinations
        if all(coord[1] >= 2 for coord in combination)
    ]
    combinations_terrain_unordered = [
        combination for combination in combinations
        if any(coord[1] < 2 for coord in combination)
    ]

    combinations_wall = reorder_combinations(
        combinations_wall_unordered,
        TILED_WALL_WIDTH,
        TILED_WALL_HEIGHT
    )
    combinations_terrain = reorder_combinations(
        combinations_wall_unordered + combinations_terrain_unordered,
        TILED_TERRAIN_WIDTH,
        TILED_TERRAIN_HEIGHT
    )

    # Wall combinations still use terrain-style subtile coordinates, so shift them up again.
    combinations_wall = [
        tuple((x, y - 2) for x, y in combination)
        for combination in combinations_wall
    ]

    return combinations_wall, combinations_terrain


def generate_terrain_subtile_combinations():
    # Top-left
    combinations_top_left = [
        ((0, 2),),
        ((2, 2),),
        ((0, 4),),
        ((2, 4),),
        ((2, 0),)
    ]

    # Bottom-right
    combinations_bottom_right = []
    for combination in combinations_top_left:
        combinations_bottom_right.append((*combination, (1, 3)))
        combinations_bottom_right.append((*combination, (3, 3)))
        combinations_bottom_right.append((*combination, (1, 5)))
        combinations_bottom_right.append((*combination, (3, 5)))
        combinations_bottom_right.append((*combination, (3, 1)))

    # Top-Right
    combinations_top_right = []
    for combination in combinations_bottom_right:
        # Pick the subtile that is in the same col as bottom-right and same row as top-left.
        reference_col_subtile = combination[1]
        reference_row_subtile = combination[0]

        # Exception: If previous subtiles are from the 2x2 '+'-shaped subtiles, use center subtile for reference.
        reference_col_subtile = reference_col_subtile if reference_col_subtile[1] > 1 else (1, 3)
        reference_row_subtile = reference_row_subtile if reference_row_subtile[1] > 1 else (2, 4)

        subtile = (reference_col_subtile[0], reference_row_subtile[1])
        combinations_top_right.append((*combination, subtile))

        # If we're adding the center subtile (the 'full' one), we can alternatively add the '+' one.
        if subtile == (1, 4):
            combinations_top_right.append((*combination, (3, 0)))

    # Bottom-left
    combinations_bottom_left = []
    for combination in combinations_top_right:
        # Pick the subtile that is in the same col as top-left and same row as bottom-right.
        reference_col_subtile = combination[0]
        reference_row_subtile = combination[1]

        # Exception: If previous subtiles are from the 2x2 '+'-shaped subtiles, use center subtile for reference.
        reference_col_subtile = reference_col_subtile if reference_col_subtile[1] > 1 else (2, 4)
        reference_row_subtile = reference_row_subtile if reference_row_subtile[1] > 1 else (1, 3)

        subtile = (reference_col_subtile[0], reference_row_subtile[1])
        combinations_bottom_left.append((*combination, (reference_col_subtile[0], reference_row_subtile[1])))
        # If we're adding the center subtile (the 'full' one), we can alternatively add the '+' one.
        if subtile == (2, 3):
            combinations_bottom_left.append((*combination, (2, 1)))

    return combinations_bottom_left


def reorder_combinations(combinations, grid_width: int, grid_height: int):
    # Flatten grid mapping row-wise into a linear mapping. Exclude cells that are outside the target grid.
    # The grid used in the reordering mapping is always 7x7 (TileD terrain grid).
    reordering = [
        (source_x + source_y * TILED_TERRAIN_WIDTH, target_x + target_y * TILED_TERRAIN_WIDTH)
        for (source_x, source_y), (target_x, target_y) in REORDERING
        if target_x < grid_width and target_y < grid_height
    ]
    reordering.sort(key=lambda mapping: mapping[1])

    # Check for source or target duplicates.
    sources = [source for source, target in reordering]
    targets = [target for source, target in reordering]
    assert(len(sources) == len(set(sources)))
    assert(len(targets) == len(set(targets)))

    # Reorder indices that are out of bound are for padding (empty) tiles. For those, include an empty combination.
    return [
        combinations[source] if source < len(combinations) else ()
        for source in sources
    ]


if __name__ == '__main__':
    run()
