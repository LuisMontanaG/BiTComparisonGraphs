# import dash
# from dash import dcc, html
# from dash.dependencies import Input, Output
# import numpy as np
#
# # Initialize the Dash app
# app = dash.Dash(__name__)
#
# # Sample data
# categories = ['A', 'B', 'C', 'D']
# values1 = np.random.randint(10, 100, size=4)
# values2 = np.random.randint(10, 100, size=4)
#
# # App layout
# app.layout = html.Div([
#     dcc.Graph(id='bar-chart'),
#     dcc.Dropdown(
#         id='chart-type-dropdown',
#         options=[
#             {'label': 'Grouped', 'value': 'group'},
#             {'label': 'Stacked', 'value': 'stack'}
#         ],
#         value='group',  # Default value
#         clearable=False,
#         style={'width': '50%'}
#     ),
#     dcc.Store(id='bar-data', data={'categories': categories, 'values1': list(values1), 'values2': list(values2)})
# ])
#
# # Client-side callback (JavaScript function)
# app.clientside_callback(
#     """
#     function(chartType, data) {
#         var categories = data.categories;
#         var values1 = data.values1;
#         var values2 = data.values2;
#
#         var barmode = chartType === 'stack' ? 'stack' : 'group';
#
#         return {
#             'data': [
#                 {
#                     'x': categories,
#                     'y': values1,
#                     'type': 'bar',
#                     'name': 'Series 1'
#                 },
#                 {
#                     'x': categories,
#                     'y': values2,
#                     'type': 'bar',
#                     'name': 'Series 2'
#                 }
#             ],
#             'layout': {
#                 'title': `Bar Chart (${chartType === 'stack' ? 'Stacked' : 'Grouped'})`,
#                 'barmode': barmode
#             }
#         };
#     }
#     """,
#     Output('bar-chart', 'figure'),
#     [Input('chart-type-dropdown', 'value')],
#     [Input('bar-data', 'data')]
# )
#
# # Run the app
# if __name__ == '__main__':
#     app.run_server(debug=False)

from dash import Dash, html, Input, Output, callback, dcc, ctx
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from functions import *

group_by = 'Teams'
database_1 = 'GEC2017'
database_2 = 'GEC2017'
team_1 = 'All'
meeting_1 = '1'
team_2 = 'All'
meeting_2 = '2'

node_type = 'Behaviours'
edge_type = 'Frequency'
colour_type = 'Behaviours'
colour_source = 'Source'
show_edges = 'All'
normalise = True

teams_1, meetings_1, teams_2, meetings_2, node_data, edge_data, nodes, edges, selector_node_classes, selector_edge_classes, min_weight, max_weight, weight_bins, node_signs, edge_signs, node_names, behaviours, node_stats, edge_stats = load_dataset_comparison(group_by, database_1, team_1, meeting_1, database_2, team_2, meeting_2, node_type, edge_type, colour_type, colour_source, normalise)
legend_nodes = get_legend_nodes(node_names, selector_node_classes, colour_type, behaviours)

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

default_stylesheet = [
    # Group selectors for nodes
    {
        'selector': 'node',
        'style': {
            #'background-color': '#00000',
            'label': 'data(label)',
            'font-size': '20px',
            'text-halign':'center',
            'text-valign':'center'
        },
    },
        {
            'selector': 'label',
            'style': {
                'content': 'data(label)',
                'color': 'white',
            }
        }
]

legend_stylesheet = [
    # Group selectors for nodes
    {
        'selector': 'node',
        'style': {
            'label': 'data(label)',
            'font-size': '20px',
            'text-halign': 'right',
            'text-valign': 'center'
        }
    },
    {
        'selector': 'label',
        'style': {
            'content': 'data(label)',
            'color': 'white',
            'text-margin-x': '10px',
        }
    },

]

layout_dropdown = html.Div([
    html.P("Layout:"),
    dcc.Dropdown(
        id='dropdown-update-layout',
        value='grid',
        clearable=False,
        options=[
            {'label': name.capitalize(), 'value': name}
            for name in ['grid', 'random', 'circle', 'cose', 'concentric']
        ],
        style={'width': '150px'},
        className='dash-bootstrap'
    )
], style = {'display': 'inline-block', 'margin-left': '20px'})

group_dropdown = html.Div([
    html.P("Group by:"),
    dcc.Dropdown(
        id='dropdown-update-group',
        value='Teams',
        clearable=False,
        options=[
            {'label': name, 'value': name}
            for name in ['Teams', 'teammark', 'airtime_evenness', 'psy_safe', 'expgroup']
        ],
        style={'width': '150px'},
        className='dash-bootstrap'
    )
], style = {'display': 'inline-block', 'margin-left': '20px'})

database_1_dropdown = html.Div([
    html.P("Database 1: "),
    dcc.Dropdown(
        id='dropdown-update-database',
        value='GEC2017',
        clearable=False,
        options=[
        {'label': name, 'value': name}
        for name in ['GEC2017', 'GEC2018', 'EYH2017', 'EYH2018', 'IDP2019', 'IDP2020']
        ],
        className='dash-bootstrap',
        style={'width': '200px'},
    )],
    style = {'display': 'inline-block', 'margin-left': '20px'},
)

team_1_dropdown = html.Div([
    html.P("Team 1:"),
    dcc.Dropdown(
        id = 'dropdown-update-team',
        value='All',
        clearable=False,
        options=[
            {'label': name, 'value': name}
            for name in teams_1
        ],
        style={'width': '200px'},
        className='dash-bootstrap'
    )],
    style = {'display': 'inline-block', 'margin-left': '20px'}
)

meeting_1_dropdown = html.Div([
    html.P("Meeting 1:"),
    dcc.Dropdown(
        id = 'dropdown-update-meeting',
        value='1',
        clearable=False,
        options=[
            {'label': name, 'value': name}
            for name in meetings_1
        ],
        style={'width': '200px'},
        className='dash-bootstrap'
    )],
    style = {'display': 'inline-block', 'margin-left': '20px'}
)

database_2_dropdown = html.Div([
    html.P("Database 2: "),
    dcc.Dropdown(
        id='dropdown-update-database-compare',
        value='GEC2017',
        clearable=False,
        options=[
        {'label': name, 'value': name}
        for name in ['GEC2017', 'GEC2018', 'EYH2017', 'EYH2018', 'IDP2019', 'IDP2020']
        ],
        className='dash-bootstrap',
        style={'width': '200px'},
    )],
    style = {'display': 'inline-block', 'margin-left': '20px'},
)

team_2_dropdown = html.Div([
    html.P("Team 2:"),
    dcc.Dropdown(
        id = 'dropdown-update-team-compare',
        value='All',
        clearable=False,
        options=[
            {'label': name, 'value': name}
            for name in teams_2
        ],
        style={'width': '200px'},
        className='dash-bootstrap'
    )],
    style = {'display': 'inline-block', 'margin-left': '20px'}
)

meeting_2_dropdown = html.Div([
    html.P("Meeting 2:"),
    dcc.Dropdown(
        id = 'dropdown-update-meeting-compare',
        value='2',
        clearable=False,
        options=[
            {'label': name, 'value': name}
            for name in meetings_2
        ],
        style={'width': '200px'},
        className='dash-bootstrap'
    )],
    style = {'display': 'inline-block', 'margin-left': '20px'}
)

node_type_radio = html.Div([html.P("Node:", style = {'display': 'inline-block'}),
    html.Div(dcc.RadioItems(['Behaviours', 'Participants'], id='radio-update-nodes', value='Behaviours', inline=True, inputStyle={'margin-right': '10px', 'margin-left': '10px'}), style={'display': 'inline-block'})
], style={'margin-left': '20px', 'margin-top': '20px', 'display': 'inline-block'})

edge_type_radio = html.Div([html.P("Edge:", style = {'display': 'inline-block'}),
    html.Div(dcc.RadioItems(['Frequency', 'Probability'], id='radio-update-edges', value='Frequency', inline=True, inputStyle={'margin-right': '10px', 'margin-left': '10px'}), style={'display': 'inline-block'})
], style={'margin-left': '20px', 'margin-top': '20px', 'display': 'inline-block'})

colour_type_radio = html.Div([html.P("Colour by:", style = {'display': 'inline-block'}),
    html.Div(dcc.RadioItems(['Behaviours', 'Participants'], id='radio-update-colour_type', value='Behaviours', inline=True, inputStyle={'margin-right': '10px', 'margin-left': '10px'}), style={'display': 'inline-block'})
], style={'margin-left': '20px', 'margin-top': '20px', 'display': 'inline-block'})

colour_source_radio = html.Div([html.P("Colour by:", style = {'display': 'inline-block'}),
    html.Div(dcc.RadioItems(['Source', 'Target'], id='radio-update-colour-source', value='Source', inline=True, inputStyle={'margin-right': '10px', 'margin-left': '10px'}), style={'display': 'inline-block'})
], style={'margin-left': '20px', 'margin-top': '20px', 'display': 'inline-block'})

show_edge_options_radio = html.Div([html.P("Show edges:", style = {'display': 'inline-block'}),
    html.Div(dcc.RadioItems(['All', 'Positive', 'Negative'], id='radio-update-edge-options', value='All', inline=True, inputStyle={'margin-right': '10px', 'margin-left': '10px'}), style={'display': 'inline-block'})
], style={'margin-left': '20px', 'margin-top': '20px', 'display': 'inline-block'})

normalise_checkbox = html.Div([dcc.Checklist(['Normalise'], id='checkbox-update-normalise', value=['Normalise'], inline=True, inputStyle={'margin-right': '10px', 'margin-left': '10px'})],
                              style={'margin-left': '20px', 'margin-top': '20px', 'display': 'inline-block'})

update_button = html.Div([
    dbc.Button("Update", id='update-button', color="primary", className="mr-1", style = {'margin-left': '20px'})
], style = {'display': 'inline-block'})

options_div = html.Div([node_type_radio, edge_type_radio, colour_type_radio, colour_source_radio, show_edge_options_radio, normalise_checkbox, update_button])

graph = html.Div([cyto.Cytoscape(
        id='BiT',
        layout={'name': 'grid',
                'radius': 200},
        elements = edges+nodes,
        stylesheet = selector_node_classes + selector_edge_classes + default_stylesheet,
        style={'width': '80%', 'height': '780px', 'display': 'inline-block'},
    ),cyto.Cytoscape(id='BiT2',
        layout={'name': 'grid', 'columns': 1},
        elements = legend_nodes,
        stylesheet = selector_node_classes + legend_stylesheet,
        style={'width': '20%', 'height': '780px', 'display': 'inline-block'},)
])

weight_slider = html.Div([
    html.P("Weight threshold", id='weight-slider-output', style={'margin-left': '20px'}),
    dcc.RangeSlider(
        min = min_weight,
        max = max_weight + 1,
        step = 1,
        value = [min_weight, max_weight],
        marks = weight_bins,
        allowCross = False,
        id = 'weight-slider'
    )
])

tooltip = html.Div([
    html.P(id='tooltip')
], style={'margin-left': '10px'})

graph_tab = html.Div([layout_dropdown, group_dropdown, database_1_dropdown, team_1_dropdown, meeting_1_dropdown, database_2_dropdown, team_2_dropdown, meeting_2_dropdown, options_div, graph, weight_slider, tooltip])
app.layout = graph_tab

# @callback(
#         Output('tooltip', 'children'),
#         [Input('BiT', 'mouseoverNodeData'),
#         Input('BiT', 'mouseoverEdgeData')])
# def mouseover_node_data(hover_node_data, hover_edge_data):
#     if hover_node_data or hover_edge_data:
#         component = list(ctx.triggered_prop_ids.keys())[0]
#         text_input = ""
#         if 'Node' in component:
#             text_input = 'Node'
#         if 'Edge' in component:
#             text_input = 'Edge'
#         if text_input == 'Node':
#             return hover_node_data['id'] + ", with frequency: " + str(round(float(hover_node_data['freq']), 3)) + " " + hover_node_data['stats']
#         elif text_input == 'Edge':
#             if node_type == 'Behaviours':
#                 if edge_type == 'Frequency':
#                     return hover_edge_data['source'].upper() + " -> " + hover_edge_data['target'].upper() + ": " + str(round(hover_edge_data['original_weight'], 3)) + " " + hover_edge_data['stats']
#                 else:
#                     return hover_edge_data['source'].upper() + " -> " + hover_edge_data['target'].upper() + ": " + str(round(hover_edge_data['weight'], 3)) + " (" + str(round(hover_edge_data['weight'], 2)) + "%)" + " " + hover_edge_data['stats']
#             else:
#                 if edge_type == 'Frequency':
#                     return hover_edge_data['source'] + " -> " + hover_edge_data['target'] + ", " + hover_edge_data['behaviour'] + ": " + str(round(hover_edge_data['original_weight'], 3)) + " " + hover_edge_data['stats']
#                 else:
#                     return hover_edge_data['source'] + " -> " + hover_edge_data['target'] + ", " + hover_edge_data['behaviour'] + ": " + str(round(hover_edge_data['original_weight'], 3)) + " (" + str(round(hover_edge_data['weight'], 3)) + "%)" + " " + hover_edge_data['stats']
#
app.clientside_callback(
    """
    function(hover_node_data) {
        if (hover_node_data) {
            return hover_node_data['id'] + ", with frequency: " + hover_node_data['freq'] + " " + hover_node_data['stats'];
        }
    }
    """,
    Output('tooltip', 'children'),
    Input('BiT', 'mouseoverNodeData'),
    prevent_initial_call=True
)

# @callback(Output('BiT', 'elements', allow_duplicate=True),
#             Input('BiT', 'selectedNodeData'), prevent_initial_call=True)
# def select_node(selected_nodes):
#     if len(selected_nodes) == 0:
#         return get_original_edges(edge_data, node_type, colour_type, colour_source, edge_signs, edge_stats) + get_original_nodes(node_data, node_type, node_signs,colour_type, node_stats)
#     else:
#         current_edges = []
#         for node in selected_nodes:
#             for edge in get_original_edges(edge_data, node_type, colour_type, colour_source, edge_signs, edge_stats):
#                 if colour_source == 'Source':
#                     if edge['data']['source'] == node['id']:
#                         current_edges.append(edge)
#                 else:
#                     if edge['data']['target'] == node['id']:
#                         current_edges.append(edge)
#         return current_edges + get_original_nodes(node_data, node_type, node_signs, colour_type, node_stats)


# @callback(Output('BiT', 'layout'),
#               Input('dropdown-update-layout', 'value'))
# def update_layout(layout):
#     return {
#         'name': layout,
#         #'animate': True
#     }

# Convert to client-side callback
# app.clientside_callback(
#     """
#     function(layout) {
#         style = {
#             'name': layout
#         };
#         return style;
#     """,
#     Output('BiT', 'layout'),
#     [Input('dropdown-update-layout', 'value')]
# )

# @callback([Output('dropdown-update-team', 'options', allow_duplicate=True),
#         Output('dropdown-update-team-compare', 'options', allow_duplicate=True)],
#     Input('dropdown-update-group', 'value'),
#     prevent_initial_call=True)
# def update_group(value):
#     global group_by
#     group_by = value
#     return get_teams_for_group(database_1, value), get_teams_for_group(database_2, value)
#
# @callback(Output('dropdown-update-team', 'options'),
# Input('dropdown-update-database', 'value'),prevent_initial_call=True)
# def update_database(value):
#     global database_1
#     database_1 = value
#     return get_teams_for_group(value, group_by)
#
# @callback(Output('dropdown-update-team-compare', 'options'),
# Input('dropdown-update-database-compare', 'value'),prevent_initial_call=True)
# def update_database(value):
#     global database_2
#     database_2 = value
#     return get_teams_for_group(value, group_by)
#
# @callback(
#     [Output('BiT', 'elements'),
#     Output('weight-slider-output', 'children')],
#     Input('weight-slider', 'value'))
# def update_graph(selected_weight):
#     global nodes, edges
#     if selected_weight == min_weight:
#         nodes = get_original_nodes(node_data, node_type, node_signs, colour_type, node_stats)
#         edges = get_original_edges(edge_data, node_type, colour_type, colour_source, edge_signs, edge_stats)
#         return edges + nodes, "Weight threshold: " + str(selected_weight)
#     else:
#         # Remove edges with weight less than selected_weight
#         current_edges = []
#         for edge in get_original_edges(edge_data, node_type, colour_type, colour_source, edge_signs, edge_stats):
#             if show_edges == 'All':
#                 if edge_type == 'Probability':
#                     if selected_weight[0] <= edge['data']['weight'] <= selected_weight[1]:
#                         current_edges.append(edge)
#                 else:
#                     if selected_weight[0] <= edge['data']['weight'] <= selected_weight[1]:
#                         current_edges.append(edge)
#             else:
#                 if edge_signs[edge['data']['source'], edge['data']['target'], edge['data']['behaviour']] == show_edges.lower():
#                     if edge_type == 'Probability':
#                         if selected_weight[0] <= edge['data']['weight'] <= selected_weight[1]:
#                             current_edges.append(edge)
#                     else:
#                         if selected_weight[0] <= edge['data']['weight'] <= selected_weight[1]:
#                             current_edges.append(edge)
#         nodes = get_original_nodes(node_data, node_type, node_signs, colour_type, node_stats)
#         edges = current_edges
#         # Format selected_weight to display only 2 decimal places
#         return edges + nodes, "Weight threshold: " + str(round(selected_weight[0], 2)) + " - " + str(round(selected_weight[1], 2))
#
# @callback(Input('radio-update-nodes', 'value'),
#     prevent_initial_call=True)
# def update_team(value):
#     global node_type
#     node_type = value
#
# @callback(Input('radio-update-edges', 'value'),
#     prevent_initial_call=True)
# def update_edge_weight(value):
#     global edge_type
#     edge_type = value
#
# @callback(Input('radio-update-colour_type', 'value'),
#     prevent_initial_call=True)
# def update_colour_type(value):
#     global colour_type
#     colour_type = value
#
# @callback(Input('radio-update-colour-source', 'value'),
#     prevent_initial_call=True)
# def update_colour_source(value):
#     global colour_source
#     colour_source = value
#
# @callback(Output('BiT', 'elements', allow_duplicate=True),
#     Input('radio-update-edge-options', 'value'),
#     prevent_initial_call=True)
# def update_show_edges(value):
#     global show_edges
#     show_edges = value
#     global nodes, edges
#     if value == 'All':
#         nodes = get_original_nodes(node_data, node_type, node_signs, colour_type, node_stats)
#         edges = get_original_edges(edge_data, node_type, colour_type, colour_source, edge_signs, edge_stats)
#         return edges + nodes
#     else:
#         # Remove edges with weight less than selected_weight
#         current_edges = []
#         for edge in get_original_edges(edge_data, node_type, colour_type, colour_source, edge_signs, edge_stats):
#             if edge_signs[edge['data']['source'], edge['data']['target'], edge['data']['behaviour']] == value.lower():
#                 current_edges.append(edge)
#         nodes = get_original_nodes(node_data, node_type, node_signs, colour_type, node_stats)
#         edges = current_edges
#         return edges + nodes
#
# @callback(
#     [Output('dropdown-update-meeting', 'options')],
#     Input('dropdown-update-team', 'value'), prevent_initial_call=True)
# def update_meeting_display(value):
#     if value != '':
#         global team_1
#         team_1 = value
#         return [get_meetings_for_team(database_1, group_by, value)]
#     else:
#         return [[]]
#
# @callback([Output('dropdown-update-meeting-compare', 'options')],
#             Input('dropdown-update-team-compare', 'value'), prevent_initial_call=True)
# def update_meeting_display_compare(value):
#     if value != '':
#         global team_2
#         team_2 = value
#         return [get_meetings_for_team(database_2, group_by, value)]
#     else:
#         return [[]]
#
# @callback(Input('dropdown-update-meeting', 'value'), prevent_initial_call=True)
# def update_graph_with_meeting(value):
#     global meeting_1
#     if value is not None:
#         meeting_1 = value
#
# @callback(Input('dropdown-update-meeting-compare', 'value'), prevent_initial_call=True)
# def update_graph_with_meeting_compare(value):
#     global meeting_2
#     if value is not None:
#         meeting_2 = value
#
# @callback(Input('checkbox-update-normalise', 'value'), prevent_initial_call=True)
# def update_normalise(value):
#     global normalise
#     if 'Normalise' in value:
#         normalise = True
#     else:
#         normalise = False
#
# @callback([Output('BiT', 'elements', allow_duplicate=True),
#              Output('BiT', 'stylesheet'),
#              Output('weight-slider', 'min'),
#              Output('weight-slider', 'max'),
#              Output('weight-slider', 'marks'),
#              Output('weight-slider', 'value'),
#            Output('BiT2', 'elements', allow_duplicate=True),
#            Output('BiT2', 'stylesheet'),],
#             Input('update-button', 'n_clicks'),
#             prevent_initial_call=True)
# def update_graph_with_button(n_clicks):
#     global teams_1, meetings_1, teams_2, meetings_2, node_data, edge_data, nodes, edges, selector_node_classes, selector_edge_classes, min_weight, max_weight, weight_bins, node_signs, edge_signs, node_names, behaviours, node_stats, edge_stats
#     valid = check_valid_options(node_type, colour_type, team_1)
#     if valid:
#         teams_1, meetings_1, teams_2, meetings_2, node_data, edge_data, nodes, edges, selector_node_classes, selector_edge_classes, min_weight, max_weight, weight_bins, node_signs, edge_signs, node_names, behaviours, node_stats, edge_stats = load_dataset_comparison(
#         group_by, database_1, team_1, meeting_1, database_2, team_2, meeting_2, node_type, edge_type, colour_type, colour_source, normalise)
#         return edges + nodes, selector_node_classes + selector_edge_classes + default_stylesheet, min_weight, max_weight + 1, weight_bins, [min_weight, max_weight], get_legend_nodes(node_names, selector_node_classes, colour_type, behaviours), selector_node_classes + legend_stylesheet
#     else:
#         raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=False)
