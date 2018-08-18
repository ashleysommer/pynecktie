# Getting Started

Make sure you have both [pip](https://pip.pypa.io/en/stable/installing/) and at
least version 3.5 of Python before starting. Necktie uses the new `async`/`await`
syntax, so earlier versions of python won't work.

1. Install Necktie: `python3 -m pip install pynecktie`
2. Create a file called `main.py` with the following code:

  ```python
  from pynecktie import Necktie
  from pynecktie.response import json

  app = Necktie()

  @app.route("/")
  async def test(request):
      return json({"hello": "world"})

  if __name__ == "__main__":
      app.run(host="0.0.0.0", port=8000)
  ```
  
3. Run the server: `python3 main.py`
4. Open the address `http://0.0.0.0:8000` in your web browser. You should see
   the message *Hello world!*.

You now have a working Necktie server!
