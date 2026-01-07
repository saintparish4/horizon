import React from 'react';
import Image from 'next/image';
import { ChevronDown, Menu, ArrowRight } from 'lucide-react';

const Navbar = () => {
  return (
    <header className="w-full">
      {/* Top Banner */}
      <div className="bg-[#00FF7F] px-4 py-2">
        <div className="container mx-auto flex flex-col md:flex-row items-center justify-center gap-2 text-sm font-medium text-[#0D0D0D]">
          <span>Baseten acquires Parsed: Own your intelligence by unifying training and inference.</span>
          <a 
            href="https://www.baseten.co/blog/parsed-baseten" 
            className="group flex items-center gap-1 font-mono text-xs uppercase underline underline-offset-4 hover:opacity-80 transition-opacity"
          >
            READ
            <ArrowRight className="size-3.5 transition-transform group-hover:translate-x-1" />
          </a>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="sticky top-0 left-0 z-[9999] w-full bg-[#FBFBFB] border-b border-dashed border-[#E5E7EB]">
        <div className="container mx-auto max-w-[1296px] px-4 py-3 lg:py-6">
          <div className="flex items-center justify-between">
            {/* Logo and Main Links */}
            <div className="flex items-center gap-10">
              <a href="/" className="block">
                <Image 
                  src="https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/8b29c68a-eaca-476e-a7ce-c0f16902fd64-baseten-co/assets/images/1764774959-lockup_horizontal_2d_light-1.png"
                  alt="Baseten Logo"
                  width={131}
                  height={34}
                  className="h-[34px] w-auto"
                />
              </a>

              {/* Desktop Menu */}
              <ul className="hidden xl:flex items-center space-x-1">
                {['Product', 'Platform', 'Developer', 'Resources'].map((item) => (
                  <li key={item} className="relative group/nav-item">
                    <button className="flex items-center gap-1.5 px-3 py-2 text-[14px] font-normal text-[#0D0D0D] transition-colors hover:text-[#00FF7F]">
                      {item}
                      <ChevronDown className="size-3.5 transition-transform duration-[236ms] group-hover/nav-item:rotate-180" />
                    </button>
                  </li>
                ))}
                <li>
                  <a href="/research" className="px-3 py-2 text-[14px] font-normal text-[#0D0D0D] hover:text-[#00FF7F] transition-colors">Research</a>
                </li>
                <li>
                  <a href="/customers" className="px-3 py-2 text-[14px] font-normal text-[#0D0D0D] hover:text-[#00FF7F] transition-colors">Customers</a>
                </li>
                <li>
                  <a href="/pricing" className="px-3 py-2 text-[14px] font-normal text-[#0D0D0D] hover:text-[#00FF7F] transition-colors">Pricing</a>
                </li>
              </ul>
            </div>

            {/* Action Buttons */}
            <div className="hidden xl:flex items-center gap-4">
              <a 
                href="https://login.baseten.co/" 
                className="relative group overflow-hidden px-4 py-2 font-mono text-[12px] uppercase border border-[#E5E7EB] hover:border-[#0D0D0D] transition-colors"
              >
                <div className="absolute inset-0 bg-[#F5F5F5] translate-y-full group-hover:translate-y-0 transition-transform duration-[236ms]" />
                <span className="relative z-10 text-[#0D0D0D]">Log in</span>
              </a>
              <a 
                href="https://login.baseten.co/sign-up" 
                className="relative group overflow-hidden px-4 py-2 font-mono text-[12px] uppercase bg-[#0D0D0D] border border-[#0D0D0D] transition-colors"
              >
                <div className="absolute inset-0 bg-[#00FF7F] translate-y-full group-hover:translate-y-0 transition-transform duration-[236ms]" />
                <span className="relative z-10 text-white group-hover:text-[#0D0D0D]">Get started</span>
              </a>
            </div>

            {/* Mobile Menu Toggle */}
            <button className="xl:hidden p-2 text-[#0D0D0D]">
              <Menu className="size-6" />
            </button>
          </div>
        </div>
      </nav>
    </header>
  );
};

export default Navbar;