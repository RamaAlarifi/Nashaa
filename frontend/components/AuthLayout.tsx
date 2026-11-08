import Link from "next/link";
import { Logo } from "./Logo";
import { Icon } from "./Icon";

const JOURNEY = [
  { icon: "idea", text: "Shape your idea", note: "Capture the problem you want to solve" },
  { icon: "spark", text: "Explore with AI", note: "Understand market, customers and risks" },
  { icon: "arrow", text: "Move forward", note: "Meet innovators, partners and investors" },
] as const;

export function AuthLayout({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <div className="auth-layout">
      <aside className="auth-story">
        <Link href="/" aria-label="Nashaa home" className="self-start rounded-lg">
          <Logo variant="reversed" />
        </Link>
        <div className="relative z-10 my-auto py-14">
          <p className="pill !border-white/10 !bg-white/[0.06] !text-turquoise-400">
            <Icon name="spark" className="h-3.5 w-3.5" />
            A new chapter starts here
          </p>
          <h2 className="mt-7 max-w-lg text-4xl font-medium leading-[1.08] tracking-tight text-white xl:text-[3.5rem]">
            Big possibilities.
            <br />
            <span className="bg-gradient-to-r from-turquoise-400 to-brand-300 bg-clip-text text-transparent">
              One idea away.
            </span>
          </h2>
          <p className="mt-6 max-w-sm text-base leading-relaxed text-navy-100/90">
            A considered space for Saudi entrepreneurs to shape an idea,
            understand its potential, and take the next step.
          </p>
          <div className="journey-graphic stagger mt-12" aria-hidden="true">
            {JOURNEY.map((step, i) => (
              <div key={step.text} className="flex items-center gap-4">
                <span className="journey-node">
                  <Icon name={step.icon} />
                </span>
                <span className="min-w-0">
                  <span className="block text-sm font-medium text-white">{step.text}</span>
                  <span className="mt-0.5 block text-xs text-navy-100/70">{step.note}</span>
                </span>
                <span className="ml-auto font-mono text-xs text-navy-100/60">0{i + 1}</span>
              </div>
            ))}
          </div>
        </div>
        <p className="relative z-10 text-xs text-navy-100/70">
          From idea to opportunity. Built around you.
        </p>
      </aside>
      <section className="flex min-w-0 flex-col justify-center px-5 py-10 sm:px-12 lg:px-16">
        <div className="page-enter mx-auto w-full max-w-[27.5rem]">
          <div className="mb-10 flex items-center justify-between lg:hidden">
            <Link href="/" className="inline-block rounded-lg" aria-label="Nashaa home">
              <Logo />
            </Link>
          </div>
          <p className="eyebrow text-brand-700">Your Nashaa workspace</p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-[2.125rem]">
            {title}
          </h1>
          <p className="mb-8 mt-3 text-[0.9375rem] leading-relaxed text-muted-light">
            {description}
          </p>
          <div className="auth-card">{children}</div>
          <p className="mt-8 flex items-center gap-2 text-xs leading-relaxed text-muted-light">
            <Icon name="lock" className="h-3.5 w-3.5 shrink-0" />
            A space to build with confidence. Demonstration data is fictional.
          </p>
        </div>
      </section>
    </div>
  );
}
