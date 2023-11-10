# Transkoder DB Batch Tool

Run bulk updates on Transkoder's MySQL DB

---

### Getting Started

Create a copy of `example.env` named `.env`, setting connection string of form `user:pass@Transkoder.IP`.

To connect to multiple servers at once, seperate connection strings with a comma.

For Transkoder servers, you must be on the same subnet as them.

To expose the Transkoders to remote systems edit `C:\xampp\mysql\bin\my.ini` on the Transkoder server modifying the below lines, then restart SQL server:

```ini
# Change here for bind listening
bind-address = "*"
#bind-address = ::1   # for ipv6
```

See examples in `main.py` for using the Transkoder class to batch-execute SQL statements

---

### Understanding Transkoder's Database

To explore the database in *PHP My Admin* console, enter this address in a browser:
`http://[TranskoderIP]/phpmyadmin`

The main tables in the Transkoder database are:
- **`projects`**: Contains all of the global data including project entries.
- ***Project Names***: One database per project, containing all project-specific data.
- **`tk_db` table**: Contains all data for Transkoder's basckground renderer.

To add a project, you must add an entry in the `projects` table within the `projects` database, and also add a database matching the `name` value in the `projects` table. I recommend copying another project as a starting point. To remove a project, simply remove from both the `projects` table and drop the database named after the project. (Note the ***ProjectVersion*** field should equal `V9` for 2022, `V10` for 2023, *etc*)

To update a **setting**, it must be updated in each project that requires it, the helper methods here can be used for that. To update global or default setting (I'm still not sure exactly which settings are global), I recommend starting the software, creating a new project without any template, changing the setting(s) required, then under *File* select *Save Default Settings*. After this the new project can be deleted.

If you wish to **Upsert** a setting (Update if it exists or insert if it doesn't), the database will also require the setting's `category` and `type`. These can be found in the database directly, or by using the list_settings() function with include_attribs=True.


