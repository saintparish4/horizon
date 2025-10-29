import Image from 'next/image';

export default function Home() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-white dark:bg-black">
      {/* Ambient gradient orbs */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-40 -top-40 h-96 w-96 rounded-full bg-gradient-to-br from-zinc-100 to-transparent opacity-60 blur-3xl dark:from-zinc-900" />
        <div className="absolute -right-40 top-1/4 h-96 w-96 rounded-full bg-gradient-to-bl from-zinc-100 to-transparent opacity-40 blur-3xl dark:from-zinc-900" />
        <div className="absolute -bottom-40 left-1/3 h-96 w-96 rounded-full bg-gradient-to-tr from-zinc-50 to-transparent opacity-30 blur-3xl dark:from-zinc-950" />
      </div>

      {/* Noise texture overlay */}
      <div className="pointer-events-none absolute inset-0 opacity-[0.015] dark:opacity-[0.02]" style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' /%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' /%3E%3C/svg%3E")`,
      }} />

      {/* Navigation */}
      <nav className="fixed top-0 z-50 w-full border-b border-zinc-200/50 bg-white/80 backdrop-blur-xl dark:border-zinc-800/50 dark:bg-black/80">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center">
        <Image
                src="/favicon.ico"
                alt="Antler Logo"
                width={32}
                height={32}
                className="h-8 w-8"
              />
            </div>
            <span className="text-lg font-semibold tracking-tight text-black dark:text-white">Antler</span>
          </div>
          
          <div className="hidden items-center gap-8 md:flex">
            <a href="#features" className="text-sm font-medium text-zinc-600 transition-colors hover:text-black dark:text-zinc-400 dark:hover:text-white">
              Features
            </a>
            <a href="#how-it-works" className="text-sm font-medium text-zinc-600 transition-colors hover:text-black dark:text-zinc-400 dark:hover:text-white">
              How it Works
            </a>
            <a href="#pricing" className="text-sm font-medium text-zinc-600 transition-colors hover:text-black dark:text-zinc-400 dark:hover:text-white">
              Pricing
            </a>
            <a href="#docs" className="text-sm font-medium text-zinc-600 transition-colors hover:text-black dark:text-zinc-400 dark:hover:text-white">
              Docs
            </a>
            <button className="rounded-full bg-black px-6 py-2 text-sm font-medium text-white transition-all hover:scale-105 active:scale-95 dark:bg-white dark:text-black">
              Get Started
            </button>
          </div>

          <button className="md:hidden">
            <svg className="h-6 w-6 text-zinc-600 dark:text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </nav>
      
      {/* Hero Section */}
      <section className="relative flex min-h-screen flex-col items-center justify-center px-6 py-32">
        {/* Logo/Brand with subtle animation */}
        <div className="mb-20 animate-in fade-in duration-1000">
          <div className="relative">
            <div className="absolute -inset-4 rounded-lg bg-gradient-to-r from-zinc-200/50 to-zinc-100/50 opacity-0 blur-xl transition-opacity duration-700 group-hover:opacity-100 dark:from-zinc-800/50 dark:to-zinc-900/50" />
            <h2 className="relative text-sm font-medium tracking-[0.25em] text-zinc-400 transition-colors duration-300 hover:text-zinc-600 dark:text-zinc-600 dark:hover:text-zinc-400">
              ANTLER
            </h2>
          </div>
        </div>

        {/* Hero section with gradient text */}
        <div className="max-w-5xl space-y-10 text-center animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-150">
          <h1 className="relative text-6xl font-extralight leading-[1.08] tracking-[-0.02em] text-black dark:text-white sm:text-7xl md:text-8xl lg:text-9xl">
            <span className="inline-block">Memory</span>{" "}
            <span className="inline-block bg-gradient-to-br from-zinc-900 via-zinc-600 to-zinc-400 bg-clip-text text-transparent dark:from-zinc-100 dark:via-zinc-400 dark:to-zinc-600">
              infrastructure
            </span>
            <br />
            <span className="inline-block text-5xl font-extralight text-zinc-400 dark:text-zinc-600 sm:text-6xl md:text-7xl lg:text-8xl">
              for AI agents
            </span>
          </h1>
          
          <p className="mx-auto max-w-2xl text-xl font-light leading-[1.7] tracking-[-0.01em] text-zinc-500 dark:text-zinc-500 sm:text-2xl md:text-3xl">
            So your AI systems remember, learn,<br className="hidden sm:block" /> and get smarter over time.
          </p>
        </div>

        {/* Enhanced CTAs */}
        <div className="mt-20 flex flex-col gap-4 sm:flex-row animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-300">
          <button className="group relative overflow-hidden rounded-full bg-black px-10 py-4 text-sm font-medium tracking-wide text-white shadow-lg shadow-black/10 transition-all duration-300 hover:scale-[1.02] hover:shadow-xl hover:shadow-black/20 active:scale-[0.98] dark:bg-white dark:text-black dark:shadow-white/10 dark:hover:shadow-white/20">
            <span className="relative z-10 flex items-center gap-2">
              Get Started
              <svg className="h-4 w-4 transition-transform duration-300 group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </span>
            <div className="absolute inset-0 bg-gradient-to-r from-zinc-800 via-zinc-700 to-black opacity-0 transition-opacity duration-300 group-hover:opacity-100 dark:from-zinc-200 dark:via-zinc-300 dark:to-white" />
          </button>
          
          <button className="group relative overflow-hidden rounded-full border border-zinc-200/80 bg-white/50 px-10 py-4 text-sm font-medium tracking-wide text-zinc-900 backdrop-blur-sm transition-all duration-300 hover:scale-[1.02] hover:border-zinc-300 hover:bg-white active:scale-[0.98] dark:border-zinc-800/80 dark:bg-black/50 dark:text-zinc-100 dark:hover:border-zinc-700 dark:hover:bg-black">
            <span className="flex items-center gap-2">
              Documentation
            </span>
          </button>
        </div>

        {/* Premium feature cards */}
        <div className="mt-40 grid max-w-7xl grid-cols-1 gap-8 px-4 md:grid-cols-3 animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-500">
          <div className="group relative">
            <div className="absolute -inset-px rounded-3xl bg-gradient-to-b from-zinc-200/50 to-zinc-100/50 opacity-0 transition-opacity duration-500 group-hover:opacity-100 dark:from-zinc-800/50 dark:to-zinc-900/50" />
            <div className="relative space-y-5 rounded-3xl border border-zinc-200/50 bg-white/80 p-8 backdrop-blur-sm transition-all duration-500 group-hover:-translate-y-2 group-hover:border-zinc-300/50 group-hover:shadow-2xl group-hover:shadow-zinc-200/50 dark:border-zinc-800/50 dark:bg-black/80 dark:group-hover:border-zinc-700/50 dark:group-hover:shadow-zinc-900/50">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-zinc-100 to-zinc-50 shadow-inner transition-transform duration-500 group-hover:scale-110 dark:from-zinc-900 dark:to-zinc-950">
                <svg className="h-7 w-7 text-zinc-700 transition-colors dark:text-zinc-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3 className="text-base font-semibold tracking-tight text-zinc-900 dark:text-zinc-100">
                Persistent Memory
              </h3>
              <p className="text-sm font-light leading-relaxed text-zinc-600 dark:text-zinc-400">
                Store and retrieve context across sessions with seamless integration into your AI infrastructure
              </p>
            </div>
          </div>

          <div className="group relative">
            <div className="absolute -inset-px rounded-3xl bg-gradient-to-b from-zinc-200/50 to-zinc-100/50 opacity-0 transition-opacity duration-500 group-hover:opacity-100 dark:from-zinc-800/50 dark:to-zinc-900/50" />
            <div className="relative space-y-5 rounded-3xl border border-zinc-200/50 bg-white/80 p-8 backdrop-blur-sm transition-all duration-500 group-hover:-translate-y-2 group-hover:border-zinc-300/50 group-hover:shadow-2xl group-hover:shadow-zinc-200/50 dark:border-zinc-800/50 dark:bg-black/80 dark:group-hover:border-zinc-700/50 dark:group-hover:shadow-zinc-900/50">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-zinc-100 to-zinc-50 shadow-inner transition-transform duration-500 group-hover:scale-110 dark:from-zinc-900 dark:to-zinc-950">
                <svg className="h-7 w-7 text-zinc-700 transition-colors dark:text-zinc-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-base font-semibold tracking-tight text-zinc-900 dark:text-zinc-100">
                Lightning Fast
              </h3>
              <p className="text-sm font-light leading-relaxed text-zinc-600 dark:text-zinc-400">
                Optimized for speed with intelligent caching and millisecond-level retrieval performance
              </p>
            </div>
          </div>

          <div className="group relative">
            <div className="absolute -inset-px rounded-3xl bg-gradient-to-b from-zinc-200/50 to-zinc-100/50 opacity-0 transition-opacity duration-500 group-hover:opacity-100 dark:from-zinc-800/50 dark:to-zinc-900/50" />
            <div className="relative space-y-5 rounded-3xl border border-zinc-200/50 bg-white/80 p-8 backdrop-blur-sm transition-all duration-500 group-hover:-translate-y-2 group-hover:border-zinc-300/50 group-hover:shadow-2xl group-hover:shadow-zinc-200/50 dark:border-zinc-800/50 dark:bg-black/80 dark:group-hover:border-zinc-700/50 dark:group-hover:shadow-zinc-900/50">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-zinc-100 to-zinc-50 shadow-inner transition-transform duration-500 group-hover:scale-110 dark:from-zinc-900 dark:to-zinc-950">
                <svg className="h-7 w-7 text-zinc-700 transition-colors dark:text-zinc-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-base font-semibold tracking-tight text-zinc-900 dark:text-zinc-100">
                Adaptive Learning
              </h3>
              <p className="text-sm font-light leading-relaxed text-zinc-600 dark:text-zinc-400">
                Continuously improve with every interaction through sophisticated feedback loops
              </p>
            </div>
          </div>
        </div>

        {/* Social proof / Stats section */}
        <div className="mt-32 flex flex-col items-center gap-12 animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-700">
          <div className="flex flex-wrap justify-center gap-12 md:gap-20">
            <div className="text-center">
              <div className="text-4xl font-extralight tracking-tight text-black dark:text-white md:text-5xl">
                <span className="bg-gradient-to-br from-zinc-900 to-zinc-600 bg-clip-text text-transparent dark:from-zinc-100 dark:to-zinc-400">∞</span>
              </div>
              <div className="mt-2 text-xs font-medium uppercase tracking-widest text-zinc-400 dark:text-zinc-600">
                Scale
              </div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-extralight tracking-tight text-black dark:text-white md:text-5xl">
                <span className="bg-gradient-to-br from-zinc-900 to-zinc-600 bg-clip-text text-transparent dark:from-zinc-100 dark:to-zinc-400">&lt;10ms</span>
              </div>
              <div className="mt-2 text-xs font-medium uppercase tracking-widest text-zinc-400 dark:text-zinc-600">
                Latency
              </div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-extralight tracking-tight text-black dark:text-white md:text-5xl">
                <span className="bg-gradient-to-br from-zinc-900 to-zinc-600 bg-clip-text text-transparent dark:from-zinc-100 dark:to-zinc-400">100%</span>
              </div>
              <div className="mt-2 text-xs font-medium uppercase tracking-widest text-zinc-400 dark:text-zinc-600">
                Reliable
              </div>
            </div>
          </div>
        </div>

        {/* Elegant footer */}
        <footer className="mt-32 flex flex-col items-center gap-8 pb-8">
          <div className="h-px w-32 bg-gradient-to-r from-transparent via-zinc-300 to-transparent dark:via-zinc-700" />
          <p className="text-xs font-light tracking-wide text-zinc-400 dark:text-zinc-600">
            Built for the future of AI
          </p>
        </footer>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="relative border-t border-zinc-200/50 bg-zinc-50/50 px-6 py-32 dark:border-zinc-800/50 dark:bg-zinc-950/50">
        <div className="mx-auto max-w-7xl">
          <div className="mb-20 text-center">
            <h2 className="mb-4 text-4xl font-extralight tracking-tight text-black dark:text-white md:text-5xl">
              How it <span className="bg-gradient-to-br from-zinc-900 to-zinc-600 bg-clip-text text-transparent dark:from-zinc-100 dark:to-zinc-400">works</span>
            </h2>
            <p className="mx-auto max-w-2xl text-lg font-light text-zinc-600 dark:text-zinc-400">
              Simple integration, powerful results. Get started in minutes.
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            <div className="relative">
              <div className="absolute -left-4 top-0 text-7xl font-extralight text-zinc-200 dark:text-zinc-900">1</div>
              <div className="relative space-y-4 pl-12 pt-8">
                <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100">Initialize</h3>
                <p className="text-sm font-light leading-relaxed text-zinc-600 dark:text-zinc-400">
                  Install the SDK and configure your memory instance with a single command. Works with any AI framework.
                </p>
                <div className="rounded-2xl border border-zinc-200 bg-white p-4 font-mono text-xs dark:border-zinc-800 dark:bg-black">
                  <span className="text-zinc-500">$</span> <span className="text-zinc-900 dark:text-zinc-100">pip install antler</span>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="absolute -left-4 top-0 text-7xl font-extralight text-zinc-200 dark:text-zinc-900">2</div>
              <div className="relative space-y-4 pl-12 pt-8">
                <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100">Store</h3>
                <p className="text-sm font-light leading-relaxed text-zinc-600 dark:text-zinc-400">
                  Seamlessly save context, conversations, and learnings as your AI interacts with users.
                </p>
                <div className="rounded-2xl border border-zinc-200 bg-white p-4 font-mono text-xs dark:border-zinc-800 dark:bg-black">
                  <span className="text-blue-600 dark:text-blue-400">memory</span>.<span className="text-purple-600 dark:text-purple-400">store</span>(<span className="text-green-600 dark:text-green-400">context</span>)
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="absolute -left-4 top-0 text-7xl font-extralight text-zinc-200 dark:text-zinc-900">3</div>
              <div className="relative space-y-4 pl-12 pt-8">
                <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100">Retrieve</h3>
                <p className="text-sm font-light leading-relaxed text-zinc-600 dark:text-zinc-400">
                  Instantly access relevant memories and context to make your AI smarter with every interaction.
                </p>
                <div className="rounded-2xl border border-zinc-200 bg-white p-4 font-mono text-xs dark:border-zinc-800 dark:bg-black">
                  <span className="text-blue-600 dark:text-blue-400">memory</span>.<span className="text-purple-600 dark:text-purple-400">recall</span>(<span className="text-green-600 dark:text-green-400">query</span>)
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="relative px-6 py-32">
        <div className="mx-auto max-w-7xl">
          <div className="mb-20 text-center">
            <h2 className="mb-4 text-4xl font-extralight tracking-tight text-black dark:text-white md:text-5xl">
              Built for every <span className="bg-gradient-to-br from-zinc-900 to-zinc-600 bg-clip-text text-transparent dark:from-zinc-100 dark:to-zinc-400">use case</span>
            </h2>
            <p className="mx-auto max-w-2xl text-lg font-light text-zinc-600 dark:text-zinc-400">
              From chatbots to autonomous agents, Antler powers intelligent memory.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <div className="group relative overflow-hidden rounded-3xl border border-zinc-200/50 bg-white p-8 transition-all hover:shadow-2xl dark:border-zinc-800/50 dark:bg-black">
              <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-zinc-100 to-zinc-50 dark:from-zinc-900 dark:to-zinc-950">
                <svg className="h-6 w-6 text-zinc-700 dark:text-zinc-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h3 className="mb-3 text-xl font-semibold text-zinc-900 dark:text-zinc-100">Customer Support</h3>
              <p className="text-sm font-light leading-relaxed text-zinc-600 dark:text-zinc-400">
                Build chatbots that remember customer preferences, past interactions, and provide personalized support at scale.
              </p>
            </div>

            <div className="group relative overflow-hidden rounded-3xl border border-zinc-200/50 bg-white p-8 transition-all hover:shadow-2xl dark:border-zinc-800/50 dark:bg-black">
              <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-zinc-100 to-zinc-50 dark:from-zinc-900 dark:to-zinc-950">
                <svg className="h-6 w-6 text-zinc-700 dark:text-zinc-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
              </div>
              <h3 className="mb-3 text-xl font-semibold text-zinc-900 dark:text-zinc-100">Autonomous Agents</h3>
              <p className="text-sm font-light leading-relaxed text-zinc-600 dark:text-zinc-400">
                Enable AI agents to learn from past decisions, adapt strategies, and execute complex workflows with context.
              </p>
            </div>

            <div className="group relative overflow-hidden rounded-3xl border border-zinc-200/50 bg-white p-8 transition-all hover:shadow-2xl dark:border-zinc-800/50 dark:bg-black">
              <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-zinc-100 to-zinc-50 dark:from-zinc-900 dark:to-zinc-950">
                <svg className="h-6 w-6 text-zinc-700 dark:text-zinc-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <h3 className="mb-3 text-xl font-semibold text-zinc-900 dark:text-zinc-100">Personal Assistants</h3>
              <p className="text-sm font-light leading-relaxed text-zinc-600 dark:text-zinc-400">
                Create AI assistants that understand user habits, preferences, and historical context for truly personalized experiences.
              </p>
            </div>

            <div className="group relative overflow-hidden rounded-3xl border border-zinc-200/50 bg-white p-8 transition-all hover:shadow-2xl dark:border-zinc-800/50 dark:bg-black">
              <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-zinc-100 to-zinc-50 dark:from-zinc-900 dark:to-zinc-950">
                <svg className="h-6 w-6 text-zinc-700 dark:text-zinc-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="mb-3 text-xl font-semibold text-zinc-900 dark:text-zinc-100">Analytics & Insights</h3>
              <p className="text-sm font-light leading-relaxed text-zinc-600 dark:text-zinc-400">
                Track patterns, analyze behavior, and generate insights from your AI&apos;s memory to improve performance over time.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Integration Section */}
      <section className="relative border-t border-zinc-200/50 bg-zinc-50/50 px-6 py-32 dark:border-zinc-800/50 dark:bg-zinc-950/50">
        <div className="mx-auto max-w-7xl">
          <div className="mb-20 text-center">
            <h2 className="mb-4 text-4xl font-extralight tracking-tight text-black dark:text-white md:text-5xl">
              Works with your <span className="bg-gradient-to-br from-zinc-900 to-zinc-600 bg-clip-text text-transparent dark:from-zinc-100 dark:to-zinc-400">stack</span>
            </h2>
            <p className="mx-auto max-w-2xl text-lg font-light text-zinc-600 dark:text-zinc-400">
              Seamless integration with popular AI frameworks and tools.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-6 md:grid-cols-4">
            {['OpenAI', 'LangChain', 'PyTorch', 'Anthropic', 'Hugging Face', 'TensorFlow', 'Pinecone', 'Weaviate'].map((tech) => (
              <div key={tech} className="group flex items-center justify-center rounded-2xl border border-zinc-200/50 bg-white p-8 transition-all hover:scale-105 hover:shadow-lg dark:border-zinc-800/50 dark:bg-black">
                <span className="text-base font-medium text-zinc-600 transition-colors group-hover:text-zinc-900 dark:text-zinc-400 dark:group-hover:text-zinc-100">
                  {tech}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="relative px-6 py-32">
        <div className="mx-auto max-w-7xl">
          <div className="mb-20 text-center">
            <h2 className="mb-4 text-4xl font-extralight tracking-tight text-black dark:text-white md:text-5xl">
              Simple, <span className="bg-gradient-to-br from-zinc-900 to-zinc-600 bg-clip-text text-transparent dark:from-zinc-100 dark:to-zinc-400">transparent</span> pricing
            </h2>
            <p className="mx-auto max-w-2xl text-lg font-light text-zinc-600 dark:text-zinc-400">
              Start free, scale as you grow. No hidden fees.
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            {/* Free Tier */}
            <div className="group relative overflow-hidden rounded-3xl border border-zinc-200/50 bg-white p-8 transition-all hover:shadow-xl dark:border-zinc-800/50 dark:bg-black">
              <h3 className="mb-2 text-xl font-semibold text-zinc-900 dark:text-zinc-100">Starter</h3>
              <div className="mb-6">
                <span className="text-5xl font-extralight text-black dark:text-white">$0</span>
                <span className="text-zinc-600 dark:text-zinc-400">/month</span>
              </div>
              <ul className="mb-8 space-y-3">
                {['10K memory operations/mo', '1 GB storage', 'Community support', 'Basic analytics'].map((feature) => (
                  <li key={feature} className="flex items-center gap-3 text-sm text-zinc-600 dark:text-zinc-400">
                    <svg className="h-5 w-5 flex-shrink-0 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>
              <button className="w-full rounded-full border border-zinc-200 py-3 text-sm font-medium transition-all hover:border-zinc-300 hover:bg-zinc-50 dark:border-zinc-800 dark:hover:border-zinc-700 dark:hover:bg-zinc-950">
                Get Started
              </button>
            </div>

            {/* Pro Tier */}
            <div className="group relative overflow-hidden rounded-3xl border-2 border-black bg-white p-8 shadow-2xl transition-all hover:scale-105 dark:border-white dark:bg-black">
              <div className="absolute right-4 top-4 rounded-full bg-black px-3 py-1 text-xs font-medium text-white dark:bg-white dark:text-black">
                Popular
              </div>
              <h3 className="mb-2 text-xl font-semibold text-zinc-900 dark:text-zinc-100">Pro</h3>
              <div className="mb-6">
                <span className="text-5xl font-extralight text-black dark:text-white">$49</span>
                <span className="text-zinc-600 dark:text-zinc-400">/month</span>
              </div>
              <ul className="mb-8 space-y-3">
                {['1M memory operations/mo', '100 GB storage', 'Priority support', 'Advanced analytics', 'Custom integrations', 'API access'].map((feature) => (
                  <li key={feature} className="flex items-center gap-3 text-sm text-zinc-600 dark:text-zinc-400">
                    <svg className="h-5 w-5 flex-shrink-0 text-black dark:text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>
              <button className="w-full rounded-full bg-black py-3 text-sm font-medium text-white transition-all hover:scale-105 dark:bg-white dark:text-black">
                Start Free Trial
              </button>
            </div>

            {/* Enterprise Tier */}
            <div className="group relative overflow-hidden rounded-3xl border border-zinc-200/50 bg-white p-8 transition-all hover:shadow-xl dark:border-zinc-800/50 dark:bg-black">
              <h3 className="mb-2 text-xl font-semibold text-zinc-900 dark:text-zinc-100">Enterprise</h3>
              <div className="mb-6">
                <span className="text-5xl font-extralight text-black dark:text-white">Custom</span>
              </div>
              <ul className="mb-8 space-y-3">
                {['Unlimited operations', 'Unlimited storage', '24/7 dedicated support', 'Custom deployment', 'SLA guarantees', 'Advanced security'].map((feature) => (
                  <li key={feature} className="flex items-center gap-3 text-sm text-zinc-600 dark:text-zinc-400">
                    <svg className="h-5 w-5 flex-shrink-0 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>
              <button className="w-full rounded-full border border-zinc-200 py-3 text-sm font-medium transition-all hover:border-zinc-300 hover:bg-zinc-50 dark:border-zinc-800 dark:hover:border-zinc-700 dark:hover:bg-zinc-950">
                Contact Sales
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="relative border-t border-zinc-200/50 bg-zinc-50/50 px-6 py-32 dark:border-zinc-800/50 dark:bg-zinc-950/50">
        <div className="mx-auto max-w-7xl">
          <div className="mb-20 text-center">
            <h2 className="mb-4 text-4xl font-extralight tracking-tight text-black dark:text-white md:text-5xl">
              Trusted by <span className="bg-gradient-to-br from-zinc-900 to-zinc-600 bg-clip-text text-transparent dark:from-zinc-100 dark:to-zinc-400">innovators</span>
            </h2>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            {[
              { quote: "Antler transformed how our AI agents learn and adapt. The memory persistence is game-changing.", author: "Sarah Chen", role: "CTO, TechCorp" },
              { quote: "Integration was seamless, and the performance gains were immediate. Our chatbot is 10x smarter now.", author: "Michael Rodriguez", role: "Lead AI Engineer, DataFlow" },
              { quote: "The analytics insights helped us understand user patterns we never saw before. Absolutely essential.", author: "Emily Watson", role: "VP Product, Innovate AI" }
            ].map((testimonial, i) => (
              <div key={i} className="rounded-3xl border border-zinc-200/50 bg-white p-8 dark:border-zinc-800/50 dark:bg-black">
                <p className="mb-6 text-sm font-light leading-relaxed text-zinc-600 dark:text-zinc-400">
                  &ldquo;{testimonial.quote}&rdquo;
                </p>
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-zinc-100 dark:bg-zinc-900">
                    <span className="text-sm font-medium text-zinc-600 dark:text-zinc-400">{testimonial.author[0]}</span>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{testimonial.author}</div>
                    <div className="text-xs text-zinc-600 dark:text-zinc-400">{testimonial.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative px-6 py-32">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="mb-8 text-5xl font-extralight leading-tight tracking-tight text-black dark:text-white md:text-6xl">
            Ready to make your AI{' '}
            <span className="bg-gradient-to-br from-zinc-900 to-zinc-600 bg-clip-text text-transparent dark:from-zinc-100 dark:to-zinc-400">
              unforgettable?
            </span>
          </h2>
          <p className="mb-12 text-xl font-light text-zinc-600 dark:text-zinc-400">
            Start building smarter AI systems today. No credit card required.
          </p>
          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <button className="group relative overflow-hidden rounded-full bg-black px-10 py-4 text-sm font-medium tracking-wide text-white shadow-lg shadow-black/10 transition-all duration-300 hover:scale-[1.02] hover:shadow-xl hover:shadow-black/20 active:scale-[0.98] dark:bg-white dark:text-black dark:shadow-white/10 dark:hover:shadow-white/20">
              <span className="relative z-10 flex items-center gap-2">
                Get Started Free
                <svg className="h-4 w-4 transition-transform duration-300 group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </span>
            </button>
            <button className="rounded-full border border-zinc-200/80 bg-white/50 px-10 py-4 text-sm font-medium tracking-wide text-zinc-900 backdrop-blur-sm transition-all duration-300 hover:scale-[1.02] hover:border-zinc-300 hover:bg-white active:scale-[0.98] dark:border-zinc-800/80 dark:bg-black/50 dark:text-zinc-100 dark:hover:border-zinc-700 dark:hover:bg-black">
              View Documentation
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative border-t border-zinc-200/50 bg-zinc-50/50 px-6 py-16 dark:border-zinc-800/50 dark:bg-zinc-950/50">
        <div className="mx-auto max-w-7xl">
          <div className="grid gap-12 md:grid-cols-5">
            <div className="md:col-span-2">
              <div className="mb-4 flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center">
            <Image
                    src="/favicon.ico"
                    alt="Antler Logo"
                    width={32}
                    height={32}
                    className="h-8 w-8"
                  />
                </div>
                <span className="text-lg font-semibold text-black dark:text-white">Antler</span>
              </div>
              <p className="mb-6 max-w-xs text-sm font-light text-zinc-600 dark:text-zinc-400">
                Memory infrastructure for AI agents. Built for the future of artificial intelligence.
              </p>
              <div className="flex gap-4">
                {['Twitter', 'GitHub', 'Discord'].map((social) => (
                  <a key={social} href="#" className="text-zinc-600 transition-colors hover:text-black dark:text-zinc-400 dark:hover:text-white">
                    <span className="sr-only">{social}</span>
                    <div className="flex h-10 w-10 items-center justify-center rounded-full border border-zinc-200 transition-colors hover:border-zinc-300 dark:border-zinc-800 dark:hover:border-zinc-700">
                      <span className="text-xs">{social[0]}</span>
                    </div>
                  </a>
                ))}
              </div>
            </div>

            <div>
              <h4 className="mb-4 text-sm font-semibold text-zinc-900 dark:text-zinc-100">Product</h4>
              <ul className="space-y-3">
                {['Features', 'Pricing', 'Documentation', 'API Reference', 'Changelog'].map((item) => (
                  <li key={item}>
                    <a href="#" className="text-sm font-light text-zinc-600 transition-colors hover:text-black dark:text-zinc-400 dark:hover:text-white">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="mb-4 text-sm font-semibold text-zinc-900 dark:text-zinc-100">Company</h4>
              <ul className="space-y-3">
                {['About', 'Blog', 'Careers', 'Contact', 'Partners'].map((item) => (
                  <li key={item}>
                    <a href="#" className="text-sm font-light text-zinc-600 transition-colors hover:text-black dark:text-zinc-400 dark:hover:text-white">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="mb-4 text-sm font-semibold text-zinc-900 dark:text-zinc-100">Legal</h4>
              <ul className="space-y-3">
                {['Privacy', 'Terms', 'Security', 'Compliance'].map((item) => (
                  <li key={item}>
                    <a href="#" className="text-sm font-light text-zinc-600 transition-colors hover:text-black dark:text-zinc-400 dark:hover:text-white">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="mt-12 border-t border-zinc-200/50 pt-8 dark:border-zinc-800/50">
            <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
              <p className="text-xs font-light text-zinc-600 dark:text-zinc-400">
                © 2025 Antler. All rights reserved.
              </p>
              <p className="text-xs font-light text-zinc-600 dark:text-zinc-400">
                Built for the future of AI
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
