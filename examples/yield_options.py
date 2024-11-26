from flowpy import Result, Plugin, Query

plugin = Plugin()


@plugin.search()
async def on_query(data: Query):
    yield f"Your text is: {data.text}"
    yield f"Your keyword is: {data.keyword}"
    yield Result(f"Your raw text is: {data.raw_text}", sub="keyword + text")


if __name__ == "__main__":
    plugin.run()
