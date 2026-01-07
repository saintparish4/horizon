import React from 'react';
import Image from 'next/image';
import { ChevronDown, Menu, ArrowRight } from 'lucide-react';

const Navbar = () => {
  return (
    <header className="w-full">
      {/* Top Banner */}
      <div className="bg-[#00FF7F] px-4 py-2">
        <div className="container mx-auto flex flex-col md:flex-row items-center justify-center gap-2 text-sm font-medium text-[#0D0D0D]">
          <span>Now in beta: Give your AI agents long-term memory with semantic search and context management.</span>
          <a 
            href="/beta" 
            className="group flex items-center gap-1 font-mono text-xs uppercase underline underline-offset-4 hover:opacity-80 transition-opacity"
          >
            JOIN BETA
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
              <a href="/" className="flex items-center gap-2">
                <span className="text-2xl">🦌</span>
                <span className="text-xl font-semibold tracking-tight text-[#0D0D0D]">Antler</span>
              </a>

              {/* Desktop Menu */}
              <ul className="hidden xl:flex items-center space-x-1">
                <li>
                  <a href="/features" className="px-3 py-2 text-[14px] font-normal text-[#0D0D0D] hover:text-[#00FF7F] transition-colors">Features</a>
                </li>
                <li>
                  <a href="/docs" className="px-3 py-2 text-[14px] font-normal text-[#0D0D0D] hover:text-[#00FF7F] transition-colors">Documentation</a>
                </li>
                <li>
                  <a href="/integrations" className="px-3 py-2 text-[14px] font-normal text-[#0D0D0D] hover:text-[#00FF7F] transition-colors">Integrations</a>
                </li>
                <li>
                  <a href="/pricing" className="px-3 py-2 text-[14px] font-normal text-[#0D0D0D] hover:text-[#00FF7F] transition-colors">Pricing</a>
                </li>
                <li>
                  <a href="/blog" className="px-3 py-2 text-[14px] font-normal text-[#0D0D0D] hover:text-[#00FF7F] transition-colors">Blog</a>
                </li>
              </ul>
            </div>

            {/* Action Buttons */}
            <div className="hidden xl:flex items-center gap-4">
              <a 
                href="/login" 
                className="relative group overflow-hidden px-4 py-2 font-mono text-[12px] uppercase border border-[#E5E7EB] hover:border-[#0D0D0D] transition-colors"
              >
                <div className="absolute inset-0 bg-[#F5F5F5] translate-y-full group-hover:translate-y-0 transition-transform duration-[236ms]" />
                <span className="relative z-10 text-[#0D0D0D]">Log in</span>
              </a>
              <a 
                href="/signup" 
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