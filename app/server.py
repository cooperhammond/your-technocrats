# System
import sys

# Deep Learning
from fastai.vision import Path

# Web
import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles


export_file_url = 'https://github.com/cooperhammond/your-technocrats/releases/download/1.0/technocrats-resnet50-v1.pkl'
export_file_name = 'technocrats-resnet50-v1.pkl'

classes = [
    'bill-gates', 
    'elon-musk',
    'jack-ma',
    'jeff-bezos',
    'larry-ellison',
    'larry-page',
    'mark-zuckerberg'
]

path = Path(__file__).parent


app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))


@app.route("/")
async def homepage(request):
    html_file = path / 'view' / 'index.html'
    return HTMLResponse(html_file.open().read())
    

if __name__ == '__main__':
    if 'serve' in sys.argv:
        port = 5000
        if sys.argv[-1] != 'serve':
            port = int(sys.argv[-1])
            uvicorn.run(app=app, host='0.0.0.0', port=port, log_level="info")