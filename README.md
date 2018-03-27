# notifications-antivirus

GOV.UK Notify Antivirus service. Read and write scan jobs via a scan queue.  Retrieves the supplied filename from the scan S3 bucket and uses ClamAV to scan the file. Sends the scan status back via a queue to update the notification status.


### `environment.sh`

Creating the environment.sh file. Replace [unique-to-environment] with your something unique to the environment. Your AWS credentials should be set up for notify-tools (the development/CI AWS account).

Create a local environment.sh file containing the following:

```
echo "

export STATSD_PREFIX='development'
export NOTIFICATION_QUEUE_PREFIX='YOUR_OWN_PREFIX'
export NOTIFY_ENVIRONMENT='development'
export FLASK_APP=application.py
export FLASK_DEBUG=1
export WERKZEUG_DEBUG_PIN=off
export AWS_ACCESS_KEY_ID='YOUR_TOOLS_AWS_ACCESS_KEY'
export AWS_SECRET_ACCESS_KEY='YOUR_TOOLS_AWS_SECRET_KEY'
export NOTIFY_LOG_PATH='/var/log/notify/antivirus'

"> environment.sh
```

NOTES:

 * Replace the placeholder key and prefix values as appropriate
 * The  unique prefix for the queue names prevents clashing with others' queues in shared amazon environment and enables filtering by queue name in the SQS interface.


```
source environment.sh
```

##  To run the application

The simplest way to run the application, is to run it inside a docker instance (recommended) 

```
make run-with-docker
```

Or to run it in a virtualenv (Nb. OS level dependencies such as ClamAV, should be resolved manually)
Run `pip install -r requirements.txt` to install Python dependencies.

```
scripts/run_celery.sh
```

##  To test the application

To run the tests 

```
make test-with-docker
```
