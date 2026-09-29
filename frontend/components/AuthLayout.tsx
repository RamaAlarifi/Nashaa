import Link from "next/link";
import { Logo } from "./Logo";
import { Icon } from "./Icon";

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
        <Link href="/" aria-label="Nashaa home">
          <Logo variant="reversed" />
        </Link>
        <div className="relative z-10 my-auto py-16">
          <p className="eyebrow text-turquoise-400">
            A new chapter starts here
          </p>
          <h2 className="mt-6 max-w-lg text-4xl font-medium leading-tight tracking-tight text-white lg:text-6xl">
            Big possibilities.
            <br />
            <span className="text-turquoise-400">One idea away.</span>
          </h2>
          <p className="mt-6 max-w-sm text-base leading-relaxed text-navy-100">
            A considered space for Saudi entrepreneurs to shape an idea,
            understand its potential, and take the next step.
          </p>
          <div className="journey-graphic mt-12" aria-hidden="true">
            {[
              { icon: "idea", text: "Shape your idea" },
              { icon: "spark", text: "Explore with AI" },
              { icon: "arrow", text: "Move forward" },
            ].map((step, i) => (
              <div key={step.text} className="flex items-center gap-4">
                <span className="journey-node">
                  <Icon name={step.icon as "idea" | "spark" | "arrow"} />
                </span>
                <span className="text-sm text-white">{step.text}</span>
                <span className="ml-auto font-mono text-xs text-navy-100">
                  0{i + 1}
                </span>
              </div>
            ))}
          </div>
        </div>
        <p className="relative z-10 text-xs text-navy-100">
          From idea to opportunity. Built around you.
        </p>
      </aside>
      <section className="flex min-w-0 flex-col justify-center px-6 py-12 sm:px-12 lg:px-16">
        <div className="mx-auto w-full max-w-md page-enter">
          <Link
            href="/"
            className="mb-10 inline-block lg:hidden"
            aria-label="Nashaa home"
          >
            <Logo />
          </Link>
          <p className="eyebrow text-brand-700">Your Nashaa workspace</p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
            {title}
          </h1>
          <p className="mb-8 mt-3 text-sm leading-relaxed text-muted-light">
            {description}
          </p>
          {children}
          <p className="mt-10 border-t border-navy/10 pt-5 text-xs leading-relaxed text-muted-light">
            A space to build with confidence. Demonstration data is fictional.
          </p>
        </div>
      </section>
    </div>
  );
}
