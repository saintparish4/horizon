import React from 'react';
import Image from 'next/image';

const logos = [
  {
    name: 'Cursor',
    url: 'https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/8b29c68a-eaca-476e-a7ce-c0f16902fd64-baseten-co/assets/images/1762279283-type-text-format-none-color-off-black-1-11.png',
    width: 100,
    height: 32,
  },
  {
    name: 'Notion',
    url: 'https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/8b29c68a-eaca-476e-a7ce-c0f16902fd64-baseten-co/assets/images/1764600859-notion_logo_1-2.png',
    width: 90,
    height: 28,
  },
  {
    name: 'OpenEvidence',
    url: 'https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/8b29c68a-eaca-476e-a7ce-c0f16902fd64-baseten-co/assets/images/1758761391-openevidence-3.png',
    width: 140,
    height: 24,
  },
  {
    name: 'Abridge',
    url: 'https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/8b29c68a-eaca-476e-a7ce-c0f16902fd64-baseten-co/assets/images/1740008335-664287c9ef936d8ce43517f8_abridge-logo-w-4.webp',
    width: 110,
    height: 28,
  },
  {
    name: 'Clay',
    url: 'https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/8b29c68a-eaca-476e-a7ce-c0f16902fd64-baseten-co/assets/images/1752855457-clay-logo-dark-1-5.png',
    width: 80,
    height: 32,
  },
  {
    name: 'Gamma',
    url: 'https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/8b29c68a-eaca-476e-a7ce-c0f16902fd64-baseten-co/assets/images/1747248934-gamma-logo-6.png',
    width: 100,
    height: 24,
  },
  {
    name: 'Writer',
    url: 'https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/8b29c68a-eaca-476e-a7ce-c0f16902fd64-baseten-co/assets/images/1758761686-logo-writer-7.png',
    width: 90,
    height: 26,
  },
  {
    name: 'Zed Industries',
    url: 'https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/8b29c68a-eaca-476e-a7ce-c0f16902fd64-baseten-co/assets/images/1758663023-zed-industries-8.png',
    width: 110,
    height: 24,
  },
  {
    name: 'ClickUp',
    url: 'https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/8b29c68a-eaca-476e-a7ce-c0f16902fd64-baseten-co/assets/images/1762205905-logo-v3-clickup-light-2-17.png',
    width: 100,
    height: 30,
  },
  {
    name: 'Patreon',
    url: 'https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/8b29c68a-eaca-476e-a7ce-c0f16902fd64-baseten-co/assets/images/1758662959-logo-patreon-18.png',
    width: 110,
    height: 22,
  },
  {
    name: 'Cisco',
    url: 'https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/8b29c68a-eaca-476e-a7ce-c0f16902fd64-baseten-co/assets/images/1758663144-cisco-19.png',
    width: 60,
    height: 32,
  },
  {
    name: 'Rime',
    url: 'https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/8b29c68a-eaca-476e-a7ce-c0f16902fd64-baseten-co/assets/images/1758761536-rime-20.png',
    width: 80,
    height: 24,
  },
];

export default function TrustLogos() {
  return (
    <section className="bg-[#FBFBFB] border-t border-dashed border-[#E5E7EB]">
      <div className="container mx-auto px-4">
        {/* Header Label */}
        <div className="flex justify-center border-x border-dashed border-[#E5E7EB] py-8 lg:py-12">
          <p className="font-mono text-[10px] md:text-xs uppercase tracking-[0.1em] text-[#737373]">
            Trusted by top engineering and machine learning teams
          </p>
        </div>

        {/* Logos Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 border-y border-dashed border-[#E5E7EB]">
          {logos.map((logo, index) => (
            <div
              key={index}
              className={`
                flex items-center justify-center p-8 lg:p-12 border-dashed border-[#E5E7EB]
                ${index % 2 !== 0 ? 'border-l' : 'border-l-0'}
                ${index >= 2 ? 'border-t md:border-t-0' : ''}
                ${index % 4 !== 0 ? 'md:border-l' : 'md:border-l-0'}
                ${index >= 4 ? 'md:border-t' : ''}
              `}
            >
              <div className="relative gray-scale opacity-70 hover:opacity-100 transition-opacity duration-300">
                <Image
                  src={logo.url}
                  alt={logo.name}
                  width={logo.width}
                  height={logo.height}
                  className="object-contain filter grayscale invert-0"
                  priority={index < 4}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <style jsx global>{`
        .gray-scale {
          filter: grayscale(100%);
        }
      `}</style>
    </section>
  );
}