import os
from src.main import app

if __name__=="__main__":
  port = int(os.environ).ger("PORT", 8000))
  app.run(host="0.0.0.0", port=port)