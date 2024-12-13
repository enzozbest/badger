# Team *Badger* Small Group project

## Team members

The members of the team are:

- Eeshal Malik
- Enzo Bestetti
- Isabella McLean
- Jiale She
- Lucia Garces Gutierrez

## Project structure

The project is called `CodeConnect by Code Tutors`. The application consists of several apps, all of which are largely
self-contained. Our system has the following apps:

- user_system: responsible for managing the User model, and by extension the interaction between users (clients) and the
  application (server)
- request_handler: responsible for managing the Request model and dealing with most of the Request logic, e.g. creation,
  deletion, updates.
- admin_functions: responsible for managing functionality exclusive to users with Admin privileges, e.g. Request
  allocation and making other users Admins.
- invoicer: responsible for generating PDF invoices automatically and storing them in a pre-defined location (be that
  locally or remotely on Amazon's S3)
- calendar_scheduler: largely responsible for booking allocated requests into actual sessions, and displaying them in a
  calendar format to the relevant users (student and tutors)

## Deployed version of the application

The deployed version of the application can be found at [*badger2024.ddns.net*](http://badger2024.ddns.net).
The administration interface is available at [*Admin Interface*](http://badger2024.ddns.net/admin).

## Installation instructions

To install the software and use it in your local development environment, you must first set up and activate a local (
virtual) development environment. From the root of the project:

```
$ python3 -m venv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Decide whether you wish to use AWS's S3 service to store automatically generated PDFs for invoices.
This is disabled by default (invoices will be stored locally at the 'invoicer/pdfs' directory).

The field "USE_AWS_S3" in 'code_tutors/settings.py' can be changed to 'True' if you wish to use S3.
If you do wish to use S3, you must also provide your AWS Account ID in the same file, to the field "AWS_ACCOUNT_ID".
You must then change the file 'config.yml' in the code_tutors/aws/resources directory, to reflect your AWS
setup (bucket name, IAM role access name, etc).

Also make sure you have correctly set up your credentials in your environment. You can do this using the AWS Command
line interface (aws-cli)
with the following command:

```
$ aws configure
```

You will be prompted to enter you AWS_ACCESS_KEY_ID, SECRET_ACCESS_KEY, and REGION_NAME. If these are correctly set up,
the application will pick them up automatically and nothing further will need to be done.

Alternatively, you can use the following commands to set environment variables which the application can also
automatically pick up:

* Linux/macOS:

```
$ export AWS_ACCESS_KEY_ID=your-access-key-here
$ export SECRET_ACCESS_KEY=your-secret-access-key-here
$ export AWS_REGION_NAME=your-aws-region-name-here
```

* Windows:

```
$ set AWS_ACCESS_KEY_ID=your-access-key-here
$ set SECRET_ACCESS_KEY=your-secret-access-key-here
$ set AWS_REGION_NAME=your-aws-region-name-here 
```

If you made any changes to the default configurations, update database migrations before continuing:

```
$ python3 manage.py makemigrations --merge
$ python3 manage.py makemigrations
```

Then, migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:

```
$ python3 manage.py test
```

All tests should pass, and coverage is at 100% if the variable USE_AWS_S3 in code_tutors/settings.py is set. Note that
if you do not use AWS (i.e. you do not have it set up locally and/or the variable is not set), AWS-related tests will be
skipped and this may impact the coverage report!

## Sources

The packages used by this application are specified in `requirements.txt`
