from db import Database, print_result


class Transkoder:
    """Connect to Transkoder databases"""

    def __init__(self, connection_list: dict = None) -> None:
        self.db = Database(connection_list)

        res_all = self.db.execute_all("projects", "SELECT name FROM projects")
        self.projects = [[row[0] for row in res] for res in res_all]

    def __del__(self) -> None:
        if hasattr(self, "db"):
            return self.db.__del__()

    def execute_project(self, server_idx: int, project: str, query: str, args=tuple()):
        """Execute statement on a single project on a single server (Server_Idx is 0-indexed position of server in env file)"""
        return self.db.execute(server_idx, project, query, args)

    def execute_server(self, server_idx: int, query: str, args=tuple()):
        """Execute statement on all projects on a given server, returns a dict { project names: results }"""

        results = dict()
        for project in self.projects[server_idx]:
            results[project] = self.execute_project(server_idx, project, query, args)
        return results

    def execute_all_servers(self, query: str, args=tuple()) -> list[dict]:
        """Execute statement on all projects on all servers, returns an array containing one dict per server [{ project names: results }, ...]"""

        results = []
        for i in range(len(self.db.dbs)):
            results.append(self.execute_server(i, query, args))
        return results

    def list_settings(self, include_attribs=False, server_idx=0, project: str = None):
        """Returns a list of all possible setting names (Use the given project/server if provided)
        - If include_attribs is True: returns as dict { settingName: category (valueType) }
        - Otherwise returns a list of setting names as strings"""
        if not project:
            project = self.projects[server_idx][0]

        if include_attribs:
            rows = self.execute_project(
                server_idx, project, "SELECT param, category, type FROM settings"
            )
            return dict([[r[0], {"category": r[1], "value_type": r[2]}] for r in rows])

        rows = self.execute_project(server_idx, project, "SELECT param FROM settings")
        return [r[0] for r in rows]

    def get_setting(self, setting: str, server_idx: int = None, project: str = None):
        """Get a setting's value from one or more projects on one or more servers
        - If no server/projct given, returns a list of dicts per server [{ projectName: [[ settingValue ]] }]
        - If no project given, returns a dict { projectName: [[ settingValue ]] }
        - If a project/server are given, return [[ settingValue ]]"""

        query = ("SELECT value FROM settings WHERE param = %s", (setting,))

        if server_idx is None:
            return self.execute_all_servers(*query)
        if project is None:
            return self.execute_server(server_idx, *query)
        return self.execute_project(server_idx, project, *query)

    def delete_setting(self, setting: str, server_idx: int = None, project: str = None):
        """Delete a setting completely from one or more projects on one or more servers
        - If no server/projct given, deletes from all servers/projects
        - If no project given, deletes from all projects on server
        - If a project/server are given, deletes only from that project on that server
        """

        query = ("DELETE FROM settings WHERE param = %s", (setting,))

        if server_idx is None:
            return self.execute_all_servers(*query)
        if project is None:
            return self.execute_server(server_idx, *query)
        return self.execute_project(server_idx, project, *query)

    def set_setting(
        self, setting: str, value: str, server_idx: int = None, project: str = None
    ):
        """Update a setting's value across one or all projects and/or servers"""
        if server_idx is None:
            self.execute_all_servers(
                "UPDATE settings SET value = %s WHERE param = %s", (value, setting)
            )
        elif project is None:
            self.execute_server(
                server_idx,
                "UPDATE settings SET value = %s WHERE param = %s",
                (value, setting),
            )
        else:
            self.execute_project(
                server_idx,
                project,
                "UPDATE settings SET value = %s WHERE param = %s",
                (value, setting),
            )

    def upsert_setting(
        self,
        setting: str,
        value: str,
        category: str,
        value_type: str,
        server_idx: int = None,
        project: str = None,
    ):
        """Update a setting across one or all projects/servers, or insert if it doesn't exist
        - Category and Type required"""

        update_dict = {
            "param": setting,
            "value": value,
            "category": category,
            "type": value_type,
        }

        if server_idx is None:
            self.execute_all_servers(*Database.get_upsert("settings", update_dict))
        elif project is None:
            self.execute_server(
                server_idx, *Database.get_upsert("settings", update_dict)
            )
        else:
            self.execute_project(
                server_idx, project, *Database.get_upsert("settings", update_dict)
            )


if __name__ == "__main__":
    tku = Transkoder()
    print_result(
        tku.execute_all_servers(
            "SELECT value FROM settings WHERE param LIKE 'CMU_Default%'"
        )
    )
