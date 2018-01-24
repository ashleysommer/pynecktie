from pynecktie import Necktie
from pynecktie.response import text

app = Necktie(__name__)

@app.route("/test1")
async def test1(request):
    return text("hello world")

if __name__ == "__main__":
    app.go_fast("help")
    app.run("127.0.0.1", 9001, debug=True)
