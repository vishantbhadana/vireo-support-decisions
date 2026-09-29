"""Regression checks against the privately supplied pack; no data bundled."""
import unittest, tempfile, shutil
from pathlib import Path
import pandas as pd
from analyze import ROOT,load_data,run,note_label,clean_text

@unittest.skipUnless((ROOT/'data/raw/tickets.csv').exists(),'Supply the assignment pack first')
class PackChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.model,cls.t,cls.d=run()
 def test_reconciled_denominators(self):
  a=self.d['audit'];self.assertEqual(a['raw_rows']-a['outside_window'],len(self.t))
  self.assertEqual(sum(r['tickets'] for r in self.d['monthly']),len(self.t))
  self.assertEqual(sum(r['tickets'] for r in self.d['intake']),len(self.t))
  self.assertEqual(sum(r['tickets'] for r in self.d['resolver']),int(self.t.completed.sum()))
 def test_timezone_and_missingness(self):
  self.assertEqual(self.d['audit']['negative_resolution_after_fix'],0)
  self.assertTrue(self.t[self.t.source_system.eq('legacy_fd')].transfers.isna().all())
  self.assertEqual(self.d['audit']['unmatched_roster_closed'],0)
 def test_business_case_independently(self):
  rows=pd.read_csv(ROOT/'output/routing-opportunity.csv')
  self.assertTrue(rows.assigned_team.eq('Billing').all());self.assertTrue(rows.transfers.gt(0).all())
  self.assertEqual(rows.transfers.sum()*305/2,self.d['goal']['quarterly_capacity_value_inr'])
  self.assertEqual(self.d['goal']['quarterly_capacity_value_inr'],20435)
 def test_same_order_policy_regression(self):
  # Same-ticket flags miss these cross-ticket orders; protect against reverting that bug.
  self.assertEqual(self.d['audit']['refund_plus_replacement_q2']['tickets'],0)
  self.assertEqual(self.d['audit']['same_order_refund_replacement_q2']['orders'],15)
 def test_duplicate_id_rejected(self):
  with tempfile.TemporaryDirectory() as directory:
   p=Path(directory);raw=pd.read_csv(ROOT/'data/raw/tickets.csv').head(2)
   pd.concat([raw,raw.head(1)]).to_csv(p/'tickets.csv',index=False)
   with self.assertRaisesRegex(ValueError,'Duplicate ticket IDs'):load_data(p)
 def test_invalid_date_rejected(self):
  with tempfile.TemporaryDirectory() as directory:
   p=Path(directory);raw=pd.read_csv(ROOT/'data/raw/tickets.csv').head(2);raw.loc[0,'created_at']='not a date'
   raw.to_csv(p/'tickets.csv',index=False)
   with self.assertRaisesRegex(ValueError,'Invalid creation'):load_data(p)

class LabelChecks(unittest.TestCase):
 def test_ambiguous_closing_note_has_no_training_label(self):
  self.assertIsNone(note_label('Invoice corrected; refund pending'))
 def test_identifier_not_feature(self):
  self.assertEqual(clean_text('Where is VR123456? a@b.com'),'where is ?')
if __name__=='__main__':unittest.main()
