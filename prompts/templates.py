"""
Enhanced prompt templates with different prompting techniques
"""


class EnhancedPromptTemplates:
    """Enhanced prompt templates with better structure"""

    SYSTEM_PROMPT = """You are an expert code reviewer with years of experience in software development, security, and best practices. Your goal is to provide constructive, actionable feedback."""

    ZERO_SHOT_REVIEW = """
    Analyze the following {language} code and provide a comprehensive review.
    
    Code to review:
    ```{language}
    {code}
    ```
    
    Please provide your analysis in this exact JSON format:
    {{
        "issues": ["list of specific issues found"],
        "suggestions": ["list of actionable improvement suggestions"], 
        "rating": "rating from: Excellent/Good/Fair/Poor",
        "reasoning": "brief explanation of your assessment"
    }}
    
    Focus on: security vulnerabilities, performance issues, code quality, maintainability, and best practices.
    """

    FEW_SHOT_REVIEW = """
    You are an expert code reviewer. Here are examples of good code reviews:
    
    Example 1:
    Code: `def add(a, b): return a + b`
    Review: {{"issues": [], "suggestions": ["Add type hints for parameters and return value", "Add docstring to document function purpose"], "rating": "Good", "reasoning": "Simple, correct function but lacks documentation and type safety"}}
    
    Example 2:  
    Code: `password = "admin123"`
    Review: {{"issues": ["Hardcoded password is a security vulnerability", "Weak password that's easily guessable"], "suggestions": ["Use environment variables or secure credential storage", "Implement proper authentication system"], "rating": "Poor", "reasoning": "Critical security vulnerabilities present"}}
    
    Now review this {language} code:
    ```{language}
    {code}
    ```
    
    Provide your analysis in the same JSON format.
    """

    COT_REVIEW = """
    Analyze this {language} code step by step:
    
    Code to review:
    ```{language}
    {code}
    ```
    
    Let me think through this systematically:
    
    1. **Syntax and Logic Check**: I'll examine for any syntax errors or logical issues
    2. **Security Analysis**: I'll identify potential security vulnerabilities
    3. **Performance Review**: I'll assess performance implications and bottlenecks
    4. **Code Quality**: I'll evaluate readability, maintainability, and best practices
    5. **Testing Considerations**: I'll consider testability and edge cases
    
    Step-by-step analysis:
    [Provide detailed reasoning for each step]
    
    Final review in JSON format:
    {{
        "issues": ["list of issues found"],
        "suggestions": ["list of improvement suggestions"],
        "rating": "overall rating",
        "reasoning": "comprehensive reasoning based on step-by-step analysis"
    }}
    """
