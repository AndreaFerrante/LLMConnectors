import os
import sys
import json
import asyncio
from dotenv import load_dotenv
from src.connectors.ApiOpenAI import OpenAIClient
from src.connectors.ConfigOpenAI import OpenAISettings
from src.connectors.ApiPerplexity import PerplexityClient
from src.connectors.ConfigPerplexity import PerplexitySettings
from src.connectors.ApiAnthropic import AnthropicClient
from src.connectors.ConfigAnthropic import AnthropicSettings

load_dotenv()

async def _test_openai():

    settings = OpenAISettings(api_key=os.environ['OPENAI_API_KEY'])
    client   = OpenAIClient(settings=settings)

    try:
        result = await client.chat_completion(query='Tell me a simple joke.', return_only_answer=True)
        #result = await client.embeddings(input='what is your name ?', return_only_embeddings=True)
        
        if type(result) is str or type(result) is list:
            print(result)

        if type(result) is dict:
            print(json.dumps(result, indent=2))

    except Exception as exc:
        sys.exit(1)
    finally:
        await client.close()

def _run_test_openai():
    asyncio.run(_test_openai())

async def _test_perplexity():

    try:

        perplexity_settings = PerplexitySettings(api_key=os.environ['PPLX_API_KEY'])
        perplexity_client   = PerplexityClient(settings=perplexity_settings)
        
        result = await perplexity_client.chat_completion(model="sonar-pro", query="Tell me how to trade using orderflow.")

        if type(result) is str or type(result) is list:
            print(result)

        if type(result) is dict:
            print(json.dumps(result, indent=2))

    except Exception as exc:
        sys.exit(1)
    finally:
        await perplexity_client.close()

def _run_test_perplexity():
    asyncio.run(_test_perplexity())

async def _test_anthropic():

    try:

        anthropic_settings = AnthropicSettings(api_key=os.environ['ANTHROPIC_API_KEY'])
        anthropic_client   = AnthropicClient(settings=anthropic_settings)
        
        result = await anthropic_client.chat_completion(model="claude-sonnet-4-5-20250929", query="Tell me how to trade using orderflow.")

        if type(result) is str or type(result) is list:
            print(result)

        if type(result) is dict:
            print(json.dumps(result, indent=2))

    except Exception as exc:
        sys.exit(1)
    finally:
        await anthropic_client.close()

def _run_test_anthropic():
    asyncio.run(_test_anthropic())

if __name__ == "__main__":
    _run_test_anthropic()
