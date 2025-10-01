"""Performance Expert Agent for code optimization and performance analysis."""

from .base_agent import BaseAgent


class PerformanceExpertAgent(BaseAgent):
    """Agent specialized in performance analysis and code optimization."""
    
    def __init__(self, backend):
        super().__init__(
            name="Performance Expert",
            description="Expert in performance analysis, code optimization, and OpenStack performance best practices",
            backend=backend
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for performance analysis."""
        return """You are a performance engineering expert specializing in OpenStack optimization with deep knowledge of:

- OpenStack performance architecture and bottlenecks
- Python performance optimization techniques
- Database query optimization and indexing strategies
- Memory management and garbage collection
- CPU and I/O optimization patterns
- OpenStack-specific performance concerns (nova, neutron, cinder, etc.)
- Profiling tools and performance monitoring
- Scalability patterns for cloud infrastructure
- Performance testing and benchmarking
- Resource utilization optimization

Your task is to analyze code for performance issues and provide:
1. Performance bottleneck identification with severity levels
2. Optimization recommendations with code examples
3. OpenStack-specific performance considerations
4. Scalability and resource utilization suggestions
5. Profiling and monitoring recommendations
6. Performance testing strategies

Always prioritize performance over convenience and provide measurable improvements."""
    
    def get_user_prompt(self, user_input: str) -> str:
        """Get the user prompt for performance analysis."""
        return f"""Please perform a comprehensive performance analysis of this code:

```python
{user_input}
```

Provide your performance analysis in the following structure:

- ⚡ **Performance Summary**: Overall performance assessment
- 🐌 **Bottlenecks Found**: List of performance issues with severity levels
- 🚀 **Optimization Opportunities**: Specific recommendations for improvement
- 📊 **OpenStack Performance**: Specific OpenStack performance considerations
- 🔧 **Code Optimizations**: Specific code changes with examples
- 📈 **Scalability Notes**: Scalability and resource utilization recommendations
- 🧪 **Testing Strategy**: Performance testing and benchmarking suggestions
- 📚 **Additional Resources**: Links to performance tools and documentation

Focus on:
- Algorithm complexity and efficiency
- Memory usage and garbage collection
- Database query optimization
- I/O operations and network calls
- Caching strategies
- OpenStack-specific performance patterns
- Resource utilization and scalability
- Profiling and monitoring recommendations

Be specific with measurable improvements and provide code examples."""
