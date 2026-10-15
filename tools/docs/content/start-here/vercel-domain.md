---
title: "Buy your own domain on Vercel (optional)"
description: "Step by step, with screenshots: search for a name, avoid the cheap-first-year renewal trap, buy it, and have Claude Code point it at your website."
section: start-here
order: 36
updated: 2026-10-15
---

Your website already gets a free address like `yourname.vercel.app`. A domain of your own, like `yourname.com`, looks sharper on a resume and costs about $10-15 a year.

This is optional. Do it after [Get your Vercel token](/docs/start-here/vercel-token/), since Claude Code uses that token to connect the domain.

> **Warning:** Domains are non-refundable. Check the spelling before you click Buy.

## 1. Open Domains, then Buy

In your Vercel dashboard, click **Domains** in the left sidebar, then the black **Buy** button at the top right.

![Vercel dashboard with Domains in the sidebar and the Buy button highlighted](https://jddavenport.com/images/docs/vercel-domain/01-domains.png)

## 2. Search, and pick a .com

Type the name you want. Vercel lists the endings that are available, each with its price.

Pick **.com** when you can. Its first-year price is the same as what it costs every year after.

> **Tip:** The $1.99 endings (.online, .site, .store and so on) are only $1.99 for the first year. After that they renew at about $22-44 a year. The checkout screen in step 4 shows the renewal price before you pay.

![Domain search results with the search box, a $1.99 ending and the .com row highlighted](https://jddavenport.com/images/docs/vercel-domain/02-search.png)

## 3. Enter your billing details

Click your domain. Fill in your card, then your name, address and phone. Domain registration requires a real contact address.

![Billing form with the card number and name fields highlighted](https://jddavenport.com/images/docs/vercel-domain/03-billing.png)

## 4. Check the total, then Buy

Scroll down. Check three things before you click:

1. **Renewal:** the line under the domain shows what it costs every year. Autorenew is on by default so you don't lose the name.
2. **Total:** the amount charged today.
3. **Buy:** this is final. Domains are non-refundable.

![Order summary with the renewal line, total and Buy button highlighted](https://jddavenport.com/images/docs/vercel-domain/04-total-buy.png)

## 5. Have Claude Code connect it

Once you've bought it, open Claude Code in your website's folder and paste this, with your domain in place of `yourname.com`:

```text
I just bought yourname.com on Vercel. Using my VERCEL_TOKEN, add it to my
portfolio project as the main domain, along with www.yourname.com, then
tell me when https://yourname.com loads my site.
```

A new domain can take a few minutes to start working. If it doesn't load right away, wait 10 minutes and try again.

> **Note:** The screenshots come from a throwaway demo account. Nothing was purchased.
