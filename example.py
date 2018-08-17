from pynecktie import Necktie
from pynecktie.response import text

app = Necktie(__name__)

@app.route("/test1")
async def test1(request):
    return text("hello worlds")

if __name__ == "__main__":
    app.run("127.0.0.1", 9002, debug=True, auto_reload=True)
