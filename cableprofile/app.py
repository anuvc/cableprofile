from collections import OrderedDict

import dash_daq as daq
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, State, callback, dash_table, dcc, exceptions, html

from cableprofile import Cable2D

app = Dash(__name__)
app.title = "cableprofile"
server = app.server

introduction = [
    "cableprofile is a tool designed to simplify the process of determining 3D coordinates of cables in prestressed concrete structures. By providing a GUI interface, it automates tedious calculations, saving time and enhancing accuracy for civil engineers. \n Created by ", 
    html.A("Anuv Chakraborty", href="https://github.com/anuvc"),
    ". For reporting problems or suggesting enhancements, please email: anuv.chakrabo[at]gmail.com.",
]

# defaults
default_df = pd.DataFrame(
    OrderedDict(
        [
            ("sl-no", [1, 2, 3, 4, 5]),
            (
                "segment_type",
                ["straight", "reverse_curve", "straight", "parabolic", "straight"],
            ),
            ("segment_start_x", [0.000, 1.550, 4.550, 10.550, 12.550]),
            ("segment_start_y", [2.325, 2.233, 2.303, 1.945, 1.886]),
            ("segment_end_x", [1.550, 4.550, 10.550, 12.550, 15.050]),
            ("segment_end_y", [2.233, 2.303, 1.945, 1.886, 1.886]),
        ]
    )
)
default_interval = 0.050
default_symmetric = False
default_filename = "cableprofile.csv"

segment_types = ["straight", "reverse_curve", "parabolic"]

app.layout = html.Div(
    [
        # html.Img(src='/assets/logo.png', style={'width': '25rem'}),
        html.H1(
            children="cableprofile",
            style={"textAlign": "left", "font-family": "monospace"},
        ),
        html.P(introduction, className="introduction"),
        html.Hr(),
        html.P("x_coord_interval", className="interval_label"),
        dcc.Input(
            id="interval",
            className="interval",
            type="number",
            value=default_interval,
            debounce=True,
        ),
        html.Div(
            children=[
                html.P("symmetric", className="symmetric_switch_label"),
                daq.BooleanSwitch(
                    id="symmetric_switch", on=default_symmetric, className="symmetric_switch_button"
                ),
            ],
            className="symmetric_switch",
        ),
        html.Div(
            dcc.Graph(id="cable2d_profile_graph"),
            className="cable2d_profile_graph",
        ),
        html.Div(
            dash_table.DataTable(
                id="segments_table",
                data=default_df.to_dict("records"),
                columns=[
                    {
                        "id": "sl-no",
                        "name": "sl-no",
                        "editable": False,
                        "type": "numeric",
                    },
                    {
                        "id": "segment_type",
                        "name": "segment_type",
                        "presentation": "dropdown",
                        "editable": True,
                        "type": "text",
                    },
                    {
                        "id": "segment_start_x",
                        "name": "segment_start_x",
                        "editable": True,
                        "type": "numeric",
                        "format": {"specifier": ".3f"},
                    },
                    {
                        "id": "segment_start_y",
                        "name": "segment_start_y",
                        "editable": True,
                        "type": "numeric",
                        "format": {"specifier": ".3f"},
                    },
                    {
                        "id": "segment_end_x",
                        "name": "segment_end_x",
                        "editable": False,
                        "type": "numeric",
                        "format": {"specifier": ".3f"},
                    },
                    {
                        "id": "segment_end_y",
                        "name": "segment_end_y",
                        "editable": False,
                        "type": "numeric",
                        "format": {"specifier": ".3f"},
                    },
                ],
                dropdown={
                    "segment_type": {
                        "options": [{"label": i, "value": i} for i in segment_types]
                    }
                },
                row_deletable=True,
                style_header={
                    "fontWeight": "bold",
                    "cursor": "default",
                },
                style_cell={
                    "textAlign": "center",
                    "border": "1px solid slategray",
                },
                style_data_conditional=[
                    {
                        "if": {"state": "selected"},
                        "backgroundColor": "inherit !important",
                        "border": "inherit !important",
                    },
                    {
                        "if": {"state": "selected", "column_id": "segment_start_x"},
                        "backgroundColor": "aliceblue",
                        "border": "dodgerblue 2px solid",
                    },
                    {
                        "if": {"column_id": "segment_type"},
                        "width": "20%",
                    },
                    {
                        "if": {"state": "selected", "column_id": "segment_start_y"},
                        "backgroundColor": "aliceblue",
                        "border": "dodgerblue 2px solid",
                    },
                    {
                        "if": {"column_id": "segment_end_x"},
                        "background-color": "lightgray",
                        "cursor": "default",
                    },
                    {
                        "if": {"column_id": "segment_end_y"},
                        "background-color": "lightgray",
                        "cursor": "default",
                    },
                    {
                        "if": {"column_id": "segment_start_x"},
                        "cursor": "text",
                    },
                    {
                        "if": {"column_id": "segment_start_y"},
                        "cursor": "text",
                    },
                ],
            ),
            className="segments_table",
        ),
        html.Div(
            className="table_editing",
            children=[
                html.Button(
                    "add_row",
                    className="add_row_button",
                    id="add_row_button",
                    n_clicks=0,
                ),
                html.Button(
                    "clear_table",
                    className="clear_table_button",
                    id="clear_button",
                    n_clicks=0,
                ),
                html.Div(
                    className="cable_end_coordinates",
                    children=[
                        dcc.Input(
                            id="cable_end_x",
                            className="cable_end_x",
                            type="number",
                            value=15.050,
                            debounce=True,
                            placeholder="cable_end_x",
                        ),
                        dcc.Input(
                            id="cable_end_y",
                            className="cable_end_y",
                            type="number",
                            value=1.886,
                            debounce=True,
                            placeholder="cable_end_y",
                        ),
                    ],
                ),
            ],
        ),
        html.Hr(),
        html.Div(
            children=[
                dcc.Input(
                    id="filename",
                    className="filename",
                    type="text",
                    value=default_filename,
                    placeholder="filename",
                    debounce=True,
                ),
                html.Button("download_csv", className="download_button", id="btn_csv"),
                dcc.Download(id="download-dataframe-csv"),
            ],
            className="download_csv",
        ),
    ],
    className="container",
)


@callback(
    Output("cable2d_profile_graph", "figure"),
    Input("segments_table", "data"),
    Input("segments_table", "columns"),
    Input("interval", "value"),
    Input("symmetric_switch", "on"),
)
def plot_cable_profile(rows, columns, interval, symmetric):
    profile_df = get_profile(rows, interval, symmetric)
    fig = px.line(profile_df, x="x", y="y")
    fig.update_yaxes(scaleratio=1)
    return fig


def get_profile(rows, interval, symmetric):
    # if rows is empty return empty dataframe
    if not rows:
        return pd.DataFrame(columns=["x", "y"])
    control_points = get_control_points_from_table(rows, symmetric)
    segment_type_list = get_segment_type_list(rows, symmetric)
    profile_df = pd.DataFrame(
        get_coordinates(control_points, segment_type_list, interval), columns=["x", "y"]
    )
    return profile_df


def get_control_points_from_table(rows, symmetric):
    control_points = [(row["segment_start_x"], row["segment_start_y"]) for row in rows]
    # add the last point/mid point
    control_points.append((rows[-1]["segment_end_x"], rows[-1]["segment_end_y"]))
    if symmetric:
        mirrored_control_points = []
        end_of_cable_x = rows[-1]["segment_end_x"]
        # loop the rows in reverse with index
        for row in rows[::-1]:
            x_difference = row["segment_end_x"] - row["segment_start_x"]
            end_of_cable_x += x_difference
            mirrored_control_points.append((end_of_cable_x, row["segment_start_y"]))
        control_points.extend(mirrored_control_points)
    return control_points


def get_segment_type_list(rows, symmetric):
    if symmetric:
        return [row["segment_type"] for row in rows] + [
            row["segment_type"] for row in rows[::-1]
        ]
    else:
        return [row["segment_type"] for row in rows]


def get_coordinates(control_points, segment_type_list, interval):
    cable = Cable2D(control_points, segment_type_list)
    coordinates = cable.profile(interval)
    return coordinates


@callback(
    Output("segments_table", "data"),
    Input("segments_table", "data_timestamp"),
    State("segments_table", "data"),
    prevent_initial_call=True,
)
def update_table(timestamp, rows):
    rows = update_sl_no(rows)
    rows = update_segment_ends(rows)
    return rows


@callback(
    Output("segments_table", "data", allow_duplicate=True),
    Input("cable_end_x", "value"),
    Input("cable_end_y", "value"),
    State("segments_table", "data"),
    prevent_initial_call=True,
)
def update_cable_end(cable_end_x, cable_end_y, rows):
    rows[-1]["segment_end_x"] = cable_end_x
    rows[-1]["segment_end_y"] = cable_end_y
    return rows


@callback(
    Output("segments_table", "data", allow_duplicate=True),
    Input("add_row_button", "n_clicks"),
    State("segments_table", "data"),
    State("segments_table", "columns"),
    State("cable_end_x", "value"),
    State("cable_end_y", "value"),
    prevent_initial_call=True,
)
def add_row(n_clicks, rows, columns, cable_end_x, cable_end_y):
    if n_clicks > 0:
        if len(rows) == 0:
            rows.append(
                {
                    "sl-no": 1,
                    "segment_type": "straight",
                    "segment_start_x": 0,
                    "segment_start_y": 0,
                    "segment_end_x": cable_end_x,
                    "segment_end_y": cable_end_y,
                }
            )
        else:
            rows.append(
                {
                    "sl-no": rows[-1]["sl-no"] + 1,
                    "segment_type": "straight",
                    # set new segment x as the midpoint of the previous segment
                    "segment_start_x": (
                        rows[-1]["segment_start_x"] + rows[-1]["segment_end_x"]
                    )
                    / 2,
                    # set new segment y as the midpoint of the previous segment
                    "segment_start_y": (
                        rows[-1]["segment_start_y"] + rows[-1]["segment_end_y"]
                    )
                    / 2,
                    "segment_end_x": cable_end_x,
                    "segment_end_y": cable_end_y,
                }
            )
        update_segment_ends(rows)
    return rows


def update_sl_no(rows):
    for i in range(0, len(rows)):
        rows[i]["sl-no"] = i + 1
    return rows


def update_segment_ends(rows):
    # update the segment_end_x and segment_end_y columns based on the segment_start_x and segment_start_y columns of the previous row
    for i in range(0, len(rows) - 1):
        rows[i]["segment_end_x"] = rows[i + 1]["segment_start_x"]
        rows[i]["segment_end_y"] = rows[i + 1]["segment_start_y"]
    return rows


@callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    State("filename", "value"),
    State("segments_table", "data"),
    State("interval", "value"),
    State("symmetric_switch", "on"),
    prevent_initial_call=True,
)
def save_profile(n_clicks, filename, rows, interval, symmetric):
    profile_df = get_profile(rows, interval, symmetric)
    return dcc.send_data_frame(profile_df.to_csv, filename)


@callback(
    Output("segments_table", "data", allow_duplicate=True),
    Input("clear_button", "n_clicks"),
    prevent_initial_call=True,
)
def clear_table_data(n_clicks):
    if n_clicks == 0:
        raise exceptions.PreventUpdate()
    data = pd.DataFrame().to_dict("records")  # empty dataframe
    return data


if __name__ == "__main__":
    app.run(debug=True)
