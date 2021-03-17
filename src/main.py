import sys
import spotipy
import matplotlib.pyplot as plt


def authenticate(authentication_file="credentials.txt"):
    # authentication file must contain Client ID, Client Secret and Redirect URI
    # each one in a single line, according to the mentioned order
    with open(authentication_file, 'r') as auth_file:
        client_id = auth_file.readline().strip()
        client_secret = auth_file.readline().strip()
        redirect_uri = auth_file.readline().strip()
        scope = "playlist-read-collaborative"

        return spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, None, scope))


def get_playlist_stats(creds, playlist_id):
    tracks_batch = creds.playlist(playlist_id)["tracks"]

    tracks_counter = 0
    users_tracks = {}
    tracks = tracks_batch["items"]

    # retrieve the whole playlist in batches of 100 tracks
    while tracks_batch['next']:
        tracks_batch = creds.next(tracks_batch)
        tracks.extend(tracks_batch["items"])

    for track in tracks:
        user_id = track["added_by"]["id"]

        try:
            users_tracks[user_id] += 1
        except KeyError:
            users_tracks[user_id] = 1

        tracks_counter += 1

    beautified_users_tracks = []

    for user_id in list(users_tracks.keys()):
        name = creds.user(user_id)["display_name"]
        beautified_users_tracks.append([name, users_tracks[user_id]])

    return beautified_users_tracks, tracks_counter


if __name__ == '__main__':
    sp = authenticate()
    users, total_tracks = get_playlist_stats(sp, sys.argv[1])

    users = sorted(users, key=lambda x: x[1])

    labels = [user[0] for user in users]
    track_weight = 100 / total_tracks
    sizes = [user[1] * track_weight for user in users]

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, None, labels, autopct='%1.1f%%', pctdistance=0.9, startangle=90, radius=1.4)
    ax1.axis('equal')   # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.show()
