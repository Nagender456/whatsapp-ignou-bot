async def main():
	message = None
	with open('currentMessage.txt', 'r') as file:
		message = file.readline().strip()
	from messageHandler.messageHandler import MessageHandler

	handler = MessageHandler(message)
	responses = await handler.handleMessage()
	if (len(responses) < 1):
		return
	responses = [x[2].strip() for x in responses]
	print("|||".join(responses))
	exit(0)
import asyncio
asyncio.run(main())