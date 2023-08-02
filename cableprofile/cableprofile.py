from typing import List, Tuple

import numpy as np


class CableSegment:
    def __init__(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> None:
        self.p1 = p1
        self.p2 = p2

    def get_coordinates(self, interval):
        NotImplementedError


class Straight(CableSegment):
    def __init__(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> None:
        super().__init__(p1, p2)

    def __repr__(self) -> str:
        return f"Straight({self.p1}, {self.p2})"

    def get_coordinates(self, interval):
        """Return a list of coordinates between two points.

        Args:
            p1 (tuple): The first point.
            p2 (tuple): The second point.
            interval (int): The interval between each point.

        Returns:
            list: A list of coordinates between p1 and p2.
        """
        x1, y1 = self.p1
        x2, y2 = self.p2
        dx = x2 - x1
        dy = y2 - y1
        x_coords = np.linspace(x1, x2, int(dx / interval), endpoint=False)
        slope = dy / dx
        intercept = y1 - slope * x1
        y_coords = slope * x_coords + intercept
        coordinates = np.column_stack((x_coords, y_coords))
        return coordinates


class Parabolic(CableSegment):
    def __init__(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> None:
        super().__init__(p1, p2)

    def __repr__(self) -> str:
        return f"Parabolic({self.p1}, {self.p2})"

    def get_coordinates(self, interval):
        """Return a list of coordinates between two points.

        Args:
            p1 (tuple): The first point.
            p2 (tuple): The second point.
            interval (int): The interval between each point.

        Returns:
            list: A list of coordinates between p1 and p2.
        """

        x1, y1 = self.p1
        x2, y2 = self.p2
        dx = x2 - x1
        dy = y2 - y1
        x_coords = np.linspace(x1, x2, int(dx / interval), endpoint=False)
        if dy > 0:
            y_coords = y1 + (x_coords - x1) ** 2 * dy / dx**2
        else:
            y_coords = y2 - (x_coords - x2) ** 2 * dy / dx**2
        coordinates = np.column_stack((x_coords, y_coords))
        return coordinates


class ReverseCurve(CableSegment):
    def __init__(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> None:
        super().__init__(p1, p2)

    def __repr__(self) -> str:
        return f"ReverseCurve({self.p1}, {self.p2})"

    def get_coordinates(self, interval):
        """Return a list of coordinates between two points.

        Args:
            p1 (tuple): The first point.
            p2 (tuple): The second point.
            interval (int): The interval between each point.

        Returns:
            list: A list of coordinates between p1 and p2.
        """

        x1, y1 = self.p1
        x2, y2 = self.p2
        dx = x2 - x1
        xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
        x_coords = np.linspace(x1, x2, int(dx / interval), endpoint=False)
        y_coords = np.piecewise(
            x_coords,
            [x_coords <= xm, x_coords > xm],
            [
                lambda x: y1 + (ym - y1) / (xm - x1) ** 2 * (x - x1) ** 2,
                lambda x: y2 - (y2 - ym) / (x2 - xm) ** 2 * (x2 - x) ** 2,
            ],
        )
        coordinates = np.column_stack((x_coords, y_coords))
        return coordinates


class Cable2D:
    def __init__(
        self,
        control_points: List[Tuple[(float, float)]],
        segment_type_list: List[str],
    ):
        self.control_points_list = control_points
        self.segment_type_list = segment_type_list
        # check if the number of control points is one more than the number of segments
        try:
            assert len(control_points) == len(segment_type_list) + 1
        except AssertionError:
            print(
                "The number of control points should be one more than the number of segments."
            )
        self.segment_list = self._create_segment_list()

    def _create_segment_list(self):
        """Return a list of CableSegment objects."""
        segment_list = []
        for i in range(len(self.segment_type_list)):
            if self.segment_type_list[i] == "straight":
                segment_list.append(
                    Straight(
                        self.control_points_list[i], self.control_points_list[i + 1]
                    )
                )
            elif self.segment_type_list[i] == "parabolic":
                segment_list.append(
                    Parabolic(
                        self.control_points_list[i], self.control_points_list[i + 1]
                    )
                )
            elif self.segment_type_list[i] == "reverse_curve":
                segment_list.append(
                    ReverseCurve(
                        self.control_points_list[i], self.control_points_list[i + 1]
                    )
                )
        return segment_list

    def profile(self, interval):
        """Return a list of coordinates of the cable profile."""
        coordinates = []
        for segment in self.segment_list:
            coordinates.append(segment.get_coordinates(interval))
        coordinates = np.concatenate(coordinates)
        # add cable endpoint to the coordinates
        coordinates = np.vstack((coordinates, self.control_points_list[-1]))
        return coordinates
