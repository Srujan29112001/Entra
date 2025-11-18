import { Button } from "@/components/ui/button";
import { ArrowRight, BarChart3, Brain, Lock, Zap } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Brain className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold">Entra</span>
          </div>
          <nav className="hidden md:flex gap-6">
            <Link href="#features" className="text-sm hover:text-primary">
              Features
            </Link>
            <Link href="#how-it-works" className="text-sm hover:text-primary">
              How It Works
            </Link>
            <Link href="#pricing" className="text-sm hover:text-primary">
              Pricing
            </Link>
          </nav>
          <div className="flex gap-2">
            <Button variant="ghost" asChild>
              <Link href="/login">Sign In</Link>
            </Button>
            <Button asChild>
              <Link href="/signup">Get Started</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 md:py-32">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 max-w-4xl mx-auto">
            Your AI Board of Advisors for{" "}
            <span className="text-primary">Finance, Tax & Strategy</span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Get expert guidance on salary planning, tax optimization, market strategy, legal
            compliance, and personal wealth management - all powered by specialized AI agents.
          </p>
          <div className="flex gap-4 justify-center">
            <Button size="lg" asChild>
              <Link href="/signup">
                Start Free Trial <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="#demo">Watch Demo</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 bg-muted/50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            Specialized AI Advisors for Every Challenge
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard
              icon={<BarChart3 className="h-10 w-10 text-primary" />}
              title="Finance & Fund Management"
              description="Runway calculations, funding strategy, unit economics, and financial projections powered by AI."
            />
            <FeatureCard
              icon={<Zap className="h-10 w-10 text-primary" />}
              title="Tax & Policy Optimization"
              description="Multi-jurisdiction tax planning, policy incentives, and salary vs dividend structuring."
            />
            <FeatureCard
              icon={<Brain className="h-10 w-10 text-primary" />}
              title="Market & Strategy"
              description="Go-to-market plans, distribution channels, SWOT analysis, and competitive positioning."
            />
            <FeatureCard
              icon={<Lock className="h-10 w-10 text-primary" />}
              title="Legal & Compliance"
              description="Contract analysis, risk identification, and jurisdiction-specific compliance guidance."
            />
            <FeatureCard
              icon={<BarChart3 className="h-10 w-10 text-primary" />}
              title="Personal Wealth Planning"
              description="Founder salary optimization, personal tax planning, and equity structuring."
            />
            <FeatureCard
              icon={<Zap className="h-10 w-10 text-primary" />}
              title="Scenario Modeling"
              description="Model different growth, hiring, and pricing scenarios with real-time analytics."
            />
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Get Expert AI Guidance?
          </h2>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join hundreds of entrepreneurs making smarter decisions with Entra.
          </p>
          <Button size="lg" asChild>
            <Link href="/signup">
              Start Your Free Trial <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>&copy; 2024 Entra. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-card p-6 rounded-lg border">
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
    </div>
  );
}
