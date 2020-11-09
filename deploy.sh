ROOT="$(git rev-parse --show-toplevel)"
source ${ROOT}/env/$1


echo "Deploying Master Account Pre-reqs"

for REGION in $REGIONS; do
    aws cloudformation deploy \
    --template-file org-master/regional_pre_reqs.yaml \
    --stack-name "${UNIQUE_NAME}-security-hub-pre-reqs-stack" \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides \
    ArtefectBucketPrefix="${ARTEFACT_BUCKET_PREFIX}" \
    --tags \
    ServiceCode="${SERVICE_CODE}" \
    ServiceName="${SERVICE_NAME}" \
    ServiceOwner="${SERVICE_OWNER}" \
    --profile ${MASTER_ACCOUNT_PROFILE} \
    --region "${REGION}"
done

echo "Deploying Master Account Stacks"

for REGION in $REGIONS; do
    aws cloudformation package \
    --template-file org-master/security_hub_master_account.yaml \
    --output-template-file org-master/security_hub_master_account_output.yaml \
    --s3-bucket "${ARTEFACT_BUCKET_PREFIX}-${REGION}" \
    --profile ${MASTER_ACCOUNT_PROFILE} \
    --region "${REGION}"

    aws cloudformation deploy \
    --template-file org-master/security_hub_master_account_output.yaml \
    --stack-name "${UNIQUE_NAME}-security-hub-master-account-stack" \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides \
    UniqueName="${UNIQUE_NAME}" \
    --tags \
    ServiceCode="${SERVICE_CODE}" \
    ServiceName="${SERVICE_NAME}" \
    ServiceOwner="${SERVICE_OWNER}" \
    --profile ${MASTER_ACCOUNT_PROFILE} \
    --region "${REGION}"
done

echo "Deploying Target Account Stacks"

aws cloudformation deploy \
    --template-file target-account/security_hub_target_role.yaml \
    --stack-name "${UNIQUE_NAME}-security-hub-target-account-role" \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides \
    OrgId="${ORG_ID}" \
    UniqueName="${UNIQUE_NAME}" \
    --tags \
    ServiceCode="${SERVICE_CODE}" \
    ServiceName="${SERVICE_NAME}" \
    ServiceOwner="${SERVICE_OWNER}" \
    --profile ${TARGET_ACCOUNT_PROFILE} \
    --region "eu-west-2"

for REGION in $REGIONS; do
    aws cloudformation deploy \
    --template-file target-account/security_hub_target_account.yaml \
    --stack-name "${UNIQUE_NAME}-security-hub-target-account-stack" \
    --capabilities CAPABILITY_NAMED_IAM \
    --tags \
    ServiceCode="${SERVICE_CODE}" \
    ServiceName="${SERVICE_NAME}" \
    ServiceOwner="${SERVICE_OWNER}" \
    --profile ${TARGET_ACCOUNT_PROFILE} \
    --region "${REGION}"
done
