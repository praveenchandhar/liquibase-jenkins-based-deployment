#!/bin/bash

echo "🚀 Jenkins Job Setup for Liquibase MongoDB Deployment"
echo "===================================================="

# Configuration
JENKINS_URL="${1:-http://localhost:8080}"
JENKINS_USER="$2"
JENKINS_TOKEN="$3"
JOB_NAME="liquibase-mongodb-deployment"

echo "Jenkins URL: $JENKINS_URL"
echo "Job Name: $JOB_NAME"

# Create job configuration XML
cat > job-config.xml << 'EOF'
<?xml version='1.1' encoding='UTF-8'?>
<org.jenkinsci.plugins.workflow.job.WorkflowJob plugin="workflow-job@2.40">
  <description>MongoDB Liquibase deployment with branch/tag support and dynamic rollback options</description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
        <hudson.model.StringParameterDefinition>
          <name>BRANCH_OR_TAG</name>
          <description>Branch or tag name containing the changesets to deploy</description>
          <defaultValue></defaultValue>
          <trim>true</trim>
        </hudson.model.StringParameterDefinition>
        <hudson.model.ChoiceParameterDefinition>
          <name>LIQUIBASE_ACTION</name>
          <description>Liquibase action to perform</description>
          <choices>
            <string>status</string>
            <string>update</string>
            <string>rollback</string>
          </choices>
        </hudson.model.ChoiceParameterDefinition>
        <hudson.model.ChoiceParameterDefinition>
          <name>ROLLBACK_COUNT</name>
          <description>Number of changesets to rollback (only for rollback action)</description>
          <choices>
            <string>1</string>
            <string>2</string>
            <string>3</string>
            <string>4</string>
            <string>5</string>
            <string>6</string>
            <string>7</string>
            <string>8</string>
            <string>9</string>
            <string>10</string>
          </choices>
        </hudson.model.ChoiceParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
  </properties>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@2.80">
    <scm class="hudson.plugins.git.GitSCM" plugin="git@4.4.4">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>https://github.com/your-org/liquibase-jenkins-based-deployment.git</url>
          <credentialsId>github-credentials</credentialsId>
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>*/main</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
      <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
      <submoduleCfg class="list"/>
      <extensions/>
    </scm>
    <scriptPath>jenkins/Jenkinsfile</scriptPath>
    <lightweight>true</lightweight>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</org.jenkinsci.plugins.workflow.job.WorkflowJob>
EOF

echo "📄 Job configuration created: job-config.xml"

# Create job if credentials provided
if [ -n "$JENKINS_USER" ] && [ -n "$JENKINS_TOKEN" ]; then
    echo "🔐 Creating Jenkins job with provided credentials..."
    
    curl -X POST \
      -u "$JENKINS_USER:$JENKINS_TOKEN" \
      -H "Content-Type: application/xml" \
      --data-binary @job-config.xml \
      "$JENKINS_URL/createItem?name=$JOB_NAME"
    
    if [ $? -eq 0 ]; then
        echo "✅ Jenkins job created successfully!"
        echo "🌐 Access: $JENKINS_URL/job/$JOB_NAME"
    else
        echo "❌ Failed to create job automatically"
        echo "💡 Use manual setup instructions below"
    fi
else
    echo "⚠️  No credentials provided - manual setup required"
fi

echo ""
echo "📋 Manual Setup Instructions:"
echo "1. Go to Jenkins: $JENKINS_URL"
echo "2. Click 'New Item'"
echo "3. Name: $JOB_NAME"
echo "4. Type: Pipeline"
echo "5. Use the job-config.xml content or configure manually"
echo ""
echo "📋 Next Steps:"
echo "1. ✅ Configure GitHub credentials (ID: github-credentials)"
echo "2. ✅ Update repository URL in job config"
echo "3. ✅ Test with a sample branch"

echo ""
echo "🎉 Setup script completed!"
