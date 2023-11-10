from dotenv import load_dotenv
from os import getenv
import mysql.connector


def print_result(execute_result, line_start=""):
    """Helper function to display a SELECT/GET result in human readable format"""

    def print_item(value, line_start: str):
        if type(value) is list:
            for item in value:
                if type(item) in (list, tuple):
                    print(f'{line_start}- {", ".join(str(i) for i in item)}')
                else:
                    print(f"{line_start}- {str(item)}")

        elif type(value) is dict:
            for key, val in value.items():
                if type(val) not in (list, tuple):
                    print(f"{line_start}{key}:\t{str(val)}")
                elif len(val) == 1:
                    print(f'{line_start}{key}:\t{", ".join(val[0])}')
                else:
                    print(f"{line_start}{key}:")
                    for v in val:
                        print(f'{line_start}\t- {", ".join(v)}')

        else:
            print(f"{line_start}{str(value)}")

    if type(execute_result) is list and type(execute_result[0]) in (dict, list):
        for server, result in enumerate(execute_result):
            print(f"{line_start}Entry {server+1}:")
            print_item(result, line_start + "  ")
    else:
        print_item(execute_result, line_start)


class Database:
    """Connect to multiple databases given via a connection list or a .env file"""

    @staticmethod
    def get_connections():
        """Load mySql connection parameters from .env variable"""
        load_dotenv()

        sqladdr = getenv("sql_addr")
        if not sqladdr:
            raise Exception("Missing MySQL server sqladdress in .env file. See README.")

        connects = []
        for addr in sqladdr.split(","):
            addr = addr.strip()

            connection = dict()
            addr, connection["host"] = addr.split("@")
            connection["user"], connection["password"] = addr.split(":")

            if connection.get("host"):
                connects.append(connection)

        if not connects:
            raise Exception("No valid MySQL server addresses were provided.")
        return connects

    @staticmethod
    def get_upsert(table: str, update_dict: dict[str, str]):
        """Generate [ upsert statement, [parameter list] ], using a dict of { column: value }"""

        keys = "`, `".join(update_dict.keys())
        vals = ", ".join("%s" for _ in update_dict.keys())
        sets = ", ".join(f"`{k}` = %s" for k in update_dict.keys())

        return [
            f"INSERT INTO `{table}` (`{keys}`) VALUES ({vals}) ON DUPLICATE KEY UPDATE {sets};",
            list(update_dict.values()) + list(update_dict.values()),
        ]

    def __init__(self, connection_list: dict = None) -> None:
        if not connection_list:
            connection_list = Database.get_connections()
        self.dbs = [mysql.connector.connect(**db) for db in connection_list]

    def __del__(self) -> None:
        if hasattr(self, "dbs"):
            for db in self.dbs:
                db.close()

    def execute(self, server_idx: int, dbname: str, query: str, args=tuple()):
        """Execute query statement on specified server (Server_Idx is 0-indexed position of server in env file)"""

        cursor = self.dbs[server_idx].cursor()
        cursor.execute(f"USE `{dbname}`")
        cursor.execute(query, args)
        return [list(row) for row in cursor]

    def execute_all(self, dbname: str, query: str, args=tuple()):
        """Execute query statement on all servers"""

        results = []
        for i in range(len(self.dbs)):
            results.append(self.execute(i, dbname, query, args))
        return results

    def upsert(
        self, server_idx: int, dbname: str, table: str, update_dict: dict[str, str]
    ):
        """Update database row if it exists, otherwise insert it on specified server, db & table
        - server_idx is 0-indexed position of server in env file
        - update_dict should be of format { column: value }"""

        return self.execute(
            server_idx, dbname, *Database.get_upsert(table, update_dict)
        )

    def upsert_all(self, dbname: str, table: str, update_dict: dict[str, str]):
        """Update database row if it exists, otherwise insert it into db & table on all servers
        - update_dict should be of format { column: value }"""

        return self.execute_all(dbname, *Database.get_upsert(table, update_dict))
