import os
import jsonref
import requests
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    OpenApiTool,
    OpenApiAnonymousAuthDetails,
)

load_dotenv()

PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT = os.getenv("FOUNDRY_AGENT_MODEL", "gpt-4.1")

OPENAPI_URL = "https://inventory-agent.politedune-38af7eb9.brazilsouth.azurecontainerapps.io/openapi.json"

if not PROJECT_ENDPOINT:
    raise ValueError("AZURE_AI_PROJECT_ENDPOINT não foi definido no .env")

print("Carregando OpenAPI...")
openapi_spec = jsonref.loads(requests.get(OPENAPI_URL, timeout=30).text)

print("Conectando ao Azure AI Foundry...")
client = AgentsClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)

openapi_tool = OpenApiTool(
    name="inventory_tools",
    spec=openapi_spec,
    description="Inventory API tools for product, supplier and purchasing policy lookup.",
    auth=OpenApiAnonymousAuthDetails(),
)

print("Criando agente...")
agent = client.create_agent(
    model=MODEL_DEPLOYMENT,
    name="inventory-agent-openapi",
    instructions=(
        "Você é um agente especialista em estoque e suprimentos. "
        "Use as ferramentas OpenAPI de inventário sempre que o usuário perguntar "
        "sobre produtos, fornecedores, políticas de estoque ou políticas de compra."
    ),
    tools=openapi_tool.definitions,
)

print("Agente criado com sucesso!")
print(f"Agent ID: {agent.id}")