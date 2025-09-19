import asyncio, sys
sys.path.insert(0,'..')
from app.services.ai_service import AIService

async def test():
    svc = AIService()
    await svc.initialize()
    print('status=', svc.get_status())
    res = await svc.conversation([{'role':'user','content':'Say hello and list two tips for studying effectively.'}])
    print('response=', res)

if __name__ == '__main__':
    asyncio.run(test())
