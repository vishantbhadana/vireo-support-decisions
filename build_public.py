"""Build the Pages demo from explicit aggregate fields; never copy source records."""
from pathlib import Path
import json
import re
import shutil

ROOT = Path(__file__).resolve().parent


def pick(obj, keys):
    return {key: obj[key] for key in keys}


def public_analysis(source):
    columns = {
        'monthly': ('month', 'inferred_category', 'tickets'),
        'intake': ('month', 'assigned_team', 'tickets'),
        'resolver': ('month', 'resolving_team', 'tickets'),
        'teams': ('assigned_team', 'tickets', 'breaches', 'transfers', 'median_resolution_hours', 'csat', 'csat_responses'),
        'shifts': ('channel', 'creation_shift', 'tickets', 'breaches', 'credit_inr'),
    }
    result = {name: [pick(row, keys) for row in source[name]] for name, keys in columns.items()}
    result.update(pick(source, ('period_total', 'q2_total')))
    result['goal'] = pick(source['goal'], (
        'eligible_tickets', 'billing_tickets', 'observed_transfers',
        'observed_transfer_cost_inr', 'quarterly_capacity_value_inr'))
    audit = source['audit']
    result['audit'] = pick(audit, ('outside_window', 'legacy_negative_resolution_before_fix', 'negative_resolution_after_fix'))
    result['audit']['model'] = pick(audit['model'], ('review_rows', 'weak_label_agreement', 'temporal_unseen_test_rows'))
    result['audit']['same_order_refund_replacement_q2'] = pick(audit['same_order_refund_replacement_q2'], ('orders',))
    result['audit']['goodwill_over_cap_q2'] = pick(audit['goodwill_over_cap_q2'], ('tickets',))
    evaluation = source.get('evaluation') or json.loads((ROOT/'evaluation/report.json').read_text())
    result['evaluation'] = pick(evaluation, ('sample_size', 'overall_category_accuracy', 'review_count'))
    return result


def replace_once(text, old, new):
    assert text.count(old) == 1, f'Template changed: {old[:80]}'
    return text.replace(old, new, 1)


def build():
    data = public_analysis(json.loads((ROOT/'output/analysis.json').read_text()))
    encoded = json.dumps(data, separators=(',', ':'), allow_nan=False)
    # Allowlist above is the primary privacy control. These guard against regressions.
    for word in ('ticket_id', 'order_id', 'customer_id', 'agent_id', 'customer_message', 'agent_notes', 'raw_sha256', 'failures'):
        assert f'"{word}"' not in encoded
    assert not re.search(r'\b(?:TK|VR)-\d+', encoded)
    for key in ('monthly', 'intake'):
        assert sum(row['tickets'] for row in data[key]) == data['period_total']

    html = (ROOT/'web/index.html').read_text()
    html = replace_once(html, '<title>Vireo | Support decisions</title>', '<title>Vireo | Public support decisions demo</title><meta name="description" content="A support-ticket analysis dashboard, measurable routing pilot and private, in-browser sample classifier."><meta name="referrer" content="no-referrer">')
    html = replace_once(html, 'Offline analysis, visible uncertainty.', 'Public demonstration · visible uncertainty.')
    banner = '''<section style="margin-top:0"><b>Public demo</b><p>Explore the real aggregate findings below. The interactive classifier uses made-up examples only; the original data-trained classifier and its evaluation are reproducible in the local review package.</p><div class="row"><a href="https://github.com/vishantbhadana/vireo-support-decisions">Code &amp; setup</a><a href="https://github.com/vishantbhadana/vireo-support-decisions/blob/main/docs/memo-priya.md">One-page recommendation</a><a href="https://drive.google.com/file/d/1VP9CjSd_xVwCxyG2zL_TCapyK6uIWuaD/view?usp=sharing">Original app walkthrough</a></div></section>'''
    html = replace_once(html, '<main><div id="loading">Loading local analysis…</div>', '<main>'+banner+'<div id="loading">Loading analysis snapshot…</div>')
    html = replace_once(html, '<h2>Try an opening message</h2>', '<h2>Try a sample complaint</h2>')
    html = replace_once(html, 'A small local text model. No closing notes or legacy tags are input features; obvious IDs and emails are removed. Nothing is sent externally or saved.', 'This demonstration model learned only from made-up examples. It is separate from the original model evaluated below. Your text is processed in this browser and is not sent to a server or saved. Use example text, not personal information.')
    html = replace_once(html, '<h2>Evidence and data quality</h2>', '<h2>Original analysis: evidence and data quality</h2>')
    html = replace_once(html, 'matched a blind AI-assisted annotation audit; ', 'matched the original local model’s blind AI-assisted annotation audit; ')
    html = replace_once(html, 'Not independently human-validated.</p>', 'Not independently human-validated. This result does not measure the public demo classifier.</p>')
    html = replace_once(html, '<details><summary>Sample of uncertain classifications (first 100)</summary><div id="reviews" class="scroll"></div></details>', '<p class="muted">Individual tickets, order details and customer messages are excluded from this public site.</p>')
    review_js = "el('reviews').innerHTML=table(d.review,[['ticket_id','Ticket'],['category','Original tag'],['prediction','Model suggestion'],['score','Score']]);"
    html = replace_once(html, review_js, '')
    html = replace_once(html, "fetch('/analysis.json')", "fetch('./analysis-public.json')")
    html = replace_once(html, 'Analysis unavailable. Run python analyze.py and restart the app.', 'The analysis snapshot could not load. Please reload the page or use the linked repository.')
    html = replace_once(html, '<script>\nlet D;', '<script src="./demo-model.js"></script>\n<script>\nconst demoReady=VireoDemo.load("./demo-model.json");\nlet D;')
    old = "const r=await fetch('/classify',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:el('message').value})});if(!r.ok)throw Error('Please enter a valid message');const d=await r.json();"
    html = replace_once(html, old, "await demoReady;const d=await VireoDemo.classify(el('message').value);")
    html = replace_once(html, 'Classifying locally…', 'Checking the sample in your browser…')
    html = replace_once(html, 'Suggested for assisted triage', 'Sample-model suggestion')
    html = replace_once(html, 'Model labels derived from explicit closing-note issue phrases; separately annotated audit details in evaluation/report.json. No third-party scripts, analytics or fonts.', 'Original model labels came from closing notes; audit details can be regenerated privately from the supplied pack. Public interactive model uses only authored synthetic examples. No third-party scripts, analytics or fonts. Hosting: GitHub Pages.')
    dest = ROOT/'docs'
    (dest/'index.html').write_text(html)
    (dest/'analysis-public.json').write_text(encoded+'\n')
    (dest/'.nojekyll').write_text('')
    shutil.copyfile(ROOT/'public-demo/model.js', dest/'demo-model.js')
    shutil.copyfile(ROOT/'public-demo/model.json', dest/'demo-model.json')
    print('Public demo built: explicit aggregates + synthetic-only model; no raw customer records.')


if __name__ == '__main__':
    build()
