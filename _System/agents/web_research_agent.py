"""
WEB RESEARCH AGENT
Automated web research using search and fetch capabilities
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.research_agent import ResearchAgent
from datetime import datetime
from typing import Dict, List


class WebResearchAgent(ResearchAgent):
    """
    Web research agent that searches the internet

    Uses Claude Code's WebSearch and WebFetch tools via a special mode
    """

    def __init__(self, agent_id: str, question: str, investigation: str,
                 research_dir: str = None, web_search_func=None, web_fetch_func=None):
        """
        Initialize web research agent

        Args:
            agent_id: Unique identifier
            question: Research question
            investigation: Investigation name
            research_dir: Research directory path
            web_search_func: Function to call for web searches
            web_fetch_func: Function to call for fetching web pages
        """
        super().__init__(agent_id, question, investigation, research_dir)

        self.web_search = web_search_func
        self.web_fetch = web_fetch_func

        # Store if functions are available
        self.has_web_tools = (web_search_func is not None)

    def execute_research(self) -> Dict:
        """
        Execute web research

        Searches web for the question, fetches top results, extracts content
        """
        print(f"[WEB AGENT {self.agent_id}] Searching web for: {self.question}")

        if not self.has_web_tools:
            # Fallback: create a mock result explaining the limitation
            return {
                'content': self._create_mock_result(),
                'summary': 'Web search tools not available - generated placeholder research',
                'sources': []
            }

        # Execute web search
        search_results = self.web_search(self.question)

        # Extract and compile content
        all_content = []
        sources = []

        for i, result in enumerate(search_results.get('results', [])[:5]):  # Top 5 results
            url = result.get('url')
            title = result.get('title')

            print(f"[WEB AGENT {self.agent_id}] Processing: {title}")

            # Fetch full content if web_fetch available
            if self.web_fetch and url:
                try:
                    page_content = self.web_fetch(url, "Extract main content and key information")
                    all_content.append(f"\n\n## Source {i+1}: {title}\n\n{page_content}")

                    sources.append({
                        'url': url,
                        'title': title,
                        'accessed': datetime.now().isoformat(),
                        'source_type': 'web'
                    })
                except Exception as e:
                    print(f"[WEB AGENT {self.agent_id}] Error fetching {url}: {e}")
                    # Still include the title and URL even if fetch fails
                    all_content.append(f"\n\n## Source {i+1}: {title}\nURL: {url}\n")
                    sources.append({
                        'url': url,
                        'title': title,
                        'accessed': datetime.now().isoformat(),
                        'source_type': 'web',
                        'note': 'Content fetch failed'
                    })

        # Combine all content
        combined_content = "\n".join(all_content)

        # Create summary
        summary = f"Researched: {self.question}\n\nFound {len(sources)} relevant sources."

        return {
            'content': combined_content,
            'summary': summary,
            'sources': sources
        }

    def _create_mock_result(self) -> str:
        """
        Create mock research result for when web tools aren't available

        This allows testing the agent framework without actual web access
        """
        return f"""# Mock Research Result

**Question:** {self.question}

**Note:** This is a placeholder result. Web search tools are not currently available in this execution context.

## Key Points

1. Research question identified: {self.question}
2. Investigation context: {self.investigation}
3. Agent ready to execute when web tools are provided

## Next Steps

To enable actual web research:
1. Provide web_search_func to WebResearchAgent constructor
2. Provide web_fetch_func for full content retrieval
3. Re-run the agent

## Sample Entities

Example Corporation (Corporation): A sample entity for testing
Research Institute (Institution): Another sample entity
Sample Technology (Technology): Technology-related sample entity

## Sample Timeline

2025-12-19: Agent created and initialized
2025-12-19: Mock research result generated

---

*This mock result allows the integration pipeline to be tested without web access.*
"""


def main():
    """Command-line interface for testing"""
    import argparse

    parser = argparse.ArgumentParser(description='Web Research Agent')
    parser.add_argument('question', help='Research question to answer')
    parser.add_argument('--investigation', default='Test_Investigation', help='Investigation name')
    parser.add_argument('--agent-id', help='Agent ID (auto-generated if not provided)')

    args = parser.parse_args()

    # Generate agent ID if not provided
    if not args.agent_id:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        agent_id = f"web_{timestamp}"
    else:
        agent_id = args.agent_id

    print(f"\nCreating Web Research Agent")
    print(f"Agent ID: {agent_id}")
    print(f"Question: {args.question}")
    print(f"Investigation: {args.investigation}")

    # Create agent (without web tools - will use mock)
    agent = WebResearchAgent(
        agent_id=agent_id,
        question=args.question,
        investigation=args.investigation
    )

    # Execute
    results = agent.execute()

    print(f"\n{'='*70}")
    print("RESEARCH COMPLETE")
    print(f"{'='*70}")
    print(f"\nStatus: {results['execution']['status']}")
    print(f"Entities: {len(results['findings']['entities_discovered'])}")
    print(f"Events: {len(results['findings']['timeline_events'])}")
    print(f"Terms: {len(results['findings']['glossary_terms'])}")
    print(f"\nFindings saved to:")
    print(f"  {agent.findings_dir}")


if __name__ == '__main__':
    main()
