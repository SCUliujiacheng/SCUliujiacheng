"""Regenerate the eight-week public repository activity plate with GitHub CLI."""
from datetime import date, datetime, time, timedelta, timezone
from html import escape
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OWNER = 'SCUliujiacheng'
REPOS = [('album-atlas', 'Album Atlas'), ('cutline-lab', 'Cutline'),
         ('split-warden', 'Split Warden'), ('caption-splice', 'Caption Splice'),
         ('agent-reliability-lab', 'Agent Reliability Lab'), ('evidence-rag-bench', 'Evidence RAG Bench')]
end = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.now(timezone.utc).date()
start = end - timedelta(days=end.weekday() + 49)
since = datetime.combine(start, time.min, timezone.utc).isoformat().replace('+00:00','Z')
until = datetime.combine(end, time.max, timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def counts(repo):
    endpoint = f'repos/{OWNER}/{repo}/commits?per_page=100&since={since}&until={until}'
    dates = subprocess.check_output(['gh', 'api', '--paginate', endpoint, '--jq', '.[].commit.committer.date'], text=True)
    weeks = [0] * 8
    for item in dates.splitlines():
        day = datetime.fromisoformat(item.replace('Z', '+00:00')).astimezone(timezone.utc).date()
        if start <= day <= end:
            weeks[(day - start).days // 7] += 1
    return weeks

rows = [(label,counts(repo)) for repo,label in REPOS]
height = 160 + 37 * len(rows)
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="{height}" viewBox="0 0 1050 {height}" role="img" aria-labelledby="title desc">',
         '<title id="title">Weekly commits in selected public repositories</title>']
parts.append('<desc id="desc">' + escape(f'From {start} to {end} UTC. ' + '. '.join(label + ': ' + ', '.join(map(str, values)) for label,values in rows)) + '</desc>')
parts.append(f'<rect width="1050" height="{height}" fill="#f4f0e7"/>')
def txt(x, y, value, size, color, anchor='start', family='Georgia,serif', extra=''):
    parts.append(f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-family="{family}" text-anchor="{anchor}" {extra}>{escape(str(value))}</text>')
def rule(y, color):
    parts.append(f'<path d="M30 {y}H1020" stroke="{color}"/>')
txt(30,47,'Carnet d’atelier',32,'#293739',extra='font-style="italic"')
txt(1020,43,'WEEKLY COMMITS   /   ' + end.strftime('%d %b %Y').upper(),15,'#455956','end','monospace')
rule(62,'#767f75')
txt(32,90,'REPOSITORY',13,'#596863',family='monospace',extra='letter-spacing="1.2"')
for col in range(8):
    txt(340+col*81,90,(start+timedelta(weeks=col)).strftime('%d %b').upper(),13,'#596863','middle','monospace')
txt(990,90,'TOTAL',13,'#596863','middle','monospace')
for i,(name,values) in enumerate(rows):
    y=121+37*i
    txt(32,y,name,19,'#273b40')
    for col,value in enumerate(values):
        x=340+81*col
        if value:
            txt(x,y,value,17,'#294c56','middle','monospace',extra='font-weight="bold"')
        else:
            txt(x,y,'·',17,'#929888','middle','monospace')
    txt(990,y,sum(values),17,'#914a37','middle','monospace')
    rule(y+12,'#d9d6ca')
txt(32,height-28,'Selected public repositories, default branches.',16,'#4e5e58',extra='font-style="italic"')
txt(1020,height-29,'UTC',13,'#596863','end','monospace')
parts.append('</svg>')
(ROOT/'assets'/'workshop-log.svg').write_text('\n'.join(parts),encoding='utf-8')
print(rows)
