"""Fresh ladder snapshot: all external losses, recent controls, two replays/top team."""
import argparse
import csv
import gzip
import io
import json
import subprocess
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
import requests
from scrape_top_episodes import harvest

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes'


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--submission',type=int,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args(); out=args.output;out.mkdir(parents=True,exist_ok=True)
    session=requests.Session(); payloads={}
    cached=out/'api';cached.mkdir(exist_ok=True)
    def get(sub):
        if sub not in payloads:
            cache=cached/(str(sub)+'.json')
            if cache.exists():payloads[sub]=json.loads(cache.read_text(encoding='utf-8'))
            else:
                r=session.post(URL,json={'submissionId':int(sub)},timeout=60)
                r.raise_for_status();payloads[sub]=r.json()
                cache.write_text(json.dumps(payloads[sub],ensure_ascii=False),encoding='utf-8');time.sleep(1)
        return payloads[sub]
    lbdir=out/'leaderboard'
    if not (lbdir/'kaggriculture.zip').exists():
        subprocess.run(['kaggle','competitions','leaderboard','kaggriculture','-d','-p',str(lbdir)],check=True)
    with zipfile.ZipFile(lbdir/'kaggriculture.zip') as z:
        lb=list(csv.DictReader(io.TextIOWrapper(z.open(z.namelist()[0]),encoding='utf-8-sig')))
    top=lb[:10]; mappings={};ratings={}
    old=ROOT/'replays_top/discovery.json'
    if old.exists():
        d=json.loads(old.read_text());mappings.update(d['team_to_sub']);ratings.update(d['episode_rating'])
    own=get(args.submission);harvest(own,mappings,ratings)
    targets={x['TeamId'] for x in top};visited={args.submission}
    for _ in range(40):
        missing=targets-set(mappings)
        if not missing:break
        frontier=sorted(((ratings.get(t,0),v['sub']) for t,v in mappings.items() if v['sub'] not in visited),reverse=True)
        if not frontier:break
        sub=frontier[0][1];visited.add(sub);harvest(get(sub),mappings,ratings)
        print('discover',len(targets-set(mappings)),'unresolved',flush=True)
    metadata=[]; chosen={}
    def rows(payload,sub):
        names={str(t['id']):t.get('teamName','') for t in payload.get('teams',[])}
        result=[]
        for ep in payload.get('episodes',[]):
            agents=ep.get('agents',[])
            if ep.get('state')!='COMPLETED' or len(agents)!=2 or any(a.get('reward') is None for a in agents):continue
            mine=next((a for a in agents if a.get('submissionId')==sub),None)
            if mine is None:continue
            opp=next(a for a in agents if a is not mine)
            margin=mine['reward']-opp['reward']
            # Protobuf JSON omits the default seat zero; seat one includes index=1.
            result.append(dict(episode_id=ep['id'],seat=mine.get('index',0),end=ep.get('endTime'),
                submission=sub,opponent_submission=opp.get('submissionId'),
                team=names.get(str(mine.get('teamId')),'?'),opponent=names.get(str(opp.get('teamId')),'?'),
                ours=mine['reward'],theirs=opp['reward'],margin=margin,
                result='W' if margin>0 else 'L' if margin<0 else 'T',
                self_play=opp.get('submissionId')==sub,
                opponent_rating=opp.get('initialScore'),own_rating=mine.get('updatedScore')))
        return sorted(result,key=lambda r:r['end'] or '')
    ownrows=rows(own,args.submission)
    for row in ownrows:
        if row['result']=='L' and not row['self_play']:
            chosen.setdefault(row['episode_id'],[]).append(dict(row,cohort='submission_loss'))
    for row in [r for r in ownrows if r['result']=='W' and not r['self_play']][-8:]:
        chosen.setdefault(row['episode_id'],[]).append(dict(row,cohort='submission_win_control'))
    for team in top:
        tid=team['TeamId']
        if tid not in mappings:
            metadata.append(dict(team,status='unresolved'));continue
        payload=get(mappings[tid]['sub']);harvest(payload,mappings,ratings)
        sub=mappings[tid]['sub'];payload=get(sub)
        recent=rows(payload,sub)[-2:]
        metadata.append(dict(team,status='resolved',submission=sub,selected_episodes=[r['episode_id'] for r in recent]))
        for row in recent:chosen.setdefault(row['episode_id'],[]).append(dict(row,cohort='top10',rank=int(team['Rank'])))
    snapshot=dict(retrieved_at=datetime.now(timezone.utc).isoformat(),submission=args.submission,
                  episodes=ownrows,top10=metadata,replays=[])
    replaydir=out/'replays';replaydir.mkdir(exist_ok=True)
    for episode,labels in chosen.items():
        gz=replaydir/f'episode-{episode}-replay.json.gz'
        raw=replaydir/f'episode-{episode}-replay.json'
        if not gz.exists():
            subprocess.run(['kaggle','competitions','replay',str(episode),'-p',str(replaydir),'-q'],check=True)
            data=raw.read_bytes();json.loads(data)
            gz.write_bytes(gzip.compress(data,mtime=0))
            # Only remove the exact just-downloaded raw duplicate after verifying gzip.
            assert gzip.decompress(gz.read_bytes())==data
            assert raw.resolve().parent==replaydir.resolve()
            raw.unlink()
        snapshot['replays'].append(dict(path=gz.relative_to(out).as_posix(),labels=labels))
        (out/'manifest.json').write_text(json.dumps(snapshot,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print('downloaded',episode,len(snapshot['replays']),'/',len(chosen),flush=True)
    (out/'episode_service_snapshot.json').write_text(json.dumps(own,ensure_ascii=False),encoding='utf-8')
    print('COMPLETE',len(snapshot['replays']),flush=True)


if __name__=='__main__':main()
