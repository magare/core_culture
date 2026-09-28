import { config } from "dotenv";
import { eq } from "drizzle-orm";

config({ path: ".env.local", quiet: true });
const { env } = await import("../src/lib/env");
if (!env.isLocal) throw new Error("Demo seeds are restricted to local development.");
const { db, pool } = await import("../src/db/index");
const { user, trainers, trainerSlots } = await import("../src/db/schema");
const demos = [
  { slug: "demo-strength", name: "Demo Strength Coach", headline: "Build strength with intention.", specialties: ["Strength", "Personal training"], yearsExperience: 8 },
  { slug: "demo-movement", name: "Demo Movement Coach", headline: "Move well. Feel stronger.", specialties: ["Mobility", "Yoga"], yearsExperience: 6 },
  { slug: "demo-conditioning", name: "Demo Conditioning Coach", headline: "Find your next level.", specialties: ["Conditioning", "Endurance"], yearsExperience: 5 },
];
try {
  for (const demo of demos) {
    await db.transaction(async (tx) => {
      const userId = demo.slug;
      await tx.insert(user).values({ id: userId, name: demo.name, email: `${demo.slug}@example.invalid`, role: "trainer" }).onConflictDoNothing();
      await tx.insert(trainers).values({ userId, slug: demo.slug, headline: demo.headline, specialties: demo.specialties,
        yearsExperience: demo.yearsExperience, bio: "A fictional trainer profile for local development. Replace this demonstration content with your club's approved trainer details before launch.",
      }).onConflictDoNothing();
      const [trainer] = await tx.select().from(trainers).where(eq(trainers.userId, userId));
      for (let day = 1; day <= 7; day++) {
        const startsAt = new Date();
        startsAt.setUTCDate(startsAt.getUTCDate() + day);
        startsAt.setUTCHours(4, 30, 0, 0); // 10:00 in Asia/Kolkata.
        await tx.insert(trainerSlots).values({ trainerId: trainer.id, startsAt, endsAt: new Date(startsAt.getTime() + 3600_000) }).onConflictDoNothing();
      }
    });
  }
  console.log("Seeded 3 explicitly fictional trainers and seven upcoming slots each. No shared passwords or admin accounts were created.");
} finally { await pool.end(); }
