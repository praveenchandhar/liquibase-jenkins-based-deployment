#!/bin/bash

# MongoDB Atlas connection base
MONGO_CONNECTION_BASE="mongodb+srv://praveenchandharts:kixIUsDWGd3n6w5S@praveen-mongodb-github.lhhwdqa.mongodb.net"

# Database contexts mapping
declare -A DATABASE_CONTEXTS=(
    ["liquibase_test"]="liquibase_test"
    ["sample_mflix"]="sample_mflix"
    ["liquibase_test_new"]="liquibase_test_new"
)

# Validate input arguments
if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <command> <database> <changeset_file> [rollback_count]"
    echo ""
    echo "Commands: status, update, rollback"
    echo "Examples:"
    echo "  $0 status liquibase_test /path/to/changeset.xml"
    echo "  $0 update liquibase_test /path/to/changeset.xml"
    echo "  $0 rollback liquibase_test /path/to/changeset.xml 2"
    exit 1
fi

command="$1"
database="$2"
changeset_file="$3"
rollback_count="$4"

# Validate command
if [[ "$command" != "status" && "$command" != "update" && "$command" != "rollback" ]]; then
    echo "❌ Invalid command: $command"
    echo "Valid commands: status, update, rollback"
    exit 1
fi

# Validate database
if [[ -z "${DATABASE_CONTEXTS[$database]}" ]]; then
    echo "❌ Invalid database: $database"
    echo "Valid databases: ${!DATABASE_CONTEXTS[*]}"
    exit 1
fi

# Validate changeset file
if [[ ! -f "$changeset_file" ]]; then
    echo "❌ Changeset file not found: $changeset_file"
    exit 1
fi

# Validate rollback count if provided
if [[ "$command" == "rollback" ]]; then
    if [[ -z "$rollback_count" ]]; then
        echo "❌ Rollback count is required for rollback command"
        exit 1
    fi
    if ! [[ "$rollback_count" =~ ^[0-9]+$ ]]; then
        echo "❌ Rollback count must be a number"
        exit 1
    fi
fi

# Setup CLASSPATH
CLASSPATH=$(find "$HOME/liquibase-jars" -name "*.jar" | tr '\n' ':')
export CLASSPATH

echo "🚀 Executing Liquibase command..."
echo "   Command: $command"
echo "   Database: $database"
echo "   Context: ${DATABASE_CONTEXTS[$database]}"
echo "   Changeset: $changeset_file"
if [[ "$command" == "rollback" ]]; then
    echo "   Rollback Count: $rollback_count"
fi

# Build liquibase command
LIQUIBASE_CMD="java -cp \"$CLASSPATH\" liquibase.integration.commandline.Main \
    --url=\"${MONGO_CONNECTION_BASE}/${database}?retryWrites=true&w=majority&tls=true\" \
    --changeLogFile=\"$changeset_file\" \
    --contexts=\"${DATABASE_CONTEXTS[$database]}\" \
    --logLevel=\"info\""

if [[ "$command" == "rollback" ]]; then
    LIQUIBASE_CMD="$LIQUIBASE_CMD rollbackCount $rollback_count"
else
    LIQUIBASE_CMD="$LIQUIBASE_CMD $command"
fi

# Execute command
eval $LIQUIBASE_CMD

# Check exit code
if [[ $? -eq 0 ]]; then
    echo "✅ Liquibase $command completed successfully"
else
    echo "❌ Liquibase $command failed"
    exit 1
fi
