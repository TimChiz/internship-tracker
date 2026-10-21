#This is a document that we must keep coming back to, to ensure we are hitting every mark. 

## 1. Team setup and roles


- [ ] A short description of each person's role written down (needed for everyone's PDF)
- [ ] Work started early, aiming to finish before week 15

## 2. GitHub setup and collaboration rules

- [ ] All project work lives in the GitHub repo (other tools are fine internally but aren't graded)
- [ ] Each person's contributions can be traced in GitHub
- [ ] **Branching / merging pattern** agreed and written down 
- [ ] **PR template** created so every PR description has the same format
- [ ] **Automatic checks** set up (e.g. GitHub Actions for tests and linting)
- [ ] Collaboration rules written in the repo (e.g. `CONTRIBUTING.md`)
- [ ] Tasks tracked in **GitHub Projects**, each with an assignee (everyone has to link the tasks they owned)
- [ ] Non-coding work (designs, mockups) also tracked and stored **in GitHub**



## 3. Continuous development

- [ ] Commits and code are spread **as evenly as possible**, both over time and across team members
- [ ] No pile-up of work at the end 


## 4. Pull requests: EVERY PR NEEDS TO ACTUALLY MAKE SENSE

A PR counts as meaningful only if it meets **all** of these:

- [ ] It implements a **small component** of the project
- [ ] It has a **clear description** of the feature inside the PR
- [ ] It has **docstrings and/or tests** where applicable
- [ ] It is **self-contained**: someone can understand it by reading only the PR
- [ ] It was **reviewed and approved** by a team member
- [ ] It was **successfully merged** into the main/master branch

Also:

- [ ] All explanations and documentation go **in the PRs themselves**, not in the PDF
- [ ] Extensive documentation is allowed as a gradable PR
- [ ] Each team member has several meaningful PRs that they authored and coded

## 5. Code reviews

- [ ] **Every team member reviews** other members' PRs.
- [ ] Reviews are good quality: lots of useful feedback, constructive criticism, and **specific actions** to improve the work
- [ ] Every review comment is **addressed by the author**, either by changing the code or by explaining why no change is needed
- [ ] **Automated review comments** (bots, AI reviewers, CI) are addressed and resolved exactly like human ones

## 6. MVPs

- [ ] **At least 3 MVPs**, and the last one is the final version
  - [ ] MVP 1 (name and label each with version and date)
  - [ ] MVP 2 
  - [ ] MVP 3 (final) 
- [ ] The reason for every change or pivot between MVPs is recorded (needed for the demo video)

## 7. App features (took them from the demo requirements)

- [ ] Users can **create an account**
- [ ] Users can **log in**
- [ ] Users can **log out**
- [ ] The major features work. So for us that would for example be:
  - [ ] Internship applications sorted by deadline priority
  - [ ] Progress sharing with others
- [ ] The app is a **useful product**

## 8. Deployment

- [ ] The app runs on a modern machine with a common OS (Linux, Windows, macOS)
- [ ] It assumes nothing else about the deployer's machine or setup
- [ ] Deployment is as simple and smooth as possible for whoever deploys it
- [ ] Clear deployment and run instructions are in the repo (e.g. README)
- [ ] Deployment tested on a fresh machine

## 9. API keys and external services

- [ ] **If the app uses an LLM:** it still works without the deployer having their own key
- [ ] **All other API keys the app needs are provided**, so no one has to sign up for a third-party service to run it
- [ ] The way keys are shared has been checked for abuse and cost risk (e.g. restricted, free-tier, or rate-limited keys)

## 10. Group demo video

- [ ] **One** recording for the whole group
- [ ] Screen recording made with Loom or a similar tool
- [ ] Includes **audio narration** explaining each step while it happens
- [ ] **Every team member presents** a portion
- [ ] Short script written together
- [ ] Length is about **10–12 minutes**
- [ ] Covers:
  - [ ] Creating an account
  - [ ] Logging in
  - [ ] Major features of the app
  - [ ] Logging out
  - [ ] High-level overview of the tech stack
  - [ ] How the app is deployed
- [ ] **About 3–5 minutes** on how the MVPs progressed and why there were changes or pivots

## 11. User testing


- [ ] Have the product tested by both target users and not target users
- [ ] Aim to have a user testing each MVP, and iterate based on their feedback. 

