# Warning control
import warnings
warnings.filterwarnings('ignore')
from crewai import Agent, Task, Crew

import os
from utils import get_openai_api_key, get_serper_api_key

openai_api_key = get_openai_api_key()
os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'
os.environ["SERPER_API_KEY"] = get_serper_api_key()

from crewai_tools import ScrapeWebsiteTool, SerperDevTool

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

estate_analyst_agent = Agent(
    role="Moroccan Real Estate Expert Analyst",
    goal="Monitor and analyze Moroccan real estate market data in real-time "
         "to identify trends and predict house prices.",
    backstory="Specializing in Moroccan real estate markets, this agent "
              "uses statistical modeling and machine learning "
              "to provide crucial insights. With a knack for real "
              "estate data, the Real Estate Expert Analyst Agent"
              " is the cornerstone for informing trading decisions "
              "that align with market conditions and the {customer}'s investment goals.",  
    verbose=True,
    allow_delegation=True,
    tools = [scrape_tool, search_tool]
)

trading_strategy_agent = Agent(
    role="Trading Strategy Developer",
    goal="Develop and test various trading strategies based "
         "on insights from the Moroccan Real Estate Analyst Agent.",
    backstory="Equipped with a deep understanding of property markets, "
              "financial markets, housing, moroccan real estate and quantitative "
              "analysis, this agent evises and refines trading "
              "strategies. It evaluates the performance of "
              "different approaches to determine the most "
              "profitable and risk-averse options.",
    verbose=True,
    allow_delegation=True,
    tools = [scrape_tool, search_tool]
)

execution_agent = Agent(
    role="Trade Advisor",
    goal="Suggest optimal trade execution strategies "
         "based on approved trading strategies.",
    backstory="This agent specializes in analyzing the timing, price, "
              "and logistical details of potential trades. By evaluating "
              "these factors, it provides well-founded suggestions for "
              "when and how trades should be executed to maximize "
              "efficiency and adherence to strategy.",
    verbose=True,
    allow_delegation=True,
    tools = [scrape_tool, search_tool]
)

risk_management_agent = Agent(
    role="Risk Advisor",
    goal="Evaluate and provide insights on the risks "
         "associated with potential trading activities.",
    backstory="Armed with a deep understanding of risk assessment models "
              "and market dynamics, this agent scrutinizes the potential "
              "risks of proposed trades. It offers a detailed analysis of "
              "risk exposure and suggests safeguards to ensure that "
              "trading activities align with the {customer}'s risk tolerance.",
    verbose=True,
    allow_delegation=True,
    tools = [scrape_tool, search_tool]
)
###################################################
support_agent = Agent(
    role="Senior Moroccan Real Estate Support Representative",
	goal="Be the most friendly, helpful and guidance providing "
        "real estate support representative in your team",
	backstory=(
		"You are now working on providing "
		"support to {customer}, a super important customer "
        " for your company."
		"You need to make sure that you provide the best support,"
		" guidance and explanation to the customer. Make sure to  "
        " provide full complete answers, and make no assumptions."
        " The {customer} wants to understand the moroccan real estate market "
        "and get insights on, then proceed to suggest the best property "
        "they're interested in buying and the best time to buy it."
	),
	allow_delegation=False,
	verbose=True
)
support_quality_assurance_agent = Agent(
	role="Support Quality Assurance Specialist",
	goal="Get recognition for providing the "
    "best support quality assurance in your team",
	backstory=(
		"You are now working with your team "
		"on a request from {customer} ensuring that "
        "the support representative is "
		"providing the best support possible.\n"
		"You need to make sure that the support representative "
        "is providing full"
		"complete answers, and make no assumptions."
	),
	verbose=True
)
###########################################################
# Task for Data Analyst Agent: Analyze Market Data
estate_analysis_task = Task(
    description=(
        "Continuously monitor and analyze  moroccan real estate  "
        "market data for the selected property ({property_selection}). "
        "Use statistical modeling and machine learning to "
        "identify trends and predict market movements,"
        "while aligning with the {customer}'s investment goals, "
        "property preferences and risk tolerance."
    ),
    expected_output=(
        "Insights and alerts about significant moroccan real estate market "
        "opportunities or threats for {property_selection}."
    ),
    agent=estate_analyst_agent,
)

# Task for Trading Strategy Agent: Develop Trading Strategies
strategy_development_task = Task(
    description=(
        "Develop and refine trading strategies based on "
        "the insights from the Moroccan Real Estate Analyst and "
        "{customer}-defined risk tolerance ({risk_tolerance}). "
        "Consider trading preferences ({trading_strategy_preference})."
    ),
    expected_output=(
        "A set of potential trading strategies for {property_selection} "
        "that align with the {customer}'s risk tolerance."
    ),
    agent=trading_strategy_agent,
)

# Task for Trade Advisor Agent: Plan Trade Execution
execution_planning_task = Task(
    description=(
        "Analyze approved trading strategies to determine the "
        "best execution methods for {property_selection}, "
        "considering current moroccan real estate market conditions and optimal pricing."
    ),
    expected_output=(
        "Detailed execution plans suggesting how and when to "
        "execute trades for {property_selection}."
    ),
    agent=execution_agent,
)
#want to add moroccan to every reference to real estate market.
# Task for Risk Advisor Agent: Assess Trading Risks
risk_assessment_task = Task(
    description=(
        "Evaluate the risks associated with the proposed trading "
        "strategies and execution plans for {property_selection}. "
        "Provide a detailed analysis of potential risks "
        "and suggest mitigation strategies."
    ),
    expected_output=(
        "A comprehensive risk analysis report detailing potential "
        "risks and mitigation recommendations for {property_selection}."
    ),
    agent=risk_management_agent,
)
from crewai import Crew, Process
from langchain_openai import ChatOpenAI

# Define the crew with agents and tasks
financial_trading_crew = Crew(
    agents=[estate_analyst_agent, 
            trading_strategy_agent, 
            execution_agent, 
            risk_management_agent],
    
    tasks=[estate_analysis_task, 
           strategy_development_task, 
           execution_planning_task, 
           risk_assessment_task],
    
    manager_llm=ChatOpenAI(model="gpt-3.5-turbo", 
                           temperature=0.7),
    process=Process.hierarchical,
    verbose=True
)

### this execution will take some time to run
# Example data for kicking off the process
financial_trading_inputs = {
    'property_selection': 'Villa in Rabat',
    'initial_capital': '3000000',
    'risk_tolerance': 'Medium',
    'trading_strategy_preference': 'Long-term Investing',
    'news_impact_consideration': True
}
result = financial_trading_crew.kickoff(inputs=financial_trading_inputs)

from IPython.display import Markdown
Markdown(result)