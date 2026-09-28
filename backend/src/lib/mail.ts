import { randomUUID } from "node:crypto";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import nodemailer from "nodemailer";
import { env } from "./env";

type Message = { to: string; subject: string; text: string };
const transport = env.MAIL_MODE === "smtp" ? nodemailer.createTransport(env.SMTP_URL!) : null;

export async function sendMail(message: Message) {
  if (transport) {
    await transport.sendMail({ from: env.MAIL_FROM, ...message });
    return;
  }
  // Local-only test mail. This directory is ignored by git and never served.
  const directory = path.resolve(env.MAIL_OUTBOX_DIR);
  await mkdir(directory, { recursive: true, mode: 0o700 });
  await writeFile(path.join(directory, `${Date.now()}-${randomUUID()}.json`), JSON.stringify({
    ...message, createdAt: new Date().toISOString(),
  }, null, 2), { flag: "wx", mode: 0o600 });
}
