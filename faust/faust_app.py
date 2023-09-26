import faust

from access_log_parser import AccessLogParser

parser = AccessLogParser()

app = faust.App(
	"access-logs",
	broker="kafka://localhost:9092",
	value_serializer="json",
	consumer_auto_offset_reset="latest"
)

success_topic = app.topic("success")
redirect_topic = app.topic("redirect")
error_topic = app.topic("error")

enriched_logs_topic = app.topic("enriched-logs")

@app.agent(success_topic)
async def access_success_logs(stream):
	async for event in stream:
		message = parser.parse(event["message"])
		message["responseType"] = "success"
		await enriched_logs_topic.send(
			key=event["host"]["name"],
			value={'expandedMessage': message}
		)

@app.agent(redirect_topic)
async def access_redirect_logs(stream):
	async for event in stream:
		message = parser.parse(event["message"])
		message["responseType"] = "redirect"
		await enriched_logs_topic.send(
			key=event["host"]["name"],
			value={'expandedMessage': message}
		)
		
@app.agent(error_topic)
async def access_error_logs(stream):
	async for event in stream:
		message = parser.parse(event["message"])
		message["responseType"] = "error"
		await enriched_logs_topic.send(
			key=event["host"]["name"],
			value={'expandedMessage': message}
		)