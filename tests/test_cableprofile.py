#!/usr/bin/env python

"""Tests for `cableprofile` package."""

import pytest

from click.testing import CliRunner

from cableprofile import cableprofile
from cableprofile import cli

import matplotlib.pyplot as plt


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'cableprofile.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output

def test_Cable2D():
    control_points = [
        (0.000, 2.325),
        (1.550, 2.233),
        (4.550, 2.303),
        (10.550, 1.945),
        (12.550, 1.886),
        (15.050, 1.886),
    ]
    segment_type_list = [
        "straight",
        "reverse_curve",
        "straight",
        "parabolic",
        "straight",
    ]
    cable = cableprofile.Cable2D(control_points, segment_type_list)
    coordinates = cable.profile(0.050)
    plt.plot(*zip(*coordinates))
    plt.show()

