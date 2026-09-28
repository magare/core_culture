import Link from "next/link";

const services = [
  { number: "01", title: "Member accounts", description: "Registration, email verification, secure sessions, and password recovery.", path: "/account", label: "Open account access" },
  { number: "02", title: "Find your trainer", description: "Trainer profiles, specialties, member preferences, and upcoming availability.", path: "/api/trainers", label: "View trainer API" },
  { number: "03", title: "Make time for progress", description: "Protected bookings and cancellations, with overlapping sessions prevented by PostgreSQL.", path: "/api/health", label: "Check service health" },
];

export default function Home() {
  return <main className="shell">
    <header className="masthead"><Link className="wordmark" href="/">CORE CULTURE<span>THE PLATFORM</span></Link><span className="badge">BACKEND / V0.1</span></header>
    <section className="hero"><p className="eyebrow">A STRONGER FOUNDATION</p><h1>Built for<br /><span>what comes next.</span></h1><p className="lead">The member services behind Core Culture. A connected foundation for people, trainers, and time well spent.</p><Link className="button" href="/account">Explore member access <span aria-hidden="true">↗</span></Link></section>
    <section className="services" aria-label="Backend capabilities">{services.map((service) => <article key={service.number}><span className="number">{service.number}</span><h2>{service.title}</h2><p>{service.description}</p><Link href={service.path}>{service.label} <span aria-hidden="true">↗</span></Link></article>)}</section>
    <footer><p>Next.js · TypeScript · PostgreSQL</p><p>Development foundation. The marketing website remains separate.</p></footer>
  </main>;
}
