"""
Web Search Stress Test - 500 Diverse Searches

Tests Nova's web search capabilities with 500 diverse queries across multiple categories.
Tracks success rates, performance, errors, and identifies areas for improvement.
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from src.nova_agents.tools.web_tools import WebSearchTool
from src.nova_shared.config import Config


class WebSearchStressTest:
    """Stress test for web search functionality."""
    
    def __init__(self, num_queries: int = 500):
        self.num_queries = num_queries
        self.search_tool = WebSearchTool()
        self.config = Config.from_env()
        self.results = []
        self.categories = self._generate_query_categories()
        
    def _generate_query_categories(self) -> Dict[str, List[str]]:
        """Generate diverse query categories."""
        return {
            "technology": [
                "latest AI developments",
                "quantum computing breakthroughs",
                "cybersecurity trends 2024",
                "cloud computing best practices",
                "machine learning frameworks",
                "blockchain technology applications",
                "5G network deployment",
                "autonomous vehicle technology",
                "augmented reality applications",
                "edge computing architecture"
            ],
            "science": [
                "climate change solutions",
                "CRISPR gene editing advances",
                "dark matter research",
                "renewable energy technologies",
                "neuroscience discoveries",
                "space exploration missions",
                "vaccine development",
                "quantum physics theories",
                "ocean acidification effects",
                "biodiversity conservation"
            ],
            "programming": [
                "Python best practices",
                "JavaScript async patterns",
                "Rust memory safety",
                "Go concurrency patterns",
                "Docker containerization",
                "Kubernetes orchestration",
                "microservices architecture",
                "GraphQL vs REST API",
                "serverless computing",
                "CI/CD pipelines"
            ],
            "data_science": [
                "neural network architectures",
                "data preprocessing techniques",
                "feature engineering methods",
                "model evaluation metrics",
                "time series forecasting",
                "natural language processing",
                "computer vision algorithms",
                "recommendation systems",
                "anomaly detection methods",
                "reinforcement learning"
            ],
            "business": [
                "startup funding strategies",
                "digital marketing trends",
                "remote work productivity",
                "supply chain optimization",
                "customer retention strategies",
                "agile project management",
                "financial forecasting",
                "market research methods",
                "brand positioning",
                "sales automation tools"
            ],
            "trending": [
                "viral social media trends",
                "breaking tech news",
                "cryptocurrency prices",
                "stock market analysis",
                "sports latest scores",
                "entertainment news",
                "political developments",
                "weather forecasts",
                "travel destinations",
                "health wellness tips"
            ],
            "technical": [
                "API rate limiting strategies",
                "database indexing performance",
                "load balancing algorithms",
                "caching mechanisms",
                "security vulnerability testing",
                "code review best practices",
                "testing automation frameworks",
                "monitoring and logging",
                "scalability patterns",
                "performance optimization"
            ],
            "research": [
                "academic paper search",
                "research methodology",
                "literature review techniques",
                "data collection methods",
                "statistical analysis tools",
                "peer review process",
                "citation management",
                "research ethics",
                "grant writing tips",
                "conference presentations"
            ],
            "educational": [
                "online learning platforms",
                "coding bootcamps review",
                "certification programs",
                "study techniques",
                "e-learning tools",
                "educational technology",
                "curriculum development",
                "student engagement",
                "assessment methods",
                "learning analytics"
            ],
            "how_to": [
                "how to deploy web application",
                "how to optimize database queries",
                "how to debug production issues",
                "how to write clean code",
                "how to design APIs",
                "how to secure applications",
                "how to scale infrastructure",
                "how to monitor systems",
                "how to automate workflows",
                "how to conduct code reviews"
            ]
        }
    
    def generate_queries(self) -> List[str]:
        """Generate list of diverse search queries."""
        queries = []
        
        # Distribute queries across categories
        queries_per_category = self.num_queries // len(self.categories)
        
        for category, base_queries in self.categories.items():
            for _ in range(queries_per_category):
                # Pick random query from category
                base_query = random.choice(base_queries)
                
                # Add variations
                variations = [
                    base_query,
                    f"{base_query} 2024",
                    f"best {base_query}",
                    f"{base_query} tutorial",
                    f"{base_query} guide",
                ]
                
                queries.append(random.choice(variations))
        
        # Fill remaining queries randomly
        while len(queries) < self.num_queries:
            category = random.choice(list(self.categories.keys()))
            base_query = random.choice(self.categories[category])
            queries.append(base_query)
        
        random.shuffle(queries)
        return queries[:self.num_queries]
    
    def run_single_search(self, query: str, index: int) -> Dict[str, Any]:
        """Execute single search and record results."""
        result = {
            "index": index,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "duration_ms": 0,
            "error": None,
            "result_count": 0,
            "response_data": None
        }
        
        start_time = time.time()
        
        try:
            response = self.search_tool.execute(query=query)
            duration_ms = (time.time() - start_time) * 1000
            
            result["duration_ms"] = duration_ms
            
            if isinstance(response, dict):
                result["success"] = response.get("success", False)
                result["error"] = response.get("error")
                
                if result["success"]:
                    # Count results
                    search_results = response.get("result", "")
                    result["result_count"] = len(search_results) if search_results else 0
                    result["backend_used"] = response.get("backend_used", "unknown")
                    result["response_data"] = {
                        "preview": str(search_results)[:200] if search_results else None
                    }
            else:
                result["success"] = True
                result["result_count"] = 1
                result["response_data"] = {"preview": str(response)[:200]}
                
        except Exception as e:
            result["error"] = str(e)
            result["duration_ms"] = (time.time() - start_time) * 1000
        
        return result
    
    def run_test(self, batch_delay: float = 0.5):
        """Run full stress test."""
        print(f"🚀 Starting Web Search Stress Test - {self.num_queries} queries\n")
        
        queries = self.generate_queries()
        
        print(f"📝 Generated {len(queries)} diverse queries across {len(self.categories)} categories")
        print(f"⏱️  Batch delay: {batch_delay}s between queries\n")
        
        start_time = time.time()
        
        for i, query in enumerate(queries, 1):
            print(f"[{i}/{self.num_queries}] Searching: {query[:60]}...")
            
            result = self.run_single_search(query, i)
            self.results.append(result)
            
            # Print status
            if result["success"]:
                backend = result.get("backend_used", "unknown")
                if backend == "fallback_synthetic":
                    status_icon = "⚠️  (Synthetic)"
                else:
                    status_icon = "✅"
                print(f"  {status_icon} {result['duration_ms']:.0f}ms - {result.get('result_count', 0)} results (Backend: {backend})")
            else:
                print(f"  ❌ {result['duration_ms']:.0f}ms - 0 results")
            
            if result["error"]:
                print(f"  ⚠️  Error: {result['error'][:100]}")
                # Dynamic backoff on error
                backoff = min(30.0, batch_delay * 5)
                print(f"  ⏸️  Backing off for {backoff}s...")
                time.sleep(backoff)
            
            # Delay between requests to avoid rate limiting
            if i < len(queries):
                time.sleep(batch_delay)
        
        total_duration = time.time() - start_time
        
        print(f"\n✅ Test completed in {total_duration:.2f}s")
        
        return self.analyze_results()
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze test results."""
        total = len(self.results)
        successful = sum(1 for r in self.results if r["success"])
        failed = total - successful
        
        success_rate = (successful / total * 100) if total > 0 else 0
        
        # Calculate performance metrics
        durations = [r["duration_ms"] for r in self.results if r["duration_ms"] > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        
        # Error analysis
        errors = [r["error"] for r in self.results if r["error"]]
        error_types = {}
        for error in errors:
            error_type = error.split(":")[0] if error else "Unknown"
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Result count analysis
        result_counts = [r["result_count"] for r in self.results if r["success"]]
        avg_results = sum(result_counts) / len(result_counts) if result_counts else 0
        
        analysis = {
            "summary": {
                "total_queries": total,
                "successful": successful,
                "failed": failed,
                "success_rate": f"{success_rate:.2f}%"
            },
            "performance": {
                "avg_duration_ms": f"{avg_duration:.2f}",
                "min_duration_ms": f"{min_duration:.2f}",
                "max_duration_ms": f"{max_duration:.2f}",
                "avg_results_per_query": f"{avg_results:.2f}"
            },
            "errors": {
                "total_errors": len(errors),
                "error_types": error_types
            },
            "recommendations": self._generate_recommendations(success_rate, error_types)
        }
        
        return analysis
    
    def _generate_recommendations(self, success_rate: float, error_types: Dict) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        if success_rate < 90:
            recommendations.append(f"⚠️  Success rate is {success_rate:.1f}%. Investigate error patterns.")
        
        if "timeout" in str(error_types).lower():
            recommendations.append("⏱️  Timeout errors detected. Consider increasing timeout limits.")
        
        if "rate" in str(error_types).lower() or "limit" in str(error_types).lower():
            recommendations.append("🚦 Rate limiting detected. Implement exponential backoff.")
        
        if "connection" in str(error_types).lower():
            recommendations.append("🔌 Connection errors found. Add retry logic with backoff.")
        
        if success_rate >= 95:
            recommendations.append("✅ Excellent success rate! System performing well.")
        
        return recommendations
    
    def save_results(self, output_path: str = None):
        """Save test results to file."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"web_search_test_{timestamp}.json"
        
        output_file = Path(output_path)
        
        data = {
            "test_config": {
                "num_queries": self.num_queries,
                "timestamp": datetime.now().isoformat(),
                "categories": list(self.categories.keys())
            },
            "results": self.results,
            "analysis": self.analyze_results()
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
        return output_file
    
    def print_report(self):
        """Print detailed test report."""
        analysis = self.analyze_results()
        
        print("\n" + "="*80)
        print("📊 WEB SEARCH STRESS TEST REPORT")
        print("="*80)
        
        print("\n📈 SUMMARY")
        print("-" * 80)
        for key, value in analysis["summary"].items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        print("\n⚡ PERFORMANCE")
        print("-" * 80)
        for key, value in analysis["performance"].items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        print("\n❌ ERRORS")
        print("-" * 80)
        print(f"  Total Errors: {analysis['errors']['total_errors']}")
        if analysis['errors']['error_types']:
            print("  Error Breakdown:")
            for error_type, count in sorted(analysis['errors']['error_types'].items(), 
                                           key=lambda x: x[1], reverse=True):
                print(f"    - {error_type}: {count}")
        
        print("\n💡 RECOMMENDATIONS")
        print("-" * 80)
        for rec in analysis["recommendations"]:
            print(f"  {rec}")
        
        print("\n" + "="*80)


def main():
    """Run stress test."""
    # Create and run test (100 queries for user verification)
    test = WebSearchStressTest(num_queries=100)
    
    # Run test with 3.0s delay between queries (safer for public APIs)
    test.run_test(batch_delay=3.0)
    
    # Print report
    test.print_report()
    
    # Save results
    test.save_results()


if __name__ == "__main__":
    main()
