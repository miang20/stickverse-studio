import unittest, tempfile, json
from pathlib import Path
from scene_planner import tokens, score, plan
class PlannerTests(unittest.TestCase):
    def test_stopwords(self):
        self.assertEqual(tokens("The SCAM was online"),{"scam","online"})
    def test_match(self):
        self.assertGreater(score("Crypto fraud exploded",{"title":"Crypto fraud footage"}),score("Crypto fraud exploded",{"title":"Birds flying"}))
    def test_requires_approval(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"clip.mp4";f.write_bytes(b"x")
            with self.assertRaises(ValueError):plan("An event happened.",[{"path":str(f),"approved":False}])
    def test_plan(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"clip.mp4";f.write_bytes(b"x")
            result=plan("A cryptocurrency scam emerged. Investors were concerned.",[{"path":str(f),"title":"cryptocurrency scam","approved":True}])
            self.assertEqual(len(result["scenes"]),2)
            self.assertGreater(result["duration_estimate"],3)
if __name__=="__main__":unittest.main()
