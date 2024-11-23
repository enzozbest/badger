# Team *Badger* Small Group project

## Team members
The members of the team are:
- Eeshal Malik
- Enzo Bestetti
- Isabella McLean
- Jiale She
- Lucia Garces Gutierrez

## Project structure
The project is called `CodeConnect by Code Tutors`.

## Deployed version of the application
The deployed version of the application can be found at [*https://isabellamcleankcl.pythonanywhere.com/*](https://isabellamcleankcl.pythonanywhere.com/).

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Decide whether you wish to use AWS's S3 service to store automatically generated invoices.
This is disabled by default, and invoices will be stored locally at the 'invoicer/pdfs' directory.

The field "USE_AWS_S3" in 'code_tutors/settings.py' can be changed to 'True' if you wish to use S3.
If you do, you must also provide your AWS Account ID in the same file, to the field "AWS_ACCOUNT_ID".
You must then change the file 'config.yml' in the code_tutors/aws/resources directory, to reflect your AWS 
setup (bucket name, IAM role access name, etc).

Also make sure you have correctly set up your credentials in your environment. You can do this using the AWS Command line interface(aws-cli)
with the following command:

```
$aws configure
```

You will then be prompted to enter you AWS_ACCESS_KEY_ID, SECRET_ACCESS_KEY, and REGION_NAME. If these are correctly set up,
the application will pick them up automatically and nothing further will need to be done.

Alternatively, you can use the following commands to set environment variables:

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

Afterwards, seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

## Sources
The packages used by this application are specified in `requirements.txt`