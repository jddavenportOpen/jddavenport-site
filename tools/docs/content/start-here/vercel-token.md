---
title: "Get your Vercel token for Claude Code"
description: "Step by step, with screenshots: create a free Vercel account, make an access token, and hand it to Claude Code so it can put your website live."
section: start-here
order: 35
updated: 2026-10-15
---

Claude Code can build you a website in minutes. To put it live on the internet, it needs permission to deploy to your Vercel account. That permission is a **token**: a long, password-like key you create once and hand to Claude Code.

This takes about 5 minutes. Do it before class.

**You need:** a laptop with Claude Code installed, a phone that can receive texts, and a GitHub account (free at [github.com](https://github.com) if you don't have one).

> **Warning:** Treat the token like a password. Anyone who has it can control your Vercel account. Don't paste it into a chat, a doc, Slack, or GitHub. You only give it to Claude Code, in step 8.

## 1. Sign up with GitHub

Go to [vercel.com/signup](https://vercel.com/signup) and click **Continue with GitHub**. Approve the GitHub screen that follows.

![Vercel sign-up page with Continue with GitHub highlighted](https://jddavenport.com/images/docs/vercel-token/01-sign-up.png)

## 2. Verify your phone

Vercel may ask for a phone number. Enter yours, click **Continue**, then type the code it texts you.

![Phone verification screen with the phone field and Continue highlighted](https://jddavenport.com/images/docs/vercel-token/02-phone.png)

## 3. Pick the free plan

Choose **I'm working on personal projects**. That's the **Hobby** plan, which is free. Type your name and click **Continue**.

> **Tip:** Don't pick "commercial projects." That starts a Pro trial that turns into a paid plan.

![Choose a Plan screen with the personal projects option, name field and Continue highlighted](https://jddavenport.com/images/docs/vercel-token/03-hobby.png)

## 4. Open your account settings

On your dashboard, click **your name in the bottom-left corner**, then the **gear icon** at the top of the menu that opens.

![Account menu open, with your name at the bottom left and the gear icon highlighted](https://jddavenport.com/images/docs/vercel-token/04-account-menu.png)

## 5. Go to Tokens

In the left sidebar, click **Tokens**. You can also go straight to [vercel.com/account/settings/tokens](https://vercel.com/account/settings/tokens).

![Account settings sidebar with Tokens highlighted](https://jddavenport.com/images/docs/vercel-token/05-tokens.png)

## 6. Create the token

Fill in the **Create Token** form:

1. **Token name:** `claude-code`
2. **Scope:** click it, choose your account name, then **All Projects**
3. **Expiration:** **1 Year**
4. Click **Create**

![Create Token form filled in: name claude-code, scope set to the account, expiration 1 Year, Create highlighted](https://jddavenport.com/images/docs/vercel-token/06-create-form.png)

## 7. Copy it right away

Click the **copy icon** next to the token. Vercel shows it **only once**. If you close this box before copying, delete the token and make a new one.

![Token Created dialog with the token blurred and the copy icon highlighted](https://jddavenport.com/images/docs/vercel-token/07-copy-token.png)

## 8. Give it to Claude Code

Open Claude Code in your course folder and paste this, with your token in place of `<PASTE TOKEN>`:

```text
Here is my Vercel token: <PASTE TOKEN>. Save it as VERCEL_TOKEN in a .env file in
my course folder, add .env to .gitignore so it never goes to GitHub, then install
the Vercel CLI and confirm the token works by running: vercel whoami
```

You're done when Claude Code shows your Vercel username from `vercel whoami`.

## If something goes wrong

- **Lost the token, or pasted it somewhere public?** Go back to the Tokens page, open the **⋯** menu on that token, click **Delete**, and create a new one.
- **`vercel whoami` fails?** The token was probably copied with a missing character. Make a new one and paste it again.
- **No text from Vercel?** Check the number and country code, then click Back and try again.

> **Note:** The screenshots come from a throwaway demo account. Its token was deleted right after the screenshot was taken.
