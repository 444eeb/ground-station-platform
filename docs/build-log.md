11#Build log
## Stage 0 — Guardrails (26 Nov 2026)

**What I did**
Before writing any code or creating any infrastructure, I set up cost and
security controls:
- Created the public GitHub repo with GitHub secret scanning and push
  protection enabled, so a commit containing a key is rejected.
- Started a Google Cloud free trial and created the project. I added a £5
  monthly budget with alerts at 25/50/90% actual and 100% forecast spend,
  and excluded promotional credits so that the budget tracks real usage
  rather than showing £0 while the trial credit absorbs it.
- Created an AWS account on the Free plan (no payment card required), turned
  on MFA for my AWS Builder ID sign-in, and added a zero-spend budget.
- Turned on 2-step verification on GitHub and Google.

**What went wrong**
- AWS's sign-up has moved to a new "Settings / Projects" model, which did not
  match the guide I was following. While exploring it, I closed my first
  project by mistake, which closed its AWS account.
- Google Cloud's budget page had renamed "Credits" to "Savings", so the
  option to exclude trial credit was in a different place.

**How I fixed it**
- I checked the project page, which confirmed the project was in a 90-day
  post-closure period and could be reopened via AWS Support. Because the Free
  plan and credits belonged to my sign-in rather than the closed project, I
  created a new project instead. The closed one incurs no cost.
- For the budget, I found that the trial credit counts as "Promotional
  credits" and unticked only that option.

**What I learned**
- Budgets only send alerts; they don't stop resources. Staying on free plans
  and tearing resources down are the real protection.
- In cloud consoles, read what an action does before confirming it.


## Stage 1 — Windows workstation (27 Nov 2026)

**What I did**
- Installed WSL2 and Ubuntu 26.04 LTS. I checked the current releases first
  and chose the newest LTS after confirming Docker and HashiCorp support it.
- Limited WSL to 8 GB RAM, 6 CPUs and 4 GB swap with a `.wslconfig` file so
  that Windows stays responsive.
- Installed Docker Engine from Docker's official apt repository, ran it as a
  systemd service and added my user to the `docker` group (aware that this
  group is effectively root access).
- Installed gcloud, Terraform, kubectl, kind and AWS CLI v2. For single-binary
  tools I verified SHA-256 checksums before installing.
- Set up an Ed25519 SSH key for GitHub, verified GitHub's host fingerprint
  against its published value, and enabled SSH commit signing. My commits now
  show as "Verified" and use a private noreply email.
- Added a hardened .gitignore (Terraform state, credentials, private keys) and
  a pre-commit hook that runs gitleaks on every commit. I tested it by trying
  to commit a fake GitHub token, and the commit was blocked.

**What went wrong**
- My first plan was Ubuntu 24.04. When I checked, 26.04 LTS was already out,
  so I installed WSL on its own first, then picked 26.04 from the catalogue.
- A typo in a `ps` command (missing `-o`) gave an error; I read the usage
  message and fixed it.
- The terminal seemed to freeze. It had gone into "Select" mode after a
  click; pressing Esc fixed it.

**What I learned**
- apt repositories verify packages using the publisher's GPG key, while
  standalone downloads need a manual checksum check.
- SSH host fingerprints protect against connecting to an impostor server.
  It's the same trust problem that TLS certificates solve.
