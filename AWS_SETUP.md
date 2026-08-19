# One-time AWS + GitHub setup for Continuous Deployment

The CI workflows (`frontend-ci.yaml`, `backend-ci.yaml`) work with no setup — they only lint,
test, and build a local Docker image. The **CD** workflows additionally push images to ECR and
deploy to EKS, which needs real AWS infrastructure and a couple of GitHub repo secrets that only
you can create (Claude has no AWS credentials and no access to your repo settings).

## 1. Create the AWS infrastructure

```bash
cd setup/terraform
terraform apply
```

Type `yes` when prompted. This creates (fixed names the workflows already expect):

- ECR repositories named `frontend` and `backend`
- An EKS cluster named `cluster` in `us-east-1`
- An IAM user named `github-action-user` that GitHub Actions will authenticate as

**Remember to `terraform destroy` when you're done** — this infrastructure costs money while running.

## 2. Generate AWS access keys for GitHub Actions

1. Open the IAM console → Users → `github-action-user` → Security credentials
2. Under Access keys, choose **Create access key** → **Application running outside AWS**
3. Copy the generated Access Key ID and Secret Access Key (shown once)

## 3. Authorize that IAM user inside the EKS cluster

```bash
cd setup
./init.sh
```

This adds the `github-action-user` IAM ARN to the cluster's `aws-auth` ConfigMap so the workflow's
`kubectl apply` calls are authorized.

## 4. Add the two secrets to your GitHub repo

Repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Name                    | Value                                  |
| ------------------------ | --------------------------------------- |
| `AWS_ACCESS_KEY_ID`     | from step 2                            |
| `AWS_SECRET_ACCESS_KEY` | from step 2                            |

## 5. Add the frontend API URL as a repo variable

The frontend needs to know where the backend lives at build time. Same page, **Variables** tab →
**New repository variable**:

| Name                       | Value                                                          |
| --------------------------- | ---------------------------------------------------------------- |
| `REACT_APP_MOVIE_API_URL`  | the backend's LoadBalancer URL (see step 6, run backend CD first) |

## 6. First deploy order

1. Push a change under `starter/backend/**` to `main` (or run `backend-cd.yaml` manually) so the
   backend Service gets created.
2. Get its public URL: `kubectl get svc backend -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'`
3. Set that as `REACT_APP_MOVIE_API_URL` (step 5), then push/run the frontend CD workflow so the
   frontend gets built pointing at the real backend.

## Verifying

```bash
kubectl get pods
kubectl get svc
```

Open the frontend LoadBalancer hostname in a browser — it should show the movie list, confirming
the backend URL was baked in correctly. `curl http://<backend-lb-hostname>/movies` should return
the JSON movie list directly.
