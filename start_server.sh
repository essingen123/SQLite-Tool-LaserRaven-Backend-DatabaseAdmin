#!/bin/bash

# Change to the sqlite_server directory
cd sqlite_server

# Start the server
python sqlite_server.py

# Open the web interface in the default browser
xdg-open http://localhost:5000 &

# Run the health check script
# python ../database_devops_automation_health_checks_procedure_1.py