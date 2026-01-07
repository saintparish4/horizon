import React from 'react';
import Image from 'next/image';
import { Github, Twitter, Linkedin, Youtube } from 'lucide-react';

const footerSections = [
  {
    title: 'Product',
    links: [
      { label: 'Dedicated deployments', href: '#' },
      { label: 'Model APIs', href: '#' },
      { label: 'Training', href: '#' },
      { label: 'Inference Stack', href: '#', isHeader: true, className: 'mt-8' },
      { label: 'Model Runtimes', href: '#' },
      { label: 'Infrastructure', href: '#' },
      { label: 'Multi-cloud Capacity Management', href: '#' },
      { label: 'Developer Experience', href: '#', isHeader: true, className: 'mt-8' },
      { label: 'Chains', href: '#' },
      { label: 'Model management', href: '#' },
    ],
  },
  {
    title: 'Deployment options',
    links: [
      { label: 'Baseten Cloud', href: '#' },
      { label: 'Self-hosted', href: '#' },
      { label: 'Hybrid', href: '#' },
      { label: 'Solutions', href: '#', isHeader: true, className: 'mt-8' },
      { label: 'Enterprise', href: '#' },
      { label: 'Transcription', href: '#' },
      { label: 'Image generation', href: '#' },
      { label: 'Text-to-speech', href: '#' },
      { label: 'Large language models', href: '#' },
      { label: 'Compound AI', href: '#' },
      { label: 'Embeddings', href: '#' },
      { label: 'Startup program', href: '#' },
    ],
  },
  {
    title: 'Developer',
    links: [
      { label: 'Documentation', href: '#' },
      { label: 'Model library', href: '#' },
      { label: 'Changelog', href: '#' },
      { label: 'Resources', href: '#', isHeader: true, className: 'mt-8' },
      { label: 'Research', href: '#' },
      { label: 'Blog', href: '#' },
      { label: 'Guides', href: '#' },
      { label: 'Events', href: '#' },
      { label: 'Customers', href: '#' },
      { label: 'Trust', href: '#' },
      { label: 'Partner', href: '#' },
      { label: 'Careers', href: '#' },
      { label: 'Contact us', href: '#' },
    ],
  },
  {
    title: 'Popular models',
    links: [
      { label: 'GLM 4.7', href: '#' },
      { label: 'DeepSeek V3.2', href: '#' },
      { label: 'GPT OSS 120B', href: '#' },
      { label: 'Kimi K2 Thinking', href: '#' },
      { label: 'Orpheus TTS', href: '#' },
      { label: 'Qwen3 Coder 480B', href: '#' },
      { label: 'Explore all', href: '#' },
      { label: 'Legal', href: '#', isHeader: true, className: 'mt-12' },
      { label: 'Terms and Conditions', href: '#' },
      { label: 'Privacy Policy', href: '#' },
      { label: 'Service Level Agreement', href: '#' },
    ],
  },
];

const Footer = () => {
  return (
    <footer className="w-full bg-black text-white pt-24 pb-12 font-sans overflow-hidden">
      <div className="container mx-auto px-6 max-w-[1296px]">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-12 lg:gap-8">
          {/* Logo and Social Section */}
          <div className="md:col-span-3 lg:col-span-4 flex flex-col gap-8">
            <div className="mb-4">
              <Image 
                src="https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/8b29c68a-eaca-476e-a7ce-c0f16902fd64-baseten-co/assets/images/1764774959-lockup_horizontal_2d_light-1.png"
                alt="Baseten"
                width={131}
                height={34}
                className="brightness-0 invert"
              />
            </div>
            <div className="flex gap-4">
              <a href="#" className="p-1 hover:text-mint transition-colors duration-200">
                <Github size={20} />
              </a>
              <a href="#" className="p-1 hover:text-mint transition-colors duration-200">
                <Twitter size={20} />
              </a>
              <a href="#" className="p-1 hover:text-mint transition-colors duration-200">
                <Linkedin size={20} />
              </a>
              <a href="#" className="p-1 hover:text-mint transition-colors duration-200">
                <Youtube size={20} />
              </a>
            </div>
          </div>

          {/* Navigation Links Grid */}
          <div className="md:col-span-9 lg:col-span-8">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-x-8 gap-y-12">
              {footerSections.map((section) => (
                <div key={section.title} className="flex flex-col gap-4">
                  <h3 className="font-mono text-[12px] uppercase tracking-[0.05em] text-[#737373]">
                    {section.title}
                  </h3>
                  <ul className="flex flex-col">
                    {section.links.map((link, idx) => (
                      <li key={idx} className={link.className}>
                        {link.isHeader ? (
                          <h4 className="font-mono text-[12px] uppercase tracking-[0.05em] text-[#737373] mb-4">
                            {link.label}
                          </h4>
                        ) : (
                          <a 
                            href={link.href}
                            className="block py-1.5 text-[14px] font-normal leading-relaxed text-[#D4D4D4] hover:text-white transition-colors duration-200"
                          >
                            {link.label}
                          </a>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom Section: Status and Copyright */}
        <div className="mt-32 pt-12 border-t border-white/10 flex flex-col md:flex-row items-center justify-between gap-8 md:gap-4">
          <div className="flex items-center">
            <div className="flex items-center gap-2 border border-[#00FF7F]/40 bg-[#00FF7F]/10 px-3 py-1.5 rounded-none group hover:bg-[#00FF7F]/20 transition-all duration-200 cursor-default">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00FF7F] opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00FF7F]"></span>
              </span>
              <span className="font-mono text-[10px] sm:text-[11px] uppercase tracking-wider text-[#00FF7F]">
                ALL SYSTEMS NORMAL
              </span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-8 md:gap-12">
            <span className="font-mono text-[11px] text-[#737373]">
              © 2025 BASETEN
            </span>
            <div className="flex items-center gap-6 opacity-60">
              <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" className="h-8 w-auto">
                <path d="M20 0C8.954 0 0 8.954 0 20C0 31.046 8.954 40 20 40C31.046 40 40 31.046 40 20C40 8.954 31.046 0 20 0ZM20 37.5C10.335 37.5 2.5 29.665 2.5 20C2.5 10.335 10.335 2.5 20 2.5C29.665 2.5 37.5 10.335 37.5 20C37.5 29.665 29.665 37.5 20 37.5Z" fill="white"/>
                <path d="M12 18H28V22H12V18Z" fill="white"/>
              </svg>
              {/* Compliance Badges logic placeholders based on screenshots */}
              <div className="flex gap-4 items-center">
                <div className="h-10 w-10 border border-white/20 flex items-center justify-center p-1">
                  <span className="font-mono text-[8px] text-center leading-tight">SOC 2 TYPE II</span>
                </div>
                <div className="h-10 w-10 border border-white/20 flex items-center justify-center p-1">
                  <span className="font-mono text-[8px] text-center leading-tight">HIPAA</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;