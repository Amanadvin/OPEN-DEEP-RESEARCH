from tavily import TavilyClient

client = TavilyClient(api_key="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")

result = client.search(
    query="What is AI?",
    search_depth="advanced",   # optional
    max_results=60              # optional
)

print(result)
