# notifications-antivirus

Reads jobs from a queue, using the supplied filename to fetch files from an S3 bucket, and ClamAV to scan them. Sends the scan status back by creating a new job to update the notification status.

## Setting up

### Docker container

This app uses dependencies that are difficult to install locally. In order to make local development easy, we run app commands through a Docker container. Run the following to set this up:

```shell
  make bootstrap
```

Because the container caches things like Python packages, you will need to run this again if you change things like "requirements.txt".

### AWS credentials

To run the app you will need appropriate AWS credentials. See the [Wiki](https://github.com/alphagov/notifications-manuals/wiki/aws-accounts#how-to-set-up-local-development) for more details.

### `environment.sh`

In the root directory of the application, run:

```
echo "
export NOTIFICATION_QUEUE_PREFIX='YOUR_OWN_PREFIX'
"> environment.sh
```

Things to change:

- Replace YOUR_OWN_PREFIX with local_dev_\<first name\> (to match other apps).

##  To run the application

```
# install dependencies, etc.
make bootstrap

# run the web app
make run-flask

# run the background tasks
make run-celery
```

##  To test the application

```
# install dependencies, etc.
make bootstrap

make test
```

If you need to run a specific command, such as a single test, you can use the `run_with_docker.sh` script. This is what `test` and other `make` rules use.

```shell
./scripts/run_with_docker.sh pytest tests/some_specific_test.py
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
