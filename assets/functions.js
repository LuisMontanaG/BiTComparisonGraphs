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
                    return [teams1.map(name => ({'label': name, 'value': name})), teams2.map(name => ({'label': name, 'value': name}))];
                } else {
                    const names1 = await read_team_groups_from_file(database1, variable);
                    const names2 = await read_team_groups_from_file(database2, variable);
                    return [names1, names2];
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
                    console.log(meetings);
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
                return meetings.map(name => ({'label': name, 'value': name}));
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }
    }
});

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