import sqlite3
import requests
import os
import datetime
from tqdm import tqdm
from jinja2 import Environment, FileSystemLoader

###
# Database setup
###

# Absolute path to current directory
path = os.path.dirname(__file__)

# Setup DB connection
con = sqlite3.connect(os.path.join(path, "skyfellows.db"))
con.execute('pragma journal_mode=wal')

# Setup DB for easy insertion of dictionaries
con.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))

cur = con.cursor()

# Function: Helper to remove any None values from dict (borrowed from: https://stackoverflow.com/a/44528129)
def clean_dict(raw_dict):
    return { k: ('' if v is None else v) for k, v in raw_dict.items() }

def cleanDB():

    # Drop table if it exists
    drop_sql = """
        DROP TABLE IF EXISTS follows;
    """

    # Create a fresh table
    setup_sql = """
        CREATE TABLE IF NOT EXISTS follows (
            did TEXT,
            handle TEXT,
            displayName TEXT,
            description TEXT,
            avatar TEXT,
            followersCount INTEGER,
            followsCount INTEGER,
            postsCount INTEGER,
            lastActive TEXT
        );
    """

    # Execute and clean everything up
    cur.execute(drop_sql)
    cur.execute(setup_sql)
    con.commit()
    con.execute("VACUUM")

###
# Bluesky authentication 
###

# Bluesky login credentials
BLUESKY_HANDLE = "example.bsky.social"
BLUESKY_APP_PASSWORD = "xxxx-xxxx-xxxx-xxxx"

# Get JWT auth token
resp = requests.post(
    "https://bsky.social/xrpc/com.atproto.server.createSession",
    json={"identifier": BLUESKY_HANDLE, "password": BLUESKY_APP_PASSWORD},
)
resp.raise_for_status()
session = resp.json()
auth_token = session["accessJwt"]

# Set logged in user DID based on response
auth_did = session["did"]

###
# Bluesky API queries
###

# Get list of follows
def getFollows():

    cleanDB()

    print("Database ready. Fetching list of follows.")

    # Follows cursor
    followscursor = None

    # Loop until break
    while(True):

        # Set up the request
        getfollows_url = "https://bsky.social/xrpc/app.bsky.graph.getFollows"
        params = {
            'actor': auth_did,
            'limit': 100
        }

        # If cursor is set, add to params
        if followscursor:
            params['cursor'] = followscursor

        # Make the GET request
        response = requests.get(url = getfollows_url, params = params, headers = {'Authorization': 'Bearer ' + auth_token, 'Connection': 'close'}, timeout=10)

        # Loop through follows
        for follow in response.json()['follows']:

            # Description is optional - replace with empty string to avoid KeyError
            if 'description' not in follow:
                follow['description'] = ""

            # Construct the basic profile
            profile = {
                'did': follow['did'],
                'handle': follow['handle'],
                'displayName': follow['displayName'],
                'description': follow['description'],
                'avatar': follow['avatar']
            }

            # Insert profile into DB
            query = "INSERT INTO follows " + str(tuple(profile.keys())) + " values" + str(tuple(clean_dict(profile).values())) + ";"
            cur.execute(query)
            con.commit()

        # If cursor key present (ie. more items exist), set and continue looping
        if 'cursor' in response.json():
            followscursor = response.json()['cursor']

        # No cursor key, break loop
        else:
            break

# Hydrate each profile with with counts
def getProfiles():

    # Grab the list of DIDs from the follows table
    sql = "SELECT did FROM follows;"
    res = cur.execute(sql)
    follows = res.fetchall()

    # Loop through each DID
    for did in tqdm(follows, total=len(follows), desc="Fetching Profile Counts:"):

        # Set up the request
        getprofile_url = "https://bsky.social/xrpc/app.bsky.actor.getProfile"
        params = {
            'actor': did['did']
        }

        # Make the GET request
        response = requests.get(url = getprofile_url, params = params, headers = {'Authorization': 'Bearer ' + auth_token, 'Connection': 'close'}, timeout=10)

        profile = response.json()

        # Construct counts to be added to profile
        counts = {
            'followersCount': int(profile['followersCount']),
            'followsCount': int(profile['followsCount']),
            'postsCount': int(profile['postsCount']),
            'did': str(did['did'])
        }

        # Insert profile into DB
        query = """
            UPDATE follows 
            SET followersCount =:followersCount, followsCount =:followsCount, postsCount =:postsCount
            WHERE did =:did;
        """

        cur.execute(query, counts)
        con.commit()

# Hydrate last post date for each profile
def getPosts():

    # Grab the list of DIDs from the follows table
    sql = "SELECT did FROM follows;"
    res = cur.execute(sql)
    follows = res.fetchall()

    # Loop through each DID
    for did in tqdm(follows, total=len(follows), desc="Fetching Latest Posts:"):

        # Set up the request
        getposts_url = "https://bsky.social/xrpc/app.bsky.feed.getAuthorFeed"
        params = {
            'actor': did['did'],
            'limit': 1
        }

        # Make the GET request
        response = requests.get(url = getposts_url, params = params, headers = {'Authorization': 'Bearer ' + auth_token, 'Connection': 'close'}, timeout=10)

        if len(response.json()['feed']) > 0:

            lastActive = response.json()['feed'][0]['post']['record']['createdAt']

            # Insert lastActive timestamp into DB
            query = """
                UPDATE follows 
                SET lastActive =:lastActive
                WHERE did =:did;
            """

            cur.execute(query, { 'lastActive': str(lastActive), 'did': str(did['did']) })
            con.commit()

###
# Build the HTML page
###

def buildPage():

    # Fetch entire table from database
    res = cur.execute("SELECT * FROM follows ORDER BY lastActive DESC;")
    follows = res.fetchall()

    # Jinja2 template config
    env = Environment(loader=FileSystemLoader(path))

    # Use template.html file
    template = env.get_template("template.html")

    # Render page
    html = template.render(follows=follows)

    # Write page to filesystem
    html_file = open(os.path.join(path, "follows.html"), "w")
    html_file.write(html)
    html_file.close()

    print("Page built: follows.html")

###
# Run it all - TBD: Make this more elegant, add error-checking, etc. 
###

getFollows()
getProfiles()
getPosts()
buildPage()