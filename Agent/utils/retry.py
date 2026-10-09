"""Retry utility for LLM invocations."""
from tenacity import retry, stop_after_attempt, wait_exponential


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def invoke_with_retry(chain, prompt):
    """Invoke a LangChain chain/LLM with automatic retry on transient errors."""
    return chain.invoke(prompt)
