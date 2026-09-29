from pathlib import Path
import json
import pandas as pd
from analyze import ROOT
p=ROOT/'evaluation';labels=pd.read_csv(p/'labels.csv');results=pd.read_csv(ROOT/'output/ticket-results.csv')
e=labels.merge(results[['ticket_id','prediction','score','review','category']],on='ticket_id',validate='one_to_one')
e['correct']=e.prediction==e.expected
e['safe_outcome']=e.correct | (e.expected.eq('Hardware / needs review') & e.review)
accepted=e[~e.review]
report={'sample_size':len(e),'sampling':'60 Q2 tickets; uniform without replacement; seed928; opening messages labeled before viewing predictions','annotator':'Coding assistant, not independent human/domain-expert gold labels','blind_to':'model output, original bot tag, agent closing note during labeling','exclusion':'All sample IDs excluded from training; all are in temporal holdout','overall_category_accuracy':float(e.correct.mean()),'safe_outcome_rate':float(e.safe_outcome.mean()),'accepted_count':len(accepted),'accepted_accuracy':float(accepted.correct.mean()),'review_count':int(e.review.sum()),'original_tag_accuracy':float((e.category==e.expected).mean()),'failures':json.loads(e[~e.correct][['ticket_id','expected','prediction','score','review','rationale']].to_json(orient='records')),'limitations':'Small AI-annotated audit, not human-validated accuracy. Limited class coverage, synthetic-like templates, no calibration study; production deployment needs a human-labeled pilot. Hardware screen cases are outside the taxonomy.'}
(p/'report.json').write_text(json.dumps(report,indent=2));e.to_csv(p/'audit-results.csv',index=False);print(json.dumps(report,indent=2))
