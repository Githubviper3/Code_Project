import sqlite3
import ast

# Connect to the SQLite database
Conn = sqlite3.connect("Data.db")

# Create a cursor object
Cursor = Conn.cursor()

# Create a command for creating the users table
cmd = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    Coins INTEGER DEFAULT 0,
    Gems INTEGER DEFAULT 0,
    Deaths INTEGER DEFAULT 0,
    ScoreId TEXT,
    Pid TEXT,
    CheckpointId TEXT
);
"""

# Execute the SQL query to create the users table
Cursor.execute(cmd)

# Create Preferences table
create_preferences_table_query = """
CREATE TABLE IF NOT EXISTS Preferences (
    Pid TEXT PRIMARY KEY,
    Volume Text DEFAULT Empty,
    AspectRatio TEXT DEFAULT "[(640,360),pygame.SCALED]",
    Controls TEXT
);
"""

# Execute the SQL query to create the Preferences table
Cursor.execute(create_preferences_table_query)

# Create LevelData table
create_level_data_table_query = """
CREATE TABLE IF NOT EXISTS LevelData (
    CheckpointId TEXT PRIMARY KEY,
    CurrentLevel INTEGER DEFAULT 0,
    Checkpoint INTEGER DEFAULT 0
);
"""

# Execute the SQL query to create the LevelData table
Cursor.execute(create_level_data_table_query)

# Create Allscores table
create_all_scores_table_query = """
CREATE TABLE IF NOT EXISTS Allscores (
    ScoreId TEXT PRIMARY KEY,
    LevelScores BLOB Default "{}"

);
"""

# Execute the SQL query to create the Allscores table
Cursor.execute(create_all_scores_table_query)

def NewAccount(Values):
    with Conn:
        Cursor.execute("SELECT MAX(id) FROM users")
        tablesize = Cursor.fetchone()[0]
        maxsize = 1 if tablesize is None else int(tablesize)+1
        for i in ["S", "C", "P"]:
            Values.append(i + str(maxsize))
        Cursor.execute("INSERT INTO users (username, password, ScoreId, CheckpointId, Pid) VALUES (?, ?, ?, ?, ?)", (Values[0], Values[1], Values[2], Values[3], Values[4]))
        Cursor.execute("INSERT INTO Allscores (ScoreId) VALUES (?)", (Values[2],))
        Cursor.execute("INSERT INTO LevelData (CheckpointId) VALUES (?)", (Values[3],))
        Cursor.execute("INSERT INTO Preferences (Pid) VALUES (?)", (Values[4],))


def UsernameFind(Value):
    with Conn:
        Cursor.execute("SELECT id FROM users WHERE username == ?", (Value,))
        val = Cursor.fetchone()
        return val[0] if val else False

def GetFromUsername(Username,Value):
    with Conn:
        Cursor.execute(f"SELECT {Value} FROM users WHERE username == ?",(Username,))
        return Cursor.fetchone()
def PasswordFind(Value):
    with Conn:
        Cursor.execute("SELECT id FROM users WHERE password == ?", (Value,))
        val = Cursor.fetchone()
        return True if val else False

def Update_ScoreTable(id, attribute,level,score):
    with Conn:
        Cursor.execute(f"SELECT {attribute} FROM Allscores WHERE ScoreID = ?", (id,))
        stored = Cursor.fetchone()[0]
        stored = ast.literal_eval(stored)

        stored[level] = score
        Cursor.execute(f"UPDATE Allscores SET {attribute} = ? WHERE ScoreID = ?", (str(stored), id))


def Update_UserTable(id, attribute, value):
    with Conn:
        Cursor.execute(f"Update users Set ({attribute}) = {attribute} + (?) WHERE id = (?) ",(value,id))

def Alter_ScoreTable(id,scores = "{}"):
    with Conn:
        Cursor.execute(f"Update Allscores Set LevelScores  = ? Where ScoreID = ?",(scores,id))


def Get_ids(username):
    with Conn:
        Cursor.execute("SELECT id,ScoreId, CheckpointId, Pid FROM users WHERE username = ?", (username,))
        user_details = Cursor.fetchone()
        return user_details if user_details else [None]

def Get_UserName_from_id(id,attribute="ScoreId"):
    with Conn:

        Cursor.execute(f"""SELECT username FROM users WHERE {attribute} == '{id}'""")
        user_details = Cursor.fetchone()
        return user_details



def Top5(table,ID,attribute,order= "Desc"):
    with Conn:
        returned = []
        Cursor.execute(f"SELECT  {attribute} , {ID}  FROM {table} ORDER BY {attribute} {order} Limit 5;")
        vals = Cursor.fetchall()
        for val in vals:
            name=  Get_UserName_from_id(val[1],"id")[0]
            name = str(name)
            number = str(val[0])
            returned.append(f"Name: {name}, {attribute}: {number}")
        return returned

def getScores():
    Cursor.execute(f"Select * FROM Allscores")
    records = Cursor.fetchall()
    maxid = 0
    maxscore = 0
    perlevelmax = {}
    perlevelid = {}
    Highscores = []

    for record in records:
        id  = record[0]
        actualdict = ast.literal_eval(record[1])
        for key,value in actualdict.items():
            if value > maxscore:
                maxscore = max(actualdict.values())
                maxid = id
            if key in perlevelmax.keys():
                if value > perlevelmax[key]:
                    perlevelmax[key] = value
                    perlevelid[key] = id
            else:
                perlevelmax[key] = value
                perlevelid[key] = id

    for key in perlevelmax.keys():
        id  = perlevelid[key]
        Highscores.append((Get_UserName_from_id(id)[0], perlevelmax[key]))

    maxid = Get_UserName_from_id(maxid)[0]
    maxscores = (f"{maxid},{maxscore}")

    return (maxscores,Highscores)


