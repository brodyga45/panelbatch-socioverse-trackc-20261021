"""Edited replay of real recorded CLI output, explicitly not a screen recording."""
import hashlib
import json
import subprocess
import tempfile
import textwrap
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
FONTROOT=Path('/Users/ignatignat/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/fonts')
TITLE=ImageFont.truetype(str(FONTROOT/'Ubuntu-B.ttf'),38)
BODY=ImageFont.truetype(str(FONTROOT/'Ubuntu-R.ttf'),25)
MONO=ImageFont.truetype(str(FONTROOT/'SourceCodePro-Regular.ttf'),22)
SMALL=ImageFont.truetype(str(FONTROOT/'Ubuntu-R.ttf'),18)


def main():
    trace=[json.loads(l)['text'] for l in (ROOT/'recorded-studies-v2/trace.jsonl').read_text().splitlines()]
    summary=json.loads((ROOT/'recorded-studies-v2/summary.json').read_text())
    assert summary['exact_parity']
    pilot=json.loads((ROOT/'bulk-study-probe-result.json').read_text())
    cold=json.loads((ROOT/'memory-probe-result.json').read_text())
    segments=[
        {'title':'PanelBatch: persistence without changed outcomes','seconds':8,'mono':False,
         'lines':['SocioVerse Track C local candidate','128 synthetic agents, six abstract decision rounds.','AI-assisted implementation; zero simulation LLM calls.','The next scenes replay actual recorded CLI output.']},
        {'title':'1 / Create a new study and validate its inputs','seconds':13,'mono':True,
         'lines':trace[2:5]+['','New fork; the official reference stays unchanged.','Typed population, environment and simulation artifacts.']},
        {'title':'2 / Run the official baseline and retain its data','seconds':14,'mono':True,
         'lines':[l for l in trace if l.startswith('baseline step=')]+['']+[l for l in trace if l.startswith('COMPLETE baseline')]},
        {'title':'3 / Select the compatible writer; run the same study','seconds':14,'mono':True,
         'lines':[l for l in trace if 'store_ref=panel_batch.arrow' in l]+[l for l in trace if l.startswith('bulk     step=')]+[l for l in trace if l.startswith('COMPLETE bulk')]},
        {'title':'4 / Compare all persisted values','seconds':12,'mono':False,
         'lines':['Exact sorted panel / metrics / events parity: PASS','896 rows per study; 768 rule decisions per writer.','Databases, Parquet exports and metric histories retained.','The source trace and data fingerprint are in the package.','This 128-agent demo is not a speed estimate.']},
        {'title':'5 / Separate performance evidence and its limits','seconds':17,'mono':False,
         'lines':[f"Pilot: 2,048 agents, six steps, three seeds: {pilot['cases'][1]['median_full_run_speedup']:.2f}x median full-run ratio.",
                  f"Separate fresh processes: {cold['results'][0]['sim_run_seconds']:.3f}s baseline / {cold['results'][1]['sim_run_seconds']:.3f}s bulk.",
                  'Peak RSS: 160.1 MB baseline / 179.5 MB bulk.',
                  'Local host only. No model-bound or memory-saving claim.',
                  'See raw timings, correctness checks and the working report.']},
        {'title':'Reproduce, inspect, then judge','seconds':10,'mono':False,
         'lines':['Original component + pinned public upstream + raw data.','One-command numerical reproduction and four compatibility checks.','No real-person dataset or API credentials are included.','Local draft: no entry, prize or payment is claimed.']},
    ]
    output=ROOT/'PanelBatch-recorded-demo-v1.mp4'
    with tempfile.TemporaryDirectory(prefix='codex-panelbatch-video-') as tmp:
        tmp=Path(tmp)
        concat=[]
        for i,seg in enumerate(segments):
            im=Image.new('RGB',(1280,720),'#101b2b');draw=ImageDraw.Draw(im)
            draw.rectangle((0,0,1280,8),fill='#60d6b2')
            for j,line in enumerate(textwrap.wrap(seg['title'],width=55)):
                draw.text((50,42+j*47),line,font=TITLE,fill='#f3f7fb')
            y=155
            for line in seg['lines']:
                font=MONO if seg['mono'] else BODY
                maxwidth=86 if seg['mono'] else 90
                for wrapped in textwrap.wrap(line,width=maxwidth) or ['']:
                    draw.text((52,y),wrapped,font=font,fill='#cee2ef')
                    y+=30 if seg['mono'] else 39
            assert y < 625,(i,y)
            draw.line((50,645,1230,645),fill='#395069',width=1)
            draw.text((50,665),'Edited CLI replay from actual local logs; frames held for reading. No live screen capture.',font=SMALL,fill='#a7bdd0')
            path=tmp/f'scene-{i}.png';im.save(path)
            im.save(ROOT/f'demo-scene-{i}.png')
            concat.extend([f"file '{path}'",f"duration {seg['seconds']}"])
        concat.append(f"file '{path}'")
        (tmp/'frames.txt').write_text('\n'.join(concat)+'\n')
        duration=sum(s['seconds'] for s in segments)
        subprocess.run(['/opt/homebrew/bin/ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(tmp/'frames.txt'),'-t',str(duration),'-r','12','-c:v','libx264','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],check=True)
    probe=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,r_frame_rate','-of','json',str(output)],text=True))
    manifest={'created_at':datetime.now(timezone.utc).isoformat(),'file':output.name,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'probe':probe,'segments':segments,
              'capture_provenance':'Actual demo_study.py output recorded in trace.jsonl; edited text-card replay, not screen capture. Timing remapped for readability. No generated screenshots, synthetic speech, fake UI or fabricated study results.',
              'source_trace':'recorded-studies-v2/trace.jsonl','source_data':'recorded-studies-v2/summary.json','simulation_LLM_calls':0,'cash_spend':0,'public_video_URL':None,
              'visual_QA':'pending'}
    (ROOT/'demo-video-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'seconds':duration,'size':output.stat().st_size,'sha256':manifest['sha256']}))


if __name__=='__main__':
    main()
