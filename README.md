# notifications-antivirus

GOV.UK Notify Antivirus service. Read and write scan jobs via a scan queue.  Retrieves the supplied filename from the scan S3 bucket and uses ClamAV to scan the file. Sends the scan status back via a queue to update the notification status.

## First-time setup

This app uses dependencies that are difficult to install locally. In order to make local development easy, we run app commands through a Docker container. Run the following to set this up:

```shell
  make bootstrap
```

Because the container caches things like Python packages, you will need to run this again if you change things like "requirements.txt".

##  Environment Variables

Creating the environment.sh file. Replace [unique-to-environment] with your something unique to the environment. Your AWS credentials should be set up for notify-tools (the development/CI AWS account).

Create a local environment.sh file containing the following:

```
echo "

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
 * The unique prefix for the queue names prevents clashing with others' queues in shared amazon environment and enables filtering by queue name in the SQS interface.


```
source environment.sh
```

##  To run the application

The simplest way to run the application, is to run it inside a Docker container:

```
make run-with-docker
```

##  To test the application

To run the tests

```
make test-with-docker
```

## To update application dependencies

`requirements.txt` file is generated from the `requirements-app.txt` in order to pin
versions of all nested dependencies. If `requirements-app.txt` has been changed (or
we want to update the unpinned nested dependencies) `requirements.txt` should be
regenerated with

```
make freeze-requirements
```

`requirements.txt` should be committed alongside `requirements-app.txt` changes.
