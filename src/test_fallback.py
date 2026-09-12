import json

from llm_orchestrator import LLMOrchestrator


class FallbackTestOrchestrator(LLMOrchestrator):
    def call_gemini(self, prompt):
        raise RuntimeError("429")


if __name__ == "__main__":
    orchestrator = FallbackTestOrchestrator()

    test_text = """
    Anthropic announced a new artificial intelligence research project
    on September 11, 2026. The project focuses on improving AI safety.
    """

    result = orchestrator.generate(test_text)

    print("\nFinal result:")
    print(json.dumps(result, indent=2))