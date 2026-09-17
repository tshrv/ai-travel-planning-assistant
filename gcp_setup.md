# Steps for GCP setup

Follow steps below to set up required services and permissions from google cloud platform.

```sh
export PROJECT_ID="YOUR_REAL_PROJECT_ID"
export REGION="global"

gcloud config set project "$PROJECT_ID"

gcloud config get-value project
gcloud projects describe "$PROJECT_ID"

# enable requried apis
# aiplatform.googleapis.com (GCP Agent Platform)
# discoveryengine.googleapis.com (Google Ranking API)
gcloud services enable \
  aiplatform.googleapis.com \
  discoveryengine.googleapis.com \
  --project="$PROJECT_ID"

# verify
gcloud services list --enabled \
  --project="$PROJECT_ID" \
  --filter="config.name:(aiplatform.googleapis.com OR discoveryengine.googleapis.com)"

# billing enbaled
gcloud beta billing projects describe "$PROJECT_ID"

# local auth - ADC
gcloud auth application-default login

# verify
gcloud auth application-default print-access-token

# set ADC quota project
gcloud auth application-default set-quota-project "$PROJECT_ID"

# grant role
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="user:YOUR_EMAIL@example.com" \
  --role="roles/aiplatform.user"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="user:YOUR_EMAIL@example.com" \
  --role="roles/discoveryengine.viewer"

# verify iam
gcloud projects get-iam-policy "$PROJECT_ID" \
  --flatten="bindings[].members" \
  --filter="bindings.members:YOUR_EMAIL@example.com" \
  --format="table(bindings.role)"

# ranking api
gcloud services enable \
  discoveryengine.googleapis.com \
  --project="$PROJECT_ID"
```