# Jenkins Setup for Liquibase MongoDB Deployment

## Overview
This directory contains Jenkins configuration files for automated MongoDB database deployments using Liquibase.

## Files
- `Jenkinsfile` - Main pipeline definition
- `setup-jenkins-job.sh` - Automated job creation script
- `README.md` - This file

## Features
- Branch/tag-based deployments
- Dynamic changeset discovery
- Rollback support with changeset counting
- Automatic database context detection
- MongoDB Atlas integration

## Usage

### Automatic Setup
```bash
cd jenkins/
chmod +x setup-jenkins-job.sh
./setup-jenkins-job.sh http://localhost:8080 your-user your-token
```

### Manual Setup
1. Copy job configuration from `setup-jenkins-job.sh`
2. Create new Pipeline job in Jenkins
3. Configure Git repository and credentials
4. Set script path to `jenkins/Jenkinsfile`

### Pipeline Parameters
- **BRANCH_OR_TAG**: Branch or tag name to deploy
- **LIQUIBASE_ACTION**: status/update/rollback
- **ROLLBACK_COUNT**: Number of changesets to rollback (1-10)

## Prerequisites
- Jenkins with Pipeline plugin
- Git plugin
- GitHub credentials configured
- Internet access for dependency downloads
