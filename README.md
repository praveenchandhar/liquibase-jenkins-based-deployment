# Liquibase Jenkins-Based Deployment

MongoDB database change management using Liquibase with Jenkins automation.

## Overview

This project provides automated MongoDB database change management using Liquibase with Jenkins integration. It converts JavaScript MongoDB operations to Liquibase XML changesets and deploys them through Jenkins pipelines.

## Workflow

1. **Developer**: Adds JS file to `db/mongodb/dev/weekly_release/YYYYMMDD/` or `db/mongodb/dev/monthly_release/YYYYMMDD/`
2. **GitHub Action**: Automatically generates XML changeset from JS file when PR is created
3. **Review & Merge**: Team reviews both JS and XML files, then merges PR
4. **Jenkins Deployment**: Use Jenkins pipeline to deploy database changes with branch/tag name

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/your-org/liquibase-jenkins-based-deployment.git
cd liquibase-jenkins-based-deployment
```

### 2. Setup Jenkins Job
```bash
cd jenkins/
chmod +x setup-jenkins-job.sh
./setup-jenkins-job.sh http://localhost:8080 your-jenkins-user your-api-token
```

### 3. Test with Sample Changeset
```bash
# Create test branch
git checkout -b test-deployment-$(date +%Y%m%d)

# Add sample JS file
mkdir -p db/mongodb/dev/weekly_release/$(date +%Y%m%d)
cat > db/mongodb/dev/weekly_release/$(date +%Y%m%d)/sample.js << 'EOF'
// context: liquibase_test

// Insert test documents
db.testCollection.insertMany([
    { name: "Test User 1", email: "test1@example.com", created: new Date() },
    { name: "Test User 2", email: "test2@example.com", created: new Date() }
]);

// Create index
db.testCollection.createIndex({ email: 1 }, { unique: true });
EOF

# Commit and push
git add .
git commit -m "Add sample MongoDB changeset"
git push origin test-deployment-$(date +%Y%m%d)

# Create PR on GitHub, review generated XML, and merge
```

### 4. Deploy via Jenkins
1. Go to Jenkins: `http://localhost:8080`
2. Open `liquibase-mongodb-deployment` job
3. Click "Build with Parameters"
4. Enter parameters:
   - **BRANCH_OR_TAG**: `test-deployment-20241215` (your branch name)
   - **LIQUIBASE_ACTION**: `status` (for dry-run) or `update` (to apply changes)
   - **ROLLBACK_COUNT**: Only needed if action is `rollback`
5. Click "Build"

## Features

- ✅ **Automatic XML Generation**: Converts JS MongoDB operations to Liquibase XML
- ✅ **Branch/Tag Deployment**: Deploy from any branch or tag name
- ✅ **Smart Rollback**: Dynamic rollback count based on available changesets
- ✅ **Context Detection**: Automatically detects database context from XML
- ✅ **MongoDB Atlas Support**: Works with MongoDB Atlas clusters
- ✅ **GitHub Integration**: Seamless workflow with GitHub Actions
- ✅ **Multi-Environment**: Support for different database contexts

## Configuration

### MongoDB Connection
Update the connection string in these files:
- `scripts/liquibase_runner.sh` (line 4)
- `jenkins/Jenkinsfile` (environment section)

```bash
MONGO_CONNECTION_BASE="your-mongodb-connection-string"
```

### GitHub Credentials in Jenkins
1. Go to Jenkins Dashboard
2. Manage Jenkins > Manage Credentials
3. Add new credential:
   - Kind: Username with password
   - Username: Your GitHub username
   - Password: GitHub Personal Access Token
   - ID: `github-credentials`

### Jenkins URL Configuration
Update Jenkins URL in:
- `.github/workflows/jenkins-deployment-notification.yml` (line 65)

## Supported MongoDB Operations

| Operation | Example | Liquibase XML |
|-----------|---------|---------------|
| **Insert One** | `db.users.insertOne({name: "John"})` | `<mongodb:insertOne>` |
| **Insert Many** | `db.users.insertMany([{...}, {...}])` | `<mongodb:insertMany>` |
| **Update One** | `db.users.updateOne({}, {$set: {}})` | `<mongodb:runCommand>` |
| **Update Many** | `db.users.updateMany({}, {$set: {}})` | `<mongodb:runCommand>` |
| **Replace One** | `db.users.replaceOne({}, {})` | `<mongodb:runCommand>` |
| **Delete One** | `db.users.deleteOne({})` | `<mongodb:runCommand>` |
| **Delete Many** | `db.users.deleteMany({})` | `<mongodb:runCommand>` |
| **Create Index** | `db.users.createIndex({email: 1})` | `<mongodb:runCommand>` |
| **Drop Index** | `db.users.dropIndex("email_1")` | `<mongodb:dropIndex>` |
| **Create Collection** | `db.createCollection("users")` | `<mongodb:createCollection>` |
| **Drop Collection** | `db.users.drop()` | `<mongodb:dropCollection>` |

## Example JS File

```javascript
// context: liquibase_test
// This comment defines which database context to use

// Insert multiple users
db.users.insertMany([
    {
        name: "John Doe",
        email: "john@example.com",
        role: "admin",
        created: new Date()
    },
    {
        name: "Jane Smith", 
        email: "jane@example.com",
        role: "user",
        created: new Date()
    }
]);

// Create unique index on email
db.users.createIndex(
    { email: 1 }, 
    { unique: true, name: "email_unique_idx" }
);

// Update all users without status
db.users.updateMany(
    { status: { $exists: false } },
    { $set: { status: "active", updated: new Date() } }
);

// Create orders collection
db.createCollection("orders");

// Insert sample order
db.orders.insertOne({
    userId: "user123",
    items: [
        { product: "laptop", price: 999.99 },
        { product: "mouse", price: 29.99 }
    ],
    total: 1029.98,
    status: "pending",
    created: new Date()
});
```

## Generated XML Example

The above JS file generates this Liquibase XML:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:mongodb="http://www.liquibase.org/xml/ns/dbchangelog-ext"
    xsi:schemaLocation="...">

    <changeSet id="20241215_1.1" author="developer" context="liquibase_test">
        <mongodb:insertMany collectionName="users">
            <mongodb:documents><![CDATA[
            [
                {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "role": "admin",
                    "created": new Date()
                },
                {
                    "name": "Jane Smith",
                    "email": "jane@example.com", 
                    "role": "user",
                    "created": new Date()
                }
            ]
            ]]></mongodb:documents>
        </mongodb:insertMany>
    </changeSet>

    <changeSet id="20241215_1.2" author="developer" context="liquibase_test">
        <mongodb:runCommand>
            <mongodb:command><![CDATA[
            {
                "createIndexes": "users",
                "indexes": [
                    {
                        "key": { "email": 1 },
                        "name": "email_unique_idx"
                    }
                ]
            }
            ]]></mongodb:command>
        </mongodb:runCommand>
    </changeSet>

    <!-- Additional changesets... -->
</databaseChangeLog>
```

## Jenkins Pipeline Parameters

### BRANCH_OR_TAG
- **Type**: String input
- **Description**: Branch or tag name containing changesets
- **Examples**: `main`, `feature/user-management`, `v1.2.0`, `hotfix/urgent-fix`

### LIQUIBASE_ACTION
- **Type**: Dropdown choice
- **Options**:
  - `status` - Show pending changes (dry-run)
  - `update` - Apply all pending changes
  - `rollback` - Rollback specified number of changesets

### ROLLBACK_COUNT
- **Type**: Dropdown choice (1-10)
- **Description**: Number of changesets to rollback
- **Only visible**: When LIQUIBASE_ACTION is `rollback`
- **Dynamic**: Pipeline validates count against available changesets

## Database Contexts

The system supports multiple database contexts for different environments:

| Context | Database | Usage |
|---------|----------|-------|
| `liquibase_test` | liquibase_test | Development testing |
| `sample_mflix` | sample_mflix | Sample movie database |
| `liquibase_test_new` | liquibase_test_new | New feature testing |

Add context at the top of your JS files:
```javascript
// context: liquibase_test
```

## Troubleshooting

### Common Issues

**1. XML not generated from JS file**
- Check JS file is in correct directory: `db/mongodb/dev/weekly_release/YYYYMMDD/` or `db/mongodb/dev/monthly_release/YYYYMMDD/`
- Verify JS file has valid MongoDB syntax
- Check GitHub Actions logs for Python script errors

**2. Jenkins job fails with "No changesets found"**
- Ensure branch/tag contains XML files in `db/mongodb/dev/` directory
- Verify branch/tag name is correct
- Check if PR was properly merged

**3. MongoDB connection timeout**
- Verify MongoDB Atlas connection string
- Check Jenkins server can reach MongoDB Atlas (firewall/network)
- Validate MongoDB credentials

**4. Rollback count validation error**
- Rollback count cannot exceed total changesets in XML file
- Pipeline automatically validates and shows available count

### Debug Commands

Check changeset files:
```bash
find db/mongodb/dev -name "*.xml" -type f
```

Count changesets in XML:
```bash
grep -c "<changeSet" path/to/changeset.xml
```

Test MongoDB connection:
```bash
# From Jenkins server
mongosh "your-connection-string" --eval "db.runCommand({ping: 1})"
```

## Support

### Prerequisites
- Jenkins with Pipeline plugin installed
- Git plugin for Jenkins
- GitHub credentials configured in Jenkins
- MongoDB Atlas cluster accessible from Jenkins
- Internet access for downloading Liquibase dependencies

### Required Jenkins Plugins
- Pipeline
- Git
- GitHub
- Credentials Binding
- Pipeline: Stage View

### File Permissions
Ensure shell scripts are executable:
```bash
chmod +x scripts/liquibase_runner.sh
chmod +x jenkins/setup-jenkins-job.sh
```

## Version History

- **v1.0** - Initial release with basic JS to XML conversion
- **v1.1** - Added Jenkins integration and rollback support
- **v1.2** - Enhanced with branch/tag deployment and dynamic parameters

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Add JS changeset in appropriate date directory
4. Test with Jenkins pipeline
5. Submit pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
