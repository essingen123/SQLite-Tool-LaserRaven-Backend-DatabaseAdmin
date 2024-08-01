#!/bin/bash

# Run the Python server in the background
python server.py &

# Open the HTML in the default web browser
open http://localhost:$(python -c "import server; print(server.port)")

# Wait for the Python server to finish
wait %1