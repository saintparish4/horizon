import React from 'react';
import Image from 'next/image';

const HeroSection = () => {
  return (
    <section className="relative w-full overflow-hidden h-auto md:h-[600px] 2xl:h-[670px] bg-[#FBFBFB] border-t border-dashed border-[#E5E7EB]">
      {/* Background Grid Pattern */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <div 
          className="w-full h-full opacity-30" 
          style={{
            backgroundImage: `linear-gradient(to right, #E5E7EB 1px, transparent 1px), linear-gradient(to bottom, #E5E7EB 1px, transparent 1px)`,
            backgroundSize: '40px 40px'
          }}
        />
      </div>

      <div className="container relative z-10 h-full mx-auto px-4 lg:px-6">
        <div className="grid grid-cols-12 h-full items-center">
          {/* Left Content Column */}
          <div className="col-span-12 lg:col-span-6 flex flex-col gap-6 md:gap-8 max-md:py-16 relative">
            {/* Visual Grid Lines Overlay for text alignment (matching original blueprint style) */}
            <div className="absolute inset-0 pointer-events-none -ml-4 -mr-4 border-l border-dashed border-[#E5E7EB] hidden lg:block" />
            
            <div className="relative">
              <h1 className="font-sans text-[3.5rem] md:text-[6rem] lg:text-[7.5rem] font-semibold tracking-[-0.04em] leading-[1.05] text-[#0D0D0D] -mt-2">
                Inference is <br /> everything
              </h1>
            </div>

            <div className="relative max-w-[480px]">
              <p className="font-sans text-xl md:text-2xl leading-[1.4] text-[#0D0D0D] text-pretty">
                The fastest model runtimes, cross-cloud high availability, and seamless developer workflows. Powered by the Baseten Inference Stack.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <a 
                href="https://login.baseten.co/sign-up"
                className="group relative inline-flex items-center justify-center gap-3 px-6 py-3 bg-[#0D0D0D] text-white font-mono text-sm uppercase tracking-tight overflow-hidden transition-all duration-200 hover:bg-[#00FF7F] hover:text-[#0D0D0D]"
              >
                <div className="absolute inset-0 bg-[#00FF7F] translate-y-full transition-transform duration-200 ease-out group-hover:translate-y-0" />
                <span className="relative z-10">Get started</span>
                <span className="relative z-10 transition-transform duration-200 group-hover:translate-x-1">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M1 7h12M13 7l-4-4M13 7l-4 4" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </span>
              </a>

              <a 
                href="/talk-to-us/"
                className="group relative inline-flex items-center justify-center gap-3 px-6 py-3 bg-white border border-[#E5E7EB] text-[#0D0D0D] font-mono text-sm uppercase tracking-tight overflow-hidden transition-all duration-200 hover:border-[#0D0D0D]"
              >
                <div className="absolute inset-0 bg-[#F5F5F5] translate-y-full transition-transform duration-200 ease-out group-hover:translate-y-0" />
                <span className="relative z-10">Talk to an engineer</span>
                <span className="relative z-10 transition-transform duration-200 group-hover:translate-x-1">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M1 7h12M13 7l-4-4M13 7l-4 4" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </span>
              </a>
            </div>
          </div>

          {/* Right Illustration Column */}
          <div className="hidden lg:flex col-span-6 relative h-full items-center justify-center">
            <div className="relative w-[110%] h-[110%] right-[-10%] translate-y-4">
              {/* Prioritizing requested globe illustration asset */}
              <img 
                src="https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/8b29c68a-eaca-476e-a7ce-c0f16902fd64-baseten-co/assets/svgs/globe-illustration-1.svg" 
                alt="Baseten Inference Infrastructure Illustration" 
                className="w-full h-full object-contain select-none pointer-events-none scale-125"
              />
              
              {/* Subtle Decorative Accent Blocks (Matching high-level design) */}
              <div className="absolute top-1/4 right-1/4 w-12 h-12 bg-[#00FF7F]/10 -z-10 animate-pulse" />
              <div className="absolute bottom-1/3 left-1/3 w-20 h-20 bg-[#E0B0FF]/10 -z-10 animate-pulse delay-700" />
            </div>
          </div>
        </div>
      </div>

      {/* Grid Lines Reveal Effect (Blueprint aesthetic) */}
      <div className="absolute left-0 top-0 bottom-0 w-px border-l border-dashed border-[#E5E7EB] hidden 2xl:block" />
      <div className="absolute right-0 top-0 bottom-0 w-px border-r border-dashed border-[#E5E7EB] hidden 2xl:block" />
      <div className="absolute bottom-0 left-0 right-0 h-px border-b border-dashed border-[#E5E7EB]" />
    </section>
  );
};

export default HeroSection;