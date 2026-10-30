// brand-fnguide-CI (internet-facing Jenkins)
// SCM: https://igit.fnguide.com/design/brand-design-management.git
// GitLab: Accepted Merge Request Events only, target ^(production|pre-production)$
// Branch Specifier: ${gitlabTargetBranch}; Script Path: Jenkinsfile
// Keep the wisereport Checkout -> Build -> Package -> Sign -> Drop contract.
pipeline {
    agent any

    options {
        disableConcurrentBuilds()
    }

    environment {
        APP_NAME   = 'brand-fnguide'
        BUILD_VER  = "${env.BUILD_NUMBER}"
        SFTP_DROP  = '/var/share/gitlab'
        NEXUS_URL  = 'http://10.200.40.128:8081'
        NEXUS_REPO = 'deploy-releases'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    def branch = (env.GIT_BRANCH ?: '')
                        .replaceAll('refs/heads/', '')
                        .replaceAll('origin/', '')
                        .trim()
                    env.DEPLOY_ENV = (branch == 'production') ? 'prod' : 'pre'
                    env.ARTIFACT = "${env.APP_NAME}-${env.BUILD_VER}.tar.gz"
                    echo "Branch: ${branch}; environment: ${env.DEPLOY_ENV}; artifact: ${env.ARTIFACT}"
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh '''#!/bin/bash
set +x
set -euo pipefail
docker build \
    --build-arg BUILD_VERSION="$BUILD_VER" \
    --build-arg DEPLOY_ENV="$DEPLOY_ENV" \
    --build-arg GIT_COMMIT="$GIT_COMMIT" \
    -t "$APP_NAME:$BUILD_VER" .
docker images "$APP_NAME:$BUILD_VER" --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}'
'''
            }
        }

        stage('Package') {
            steps {
                sh '''#!/bin/bash
set +x
set -euo pipefail
docker save "$APP_NAME:$BUILD_VER" | gzip > "$ARTIFACT"
echo "Artifact: $ARTIFACT"
du -sh "$ARTIFACT"
'''
            }
        }

        stage('Sign') {
            steps {
                withCredentials([file(credentialsId: 'GPG_DEPLOY_KEY', variable: 'GPG_KEY')]) {
                    sh '''#!/bin/bash
set +x
set -euo pipefail
gpg --batch --import "$GPG_KEY"
gpg --batch --yes --detach-sign --armor \
    --default-key fnguide.it@fnguide.com "$ARTIFACT"
sha256sum "$ARTIFACT" > "$ARTIFACT.sha256"
echo "Signature: $ARTIFACT.asc"
'''
                }
            }
        }

        stage('Transfer to SFTP Drop') {
            steps {
                sh '''#!/bin/bash
set +x
set -euo pipefail
TARGET_DIR="$SFTP_DROP/$APP_NAME/$DEPLOY_ENV"
mkdir -p "$TARGET_DIR"
chgrp deploy_user "$SFTP_DROP/$APP_NAME" "$TARGET_DIR" 2>/dev/null || true
chmod 775 "$SFTP_DROP/$APP_NAME" "$TARGET_DIR" 2>/dev/null || true
find "$TARGET_DIR" -maxdepth 1 -type f \
    '(' -name '*.tar.gz' -o -name '*.tar.gz.asc' -o -name '*.tar.gz.sha256' ')' \
    -exec rm -f {} +

# Expose the archive only after all three files have been copied completely.
cp "$ARTIFACT.asc" "$TARGET_DIR/"
cp "$ARTIFACT.sha256" "$TARGET_DIR/"
cp "$ARTIFACT" "$TARGET_DIR/$ARTIFACT.tmp"
chgrp deploy_user "$TARGET_DIR/$ARTIFACT.asc" "$TARGET_DIR/$ARTIFACT.sha256" "$TARGET_DIR/$ARTIFACT.tmp" 2>/dev/null || true
chmod 664 "$TARGET_DIR/$ARTIFACT.asc" "$TARGET_DIR/$ARTIFACT.sha256" "$TARGET_DIR/$ARTIFACT.tmp"
mv -f "$TARGET_DIR/$ARTIFACT.tmp" "$TARGET_DIR/$ARTIFACT"
echo "SFTP Drop 저장 완료 [$DEPLOY_ENV]:"
ls -lh "$TARGET_DIR/"
'''
            }
        }
    }

    post {
        success {
            echo "CI 완료 [${env.DEPLOY_ENV}]: ${env.ARTIFACT}"
        }
        failure {
            echo "CI 실패: ${env.BUILD_URL}"
        }
        cleanup {
            sh '''#!/bin/bash
set +x
set -e
if [ -n "${ARTIFACT:-}" ]; then
    rm -f "$ARTIFACT" "$ARTIFACT.asc" "$ARTIFACT.sha256"
fi
docker rmi "$APP_NAME:$BUILD_VER" 2>/dev/null || true
'''
        }
    }
}
