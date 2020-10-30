<p align="center">
	<img alt="Cloud Team" title="Cloud Team" src=".assets/logo.png" width="180">
</p>

<h1 align="center">Security Hub Organizations Deployment PoC</h1>

<p align="center">
  	<a href="#getting-started">Getting started</a> |
  	<a href="#deployment">Deployment</a> |
  	<a href="#how-to-use">How to use</a> |
  	<a href="#authors">Authors</a> 
</p>

## Getting started
### Pre-requisites
To clone and run this application, you'll need **[Git](https://git-scm.com)** and **[Python](https://www.python.org/)**

## Deployment 
### Installation
From your favourite command line tool, run the following:
```bash
# Clone the repo
$ git clone git@github.com:MetOffice/cloudteam-module-securityhub.git
```

Using the **[sample .env](env/.env.sample)** provided, create a new **.env** file in the env/ directory and add the following key-value
 pairs:
```.env
ARTEFACT_BUCKET_PREFIX=david-securityhub-artifacts-bucket
BRANCH_NAME=master
MASTER_ACCOUNT_PROFILE=testorg-opscentral
ORG_ID=o-n4q9yibv9t
REGIONS="eu-west-1 eu-west-2 us-east-1"
SERVICE_CODE=WCLOUD
SERVICE_NAME="Cloud Team"
SERVICE_OWNER=cloudops@metoffice.gov.uk
TARGET_ACCOUNT_PROFILE=testorg-productdev
UNIQUE_NAME=david
```

### Creating a feature environment
1. Deploy the pre-reqs and resources CloudFormation Stacks in the ops central test account of the
 Test AWS Organisation (148790130844), using the following script:
```bash
$ bash ./deploy.sh .env
```

### How to use
Copy the contents of the deploy.json file into the Test Events interface in the Lambda Console, then run the test in the Lambda.

You can also invoke the Lambda using the CLI, with deploy.json as the payload.


## Authors
**[Cloud Team](https://metoffice.sharepoint.com/sites/CloudTeamCommsSite)**
