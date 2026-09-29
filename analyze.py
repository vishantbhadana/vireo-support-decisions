"""Vireo: reproducible local analysis. Raw files remain unchanged."""
from pathlib import Path
import re, json, time, hashlib, argparse
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

ROOT=Path(__file__).resolve().parent
COST={'chat':210,'email':260,'voice':520,'social':240}
SLA={'chat':15,'voice':120,'social':240,'email':480}
RULES={
'Delivery & Shipping':r'dlvry|delivery delay|order not delivered|ord not delivered|shipment not|lost in transit|wrong item|wrong variant|incorrect product|unit received damaged|transit damage',
'Returns & Refunds':r'refund pending|rfnd pending|refund not credited|rfnd not credited|reverse pickup|reverse pkp|pickup missed|return pickup',
'Billing & Payments':r'double charge|charged twice|duplicate payment|invoice|gstin|amount deducted without|failed ord after payment|payment failed|payment failure',
'Charging & Battery':r'battery|no power|no charge|not charging|not taking charge|bud no charge|charging issue',
'Connectivity':r'pairing failure|unable to pair|not discoverable|connection drop|connection dropping|connection droping|disconnect|connect to wifi|wi-fi|wifi issue',
'Audio Quality':r'audio distortion|no audio|one side|left side silent|single side audio|mic issue|mic not working|low mic|sound quality',
'App & Firmware':r'app crash|app not opening|firmware update failed|update hang|update stuck|app issue',
'Account & Login':r'login issue|unable to log in|otp|account locked',
'Product Enquiry':r'product enquiry|compatibility query|pre-sales query|spec sheet',
'Warranty & Repair':r'repair status|rma status|wty claim status|warranty claim status',
'Order Changes':r'cancellation request|ord cancellation|order cancellation|address update',
}
def note_label(s):
 s=str(s).lower(); hits=[k for k,v in RULES.items() if re.search(v,s)]
 return hits[0] if len(hits)==1 else None

def clean_text(s):
 s=str(s).lower().replace('\\n',' ')
 s=re.sub(r'\b(?:vr|tk)[- ]?\d+\b',' ',s)
 s=re.sub(r'\b[\w.+-]+@[\w.-]+\b',' ',s)
 s=re.sub(r'\d+',' ',s)
 return re.sub(r'\s+',' ',s).strip()

def load_data(data_dir):
 t=pd.read_csv(data_dir/'tickets.csv',keep_default_na=True)
 audit={'raw_rows':len(t),'raw_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data_dir.glob('*.csv')}}
 for col in ['created_at','first_response_at','resolved_at']:t[col]=pd.to_datetime(t[col],errors='coerce')
 audit['exact_contact_duplicates']=int(t.duplicated(['customer_id','created_at','customer_message']).sum())
 audit['duplicate_ticket_ids']=int(t.ticket_id.duplicated().sum())
 # No fuzzy deduplication: repeat contacts must not be silently deleted.
 if audit['duplicate_ticket_ids']: raise ValueError('Duplicate ticket IDs require explicit reconciliation before analysis')
 audit['invalid_creation_timestamps']=int(t.created_at.isna().sum())
 if audit['invalid_creation_timestamps']:raise ValueError('Invalid creation timestamps require reconciliation')
 audit['missing_first_response']=int(t.first_response_at.isna().sum())
 audit['negative_response_intervals']=int((t.first_response_at<t.created_at).sum())
 audit['outside_window']=int((~t.created_at.between('2025-01-01','2026-06-30 23:59:59')).sum())
 audit['legacy_negative_resolution_before_fix']=int(((t.resolved_at<t.first_response_at)&t.source_system.eq('legacy_fd')).sum())
 legacy=t.source_system.eq('legacy_fd')
 t.loc[legacy,'resolved_at']=t.loc[legacy,'resolved_at']+pd.Timedelta(hours=5,minutes=30)
 audit['negative_resolution_after_fix']=int((t.resolved_at<t.first_response_at).sum())
 audit['legacy_money_decision']='No scale conversion: sampled explicit note amounts match stored amounts; native unit unspecified. Legacy money excluded from primary business case.'
 t=t[t.created_at.between('2025-01-01','2026-06-30 23:59:59')].copy()
 a=pd.read_csv(data_dir/'agents.csv');a['from_date']=pd.to_datetime(a.from_date);a['to_date']=pd.to_datetime(a.to_date)
 # Resolve roster assignment at resolution; open records have no confirmed resolver attribution.
 roster=[]
 assignments={key:list(group.itertuples()) for key,group in a.groupby('agent_id')}
 for r in t.itertuples():
  matches=[x for x in assignments.get(r.agent_id,[]) if pd.notna(r.resolved_at) and x.from_date<=r.resolved_at and (pd.isna(x.to_date) or r.resolved_at<x.to_date+pd.Timedelta(days=1))]
  roster.append([matches[0].team,matches[0].site,matches[0].shift,matches[0].tier] if len(matches)==1 else [None]*4)
 t[['resolving_team','site','shift','tier']]=roster
 audit['unmatched_roster_closed']=int((t.status.isin(['resolved','closed'])&t.resolving_team.isna()).sum())
 t['response_minutes']=(t.first_response_at-t.created_at).dt.total_seconds()/60
 t['breach']=t.response_minutes>t.channel.map(SLA)
 t['completed']=t.status.isin(['resolved','closed'])
 t['credit_incurred']=t.breach&t.completed
 t['resolution_hours']=(t.resolved_at-t.created_at).dt.total_seconds()/3600
 t['elapsed_handle_hours']=(t.resolved_at-t.first_response_at).dt.total_seconds()/3600
 t['month']=t.created_at.dt.strftime('%Y-%m')
 t['creation_shift']=t.created_at.dt.hour.map(lambda h:'Night' if h>=22 or h<6 else ('Morning' if h<14 else 'Day'))
 t['note_label']=t.agent_notes.map(note_label)
 t['model_text']=t.customer_message.map(clean_text)
 audit['missing_transfers']=int(t.transfers.isna().sum())
 audit['missing_csat']=int(t.csat_score.isna().sum())
 audit['window_rows']=len(t)
 return t,a,audit

def train(t,audit):
 # Group by normalized opening text to avoid exact-template leakage across time split.
 candidates=t[t.note_label.notna() & (t.created_at<'2026-04-01')].copy()
 # The separately annotated audit sample is never used in training or threshold tuning.
 held=ROOT/'evaluation/labels.csv'
 excluded=set(pd.read_csv(held).ticket_id) if held.exists() else set()
 candidates=candidates[~candidates.ticket_id.isin(excluded)]
 model=Pipeline([('tfidf',TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),min_df=2,max_features=35000,sublinear_tf=True)),('clf',LogisticRegression(max_iter=500,C=4,class_weight='balanced',random_state=42))])
 model.fit(candidates.model_text,candidates.note_label)
 prob=model.predict_proba(t.model_text); t['prediction']=model.classes_[prob.argmax(axis=1)];t['score']=prob.max(axis=1)
 t['review']=t.score<.70
 t['inferred_category']=np.where(t.review,'Needs review',t.prediction)
 unseen=t[(t.created_at>='2026-04-01')&t.note_label.notna()&~t.model_text.isin(set(candidates.model_text))]
 audit['model']={'type':'Character TF-IDF + logistic regression, opening message only','training_rows':len(candidates),'weak_label_coverage':int(t.note_label.notna().sum()),'temporal_unseen_test_rows':len(unseen),'weak_label_agreement':float(accuracy_score(unseen.note_label,unseen.prediction)),'review_threshold':.70,'review_rows':int(t.review.sum()),'warning':'Agreement with note-derived weak labels is not independently measured accuracy. Confidence is an uncalibrated model score.'}
 return model,t

def records(df):return json.loads(df.to_json(orient='records',date_format='iso'))

def run(data_dir=ROOT/'data/raw'):
 start=time.perf_counter();t,a,audit=load_data(data_dir);model,t=train(t,audit)
 out=ROOT/'output';out.mkdir(exist_ok=True)
 q=t[t.created_at>='2026-04-01'].copy()
 # Conservative routing opportunity: Billing intake, explicit logistics issue in closing note,
 # classifier agrees from opening text, observed transfers and current-system records only.
 target=q[(q.assigned_team=='Billing')&(q.note_label=='Delivery & Shipping')&(q.prediction=='Delivery & Shipping')&(~q.review)&(q.transfers>0)]
 transfers=float(target.transfers.sum());quarter_cost=transfers*305
 goal={'period':'2026 Q2','billing_tickets':int((q.assigned_team=='Billing').sum()),'eligible_tickets':len(target),'observed_transfers':transfers,'observed_transfer_cost_inr':quarter_cost,'pilot_reduction':.5,'quarterly_capacity_value_inr':quarter_cost*.5,'annualized_capacity_value_inr':quarter_cost*.5*4,'definition':'Halve observed transfers in high-confidence Billing-to-Logistics misroutes. Capacity value, not guaranteed cash savings; no SLA or repeat-contact benefits added.'}
 monthly=t.groupby(['month','inferred_category']).size().reset_index(name='tickets')
 by_intake=t.groupby(['month','assigned_team']).size().reset_index(name='tickets')
 by_resolver=t[t.completed].groupby(['month','resolving_team']).size().reset_index(name='tickets')
 team=q.groupby('assigned_team').agg(tickets=('ticket_id','size'),breaches=('breach','sum'),credit_tickets=('credit_incurred','sum'),transfers=('transfers','sum'),median_resolution_hours=('resolution_hours','median'),csat=('csat_score','mean'),csat_responses=('csat_score','count')).reset_index()
 for column in ['median_resolution_hours','csat']:team[column]=team[column].round(2)
 shift=q.groupby(['channel','creation_shift']).agg(tickets=('ticket_id','size'),breaches=('breach','sum'),credit_tickets=('credit_incurred','sum')).reset_index();shift['credit_inr']=shift.credit_tickets*350
 products=pd.read_csv(data_dir/'products.csv');orders=pd.read_csv(data_dir/'orders.csv')
 # Exact order join only. Never multiply rows through ambiguous customer+SKU fallback.
 q=q.merge(orders[['order_id','customer_id','sku','lot_code','order_value_inr']],on='order_id',how='left',validate='many_to_one',suffixes=('','_order')).merge(products[['sku','unit_cost_inr']],left_on='product_sku',right_on='sku',how='left',validate='many_to_one',suffixes=('','_product'))
 valid=q.customer_id.eq(q.customer_id_order)&q.product_sku.eq(q.sku)
 conflict=q[(q.refund_amount_inr>0)&q.replacement_issued.eq('Y')].copy();conflict['replacement_cost']=conflict.unit_cost_inr+340
 audit['order_link_missing_q2']=int(q.order_value_inr.isna().sum());audit['order_link_mismatch_q2']=int((q.order_value_inr.notna()&~valid).sum())
 # Policy is per ORDER, not per ticket: separate contacts can carry each side.
 linked=q[valid & q.order_id.notna()].copy()
 order_flags=linked.groupby('order_id').agg(tickets=('ticket_id','size'),refund_inr=('refund_amount_inr','sum'),replacement_count=('replacement_issued',lambda s:int(s.eq('Y').sum())))
 order_flags=order_flags[(order_flags.refund_inr>0)&(order_flags.replacement_count>0)].reset_index()
 order_flags.to_csv(out/'same-order-refund-replacement.csv',index=False)
 goodwill=q[q.refund_reason_code.eq('GW-OTHER') & q.refund_amount_inr.gt(500)]
 goodwill[['ticket_id','order_id','refund_amount_inr']].to_csv(out/'goodwill-review.csv',index=False)
 audit['same_order_refund_replacement_q2']={'orders':len(order_flags),'refund_inr':float(order_flags.refund_inr.sum()),'scope':'Exact matched orders, Q2 contacts only; may miss cross-quarter events; fulfilment evidence needed.'}
 audit['goodwill_over_cap_q2']={'tickets':len(goodwill),'refund_inr':float(goodwill.refund_amount_inr.sum()),'warning':'Reason code is not proof of true goodwill. Validate coding and approval with Finance.'}
 # Repeat contacts are a proxy; issues, not just customers, must match. Exclude right-censored index tickets.
 repeats=[]
 for _,g in t[~t.review].groupby(['customer_id','product_sku','prediction']):
  g=g.sort_values('created_at');previous=[]
  for row in g.itertuples():
   eligible=[r for r in previous if pd.notna(r.resolved_at) and r.resolved_at<row.created_at<=r.resolved_at+pd.Timedelta(days=30)]
   if eligible:repeats.append({'ticket_id':row.ticket_id,'prior_ticket_id':eligible[-1].ticket_id,'created_at':str(row.created_at),'channel_cost':COST[row.channel]})
   previous.append(row)
 audit['repeat_contact_proxy_count']=len(repeats);audit['repeat_warning']='Same customer + SKU + predicted category within 30 days of prior resolution is only an issue proxy. No repeat savings claimed; last 30 days are censored for FCR.'
 audit['refund_plus_replacement_q2']={'tickets':len(conflict),'flagged_refund_inr':float(conflict.refund_amount_inr.sum()),'flagged_replacement_cost_inr':float(conflict.replacement_cost.sum()),'warning':'Flags for Finance review, not proven leakage. Check same-order evidence, actual fulfilment and legitimate exceptions; do not add both amounts as savings.'}
 exportcols=['ticket_id','created_at','month','channel','category','assigned_team','resolving_team','prediction','score','review','note_label','transfers','breach','credit_incurred','resolution_hours','source_system']
 t[exportcols].to_csv(out/'ticket-results.csv',index=False)
 monthly.to_csv(out/'monthly-categories.csv',index=False);by_intake.to_csv(out/'monthly-intake-teams.csv',index=False);by_resolver.to_csv(out/'monthly-resolving-teams.csv',index=False)
 target[exportcols].to_csv(out/'routing-opportunity.csv',index=False);conflict[['ticket_id','order_id','refund_amount_inr','replacement_cost','refund_reason_code']].to_csv(out/'refund-review.csv',index=False)
 pd.DataFrame(repeats).to_csv(out/'repeat-contact-proxy.csv',index=False)
 audit['analysis_seconds']=round(time.perf_counter()-start,3)
 data={'audit':audit,'goal':goal,'monthly':records(monthly),'intake':records(by_intake),'resolver':records(by_resolver),'teams':records(team),'shifts':records(shift),'evaluation':json.loads((ROOT/'evaluation/report.json').read_text()) if (ROOT/'evaluation/report.json').exists() else None,'review':records(t[t.review][exportcols].head(100)),'routing':records(target[exportcols]),'period_total':len(t),'q2_total':len(q)}
 (out/'analysis.json').write_text(json.dumps(data,indent=2,allow_nan=False))
 print(json.dumps({'audit':audit,'goal':goal,'teams':records(team),'shifts':records(shift)},indent=2))
 return model,t,data

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--data-dir',type=Path,default=ROOT/'data/raw');args=parser.parse_args();run(args.data_dir)
