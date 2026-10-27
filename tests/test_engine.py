import unittest
from engine import split_script,action_for,plan,draw_frame
class EngineTests(unittest.TestCase):
    def test_split(self):
        self.assertEqual(len(split_script("He ran. She jumped.")),1)
    def test_action(self):
        self.assertEqual(action_for("He started to run away"),"run")
        self.assertEqual(action_for("Why did he disappear?"),"think")
    def test_plan(self):
        self.assertEqual(plan("He ran. He fell.","Horror",3)[1]["action"],"fall")
    def test_frame(self):
        im=draw_frame(320,180,0,4,"He ran",0,"Psychology")
        self.assertEqual(im.shape,(180,320,3))
if __name__=="__main__":unittest.main()
