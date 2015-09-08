echo "Stopping all services, removing containers"
sh stop-all.sh
echo "Starting all sertvices"
sh popit/server-run.sh
sh billit/server-run.sh
sh legislative/server-run.sh

