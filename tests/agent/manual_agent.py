import asyncio

from backend.app.agent import Agent


async def main():
    agent = Agent()

    question = input("Ask MCPilot: ")

    answer = await agent.run(question)

    print("\nMCPilot:")
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())