from vad.silerovad import SileroVAD
from stt.groqWhisper import GroqWhisper
from tts.groqPlayai import GroqPlayai
from gen.groq import GroqGen

class Conversation:
    def __init__(self,
                 vad=SileroVAD(),
                 stt=GroqWhisper(),
                 tts=GroqPlayai(),
                 gen=GroqGen()
                 ):
        self.vad = vad
        self.stt = stt
        self.tts = tts
        self.gen = gen