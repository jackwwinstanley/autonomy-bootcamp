"""
TODO(bootcamper): write the tests for ``src/waypoint_utils.py`` in here.

The example below covers files that parse fine: with and without ``home``,
and files with comments and blank lines in them. The rest is yours:

- Bad data: a file whose top level isn't a mapping, waypoints missing
  ``lat``, ``lon``, or ``alt``, values that aren't numbers, YAML that
  doesn't parse, and a file that isn't there.
- Out of range: latitudes past +/-90 and longitudes past +/-180 get
  rejected.
- Nothing to work with: an empty file, an empty ``waypoints`` list, and
  ``sort_clockwise_sweep`` given a list of 0 or 1 waypoints.
- ``east_north_coordinate_offset_m``: offsets you worked out yourself,
  compared with ``pytest.approx``. Never use ``==`` on meters.
- Ordering: with no ``home``, ``sort_clockwise_sweep`` goes clockwise
  starting from north.
- With a ``home``: the order starts in home's direction instead, and goes
  back to starting at north if home is right on top of the centroid.
- Two waypoints in the same direction: the closer one comes first.
- Parsing gives you frozen ``Coordinate`` objects that can't be changed.

Graded by ``warg run utils grade-tests``: pass on the real code, 90% branch
coverage, and fail on every broken copy in ``grader/mutants/``.
"""

import pytest

from src.types import Coordinate
from src.waypoint_utils import (
    east_north_coordinate_offset_m,
    parse_waypoints_file,
    sort_clockwise_sweep,
)

# The helper and the test below are given to you.


def write_to_tmp_waypoints_file(tmp_path, text):
    """Write ``text`` to a YAML file and hand back its path.

    ``tmp_path`` is a pytest fixture: a fresh empty directory per test.
    """
    path = tmp_path / "waypoints.yaml"
    path.write_text(text)
    return path


# One test, three files. ``parametrize`` runs the test body once per
# ``(text, expected)`` pair, and ``ids`` names each run so a failure tells you
# which file broke.
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            """
            home: {lat: 1, lon: 2, alt: 3}
            waypoints:
              - {lat: 4, lon: 5, alt: 6}
            """,
            (Coordinate(1, 2, 3), [Coordinate(4, 5, 6)]),
        ),
        (
            """
            waypoints:
              - {lat: 4, lon: 5, alt: 6}
              - {lat: 7, lon: 8, alt: 9}
            """,
            (None, [Coordinate(4, 5, 6), Coordinate(7, 8, 9)]),
        ),
        (
            """
            # a lap

            home: {lat: 1, lon: 2, alt: 3}

            waypoints:
              # first leg
              - {lat: 4, lon: 5, alt: 6}
            """,
            (Coordinate(1, 2, 3), [Coordinate(4, 5, 6)]),
        ),
    ],
    ids=["home-and-waypoints", "no-home", "comments-and-blank-lines"],
)
def test_parse_waypoints_file_success(tmp_path, text, expected):
    path = write_to_tmp_waypoints_file(tmp_path, text)
    assert parse_waypoints_file(path) == expected


# def test_placeholder():
#   # TODO(bootcamper): delete this and write real tests. It's only here so
#   # linter doesn't complain about unused imports before you start.
#   assert callable(east_north_coordinate_offset_m)
#   assert callable(parse_waypoints_file)
#   assert callable(sort_clockwise_sweep)

yaml_text_1 = """
waypoints: 
- lat: north
  lon: 2
  alt: 3  
"""
yaml_text_2 = """
waypoints: 
- lat: 1
  lon: east
  alt: 3  
"""

yaml_text_3= """
waypoints: 
- lat: 1
  lon: 2
  alt: high
"""

@pytest.mark.parametrize("text", [yaml_text_1, yaml_text_2, yaml_text_3])
def test_waypoint_non_numerical(tmp_path, text):
    path = write_to_tmp_waypoints_file(tmp_path, text)
    with pytest.raises(ValueError):
        parse_waypoints_file(path)

@pytest.mark.parametrize("text",
[
"""
waypoints:
- lat: 91
  lon: 2
  alt: 7
"""
,
"""
waypoints:
- lat: -91
  lon: 2
  alt: 7
"""
])
def test_waypoint_out_of_range_lat(tmp_path, text):
    path = write_to_tmp_waypoints_file(tmp_path, text)
    with pytest.raises(ValueError):
        parse_waypoints_file(path)


@pytest.mark.parametrize("text",
[
"""
waypoints:
- lat: 9
  lon: 181
  alt: 7
"""
,
"""
waypoints:
- lat: 1
  lon: -181
  alt: 7
"""
])
def test_waypoint_out_of_range_lon(tmp_path,text):
    path = write_to_tmp_waypoints_file(tmp_path, text)
    with pytest.raises(ValueError):
        parse_waypoints_file(path)
    
@pytest.mark.parametrize(
    "text",
    [
        """
waypoints:
  - lon: 1
    alt: 3
""",
        """
waypoints:
  - lat: 1
    alt: 2
""",
        """
waypoints:
  - lat: 1
    lon: 2
""",
    ],
)
def test_waypoint_missing_inputs(tmp_path,text):
    path = write_to_tmp_waypoints_file(tmp_path, text)
    with pytest.raises(ValueError):
        parse_waypoints_file(path)

def test_waypoint_empty(tmp_path):
    text = ""
    path = write_to_tmp_waypoints_file(tmp_path, text)
    _, waypoints = parse_waypoints_file(path)
    assert [] == waypoints

def test_waypoint_empty_list(tmp_path):
    text = """
waypoints: []
"""
    path = write_to_tmp_waypoints_file(tmp_path, text)
    _, waypoints = parse_waypoints_file(path)
    assert [] == waypoints

def test_waypoints_no_indicator(tmp_path):
    text = """
waypoints:
 lat: 1
 lon: 2
 alt: 3
 """
    path = write_to_tmp_waypoints_file(tmp_path, text)
    with pytest.raises(ValueError):
        parse_waypoints_file(path)

def test_clockwise_sweep_with_empty_list():
    empty_list = []
    res = sort_clockwise_sweep(empty_list)
    assert(res == [])

def test_clockwise_sweep_without_enough_waypoints():
    test = Coordinate(1,2,3)
    waypoints = [test]
    assert([test] == sort_clockwise_sweep(waypoints))

def test_east_north_coordinate_offsets():
    east, north = east_north_coordinate_offset_m(10,10,5,5)
    proj_east = -551219
    proj_north = -555975
    assert(east == pytest.approx(proj_east))
    assert(north == pytest.approx(proj_north))

def test_ordering_clockwise_sweep():
    one = Coordinate(5, 10, 1)
    two = Coordinate(15, 10, 1)
    three = Coordinate(10, 5, 1)
    four = Coordinate(10, 15, 1)
    waypoints = [four, one, two, three]

    res = sort_clockwise_sweep(waypoints)

    expected_order = [two, four, one, three]

    assert res == expected_order

def test_home_ordering_clockwise_sweep():
    one = Coordinate(5, 10, 1)
    two = Coordinate(15, 10, 1)
    three = Coordinate(10, 5, 1)
    four = Coordinate(10, 15, 1)
    waypoints = [four, one, two, three]

    res = sort_clockwise_sweep(waypoints, four)

    expected_order = [four, one, three, two]

    assert res == expected_order

def test_home_centroid_clockwise_sweep():
    one = Coordinate(5, 10, 1)
    two = Coordinate(15, 10, 1)
    three = Coordinate(10, 5, 1)
    four = Coordinate(10, 15, 1)
    home = Coordinate(10,10,1)

    waypoints = [four, one, two, three]

    res = sort_clockwise_sweep(waypoints, home)


    expected_order = [two, four, one, three]

    assert res == expected_order

def test_same_direction_different_distances_centroid_clockwise_sweep():
    close = Coordinate(10,15,1)
    close2 = Coordinate(10,5,1)

    far = Coordinate(10,20,1)
    far2 = Coordinate(10,0,1)


    waypoints = [far, close2, far2, close]

    res = sort_clockwise_sweep(waypoints)


    expected_order = [close, far, close2, far2]

    assert res == expected_order

def test_frozen_coordinate_after_waypoint_parse(tmp_path):
    text = """
waypoints:
- lat: 1
  lon: 2
  alt: 3
"""
    path = write_to_tmp_waypoints_file(tmp_path,text)
    _, waypoints = parse_waypoints_file(path)
    coord = waypoints[0]
    with pytest.raises(AttributeError):
      coord.lat = 3

def test_waypoint_invalid_text(tmp_path):
    text = """
hello
"""
    path = write_to_tmp_waypoints_file(tmp_path, text)
    with pytest.raises(ValueError):
        parse_waypoints_file(path)

def test_waypoint_invalid_yaml(tmp_path):
    text = """
waypoints: [
"""
    path = write_to_tmp_waypoints_file(tmp_path, text)
    with pytest.raises(ValueError):
        parse_waypoints_file(path)

def test_waypoint_invalid_path(tmp_path):
    path = tmp_path / "missing.yaml"
    with pytest.raises(OSError):
        parse_waypoints_file(path)

