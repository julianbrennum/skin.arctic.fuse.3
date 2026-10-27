# Open a TV show at the season you're up to.
#
#   RunScript(special://skin/extras/scripts/jb_nextup.py,<tvshowid>)
#
# Picks the episode you're midway through, else the first unwatched episode after
# the last one you played, else the first unwatched episode, else the last played
# one. Opens that season's episode list; Kodi's "select first unwatched item"
# setting (videolibrary.tvshowsselectfirstunwatcheditem = always) then focuses it.
import json
import sys

import xbmc


def rpc(method, **params):
    req = {'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}
    return json.loads(xbmc.executeJSONRPC(json.dumps(req))).get('result') or {}


def pick(episodes):
    eps = [e for e in episodes if e['season'] > 0] or episodes
    if not eps:
        return None
    resumed = [e for e in eps if e['resume']['position'] > 0 and not e['playcount']]
    if resumed:
        return max(resumed, key=lambda e: e['lastplayed'])
    played = [i for i, e in enumerate(eps) if e['lastplayed']]
    if played:
        last = max(played, key=lambda i: eps[i]['lastplayed'])
        after = next((e for e in eps[last + 1:] if not e['playcount']), None)
        if after:
            return after
    return next((e for e in eps if not e['playcount']), None) or (eps[played[-1]] if played else eps[0])


def main():
    try:
        tvshowid = int(sys.argv[1])
    except (IndexError, ValueError):
        return
    episodes = rpc('VideoLibrary.GetEpisodes', tvshowid=tvshowid,
                   properties=['season', 'episode', 'playcount', 'lastplayed', 'resume'],
                   sort={'method': 'episode', 'order': 'ascending'}).get('episodes') or []
    episodes.sort(key=lambda e: (e['season'], e['episode']))
    ep = pick(episodes)
    path = f'videodb://tvshows/titles/{tvshowid}/' + (f'{ep["season"]}/' if ep else '')
    xbmc.executebuiltin(f'ActivateWindow(Videos,{path},return)')


main()
