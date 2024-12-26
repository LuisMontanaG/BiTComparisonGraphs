window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        get_teams_for_group: async function (database, variable) {
            try {
                const file = "https://raw.githubusercontent.com/LuisMontanaG/BiTComparisonGraphs/refs/heads/main/" + database + "/Events.csv"
                // const response = await fetch(file, {
                //     method: 'GET',
                //     mode: 'no-cors',
                //     headers: {
                //         'Content-Type': 'text/csv;charset=UTF-8'
                //     }
                // });
                const response = await fetch(file);
                const data = await response.text();
                console.log("si")
                console.log(data)
                return data;
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }
    }
});