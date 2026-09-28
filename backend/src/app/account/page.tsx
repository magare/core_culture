import { Suspense } from "react";
import Link from "next/link";
import { headers } from "next/headers";
import { auth } from "@/lib/auth";
import { env } from "@/lib/env";
import { AccountForm } from "./account-form";

export default async function AccountPage() {
  const session = await auth.api.getSession({ headers: await headers() });
  return <main className="shell account-shell"><header className="masthead"><Link className="wordmark" href="/">CORE CULTURE<span>MEMBER ACCESS</span></Link><Link href="/">Back to platform ↗</Link></header><section className="account-layout"><div><p className="eyebrow">YOUR NEXT CHAPTER</p><h1>Start with<br /><span>yourself.</span></h1><p className="lead">Create your account. Find your rhythm. This first step connects you to the Core Culture platform.</p>{env.MAIL_MODE === "outbox" && <p className="notice">Local development: verification and recovery emails are saved privately in <code>.local/mail</code>. No email is sent unless SMTP is configured.</p>}</div><Suspense fallback={<p>Loading member access…</p>}><AccountForm initiallySignedIn={Boolean(session?.user.emailVerified)} /></Suspense></section></main>;
}
