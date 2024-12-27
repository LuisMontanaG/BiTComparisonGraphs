window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        get_teams_for_group: async function (database, variable) {
            try {
                if (variable === 'Teams') {
                    const files = await read_files(database);
                    const teams = files[2];
                    return [teams.map(name => ({'label': name, 'value': name})), database];
                } else {
                    const names = await read_team_groups_from_file(database, variable);
                    return [names, database];
                }
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        },

        get_teams_for_group_both_databases: async function (variable, database1, database2) {
            try {
                if (variable === 'Teams') {
                    const files1 = await read_files(database1);
                    const files2 = await read_files(database2);
                    const teams1 = files1[2];
                    const teams2 = files2[2];
                    return [teams1.map(name => ({'label': name, 'value': name})), teams2.map(name => ({'label': name, 'value': name})), variable];
                } else {
                    const names1 = await read_team_groups_from_file(database1, variable);
                    const names2 = await read_team_groups_from_file(database2, variable);
                    return [names1, names2, variable];
                }
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        },

        get_meetings_for_team: async function (team, database, group_by) {
            try {
                const files = await read_files(database);
                var events = files[0];
                var meetings = []
                if (team === null) {
                    meetings.push('All');
                } else if (team === 'All') {
                    meetings = events.getColumn('sequenceId');
                    meetings = [...new Set(meetings)];
                    meetings = meetings.map(meeting => meeting.split('_')[0]);
                    meetings = [...new Set(meetings)];
                    meetings = meetings.filter(meeting => meeting !== "");
                    meetings.sort();
                    meetings.unshift('All');
                } else if (team.match(/\d+/g)) {
                    events = events.data.filter(event => event.sequenceId.split('_')[1] === team);
                    meetings = events.map(event => event.sequenceId.split('_')[0]);
                    meetings = [...new Set(meetings)];
                    meetings.sort();
                    meetings.unshift('All');
                } else {
                    const team_list = await read_teams_from_file(database, group_by, team);
                    events = events.data.filter(event => team_list.includes(event.sequenceId.split('_')[1]));
                    meetings = events.map(event => event.sequenceId.split('_')[0]);
                    meetings = [...new Set(meetings)];
                    meetings.sort();
                    meetings.unshift('All');
                }
                return [meetings.map(name => ({'label': name, 'value': name})), team];
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        },

        show_hide_edges: function (show, node_data, node_type, node_signs, colour_type, colour_source, edge_data, edge_signs) {
            edge_signs = new Map(edge_signs);
            // Change the keys of the map to string
            edge_signs = new Map([...edge_signs].map(([k, v]) => [JSON.stringify(k), v]));

            // Revert the keys of the map back to their original form
            // edge_signs = new Map([...edge_signs].map(([k, v]) => [JSON.parse(k), v]));

            var nodes = get_original_nodes(node_data, node_type, node_signs, colour_type);
            var edges = [];

            if (show.includes('All')) {
                edges = get_original_edges(edge_data, node_type, colour_type, colour_source, edge_signs)
            }
            else {
                show = show.toLowerCase()
                var current_edges = [];
                var original_edges = get_original_edges(edge_data, node_type, colour_type, colour_source, edge_signs);
                // Iterate over original edges and keep only the ones whose sign is equal to show value
                original_edges.forEach(edge => {
                    const sign = edge_signs.get(JSON.stringify([edge['data']['source'], edge['data']['target'], edge['data']['behaviour']]));
                    if (show.includes(sign)) {
                        current_edges.push(edge);
                    }
                });
                edges = current_edges;
            }
            // Append edges to nodes
            return nodes.concat(edges);
        }
    }
});

function get_original_nodes(node_data, node_type, node_signs, colour_type) {
    var original_nodes = [];
    if (node_type === 'Behaviours') {
        original_nodes = node_data.map((node, i) => {
            return {
                'data': {'id': node[0], 'label': node[1], 'freq': node[2], 'size': node[5]},
                'position': {'x': 20 * node[4], 'y': -20 * node[3]},
                'classes': "node" + node[0] + node_signs[i]
            }
        });
    }
    else {
        if (colour_type === 'Behaviours') {
            original_nodes = node_data.map((node, i) => {
                return {
                    'data': {'id': node[0], 'label': node[1], 'freq': node[2], 'size': node[5]},
                    'position': {'x': 20 * node[4], 'y': -20 * node[3]},
                    'classes': "nodeParticipant" + node_signs[i]
                }
            });
        }
        else {
            original_nodes = node_data.map((node, i) => {
                return {
                    'data': {'id': node[0], 'label': node[1], 'freq': node[2], 'size': node[5]},
                    'position': {'x': 20 * node[4], 'y': -20 * node[3]},
                    'classes': "node" + node[0] + node_signs[i]
                }
            });
        }
    }

    console.log(original_nodes);
    return original_nodes;
}

function get_original_edges(edge_data, node_type, colour_type, colour_source, edge_signs) {
    var original_edges = [];
    if (node_type === 'Behaviours') {
        if (colour_source === "Source") {
            original_edges = edge_data.map((edge, i) => {
                return {
                    'data': {'source': edge[0], 'target': edge[1], 'behaviour': edge[2], 'weight': edge[3], 'original_weight': edge[4]},
                    'classes': "edge" + edge[0]
                }
            });
        } else {
            original_edges = edge_data.map((edge, i) => {
                return {
                    'data': {'source': edge[0], 'target': edge[1], 'behaviour': edge[2], 'weight': edge[3], 'original_weight': edge[4]},
                    'classes': "edge" + edge[1]
                }
            });
        }
    } else {
        if (colour_type === 'Behaviours') {
            original_edges = edge_data.map((edge, i) => {
                return {
                    'data': {
                        'source': edge[0],
                        'target': edge[1],
                        'weight': edge[3],
                        'original_weight': edge[4],
                        'behaviour': edge[2]
                    },
                    'classes': "edge" + edge[2]
                }
            });
        } else {
            if (colour_source === "Source") {
                original_edges = edge_data.map((edge, i) => {
                    return {
                        'data': {
                            'source': edge[0],
                            'target': edge[1],
                            'weight': edge[3],
                            'original_weight': edge[4],
                            'behaviour': edge[2]
                        },
                        'classes': "edge" + edge[0]
                    }
                });
            } else {
                original_edges = edge_data.map((edge, i) => {
                    return {
                        'data': {
                            'source': edge[0],
                            'target': edge[1],
                            'weight': edge[3],
                            'original_weight': edge[4],
                            'behaviour': edge[2]
                        },
                        'classes': "edge" + edge[1]
                    }
                });
            }
        }
    }
    // Change the class of each edge depending on the sign of the weight (add word positive or negative)
    original_edges = original_edges.map((edge) => {
        edge['classes'] += edge_signs.get(JSON.stringify([edge['data']['source'], edge['data']['target'], edge['data']['behaviour']]));
        return edge;
    });
    return original_edges;
}

async function read_files(database) {
    const events_file = "https://raw.githubusercontent.com/LuisMontanaG/BiTComparisonGraphs/refs/heads/main/" + database + "/Events.csv"
    const entities_file = "https://raw.githubusercontent.com/LuisMontanaG/BiTComparisonGraphs/refs/heads/main/" + database + "/EntityAttributes.csv"

    const event_data = await fetch(events_file)
    const entity_data = await fetch(entities_file)
    const events_data = await event_data.text()
    const entities_data = await entity_data.text()

    // Split the data into rows
    const events_rows = events_data.split('\n')
    const entities_rows = entities_data.split('\n')

    // Create a DataFrame
    const events = new DataFrame(events_rows)
    const entities = new DataFrame(entities_rows)

    events.drop(['start', 'eventId'])
    events.removeRows('event', 'Online')

    entities.drop(['sequenceId'])

    // Get teams
    var teams = events.getColumn('sequenceId');
    teams = [...new Set(teams)];
    teams = teams.map(team => team.split('_')[1]);
    teams = [...new Set(teams)];
    teams = teams.filter(team => team !== undefined);
    teams.sort();
    teams.unshift('All');

    // Get behaviours
    var behaviours = events.getColumn('event');
    behaviours = [...new Set(behaviours)];
    behaviours = behaviours.filter(behaviour => behaviour !== 'Break' && behaviour !== undefined);

    // Get meetings
    var meetings = events.getColumn('sequenceId');
    meetings = [...new Set(meetings)];
    meetings = meetings.map(meeting => meeting.split('_')[0]);
    meetings = [...new Set(meetings)];
    meetings = meetings.filter(meeting => meeting !== "");
    meetings.sort();
    meetings.unshift('All');

    return [events, entities, teams, behaviours, meetings];
}

async function read_team_groups_from_file(database, variable) {
    const file = "https://raw.githubusercontent.com/LuisMontanaG/BiTComparisonGraphs/refs/heads/main/" + database + "/Variables.csv"
    const data = await fetch(file)
    const variables_data = await data.text()

    const lines = variables_data.split('\n')
    lines.pop();
    var is_variable = false;
    var names = [];

    lines.forEach(line => {
        if (line.includes('Attribute')) {
            is_variable = line.includes(variable);
        }
        if (is_variable) {
            if (line.startsWith('ids')) {
                names.push(line.split(':')[1].trim());
            }
        }
    });
    return names.map(name => ({'label': name, 'value': name}));
}

async function read_teams_from_file(database, variable, group_name) {
    const file = "https://raw.githubusercontent.com/LuisMontanaG/BiTComparisonGraphs/refs/heads/main/" + database + "/Variables.csv"
    const data = await fetch(file)
    const variables_data = await data.text()

    const lines = variables_data.split('\n')
    lines.pop();
    var is_variable = false;
    var is_group = false;
    var teams = [];
    lines.forEach(line => {
        if (line.includes('Attribute')) {
            is_variable = line.includes(variable);
            return;
        }
        if (is_variable) {
            if (line.includes(group_name)) {
                is_group = true;
                return;
            }
        }
        if (is_group) {
            teams = line.split(',');
            teams = teams.filter(team => team !== 'NA');
            teams = teams.map(team => team.split('_')[1].trim());
            is_group = false;
            is_variable = false;
        }
    });
    return teams
}

class DataFrame {
    // Constructor
    constructor(rows) {
        this.columns = rows[0].split(',');
        this.data = rows.slice(1).map(row => {
            let obj = {};
            const values = row.split(','); // Split each row by commas to get values
            this.columns.forEach((col, index) => {
                obj[col] = values[index];
            });
            return obj;
        });
    }

    // Method to get number of rows
    getNumRows() {
        return this.data.length;
    }

    // Method to get column names
    getColumns() {
        return this.columns;
    }

    // Method to get a column
    getColumn(columnName) {
        return this.data.map(row => row[columnName]);
    }

    // Method to drop columns
    drop(columnsToDrop) {
        this.data = this.data.map(row => {
            let newRow = { ...row };
            columnsToDrop.forEach(col => delete newRow[col]);
            return newRow;
        });
        this.columns = this.columns.filter(col => !columnsToDrop.includes(col));
    }

    // Method to remove rows where a specific column has a specific value
    removeRows(columnName, value) {
        this.data = this.data.filter(row => row[columnName] !== value);
    }

    // Method to display the DataFrame
    display() {
        console.table(this.data);
    }

    // Method to get a row by index
    getRow(index) {
        return this.data[index];
    }
}