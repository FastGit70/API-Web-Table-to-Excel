from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
import uuid
import threading
import time

app = FastAPI()

@app.get("/table-to-excel/")
def table_to_excel(url: str, table_index: int = Query(0, ge=0)):
    try:
        # Fetch and parse the webpage
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        tables = soup.find_all("table")

        if not tables:
            raise ValueError("No tables found on the page.")
        if table_index >= len(tables):
            raise ValueError(f"Only {len(tables)} tables found. Index {table_index} is out of range.")

        # Read table using pandas
        df = pd.read_html(str(tables[table_index]))[0]

        # Save to Excel file
        filename = f"table_{uuid.uuid4().hex}.xlsx"
        df.to_excel(filename, index=False)

        # Schedule cleanup
        threading.Thread(target=delete_later, args=(filename,)).start()

        return FileResponse(filename, filename=filename, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def delete_later(filepath, delay=30):
    time.sleep(delay)
    try:
        os.remove(filepath)
    except Exception:
        pass
