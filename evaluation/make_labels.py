from pathlib import Path
import pandas as pd
p=Path(__file__).parent
t=pd.read_csv(p.parent/'data/raw/tickets.csv')
s=t[t.created_at.ge('2026-04-01') & t.created_at.lt('2026-07-01')].sample(n=60,random_state=928)[['ticket_id','customer_message']].reset_index(drop=True)
# Assigned by the coding assistant from customer opening text before viewing model outputs.
labels=['Billing & Payments','Billing & Payments','Billing & Payments','Connectivity','Charging & Battery','Order Changes','Charging & Battery','Delivery & Shipping','Charging & Battery','Delivery & Shipping','Order Changes','Hardware / needs review','Order Changes','Audio Quality','Delivery & Shipping','Product Enquiry','Billing & Payments','Returns & Refunds','Returns & Refunds','Connectivity','Charging & Battery','Returns & Refunds','Returns & Refunds','Warranty & Repair','Order Changes','Returns & Refunds','Delivery & Shipping','Delivery & Shipping','Delivery & Shipping','Returns & Refunds','Connectivity','Billing & Payments','Returns & Refunds','Product Enquiry','Delivery & Shipping','Delivery & Shipping','Delivery & Shipping','Hardware / needs review','Charging & Battery','Account & Login','Delivery & Shipping','Charging & Battery','Delivery & Shipping','Delivery & Shipping','Delivery & Shipping','Billing & Payments','Account & Login','Charging & Battery','Connectivity','Connectivity','Returns & Refunds','Connectivity','Audio Quality','Account & Login','Audio Quality','Returns & Refunds','Order Changes','Order Changes','Connectivity','App & Firmware']
assert len(s)==len(labels)
s['expected']=labels
s['annotation_source']='AI-assisted manual interpretation of opening message; no model predictions or closing-note labels shown'
s['rationale']='Primary customer issue; requested refund/replacement is an outcome, not necessarily the issue category'
s.loc[[11,37],'rationale']='Unresponsive touchscreen does not fit defined classes. Model should abstain, not force a category.'
s.loc[26,'rationale']='Delivery interpretation from context is plausible but terse; human review preferred.'
s.loc[54,'rationale']='Meetings-only audio issue inferred; ambiguity between microphone/audio and connection remains.'
s[['ticket_id','expected','annotation_source','rationale']].to_csv(p/'labels.csv',index=False)
