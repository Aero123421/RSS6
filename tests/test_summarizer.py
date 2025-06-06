import unittest
import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "summarizer", pathlib.Path(__file__).resolve().parents[1] / "ai" / "summarizer.py"
)
summarizer_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summarizer_module)
Summarizer = summarizer_module.Summarizer

class DummyAPI:
    def __init__(self, fail=False):
        self.fail = fail
    async def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.3):
        if self.fail:
            raise Exception("api error")
        return "これはテストの要約です"

class TestSummarizer(unittest.IsolatedAsyncioTestCase):
    async def test_summarize_success(self):
        summarizer = Summarizer(DummyAPI())
        summary = await summarizer.summarize("dummy text", 50)
        self.assertIn("テストの要約", summary)

    async def test_summarize_failure(self):
        summarizer = Summarizer(DummyAPI(fail=True))
        with self.assertRaises(Exception):
            await summarizer.summarize("dummy text", 50)

if __name__ == '__main__':
    unittest.main()
