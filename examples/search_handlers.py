from flogin import Plugin, Query, SearchHandler

plugin = Plugin()


class MyHandler(SearchHandler):
    async def callback(self, query: Query):
        return "This comes from my subclassed handler"

    async def on_error(self, query: Query, error: Exception):
        """Handle errors from the 'callback' method"""
        return f"An error occured: {error}"


plugin.register_search_handler(MyHandler())


@plugin.search()
async def my_simple_search_handler(data: Query):
    return "This comes from my simple handler"


@my_simple_search_handler.error
async def my_simple_search_handler_error_handler(query: Query, error: Exception):
    """Handle errors in my 'my_simple_search_handler'"""
    return f"An error occured: {error}"


if __name__ == "__main__":
    plugin.run()
