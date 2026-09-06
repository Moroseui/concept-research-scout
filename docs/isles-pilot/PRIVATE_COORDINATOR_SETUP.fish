# Plan-only fish command sheet. Prints commands; never provisions resources.
set -l project isles24-pilot-20260905
set -l region us-central1
set -l zone us-central1-a
printf '%s\n' 'PROPOSAL ONLY: approve the resource/budget plan and supply billing account first.'
printf '%s\n' "gcloud projects create $project" \
  "gcloud config set project $project" \
  'read -P "Approved billing account ID: " ISLES_BILLING_ACCOUNT' \
  'gcloud billing projects link isles24-pilot-20260905 --billing-account $ISLES_BILLING_ACCOUNT' \
  'gcloud services enable compute.googleapis.com batch.googleapis.com storage.googleapis.com artifactregistry.googleapis.com iap.googleapis.com' \
  'gcloud compute networks create pilot-private --subnet-mode custom' \
  "gcloud compute networks subnets create pilot-central --network pilot-private --region $region --range 10.24.0.0/24 --enable-private-ip-google-access" \
  'gcloud iam service-accounts create pilot-coordinator' \
  'gcloud iam service-accounts create pilot-worker' \
  "gcloud storage buckets create gs://$project-inputs --location $region --uniform-bucket-level-access --public-access-prevention" \
  "gcloud storage buckets create gs://$project-private --location $region --uniform-bucket-level-access --public-access-prevention" \
  "gcloud storage buckets create gs://$project-aggregate --location $region --uniform-bucket-level-access --public-access-prevention" \
  "gcloud artifacts repositories create pilot-images --repository-format docker --location $region" \
  'STOP: review exact least-privilege IAM, firewall, container digest, startup service and Batch template before creating a VM or submitting any task.'
