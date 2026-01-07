import React from 'react';
import { ChevronRight } from 'lucide-react';

/**
 * ExploreBasetenCTA Component
 * 
 * Clones the final "Explore Baseten today" CTA section with the black action buttons
 * and the colorful geometric pixel-art style transition bar above the main footer.
 */
const ExploreBasetenCTA: React.FC = () => {
  return (
    <section className="relative w-full bg-[#FBFBFB]">
      {/* Main CTA Content */}
      <div className="container mx-auto max-w-[1296px] px-4 py-[120px]">
        <div className="flex flex-col items-center justify-center text-center">
          {/* Section Heading */}
          <h2 className="mb-10 font-sans text-[clamp(2.5rem,5vw,4rem)] font-semibold tracking-[-0.04em] text-[#0D0D0D]">
            Explore Baseten today
          </h2>

          {/* Action Buttons */}
          <div className="flex flex-col items-center gap-4 sm:flex-row">
            {/* Primary Button */}
            <a
              href="https://login.baseten.co/sign-up"
              className="group relative flex h-[46px] items-center justify-center gap-2 overflow-hidden bg-[#0D0D0D] px-6 py-3 font-mono text-[13px] font-medium tracking-[-0.02em] uppercase text-white transition-all duration-[236ms] ease-[cubic-bezier(0.5,0.2,0.4,1)] hover:outline hover:outline-1 hover:outline-[#00FF7F]"
            >
              <div className="absolute inset-0 z-0 translate-y-full bg-[#00FF7F] transition-transform duration-[236ms] ease-[cubic-bezier(0.5,0.2,0.4,1)] group-hover:translate-y-0" />
              <span className="relative z-10 group-hover:text-[#0D0D0D]">Start deploying</span>
              <ChevronRight className="relative z-10 h-4 w-4 transition-transform duration-[236ms] group-hover:translate-x-1 group-hover:text-[#0D0D0D]" />
            </a>

            {/* Secondary Button */}
            <a
              href="/talk-to-us/"
              className="group relative flex h-[46px] items-center justify-center gap-2 overflow-hidden bg-white px-6 py-3 font-mono text-[13px] font-medium tracking-[-0.02em] uppercase text-[#0D0D0D] outline outline-1 outline-[#E5E7EB] transition-all duration-[236ms] ease-[cubic-bezier(0.5,0.2,0.4,1)] hover:outline-[#0D0D0D]"
            >
              <div className="absolute inset-0 z-0 translate-y-full bg-[#F5F5F5] transition-transform duration-[236ms] ease-[cubic-bezier(0.5,0.2,0.4,1)] group-hover:translate-y-0" />
              <span className="relative z-10">Talk to an engineer</span>
              <ChevronRight className="relative z-10 h-4 w-4 transition-transform duration-[236ms] group-hover:translate-x-1" />
            </a>
          </div>
        </div>
      </div>

      {/* Geometric Transition Bar (Pixel-art style) */}
      <div className="relative w-full border-t border-dashed border-[#E5E7EB] h-[64px] overflow-hidden">
        {/* Dash/Grid Context lines */}
        <div className="absolute inset-0 pointer-events-none">
            <div className="container mx-auto max-w-[1296px] h-full flex">
                <div className="w-1/4 border-r border-dashed border-[#E5E7EB]" />
                <div className="w-1/4 border-r border-dashed border-[#E5E7EB]" />
                <div className="w-1/4 border-r border-dashed border-[#E5E7EB]" />
                <div className="w-1/4" />
            </div>
        </div>

        {/* Floating Pixel Blocks - Replicating the screenshot layout manually */}
        <div className="container mx-auto max-w-[1296px] relative h-full">
            {/* Group 1: Left */}
            <div className="absolute left-[5%] top-8 w-6 h-6 bg-[#00FF7F]" />
            <div className="absolute left-[8%] top-12 w-4 h-8 bg-[#E0B0FF]" />
            
            {/* Group 2: Center-Left */}
            <div className="absolute left-[20%] top-2 w-8 h-8 bg-[#00FF7F]" />
            
            {/* Group 3: Center-Right */}
            <div className="absolute left-[38%] top-4 w-3 h-8 bg-[#E0B0FF]" />
            <div className="absolute left-[40%] top-12 w-6 h-4 bg-[#F5F5F5]" />

            {/* Group 4: Right */}
            <div className="absolute right-[35%] top-8 w-4 h-12 bg-[#F5F5F5]" />
            <div className="absolute right-[22%] top-2 w-3 h-8 bg-[#00FF7F]" />
            <div className="absolute right-[15%] top-10 w-5 h-8 bg-[#00FF7F]" />
            <div className="absolute right-[8%] top-14 w-8 h-4 bg-[#E0B0FF]" />
        </div>
      </div>
    </section>
  );
};

export default ExploreBasetenCTA;