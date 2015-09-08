#
## 
rm -f /src/bill-it/tmp/pids/server.pid
cd $billit && bundle exec rake sunspot:solr:start && rails server --port 8002


