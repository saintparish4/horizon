import AnnouncementBar from '@/components/sections/announcement-bar';
import Navbar from '@/components/sections/navbar';
import HeroSection from '@/components/sections/hero';
import TrustLogos from '@/components/sections/trust-logos';
import PerformancePlatform from '@/components/sections/performance-platform';
import TechnicalFeaturesGrid from '@/components/sections/technical-features';
import DeploymentOptions from '@/components/sections/deployment-options';
import GenAiSolutions from '@/components/sections/gen-ai-solutions';
import Testimonials from '@/components/sections/testimonials';
import ExploreBasetenCTA from '@/components/sections/cta-footer-banner';
import Footer from '@/components/sections/footer';

export default function Home() {
  return (
    <main className="min-h-screen bg-[#FBFBFB]">
      <Navbar />
      <HeroSection />
      <TrustLogos />
      <PerformancePlatform />
      <TechnicalFeaturesGrid />
      <DeploymentOptions />
      <GenAiSolutions />
      <Testimonials />
      <ExploreBasetenCTA />
      <Footer />
    </main>
  );
}
