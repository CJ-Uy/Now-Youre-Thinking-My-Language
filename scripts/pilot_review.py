"""Render the selected, still-unreviewed candidates using the round-1 review layout."""
import hashlib
import html
import re
from pathlib import Path

from research import core


def label(row):
    return f"{row['id'].removeprefix('train-')}-{'E' if row['pool'] == 'english' else 'M'}{row['candidate']}"


def render(problems, groups, pool, template, prereview, ledger):
    original = {p['id']: p for p in problems}
    picks = {}
    for strategy in ('shortest', 'feedback'):
        for row in groups[pool + '-' + strategy]:
            identity = label(row)
            if identity in picks and picks[identity]['row'] != row:
                raise ValueError(f'Conflicting selected candidate: {identity}')
            picks.setdefault(identity, {'row': row, 'strategies': []})['strategies'].append(strategy)
    hints = {r['candidate']: r for r in prereview}
    pending = {ref for r in ledger if r.get('scope') == 'note' for ref in r.get('refers_to', [])}
    decisions = {label(r): r for r in ledger if r.get('scope') == 'candidate'
                 and r.get('arm') == 'opus55' and r['decision_id'] in pending}
    prior_priority = template.split('<h2>Check these first</h2>', 1)[1].split('<h2>train-', 1)[0]
    priority = set(re.findall(r'\d+-[ME]\d+', prior_priority))
    notes = {}
    for identity, pick in picks.items():
        parts = ['Selected by: ' + ', '.join(pick['strategies']) + '.']
        hint = hints.get(identity) if pool == 'multilingual' else None
        if hint:
            parts.append(f"Fable AI pre-review (not human): {hint['decision']}. {hint['reason']}")
            if hint.get('note_disagreement'):
                parts.append('AI disagreement: ' + hint['note_disagreement'])
            if hint['decision'] != 'A' or hint.get('disagrees_with_note'):
                priority.add(identity)
        if identity in decisions:
            decision = decisions[identity]
            parts.append(f"{decision['decision_id']}: earlier {decision['decision']} from an English gloss; needs bilingual confirmation. {decision['rationale']}")
            priority.add(identity)
        notes[identity] = ' '.join(parts)
    priority &= set(picks)
    instructions = re.search(r'<ol>.*?</ol>', template, flags=re.S)
    if instructions is None:
        raise ValueError('Round-1 A/R/U instructions are missing')
    instructions = instructions.group().replace('For each candidate (M0 to M3)', 'For each selected candidate')
    title = 'English' if pool == 'english' else 'Mandarin / mixed-language'
    escape = html.escape
    parts = ['<!doctype html><meta charset="utf-8">', f'<h1>Opus 5.5 pilot {title} review</h1>',
             '<p><b>Reviewer:</b> ________ <b>Date started:</b> ________ <b>Date finished:</b> ________</p>',
             f'<p>Review all {len(picks)} unique selected rewrites. These are unreviewed screening inputs, not approved training data. '
             'Every rewrite must preserve the meaning of the original solution. No decision is prefilled.</p>',
             '<h2>How to review</h2>', instructions, '<h2>Check these first</h2>',
             '<p>' + (escape(', '.join(sorted(priority))) if priority else 'No earlier flags apply to these selected picks.') + '</p>']
    question_order = {p['id']: i for i, p in enumerate(problems)}
    ids = {p['row']['id'] for p in picks.values()}
    ids = sorted(ids, key=lambda q: (not any(k in priority and p['row']['id'] == q for k, p in picks.items()), question_order[q]))
    for question_id in ids:
        source = original[question_id]
        parts += [f'<h2>{escape(question_id)}</h2>', '<p><b>Question:</b> ' + escape(source['question']) + '</p>',
                  '<p><b>Original solution:</b><br>' + escape(source['solution']).replace('\n', '<br>') + '</p>',
                  '<table border="1" cellpadding="4"><tr><th>Candidate</th><th>Steps (text, then the fixed equation)</th>'
                  '<th>Notes (AI hints; earlier decisions need confirmation)</th><th>Decision: A / R / U, and reason</th></tr>']
        selected = [(identity, p) for identity, p in picks.items() if p['row']['id'] == question_id]
        for identity, pick in sorted(selected, key=lambda item: (item[0] not in priority, item[0])):
            row = pick['row']
            steps = '<br>'.join(f"<b>Step {i}:</b> {escape(s['text'])} [{escape(s['equation'])}]"
                                for i, s in enumerate(row['steps'], 1))
            parts.append(f"<tr><td>{escape(identity)}</td><td>{steps}<br><b>Answer:</b> {escape(row['answer'])}</td>"
                         f"<td>{escape(notes[identity])}</td><td></td></tr>")
        parts.append('</table>')
    return '\n'.join(parts) + '\n', sorted(picks)


def prepare(root, conditions, output):
    root, conditions, output = Path(root), Path(conditions), Path(output)
    review = root / 'artifacts/teacher-comparison/chat-export-round1/human-review-20261024'
    template = (review / 'mandarin-review-sheet.html').read_text(encoding='utf-8')
    problems = core.read_jsonl(root / 'artifacts/data/pilot/train.jsonl')
    groups = {name: core.read_jsonl(conditions / (name + '.jsonl')) for name in core.CONDITIONS}
    expected = [r['id'] for r in groups['original']]
    if not expected or any([r['id'] for r in rows] != expected for rows in groups.values()):
        raise ValueError('Review sheets require five conditions with identical ordered IDs')
    hints = core.read_jsonl(review / 'ai-prereview-fable52-20261110.jsonl')
    ledger = core.read_jsonl(review / 'decisions.jsonl')
    output.mkdir(parents=True, exist_ok=False)
    manifest = {'purpose': 'human review required; no inferred decisions', 'sheets': {}}
    for pool, filename in [('english', 'english-review-sheet.html'), ('multilingual', 'mandarin-review-sheet.html')]:
        text, picks = render(problems, groups, pool, template, hints, ledger)
        path = output / filename
        path.write_text(text, encoding='utf-8', newline='\n')
        manifest['sheets'][pool] = {'file': filename, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'picks': picks}
    manifest['conditions_manifest_sha256'] = hashlib.sha256((conditions / 'manifest.json').read_bytes()).hexdigest()
    manifest['ledger_sha256'] = hashlib.sha256((review / 'decisions.jsonl').read_bytes()).hexdigest()
    core.write_json(output / 'manifest.json', manifest)
    return manifest
