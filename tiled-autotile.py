#!/usr/bin/env python3
from typing import Tuple, Any

from PIL import Image
import sys
import os


TILE_SIZE = 32

SUBTILE_SIZE = TILE_SIZE // 2

TERRAIN_AUTOTILE_WIDTH = TILE_SIZE * 2
TERRAIN_AUTOTILE_HEIGHT = TILE_SIZE * 3

TERRAIN_TILED_WIDTH = TILE_SIZE * 3
TERRAIN_TILED_HEIGHT = TILE_SIZE * 5


def run():
    source = Image.open(sys.argv[1])
    target = unpack(source)
    filename = '_unpacked'.join(os.path.splitext(sys.argv[1]))
    target.save(filename)


def unpack(source: Image) -> Image:
    num_x = source.width // TERRAIN_AUTOTILE_WIDTH
    num_y = source.height // TERRAIN_AUTOTILE_HEIGHT

    target = Image.new('RGBA', (TERRAIN_TILED_WIDTH * num_x, TERRAIN_TILED_HEIGHT * num_y))

    # Handle each terrain tile cluster independently.
    for y in range(num_y):
        for x in range(num_x):
            left = TERRAIN_AUTOTILE_WIDTH * x
            upper = TERRAIN_AUTOTILE_HEIGHT * y
            right = left + TERRAIN_AUTOTILE_WIDTH
            lower = upper + TERRAIN_AUTOTILE_HEIGHT
            terrain_source = source.crop((left, upper, right, lower))

            left = TERRAIN_TILED_WIDTH * x
            upper = TERRAIN_TILED_HEIGHT * y
            right = left + TERRAIN_TILED_WIDTH
            lower = upper + TERRAIN_TILED_HEIGHT
            terrain_target = target.crop((left, upper, right, lower))

            convert_terrain(terrain_source, terrain_target)
            target.paste(terrain_target, (left, upper))

    return target


def convert_terrain(source: Image, target: Image):
    # Terrain preview tile (unused in actual tiling).
    preview = source.crop((0, 0, TILE_SIZE, TILE_SIZE))
    target.paste(preview)

    # Outer 2x2 square, row-by-row.
    copy_subtiles(source, target, ((2, 4), (1, 4), (2, 3), (3, 1)), (1, 0))
    copy_subtiles(source, target, ((2, 4), (1, 4), (2, 1), (1, 3)), (2, 0))
    copy_subtiles(source, target, ((2, 4), (3, 0), (2, 3), (1, 3)), (1, 1))
    copy_subtiles(source, target, ((2, 0), (1, 4), (2, 3), (1, 3)), (2, 1))

    # Inner 3x3 square, row-by-row.
    copy_subtiles(source, target, ((0, 2), (1, 2), (0, 3), (1, 3)), (0, 2))
    copy_subtiles(source, target, ((2, 2), (1, 2), (2, 3), (1, 3)), (1, 2))
    copy_subtiles(source, target, ((2, 2), (3, 2), (2, 3), (3, 3)), (2, 2))

    copy_subtiles(source, target, ((0, 4), (1, 4), (0, 3), (1, 3)), (0, 3))
    copy_subtiles(source, target, ((2, 4), (1, 4), (2, 3), (1, 3)), (1, 3))
    copy_subtiles(source, target, ((2, 4), (3, 4), (2, 3), (3, 3)), (2, 3))

    copy_subtiles(source, target, ((0, 4), (1, 4), (0, 5), (1, 5)), (0, 4))
    copy_subtiles(source, target, ((2, 4), (1, 4), (2, 5), (1, 5)), (1, 4))
    copy_subtiles(source, target, ((2, 4), (3, 4), (2, 5), (3, 5)), (2, 4))


def copy_subtiles(source: Image, target: Image, subtile_coords: Tuple, target_coords: Tuple[int, int]):
    target_x = target_coords[0] * TILE_SIZE
    target_y = target_coords[1] * TILE_SIZE
    for (x, y), (target_offset_x, target_offset_y) in zip(subtile_coords, ((0, 0), (1, 0), (0, 1), (1, 1))):
        left = SUBTILE_SIZE * x
        upper = SUBTILE_SIZE * y
        right = left + SUBTILE_SIZE
        lower = upper + SUBTILE_SIZE

        subtile = source.crop((left, upper, right, lower))
        left = target_x + SUBTILE_SIZE * target_offset_x
        upper = target_y + SUBTILE_SIZE * target_offset_y
        target.paste(subtile, (left, upper))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: {} input_file".format(sys.argv[0]))
        exit(1)
    run()
