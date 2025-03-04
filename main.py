from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType, tool
import os
import json
from langchain.tools import Tool


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")



@tool(parse_docstring=True)
def fetch_secure_rights(confirmation:str) -> str:
    """
    Fetches the list of available secure rights when the user asks for it.

    Args:
        confirmation (str): This just a confirmation from user yes / no or maybe they can ask for any specific secure right if present or not.

    Returns:
        str: A JSON string containing a list of secure rights with their IDs and names.
    """
    secure_rights = [
        {"id": 1, "name": "Secure Right 1"},
        {"id": 2, "name": "Secure Right 2"},
        {"id": 3, "name": "Secure Right 3"}
    ]
   
    return  json.dumps({"secure_rights": secure_rights})

@tool(parse_docstring=True)
def fetch_ownership_details(asset_name: str) -> str:
    """
    Ownership Verification: Verifies the ownership of a specific asset (e.g., film script or music composition).Get asset name from user or else do not proceed it is mandatory do not assume.

    Args:
        asset_name (str): The name of the asset to check ownership for.

    Returns:
        str: A JSON string containing ownership details of the asset.
    """
    ownership_details = {
        "asset_name": asset_name,
        "owner": "John Doe",
        "ownership_verified": True
    }
    return json.dumps(ownership_details)

@tool(parse_docstring=True)
def fetch_right_allocation(asset_name: str) -> str:
    """
    Right Allocation: Identifies the specific rights granted for a given asset.Get asset name from user or else do not proceed it is mandatory do not assume.

    Args:
        asset_name (str): The name of the asset to check rights for.

    Returns:
        str: A JSON string containing details about rights associated with the asset.
    """
    rights_allocation = [
        {"right": "Distribution Right", "granted_to": "John Doe"},
        {"right": "Adaptation Right", "granted_to": "Jane Smith"}
    ]
    return json.dumps({"asset_name": asset_name, "rights": rights_allocation})

@tool(parse_docstring=True)
def revenue_distribution(asset_name: str) -> str:
    """
    Revenue Distribution: Automatically calculates and distributes revenue generated from assets based on pre-defined rules. Get asset name from user or else do not proceed it is mandatory do not assume.

    Args:
        asset_name (str): The name of the asset for which revenue distribution will be calculated.

    Returns:
        str: A JSON string confirming the revenue distribution for the asset.
    """
    revenue_details = {
        "asset_name": asset_name,
        "total_revenue": 10000,
        "distribution": [
            {"owner": "John Doe", "amount": 6000},
            {"owner": "Jane Smith", "amount": 4000}
        ]
    }
    return json.dumps(revenue_details)

@tool(parse_docstring=True)
def ask_user_for_input(question: str) -> str:
    """
    Ask User Input: Prompts the user for missing or required information during the agent's execution. 
    This tool pauses the process and asks the user a specific question through the console. 
    It is mandatory to get the user's input and do not proceed without it.

    Args:
        question (str): The specific question that needs to be asked to the user for input.

    Returns:
        str: The user's response as a string.
    """
    return input(question)

@tool(parse_docstring=True)
def recommend_smart_contract(contract_type: str, asset_name: str) -> str:
    """
    Smart Contract Recommendation: Recommends a suitable smart contract template based on the contract type and asset name.

    Args:
        contract_type (str): The type of smart contract needed. Example: "film right", "revenue", "licensing".
        asset_name (str): The name of the asset the smart contract will be applied to.

    Returns:
        str: A JSON string containing the recommended smart contract details.
    """
    contract_templates = {
        "film right": {
            "template_name": "Film Rights Agreement",
            "description": "Handles the allocation and transfer of film rights for production and distribution."
        },
        "revenue": {
            "template_name": "Revenue Sharing Contract",
         "description": "Automates the distribution of generated revenue between stakeholders."
        },
         
             "licensing":{
            "template_name": "Licensing Agreement",
            "description": "Manages licensing terms and usage rights of the asset."
        }
    }

    recommendation = contract_templates.get(contract_type.lower(), {
        "template_name": "General Smart Contract",
        "description": "A general-purpose smart contract template."
    })

    result = {
        "asset_name": asset_name,
        "recommended_contract": recommendation
    }
    
    return json.dumps(result)



tools_list = [
    fetch_ownership_details,
    fetch_right_allocation,
    revenue_distribution,
    fetch_secure_rights,
    ask_user_for_input,
    recommend_smart_contract,
]



model = init_chat_model("llama-3.3-70b-versatile", model_provider="groq")
llm_with_tools = model.bind_tools(tools_list)


agent = initialize_agent(
    tools=tools_list,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    llm=model,
    verbose=False
)

tool_selection_prompt = PromptTemplate(
    input_variables=["query"],
    template="""You are a smart assistant responsible for selecting the correct tool to handle the user's request.

Below are the available tools you can call:

---
Tool Name: "fetch_ownership_details"
Trigger: When the user asks about checking, verifying, or confirming the ownership of an asset.

Tool Name: "fetch_right_allocation"
Trigger: When the user asks about fetching, checking, or viewing right allocations of an asset.

Tool Name: "revenue_distribution"
Trigger: When the user asks about reviewing, calculating, or checking the distribution of revenue or earnings.

Tool Name: "fetch_secure_rights"
Trigger: When the user asks about securing rights, obtaining protection, or fetching secure rights for an asset.

Tool Name: "recommend_smart_contract"
Trigger: When the user asks about recommending or creating smart contracts for an asset, including contract types like "film rights", "revenue", or "licensing".
---

### Instructions:
1. Carefully analyze the user query: "{query}"
2. Identify if it matches **any** of the tool triggers above, considering synonyms and intent.
3. Return **only** the exact tool name that matches the user's request.
4. If no matching tool is found, return `"none"`.
5. Do **NOT** explain your answer.

### Output format:
Return one of:
- fetch_ownership_details
- fetch_right_allocation
- revenue_distribution
- fetch_secure_rights
- recommend_smart_contract
- none
    """
)



def get_tool_from_llm(query: str) -> str:
    query = tool_selection_prompt.format(query=query)
    response = llm_with_tools.invoke([query])
    tool_name = response.content.lower()
    print(f"Tool name: {tool_name}")
    tool_name_mapping = {tool.func.__name__.lower(): tool for tool in tools_list}
    return tool_name_mapping.get(tool_name, "none")


print("AI Assistant: Hello! How can I assist you today?")
while True:
    user_input = input("You: ").strip()

    if user_input.lower() == "exit":
        print("AI Assistant: Thanks!")
        break

    try:
        selected_task = get_tool_from_llm(user_input.lower())
        available_tools = tools_list
        if selected_task in available_tools:
            response = agent.invoke(user_input)
            print(f"AI Assistant: {response['output']}")
        else:
            query_prompt = f"""You are Filmfusion bot blockchain assistant.Response to Random greetings and appreciations are fine but do not answer query outside the scope. If user query is not understandable ask user to clarify things to match with task tools. And if possible let user know what task you can help with.

           You assist with :
            - Verifying asset ownership details.
            - Fetching secure rights.
            - Revenue distribution.
            - Fetching Right allocation.
            - Recommending smart contracts."""
            response = model.invoke(query_prompt)
            print(f"AI Assistant: {response.content}")

    except Exception as e:
        print(f"AI Assistant: Exception  {e}")




